#!/usr/bin/env python3
"""
IFLOW工作流自动化程序
使用iflow SDK自动执行IFLOW.md中定义的工作流
"""

import asyncio
import json
import re
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import iflow_sdk
from iflow_sdk import IFlowClient, AssistantMessage, TaskFinishMessage


class IFLOWWorkflowParser:
    """解析IFLOW.md文件中的工作流定义"""
    
    def __init__(self, iflow_file_path: str):
        self.iflow_file_path = iflow_file_path
        self.content = ""
        self.phases = {}
        
    def parse(self) -> Dict[str, Any]:
        """解析IFLOW.md文件"""
        try:
            with open(self.iflow_file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            
            # 提取工作流阶段
            self._extract_phases()
            
            # 提取关键行为约束
            self._extract_constraints()
            
            # 提取工具库信息
            self._extract_toolkit()
            
            return {
                'phases': self.phases,
                'constraints': self.constraints,
                'toolkit': self.toolkit,
                'raw_content': self.content[:5000]  # 只保留前5000字符用于上下文
            }
        except Exception as e:
            raise Exception(f"解析IFLOW.md文件失败: {e}")
    
    def _extract_phases(self):
        """提取工作流阶段"""
        phase_pattern = r'### Phase (\d+): ([^\n]+)\n\n(.*?)(?=\n### Phase|\n---|\Z)'
        phases = re.findall(phase_pattern, self.content, re.DOTALL)
        
        for phase_num, phase_title, phase_content in phases:
            phase_key = f"Phase {phase_num}"
            self.phases[phase_key] = {
                'title': phase_title.strip(),
                'content': phase_content.strip(),
                'steps': self._extract_phase_steps(phase_content)
            }
    
    def _extract_phase_steps(self, phase_content: str) -> List[str]:
        """提取阶段中的步骤"""
        # 提取编号步骤
        step_pattern = r'\d+\.\s+(.*?)(?=\n\d+\.|\n\*\*|\n###|\Z)'
        steps = re.findall(step_pattern, phase_content, re.DOTALL)
        
        # 清理步骤文本
        cleaned_steps = []
        for step in steps:
            step = step.strip()
            # 移除换行符和多余空格
            step = ' '.join(step.split())
            if step:
                cleaned_steps.append(step)
        
        return cleaned_steps
    
    def _extract_constraints(self):
        """提取关键行为约束"""
        self.constraints = {}
        
        # 提取批量生存法则
        batch_rule_match = re.search(r'### \*\*1\. 批量生存法则.*?\n\n(.*?)(?=\n###|\n---|\Z)', 
                                    self.content, re.DOTALL)
        if batch_rule_match:
            self.constraints['batch_rule'] = batch_rule_match.group(1).strip()
        
        # 提取死循环优化机制
        loop_rule_match = re.search(r'### \*\*2\. 死循环优化机制.*?\n\n(.*?)(?=\n###|\n---|\Z)', 
                                   self.content, re.DOTALL)
        if loop_rule_match:
            self.constraints['loop_rule'] = loop_rule_match.group(1).strip()
        
        # 提取僵尸模拟熔断机制
        zombie_rule_match = re.search(r'### \*\*3\. 僵尸模拟熔断机制.*?\n\n(.*?)(?=\n###|\n---|\Z)', 
                                     self.content, re.DOTALL)
        if zombie_rule_match:
            self.constraints['zombie_rule'] = zombie_rule_match.group(1).strip()
    
    def _extract_toolkit(self):
        """提取核心工具库"""
        toolkit_match = re.search(r'### \*\*核心工具库.*?\n\n(.*?)(?=\n###|\n---|\Z)', 
                                 self.content, re.DOTALL)
        if toolkit_match:
            self.toolkit = toolkit_match.group(1).strip()
        else:
            self.toolkit = ""


class IFLOWWorkflowExecutor:
    """执行IFLOW工作流"""
    
    def __init__(self, workflow_data: Dict[str, Any]):
        self.workflow_data = workflow_data
        self.client = None
        self.current_phase = None
        self.execution_log = []
        
    async def initialize(self):
        """初始化iflow客户端"""
        print("初始化iflow客户端...")
        self.client = IFlowClient()
        await self.client.__aenter__()
        print("iflow客户端初始化完成")
        
    async def cleanup(self):
        """清理资源"""
        if self.client:
            await self.client.__aexit__(None, None, None)
            print("iflow客户端已关闭")
    
    async def execute_workflow(self):
        """执行完整的工作流"""
        print("=" * 60)
        print("开始执行IFLOW工作流")
        print("=" * 60)
        
        try:
            # Phase 1: 目标与情报
            await self.execute_phase("Phase 1", "目标与情报")
            
            # Phase 2: AI驱动的智能Alpha生成
            await self.execute_phase("Phase 2", "AI驱动的智能Alpha生成")
            
            # Phase 3: 智能模拟与动态监控
            await self.execute_phase("Phase 3", "智能模拟与动态监控")
            
            # Phase 4: AI驱动的迭代优化循环
            await self.execute_phase("Phase 4", "AI驱动的迭代优化循环")
            
            # Phase 5: 智能提交前评估
            await self.execute_phase("Phase 5", "智能提交前评估")
            
            # Phase 6: 智能终局报告与知识积累
            await self.execute_phase("Phase 6", "智能终局报告与知识积累")
            
            print("\n" + "=" * 60)
            print("工作流执行完成！")
            print("=" * 60)
            
        except Exception as e:
            print(f"工作流执行失败: {e}")
            raise
    
    async def execute_phase(self, phase_key: str, phase_title: str):
        """执行单个阶段"""
        print(f"\n{'='*40}")
        print(f"执行阶段: {phase_key} - {phase_title}")
        print(f"{'='*40}")
        
        if phase_key not in self.workflow_data['phases']:
            print(f"警告: 未找到阶段 {phase_key}")
            return
        
        phase = self.workflow_data['phases'][phase_key]
        self.current_phase = phase_key
        
        # 构建阶段执行提示
        prompt = self._build_phase_prompt(phase)
        
        # 发送提示到iflow
        response = await self._send_prompt(prompt)
        
        # 记录执行日志
        self.execution_log.append({
            'phase': phase_key,
            'title': phase_title,
            'prompt': prompt[:500],  # 只记录前500字符
            'response': response[:1000]  # 只记录前1000字符
        })
        
        print(f"阶段 {phase_key} 执行完成")
    
    def _build_phase_prompt(self, phase: Dict[str, Any]) -> str:
        """构建阶段执行提示"""
        prompt = f"""# IFLOW工作流 - {phase['title']}

## 阶段描述
{phase['content'][:1000]}

## 具体步骤
"""
        
        for i, step in enumerate(phase['steps'], 1):
            prompt += f"{i}. {step}\n"
        
        prompt += f"""

## 关键约束
{self.workflow_data['constraints'].get('batch_rule', '')[:500]}

## 可用工具
{self.workflow_data['toolkit'][:500]}

请按照上述工作流要求执行本阶段任务。请严格按照IFLOW.md中的规则和约束进行操作。
请开始执行本阶段工作。"""
        
        return prompt
    
    async def _send_prompt(self, prompt: str) -> str:
        """发送提示到iflow并获取响应"""
        if not self.client:
            raise Exception("iflow客户端未初始化")
        
        print(f"发送提示到iflow (长度: {len(prompt)} 字符)...")
        
        await self.client.send_message(prompt)
        
        # 接收响应
        full_response = ""
        async for message in self.client.receive_messages():
            if isinstance(message, AssistantMessage):
                chunk_text = message.chunk.text
                full_response += chunk_text
                print(f"收到响应片段: {chunk_text[:100]}...")
            elif isinstance(message, TaskFinishMessage):
                print(f"任务完成")
                break
        
        print(f"收到完整响应 (长度: {len(full_response)} 字符)")
        return full_response
    
    def save_execution_log(self, output_file: str = "iflow_workflow_execution_log.json"):
        """保存执行日志"""
        log_data = {
            'workflow_summary': {
                'phases_executed': list(self.workflow_data['phases'].keys()),
                'total_phases': len(self.workflow_data['phases'])
            },
            'execution_log': self.execution_log,
            'constraints': self.workflow_data['constraints']
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)
        
        print(f"执行日志已保存到: {output_file}")


async def main():
    """主函数"""
    # 检查IFLOW.md文件是否存在
    iflow_file = "IFLOW.md"
    if not os.path.exists(iflow_file):
        print(f"错误: 未找到 {iflow_file} 文件")
        sys.exit(1)
    
    print("=" * 60)
    print("IFLOW工作流自动化程序")
    print("=" * 60)
    
    # 解析IFLOW.md文件
    print("解析IFLOW.md文件...")
    parser = IFLOWWorkflowParser(iflow_file)
    workflow_data = parser.parse()
    
    print(f"解析完成: 找到 {len(workflow_data['phases'])} 个工作流阶段")
    for phase_key, phase_info in workflow_data['phases'].items():
        print(f"  - {phase_key}: {phase_info['title']} ({len(phase_info['steps'])} 个步骤)")
    
    # 创建工作流执行器
    executor = IFLOWWorkflowExecutor(workflow_data)
    
    try:
        # 初始化
        await executor.initialize()
        
        # 执行工作流
        await executor.execute_workflow()
        
        # 保存执行日志
        executor.save_execution_log()
        
    except Exception as e:
        print(f"程序执行出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理资源
        await executor.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
