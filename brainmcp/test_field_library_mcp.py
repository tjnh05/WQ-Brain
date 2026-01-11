#!/usr/bin/env python3
"""
测试字段库MCP服务器
"""

import json
import subprocess
import sys
import time
from typing import Dict, Any, Optional

def send_mcp_request(server_process: subprocess.Popen, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """发送MCP请求并获取响应"""
    # 发送请求
    request_json = json.dumps(request) + "\n"
    server_process.stdin.write(request_json.encode())
    server_process.stdin.flush()
    
    # 读取响应
    line = server_process.stdout.readline()
    if not line:
        return None
    
    try:
        return json.loads(line.decode())
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}, 原始响应: {line}")
        return None

def test_mcp_server():
    """测试MCP服务器"""
    print("启动字段库MCP服务器测试...")
    
    # 启动MCP服务器进程
    server_path = "/Users/mac/WQ-Brain/brainmcp/field_library_mcp.py"
    server_process = subprocess.Popen(
        ["python3", server_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # 等待服务器初始化
    time.sleep(1)
    
    try:
        # 1. 测试初始化
        print("\n1. 测试初始化...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }
        
        init_response = send_mcp_request(server_process, init_request)
        if init_response and "result" in init_response:
            print(f"初始化成功: {init_response['result']['serverInfo']['name']}")
        else:
            print(f"初始化失败: {init_response}")
            return False
        
        # 2. 测试获取工具列表
        print("\n2. 测试获取工具列表...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        tools_response = send_mcp_request(server_process, tools_request)
        if tools_response and "result" in tools_response:
            tools = tools_response["result"]["tools"]
            print(f"找到 {len(tools)} 个工具:")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description']}")
        else:
            print(f"获取工具列表失败: {tools_response}")
            return False
        
        # 3. 测试字段推荐工具
        print("\n3. 测试字段推荐工具...")
        recommend_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "field_library_recommend",
                "arguments": {
                    "region": "IND",
                    "alpha_type": "POWER_POOL",
                    "num_fields": 3
                }
            }
        }
        
        recommend_response = send_mcp_request(server_process, recommend_request)
        if recommend_response and "result" in recommend_response:
            result_text = recommend_response["result"]["content"][0]["text"]
            result = json.loads(result_text)
            if result.get("success"):
                print(f"字段推荐成功: 推荐了 {result.get('count', 0)} 个字段")
                for field in result.get("fields", [])[:3]:
                    print(f"  - {field.get('name')} (风险: {field.get('correlation_risk', {}).get('level', 'UNKNOWN')})")
            else:
                print(f"字段推荐失败: {result.get('error')}")
        else:
            print(f"字段推荐调用失败: {recommend_response}")
        
        # 4. 测试变体生成工具
        print("\n4. 测试变体生成工具...")
        generate_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "field_library_generate_variants",
                "arguments": {
                    "region": "IND",
                    "alpha_type": "POWER_POOL",
                    "num_variants": 3,
                    "strategy": "balanced"
                }
            }
        }
        
        generate_response = send_mcp_request(server_process, generate_request)
        if generate_response and "result" in generate_response:
            result_text = generate_response["result"]["content"][0]["text"]
            result = json.loads(result_text)
            if result.get("success"):
                print(f"变体生成成功: 生成了 {result.get('count', 0)} 个变体")
                for i, variant in enumerate(result.get("variants", [])[:3], 1):
                    print(f"  {i}. {variant}")
            else:
                print(f"变体生成失败: {result.get('error')}")
        else:
            print(f"变体生成调用失败: {generate_response}")
        
        # 5. 测试表达式分析工具
        print("\n5. 测试表达式分析工具...")
        sample_expr = "ts_delta(rank(mdl110_value) + rank(sector_value_momentum_rank_float), 66)"
        analyze_request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "field_library_analyze",
                "arguments": {
                    "expression": sample_expr
                }
            }
        }
        
        analyze_response = send_mcp_request(server_process, analyze_request)
        if analyze_response and "result" in analyze_response:
            result_text = analyze_response["result"]["content"][0]["text"]
            result = json.loads(result_text)
            if result.get("success"):
                analysis = result.get("analysis", {})
                print(f"表达式分析成功:")
                print(f"  字段数: {analysis.get('field_count')}")
                print(f"  操作符数: {analysis.get('operator_count')}")
                print(f"  复杂度: {analysis.get('complexity_level')}")
            else:
                print(f"表达式分析失败: {result.get('error')}")
        else:
            print(f"表达式分析调用失败: {analyze_response}")
        
        # 6. 测试字段搜索工具
        print("\n6. 测试字段搜索工具...")
        search_request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "field_library_search",
                "arguments": {
                    "dataset": "Model",
                    "max_risk": "LOW",
                    "min_success_rate": 0.3
                }
            }
        }
        
        search_response = send_mcp_request(server_process, search_request)
        if search_response and "result" in search_response:
            result_text = search_response["result"]["content"][0]["text"]
            result = json.loads(result_text)
            if result.get("success"):
                print(f"字段搜索成功: 找到 {result.get('count', 0)} 个字段")
            else:
                print(f"字段搜索失败: {result.get('error')}")
        else:
            print(f"字段搜索调用失败: {search_response}")
        
        print("\n所有测试完成！")
        return True
        
    except Exception as e:
        print(f"测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理服务器进程
        server_process.terminate()
        server_process.wait()
        print("MCP服务器进程已终止")

if __name__ == "__main__":
    success = test_mcp_server()
    sys.exit(0 if success else 1)
