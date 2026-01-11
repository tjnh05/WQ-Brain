#!/usr/bin/env python3
"""
字段使用频率分析脚本
分析收集到的Alpha表达式，提取字段使用模式
"""
import re
import json
from collections import Counter, defaultdict
import os

def extract_fields_from_expression(expr):
    """从Alpha表达式中提取字段名称"""
    # 字段名称模式：字母数字下划线组合，常见模式如 mdl110_value, anl4_afv4_eps_mean
    # 排除常见操作符和函数名
    field_pattern = r'\b([a-z]+[0-9]+_[a-z_]+|[a-z]+_[a-z0-9]+_[a-z_]+)\b'
    
    # 排除常见的操作符和函数
    excluded_keywords = {
        'ts_delta', 'ts_mean', 'ts_rank', 'ts_zscore', 'ts_av_diff', 'ts_backfill',
        'ts_regression', 'ts_corr', 'ts_delay', 'ts_decay_linear',
        'rank', 'zscore', 'scale', 'winsorize', 'normalize',
        'reverse', 'if_else', 'greater', 'less', 'equal',
        'group_rank', 'group_mean', 'group_zscore',
        'vector_neut', 'regression_neut', 'left_tail', 'right_tail', 'tail'
    }
    
    matches = re.findall(field_pattern, expr)
    # 过滤掉操作符和函数
    fields = [m for m in matches if m not in excluded_keywords]
    
    return fields

def analyze_file(file_path, field_counter, expression_counter):
    """分析单个文件中的字段使用情况"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 提取表达式（假设表达式在代码块或特定标记中）
        # 简单方法：查找包含字段的模式
        lines = content.split('\n')
        expressions = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                # 检查是否包含字段模式
                if re.search(r'\b(mdl|anl|global|industry|sector|country|region|long_term|mid_term|short_term)', line):
                    expressions.append(line)
        
        for expr in expressions:
            fields = extract_fields_from_expression(expr)
            for field in fields:
                field_counter[field] += 1
            expression_counter['total'] += 1
            if fields:
                expression_counter['with_fields'] += 1
                
        return len(expressions)
    except Exception as e:
        print(f"分析文件 {file_path} 时出错: {e}")
        return 0

def main():
    # 定义要分析的文件列表
    base_dir = "/Users/mac/WQ-Brain/brainmcp"
    files_to_analyze = [
        os.path.join(base_dir, "IND_Model_Addition_Templates_20251230.txt"),
        os.path.join(base_dir, "IND_Model_Differentiated_Expressions_20251230.txt"),
        os.path.join(base_dir, "USA_Alpha_Expressions_20251229.txt"),
        os.path.join(base_dir, "AIResearchReports/IND_PowerPool_Alpha_Mining_Report_20260109.md"),
        os.path.join(base_dir, "IND_Alpha_Submission_Queue_20251231.json"),
        # 新增表达式文件扩展字段覆盖
        os.path.join(base_dir, "news17_expressions.txt"),
        os.path.join(base_dir, "pv_expressions.txt"),
        os.path.join(base_dir, "sentiment_expressions.txt"),
        os.path.join(base_dir, "ASI_Alpha_Expressions_Library_20251225.txt"),
        os.path.join(base_dir, "IND_Alpha_Mining_Ready_Expressions_20251226.txt"),
        # USA区域表达式文件
        os.path.join(base_dir, "USA_Alpha_Correlation_Reduction_Expressions_20251229.txt"),
        os.path.join(base_dir, "USA_Alpha_Final_Optimized_Expressions_20251229.txt"),
        os.path.join(base_dir, "USA_Alpha_LongWindow_Expressions_20251229.txt"),
        os.path.join(base_dir, "USA_Alpha_Neutralization_Expressions_20251229.txt"),
        os.path.join(base_dir, "USA_Alpha_New_Fields_Expressions_20251229.txt"),
        os.path.join(base_dir, "USA_Alpha_Optimized_Expressions_20251229.txt"),
        os.path.join(base_dir, "USA_Alpha_ts_delta_Optimized_Expressions_20251229.txt"),
        os.path.join(base_dir, "USA_Analyst15_Alpha_Expressions_20251229.txt"),
        os.path.join(base_dir, "USA_Analyst15_Alpha_New_Expressions_20251229.txt"),
        os.path.join(base_dir, "USA_Analyst15_Alpha_Optimization_Variants_20251229.txt"),
        os.path.join(base_dir, "USA_Analyst4_Alpha_Optimization_Variants_20251229.txt"),
        os.path.join(base_dir, "USA_Earnings6_Alpha_Expressions_20251229.txt"),
    ]
    
    field_counter = Counter()
    expression_counter = {'total': 0, 'with_fields': 0}
    
    print("开始分析字段使用频率...")
    print("=" * 60)
    
    for file_path in files_to_analyze:
        if os.path.exists(file_path):
            expr_count = analyze_file(file_path, field_counter, expression_counter)
            print(f"分析文件: {os.path.basename(file_path)}")
            print(f"  发现表达式: {expr_count} 个")
    
    print("=" * 60)
    print(f"总共分析表达式: {expression_counter['total']} 个")
    print(f"包含字段的表达式: {expression_counter['with_fields']} 个")
    print("\n字段使用频率排名（Top 20）:")
    print("-" * 60)
    
    for field, count in field_counter.most_common(20):
        print(f"  {field}: {count} 次")
    
    # 按数据集分类字段
    dataset_fields = defaultdict(list)
    for field in field_counter:
        if field.startswith('mdl'):
            dataset_fields['Model'].append((field, field_counter[field]))
        elif field.startswith('anl'):
            dataset_fields['Analyst'].append((field, field_counter[field]))
        elif 'global' in field or 'industry' in field or 'sector' in field:
            dataset_fields['Momentum'].append((field, field_counter[field]))
        else:
            dataset_fields['Other'].append((field, field_counter[field]))
    
    print("\n按数据集分类字段:")
    print("-" * 60)
    for dataset, fields in dataset_fields.items():
        if fields:
            print(f"\n{dataset} 数据集:")
            for field, count in sorted(fields, key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {field}: {count} 次")
    
    # 分析字段组合模式
    print("\n常见字段组合模式分析:")
    print("-" * 60)
    
    # 从模板文件中提取组合模式
    template_file = os.path.join(base_dir, "IND_Model_Addition_Templates_20251230.txt")
    if os.path.exists(template_file):
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找模板表达式
        template_pattern = r'表达式[A-Z0-9]+\*\*?.*?`(.*?)`'
        templates = re.findall(template_pattern, content, re.DOTALL)
        
        if templates:
            print(f"从模板文件中发现 {len(templates)} 个模板表达式")
            print("常见组合模式:")
            for i, template in enumerate(templates[:5], 1):
                fields = extract_fields_from_expression(template)
                if len(fields) >= 2:
                    print(f"  模式{i}: {fields[0]} + {fields[1]}")
    
    # 保存分析结果
    output = {
        'total_expressions': expression_counter['total'],
        'expressions_with_fields': expression_counter['with_fields'],
        'field_frequency': dict(field_counter.most_common(50)),
        'dataset_fields': {k: dict(v) for k, v in dataset_fields.items()}
    }
    
    output_file = os.path.join(base_dir, "field_analysis_results.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n分析结果已保存到: {output_file}")

if __name__ == "__main__":
    main()
