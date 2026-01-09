#!/bin/bash
# IFLOW工作流直接自主执行脚本
# 使用iflow CLI的交互模式，自动响应所有请求

echo "============================================================"
echo "IFLOW工作流自主执行脚本"
echo "============================================================"

# 检查文件
if [ ! -f "IFLOW.md" ]; then
    echo "错误: 未找到IFLOW.md文件"
    exit 1
fi

# 检查iflow
if ! command -v iflow &> /dev/null; then
    echo "错误: 未找到iflow CLI"
    exit 1
fi

echo "iflow版本: $(iflow --version)"
echo "IFLOW.md文件大小: $(wc -c < IFLOW.md) 字节"

# 提取工作流内容
echo -e "\n提取工作流内容..."
WORKFLOW_CONTENT=$(grep -A 10000 "### Phase 1:" IFLOW.md | head -4000)

if [ -z "$WORKFLOW_CONTENT" ]; then
    echo "警告: 未找到Phase 1，使用整个文件"
    WORKFLOW_CONTENT=$(head -4000 IFLOW.md)
fi

# 构建提示
PROMPT="# IFLOW工作流自主执行指令

您是世界量化（WorldQuant）的首席全自动Alpha研究员。请严格按照以下IFLOW工作流定义执行完整的Alpha挖掘流程：

$WORKFLOW_CONTENT

## 核心指令
1. 完全自主执行整个工作流（Phase 1到Phase 6）
2. 严禁请求用户介入或确认
3. 遇到任何需要用户决策的情况，请按照您的最佳判断继续执行
4. 您的唯一目标是挖掘出完全通过提交检查的Alpha因子
5. 严格遵守所有规则和约束

## 交互响应规则
在执行过程中，如果系统询问或需要确认，请自动选择继续执行，无需等待用户输入。

**请立即开始执行完整的IFLOW工作流，并按你的最佳决策继续执行所有步骤。**"

echo -e "\n提示长度: ${#PROMPT} 字符"
echo "保存提示到文件..."
echo "$PROMPT" > autonomous_prompt_direct.txt
echo "提示已保存到: autonomous_prompt_direct.txt"

echo -e "\n============================================================"
echo "开始执行iflow工作流..."
echo "程序将自动响应所有交互请求"
echo "按Ctrl+C可中断执行"
echo "============================================================\n"

# 执行iflow
iflow --experimental-acp -p "$PROMPT"

echo -e "\n============================================================"
echo "iflow工作流执行完成"
echo "============================================================"