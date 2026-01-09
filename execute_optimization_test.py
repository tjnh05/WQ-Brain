#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行优化测试脚本
测试KPe53rmE和A16LxZ1d的优化变体
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# 添加路径以便导入platform_functions
sys.path.append('/Users/mac/WQ-Brain/brainmcp')

async def test_optimization_variants():
    """测试优化变体"""
    print("=" * 60)
    print("🚀 执行优化测试")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 优化变体表达式（8个）
    optimization_variants = [
        # KPe53rmE优化变体（解决相关性问题）
        {
            "name": "KPe53rmE_opt1",
            "expression": "ts_av_diff(rank(industry_value_momentum_rank_float), 252)",
            "description": "字段替换：global→industry，保持252天窗口",
            "target_problem": "解决KPe53rmE相关性问题"
        },
        {
            "name": "KPe53rmE_opt2", 
            "expression": "ts_av_diff(rank(country_value_momentum_rank_float), 252)",
            "description": "字段替换：global→country，保持252天窗口",
            "target_problem": "解决KPe53rmE相关性问题"
        },
        {
            "name": "KPe53rmE_opt3",
            "expression": "ts_av_diff(zscore(ts_backfill(industry_value_momentum_rank_float, 5)), 120)",
            "description": "预处理优化：backfill+zscore，120天窗口",
            "target_problem": "解决KPe53rmE相关性问题"
        },
        
        # A16LxZ1d优化变体（解决信号平滑问题）
        {
            "name": "A16LxZ1d_opt1",
            "expression": "ts_av_diff(rank(industry_value_momentum_rank_float), 120)",
            "description": "窗口期优化：504天→120天，字段替换",
            "target_problem": "解决A16LxZ1d信号平滑问题"
        },
        {
            "name": "A16LxZ1d_opt2",
            "expression": "ts_delta(rank(industry_value_momentum_rank_float), 66)",
            "description": "算子替换：ts_av_diff→ts_delta，66天窗口",
            "target_problem": "解决A16LxZ1d信号平滑问题"
        },
        {
            "name": "A16LxZ1d_opt3",
            "expression": "ts_mean(rank(industry_value_momentum_rank_float), 22) + ts_delta(rank(country_value_momentum_rank_float), 66)",
            "description": "双字段组合：industry+country，混合算子",
            "target_problem": "解决A16LxZ1d信号平滑问题"
        },
        
        # 额外变体（凑齐8个）
        {
            "name": "extra_opt1",
            "expression": "ts_av_diff(zscore(ts_backfill(country_value_momentum_rank_float, 5)), 66)",
            "description": "额外变体：country字段，预处理，66天窗口",
            "target_problem": "增强测试多样性"
        },
        {
            "name": "extra_opt2",
            "expression": "ts_delta(rank(country_value_momentum_rank_float), 22) + ts_mean(rank(industry_value_momentum_rank_float), 120)",
            "description": "额外变体：双字段反向组合，不同窗口期",
            "target_problem": "增强测试多样性"
        }
    ]
    
    # 显示测试计划
    print("\n📋 测试计划:")
    print(f"  总变体数: {len(optimization_variants)}")
    print(f"  目标问题: KPe53rmE(相关性) + A16LxZ1d(信号平滑)")
    
    print("\n🔍 测试变体详情:")
    for i, variant in enumerate(optimization_variants, 1):
        print(f"  {i}. {variant['name']}")
        print(f"     表达式: {variant['expression']}")
        print(f"     描述: {variant['description']}")
        print(f"     目标问题: {variant['target_problem']}")
        print()
    
    # 准备测试参数
    test_params = {
        "region": "IND",
        "universe": "TOP500",
        "neutralization": "INDUSTRY",
        "decay": 2,
        "truncation": 0.001,
        "instrument_type": "EQUITY"
    }
    
    print("\n⚙️ 测试参数:")
    for key, value in test_params.items():
        print(f"  {key}: {value}")
    
    # 尝试导入platform_functions
    try:
        from platform_functions import create_multi_simulation
        print("\n✅ 成功导入platform_functions")
    except ImportError as e:
        print(f"\n❌ 导入platform_functions失败: {e}")
        print("建议检查:")
        print("1. 确保在正确目录运行")
        print("2. 检查platform_functions.py是否存在")
        print("3. 检查依赖是否安装")
        return False
    
    # 提取表达式列表
    expressions = [v["expression"] for v in optimization_variants]
    
    print("\n🎯 准备执行create_multi_simulation...")
    print(f"  表达式数量: {len(expressions)}")
    
    try:
        # 调用create_multi_simulation
        print("\n🔄 调用create_multi_simulation...")
        result = await create_multi_simulation(
            expressions=expressions,
            region=test_params["region"],
            universe=test_params["universe"],
            neutralization=test_params["neutralization"],
            decay=test_params["decay"],
            truncation=test_params["truncation"],
            instrument_type=test_params["instrument_type"]
        )
        
        print("\n✅ create_multi_simulation调用成功!")
        print("\n📊 结果摘要:")
        
        if isinstance(result, dict):
            # 打印关键信息
            if "simulation_id" in result:
                print(f"  模拟ID: {result['simulation_id']}")
            
            if "status" in result:
                print(f"  状态: {result['status']}")
            
            if "message" in result:
                print(f"  消息: {result['message']}")
            
            if "alphas" in result:
                print(f"  创建的Alpha数量: {len(result['alphas'])}")
                for i, alpha in enumerate(result['alphas'], 1):
                    print(f"    {i}. ID: {alpha.get('id', 'N/A')}, 状态: {alpha.get('status', 'N/A')}")
            
            # 保存详细结果
            result_file = f"optimization_test_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(result_file, 'w') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n💾 详细结果已保存到: {result_file}")
            
        else:
            print(f"  返回结果类型: {type(result)}")
            print(f"  结果内容: {result}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ create_multi_simulation调用失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函数"""
    print("🚀 KPe53rmE和A16LxZ1d优化测试")
    print("=" * 60)
    
    # 检查认证
    print("🔐 检查认证状态...")
    try:
        import redis
        redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        keys = redis_client.keys("brain:token:*")
        if keys:
            print(f"✅ 找到 {len(keys)} 个认证令牌")
        else:
            print("❌ 未找到认证令牌，需要先运行 test_auth_redis.py")
            return False
    except Exception as e:
        print(f"❌ Redis检查失败: {e}")
        return False
    
    # 执行优化测试
    success = await test_optimization_variants()
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
    
    if success:
        print("✅ 优化测试执行成功!")
        print("\n📋 后续步骤:")
        print("1. 使用 check_multisimulation_status 监控测试进度")
        print("2. 使用 get_multisimulation_result 获取详细结果")
        print("3. 分析优化变体的表现")
        print("4. 将成功的变体添加到提交队列")
    else:
        print("❌ 优化测试执行失败")
        print("\n🔧 问题排查:")
        print("1. 检查认证状态")
        print("2. 检查平台函数可用性")
        print("3. 检查网络连接")
        print("4. 查看错误日志")
    
    return success

if __name__ == "__main__":
    # 运行异步主函数
    success = asyncio.run(main())
    exit(0 if success else 1)