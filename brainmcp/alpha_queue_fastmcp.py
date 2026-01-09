#!/usr/bin/env python3
"""
Alpha队列MCP服务器（FastMCP版本）
提供Alpha队列管理的MCP工具接口
使用FastMCP框架简化开发
"""

import json
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP

# 创建FastMCP应用
app = FastMCP(
    name="alpha-queue",
    version="1.0.0"
)

QUEUE_FILE = 'IND_Alpha_Queue_Simplified.json'

class AlphaQueueManager:
    """Alpha队列管理器"""
    
    @staticmethod
    def load_queue() -> Dict[str, Any]:
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
    
    @staticmethod
    def save_queue(data: Dict[str, Any]) -> Dict[str, Any]:
        """保存队列文件并返回更新后的数据"""
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
        
        return data
    
    @staticmethod
    def list_alphas(status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出Alpha"""
        data = AlphaQueueManager.load_queue()
        alphas = data['alphas']
        
        if status_filter:
            alphas = [a for a in alphas if a['status'] == status_filter]
        
        return alphas
    
    @staticmethod
    def add_alpha(alpha_id: str, expression: str = '', status: str = 'pending',
                  scheduled_date: str = '', priority: float = 5.0, reason: str = '') -> Dict[str, Any]:
        """添加Alpha到队列"""
        data = AlphaQueueManager.load_queue()
        
        # 检查是否已存在
        for alpha in data['alphas']:
            if alpha['id'] == alpha_id:
                return {
                    'success': False,
                    'error': f'Alpha {alpha_id} 已存在，状态: {alpha["status"]}'
                }
        
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
        data = AlphaQueueManager.save_queue(data)
        
        return {
            'success': True,
            'message': f'已添加Alpha {alpha_id}, 状态: {status}',
            'alpha': new_alpha
        }
    
    @staticmethod
    def update_status(alpha_id: str, new_status: str, reason: str = '') -> Dict[str, Any]:
        """更新Alpha状态"""
        data = AlphaQueueManager.load_queue()
        
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
                
                data = AlphaQueueManager.save_queue(data)
                
                return {
                    'success': True,
                    'message': f'Alpha {alpha_id} 状态更新: {old_status} → {new_status}',
                    'alpha': alpha,
                    'reason': reason if reason else None
                }
        
        return {
            'success': False,
            'error': f'未找到Alpha: {alpha_id}'
        }
    
    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """获取统计信息"""
        data = AlphaQueueManager.load_queue()
        return {
            'total': data['stats']['total'],
            'by_status': data['stats']['by_status'],
            'metadata': data['metadata']
        }
    
    @staticmethod
    def validate_queue() -> Dict[str, Any]:
        """验证队列数据"""
        data = AlphaQueueManager.load_queue()
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
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'alpha_count': len(data['alphas'])
        }


# FastMCP工具定义
# 工具名称与原始MCP服务器保持一致以确保兼容性

@app.tool(name="alpha_queue_list")
def list_alphas(status_filter: Optional[str] = None) -> str:
    """
    列出Alpha队列中的Alpha
    
    Args:
        status_filter: 状态过滤 (pending, submitted, failed, high_correlation)
    """
    alphas = AlphaQueueManager.list_alphas(status_filter)
    return json.dumps(alphas, indent=2, ensure_ascii=False)


@app.tool(name="alpha_queue_add")
def add_alpha(
    alpha_id: str,
    expression: str = "",
    status: str = "pending",
    scheduled_date: str = "",
    priority: float = 5.0,
    reason: str = ""
) -> str:
    """
    添加Alpha到队列
    
    Args:
        alpha_id: Alpha ID (8位字母数字)
        expression: Alpha表达式
        status: 状态 (pending, submitted, failed, high_correlation)
        scheduled_date: 计划提交日期 (YYYY-MM-DD)
        priority: 优先级 (1-10)
        reason: 原因 (用于failed或high_correlation状态)
    """
    result = AlphaQueueManager.add_alpha(
        alpha_id=alpha_id,
        expression=expression,
        status=status,
        scheduled_date=scheduled_date,
        priority=priority,
        reason=reason
    )
    return json.dumps(result, indent=2, ensure_ascii=False)


@app.tool(name="alpha_queue_update")
def update_status(
    alpha_id: str,
    new_status: str,
    reason: str = ""
) -> str:
    """
    更新Alpha状态
    
    Args:
        alpha_id: Alpha ID
        new_status: 新状态 (pending, submitted, failed, high_correlation)
        reason: 状态变更原因
    """
    result = AlphaQueueManager.update_status(
        alpha_id=alpha_id,
        new_status=new_status,
        reason=reason
    )
    return json.dumps(result, indent=2, ensure_ascii=False)


@app.tool(name="alpha_queue_stats")
def get_stats() -> str:
    """
    获取队列统计信息
    """
    result = AlphaQueueManager.get_stats()
    return json.dumps(result, indent=2, ensure_ascii=False)


@app.tool(name="alpha_queue_validate")
def validate_queue() -> str:
    """
    验证队列数据完整性
    """
    result = AlphaQueueManager.validate_queue()
    return json.dumps(result, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # 运行FastMCP应用，使用stdio传输，禁用横幅
    app.run(transport="stdio", show_banner=False)