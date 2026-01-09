#!/usr/bin/env python3
"""
FastMCP服务器快速测试
验证Alpha队列FastMCP版本是否正常工作
"""

import json
import subprocess
import sys
import time

def send_request(process, request):
    """发送请求到MCP服务器并获取响应"""
    request_json = json.dumps(request) + "\n"
    process.stdin.write(request_json)
    process.stdin.flush()
    
    # 读取响应
    response_line = process.stdout.readline()
    if not response_line:
        return None
    
    return json.loads(response_line.strip())

def main():
    print("测试FastMCP Alpha队列服务器...")
    
    # 启动FastMCP服务器进程
    try:
        server_process = subprocess.Popen(
            [sys.executable, "alpha_queue_fastmcp.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # 等待服务器启动
        time.sleep(0.5)
        
        # 测试1: 初始化请求
        print("1. 测试初始化...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "fastmcp-test",
                    "version": "1.0.0"
                }
            }
        }
        
        init_response = send_request(server_process, init_request)
        if init_response and "result" in init_response:
            server_info = init_response['result']['serverInfo']
            print(f"   ✅ 初始化成功: {server_info['name']} v{server_info['version']}")
        else:
            print(f"   ❌ 初始化失败: {init_response}")
            server_process.terminate()
            return
        
        # 测试2: 工具列表
        print("2. 测试工具列表...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        tools_response = send_request(server_process, tools_request)
        if tools_response and "result" in tools_response:
            tools = tools_response['result']['tools']
            print(f"   ✅ 获取到 {len(tools)} 个工具")
            for tool in tools:
                print(f"     - {tool['name']}")
        else:
            print(f"   ❌ 工具列表失败: {tools_response}")
            server_process.terminate()
            return
        
        # 测试3: 列出Alpha
        print("3. 测试列出Alpha...")
        list_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "alpha_queue_list",
                "arguments": {}
            }
        }
        
        list_response = send_request(server_process, list_request)
        if list_response and "result" in list_response:
            content = list_response['result']['content'][0]['text']
            alphas = json.loads(content)
            print(f"   ✅ 列出Alpha成功，共 {len(alphas)} 个Alpha")
        else:
            print(f"   ❌ 列出Alpha失败: {list_response}")
        
        # 测试4: 获取统计
        print("4. 测试获取统计...")
        stats_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "alpha_queue_stats",
                "arguments": {}
            }
        }
        
        stats_response = send_request(server_process, stats_request)
        if stats_response and "result" in stats_response:
            content = stats_response['result']['content'][0]['text']
            stats = json.loads(content)
            print(f"   ✅ 获取统计成功: 总Alpha数 {stats['total']}")
        else:
            print(f"   ❌ 获取统计失败: {stats_response}")
        
        # 关闭服务器
        server_process.terminate()
        server_process.wait()
        
        # 读取错误输出（如果有）
        stderr_output = server_process.stderr.read()
        if stderr_output:
            print(f"\n服务器错误输出:\n{stderr_output}")
        
        print("\n✅ FastMCP服务器测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()