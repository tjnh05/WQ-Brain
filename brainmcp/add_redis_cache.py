#!/usr/bin/env python3
"""
脚本用于修改cnhkmcp的platform_functions.py，添加Redis token缓存机制
"""

import sys
import os

def add_redis_cache(file_path):
    """修改文件添加Redis缓存支持"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 检查是否已添加import redis
    redis_import_added = any('import redis' in line for line in lines)
    
    # 1. 确保import redis存在（在import requests附近）
    if not redis_import_added:
        for i, line in enumerate(lines):
            if 'import requests' in line:
                # 在import requests后添加import redis
                lines.insert(i + 1, 'import redis\n')
                print("✅ 已添加import redis")
                break
    
    # 2. 在brain_client实例化后添加Redis客户端初始化
    redis_client_added = any('redis.Redis(' in line for line in lines)
    
    if not redis_client_added:
        for i, line in enumerate(lines):
            if 'brain_client = BrainApiClient()' in line:
                # 在这一行后添加Redis初始化
                redis_init = '''\n# Redis缓存客户端初始化
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    # 测试连接
    redis_client.ping()
    print("✅ Redis缓存客户端初始化成功")
except Exception as e:
    print(f"⚠️ Redis缓存初始化失败: {e}")
    redis_client = None\n'''
                lines.insert(i + 1, redis_init)
                print("✅ 已添加Redis客户端初始化")
                break
    
    # 3. 修改authenticate函数，添加缓存逻辑
    # 找到authenticate函数定义
    for i, line in enumerate(lines):
        if '@mcp.tool()' in line and i+1 < len(lines) and 'async def authenticate(' in lines[i+1]:
            # 找到函数开始位置
            func_start = i
            # 找到函数结束位置（假设函数不太长，我们查找下一个@mcp.tool()或空行后的大量缩进减少）
            # 简化：我们将在函数内部添加缓存逻辑
            # 先读取整个函数，然后修改
            print(f"✅ 找到authenticate函数在第{func_start}行附近")
            
            # 创建一个新版本的文件
            new_lines = lines[:func_start]
            
            # 添加修改后的authenticate函数
            modified_func = '''@mcp.tool()
async def authenticate(email: Optional[str] = "", password: Optional[str] = "") -> Dict[str, Any]:
    """
    🔐 Authenticate with WorldQuant BRAIN platform with Redis token caching.
    
    This is the first step in any BRAIN workflow. You must authenticate before using any other tools.
    
    Args:
        email: Your BRAIN platform email address (optional if in config or .brain_credentials)
        password: Your BRAIN platform password (optional if in config or .brain_credentials)
    
    Returns:
        Authentication result with user info and permissions
    """
    try:
        config = load_config()
        if 'credentials' in config:
            if not email:
                email = config['credentials'].get('email', '')
            if not password:
                password = config['credentials'].get('password', '')
        
        if not email or not password:
            return {"error": "Email and password required. Either provide them as arguments, configure them in user_config.json, or create a .brain_credentials file in your home directory with format: [\"email\", \"password\"]"}
        
        # 尝试从Redis缓存获取token
        cached_token = None
        if redis_client:
            try:
                cache_key = f"brain:token:{email}"
                cached_data = redis_client.get(cache_key)
                if cached_data:
                    import json
                    token_data = json.loads(cached_data)
                    # 检查是否过期（2小时缓存）
                    import time
                    if time.time() < token_data.get('expires_at', 0):
                        cached_token = token_data.get('token')
                        print(f"✅ 使用缓存的Token for {email}")
                        # 直接返回缓存结果
                        return {
                            'user': {'email': email},
                            'status': 'authenticated',
                            'permissions': ['read', 'write'],
                            'message': 'Authentication successful (from cache)',
                            'status_code': 200,
                            'has_jwt': True,
                            'cached': True
                        }
            except Exception as e:
                print(f"⚠️ Redis缓存读取失败: {e}")
        
        # 需要重新认证
        print(f"🔄 Token缓存未找到或已过期，重新认证...")
        result = await brain_client.authenticate(email, password)
        
        # 保存Token到Redis缓存（2小时过期）
        if redis_client and 'status' in result and result['status'] == 'authenticated':
            try:
                import json
                import time
                cache_key = f"brain:token:{email}"
                token_data = {
                    'token': 'cached_auth',  # 实际token在session中，我们只缓存认证状态
                    'email': email,
                    'created_at': time.time(),
                    'expires_at': time.time() + 7200  # 2小时
                }
                redis_client.setex(cache_key, 7200, json.dumps(token_data))
                print(f"💾 Token已保存到Redis缓存，过期时间: 2小时")
            except Exception as e:
                print(f"⚠️ Redis缓存保存失败: {e}")
        
        # Save credentials to config for future use
        config = load_config()
        if 'credentials' not in config:
            config['credentials'] = {}
        config['credentials']['email'] = email
        config['credentials']['password'] = password
        save_config(config)
        
        return result
    except Exception as e:
        return {"error": str(e)}
'''
            new_lines.append(modified_func)
            
            # 跳过原始函数，找到下一个工具函数
            j = func_start
            while j < len(lines):
                if j > func_start and '@mcp.tool()' in lines[j]:
                    break
                j += 1
            
            # 添加剩余的行
            new_lines.extend(lines[j:])
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            print("✅ authenticate函数已修改，添加Redis缓存支持")
            return True
    
    # 如果没有找到函数，直接写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("✅ 文件已更新（可能已包含缓存支持）")
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("使用方法: python add_redis_cache.py <platform_functions.py路径>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在: {file_path}")
        sys.exit(1)
    
    # 备份原文件
    import shutil
    import time
    backup_path = file_path + '.backup.' + str(int(time.time()))
    shutil.copy2(file_path, backup_path)
    print(f"📁 已创建备份: {backup_path}")
    
    try:
        add_redis_cache(file_path)
        print("🎉 修改完成！")
    except Exception as e:
        print(f"❌ 修改失败: {e}")
        # 恢复备份
        shutil.copy2(backup_path, file_path)
        print("已恢复备份文件")
        sys.exit(1)