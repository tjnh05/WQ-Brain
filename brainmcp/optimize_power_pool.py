#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Power Pool Alpha优化脚本
优化O0eRZm57、KPe53rmE、88AVQ6am
"""
import asyncio
import sys
import os
import json
from typing import List, Dict, Any
sys.path.append('.')

from platform_functions import (
    authenticate, create_multiSim, get_submission_check, check_correlation
)

async def optimize_power_pool_alphas():
    """优化Power Pool Alpha"""
    print("=" * 60)
    print("Power Pool Alpha优化开始")
    print("=" * 60)
    
    # 1. 确保认证
    auth_result = await authenticate()
    if auth_result.get('status') != 'authenticated':
        print("❌ 认证失败，无法继续")
        return
    
    print("✅ 认证成功")
    
    # 2. 定义优化变体
    # O0eRZm57 原表达式: ts_av_diff(rank(sector_value_momentum_rank_float), 252)
    o0erzm57_variants = [
        # 变体1: 字段替换 + 窗口期调整
        {
            "name": "O0eRZm57_opt1",
            "expression": "ts_av_diff(rank(industry_value_momentum_rank_float), 120)",
            "description": "字段替换: sector→industry, 窗口期: 252→120"
        },
        # 变体2: 字段替换 + 数据预处理
        {
            "name": "O0eRZm57_opt2", 
            "expression": "ts_av_diff(zscore(ts_backfill(industry_value_momentum_rank_float, 5)), 66)",
            "description": "industry字段 + 数据预处理(zscore+backfill)"
        },
        # 变体3: country字段替换
        {
            "name": "O0eRZm57_opt3",
            "expression": "ts_av_diff(rank(country_value_momentum_rank_float), 252)",
            "description": "字段替换: sector→country, 保持252天窗口"
        },
        # 变体4: 双字段组合降低相关性
        {
            "name": "O0eRZm57_opt4",
            "expression": "ts_av_diff(rank(industry_value_momentum_rank_float), 120) + ts_delta(rank(country_value_momentum_rank_float), 66)",
            "description": "双字段组合: industry+country, 不同窗口期"
        },
        # 变体5: 改变算子类型
        {
            "name": "O0eRZm57_opt5",
            "expression": "ts_delta(rank(industry_value_momentum_rank_float), 66)",
            "description": "算子改变: ts_av_diff→ts_delta, 短期信号"
        },
        # 变体6: 跨数据集组合
        {
            "name": "O0eRZm57_opt6",
            "expression": "ts_av_diff(rank(industry_value_momentum_rank_float), 120) + ts_av_diff(rank(anl4_afv4_eps_mean), 66)",
            "description": "跨数据集: Model(industry) + Analyst(eps_mean)"
        },
        # 变体7: 完全不同的字段
        {
            "name": "O0eRZm57_opt7",
            "expression": "ts_av_diff(rank(mdl110_value), 252)",
            "description": "完全改变字段: sector→mdl110_value"
        },
        # 变体8: 简化版本
        {
            "name": "O0eRZm57_opt8",
            "expression": "rank(industry_value_momentum_rank_float)",
            "description": "简化版本: 仅rank字段"
        }
    ]
    
    # KPe53rmE 原表达式: ts_av_diff(rank(global_value_momentum_rank_float), 252)
    kpe53rme_variants = [
        # 变体1: 字段替换
        {
            "name": "KPe53rmE_opt1",
            "expression": "ts_av_diff(rank(industry_value_momentum_rank_float), 120)",
            "description": "字段替换: global→industry, 窗口期调整"
        },
        # 变体2: country字段
        {
            "name": "KPe53rmE_opt2",
            "expression": "ts_av_diff(rank(country_value_momentum_rank_float), 66)",
            "description": "字段替换: global→country, 短期窗口"
        },
        # 变体3: 数据预处理
        {
            "name": "KPe53rmE_opt3",
            "expression": "ts_av_diff(zscore(ts_backfill(industry_value_momentum_rank_float, 5)), 252)",
            "description": "industry字段 + 数据预处理"
        }
    ]
    
    # 88AVQ6am 原表达式: ts_av_diff(rank(sector_value_momentum_rank_float), 504)
    _88avq6am_variants = [
        # 变体1: 缩短窗口期
        {
            "name": "88AVQ6am_opt1",
            "expression": "ts_av_diff(rank(sector_value_momentum_rank_float), 120)",
            "description": "缩短窗口期: 504→120"
        },
        # 变体2: 字段替换
        {
            "name": "88AVQ6am_opt2",
            "expression": "ts_av_diff(rank(industry_value_momentum_rank_float), 252)",
            "description": "字段替换: sector→industry"
        },
        # 变体3: 改变算子
        {
            "name": "88AVQ6am_opt3",
            "expression": "ts_delta(rank(industry_value_momentum_rank_float), 66)",
            "description": "字段替换 + 算子改变"
        }
    ]
    
    # 3. 选择最关键的变体进行测试（先测试4个）
    # 根据IFLOW.md的8/5-8规则，IND区域可以测试5-8个表达式
    # 我们先测试4个关键变体
    key_variants = [
        o0erzm57_variants[0],  # 变体1: industry字段替换
        o0erzm57_variants[1],  # 变体2: 数据预处理版本
        kpe53rme_variants[0],  # KPe53rmE变体1
        _88avq6am_variants[0]  # 88AVQ6am变体1
    ]
    
    print(f"\n📊 准备测试 {len(key_variants)} 个关键优化变体")
    for i, variant in enumerate(key_variants, 1):
        print(f"  {i}. {variant['name']}: {variant['expression']}")
        print(f"     描述: {variant['description']}")
    
    # 4. 准备模拟参数（Power Pool Alpha设置）
    simulation_params = {
        "instrument_type": "EQUITY",
        "region": "IND",
        "universe": "TOP500",  # IND区域仅支持TOP500
        "delay": 1,
        "decay": 0,
        "neutralization": "INDUSTRY",  # Power Pool要求Risk Handled，IND区域使用INDUSTRY
        "truncation": 0.001,
        "test_period": "P0Y0M",
        "unit_handling": "NONE", 
        "nan_handling": "NONE",
        "language": "FASTEXPR",
        "visualization": True
    }
    
    # 5. 提取表达式列表
    expressions = [variant["expression"] for variant in key_variants]
    
    print(f"\n🚀 开始批量模拟测试...")
    print(f"参数设置: {json.dumps(simulation_params, indent=2)}")
    
    # 6. 调用create_multiSim
    try:
        print(f"\n📤 提交 {len(expressions)} 个表达式进行多模拟测试")
        print(f"注意: create_multiSim函数会自动等待模拟完成（可能需要8+分钟）")
        
        multi_sim_result = await create_multiSim(
            alpha_expressions=expressions,
            instrument_type=simulation_params["instrument_type"],
            region=simulation_params["region"],
            universe=simulation_params["universe"],
            delay=simulation_params["delay"],
            decay=simulation_params["decay"],
            neutralization=simulation_params["neutralization"],
            truncation=simulation_params["truncation"],
            test_period=simulation_params["test_period"],
            unit_handling=simulation_params["unit_handling"],
            nan_handling=simulation_params["nan_handling"],
            language=simulation_params["language"],
            visualization=simulation_params["visualization"]
        )
        
        print(f"\n多模拟结果: {json.dumps(multi_sim_result, indent=2)}")
        
        # 7. 保存结果
        if 'simulation_id' in multi_sim_result:
            sim_id = multi_sim_result['simulation_id']
            output_file = f"power_pool_optimization_results_{sim_id}.json"
            
            result_data = {
                "simulation_id": sim_id,
                "parameters": simulation_params,
                "variants": key_variants,
                "results": multi_sim_result
            }
            
            with open(output_file, 'w') as f:
                json.dump(result_data, f, indent=2)
            
            print(f"\n📁 结果已保存到: {output_file}")
            
            # 分析结果
            print("\n📈 结果分析:")
            if 'alphas' in multi_sim_result:
                alphas = multi_sim_result['alphas']
                print(f"成功创建 {len(alphas)} 个Alpha")
                
                for i, alpha in enumerate(alphas):
                    if 'alpha_id' in alpha:
                        print(f"\nAlpha {i+1}: {alpha.get('alpha_id', '未知')}")
                        print(f"  表达式: {key_variants[i]['expression']}")
                        print(f"  名称: {key_variants[i]['name']}")
                        
                        # 检查基本性能指标
                        if 'properties' in alpha:
                            props = alpha['properties']
                            sharpe = props.get('sharpe', '未知')
                            fitness = props.get('fitness', '未知')
                            turnover = props.get('turnover', '未知')
                            print(f"  Sharpe: {sharpe}, Fitness: {fitness}, Turnover: {turnover}")
            
            return multi_sim_result
        else:
            print(f"❌ 多模拟创建失败或返回异常")
            if 'error' in multi_sim_result:
                print(f"错误信息: {multi_sim_result['error']}")
            return multi_sim_result
            
    except Exception as e:
        print(f"❌ 模拟过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

async def check_alpha_correlation(alpha_id: str):
    """检查Alpha相关性"""
    print(f"\n🔍 检查Alpha {alpha_id} 的相关性...")
    try:
        correlation_result = await check_correlation(alpha_id=alpha_id)
        print(f"相关性结果: {correlation_result}")
        return correlation_result
    except Exception as e:
        print(f"❌ 相关性检查失败: {str(e)}")
        return {"error": str(e)}

async def submission_check(alpha_id: str):
    """提交前检查"""
    print(f"\n📋 检查Alpha {alpha_id} 的提交状态...")
    try:
        check_result = await get_submission_check(alpha_id=alpha_id)
        print(f"提交检查结果: {check_result}")
        return check_result
    except Exception as e:
        print(f"❌ 提交检查失败: {str(e)}")
        return {"error": str(e)}

async def main():
    """主函数"""
    print("Power Pool Alpha优化程序")
    print("当前日期: 2026年1月9日（Power Pool比赛期间）")
    print("=" * 60)
    
    # 执行优化
    optimization_results = await optimize_power_pool_alphas()
    
    if optimization_results and 'error' not in optimization_results:
        print("\n" + "=" * 60)
        print("优化完成！")
        print("=" * 60)
        
        # 分析结果并给出建议
        print("\n📈 优化结果分析:")
        print("1. 检查每个变体的Sharpe、Fitness、Turnover")
        print("2. 验证Power Pool复杂度要求（操作符≤8，字段≤3）")
        print("3. 进行相关性检查（PC < 0.7, PPAC < 0.5）")
        print("4. 通过提交检查后立即提交（比赛期间优先）")
        
        # 建议下一步操作
        print("\n🎯 建议下一步:")
        print("1. 从成功变体中选择最佳候选")
        print("2. 进行相关性检查确保PC < 0.7")
        print("3. 验证Power Pool属性设置")
        print("4. 立即提交（利用比赛期间优势）")
        
    else:
        print("\n❌ 优化过程出现问题")
        if optimization_results:
            print(f"错误信息: {optimization_results.get('error', '未知错误')}")

if __name__ == "__main__":
    asyncio.run(main())
