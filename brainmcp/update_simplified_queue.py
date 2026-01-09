#!/usr/bin/env python3
"""
简化Alpha队列更新脚本
用法: 
  python update_simplified_queue.py --add <alpha_id> --expression <expr> --status pending
  python update_simplified_queue.py --update <alpha_id> --new-status <status> --reason <reason>
  python update_simplified_queue.py --list --status pending
"""

import json
import argparse
import sys
from datetime import datetime

QUEUE_FILE = 'IND_Alpha_Queue_Simplified.json'

def load_queue():
    """加载队列文件"""
    try:
        with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # 创建新队列
        return {
            'metadata': {
                'created': datetime.now().strftime('%Y-%m-%d'),
                'updated': datetime.now().strftime('%Y-%m-%d'),
                'author': 'BW53146',
                'region': 'IND',
                'version': '2.0-simplified',
                'description': '简化Alpha队列'
            },
            'alphas': [],
            'schedule': {},
            'stats': {'total': 0, 'by_status': {}}
        }

def save_queue(data):
    """保存队列文件"""
    data['metadata']['updated'] = datetime.now().strftime('%Y-%m-%d')
    
    # 更新统计
    stats = {'total': 0, 'by_status': {}}
    for alpha in data['alphas']:
        status = alpha['status']
        stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
        stats['total'] += 1
    data['stats'] = stats
    
    with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f'队列已保存: {QUEUE_FILE}')
    print(f'统计: {stats["total"]}个Alpha ({", ".join([f"{k}:{v}" for k, v in stats["by_status"].items()])})')

def add_alpha(data, alpha_id, expression='', status='pending', scheduled_date='', priority=5.0, reason=''):
    """添加Alpha到队列"""
    # 检查是否已存在
    for alpha in data['alphas']:
        if alpha['id'] == alpha_id:
            print(f'警告: Alpha {alpha_id} 已存在，状态: {alpha["status"]}')
            return False
    
    # 添加新Alpha
    new_alpha = {
        'id': alpha_id,
        'status': status,
        'date': datetime.now().strftime('%Y-%m-%d')
    }
    
    if status == 'pending':
        if expression:
            new_alpha['expression'] = expression
        if scheduled_date:
            new_alpha['scheduled'] = scheduled_date
        new_alpha['priority'] = priority
    elif reason:
        new_alpha['reason'] = reason
    
    data['alphas'].append(new_alpha)
    print(f'✓ 已添加Alpha {alpha_id}, 状态: {status}')
    return True

def update_status(data, alpha_id, new_status, reason=''):
    """更新Alpha状态"""
    for alpha in data['alphas']:
        if alpha['id'] == alpha_id:
            old_status = alpha['status']
            alpha['status'] = new_status
            alpha['date'] = datetime.now().strftime('%Y-%m-%d')
            
            if reason:
                alpha['reason'] = reason
            elif 'reason' in alpha and new_status not in ['failed', 'high_correlation']:
                # 如果不是失败状态，移除原因字段
                del alpha['reason']
            
            print(f'✓ Alpha {alpha_id} 状态更新: {old_status} → {new_status}')
            if reason:
                print(f'  原因: {reason}')
            return True
    
    print(f'✗ 未找到Alpha: {alpha_id}')
    return False

def list_alphas(data, status_filter=None):
    """列出Alpha"""
    filtered = data['alphas']
    if status_filter:
        filtered = [a for a in filtered if a['status'] == status_filter]
    
    if not filtered:
        print(f'没有符合条件的Alpha' + (f' (状态: {status_filter})' if status_filter else ''))
        return
    
    print(f'找到 {len(filtered)} 个Alpha' + (f' (状态: {status_filter})' if status_filter else ''))
    print('-' * 80)
    
    for alpha in filtered:
        print(f"ID: {alpha['id']}")
        print(f"状态: {alpha['status']} (添加: {alpha['date']})")
        if 'expression' in alpha:
            expr = alpha['expression']
            if len(expr) > 60:
                expr = expr[:57] + '...'
            print(f"表达式: {expr}")
        if 'scheduled' in alpha:
            print(f"计划提交: {alpha['scheduled']}")
        if 'priority' in alpha:
            print(f"优先级: {alpha['priority']}")
        if 'reason' in alpha:
            print(f"原因: {alpha['reason']}")
        print('-' * 80)

def validate_queue(data):
    """验证队列数据"""
    issues = []
    
    # 检查重复ID
    ids = [a['id'] for a in data['alphas']]
    duplicates = [id for id in set(ids) if ids.count(id) > 1]
    if duplicates:
        issues.append(f'重复的Alpha ID: {duplicates}')
    
    # 检查pending状态必须有表达式
    for alpha in data['alphas']:
        if alpha['status'] == 'pending' and 'expression' not in alpha:
            issues.append(f'pending状态的Alpha {alpha["id"]} 缺少表达式')
    
    return issues

def main():
    parser = argparse.ArgumentParser(description='简化Alpha队列管理工具')
    parser.add_argument('--add', help='添加Alpha (ID)')
    parser.add_argument('--expression', help='Alpha表达式')
    parser.add_argument('--status', choices=['pending', 'submitted', 'failed', 'high_correlation'], 
                       default='pending', help='状态')
    parser.add_argument('--schedule', help='计划提交日期 (YYYY-MM-DD)')
    parser.add_argument('--priority', type=float, default=5.0, help='优先级 (1-10)')
    parser.add_argument('--update', help='更新状态的Alpha ID')
    parser.add_argument('--new-status', choices=['pending', 'submitted', 'failed', 'high_correlation'],
                       help='新状态')
    parser.add_argument('--reason', help='状态变更原因')
    parser.add_argument('--list', action='store_true', help='列出Alpha')
    parser.add_argument('--status-filter', choices=['pending', 'submitted', 'failed', 'high_correlation'],
                       help='列出时过滤状态')
    parser.add_argument('--validate', action='store_true', help='验证队列数据')
    parser.add_argument('--stats', action='store_true', help='显示统计信息')
    
    args = parser.parse_args()
    
    data = load_queue()
    
    if args.validate:
        issues = validate_queue(data)
        if issues:
            print('发现以下问题:')
            for issue in issues:
                print(f'  - {issue}')
        else:
            print('队列数据验证通过')
        return
    
    if args.stats:
        print(f'队列统计:')
        print(f'  总Alpha数: {data["stats"]["total"]}')
        for status, count in sorted(data['stats']['by_status'].items()):
            print(f'  {status}: {count}')
        return
    
    if args.list:
        list_alphas(data, args.status_filter)
        return
    
    if args.add:
        success = add_alpha(data, args.add, args.expression, args.status, 
                           args.schedule, args.priority, args.reason)
    elif args.update and args.new_status:
        success = update_status(data, args.update, args.new_status, args.reason)
    else:
        parser.print_help()
        return
    
    if success:
        save_queue(data)

if __name__ == '__main__':
    main()