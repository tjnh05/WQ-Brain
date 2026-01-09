#!/usr/bin/env python3
"""
执行单模拟优化测试
为8个优化变体表达式创建独立的模拟
IND区域单模拟上限为8个，符合平台限制
"""

import asyncio
import sys
import time
from typing import Dict, Any, List

# 添加brainmcp目录到Python路径
sys.path.append('/Users/mac/WQ-Brain/brainmcp')

try:
    from platform_functions import create_simulation
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保在正确目录中运行此脚本")
    sys.exit(1)

# 优化变体表达式（来自optimize_alpha_problems.py）
OPTIMIZATION_VARIANTS = [
    "ts_av_diff(rank(industry_value_momentum_rank_float), 252)",
    "ts_av_diff(rank(country_value_momentum_rank_float), 252)",
    "ts_av_diff(zscore(ts_backfill(industry_value_momentum_rank_float, 5)), 120)",
    "ts_av_diff(rank(industry_value_momentum_rank_float), 120)",
    "ts_delta(rank(industry_value_momentum_rank_float), 66)",
    "ts_mean(rank(industry_value_momentum_rank_float), 22) + ts_delta(rank(country_value_momentum_rank_float), 66)",
    "ts_av_diff(zscore(ts_backfill(country_value_momentum_rank_float, 5)), 66)",
    "ts_delta(rank(country_value_momentum_rank_float), 22) + ts_mean(rank(industry_value_momentum_rank_float), 120)"
]

# IND区域模拟参数
IND_PARAMS = {
    "type": "REGULAR",
    "instrument_type": "EQUITY",
    "region": "IND",
    "universe": "TOP500",
    "delay": 1,  # D1优先于D0
    "decay": 2.0,  # 黄金组合：Decay=2
    "neutralization": "INDUSTRY",  # IND地区Industry中性化效果较好
    "truncation": 0.001,  # 黄金组合：Truncation=0.001
    "test_period": "P0Y0M",  # 默认测试周期
    "unit_handling": "VERIFY",
    "nan_handling": "OFF",
    "language": "FASTEXPR",
    "visualization": True,
    "pasteurization": "ON",
    "max_trade": "OFF",
    "selection_handling": "POSITIVE",
    "selection_limit": 1000,
    "component_activation": "IS"
}

async def create_single_simulation(expression: str, index: int) -> Dict[str, Any]:
    """
    为单个表达式创建模拟
    
    Args:
        expression: Alpha表达式
        index: 表达式索引（用于日志）
    
    Returns:
        模拟创建结果
    """
    print(f"\n=== 创建模拟 {index+1}/8 ===")
    print(f"表达式: {expression}")
    
    try:
        # 调用create_simulation工具
        result = await create_simulation(
            regular=expression,
            **IND_PARAMS
        )
        
        print(f"创建结果: {result}")
        
        # 检查是否成功
        if result.get("simulation_id"):
            print(f"✅ 模拟创建成功！ID: {result['simulation_id']}")
        else:
            print(f"⚠️ 模拟创建可能有问题: {result}")
            
        return result
        
    except Exception as e:
        print(f"❌ 创建模拟时出错: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

async def main():
    """主函数：依次创建8个模拟"""
    print("=" * 60)
    print("开始执行单模拟优化测试")
    print(f"目标区域: {IND_PARAMS['region']}")
    print(f"宇宙: {IND_PARAMS['universe']}")
    print(f"中性化: {IND_PARAMS['neutralization']}")
    print(f"Decay: {IND_PARAMS['decay']}")
    print(f"Truncation: {IND_PARAMS['truncation']}")
    print("=" * 60)
    
    results = []
    
    for i, expression in enumerate(OPTIMIZATION_VARIANTS):
        # 创建模拟
        result = await create_single_simulation(expression, i)
        results.append(result)
        
        # 如果不是最后一个，添加延迟避免速率限制
        if i < len(OPTIMIZATION_VARIANTS) - 1:
            delay_seconds = 10  # 10秒延迟
            print(f"\n等待{delay_seconds}秒后继续...")
            await asyncio.sleep(delay_seconds)
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试完成汇总")
    print("=" * 60)
    
    success_count = sum(1 for r in results if r.get("simulation_id"))
    error_count = sum(1 for r in results if r.get("error"))
    
    print(f"总测试数: {len(results)}")
    print(f"成功创建: {success_count}")
    print(f"错误数: {error_count}")
    
    # 保存结果到文件
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_file = f"single_simulation_results_{timestamp}.json"
    
    import json
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": timestamp,
            "params": IND_PARAMS,
            "expressions": OPTIMIZATION_VARIANTS,
            "results": results,
            "summary": {
                "total": len(results),
                "success": success_count,
                "errors": error_count
            }
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\n详细结果已保存到: {output_file}")
    
    # 输出成功模拟ID
    print("\n成功创建的模拟ID:")
    for i, result in enumerate(results):
        if sim_id := result.get("simulation_id"):
            print(f"  表达式{i+1}: {sim_id}")

if __name__ == "__main__":
    asyncio.run(main())
