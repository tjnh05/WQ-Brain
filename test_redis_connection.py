#!/usr/bin/env python3
"""
测试Redis容器连接
"""

import redis
import sys

def test_redis_connection():
    """测试Redis连接"""
    print("🔍 测试Redis容器连接...")
    
    # 尝试连接Redis
    try:
        # 连接到localhost:6379（redis_container映射的端口）
        client = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True,
            socket_connect_timeout=5
        )
        
        # 测试连接
        result = client.ping()
        print(f"✅ Redis连接成功: ping() = {result}")
        
        # 检查是否有认证令牌
        keys = client.keys("brain:token:*")
        if keys:
            print(f"✅ 找到认证令牌: {len(keys)} 个")
            for key in keys[:3]:  # 显示前3个
                print(f"   - {key}")
        else:
            print("⚠️  未找到认证令牌，需要先进行认证")
            
        # 检查Redis信息
        info = client.info()
        print(f"📊 Redis信息:")
        print(f"  版本: {info.get('redis_version', 'N/A')}")
        print(f"  运行时间: {info.get('uptime_in_days', 'N/A')} 天")
        print(f"  内存使用: {info.get('used_memory_human', 'N/A')}")
        
        client.close()
        return True
        
    except redis.ConnectionError as e:
        print(f"❌ Redis连接失败: {e}")
        print("可能原因:")
        print("  1. Redis容器未运行")
        print("  2. 端口映射不正确")
        print("  3. 防火墙阻止连接")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def test_docker_redis_cli():
    """通过Docker exec测试Redis"""
    print("\n🔍 通过Docker exec测试Redis...")
    
    import subprocess
    try:
        # 尝试通过docker exec执行redis-cli
        cmd = ["docker", "exec", "redis_container", "redis-cli", "ping"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"✅ Docker exec成功: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Docker exec失败: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ Docker命令未找到")
        return False
    except Exception as e:
        print(f"❌ 执行错误: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Redis容器连接测试")
    print("=" * 50)
    
    # 测试Python Redis连接
    python_success = test_redis_connection()
    
    # 测试Docker exec连接
    docker_success = test_docker_redis_cli()
    
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"  Python Redis连接: {'✅ 成功' if python_success else '❌ 失败'}")
    print(f"  Docker exec连接: {'✅ 成功' if docker_success else '❌ 失败'}")
    
    if python_success:
        print("\n🎉 建议: 直接使用Python redis-py库连接localhost:6379")
        print("   修改platform_functions.py中的Redis连接配置即可")
    else:
        print("\n⚠️  需要检查:")
        print("   1. Redis容器是否正常运行")
        print("   2. 端口映射配置")
        print("   3. 网络连接设置")
