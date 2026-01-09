#!/usr/bin/env python3
"""
修改platform_functions.py中的authenticate函数，实现方案1：
1. 缓存实际的JWT token和cookies
2. 过期时间设置为30分钟（1800秒）
3. 恢复时设置回session
"""

import re
import sys
import os
import time

def modify_authenticate_function(file_path):
    """修改authenticate函数"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 新版的authenticate函数（方案1）
    new_authenticate = '''@mcp.tool()
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
        
        # 尝试从Redis缓存获取token和session
        if redis_client:
            try:
                cache_key = f"brain:token:{email}"
                cached_data = redis_client.get(cache_key)
                if cached_data:
                    import json
                    import time
                    session_data = json.loads(cached_data)
                    # 检查是否过期（30分钟缓存）
                    if time.time() < session_data.get('expires_at', 0):
                        # 恢复session cookies
                        cookies_dict = session_data.get('cookies', {})
                        for name, value in cookies_dict.items():
                            brain_client.session.cookies.set(name, value)
                        
                        print(f"✅ 使用缓存的Token for {email} (30分钟缓存)")
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
                    else:
                        print(f"🔄 缓存已过期，重新认证...")
            except Exception as e:
                print(f"⚠️ Redis缓存读取失败: {e}")
        
        # 需要重新认证
        print(f"🔄 Token缓存未找到或已过期，重新认证...")
        result = await brain_client.authenticate(email, password)
        
        # 保存完整的session状态到Redis缓存（30分钟过期）
        if redis_client and 'status' in result and result['status'] == 'authenticated':
            try:
                import json
                import time
                cache_key = f"brain:token:{email}"
                # 获取实际的JWT token和所有cookies
                jwt_token = brain_client.session.cookies.get('t')
                cookies_dict = dict(brain_client.session.cookies)
                
                session_data = {
                    'jwt_token': jwt_token,
                    'cookies': cookies_dict,
                    'email': email,
                    'created_at': time.time(),
                    'expires_at': time.time() + 1800  # 30分钟
                }
                redis_client.setex(cache_key, 1800, json.dumps(session_data))
                print(f"💾 Token和session已保存到Redis缓存，过期时间: 30分钟")
                if jwt_token:
                    print(f"   JWT token: {jwt_token[:20]}...")
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
        return {"error": str(e)}'''
    
    # 查找并替换authenticate函数
    # 模式：从@mcp.tool()开始，到下一个@mcp.tool()之前，但我们需要匹配整个authenticate函数
    # 更简单的方法：替换从当前authenticate函数开始到下一个@mcp.tool()之间的内容
    
    # 首先找到authenticate函数的位置
    pattern = r'(@mcp\.tool\(\)\s*\nasync def authenticate\(.*?)(?=\n@mcp\.tool\(\)|\Z)'
    
    # 使用re.DOTALL使.匹配换行符
    new_content = re.sub(pattern, new_authenticate, content, flags=re.DOTALL)
    
    if new_content == content:
        print("⚠️ 未找到authenticate函数，可能模式不匹配")
        # 尝试另一种方法：查找并替换特定行范围
        lines = content.split('\n')
        in_authenticate = False
        authenticate_start = -1
        authenticate_end = -1
        
        for i, line in enumerate(lines):
            if '@mcp.tool()' in line and i+1 < len(lines) and 'async def authenticate(' in lines[i+1]:
                authenticate_start = i
                in_authenticate = True
            elif in_authenticate and '@mcp.tool()' in line and i > authenticate_start:
                authenticate_end = i
                break
        
        if authenticate_start != -1 and authenticate_end != -1:
            # 替换这个区间的行
            new_lines = lines[:authenticate_start] + new_authenticate.split('\n') + lines[authenticate_end:]
            new_content = '\n'.join(new_lines)
            print(f"✅ 使用行范围替换: 第{authenticate_start}到{authenticate_end}行")
        else:
            print("❌ 无法找到authenticate函数位置")
            return False
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("使用方法: python fix_auth_cache.py <platform_functions.py路径>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在: {file_path}")
        sys.exit(1)
    
    # 备份
    backup_path = file_path + '.backup.' + str(int(time.time()))
    import shutil
    shutil.copy2(file_path, backup_path)
    print(f"📁 已创建备份: {backup_path}")
    
    try:
        if modify_authenticate_function(file_path):
            print("✅ authenticate函数修改成功！")
            print("   修改内容:")
            print("   1. 缓存实际的JWT token和session cookies")
            print("   2. 过期时间设置为30分钟（1800秒）")
            print("   3. 恢复时自动设置cookies到brain_client.session")
        else:
            print("❌ 修改失败")
            # 恢复备份
            shutil.copy2(backup_path, file_path)
            print("已恢复备份文件")
            sys.exit(1)
    except Exception as e:
        print(f"❌ 修改过程中出错: {e}")
        import traceback
        traceback.print_exc()
        # 恢复备份
        shutil.copy2(backup_path, file_path)
        print("已恢复备份文件")
        sys.exit(1)