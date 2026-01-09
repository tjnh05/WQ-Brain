#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速检查认证状态和Redis连接
用于优化测试前的验证
"""

import redis
import json
import time

def check_redis_auth():
    """检查Redis连接和认证令牌"""
    print("=" * 60)
    print("优化测试前验证")
    print("=" * 60)
    
    # 检查Redis连接
    try:
        redis_client = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )
        
        # 测试连接
        if redis_client.ping():
            print("✅ Redis连接正常")
        else:
            print("❌ Redis连接失败")
            return False
        
        # 检查认证令牌
        keys = redis_client.keys("brain:token:*")
        if keys:
            print(f"✅ 找到 {len(keys)} 个认证令牌")
            for key in keys:
                # 获取令牌信息
                data = redis_client.get(key)
                try:
                    token_data = json.loads(data)
                    email = token_data.get('email', 'unknown')
                    expires_at = token_data.get('expires_at', 0)
                    remaining = max(0, expires_at - time.time())
                    
                    print(f"   - {key}: {email}")
                    print(f"     剩余时间: {int(remaining)} 秒 ({int(remaining/60)} 分钟)")
                    
                    if remaining < 300:  # 少于5分钟
                        print(f"     ⚠️  令牌即将过期，建议重新认证")
                        return False
                    else:
                        print(f"     ✅ 令牌有效")
                        return True
                        
                except json.JSONDecodeError:
                    print(f"   - {key}: 数据格式错误")
        else:
            print("❌ 未找到认证令牌，需要重新认证")
            return False
            
    except Exception as e:
        print(f"❌ Redis检查错误: {e}")
        return False

def check_platform_functions():
    """检查平台函数可用性"""
    print("\n🔍 检查平台函数...")
    try:
        # 尝试导入platform_functions
        import sys
        sys.path.append('/Users/mac/WQ-Brain/brainmcp')
        
        from platform_functions import redis_client, brain_client
        
        if redis_client:
            print("✅ platform_functions.redis_client 可用")
        else:
            print("❌ platform_functions.redis_client 不可用")
            
        if brain_client:
            print("✅ platform_functions.brain_client 可用")
        else:
            print("❌ platform_functions.brain_client 不可用")
            
        return True
        
    except ImportError as e:
        print(f"❌ 导入platform_functions失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 检查平台函数时出错: {e}")
        return False

def main():
    """主函数"""
    print("🚀 优化测试前验证检查")
    
    # 检查Redis和认证
    redis_ok = check_redis_auth()
    
    # 检查平台函数
    platform_ok = check_platform_functions()
    
    print("\n" + "=" * 60)
    print("验证结果:")
    print("=" * 60)
    
    if redis_ok and platform_ok:
        print("✅ 所有检查通过，可以开始优化测试")
        return True
    else:
        print("❌ 检查未通过，需要解决问题:")
        if not redis_ok:
            print("   - Redis连接或认证令牌有问题")
        if not platform_ok:
            print("   - 平台函数导入有问题")
        print("\n建议:")
        print("1. 运行 test_auth_redis.py 重新认证")
        print("2. 检查 platform_functions.py 是否正确配置")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)