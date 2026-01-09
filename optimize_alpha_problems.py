#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alpha问题优化脚本
优化KPe53rmE和A16LxZ1d的问题：
1. KPe53rmE: PPAC > 0.7 且 PC > 0.7
2. A16LxZ1d: IS收益曲线两端是一条直线（表现不好）
"""

import json
from datetime import datetime

def analyze_problems():
    """分析Alpha问题"""
    print("=" * 60)
    print("Alpha问题诊断与优化")
    print("=" * 60)
    
    # 问题分析
    problems = {
        "KPe53rmE": {
            "alpha_id": "KPe53rmE",
            "original_expression": "ts_av_diff(rank(global_value_momentum_rank_float), 252)",
            "problems": [
                "PPAC > 0.7 (Power Pool内部自相关性过高)",
                "PC > 0.7 (生产相关性过高)",
                "使用global_value_momentum_rank_float字段可能与其他Alpha高度相关"
            ],
            "root_cause": "字段选择问题 - global_value_momentum_rank_float可能被多个Alpha使用，导致相关性过高"
        },
        "A16LxZ1d": {
            "alpha_id": "A16LxZ1d",
            "original_expression": "ts_av_diff(rank(global_value_momentum_rank_float), 504)",
            "problems": [
                "IS收益曲线两端是一条直线（表现不好）",
                "窗口期过长（504天）导致信号过于平滑",
                "可能缺乏短期信号响应"
            ],
            "root_cause": "窗口期问题 - 504天窗口期过长，信号过于平滑，缺乏短期动态"
        }
    }
    
    return problems

def generate_optimization_variants(problems):
    """生成优化变体"""
    print("\n" + "=" * 60)
    print("优化变体生成")
    print("=" * 60)
    
    variants = {
        "KPe53rmE": [],
        "A16LxZ1d": []
    }
    
    # KPe53rmE优化变体（解决相关性问题）
    variants["KPe53rmE"] = [
        {
            "name": "字段替换变体1",
            "expression": "ts_av_diff(rank(industry_value_momentum_rank_float), 252)",
            "changes": [
                "global_value_momentum_rank_float → industry_value_momentum_rank_float",
                "从全球级别改为行业级别，降低相关性"
            ],
            "expected_benefits": [
                "降低与使用global字段的Alpha的相关性",
                "保持252天窗口期的稳定性",
                "行业级别数据可能更有区分度"
            ]
        },
        {
            "name": "字段替换变体2",
            "expression": "ts_av_diff(rank(country_value_momentum_rank_float), 252)",
            "changes": [
                "global_value_momentum_rank_float → country_value_momentum_rank_float",
                "从全球级别改为国家级别"
            ],
            "expected_benefits": [
                "进一步降低相关性",
                "国家级别数据可能更稳定",
                "与行业级别数据形成互补"
            ]
        },
        {
            "name": "预处理优化变体",
            "expression": "ts_av_diff(zscore(ts_backfill(industry_value_momentum_rank_float, 5)), 120)",
            "changes": [
                "添加ts_backfill(x, 5)处理缺失值",
                "使用zscore()标准化数据",
                "窗口期252天→120天"
            ],
            "expected_benefits": [
                "数据预处理提升稳定性",
                "标准化使信号更均匀",
                "中等窗口期平衡稳定性和敏感性"
            ]
        }
    ]
    
    # A16LxZ1d优化变体（解决信号平滑问题）
    variants["A16LxZ1d"] = [
        {
            "name": "窗口期优化变体1",
            "expression": "ts_av_diff(rank(industry_value_momentum_rank_float), 120)",
            "changes": [
                "global_value_momentum_rank_float → industry_value_momentum_rank_float",
                "窗口期504天→120天"
            ],
            "expected_benefits": [
                "缩短窗口期避免信号过于平滑",
                "行业字段替代全球字段",
                "提升信号响应速度"
            ]
        },
        {
            "name": "算子替换变体",
            "expression": "ts_delta(rank(industry_value_momentum_rank_float), 66)",
            "changes": [
                "ts_av_diff → ts_delta",
                "窗口期504天→66天"
            ],
            "expected_benefits": [
                "ts_delta提供更敏感的信号变化",
                "66天窗口期适合中期动量",
                "避免长窗口期的过度平滑"
            ]
        },
        {
            "name": "双字段组合变体",
            "expression": "ts_mean(rank(industry_value_momentum_rank_float), 22) + ts_delta(rank(country_value_momentum_rank_float), 66)",
            "changes": [
                "双字段组合：industry + country",
                "混合算子：ts_mean + ts_delta",
                "不同窗口期：22天 + 66天"
            ],
            "expected_benefits": [
                "多维度信号增强稳定性",
                "混合算子提供不同时间尺度信号",
                "避免单一窗口期的局限性"
            ]
        }
    ]
    
    return variants

def generate_test_plan(problems, variants):
    """生成测试计划"""
    print("\n" + "=" * 60)
    print("优化测试计划")
    print("=" * 60)
    
    test_plan = {
        "测试目标": "解决KPe53rmE和A16LxZ1d的问题，生成新的优化变体",
        "测试策略": "批量生成8个变体，使用create_multi_simulation测试",
        "优先级": "高 - 这两个都是Power Pool Alpha候选，比赛期间需要高质量Alpha"
    }
    
    # 组合所有变体
    all_variants = []
    
    for alpha_id in ["KPe53rmE", "A16LxZ1d"]:
        print(f"\n🔍 {alpha_id}优化变体:")
        for i, variant in enumerate(variants[alpha_id], 1):
            variant_id = f"{alpha_id}_opt{i}"
            all_variants.append({
                "variant_id": variant_id,
                "based_on": alpha_id,
                "name": variant["name"],
                "expression": variant["expression"],
                "changes": variant["changes"],
                "expected_benefits": variant["expected_benefits"]
            })
            
            print(f"  {i}. {variant['name']}")
            print(f"     表达式: {variant['expression']}")
            print(f"     主要改变: {', '.join(variant['changes'])}")
    
    # 生成8个测试表达式（4+4组合）
    test_expressions = []
    for variant in all_variants[:8]:  # 取前8个变体
        test_expressions.append(variant["expression"])
    
    test_plan["test_expressions"] = test_expressions
    test_plan["total_variants"] = len(all_variants)
    test_plan["selected_for_test"] = 8
    
    return test_plan

def update_queue_file(problems, variants, test_plan):
    """更新队列文件建议"""
    print("\n" + "=" * 60)
    print("队列更新建议")
    print("=" * 60)
    
    update_suggestions = {
        "KPe53rmE": {
            "current_status": "pending_alphas中，但PPAC>0.7且PC>0.7",
            "recommended_action": "移动到high_correlation_alphas，添加优化变体记录",
            "optimization_notes": "需要完全改变字段组合，避免使用global_value_momentum_rank_float"
        },
        "A16LxZ1d": {
            "current_status": "pending_alphas中，但IS收益曲线表现不佳",
            "recommended_action": "移动到failed_alphas或添加性能警告",
            "optimization_notes": "需要缩短窗口期，改变算子结构，避免信号过度平滑"
        }
    }
    
    return update_suggestions

def main():
    """主函数"""
    print("🚀 Alpha问题优化脚本")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 分析问题
    problems = analyze_problems()
    
    # 生成优化变体
    variants = generate_optimization_variants(problems)
    
    # 生成测试计划
    test_plan = generate_test_plan(problems, variants)
    
    # 队列更新建议
    update_suggestions = update_queue_file(problems, variants, test_plan)
    
    print("\n" + "=" * 60)
    print("🎯 执行建议")
    print("=" * 60)
    
    print("1. 立即更新队列文件:")
    print("   - 将KPe53rmE移动到high_correlation_alphas")
    print("   - 为A16LxZ1d添加性能警告")
    
    print("\n2. 执行优化测试:")
    print("   - 使用create_multi_simulation测试8个优化变体")
    print("   - 重点关注相关性检查和IS收益曲线")
    
    print("\n3. 监控测试结果:")
    print("   - 检查新变体的PPAC和PC值")
    print("   - 验证IS收益曲线是否改善")
    print("   - 评估Robust Universe Sharpe")
    
    print("\n4. 后续优化:")
    print("   - 如果变体成功，添加到队列")
    print("   - 如果失败，分析原因并调整策略")
    
    print("\n" + "=" * 60)
    print("📋 生成的测试表达式（8个）:")
    print("=" * 60)
    for i, expr in enumerate(test_plan["test_expressions"], 1):
        print(f"{i}. {expr}")
    
    print("\n✅ 优化方案生成完成！")

if __name__ == "__main__":
    main()
