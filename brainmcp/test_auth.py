#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试认证功能
"""
import asyncio
import sys
import os
sys.path.append('.')

from platform_functions import authenticate

async def test_auth():
    """测试认证功能"""
    try:
        print("开始认证测试...")
        result = await authenticate()
        print("认证结果:", result)
        return result
    except Exception as e:
        print("认证错误:", str(e))
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(test_auth())
    if result:
        print("\n认证状态:", result.get('status', '未知'))
        print("认证有效:", result.get('status') == 'authenticated')
        if result.get('status') == 'authenticated':
            print("✅ 认证成功！可以开始Alpha优化工作")
        else:
            print("❌ 认证失败，请检查凭证")
