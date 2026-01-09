#!/usr/bin/env python3
"""
测试最终程序的基本功能
"""

import os
import sys
import json
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_functions():
    """测试基本功能"""
    print("="*60)
    print("测试IFLOW工作流自动化程序基本功能")
    print("="*60)
    
    # 测试1: 检查IFLOW.md文件
    print("\n测试1: 检查IFLOW.md文件")
    iflow_path = "IFLOW.md"
    if os.path.exists(iflow_path):
        file_size = os.path.getsize(iflow_path)
        print(f"  ✓ 找到IFLOW.md文件 (大小: {file_size} 字节)")
        
        # 读取文件内容
        with open(iflow_path, 'r', encoding='utf-8') as f:
            content = f.read(5000)  # 只读取前5000字符
        
        # 检查关键内容
        checks = [
            ("Phase 1", "Phase 1: 目标与情报"),
            ("Phase 2", "Phase 2: AI驱动的智能Alpha生成"),
            ("核心工具库", "核心工具库"),
            ("关键行为约束", "关键行为约束"),
        ]
        
        for check_name, check_content in checks:
            if check_content in content:
                print(f"  ✓ 找到 '{check_name}' 部分")
            else:
                print(f"  ✗ 未找到 '{check_name}' 部分")
    else:
        print(f"  ✗ 未找到IFLOW.md文件")
        return False
    
    # 测试2: 检查iflow CLI
    print("\n测试2: 检查iflow CLI")
    try:
        import subprocess
        result = subprocess.run(["iflow", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ iflow CLI已安装 (版本: {result.stdout.strip()})")
        else:
            print(f"  ✗ iflow CLI检查失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"  ✗ iflow CLI检查失败: {e}")
        return False
    
    # 测试3: 检查Python模块
    print("\n测试3: 检查Python模块")
    required_modules = ['json', 'os', 'sys', 'time', 'pathlib', 'subprocess', 're']
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✓ 模块 '{module}' 可用")
        except ImportError:
            print(f"  ✗ 模块 '{module}' 不可用")
            return False
    
    # 测试4: 测试程序类的基本功能
    print("\n测试4: 测试程序类的基本功能")
    try:
        # 导入并测试类
        from iflow_workflow_final import IFLOWWorkflowCLI
        
        automator = IFLOWWorkflowCLI()
        
        # 测试文件读取
        content = automator.read_iflow_content()
        print(f"  ✓ 文件读取成功 (长度: {len(content)} 字符)")
        
        # 测试工作流摘要提取
        summary = automator.extract_workflow_summary(content)
        print(f"  ✓ 工作流摘要提取成功")
        print(f"    总阶段数: {summary['total_phases']}")
        print(f"    可用工具数: {len(summary['available_tools'])}")
        
        # 测试提示构建
        test_prompt = automator._build_phase_prompt(1, "目标与情报", content[:5000])
        print(f"  ✓ 提示构建成功 (长度: {len(test_prompt)} 字符)")
        
    except Exception as e:
        print(f"  ✗ 程序类测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "="*60)
    print("所有基本功能测试通过！")
    print("="*60)
    return True

def create_usage_example():
    """创建使用示例"""
    print("\n" + "="*60)
    print("使用示例")
    print("="*60)
    
    example_code = '''# 示例1: 执行完整工作流
python iflow_workflow_final.py

# 示例2: 直接使用类
from iflow_workflow_final import IFLOWWorkflowCLI

# 创建自动化器
automator = IFLOWWorkflowCLI()

# 读取工作流内容
content = automator.read_iflow_content()

# 提取摘要
summary = automator.extract_workflow_summary(content)

# 执行特定阶段
result = automator.execute_workflow_phase(1, "目标与情报", content)

# 保存日志
automator.save_execution_log()

# 示例3: 命令行测试
python iflow_workflow_final.py
# 然后选择:
#   1. 执行完整工作流 (所有阶段)
#   2. 执行特定阶段
#   3. 测试单个阶段'''
    
    print(example_code)
    
    print("\n" + "="*60)
    print("程序功能说明")
    print("="*60)
    print("""
1. 自动读取IFLOW.md文件中的工作流定义
2. 提取工作流阶段、约束和工具信息
3. 使用iflow CLI执行各个阶段
4. 支持完整工作流、特定阶段或测试模式
5. 记录执行日志并保存为JSON文件
6. 提供交互式命令行界面
    """)

def main():
    """主函数"""
    print("IFLOW工作流自动化程序测试")
    print("="*60)
    
    # 运行基本功能测试
    if test_basic_functions():
        # 创建使用示例
        create_usage_example()
        
        print("\n" + "="*60)
        print("下一步:")
        print("  1. 运行完整程序: python iflow_workflow_final.py")
        print("  2. 选择执行模式 (1-3)")
        print("  3. 查看生成的执行日志")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("测试失败，请检查环境和配置")
        print("="*60)
        sys.exit(1)

if __name__ == "__main__":
    main()