#!/usr/bin/env python3
"""
测试认证流程和Redis缓存
"""

import asyncio
import sys
import os

# 添加brainmcp到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'brainmcp'))

async def test_auth_and_redis():
    """测试认证和Redis缓存"""
    print("🔍 测试认证流程和Redis缓存...")
    
    try:
        # 导入platform_functions
        from platform_functions import authenticate
        
        # 测试认证
        print("🔄 尝试认证...")
        result = await authenticate()
        
        print(f"📊 认证结果: {result.get('status', 'unknown')}")
        
        if result.get('status') == 'authenticated':
            print("✅ 认证成功！")
            
            # 检查Redis中是否有token
            import redis
            redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            
            # 查找所有brain:token:*键
            keys = redis_client.keys("brain:token:*")
            if keys:
                print(f"✅ Redis中找到认证令牌: {len(keys)} 个")
                for key in keys:
                    print(f"   - {key}")
                    # 显示部分信息
                    data = redis_client.get(key)
                    if data:
                        import json
                        try:
                            session_data = json.loads(data)
                            email = session_data.get('email', 'unknown')
                            expires_at = session_data.get('expires_at', 0)
                            import time
                            remaining = expires_at - time.time()
                            print(f"     邮箱: {email}")
                            print(f"     剩余时间: {remaining:.0f} 秒")
                        except:
                            print(f"     数据格式: {data[:50]}...")
            else:
                print("❌ Redis中未找到认证令牌")
                print("可能原因:")
                print("  1. 认证成功但Redis存储失败")
                print("  2. Redis连接配置问题")
                print("  3. 认证流程未正确存储令牌")
        else:
            print(f"❌ 认证失败: {result.get('error', '未知错误')}")
            
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保在brainmcp目录中运行")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

async def test_redis_connection():
    """测试Redis连接"""
    print("\n🔍 测试Redis连接...")
    
    import redis
    try:
        redis_client = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True,
            socket_connect_timeout=5
        )
        
        result = redis_client.ping()
        print(f"✅ Redis连接成功: ping() = {result}")
        
        # 检查Redis信息
        info = redis_client.info()
        print(f"📊 Redis信息:")
        print(f"  版本: {info.get('redis_version', 'N/A')}")
        print(f"  内存使用: {info.get('used_memory_human', 'N/A')}")
        
        # 检查所有键
        all_keys = redis_client.keys("*")
        print(f"🔑 Redis中所有键: {len(all_keys)} 个")
        if all_keys:
            for key in all_keys[:10]:  # 显示前10个
                print(f"   - {key}")
            if len(all_keys) > 10:
                print(f"   ... 还有 {len(all_keys) - 10} 个键")
        
        redis_client.close()
        return True
        
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("认证和Redis缓存测试")
    print("=" * 50)
    
    # 测试Redis连接
    redis_success = asyncio.run(test_redis_connection())
    
    if redis_success:
        # 测试认证流程
        asyncio.run(test_auth_and_redis())
    else:
        print("\n❌ Redis连接失败，无法测试认证流程")
        print("请检查:")
        print("  1. Redis容器是否运行: docker ps | grep redis")
        print("  2. 端口映射: docker port redis_container")
        print("  3. 网络连接: telnet localhost 6379")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)
