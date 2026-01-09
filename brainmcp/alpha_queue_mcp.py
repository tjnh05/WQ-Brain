#!/usr/bin/env python3
"""
Alpha队列MCP服务器
提供Alpha队列管理的MCP工具接口
"""

import json
import sys
import traceback
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

QUEUE_FILE = 'IND_Alpha_Queue_Simplified.json'

class AlphaQueueManager:
    """Alpha队列管理器"""
    
    @staticmethod
    def load_queue() -> Dict[str, Any]:
        """加载队列文件"""
        try:
            with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # 创建新队列
            return {
                'metadata': {
                    'created': datetime.now().strftime('%Y-%m-%d'),
                    'updated': datetime.now().strftime('%Y-%m-%d'),
                    'author': 'BW53146',
                    'region': 'IND',
                    'version': '2.0-simplified',
                    'description': '简化Alpha队列'
                },
                'alphas': [],
                'schedule': {},
                'stats': {'total': 0, 'by_status': {}}
            }
    
    @staticmethod
    def save_queue(data: Dict[str, Any]) -> Dict[str, Any]:
        """保存队列文件并返回更新后的数据"""
        data['metadata']['updated'] = datetime.now().strftime('%Y-%m-%d')
        
        # 更新统计
        stats = {'total': 0, 'by_status': {}}
        for alpha in data['alphas']:
            status = alpha['status']
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            stats['total'] += 1
        data['stats'] = stats
        
        with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return data
    
    @staticmethod
    def list_alphas(status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出Alpha"""
        data = AlphaQueueManager.load_queue()
        alphas = data['alphas']
        
        if status_filter:
            alphas = [a for a in alphas if a['status'] == status_filter]
        
        return alphas
    
    @staticmethod
    def add_alpha(alpha_id: str, expression: str = '', status: str = 'pending',
                  scheduled_date: str = '', priority: float = 5.0, reason: str = '') -> Dict[str, Any]:
        """添加Alpha到队列"""
        data = AlphaQueueManager.load_queue()
        
        # 检查是否已存在
        for alpha in data['alphas']:
            if alpha['id'] == alpha_id:
                return {
                    'success': False,
                    'error': f'Alpha {alpha_id} 已存在，状态: {alpha["status"]}'
                }
        
        # 添加新Alpha
        new_alpha = {
            'id': alpha_id,
            'status': status,
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        
        if status == 'pending':
            if expression:
                new_alpha['expression'] = expression
            if scheduled_date:
                new_alpha['scheduled'] = scheduled_date
            new_alpha['priority'] = priority
        elif reason:
            new_alpha['reason'] = reason
        
        data['alphas'].append(new_alpha)
        data = AlphaQueueManager.save_queue(data)
        
        return {
            'success': True,
            'message': f'已添加Alpha {alpha_id}, 状态: {status}',
            'alpha': new_alpha
        }
    
    @staticmethod
    def update_status(alpha_id: str, new_status: str, reason: str = '') -> Dict[str, Any]:
        """更新Alpha状态"""
        data = AlphaQueueManager.load_queue()
        
        for alpha in data['alphas']:
            if alpha['id'] == alpha_id:
                old_status = alpha['status']
                alpha['status'] = new_status
                alpha['date'] = datetime.now().strftime('%Y-%m-%d')
                
                if reason:
                    alpha['reason'] = reason
                elif 'reason' in alpha and new_status not in ['failed', 'high_correlation']:
                    # 如果不是失败状态，移除原因字段
                    del alpha['reason']
                
                data = AlphaQueueManager.save_queue(data)
                
                return {
                    'success': True,
                    'message': f'Alpha {alpha_id} 状态更新: {old_status} → {new_status}',
                    'alpha': alpha,
                    'reason': reason if reason else None
                }
        
        return {
            'success': False,
            'error': f'未找到Alpha: {alpha_id}'
        }
    
    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """获取统计信息"""
        data = AlphaQueueManager.load_queue()
        return {
            'total': data['stats']['total'],
            'by_status': data['stats']['by_status'],
            'metadata': data['metadata']
        }
    
    @staticmethod
    def validate_queue() -> Dict[str, Any]:
        """验证队列数据"""
        data = AlphaQueueManager.load_queue()
        issues = []
        
        # 检查重复ID
        ids = [a['id'] for a in data['alphas']]
        duplicates = [id for id in set(ids) if ids.count(id) > 1]
        if duplicates:
            issues.append(f'重复的Alpha ID: {duplicates}')
        
        # 检查pending状态必须有表达式
        for alpha in data['alphas']:
            if alpha['status'] == 'pending' and 'expression' not in alpha:
                issues.append(f'pending状态的Alpha {alpha["id"]} 缺少表达式')
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'alpha_count': len(data['alphas'])
        }


class MCPServer:
    """MCP服务器实现"""
    
    def __init__(self):
        self.queue_manager = AlphaQueueManager()
        self.tools = self._get_tools()
    
    def _get_tools(self) -> List[Dict[str, Any]]:
        """获取可用工具列表"""
        return [
            {
                "name": "alpha_queue_list",
                "description": "列出Alpha队列中的Alpha，可选状态过滤",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "status_filter": {
                            "type": "string",
                            "description": "状态过滤 (pending, submitted, failed, high_correlation)",
                            "enum": ["pending", "submitted", "failed", "high_correlation"]
                        }
                    }
                }
            },
            {
                "name": "alpha_queue_add",
                "description": "添加Alpha到队列",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "alpha_id": {
                            "type": "string",
                            "description": "Alpha ID (8位字母数字)"
                        },
                        "expression": {
                            "type": "string",
                            "description": "Alpha表达式"
                        },
                        "status": {
                            "type": "string",
                            "description": "状态",
                            "enum": ["pending", "submitted", "failed", "high_correlation"],
                            "default": "pending"
                        },
                        "scheduled_date": {
                            "type": "string",
                            "description": "计划提交日期 (YYYY-MM-DD)"
                        },
                        "priority": {
                            "type": "number",
                            "description": "优先级 (1-10)",
                            "default": 5.0
                        },
                        "reason": {
                            "type": "string",
                            "description": "原因 (用于failed或high_correlation状态)"
                        }
                    },
                    "required": ["alpha_id"]
                }
            },
            {
                "name": "alpha_queue_update",
                "description": "更新Alpha状态",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "alpha_id": {
                            "type": "string",
                            "description": "Alpha ID"
                        },
                        "new_status": {
                            "type": "string",
                            "description": "新状态",
                            "enum": ["pending", "submitted", "failed", "high_correlation"]
                        },
                        "reason": {
                            "type": "string",
                            "description": "状态变更原因"
                        }
                    },
                    "required": ["alpha_id", "new_status"]
                }
            },
            {
                "name": "alpha_queue_stats",
                "description": "获取队列统计信息",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "alpha_queue_validate",
                "description": "验证队列数据完整性",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理MCP请求"""
        method = request.get("method")
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                return self._handle_initialize(request, request_id)
            elif method == "tools/list":
                return self._handle_tools_list(request, request_id)
            elif method == "tools/call":
                return self._handle_tools_call(request, request_id)
            else:
                return self._create_error_response(request_id, -32601, "Method not found")
        except Exception as e:
            return self._create_error_response(request_id, -32603, f"Internal error: {str(e)}")
    
    def _handle_initialize(self, request: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """处理初始化请求"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "alpha-queue-mcp-server",
                    "version": "1.0.0"
                }
            }
        }
    
    def _handle_tools_list(self, request: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """处理工具列表请求"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": self.tools
            }
        }
    
    def _handle_tools_call(self, request: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """处理工具调用请求"""
        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name == "alpha_queue_list":
            result = self.queue_manager.list_alphas(arguments.get("status_filter"))
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2, ensure_ascii=False)
                        }
                    ]
                }
            }
        
        elif tool_name == "alpha_queue_add":
            result = self.queue_manager.add_alpha(
                alpha_id=arguments.get("alpha_id"),
                expression=arguments.get("expression", ""),
                status=arguments.get("status", "pending"),
                scheduled_date=arguments.get("scheduled_date", ""),
                priority=arguments.get("priority", 5.0),
                reason=arguments.get("reason", "")
            )
            return self._create_tool_response(request_id, result)
        
        elif tool_name == "alpha_queue_update":
            result = self.queue_manager.update_status(
                alpha_id=arguments.get("alpha_id"),
                new_status=arguments.get("new_status"),
                reason=arguments.get("reason", "")
            )
            return self._create_tool_response(request_id, result)
        
        elif tool_name == "alpha_queue_stats":
            result = self.queue_manager.get_stats()
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2, ensure_ascii=False)
                        }
                    ]
                }
            }
        
        elif tool_name == "alpha_queue_validate":
            result = self.queue_manager.validate_queue()
            return self._create_tool_response(request_id, result)
        
        else:
            return self._create_error_response(request_id, -32601, f"Tool not found: {tool_name}")
    
    def _create_tool_response(self, request_id: Any, result: Dict[str, Any]) -> Dict[str, Any]:
        """创建工具响应"""
        if result.get("success", False):
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2, ensure_ascii=False)
                        }
                    ]
                }
            }
        else:
            return self._create_error_response(request_id, -32000, result.get("error", "Unknown error"))
    
    def _create_error_response(self, request_id: Any, code: int, message: str) -> Dict[str, Any]:
        """创建错误响应"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message
            }
        }


def main():
    """主函数：运行MCP服务器"""
    server = MCPServer()
    
    # 从stdin读取请求，向stdout写入响应
    for line in sys.stdin:
        if not line.strip():
            continue
        
        try:
            request = json.loads(line)
            response = server.handle_request(request)
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
        except json.JSONDecodeError as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            }
            sys.stdout.write(json.dumps(error_response) + "\n")
            sys.stdout.flush()
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            sys.stdout.write(json.dumps(error_response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()