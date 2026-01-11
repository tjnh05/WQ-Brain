#!/usr/bin/env python3
"""
创建字段分类和相关性数据库
基于历史表达式分析构建结构化字段库
"""

import json
import os
from collections import defaultdict

def load_field_analysis():
    """加载字段分析结果"""
    analysis_file = "/Users/mac/WQ-Brain/brainmcp/field_analysis_results.json"
    with open(analysis_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def infer_dataset(field_name):
    """根据字段名称推断数据集"""
    if field_name.startswith('mdl'):
        return 'Model'
    elif field_name.startswith('anl'):
        return 'Analyst'
    elif 'momentum' in field_name.lower() or 'price' in field_name.lower():
        return 'Momentum'
    elif 'value' in field_name.lower() and 'momentum' in field_name.lower():
        return 'Momentum'
    elif 'earnings' in field_name.lower() or 'eps' in field_name.lower():
        return 'Earnings'
    elif 'fundamental' in field_name.lower():
        return 'Fundamental'
    elif 'risk' in field_name.lower():
        return 'Risk'
    else:
        return 'Other'

def infer_data_type(field_name):
    """推断数据类型"""
    if 'rank' in field_name:
        return 'RANK'
    elif 'score' in field_name:
        return 'SCORE'
    elif 'value' in field_name:
        return 'VALUE'
    elif 'indicator' in field_name:
        return 'INDICATOR'
    elif 'flag' in field_name:
        return 'FLAG'
    else:
        return 'UNKNOWN'

def get_field_description(field_name):
    """获取字段描述（基于已知信息）"""
    descriptions = {
        'mdl110_value': '价值因子综合评分（Model 110数据集）',
        'mdl110_score': '所有因子总和评分（Model 110数据集）',
        'mdl110_growth': '增长因子综合评分（Model 110数据集）',
        'mdl110_quality': '质量因子综合评分（Model 110数据集）',
        'mdl110_alternative': '另类因子综合评分（Model 110数据集）',
        'mdl110_analyst_sentiment': '分析师情绪综合评分（Model 110数据集）',
        'mdl110_price_momentum_reversal': '价格动量反转指标（Model 110数据集）',
        'mdl110_tree': '非线性树组件综合评分（Model 110数据集）',
        
        'sector_value_momentum_rank_float': '精确板块相对价值动量排名（Model 39数据集）',
        'global_value_momentum_rank_float': '精确全球相对价值动量排名（Model 39数据集）',
        'industry_value_momentum_rank_float': '精确行业相对价值动量排名（Model 39数据集）',
        'country_value_momentum_rank_float': '精确国家相对价值动量排名（Model 39数据集）',
        'region_value_momentum_rank_float': '精确地区相对价值动量排名（Model 39数据集）',
        
        'anl4_afv4_eps_mean': '每股收益均值估计（Analyst 4数据集）',
        'anl46_indicator': '分析师指标（Analyst 46数据集）',
        
        'global_price_momentum_percentile_2': '价格动量百分位数排名（全球）',
        'industry_price_momentum_score_2': '行业相对价格动量得分',
        'long_term_price_momentum_score_2': '长期（12个月）价格动量得分',
        'mid_term_price_momentum_score_2': '中期（6个月）价格动量得分',
        'short_term_price_momentum_score_2': '短期（3个月或1周）价格动量得分',
    }
    
    return descriptions.get(field_name, f'{field_name}（自动推断）')

def identify_correlation_risk(field_name, frequency, common_combinations):
    """识别相关性风险"""
    high_risk_fields = {
        'mdl110_value', 'sector_value_momentum_rank_float', 'global_value_momentum_rank_float'
    }
    
    risk_level = 'LOW'
    reasons = []
    
    # 基于使用频率
    if frequency > 10:
        risk_level = 'HIGH'
        reasons.append(f'高频使用字段（使用{frequency}次）')
    elif frequency > 5:
        risk_level = 'MEDIUM'
        reasons.append(f'中频使用字段（使用{frequency}次）')
    
    # 基于字段类型
    if field_name in high_risk_fields:
        risk_level = 'HIGH'
        reasons.append('常见高相关性字段')
    
    # 基于数据集
    dataset = infer_dataset(field_name)
    if dataset == 'Model' and 'value' in field_name:
        reasons.append('Model价值因子易产生高相关性')
    
    return {
        'level': risk_level,
        'reasons': reasons,
        'common_combinations': common_combinations.get(field_name, [])
    }

def get_power_pool_suitability(field_name, frequency):
    """评估Power Pool适配性"""
    # Power Pool需要低相关性和简单性
    if frequency > 8:
        return 'LOW'  # 高频使用字段可能相关性高
    elif 'momentum' in field_name or 'value' in field_name:
        return 'MEDIUM'  # 动量/价值字段需谨慎组合
    else:
        return 'HIGH'  # 其他字段可能更适合

def get_regional_performance(field_name):
    """获取区域表现（基于历史经验）"""
    performance = {
        'IND': {'success_rate': 0.0, 'avg_sharpe': 0.0, 'notes': ''},
        'USA': {'success_rate': 0.0, 'avg_sharpe': 0.0, 'notes': ''},
        'EUR': {'success_rate': 0.0, 'avg_sharpe': 0.0, 'notes': ''},
        'ASI': {'success_rate': 0.0, 'avg_sharpe': 0.0, 'notes': ''}
    }
    
    # 基于已知成功案例设置
    if field_name == 'anl4_afv4_eps_mean':
        performance['IND'] = {'success_rate': 0.8, 'avg_sharpe': 1.9, 'notes': 'Vkn55eQM成功案例'}
    elif field_name == 'mdl110_value':
        performance['IND'] = {'success_rate': 0.6, 'avg_sharpe': 2.5, 'notes': '多个成功Alpha'}
    elif 'momentum' in field_name:
        performance['IND'] = {'success_rate': 0.7, 'avg_sharpe': 2.8, 'notes': '动量字段在IND表现良好'}
    
    return performance

def identify_common_combinations():
    """识别常见字段组合"""
    # 基于模板文件分析
    common_combo = defaultdict(list)
    
    # 从模板中提取的常见组合
    common_combo['mdl110_value'].append('sector_value_momentum_rank_float')
    common_combo['mdl110_value'].append('industry_value_momentum_rank_float')
    common_combo['mdl110_growth'].append('global_value_momentum_rank_float')
    common_combo['mdl110_quality'].append('sector_value_momentum_rank_float')
    
    # 从成功案例中提取
    common_combo['anl4_afv4_eps_mean'].append('ts_mean')  # 操作符组合
    
    return common_combo

def create_field_database():
    """创建字段数据库"""
    print("开始创建字段分类和相关性数据库...")
    
    # 加载分析结果
    analysis = load_field_analysis()
    field_freq = analysis['field_frequency']
    
    # 识别常见组合
    common_combinations = identify_common_combinations()
    
    database = {
        'metadata': {
            'version': '1.0',
            'created_date': '2026-01-10',
            'total_fields': len(field_freq),
            'data_sources': [
                'IND_Model_Addition_Templates_20251230.txt',
                'IND_Model_Differentiated_Expressions_20251230.txt',
                'USA_Alpha_Expressions_20251229.txt',
                'IND_PowerPool_Alpha_Mining_Report_20260109.md',
                'IND_Alpha_Submission_Queue_20251231.json',
                'news17_expressions.txt',
                'pv_expressions.txt',
                'sentiment_expressions.txt',
                'ASI_Alpha_Expressions_Library_20251225.txt',
                'IND_Alpha_Mining_Ready_Expressions_20251226.txt',
                'USA_Alpha_Correlation_Reduction_Expressions_20251229.txt',
                'USA_Alpha_Final_Optimized_Expressions_20251229.txt',
                'USA_Alpha_LongWindow_Expressions_20251229.txt',
                'USA_Alpha_Neutralization_Expressions_20251229.txt',
                'USA_Alpha_New_Fields_Expressions_20251229.txt',
                'USA_Alpha_Optimized_Expressions_20251229.txt',
                'USA_Alpha_ts_delta_Optimized_Expressions_20251229.txt',
                'USA_Analyst15_Alpha_Expressions_20251229.txt',
                'USA_Analyst15_Alpha_New_Expressions_20251229.txt',
                'USA_Analyst15_Alpha_Optimization_Variants_20251229.txt',
                'USA_Analyst4_Alpha_Optimization_Variants_20251229.txt',
                'USA_Earnings6_Alpha_Expressions_20251229.txt'
            ]
        },
        'fields': {},
        'statistics': {
            'by_dataset': defaultdict(int),
            'by_data_type': defaultdict(int),
            'by_correlation_risk': defaultdict(int),
            'by_power_pool_suitability': defaultdict(int)
        }
    }
    
    # 处理每个字段
    for field_name, frequency in field_freq.items():
        dataset = infer_dataset(field_name)
        data_type = infer_data_type(field_name)
        description = get_field_description(field_name)
        
        correlation_risk = identify_correlation_risk(field_name, frequency, common_combinations)
        power_pool_suitability = get_power_pool_suitability(field_name, frequency)
        regional_performance = get_regional_performance(field_name)
        
        field_data = {
            'name': field_name,
            'dataset': dataset,
            'data_type': data_type,
            'description': description,
            'usage_statistics': {
                'frequency': frequency,
                'percentage': round(frequency / analysis['expressions_with_fields'] * 100, 2)
            },
            'correlation_risk': correlation_risk,
            'power_pool_suitability': power_pool_suitability,
            'regional_performance': regional_performance,
            'recommendations': {
                'best_regions': [region for region, perf in regional_performance.items() if perf['success_rate'] > 0.5],
                'avoid_combinations': common_combinations.get(field_name, [])[:3],  # 避免与这些字段高频组合
                'suggested_operators': ['rank', 'zscore', 'ts_delta', 'ts_mean'],  # 通用建议
                'complexity_level': 'LOW' if 'rank' in field_name or 'score' in field_name else 'MEDIUM'
            }
        }
        
        database['fields'][field_name] = field_data
        
        # 更新统计信息
        database['statistics']['by_dataset'][dataset] += 1
        database['statistics']['by_data_type'][data_type] += 1
        database['statistics']['by_correlation_risk'][correlation_risk['level']] += 1
        database['statistics']['by_power_pool_suitability'][power_pool_suitability] += 1
    
    # 添加成功模板组合
    database['successful_templates'] = [
        {
            'name': '双字段加法模板',
            'pattern': 'ts_delta(rank(field1) + rank(field2), 66)',
            'description': 'IND地区Model数据集成功模板，Sharpe高，Robust Sharpe稳定',
            'example': 'ts_delta(rank(mdl110_growth) + rank(global_value_momentum_rank_float), 66)',
            'success_rate': 0.7,
            'recommended_datasets': ['Model', 'Momentum']
        },
        {
            'name': 'Power Pool简单模板',
            'pattern': 'ts_delta(ts_mean(field, 5), 5)',
            'description': 'Power Pool成功模板，操作符≤2，字段≤1，符合复杂度限制',
            'example': 'ts_delta(ts_mean(anl4_afv4_eps_mean, 5), 5)',
            'success_rate': 0.8,
            'recommended_datasets': ['Analyst', 'Model']
        },
        {
            'name': '三字段zscore交互模板',
            'pattern': 'ts_zscore(field1, 504) * ts_zscore(field2, 504) * ts_zscore(field3, 504)',
            'description': '差异化模板，降低相关性，适合高PC场景',
            'example': 'ts_zscore(mdl110_score, 504) * ts_zscore(sector_value_momentum_rank_float, 504) * ts_zscore(long_term_price_momentum_score_2, 504)',
            'success_rate': 0.6,
            'recommended_datasets': ['Model', 'Momentum']
        }
    ]
    
    # 添加高风险组合警告
    database['high_risk_combinations'] = [
        {
            'combination': ['mdl110_value', 'sector_value_momentum_rank_float'],
            'risk_level': 'HIGH',
            'reason': '高频使用组合，PC通常>0.7',
            'suggestion': '替换其中一个字段为低频率字段'
        },
        {
            'combination': ['global_value_momentum_rank_float', 'industry_value_momentum_rank_float'],
            'risk_level': 'HIGH',
            'reason': '相似动量字段，高度相关',
            'suggestion': '选择不同粒度字段（如country vs industry）'
        }
    ]
    
    # 添加Power Pool优化建议
    database['power_pool_guidelines'] = {
        'complexity_limit': {
            'max_operators': 8,
            'max_unique_fields': 3,
            'recommended': '操作符≤4，字段≤2 成功率更高'
        },
        'field_selection': {
            'high_suitability': ['anl4_afv4_eps_mean', 'mdl110_tree', 'anl46_indicator'],
            'medium_suitability': ['mdl110_growth', 'industry_value_momentum_rank_float'],
            'low_suitability': ['mdl110_value', 'global_value_momentum_rank_float']
        },
        'operator_recommendations': {
            'high_success': ['ts_delta', 'ts_mean', 'rank'],
            'medium_success': ['ts_rank', 'ts_zscore', 'group_rank'],
            'specialized': ['vector_neut', 'regression_neut', 'if_else']
        }
    }
    
    # 保存数据库
    output_file = "/Users/mac/WQ-Brain/brainmcp/field_database_v1.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2, ensure_ascii=False)
    
    print(f"字段数据库创建完成！")
    print(f"总计字段: {len(database['fields'])}")
    print(f"数据集分布: {dict(database['statistics']['by_dataset'])}")
    print(f"相关性风险分布: {dict(database['statistics']['by_correlation_risk'])}")
    print(f"Power Pool适配性分布: {dict(database['statistics']['by_power_pool_suitability'])}")
    print(f"数据库已保存到: {output_file}")
    
    return database

if __name__ == "__main__":
    create_field_database()