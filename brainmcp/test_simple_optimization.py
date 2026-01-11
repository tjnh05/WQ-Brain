#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试Power Pool Alpha优化变体
"""

import asyncio
import json
import sys
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append('.')

from platform_functions import authenticate, create_multiSim

async def test_simple_variants():
    """测试简单的优化变体"""
    print("🧪 测试Power Pool Alpha优化变体")
    print("=" * 60)
    
    # 1. 认证
    print("\n1. 🔐 认证...")
    auth_result = await authenticate()
    if 'error' in auth_result:
        print(f"❌ 认证失败: {auth_result['error']}")
        return False
    
    print(f"✅ 认证成功: {auth_result.get('status', '未知')}")
    
    # 2. 准备优化变体
    print("\n2. 📝 准备优化变体...")
    
    # 基于O0eRZm57的优化变体
    variants = [
        {
            "name": "O0eRZm57_opt_simple",
            "expression": "rank(industry_value_momentum_rank_float)",
            "description": "最简单的industry字段版本"
        },
        {
            "name": "O0eRZm57_opt_tsdiff",
            "expression": "ts_delta(rank(industry_value_momentum_rank_float), 66)",
            "description": "使用ts_delta替代ts_av_diff，66天窗口"
        },
        {
            "name": "KPe53rmE_opt_simple", 
            "expression": "rank(country_value_momentum_rank_float)",
            "description": "使用country字段替代global"
        },
        {
            "name": "88AVQ6am_opt_short",
            "expression": "ts_delta(rank(sector_value_momentum_rank_float), 66)",
            "description": "缩短窗口期，使用ts_delta"
        }
    ]
    
    print(f"准备测试 {len(variants)} 个变体:")
    for i, variant in enumerate(variants, 1):
        print(f"  {i}. {variant['name']}: {variant['expression']}")
    
    # 3. 准备模拟参数
    print("\n3. ⚙️ 准备模拟参数...")
    
    # 根据IFLOW.md，IND区域使用TOP500 Universe
    simulation_params = {
        "instrument_type": "EQUITY",
        "region": "IND",
        "universe": "TOP500",
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
    
    print(f"模拟参数:")
    for key, value in simulation_params.items():
        print(f"  {key}: {value}")
    
    # 4. 提取表达式
    expressions = [variant["expression"] for variant in variants]
    
    # 5. 调用create_multiSim
    print(f"\n4. 🚀 提交多模拟测试...")
    print(f"注意: 这可能需要几分钟时间")
    
    try:
        result = await create_multiSim(
            alpha_expressions=expressions,
            **simulation_params
        )
        
        print(f"\n5. 📊 结果分析:")
        print(json.dumps(result, indent=2))
        
        # 保存结果
        if 'simulation_id' in result:
            sim_id = result['simulation_id']
            output_file = f"simple_optimization_test_{sim_id}.json"
            
            result_data = {
                "simulation_id": sim_id,
                "timestamp": datetime.now().isoformat(),
                "parameters": simulation_params,
                "variants": variants,
                "results": result
            }
            
            with open(output_file, 'w') as f:
                json.dump(result_data, f, indent=2)
            
            print(f"\n📁 结果已保存到: {output_file}")
            
            # 简单分析
            if 'alphas' in result:
                alphas = result['alphas']
                print(f"\n✅ 成功创建 {len(alphas)} 个Alpha")
                
                success_count = 0
                for i, alpha in enumerate(alphas):
                    if 'alpha_id' in alpha:
                        success_count += 1
                        print(f"\nAlpha {i+1}: {alpha.get('alpha_id', '未知')}")
                        print(f"  变体: {variants[i]['name']}")
                        print(f"  表达式: {variants[i]['expression']}")
                        
                        if 'properties' in alpha:
                            props = alpha['properties']
                            sharpe = props.get('sharpe', '未知')
                            fitness = props.get('fitness', '未知')
                            turnover = props.get('turnover', '未知')
                            print(f"  Sharpe: {sharpe}, Fitness: {fitness}, Turnover: {turnover}")
                
                print(f"\n📈 成功率: {success_count}/{len(variants)} ({success_count/len(variants)*100:.1f}%)")
            
            return True
        else:
            print(f"\n❌ 模拟失败或返回异常")
            if 'error' in result:
                print(f"错误信息: {result['error']}")
            return False
            
    except Exception as e:
        print(f"\n❌ 模拟过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    print("Power Pool Alpha简单优化测试")
    print(f"当前日期: {datetime.now().strftime('%Y年%m月%d日')}")
    print("=" * 60)
    
    success = await test_simple_variants()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 测试完成")
    else:
        print("❌ 测试失败")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())
