#!/usr/bin/env python3
"""
模板化变体生成算法
基于字段数据库和成功模板自动生成Alpha表达式变体
"""

import json
import random
from typing import List, Dict, Tuple, Optional

class VariantGenerator:
    def __init__(self, database_path: str):
        """初始化生成器，加载字段数据库"""
        with open(database_path, 'r', encoding='utf-8') as f:
            self.database = json.load(f)
        
        # 预定义模板
        self.templates = self.database.get('successful_templates', [])
        
        # 预定义操作符和参数
        self.operators = {
            'high_success': ['ts_delta', 'ts_mean', 'rank'],
            'medium_success': ['ts_rank', 'ts_zscore', 'group_rank'],
            'specialized': ['vector_neut', 'regression_neut', 'if_else']
        }
        
        self.windows = [5, 22, 66, 120, 252, 504]  # 经济学时间窗口
        self.decays = [0, 1, 2, 3, 5]  # decay值必须是整数
    
    def filter_fields(self, region: str, alpha_type: str = 'REGULAR', 
                      max_correlation_risk: str = 'MEDIUM') -> List[Dict]:
        """根据区域、Alpha类型和相关性风险筛选字段"""
        suitable_fields = []
        
        for field_name, field_data in self.database['fields'].items():
            # 检查相关性风险
            risk_level = field_data['correlation_risk']['level']
            risk_order = {'LOW': 0, 'MEDIUM': 1, 'HIGH': 2}
            if risk_order[risk_level] > risk_order[max_correlation_risk]:
                continue
            
            # 检查区域表现
            region_perf = field_data['regional_performance'].get(region, {})
            success_rate = region_perf.get('success_rate', 0)
            
            # 对于Power Pool Alpha，检查适配性
            if alpha_type == 'POWER_POOL':
                suitability = field_data['power_pool_suitability']
                if suitability == 'LOW':
                    continue
            
            suitable_fields.append(field_data)
        
        return suitable_fields
    
    def select_template(self, alpha_type: str, num_fields: int) -> Dict:
        """根据Alpha类型和字段数量选择模板"""
        suitable_templates = []
        
        for template in self.templates:
            # 估算模板所需字段数
            if 'field1' in template['pattern'] and 'field2' in template['pattern']:
                template_field_count = 2
            elif 'field1' in template['pattern']:
                template_field_count = 1
            else:
                template_field_count = 0
            
            if template_field_count <= num_fields:
                suitable_templates.append(template)
        
        if not suitable_templates:
            # 返回默认模板
            if alpha_type == 'POWER_POOL':
                return {
                    'name': 'Power Pool简单模板',
                    'pattern': 'ts_delta(ts_mean({field1}, {window1}), {window2})',
                    'description': 'Power Pool成功模板'
                }
            else:
                return {
                    'name': '双字段加法模板',
                    'pattern': 'ts_delta(rank({field1}) + rank({field2}), {window})',
                    'description': '常规Alpha成功模板'
                }
        
        # 根据成功率选择最佳模板
        suitable_templates.sort(key=lambda x: x.get('success_rate', 0), reverse=True)
        return suitable_templates[0]
    
    def generate_single_variant(self, fields: List[Dict], template: Dict, 
                                alpha_type: str = 'REGULAR') -> str:
        """生成单个表达式变体"""
        pattern = template['pattern']
        
        # 选择操作符（如果需要）
        if '{operator}' in pattern:
            if alpha_type == 'POWER_POOL':
                op_pool = self.operators['high_success']
            else:
                op_pool = self.operators['high_success'] + self.operators['medium_success']
            operator = random.choice(op_pool)
            pattern = pattern.replace('{operator}', operator)
        
        # 替换字段占位符
        field_names = [f['name'] for f in fields]
        for i, field_name in enumerate(field_names, 1):
            placeholder = f'{{field{i}}}'
            if placeholder in pattern:
                pattern = pattern.replace(placeholder, field_name)
        
        # 替换窗口期参数
        window_placeholders = ['{window}', '{window1}', '{window2}', '{window3}']
        for placeholder in window_placeholders:
            if placeholder in pattern:
                window = random.choice(self.windows)
                pattern = pattern.replace(placeholder, str(window))
        
        # 替换decay参数
        if '{decay}' in pattern:
            decay = random.choice(self.decays)
            pattern = pattern.replace('{decay}', str(decay))
        
        return pattern
    
    def generate_variants(self, region: str = 'IND', alpha_type: str = 'REGULAR',
                          num_variants: int = 8, field_selection_strategy: str = 'balanced') -> List[str]:
        """
        生成多个表达式变体
        
        Args:
            region: 目标区域
            alpha_type: Alpha类型（REGULAR 或 POWER_POOL）
            num_variants: 需要生成的变体数量
            field_selection_strategy: 字段选择策略
                - 'balanced': 平衡相关性和成功率
                - 'low_correlation': 优先低相关性字段
                - 'high_success': 优先高成功率字段
        """
        # 确定相关性风险阈值
        if field_selection_strategy == 'low_correlation':
            max_risk = 'LOW'
        elif field_selection_strategy == 'high_success':
            max_risk = 'HIGH'  # 允许高风险但高成功率字段
        else:
            max_risk = 'MEDIUM'
        
        # 筛选字段
        all_fields = self.filter_fields(region, alpha_type, max_risk)
        
        if not all_fields:
            raise ValueError(f"未找到适合{region}区域{alpha_type} Alpha的字段")
        
        # 根据策略排序字段
        if field_selection_strategy == 'low_correlation':
            all_fields.sort(key=lambda x: x['correlation_risk']['level'] == 'LOW', reverse=True)
        elif field_selection_strategy == 'high_success':
            all_fields.sort(key=lambda x: x['regional_performance'].get(region, {}).get('success_rate', 0), reverse=True)
        
        variants = []
        used_field_combinations = set()
        
        while len(variants) < num_variants and len(all_fields) >= 2:
            # 选择字段数量（1-3个，Power Pool最多3个）
            if alpha_type == 'POWER_POOL':
                num_fields = random.choice([1, 2])
            else:
                num_fields = random.choice([1, 2, 3])
            
            # 选择字段
            selected_fields = random.sample(all_fields, min(num_fields, len(all_fields)))
            field_names = tuple(sorted([f['name'] for f in selected_fields]))
            
            # 避免重复组合
            if field_names in used_field_combinations:
                continue
            
            used_field_combinations.add(field_names)
            
            # 选择模板
            template = self.select_template(alpha_type, num_fields)
            
            try:
                variant = self.generate_single_variant(selected_fields, template, alpha_type)
                
                # 验证表达式基本语法
                if self.validate_expression(variant):
                    variants.append(variant)
                else:
                    continue
                    
            except Exception as e:
                print(f"生成变体时出错: {e}")
                continue
        
        return variants
    
    def validate_expression(self, expression: str) -> bool:
        """基本表达式验证"""
        # 检查括号匹配
        if expression.count('(') != expression.count(')'):
            return False
        
        # 检查基本语法
        if '()' in expression:  # 空括号
            return False
        
        # 检查字段占位符是否已替换
        if '{field' in expression or '{window' in expression:
            return False
        
        return True
    
    def generate_power_pool_variants(self, region: str = 'IND', num_variants: int = 5) -> List[str]:
        """专门生成Power Pool Alpha变体"""
        variants = self.generate_variants(
            region=region,
            alpha_type='POWER_POOL',
            num_variants=num_variants,
            field_selection_strategy='low_correlation'  # Power Pool需要低相关性
        )
        
        # 额外验证：检查复杂度
        validated_variants = []
        for variant in variants:
            # 估算操作符数量（简单方法）
            operator_count = sum(1 for op in ['ts_delta', 'ts_mean', 'ts_rank', 'ts_zscore', 
                                              'rank', 'zscore', 'group_rank'] if op in variant)
            if operator_count <= 8:  # Power Pool限制
                validated_variants.append(variant)
        
        return validated_variants
    
    def generate_for_high_correlation_alpha(self, original_expression: str, 
                                           original_fields: List[str]) -> List[str]:
        """为高相关性Alpha生成优化变体"""
        # 分析原表达式字段
        suggestions = []
        
        # 策略1：替换为低相关性字段
        low_risk_fields = self.filter_fields('IND', 'REGULAR', 'LOW')
        if low_risk_fields:
            for field in low_risk_fields[:3]:
                new_expr = original_expression
                for orig_field in original_fields:
                    if orig_field in new_expr:
                        new_expr = new_expr.replace(orig_field, field['name'])
                suggestions.append(new_expr)
        
        # 策略2：改变窗口期
        for window in [120, 252]:  # 更长窗口期降低相关性
            if '66' in original_expression:
                new_expr = original_expression.replace('66', str(window))
                suggestions.append(new_expr)
        
        # 策略3：添加数据预处理
        if 'rank(' in original_expression:
            new_expr = original_expression.replace('rank(', 'rank(ts_backfill(')
            new_expr = new_expr.replace(')', ', 5))', 1)  # 只替换第一个
            suggestions.append(new_expr)
        
        return suggestions[:5]  # 返回前5个建议

def main():
    """主函数：演示变体生成"""
    print("模板化变体生成算法演示")
    print("=" * 60)
    
    # 初始化生成器
    generator = VariantGenerator("/Users/mac/WQ-Brain/brainmcp/field_database_v1.json")
    
    # 生成Power Pool Alpha变体
    print("\n1. 生成IND区域Power Pool Alpha变体（5个）:")
    print("-" * 60)
    power_pool_variants = generator.generate_power_pool_variants('IND', 5)
    for i, variant in enumerate(power_pool_variants, 1):
        print(f"{i}. {variant}")
    
    # 生成常规Alpha变体
    print("\n2. 生成IND区域常规Alpha变体（8个）:")
    print("-" * 60)
    regular_variants = generator.generate_variants('IND', 'REGULAR', 8, 'balanced')
    for i, variant in enumerate(regular_variants, 1):
        print(f"{i}. {variant}")
    
    # 演示高相关性Alpha优化
    print("\n3. 高相关性Alpha优化示例:")
    print("-" * 60)
    original_expr = "ts_av_diff(rank(global_value_momentum_rank_float), 252)"
    original_fields = ["global_value_momentum_rank_float"]
    optimized = generator.generate_for_high_correlation_alpha(original_expr, original_fields)
    for i, variant in enumerate(optimized, 1):
        print(f"{i}. {variant}")
    
    # 保存生成的变体
    output = {
        'power_pool_variants': power_pool_variants,
        'regular_variants': regular_variants,
        'optimization_examples': optimized,
        'generation_date': '2026-01-10'
    }
    
    output_file = "/Users/mac/WQ-Brain/brainmcp/generated_variants.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n变体已保存到: {output_file}")
    
    # 统计信息
    print("\n生成统计:")
    print(f"- Power Pool变体: {len(power_pool_variants)} 个")
    print(f"- 常规变体: {len(regular_variants)} 个")
    print(f"- 优化示例: {len(optimized)} 个")
    
    # 字段使用分析
    all_variants = power_pool_variants + regular_variants + optimized
    field_usage = {}
    for variant in all_variants:
        for field_data in generator.database['fields'].values():
            if field_data['name'] in variant:
                field_usage[field_data['name']] = field_usage.get(field_data['name'], 0) + 1
    
    print("\n生成变体中的字段使用频率:")
    for field, count in sorted(field_usage.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {field}: {count} 次")

if __name__ == "__main__":
    main()
