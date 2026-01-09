#!/usr/bin/env python3
"""
IFLOW工作流简单自主执行程序
直接执行整个工作流，自动响应所有交互
"""

import subprocess
import os
import sys
import time


def read_iflow_file():
    """读取IFLOW.md文件"""
    if not os.path.exists("IFLOW.md"):
        print("错误: 未找到IFLOW.md文件")
        return None
    
    with open("IFLOW.md", 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"已读取IFLOW.md文件 (长度: {len(content)} 字符)")
    return content


def build_simple_prompt(iflow_content):
    """构建简单提示"""
    # 提取工作流部分
    workflow_start = iflow_content.find('### Phase 1:')
    if workflow_start == -1:
        workflow_content = iflow_content
    else:
        workflow_content = iflow_content[workflow_start:]
    
    prompt = f"""# IFLOW工作流自主执行指令

您是世界量化（WorldQuant）的首席全自动Alpha研究员。请严格按照以下IFLOW工作流定义执行完整的Alpha挖掘流程：

{workflow_content[:4000]}

## 重要指令
1. 您必须完全自主地执行整个工作流，从Phase 1到Phase 6
2. 严禁请求用户介入或确认
3. 遇到任何需要用户决策的情况，请按照您的最佳判断继续执行
4. 您的唯一目标是挖掘出完全通过提交检查的Alpha因子
5. 严格遵守所有规则和约束（8/4规则、僵尸模拟熔断机制等）

## 交互响应规则
在执行过程中，如果系统询问或需要确认，请：
- 自动选择继续执行
- 无需等待用户输入
- 保持工作流连续性

**请立即开始执行完整的IFLOW工作流，并按你的最佳决策继续执行所有步骤。**"""
    
    return prompt


def run_autonomous_workflow():
    """运行自主工作流"""
    print("=" * 60)
    print("IFLOW工作流自主执行")
    print("=" * 60)
    
    # 读取文件
    iflow_content = read_iflow_file()
    if not iflow_content:
        return False
    
    # 构建提示
    prompt = build_simple_prompt(iflow_content)
    
    print(f"\n提示长度: {len(prompt)} 字符")
    print("提示已准备就绪")
    
    # 保存提示到文件（可选）
    with open("autonomous_prompt.txt", "w", encoding="utf-8") as f:
        f.write(prompt)
    print("提示已保存到: autonomous_prompt.txt")
    
    print("\n" + "="*60)
    print("开始执行iflow工作流...")
    print("程序将自动响应所有交互请求")
    print("="*60 + "\n")
    
    # 执行命令
    try:
        # 使用简单的subprocess.run，让iflow处理交互
        result = subprocess.run(
            ["iflow", "--experimental-acp", "-p", prompt],
            text=True,
            encoding='utf-8',
            capture_output=False,  # 不捕获输出，直接显示
            timeout=3600  # 1小时超时
        )
        
        print("\n" + "="*60)
        print("iflow工作流执行完成")
        print(f"返回码: {result.returncode}")
        print("="*60)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("\n" + "="*60)
        print("执行超时（1小时）")
        print("="*60)
        return False
        
    except Exception as e:
        print(f"\n执行失败: {e}")
        return False


def main():
    """主函数"""
    print("IFLOW工作流自主执行程序")
    print("=" * 60)
    
    print("\n此程序将：")
    print("1. 读取IFLOW.md文件中的工作流定义")
    print("2. 让iflow CLI自主执行整个工作流")
    print("3. 自动响应所有用户交互请求")
    print("4. 按照'请按你的最佳决策继续执行'原则执行")
    
    print("\n" + "="*60)
    input("按Enter键开始执行，或按Ctrl+C取消...")
    
    success = run_autonomous_workflow()
    
    print("\n" + "="*60)
    if success:
        print("✓ 工作流执行成功完成")
    else:
        print("✗ 工作流执行失败或中断")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户取消执行")
    except Exception as e:
        print(f"\n程序错误: {e}")