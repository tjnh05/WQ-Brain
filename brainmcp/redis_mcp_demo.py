#!/usr/bin/env python3
"""
Redis MCP 演示脚本
提供基本的Redis操作功能
"""

import redis
import json
from typing import Dict, Any, List, Optional

class RedisMCPDemo:
    def __init__(self, host='localhost', port=6379, db=0):
        self.client = redis.Redis(host=host, port=port, db=db)
        
    def ping(self) -> bool:
        """测试Redis连接"""
        return self.client.ping()
    
    def set_key(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """设置键值对"""
        result = self.client.set(key, value)
        if expire:
            self.client.expire(key, expire)
        return result
    
    def get_key(self, key: str) -> Optional[str]:
        """获取键值"""
        value = self.client.get(key)
        return value.decode('utf-8') if value else None
    
    def delete_key(self, key: str) -> int:
        """删除键"""
        return self.client.delete(key)
    
    def get_all_keys(self, pattern: str = '*') -> List[str]:
        """获取所有匹配模式的键"""
        keys = self.client.keys(pattern)
        return [k.decode('utf-8') for k in keys]
    
    def get_key_info(self, key: str) -> Dict[str, Any]:
        """获取键的详细信息"""
        key_type = self.client.type(key).decode('utf-8')
        ttl = self.client.ttl(key)
        
        info = {
            'key': key,
            'type': key_type,
            'ttl': ttl,
            'exists': self.client.exists(key) == 1
        }
        
        # 根据类型获取值
        if key_type == 'string':
            value = self.client.get(key)
            info['value'] = value.decode('utf-8') if value else None
        elif key_type == 'hash':
            info['value'] = {k.decode('utf-8'): v.decode('utf-8') 
                           for k, v in self.client.hgetall(key).items()}
        elif key_type == 'list':
            info['value'] = [v.decode('utf-8') for v in self.client.lrange(key, 0, -1)]
        elif key_type == 'set':
            info['value'] = [v.decode('utf-8') for v in self.client.smembers(key)]
        elif key_type == 'zset':
            info['value'] = [(v.decode('utf-8'), score) 
                           for v, score in self.client.zrange(key, 0, -1, withscores=True)]
        
        return info
    
    def get_server_info(self) -> Dict[str, Any]:
        """获取Redis服务器信息"""
        info = self.client.info()
        # 提取重要信息
        important_info = {
            'redis_version': info.get('redis_version'),
            'uptime_in_days': info.get('uptime_in_days'),
            'used_memory_human': info.get('used_memory_human'),
            'connected_clients': info.get('connected_clients'),
            'total_commands_processed': info.get('total_commands_processed'),
            'keyspace_hits': info.get('keyspace_hits'),
            'keyspace_misses': info.get('keyspace_misses'),
            'db_size': self.client.dbsize()
        }
        return important_info
    
    def execute_command(self, command: str, *args) -> Any:
        """执行原始Redis命令"""
        return self.client.execute_command(command, *args)

def main():
    """演示函数"""
    try:
        # 创建Redis客户端
        redis_mcp = RedisMCPDemo()
        
        # 测试连接
        if redis_mcp.ping():
            print("✅ Redis连接成功")
        else:
            print("❌ Redis连接失败")
            return
        
        print("\n=== Redis服务器信息 ===")
        server_info = redis_mcp.get_server_info()
        for key, value in server_info.items():
            print(f"{key}: {value}")
        
        print("\n=== 当前所有键 ===")
        keys = redis_mcp.get_all_keys()
        for key in keys:
            info = redis_mcp.get_key_info(key)
            print(f"{key} ({info['type']}): TTL={info['ttl']}")
            if info['type'] == 'string' and info['value']:
                print(f"  值: {info['value'][:50]}..." if len(info['value']) > 50 else f"  值: {info['value']}")
        
        print("\n=== 演示操作 ===")
        # 设置新键
        redis_mcp.set_key('demo:timestamp', '2025-12-19 10:45:00', expire=300)
        print("设置 demo:timestamp (300秒过期)")
        
        # 获取键信息
        demo_info = redis_mcp.get_key_info('demo:timestamp')
        print(f"demo:timestamp 信息: {json.dumps(demo_info, indent=2, ensure_ascii=False)}")
        
        # 执行原始命令
        result = redis_mcp.execute_command('TIME')
        print(f"Redis服务器时间: {result}")
        
    except redis.ConnectionError as e:
        print(f"❌ Redis连接错误: {e}")
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == '__main__':
    main()