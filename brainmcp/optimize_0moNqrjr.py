#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
0moNqrjr Alpha优化测试脚本
针对Power Pool Alpha相关性失败问题生成优化变体
"""

import asyncio
import json
import sys
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append('.')

from platform_functions import authenticate, create_multiSim

async def optimize_0moNqrjr():
    """优化0moNqrjr Alpha"""
    print("🔧 0moNqrjr Power Pool Alpha优化测试")
    print("=" * 60)
    
    # 1. 认证
    print("\n1. 🔐 认证...")
    auth_result = await authenticate()
    if 'error' in auth_result:
        print(f"❌ 认证失败: {auth_result['error']}")
        return False
    
    print(f"✅ 认证成功: {auth_result.get('status', '未知')}")
    
    # 2. 原Alpha信息
    print("\n2. 📋 原Alpha分析:")
    original_expression = "ts_av_diff(rank(industry_value_momentum_rank_float), 252)"
    print(f"   表达式: {original_expression}")
    print(f"   问题: PC=0.785 > 0.7，且Sharpe未比最相关Alpha高10%")
    print(f"   Sharpe: 3.20")
    print(f"   类型: Power Pool Alpha（比赛期间优先）")
    
    # 3. 生成8个优化变体（符合8/5-8规则）
    print("\n3. 📝 生成8个优化变体:")
    
    variants = [
        {
            "name": "0moNqrjr_opt1_country",
            "expression": "ts_av_diff(rank(country_value_momentum_rank_float), 66)",
            "description": "字段替换: industry→country，窗口期: 252→66天"
        },
        {
            "name": "0moNqrjr_opt2_zscore",
            "expression": "ts_delta(zscore(ts_backfill(industry_value_momentum_rank_float, 5)), 120)",
            "description": "数据预处理: zscore+backfill，算子: ts_av_diff→ts_delta"
        },
        {
            "name": "0moNqrjr_opt3_dual_field",
            "expression": "ts_av_diff(rank(industry_value_momentum_rank_float), 120) + ts_av_diff(rank(country_value_momentum_rank_float), 66)",
            "description": "双字段组合，非对称窗口期(120+66)"
        },
        {
            "name": "0moNqrjr_opt4_market_tsrank",
            "expression": "ts_rank(rank(market_value_momentum_rank_float), 66)",
            "description": "完全改变: industry→market，ts_av_diff→ts_rank"
        },
        {
            "name": "0moNqrjr_opt5_tail_weight",
            "expression": "ts_av_diff(tail(rank(industry_value_momentum_rank_float), lower=0, upper=0.1, newval=0), 120)",
            "description": "权重控制: tail操作符限制极端权重"
        },
        {
            "name": "0moNqrjr_opt6_group_rank",
            "expression": "group_rank(industry_value_momentum_rank_float, industry)",
            "description": "均值回归策略: group_rank算子"
        },
        {
            "name": "0moNqrjr_opt7_short_term",
            "expression": "ts_delta(zscore(ts_backfill(country_value_momentum_rank_float, 5)), 22)",
            "description": "短期信号: 22天窗口，数据预处理"
        },
        {
            "name": "0moNqrjr_opt8_smooth",
            "expression": "ts_av_diff(rank(ts_mean(industry_value_momentum_rank_float, 5)), 252)",
            "description": "平滑处理: ts_mean预处理，保持原窗口期"
        }
    ]
    
    print(f"生成 {len(variants)} 个优化变体:")
    for i, variant in enumerate(variants, 1):
        print(f"  {i}. {variant['name']}")
        print(f"     表达式: {variant['expression']}")
        print(f"     描述: {variant['description']}")
    
    # 4. 准备模拟参数（Power Pool Alpha设置）
    print("\n4. ⚙️ 准备模拟参数（Power Pool Alpha）:")
    
    simulation_params = {
        "instrument_type": "EQUITY",
        "region": "IND",
        "universe": "TOP500",  # IND区域仅支持TOP500
        "delay": 1,
        "decay": 0,
        "neutralization": "INDUSTRY",  # Power Pool要求Risk Handled
        "truncation": 0.001,
        "test_period": "P0Y0M",
        "unit_handling": "NONE",
        "nan_handling": "NONE",
        "language": "FASTEXPR",
        "visualization": True
    }
    
    print(f"参数设置:")
    for key, value in simulation_params.items():
        print(f"  {key}: {value}")
    
    # 5. 提取表达式列表
    expressions = [variant["expression"] for variant in variants]
    
    # 6. 调用create_multiSim
    print(f"\n5. 🚀 提交多模拟测试（8个变体）...")
    print(f"注意: 根据8/5-8规则，IND区域可以测试5-8个表达式")
    print(f"预计时间: 8+分钟")
    
    try:
        result = await create_multiSim(
            alpha_expressions=expressions,
            **simulation_params
        )
        
        print(f"\n6. 📊 结果分析:")
        
        # 保存结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"0moNqrjr_optimization_results_{timestamp}.json"
        
        result_data = {
            "original_alpha": {
                "id": "0moNqrjr",
                "expression": original_expression,
                "problem": "PC=0.785>0.7且Sharpe未高10%",
                "sharpe": 3.20
            },
            "optimization_variants": variants,
            "simulation_parameters": simulation_params,
            "results": result,
            "timestamp": timestamp
        }
        
        with open(output_file, 'w') as f:
            json.dump(result_data, f, indent=2)
        
        print(f"📁 结果已保存到: {output_file}")
        
        # 分析结果
        if 'error' in result:
            print(f"❌ 模拟失败: {result['error']}")
            return False
        
        if 'simulation_id' in result:
            sim_id = result['simulation_id']
            print(f"✅ 模拟创建成功，ID: {sim_id}")
            
            if 'alphas' in result:
                alphas = result['alphas']
                print(f"\n📈 成功创建 {len(alphas)} 个Alpha:")
                
                success_count = 0
                for i, alpha in enumerate(alphas):
                    if 'alpha_id' in alpha:
                        success_count += 1
                        variant = variants[i]
                        print(f"\nAlpha {i+1}: {alpha.get('alpha_id', '未知')}")
                        print(f"  变体: {variant['name']}")
                        print(f"  表达式: {variant['expression']}")
                        
                        # 检查基本性能指标
                        if 'properties' in alpha:
                            props = alpha['properties']
                            sharpe = props.get('sharpe', '未知')
                            fitness = props.get('fitness', '未知')
                            turnover = props.get('turnover', '未知')
                            robust_sharpe = props.get('robust_universe_sharpe', '未知')
                            
                            print(f"  Sharpe: {sharpe}, Fitness: {fitness}")
                            print(f"  Turnover: {turnover}, Robust Sharpe: {robust_sharpe}")
                            
                            # Power Pool Alpha检查
                            if float(sharpe) >= 1.0 and 0.01 <= float(turnover) <= 0.70:
                                print(f"  ✅ 符合Power Pool基本要求")
                            else:
                                print(f"  ⚠️ 可能不符合Power Pool要求")
                
                print(f"\n🎯 优化成功率: {success_count}/{len(variants)} ({success_count/len(variants)*100:.1f}%)")
                
                # 生成优化建议
                print(f"\n💡 下一步建议:")
                print(f"  1. 检查成功Alpha的相关性(PC和PPAC)")
                print(f"  2. 对通过基本检查的Alpha进行提交检查")
                print(f"  3. Power Pool比赛期间优先提交合格Alpha")
                print(f"  4. 更新队列状态，移除失败变体")
            
            return True
        else:
            print(f"❌ 模拟返回异常结构")
            return False
            
    except Exception as e:
        print(f"\n❌ 模拟过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    print("0moNqrjr Power Pool Alpha优化程序")
    print(f"执行时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
    print("=" * 60)
    
    print("问题: PC=0.785 > 0.7，且Sharpe未比最相关Alpha高10%")
    print("策略: 生成8个优化变体，大幅改变字段、窗口期和算子")
    print("目标: 降低相关性，保持或提升Sharpe")
    
    success = await optimize_0moNqrjr()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 优化测试完成")
        print("下一步: 分析结果，选择最佳变体进行提交")
    else:
        print("❌ 优化测试失败")
        print("建议: 检查表达式语法或平台设置")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())