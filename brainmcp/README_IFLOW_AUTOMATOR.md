# IFLOW工作流自动化程序

## 概述

这是一个使用iflow SDK自动调用IFLOW.md文件中定义的工作流的Python程序。程序能够读取IFLOW.md文件，解析工作流定义，并使用iflow CLI自动执行各个阶段。

## 功能特性

1. **自动解析工作流**：读取IFLOW.md文件，提取工作流阶段、约束和工具信息
2. **多模式执行**：支持完整工作流、特定阶段或测试模式
3. **交互式界面**：提供命令行交互界面，方便用户选择执行选项
4. **执行日志**：记录所有执行结果并保存为JSON格式
5. **错误处理**：完善的错误处理和超时控制

## 系统要求

- Python 3.7+
- iflow CLI 0.4.0+
- iflow-cli-sdk 0.2.0+

## 安装和配置

### 1. 检查环境

```bash
# 检查Python版本
python --version

# 检查iflow CLI
iflow --version

# 检查iflow SDK
pip list | grep iflow
```

### 2. 确保IFLOW.md文件存在

程序需要读取当前目录下的`IFLOW.md`文件。请确保该文件存在并包含正确的工作流定义。

## 使用方法

### 方法1：交互式命令行界面

```bash
python iflow_workflow_final.py
```

程序将显示菜单：
```
============================================================
IFLOW工作流自动化程序
============================================================

工作流摘要:
  总阶段数: 6
  关键约束: 3 个
  可用工具: 14 个

工作流阶段:
  Phase 1: 目标与情报 (Initialization & Intelligence)
  Phase 2: AI驱动的智能Alpha生成 (AI-Powered Alpha Generation)
  Phase 3: 智能模拟与动态监控 (Intelligent Simulation & Monitoring)
  Phase 4: AI驱动的迭代优化循环 (AI-Powered Iterative Loop)
  Phase 5: 智能提交前评估 (Intelligent Pre-Submission Check)
  Phase 6: 智能终局报告与知识积累 (Intelligent Final Report & Knowledge Accumulation)

============================================================
请选择执行选项:
  1. 执行完整工作流 (所有阶段)
  2. 执行特定阶段
  3. 测试单个阶段
============================================================
请输入选择 (1-3):
```

### 方法2：直接使用Python类

```python
from iflow_workflow_final import IFLOWWorkflowCLI

# 创建自动化器
automator = IFLOWWorkflowCLI()

# 读取工作流内容
content = automator.read_iflow_content()

# 提取工作流摘要
summary = automator.extract_workflow_summary(content)
print(f"总阶段数: {summary['total_phases']}")

# 执行特定阶段
result = automator.execute_workflow_phase(1, "目标与情报", content)

# 保存执行日志
automator.save_execution_log("my_execution_log.json")
```

### 方法3：批量执行脚本

```python
#!/usr/bin/env python3
from iflow_workflow_final import IFLOWWorkflowCLI
import json

def batch_execute_phases(phase_numbers):
    """批量执行指定阶段"""
    automator = IFLOWWorkflowCLI()
    content = automator.read_iflow_content()
    
    for phase_num in phase_numbers:
        # 这里需要根据实际阶段标题进行调整
        result = automator.execute_workflow_phase(phase_num, "目标与情报", content)
        
        if not result['success']:
            print(f"Phase {phase_num} 执行失败，停止执行")
            break
    
    automator.save_execution_log()

# 执行Phase 1, 2, 3
batch_execute_phases([1, 2, 3])
```

## 程序结构

```
iflow_workflow_final.py
├── IFLOWWorkflowCLI 类
│   ├── __init__() - 初始化
│   ├── read_iflow_content() - 读取IFLOW.md文件
│   ├── extract_workflow_summary() - 提取工作流摘要
│   ├── run_iflow_command() - 执行iflow命令
│   ├── execute_workflow_phase() - 执行单个阶段
│   ├── execute_complete_workflow() - 执行完整工作流
│   └── save_execution_log() - 保存执行日志
└── main() - 主函数
```

## 输出文件

程序会生成以下输出文件：

1. **执行日志** (`iflow_workflow_execution_log.json`)：
   ```json
   {
     "timestamp": "2025-12-26 10:30:00",
     "total_executions": 3,
     "successful_executions": 3,
     "execution_log": [
       {
         "phase_num": 1,
         "phase_title": "目标与情报",
         "prompt_preview": "# IFLOW工作流执行 - Phase 1...",
         "success": true,
         "elapsed_time": 45.2,
         "output_length": 1250,
         "return_code": 0
       }
     ]
   }
   ```

2. **iflow输出**：每个阶段的执行结果会显示在控制台，并包含在日志中。

## 故障排除

### 常见问题

1. **iflow CLI未找到**
   ```
   错误: iflow CLI未安装或不在PATH中
   解决方案: 安装iflow CLI或将其添加到PATH
   ```

2. **IFLOW.md文件不存在**
   ```
   错误: 未找到文件: IFLOW.md
   解决方案: 确保IFLOW.md文件在当前目录
   ```

3. **连接超时**
   ```
   错误: 命令执行超时
   解决方案: 增加超时时间或检查网络连接
   ```

4. **权限问题**
   ```
   错误: 权限被拒绝
   解决方案: 检查文件权限或使用sudo（不推荐）
   ```

### 调试模式

要启用调试模式，可以修改`run_iflow_command()`方法：

```python
def run_iflow_command(self, prompt: str, timeout: int = 300):
    # 添加调试参数
    cmd = ["iflow", "--experimental-acp", "-p", prompt, "--debug"]
    # ...
```

## 自定义配置

### 修改超时时间

```python
# 在execute_workflow_phase方法中修改
result = self.run_iflow_command(prompt, timeout=900)  # 15分钟超时
```

### 自定义输出文件

```python
automator.save_execution_log("custom_log_20251226.json")
```

### 添加额外参数

```python
def run_iflow_command(self, prompt: str, timeout: int = 300):
    cmd = [
        "iflow", 
        "--experimental-acp", 
        "-p", prompt,
        "--max-turns", "50",  # 限制最大轮数
        "--max-tokens", "8000"  # 限制最大token数
    ]
    # ...
```

## 安全注意事项

1. **工具调用确认**：iflow CLI可能会请求工具调用确认，请根据提示操作
2. **文件修改**：工作流执行可能会修改项目文件，建议在测试环境中运行
3. **API调用**：某些工具可能会调用外部API，注意相关费用和限制
4. **敏感信息**：避免在提示中包含敏感信息

## 扩展开发

### 添加新功能

1. **进度显示**：添加进度条显示执行进度
2. **邮件通知**：执行完成后发送邮件通知
3. **结果分析**：自动分析执行结果并生成报告
4. **并行执行**：支持多个阶段并行执行

### 集成其他工具

```python
class EnhancedIFLOWWorkflowCLI(IFLOWWorkflowCLI):
    def __init__(self):
        super().__init__()
        self.report_generator = ReportGenerator()
        self.notifier = EmailNotifier()
    
    def execute_workflow_phase(self, phase_num, phase_title, content):
        result = super().execute_workflow_phase(phase_num, phase_title, content)
        
        # 扩展功能
        if result['success']:
            self.report_generator.generate_phase_report(phase_num, result)
            self.notifier.send_notification(f"Phase {phase_num} 执行完成")
        
        return result
```

## 许可证

MIT License

## 支持

如有问题或建议，请：
1. 检查本文档的故障排除部分
2. 查看程序输出的错误信息
3. 检查执行日志文件
4. 联系开发团队