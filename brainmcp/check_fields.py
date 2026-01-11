#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查IND区域可用字段
"""

import asyncio
import sys

sys.path.append('.')

from platform_functions import authenticate, get_datafields

async def check_ind_fields():
    """检查IND区域字段"""
    print("🔍 检查IND区域可用字段")
    print("=" * 60)
    
    # 认证
    auth_result = await authenticate()
    if 'error' in auth_result:
        print(f"❌ 认证失败: {auth_result['error']}")
        return
    
    print("✅ 认证成功")
    
    # 获取IND区域数据字段
    print("\n📊 获取IND区域数据字段...")
    result = await get_datafields(
        instrument_type="EQUITY",
        region="IND",
        delay=1,
        universe="TOP500"
    )
    
    if 'error' in result:
        print(f"❌ 获取数据字段失败: {result['error']}")
        return
    
    datafields = result.get('datafields', [])
    print(f"✅ 获取到 {len(datafields)} 个数据字段")
    
    # 检查我们使用的字段
    fields_to_check = [
        'industry_value_momentum_rank_float',
        'country_value_momentum_rank_float',
        'market_value_momentum_rank_float',
        'sector_value_momentum_rank_float',
        'global_value_momentum_rank_float'
    ]
    
    print("\n🔎 字段检查结果:")
    found_fields = []
    missing_fields = []
    
    for field in fields_to_check:
        # 检查字段是否存在（部分匹配）
        found = False
        for df in datafields:
            if field in df:
                found = True
                found_fields.append(field)
                print(f"✅ {field} - 存在")
                break
        
        if not found:
            missing_fields.append(field)
            print(f"❌ {field} - 未找到")
    
    print(f"\n📈 统计:")
    print(f"找到字段: {len(found_fields)}/{len(fields_to_check)}")
    print(f"缺失字段: {len(missing_fields)}/{len(fields_to_check)}")
    
    if missing_fields:
        print(f"\n⚠️ 建议使用以下替代字段:")
        # 搜索相关字段
        for missing in missing_fields:
            print(f"\n搜索 '{missing}' 相关字段:")
            related = []
            for df in datafields:
                if any(term in df for term in ['industry', 'country', 'market', 'sector', 'global', 'momentum']):
                    related.append(df)
            
            if related:
                for i, field in enumerate(related[:5], 1):  # 显示前5个
                    print(f"  {i}. {field}")
            else:
                print("  未找到相关字段")
    
    return found_fields

async def main():
    """主函数"""
    print("IND区域字段检查工具")
    print("=" * 60)
    
    found_fields = await check_ind_fields()
    
    print("\n" + "=" * 60)
    if found_fields:
        print(f"✅ 找到 {len(found_fields)} 个关键字段")
        print("建议使用这些字段构建Alpha表达式")
    else:
        print("❌ 未找到关键字段，需要调整策略")

if __name__ == "__main__":
    asyncio.run(main())
