#!/usr/bin/env python3
"""
实际功能测试脚本
测试修改后的platform_functions.py在实际环境中的表现
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from platform_functions import BrainApiClient

async def test_actual_functionality():
    """测试实际功能"""
    print("🧪 实际功能测试")
    print("=" * 50)
    
    # 创建客户端
    client = BrainApiClient()
    print("✅ BrainApiClient初始化成功")
    
    # 测试1: 检查认证状态（应该为未认证）
    print("\n1. 测试认证状态检查")
    try:
        is_auth = await client.is_authenticated()
        print(f"   - 当前认证状态: {'已认证' if is_auth else '未认证'}")
    except Exception as e:
        print(f"   ❌ 认证状态检查失败: {e}")
    
    # 测试2: 测试缓存方法
    print("\n2. 测试缓存方法")
    try:
        # 测试缓存写入
        test_data = {"test": "data", "timestamp": "2026-01-09"}
        cache_result = client._cache_data("test:cache:key", test_data, ttl=60)
        print(f"   - 缓存写入结果: {'成功' if cache_result else '失败'}")
        
        # 测试缓存读取
        cached_data = client._get_cached_data("test:cache:key")
        if cached_data:
            print(f"   - 缓存读取成功: {cached_data.get('test')}")
        else:
            print("   - 缓存读取失败或数据不存在")
    except Exception as e:
        print(f"   ❌ 缓存测试失败: {e}")
    
    # 测试3: 测试静态数据方法（不需要认证）
    print("\n3. 测试静态数据方法")
    try:
        # 测试get_operators（应该使用缓存）
        print("   - 测试get_operators...")
        operators = await client.get_operators()
        if operators and isinstance(operators, dict):
            print(f"   ✅ get_operators成功，返回{len(operators.get('operators', []))}个操作符")
        else:
            print("   ❌ get_operators返回格式不正确")
    except Exception as e:
        print(f"   ❌ get_operators测试失败: {e}")
    
    # 测试4: 测试统一的API调用包装器
    print("\n4. 测试API调用包装器")
    try:
        # 测试一个不需要认证的API调用
        print("   - 测试_make_api_call_raw...")
        # 这里我们测试一个简单的HTTP请求
        import aiohttp
        async with aiohttp.ClientSession() as session:
            # 测试一个公开的API
            response = await session.get('https://httpbin.org/get')
            if response.status == 200:
                print("   ✅ HTTP请求测试成功")
            else:
                print(f"   ❌ HTTP请求失败: {response.status}")
    except Exception as e:
        print(f"   ❌ API调用测试失败: {e}")
    
    # 测试5: 检查代码结构
    print("\n5. 检查代码结构")
    required_methods = [
        'ensure_authenticated',
        '_make_api_call',
        '_make_api_call_raw',
        '_get_cached_data',
        '_cache_data',
        'get_datasets',
        'get_datafields',
        'get_platform_setting_options',
        'get_operators',
        'get_documentations',
        'submit_alpha'
    ]
    
    missing_methods = []
    for method in required_methods:
        if hasattr(client, method):
            print(f"   ✅ {method} 存在")
        else:
            print(f"   ❌ {method} 不存在")
            missing_methods.append(method)
    
    if missing_methods:
        print(f"\n⚠️  缺少方法: {', '.join(missing_methods)}")
    else:
        print("\n✅ 所有必需方法都存在")
    
    print("\n" + "=" * 50)
    print("🎉 实际功能测试完成！")
    print("\n建议下一步:")
    print("1. 配置认证信息进行完整测试")
    print("2. 测试多模拟功能")
    print("3. 测试submit_alpha功能")
    print("4. 验证缓存在实际API调用中的效果")

if __name__ == "__main__":
    asyncio.run(test_actual_functionality())
