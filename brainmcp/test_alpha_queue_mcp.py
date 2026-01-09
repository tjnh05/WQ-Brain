#!/usr/bin/env python3
"""
Alpha队列MCP服务器测试脚本
测试MCP服务器的基本功能
"""

import json
import subprocess
import sys
import time

def send_request(server_process, request):
    """发送请求到MCP服务器并获取响应"""
    request_json = json.dumps(request) + "\n"
    server_process.stdin.write(request_json)
    server_process.stdin.flush()
    
    # 读取响应
    response_line = server_process.stdout.readline()
    if not response_line:
        return None
    
    return json.loads(response_line.strip())

def test_initialize(server_process):
    """测试初始化请求"""
    print("测试初始化...")
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    response = send_request(server_process, request)
    if response and "result" in response:
        print("✅ 初始化成功")
        print(f"  服务器: {response['result']['serverInfo']['name']} v{response['result']['serverInfo']['version']}")
        return True
    else:
        print("❌ 初始化失败")
        print(f"  响应: {response}")
        return False

def test_tools_list(server_process):
    """测试工具列表请求"""
    print("\n测试工具列表...")
    request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    response = send_request(server_process, request)
    if response and "result" in response:
        tools = response['result']['tools']
        print(f"✅ 获取到 {len(tools)} 个工具:")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
        return True
    else:
        print("❌ 工具列表失败")
        return False

def test_list_alphas(server_process):
    """测试列出Alpha"""
    print("\n测试列出Alpha...")
    request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "alpha_queue_list",
            "arguments": {}
        }
    }
    
    response = send_request(server_process, request)
    if response and "result" in response:
        content = response['result']['content'][0]['text']
        alphas = json.loads(content)
        print(f"✅ 列出Alpha成功，共 {len(alphas)} 个Alpha")
        return True
    else:
        print("❌ 列出Alpha失败")
        return False

def test_add_alpha(server_process):
    """测试添加Alpha"""
    print("\n测试添加Alpha...")
    request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "alpha_queue_add",
            "arguments": {
                "alpha_id": "TEST1234",
                "expression": "rank(close)",
                "status": "pending",
                "priority": 7.5,
                "reason": "测试添加"
            }
        }
    }
    
    response = send_request(server_process, request)
    if response and "result" in response:
        content = response['result']['content'][0]['text']
        result = json.loads(content)
        print(f"✅ 添加Alpha成功: {result['message']}")
        return True
    else:
        print("❌ 添加Alpha失败")
        return False

def test_stats(server_process):
    """测试获取统计"""
    print("\n测试获取统计...")
    request = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "alpha_queue_stats",
            "arguments": {}
        }
    }
    
    response = send_request(server_process, request)
    if response and "result" in response:
        content = response['result']['content'][0]['text']
        stats = json.loads(content)
        print(f"✅ 获取统计成功:")
        print(f"  总Alpha数: {stats['total']}")
        for status, count in stats['by_status'].items():
            print(f"  {status}: {count}")
        return True
    else:
        print("❌ 获取统计失败")
        return False

def test_validate(server_process):
    """测试验证队列"""
    print("\n测试验证队列...")
    request = {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "alpha_queue_validate",
            "arguments": {}
        }
    }
    
    response = send_request(server_process, request)
    if response and "result" in response:
        content = response['result']['content'][0]['text']
        result = json.loads(content)
        if result['valid']:
            print(f"✅ 队列验证通过，共 {result['alpha_count']} 个Alpha")
        else:
            print(f"⚠️ 队列验证发现问题: {result['issues']}")
        return True
    else:
        print("❌ 验证队列失败")
        return False

def main():
    """主测试函数"""
    print("启动Alpha队列MCP服务器测试...")
    
    # 启动MCP服务器进程
    try:
        server_process = subprocess.Popen(
            [sys.executable, "alpha_queue_mcp.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # 等待服务器启动
        time.sleep(0.5)
        
        # 运行测试
        tests = [
            test_initialize,
            test_tools_list,
            test_list_alphas,
            test_add_alpha,
            test_stats,
            test_validate
        ]
        
        passed = 0
        total = len(tests)
        
        for test_func in tests:
            try:
                if test_func(server_process):
                    passed += 1
            except Exception as e:
                print(f"❌ 测试失败: {e}")
        
        # 关闭服务器
        server_process.terminate()
        server_process.wait()
        
        # 读取错误输出（如果有）
        stderr_output = server_process.stderr.read()
        if stderr_output:
            print(f"\n服务器错误输出:\n{stderr_output}")
        
        print(f"\n测试完成: {passed}/{total} 通过")
        if passed == total:
            print("✅ 所有测试通过！")
        else:
            print("⚠️ 部分测试失败")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ 测试启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()