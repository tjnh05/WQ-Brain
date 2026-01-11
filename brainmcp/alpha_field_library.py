#!/usr/bin/env python3
"""
Alpha字段库与模板化生产系统
集成字段数据库、相关性分析和变体生成功能
"""

import json
import random
import re
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Optional, Any

class AlphaFieldLibrary:
    """Alpha字段库核心类"""
    
    def __init__(self, database_path: str = None):
        """初始化字段库"""
        if database_path is None:
            database_path = "/Users/mac/WQ-Brain/brainmcp/field_database_v1.json"
        
        self.database_path = database_path
        self.load_database()
        self.init_templates()
        self.init_operators()
        
    def load_database(self):
        """加载字段数据库"""
        try:
            with open(self.database_path, 'r', encoding='utf-8') as f:
                self.database = json.load(f)
            print(f"字段数据库加载成功，包含 {len(self.database['fields'])} 个字段")
        except Exception as e:
            print(f"加载数据库失败: {e}")
            self.database = {'fields': {}, 'metadata': {}}
    
    def init_templates(self):
        """初始化模板系统"""
        self.templates = {
            # Power Pool模板
            'power_pool_simple': {
                'name': 'Power Pool简单模板',
                'pattern': 'ts_delta(ts_mean({field1}, {window1}), {window2})',
                'description': '简单Power Pool模板，操作符≤2，字段≤1',
                'field_count': 1,
                'operator_count': 2,
                'success_rate': 0.8
            },
            'power_pool_rank': {
                'name': 'Power Pool排名模板',
                'pattern': 'ts_delta(rank({field1}), {window})',
                'description': '排名变化Power Pool模板',
                'field_count': 1,
                'operator_count': 2,
                'success_rate': 0.7
            },
            
            # 常规Alpha模板
            'regular_two_field_add': {
                'name': '双字段加法模板',
                'pattern': 'ts_delta(rank({field1}) + rank({field2}), {window})',
                'description': '双字段加法，IND地区成功模板',
                'field_count': 2,
                'operator_count': 3,
                'success_rate': 0.7
            },
            'regular_zscore_interact': {
                'name': 'zscore交互模板',
                'pattern': 'ts_zscore({field1}, {window1}) * ts_zscore({field2}, {window2})',
                'description': 'zscore标准化交互，降低相关性',
                'field_count': 2,
                'operator_count': 2,
                'success_rate': 0.6
            },
            'regular_three_field_add': {
                'name': '三字段加法模板',
                'pattern': 'ts_rank(rank({field1}) + rank({field2}) + rank({field3}), {window})',
                'description': '三字段加法，增强差异化',
                'field_count': 3,
                'operator_count': 4,
                'success_rate': 0.5
            },
            
            # 高相关性优化模板
            'optimize_window_change': {
                'name': '窗口期优化模板',
                'pattern': 'ts_av_diff(rank({field1}), {window})',
                'description': '改变窗口期降低相关性',
                'field_count': 1,
                'operator_count': 2,
                'success_rate': 0.6
            },
            'optimize_preprocessing': {
                'name': '数据预处理模板',
                'pattern': 'ts_av_diff(rank(ts_backfill({field1}, 5)), {window})',
                'description': '添加ts_backfill预处理',
                'field_count': 1,
                'operator_count': 3,
                'success_rate': 0.5
            }
        }
        
        # 经济学时间窗口
        self.windows = [5, 22, 66, 120, 252, 504]
        
        # decay值（必须是整数）
        self.decays = [0, 1, 2, 3, 5]
    
    def init_operators(self):
        """初始化操作符系统"""
        self.operators = {
            'high_success': ['ts_delta', 'ts_mean', 'rank', 'ts_av_diff'],
            'medium_success': ['ts_rank', 'ts_zscore', 'group_rank', 'zscore'],
            'specialized': ['vector_neut', 'regression_neut', 'if_else', 'left_tail', 'right_tail']
        }
    
    def get_field(self, field_name: str) -> Optional[Dict]:
        """获取字段详细信息"""
        return self.database['fields'].get(field_name)
    
    def search_fields(self, dataset: str = None, data_type: str = None, 
                      max_risk: str = 'MEDIUM', min_success_rate: float = 0.0) -> List[Dict]:
        """搜索符合条件的字段"""
        results = []
        risk_order = {'LOW': 0, 'MEDIUM': 1, 'HIGH': 2}
        
        for field_name, field_data in self.database['fields'].items():
            # 数据集过滤
            if dataset and field_data['dataset'] != dataset:
                continue
            
            # 数据类型过滤
            if data_type and field_data['data_type'] != data_type:
                continue
            
            # 风险等级过滤
            field_risk = field_data['correlation_risk']['level']
            if risk_order[field_risk] > risk_order[max_risk]:
                continue
            
            # 成功率过滤（使用IND区域作为参考）
            ind_perf = field_data['regional_performance'].get('IND', {})
            success_rate = ind_perf.get('success_rate', 0)
            if success_rate < min_success_rate:
                continue
            
            results.append(field_data)
        
        return results
    
    def recommend_fields(self, region: str = 'IND', alpha_type: str = 'REGULAR',
                         num_fields: int = 3) -> List[Dict]:
        """推荐适合的字段"""
        if alpha_type == 'POWER_POOL':
            # Power Pool需要低相关性和简单性
            fields = self.search_fields(max_risk='LOW', min_success_rate=0.5)
            # 按Power Pool适配性排序
            fields.sort(key=lambda x: x['power_pool_suitability'] != 'HIGH')
        else:
            # 常规Alpha可以接受中等风险
            fields = self.search_fields(max_risk='MEDIUM', min_success_rate=0.3)
            # 按区域成功率排序
            fields.sort(key=lambda x: x['regional_performance'].get(region, {}).get('success_rate', 0), reverse=True)
        
        return fields[:num_fields]
    
    def generate_expression(self, fields: List[Dict], template_name: str = None, 
                           alpha_type: str = 'REGULAR') -> str:
        """生成单个Alpha表达式"""
        # 选择模板
        if template_name and template_name in self.templates:
            template = self.templates[template_name]
        else:
            # 自动选择模板
            if alpha_type == 'POWER_POOL':
                template = self.templates['power_pool_simple']
            else:
                if len(fields) == 1:
                    template = self.templates['optimize_window_change']
                elif len(fields) == 2:
                    template = self.templates['regular_two_field_add']
                else:
                    template = self.templates['regular_three_field_add']
        
        # 获取模板模式
        pattern = template['pattern']
        
        # 替换字段占位符
        for i, field in enumerate(fields, 1):
            placeholder = f'{{field{i}}}'
            if placeholder in pattern:
                pattern = pattern.replace(placeholder, field['name'])
        
        # 替换窗口期参数
        window_matches = re.findall(r'\{window\d*\}', pattern)
        for match in set(window_matches):
            window = random.choice(self.windows)
            pattern = pattern.replace(match, str(window))
        
        # 替换其他参数
        if '{decay}' in pattern:
            pattern = pattern.replace('{decay}', str(random.choice(self.decays)))
        
        return pattern
    
    def generate_variants(self, region: str = 'IND', alpha_type: str = 'REGULAR',
                         num_variants: int = 8, strategy: str = 'balanced') -> List[str]:
        """生成多个Alpha表达式变体"""
        variants = []
        used_combinations = set()
        
        while len(variants) < num_variants:
            # 选择字段数量
            if alpha_type == 'POWER_POOL':
                field_count = random.choice([1, 2])  # Power Pool建议1-2个字段
            else:
                field_count = random.choice([1, 2, 3])
            
            # 推荐字段
            recommended = self.recommend_fields(region, alpha_type, field_count * 2)
            if len(recommended) < field_count:
                break
            
            selected_fields = random.sample(recommended, field_count)
            field_names = tuple(sorted([f['name'] for f in selected_fields]))
            
            # 避免重复组合
            if field_names in used_combinations:
                continue
            used_combinations.add(field_names)
            
            # 生成表达式
            try:
                expr = self.generate_expression(selected_fields, alpha_type=alpha_type)
                
                # 基本验证
                if self.validate_expression(expr):
                    variants.append(expr)
            except Exception as e:
                print(f"生成表达式时出错: {e}")
                continue
        
        return variants
    
    def validate_expression(self, expression: str) -> bool:
        """验证表达式基本语法"""
        # 检查括号匹配
        if expression.count('(') != expression.count(')'):
            return False
        
        # 检查空括号
        if '()' in expression:
            return False
        
        # 检查未替换的占位符
        if re.search(r'\{\w+\}', expression):
            return False
        
        return True
    
    def optimize_high_correlation_alpha(self, original_expr: str, 
                                       original_field: str) -> List[str]:
        """优化高相关性Alpha"""
        optimizations = []
        
        # 获取原字段信息
        field_data = self.get_field(original_field)
        if not field_data:
            return optimizations
        
        # 策略1：替换为低相关性字段
        low_risk_fields = self.search_fields(max_risk='LOW', min_success_rate=0.3)
        for new_field in low_risk_fields[:3]:
            new_expr = original_expr.replace(original_field, new_field['name'])
            optimizations.append(new_expr)
        
        # 策略2：改变窗口期
        for window in [120, 252]:
            if '66' in original_expr:
                new_expr = original_expr.replace('66', str(window))
                optimizations.append(new_expr)
            elif '252' in original_expr:
                new_expr = original_expr.replace('252', str(window))
                optimizations.append(new_expr)
        
        # 策略3：添加预处理
        if 'rank(' in original_expr:
            new_expr = original_expr.replace('rank(', 'rank(ts_backfill(')
            # 找到对应的闭括号
            parts = new_expr.split('ts_backfill(')
            if len(parts) > 1:
                new_expr = parts[0] + 'ts_backfill(' + parts[1].replace(')', ', 5))', 1)
            optimizations.append(new_expr)
        
        # 策略4：改变操作符
        if 'ts_av_diff' in original_expr:
            new_expr = original_expr.replace('ts_av_diff', 'ts_delta')
            optimizations.append(new_expr)
        
        return optimizations[:5]
    
    def analyze_expression(self, expression: str) -> Dict:
        """分析表达式特征"""
        analysis = {
            'field_count': 0,
            'operator_count': 0,
            'fields': [],
            'operators': [],
            'window_sizes': [],
            'complexity_level': 'LOW'
        }
        
        # 识别字段
        for field_name in self.database['fields']:
            if field_name in expression:
                analysis['fields'].append(field_name)
                analysis['field_count'] += 1
        
        # 识别操作符
        for op_category in self.operators.values():
            for op in op_category:
                if op in expression:
                    analysis['operators'].append(op)
                    analysis['operator_count'] += 1
        
        # 识别窗口期
        for window in self.windows:
            if str(window) in expression:
                analysis['window_sizes'].append(window)
        
        # 评估复杂度
        total_ops = analysis['operator_count']
        if total_ops <= 3:
            analysis['complexity_level'] = 'LOW'
        elif total_ops <= 5:
            analysis['complexity_level'] = 'MEDIUM'
        else:
            analysis['complexity_level'] = 'HIGH'
        
        return analysis
    
    def save_variants(self, variants: List[str], filename: str):
        """保存生成的变体到文件"""
        output = {
            'variants': variants,
            'count': len(variants),
            'generation_date': '2026-01-10',
            'source_database': self.database_path
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"变体已保存到: {filename}")

def demo():
    """演示字段库功能"""
    print("Alpha字段库与模板化生产系统演示")
    print("=" * 60)
    
    # 初始化字段库
    library = AlphaFieldLibrary()
    
    # 1. 字段查询演示
    print("\n1. 字段查询演示:")
    print("-" * 60)
    model_fields = library.search_fields(dataset='Model', max_risk='LOW')
    print(f"Model数据集低风险字段: {len(model_fields)} 个")
    for field in model_fields[:5]:
        print(f"  - {field['name']}: {field['description']}")
    
    # 2. 字段推荐演示
    print("\n2. IND区域Power Pool字段推荐:")
    print("-" * 60)
    recommended = library.recommend_fields('IND', 'POWER_POOL', 5)
    for i, field in enumerate(recommended, 1):
        risk = field['correlation_risk']['level']
        suitability = field['power_pool_suitability']
        print(f"{i}. {field['name']} (风险: {risk}, 适配性: {suitability})")
    
    # 3. 生成Power Pool变体
    print("\n3. 生成IND区域Power Pool Alpha变体:")
    print("-" * 60)
    power_pool_variants = library.generate_variants('IND', 'POWER_POOL', 5)
    for i, variant in enumerate(power_pool_variants, 1):
        print(f"{i}. {variant}")
    
    # 4. 生成常规Alpha变体
    print("\n4. 生成IND区域常规Alpha变体:")
    print("-" * 60)
    regular_variants = library.generate_variants('IND', 'REGULAR', 8)
    for i, variant in enumerate(regular_variants, 1):
        print(f"{i}. {variant}")
    
    # 5. 高相关性Alpha优化演示
    print("\n5. 高相关性Alpha优化演示:")
    print("-" * 60)
    original_expr = "ts_av_diff(rank(global_value_momentum_rank_float), 252)"
    original_field = "global_value_momentum_rank_float"
    optimizations = library.optimize_high_correlation_alpha(original_expr, original_field)
    for i, opt in enumerate(optimizations, 1):
        print(f"{i}. {opt}")
    
    # 6. 表达式分析演示
    print("\n6. 表达式分析演示:")
    print("-" * 60)
    sample_expr = "ts_delta(rank(mdl110_value) + rank(sector_value_momentum_rank_float), 66)"
    analysis = library.analyze_expression(sample_expr)
    print(f"表达式: {sample_expr}")
    print(f"字段数: {analysis['field_count']} ({', '.join(analysis['fields'])})")
    print(f"操作符数: {analysis['operator_count']} ({', '.join(analysis['operators'])})")
    print(f"窗口期: {analysis['window_sizes']}")
    print(f"复杂度: {analysis['complexity_level']}")
    
    # 保存生成的变体
    library.save_variants(power_pool_variants + regular_variants, 
                         "/Users/mac/WQ-Brain/brainmcp/library_generated_variants.json")
    
    print("\n演示完成！")

if __name__ == "__main__":
    demo()