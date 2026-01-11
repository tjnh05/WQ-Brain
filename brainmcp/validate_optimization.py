#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证Power Pool Alpha优化环境
"""

import asyncio
import json
import sys
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append('.')

from platform_functions import (
    authenticate, get_operators, get_platform_setting_options, 
    get_datafields, create_multiSim
)

async def validate_optimization_environment():
    """验证优化环境"""
    print("🔍 验证Power Pool Alpha优化环境")
    print("=" * 60)
    
    # 1. 认证
    print("\n1. 🔐 认证检查...")
    auth_result = await authenticate()
    if 'error' in auth_result:
        print(f"❌ 认证失败: {auth_result['error']}")
        return False
    print(f"✅ 认证成功: {auth_result.get('status', '未知')}")
    
    # 2. 检查操作符
    print("\n2. 🔧 操作符检查...")
    operators_result = await get_operators()
    if 'error' in operators_result:
        print(f"❌ 获取操作符失败: {operators_result['error']}")
        return False
    
    operators = operators_result.get('operators', [])
    print(f"✅ 可用操作符数量: {len(operators)}")
    
    # 检查我们使用的操作符
    used_operators = ['ts_av_diff', 'rank', 'zscore', 'ts_backfill']
    available_ops = []
    missing_ops = []
    
    for op in used_operators:
        if any(op in operator for operator in operators):
            available_ops.append(op)
        else:
            missing_ops.append(op)
    
    print(f"✅ 使用的操作符可用: {', '.join(available_ops)}")
    if missing_ops:
        print(f"⚠️ 操作符可能不可用: {', '.join(missing_ops)}")
    
    # 3. 检查平台设置选项
    print("\n3. ⚙️ 平台设置选项检查...")
    settings_result = await get_platform_setting_options()
    if 'error' in settings_result:
        print(f"❌ 获取平台设置失败: {settings_result['error']}")
        return False
    
    print("✅ 平台设置选项获取成功")
    
    # 检查IND区域设置
    if 'region' in settings_result:
        regions = settings_result.get('region', [])
        if 'IND' in regions:
            print(f"✅ IND区域可用")
        else:
            print(f"❌ IND区域不可用，可用区域: {regions}")
    
    # 检查IND区域的Universe
    if 'universe' in settings_result:
        universes = settings_result.get('universe', [])
        if 'TOP500' in universes:
            print(f"✅ IND区域TOP500 Universe可用")
        else:
            print(f"⚠️ TOP500可能不可用，可用Universe: {universes}")
    
    # 4. 检查数据字段
    print("\n4. 📊 数据字段检查...")
    datafields_result = await get_datafields(
        instrument_type="EQUITY",
        region="IND",
        delay=1,
        universe="TOP500"
    )
    
    if 'error' in datafields_result:
        print(f"❌ 获取数据字段失败: {datafields_result['error']}")
        return False
    
    datafields = datafields_result.get('datafields', [])
    print(f"✅ IND区域数据字段数量: {len(datafields)}")
    
    # 检查我们使用的字段
    used_fields = [
        'sector_value_momentum_rank_float',
        'industry_value_momentum_rank_float',
        'global_value_momentum_rank_float'
    ]
    
    available_fields = []
    missing_fields = []
    
    for field in used_fields:
        if any(field in df for df in datafields):
            available_fields.append(field)
        else:
            missing_fields.append(field)
    
    print(f"✅ 使用的字段可用: {', '.join(available_fields)}")
    if missing_fields:
        print(f"❌ 字段不可用: {', '.join(missing_fields)}")
        return False
    
    # 5. 测试一个简单的表达式
    print("\n5. 🧪 测试简单表达式...")
    test_expressions = [
        "rank(industry_value_momentum_rank_float)",
        "ts_av_diff(rank(industry_value_momentum_rank_float), 120)"
    ]
    
    print(f"测试表达式:")
    for i, expr in enumerate(test_expressions, 1):
        print(f"  {i}. {expr}")
    
    try:
        test_result = await create_multiSim(
            alpha_expressions=test_expressions,
            instrument_type="EQUITY",
            region="IND",
            universe="TOP500",
            delay=1,
            decay=0,
            neutralization="INDUSTRY",
            truncation=0.001,
            test_period="P0Y0M",
            unit_handling="NONE",
            nan_handling="NONE",
            language="FASTEXPR",
            visualization=True
        )
        
        if 'error' in test_result:
            print(f"❌ 测试表达式失败: {test_result['error']}")
            return False
        
        print(f"✅ 测试表达式成功")
        if 'simulation_id' in test_result:
            print(f"   模拟ID: {test_result['simulation_id']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试表达式异常: {str(e)}")
        return False

async def main():
    """主函数"""
    print("Power Pool Alpha优化环境验证")
    print(f"当前日期: {datetime.now().strftime('%Y年%m月%d日')}")
    print("=" * 60)
    
    success = await validate_optimization_environment()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ 环境验证通过，可以开始优化工作")
    else:
        print("❌ 环境验证失败，请检查问题")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())
