#!/bin/bash
# IFLOW工作流自动化程序启动脚本

echo "============================================================"
echo "IFLOW工作流自动化程序"
echo "============================================================"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到python3，请安装Python 3.7+"
    exit 1
fi

# 检查iflow CLI
if ! command -v iflow &> /dev/null; then
    echo "错误: 未找到iflow CLI，请安装iflow CLI"
    echo "安装命令: npm install -g @iflow/cli"
    exit 1
fi

# 检查IFLOW.md文件
if [ ! -f "IFLOW.md" ]; then
    echo "错误: 未找到IFLOW.md文件"
    echo "请确保IFLOW.md文件在当前目录"
    exit 1
fi

# 显示iflow版本
iflow_version=$(iflow --version)
echo "iflow CLI版本: $iflow_version"

# 显示Python版本
python_version=$(python3 --version)
echo "Python版本: $python_version"

# 显示文件信息
file_size=$(wc -c < IFLOW.md)
echo "IFLOW.md文件大小: $file_size 字节"

echo ""
echo "准备就绪，开始执行工作流自动化程序..."
echo "============================================================"

# 执行Python程序
python3 iflow_workflow_final.py

echo ""
echo "============================================================"
echo "程序执行完成"
echo "执行日志已保存到: iflow_workflow_execution_log.json"
echo "============================================================"