#!/usr/bin/env python3
"""
IFLOW工作流自动化程序 - 最终版
使用iflow CLI自动执行IFLOW.md中定义的工作流
"""

import subprocess
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any


class IFLOWWorkflowCLI:
    """使用iflow CLI执行工作流"""
    
    def __init__(self, iflow_file_path: str = "IFLOW.md"):
        self.iflow_file_path = iflow_file_path
        self.execution_log = []
        
    def read_iflow_content(self) -> str:
        """读取IFLOW.md文件内容"""
        if not os.path.exists(self.iflow_file_path):
            raise FileNotFoundError(f"未找到文件: {self.iflow_file_path}")
        
        with open(self.iflow_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"已读取IFLOW.md文件 (长度: {len(content)} 字符)")
        return content
    
    def extract_workflow_summary(self, content: str) -> Dict[str, Any]:
        """提取工作流摘要信息"""
        summary = {
            'total_phases': 0,
            'phases': [],
            'key_constraints': [],
            'available_tools': []
        }
        
        # 提取阶段信息
        import re
        phase_pattern = r'### Phase (\d+): ([^\n]+)'
        phases = re.findall(phase_pattern, content)
        summary['total_phases'] = len(phases)
        summary['phases'] = [{'num': num, 'title': title} for num, title in phases]
        
        # 提取关键约束
        constraint_pattern = r'### \*\*(\d+\. [^\n]+)\*\*\s*\n\n(.*?)(?=\n###|\n---|\Z)'
        constraints = re.findall(constraint_pattern, content, re.DOTALL)
        summary['key_constraints'] = [{'title': title, 'content': content.strip()} 
                                     for title, content in constraints[:3]]  # 只取前3个
        
        # 提取工具信息
        if '核心工具库' in content:
            toolkit_start = content.find('核心工具库')
            toolkit_end = content.find('###', toolkit_start + 1)
            if toolkit_end == -1:
                toolkit_end = len(content)
            toolkit_section = content[toolkit_start:toolkit_end]
            summary['available_tools'] = self._extract_tools_from_section(toolkit_section)
        
        return summary
    
    def _extract_tools_from_section(self, section: str) -> List[str]:
        """从章节中提取工具列表"""
        tools = []
        lines = section.split('\n')
        for line in lines:
            if '`' in line:
                # 提取反引号中的工具名
                import re
                tool_matches = re.findall(r'`([^`]+)`', line)
                tools.extend(tool_matches)
        return list(set(tools))[:20]  # 去重并限制数量
    
    def run_iflow_command(self, prompt: str, timeout: int = 300) -> Dict[str, Any]:
        """运行iflow命令"""
        print(f"执行iflow命令 (超时: {timeout}秒)...")
        
        # 构建命令
        cmd = ["iflow", "--experimental-acp", "-p", prompt]
        
        try:
            start_time = time.time()
            
            # 执行命令
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8'
            )
            
            # 等待完成或超时
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                return_code = process.returncode
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                return_code = -1
                print("命令执行超时")
            
            elapsed_time = time.time() - start_time
            
            result = {
                'success': return_code == 0,
                'return_code': return_code,
                'stdout': stdout,
                'stderr': stderr,
                'elapsed_time': elapsed_time,
                'command': ' '.join(cmd[:3]) + ' ...'  # 隐藏完整提示
            }
            
            print(f"命令执行完成 (耗时: {elapsed_time:.1f}秒, 返回码: {return_code})")
            if stdout:
                print(f"输出长度: {len(stdout)} 字符")
            
            return result
            
        except Exception as e:
            print(f"命令执行失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'stdout': '',
                'stderr': '',
                'elapsed_time': 0
            }
    
    def execute_workflow_phase(self, phase_num: int, phase_title: str, 
                              workflow_content: str) -> Dict[str, Any]:
        """执行单个工作流阶段"""
        print(f"\n{'='*60}")
        print(f"执行阶段 {phase_num}: {phase_title}")
        print(f"{'='*60}")
        
        # 构建阶段执行提示
        prompt = self._build_phase_prompt(phase_num, phase_title, workflow_content)
        
        # 执行命令
        result = self.run_iflow_command(prompt, timeout=600)  # 10分钟超时
        
        # 记录执行日志
        log_entry = {
            'phase_num': phase_num,
            'phase_title': phase_title,
            'prompt_preview': prompt[:200],
            'success': result['success'],
            'elapsed_time': result['elapsed_time'],
            'output_length': len(result['stdout']),
            'return_code': result.get('return_code', -1)
        }
        
        self.execution_log.append(log_entry)
        
        return result
    
    def _build_phase_prompt(self, phase_num: int, phase_title: str, 
                           workflow_content: str) -> str:
        """构建阶段执行提示"""
        # 提取该阶段的内容
        phase_pattern = f'### Phase {phase_num}: {phase_title}'
        start_idx = workflow_content.find(phase_pattern)
        
        if start_idx == -1:
            # 如果找不到精确匹配，尝试模糊匹配
            phase_pattern = f'### Phase {phase_num}:'
            start_idx = workflow_content.find(phase_pattern)
        
        if start_idx == -1:
            # 如果还是找不到，使用通用提示
            return f"""请执行IFLOW工作流的Phase {phase_num}: {phase_title}。

请按照IFLOW.md文件中的工作流定义执行本阶段任务。"""
        
        # 查找阶段结束位置
        end_idx = workflow_content.find('### Phase', start_idx + 1)
        if end_idx == -1:
            end_idx = len(workflow_content)
        
        phase_content = workflow_content[start_idx:end_idx].strip()
        
        # 构建提示
        prompt = f"""# IFLOW工作流执行 - Phase {phase_num}: {phase_title}

## 阶段内容
{phase_content[:3000]}  # 限制内容长度

## 执行要求
请严格按照上述工作流定义执行本阶段任务。您需要：
1. 理解本阶段的目标和要求
2. 按照工作流步骤执行
3. 使用可用的工具和资源
4. 遵循所有约束和规则
5. 自主完成本阶段工作

请开始执行Phase {phase_num}: {phase_title}。"""
        
        return prompt
    
    def execute_complete_workflow(self):
        """执行完整的工作流"""
        print("=" * 60)
        print("IFLOW工作流自动化程序")
        print("=" * 60)
        
        # 读取IFLOW.md文件
        content = self.read_iflow_content()
        
        # 提取工作流摘要
        summary = self.extract_workflow_summary(content)
        
        print(f"\n工作流摘要:")
        print(f"  总阶段数: {summary['total_phases']}")
        print(f"  关键约束: {len(summary['key_constraints'])} 个")
        print(f"  可用工具: {len(summary['available_tools'])} 个")
        
        # 显示阶段列表
        print("\n工作流阶段:")
        for phase in summary['phases']:
            print(f"  Phase {phase['num']}: {phase['title']}")
        
        # 询问用户要执行的阶段
        print("\n" + "="*60)
        print("请选择执行选项:")
        print("  1. 执行完整工作流 (所有阶段)")
        print("  2. 执行特定阶段")
        print("  3. 测试单个阶段")
        print("="*60)
        
        choice = input("请输入选择 (1-3): ").strip()
        
        if choice == "1":
            # 执行完整工作流
            self._execute_all_phases(summary['phases'], content)
        elif choice == "2":
            # 执行特定阶段
            self._execute_specific_phases(summary['phases'], content)
        elif choice == "3":
            # 测试单个阶段
            self._test_single_phase(summary['phases'], content)
        else:
            print("无效选择，退出程序。")
            return
        
        # 保存执行日志
        self.save_execution_log()
        
        print("\n" + "="*60)
        print("程序执行完成")
        print("="*60)
    
    def _execute_all_phases(self, phases: List[Dict], content: str):
        """执行所有阶段"""
        print(f"\n开始执行完整工作流 ({len(phases)} 个阶段)...")
        
        results = []
        for phase in phases:
            phase_num = int(phase['num'])
            phase_title = phase['title']
            
            print(f"\n>>> 开始执行 Phase {phase_num}: {phase_title}")
            result = self.execute_workflow_phase(phase_num, phase_title, content)
            results.append(result)
            
            # 检查是否成功
            if not result['success']:
                print(f"警告: Phase {phase_num} 执行失败")
                continue_option = input("是否继续执行下一个阶段? (y/n): ").strip().lower()
                if continue_option != 'y':
                    print("用户选择停止执行")
                    break
        
        print(f"\n完整工作流执行完成，共执行 {len(results)} 个阶段")
    
    def _execute_specific_phases(self, phases: List[Dict], content: str):
        """执行特定阶段"""
        print("\n可用阶段:")
        for phase in phases:
            print(f"  {phase['num']}. Phase {phase['num']}: {phase['title']}")
        
        phase_nums = input("\n请输入要执行的阶段编号 (用逗号分隔，如: 1,3,5): ").strip()
        
        try:
            selected_nums = [int(num.strip()) for num in phase_nums.split(',') if num.strip()]
        except ValueError:
            print("输入格式错误，退出程序。")
            return
        
        # 过滤有效的阶段
        valid_phases = []
        for num in selected_nums:
            phase = next((p for p in phases if int(p['num']) == num), None)
            if phase:
                valid_phases.append(phase)
            else:
                print(f"警告: Phase {num} 不存在")
        
        if not valid_phases:
            print("没有有效的阶段可执行，退出程序。")
            return
        
        print(f"\n开始执行 {len(valid_phases)} 个选定阶段...")
        
        for phase in valid_phases:
            phase_num = int(phase['num'])
            phase_title = phase['title']
            
            print(f"\n>>> 开始执行 Phase {phase_num}: {phase_title}")
            self.execute_workflow_phase(phase_num, phase_title, content)
    
    def _test_single_phase(self, phases: List[Dict], content: str):
        """测试单个阶段"""
        print("\n可用阶段:")
        for phase in phases:
            print(f"  {phase['num']}. Phase {phase['num']}: {phase['title']}")
        
        phase_num = input("\n请输入要测试的阶段编号: ").strip()
        
        try:
            phase_num_int = int(phase_num)
        except ValueError:
            print("输入格式错误，退出程序。")
            return
        
        # 查找阶段
        phase = next((p for p in phases if int(p['num']) == phase_num_int), None)
        if not phase:
            print(f"错误: Phase {phase_num_int} 不存在")
            return
        
        print(f"\n测试 Phase {phase_num_int}: {phase['title']}")
        
        # 使用简化的测试提示
        test_prompt = f"""请简要说明IFLOW工作流中Phase {phase_num_int}的主要任务和执行步骤。

请基于IFLOW.md文件中的工作流定义回答。"""
        
        print(f"发送测试提示...")
        result = self.run_iflow_command(test_prompt, timeout=120)
        
        if result['success'] and result['stdout']:
            print(f"\n测试结果:")
            print(result['stdout'][:1000])  # 显示前1000字符
        else:
            print(f"测试失败: {result.get('stderr', '未知错误')}")
    
    def save_execution_log(self, output_file: str = "iflow_workflow_execution_log.json"):
        """保存执行日志"""
        if not self.execution_log:
            print("没有执行日志可保存")
            return
        
        log_data = {
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'total_executions': len(self.execution_log),
            'successful_executions': sum(1 for log in self.execution_log if log['success']),
            'execution_log': self.execution_log
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
        
        print(f"执行日志已保存到: {output_file}")


def main():
    """主函数"""
    automator = IFLOWWorkflowCLI()
    
    try:
        automator.execute_complete_workflow()
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