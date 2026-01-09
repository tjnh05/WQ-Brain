#!/usr/bin/env python3
"""
IFLOW工作流自主执行程序
让iflow CLI自主执行整个IFLOW工作流，无需拆分步骤
在需要用户交互时自动回复"请按你的最佳决策继续执行"
"""

import subprocess
import json
import os
import sys
import time
import select
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


class IFLOWAutonomousExecutor:
    """自主执行IFLOW工作流"""
    
    def __init__(self, iflow_file_path: str = "IFLOW.md"):
        self.iflow_file_path = iflow_file_path
        self.execution_log = []
        self.process = None
        self.is_running = False
        
    def read_iflow_content(self) -> str:
        """读取IFLOW.md文件内容"""
        if not os.path.exists(self.iflow_file_path):
            raise FileNotFoundError(f"未找到文件: {self.iflow_file_path}")
        
        with open(self.iflow_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"已读取IFLOW.md文件 (长度: {len(content)} 字符)")
        return content
    
    def build_autonomous_prompt(self, iflow_content: str) -> str:
        """构建自主执行提示"""
        # 提取工作流的核心部分（去掉前面的规则说明）
        workflow_start = iflow_content.find('### **全自动执行工作流 (EXECUTION WORKFLOW)')
        if workflow_start == -1:
            workflow_start = iflow_content.find('### Phase 1:')
        
        if workflow_start == -1:
            # 如果找不到工作流部分，使用整个文件
            workflow_content = iflow_content
        else:
            workflow_content = iflow_content[workflow_start:]
        
        # 构建提示
        prompt = f"""# IFLOW工作流自主执行

## 工作流定义
{workflow_content[:5000]}  # 限制内容长度

## 执行要求
您是世界量化（WorldQuant）的首席全自动Alpha研究员。请严格按照上述IFLOW工作流定义执行完整的Alpha挖掘流程。

## 核心原则
1. **完全自主**：您必须完全自主地管理研究生命周期，严禁请求用户介入
2. **结果导向**：您的唯一目标是挖掘出完全通过提交检查（Submission Check Passed）的Alpha因子
3. **闭环优化**：工作流是闭环的，严禁在Alpha未通过所有测试前停止
4. **批量生存法则**：严格遵守8/4规则（通用地区8个表达式，IND地区4个表达式）

## 交互规则
在执行过程中，如果遇到需要用户确认或决策的情况，请：
1. 继续按照您的最佳判断执行
2. 无需等待用户确认
3. 保持工作流的连续性和自主性

## 开始执行
请立即开始执行完整的IFLOW工作流。从Phase 1开始，按照工作流定义自主执行所有阶段，直到成功挖掘出可通过提交检查的Alpha因子。

**请按你的最佳决策继续执行。**"""
        
        return prompt
    
    def send_continue_response(self, process, response: str = "请按你的最佳决策继续执行"):
        """发送继续执行的响应"""
        try:
            # 发送响应并换行
            process.stdin.write(response + "\n")
            process.stdin.flush()
            print(f"已发送自动响应: {response}")
        except Exception as e:
            print(f"发送响应失败: {e}")
    
    def monitor_and_respond(self, process, timeout: int = 3600):
        """监控进程输出并在需要时自动响应"""
        print(f"开始监控iflow进程 (超时: {timeout}秒)...")
        
        start_time = time.time()
        last_activity_time = start_time
        output_buffer = ""
        
        while self.is_running and process.poll() is None:
            # 检查超时
            if time.time() - start_time > timeout:
                print(f"执行超时 ({timeout}秒)，终止进程")
                process.terminate()
                break
            
            # 检查是否长时间无输出
            if time.time() - last_activity_time > 300:  # 5分钟无活动
                print("检测到长时间无活动，发送继续执行提示...")
                self.send_continue_response(process)
                last_activity_time = time.time()
            
            # 使用select检查是否有输出可读
            readable, _, _ = select.select([process.stdout, process.stderr], [], [], 1.0)
            
            for stream in readable:
                if stream == process.stdout:
                    line = process.stdout.readline()
                    if line:
                        output_buffer += line
                        last_activity_time = time.time()
                        
                        # 打印输出
                        sys.stdout.write(line)
                        sys.stdout.flush()
                        
                        # 检查是否需要自动响应
                        if self._needs_auto_response(line):
                            print("\n检测到需要用户交互，发送自动响应...")
                            self.send_continue_response(process)
                
                elif stream == process.stderr:
                    line = process.stderr.readline()
                    if line:
                        sys.stderr.write(line)
                        sys.stderr.flush()
                        last_activity_time = time.time()
            
            # 定期检查进程状态
            time.sleep(0.1)
        
        # 读取剩余输出
        try:
            remaining_stdout, remaining_stderr = process.communicate(timeout=5)
            if remaining_stdout:
                output_buffer += remaining_stdout
                sys.stdout.write(remaining_stdout)
            if remaining_stderr:
                sys.stderr.write(remaining_stderr)
        except subprocess.TimeoutExpired:
            process.kill()
            remaining_stdout, remaining_stderr = process.communicate()
        
        return output_buffer
    
    def _needs_auto_response(self, line: str) -> bool:
        """检查是否需要自动响应"""
        line_lower = line.lower()
        
        # 检查是否在询问用户
        prompts = [
            "confirm", "continue", "proceed", "yes/no", "y/n",
            "是否", "确认", "继续", "同意", "请选择",
            "do you", "would you", "should i", "can i",
            "?", "？"
        ]
        
        for prompt in prompts:
            if prompt in line_lower:
                return True
        
        # 检查是否在等待输入
        if any(indicator in line for indicator in [":", ">", "?", "？", "[Y/n]", "(y/n)"]):
            return True
        
        return False
    
    def execute_autonomous_workflow(self, timeout: int = 7200):
        """自主执行完整工作流"""
        print("=" * 60)
        print("IFLOW工作流自主执行程序")
        print("=" * 60)
        
        # 读取IFLOW.md文件
        try:
            iflow_content = self.read_iflow_content()
        except FileNotFoundError as e:
            print(f"错误: {e}")
            return False
        
        # 构建自主执行提示
        prompt = self.build_autonomous_prompt(iflow_content)
        
        print(f"\n构建的提示长度: {len(prompt)} 字符")
        print(f"提示预览:\n{prompt[:500]}...\n")
        
        # 保存提示到临时文件（用于调试）
        with open("autonomous_prompt.txt", "w", encoding="utf-8") as f:
            f.write(prompt)
        print("提示已保存到: autonomous_prompt.txt")
        
        # 执行iflow命令
        print(f"\n开始执行iflow工作流 (超时: {timeout}秒)...")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            # 启动iflow进程
            self.is_running = True
            self.process = subprocess.Popen(
                ["iflow", "--experimental-acp", "-p", prompt],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                bufsize=1,
                universal_newlines=True
            )
            
            print(f"iflow进程已启动 (PID: {self.process.pid})")
            
            # 监控并自动响应
            output = self.monitor_and_respond(self.process, timeout)
            
            # 等待进程结束
            return_code = self.process.wait()
            elapsed_time = time.time() - start_time
            
            print(f"\n" + "="*60)
            print(f"iflow进程已结束")
            print(f"返回码: {return_code}")
            print(f"执行时间: {elapsed_time:.1f}秒")
            print(f"输出长度: {len(output)} 字符")
            print("="*60)
            
            # 记录执行结果
            result = {
                'success': return_code == 0,
                'return_code': return_code,
                'elapsed_time': elapsed_time,
                'output_length': len(output),
                'output_preview': output[:1000] if output else "",
                'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.execution_log.append(result)
            
            # 保存输出到文件
            output_file = f"iflow_autonomous_output_{int(time.time())}.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"完整输出已保存到: {output_file}")
            
            return result['success']
            
        except Exception as e:
            print(f"执行失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            self.is_running = False
            if self.process and self.process.poll() is None:
                self.process.terminate()
    
    def save_execution_log(self, output_file: str = "iflow_autonomous_execution_log.json"):
        """保存执行日志"""
        if not self.execution_log:
            print("没有执行日志可保存")
            return
        
        log_data = {
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'total_executions': len(self.execution_log),
            'execution_log': self.execution_log
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
        
        print(f"执行日志已保存到: {output_file}")
    
    def run_interactive(self):
        """交互式运行"""
        print("=" * 60)
        print("IFLOW工作流自主执行程序")
        print("=" * 60)
        
        print("\n选项:")
        print("  1. 执行完整工作流 (推荐)")
        print("  2. 查看IFLOW.md摘要")
        print("  3. 退出")
        
        choice = input("\n请选择 (1-3): ").strip()
        
        if choice == "1":
            # 设置超时时间（默认2小时）
            timeout_input = input("请输入超时时间（秒，默认7200）: ").strip()
            timeout = int(timeout_input) if timeout_input else 7200
            
            print(f"\n开始执行，超时时间: {timeout}秒")
            print("程序将自动响应所有用户交互请求")
            print("="*60)
            
            success = self.execute_autonomous_workflow(timeout)
            
            if success:
                print("\n✓ 工作流执行完成")
            else:
                print("\n✗ 工作流执行失败")
            
            # 保存日志
            self.save_execution_log()
            
        elif choice == "2":
            # 显示IFLOW.md摘要
            try:
                content = self.read_iflow_content()
                print(f"\nIFLOW.md文件摘要:")
                print(f"文件大小: {len(content)} 字符")
                
                # 查找关键部分
                sections = [
                    ("核心工具库", "核心工具库"),
                    ("关键行为约束", "关键行为约束"),
                    ("Phase 1", "Phase 1:"),
                    ("Phase 6", "Phase 6:"),
                ]
                
                for name, keyword in sections:
                    if keyword in content:
                        start = content.find(keyword)
                        end = content.find("\n###", start + 1)
                        if end == -1:
                            end = min(start + 500, len(content))
                        preview = content[start:end].strip()
                        print(f"\n{name}:\n{preview[:300]}...")
                
            except Exception as e:
                print(f"读取文件失败: {e}")
        
        elif choice == "3":
            print("退出程序")
            return
        
        else:
            print("无效选择")


def main():
    """主函数"""
    executor = IFLOWAutonomousExecutor()
    
    try:
        executor.run_interactive()
    except KeyboardInterrupt:
        print("\n\n用户中断执行")
    except Exception as e:
        print(f"\n程序执行出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n程序结束")


if __name__ == "__main__":
    main()