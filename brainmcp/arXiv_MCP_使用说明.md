# arXiv MCP 使用说明

## 概述
arXiv MCP 是一个用于搜索和下载arXiv论文的MCP（Model Context Protocol）服务器。它提供了三个主要功能：
1. 搜索arXiv论文
2. 获取论文详细信息
3. 下载论文PDF文件

## 配置状态
✅ **已成功配置**

- **MCP服务器名称**: `arxiv`
- **Python路径**: `/Users/mac/miniconda3/envs/WQ-Brain/bin/python`
- **脚本路径**: `/Users/mac/WQ-Brain/brainmcp/arxiv_mcp.py`
- **配置文件**: `.iflow/settings.json`

## 可用工具

### 1. `search_papers` - 搜索论文
**参数**:
- `query`: 搜索关键词（字符串）
- `max_results`: 最大返回结果数（整数，默认10）

**返回**: 论文列表，每篇论文包含：
- `title`: 论文标题
- `authors`: 作者列表
- `abstract`: 摘要
- `paper_id`: arXiv论文ID
- `published`: 发布日期

### 2. `get_paper_info` - 获取论文详细信息
**参数**:
- `paper_id`: arXiv论文ID（字符串）

**返回**: 论文详细信息

### 3. `download_paper_file` - 下载论文PDF
**参数**:
- `paper_id`: arXiv论文ID（字符串）
- `output_dir`: 输出目录（可选，默认从环境变量`ARXIV_DOWNLOAD_DIR`获取或使用`downloaded_papers`目录）
- `paper_title`: 论文标题（可选，用于文件命名）

**返回**: 下载文件的路径

## 使用示例

### 在iFlow CLI中使用
```bash
# 搜索论文
search_papers query="quantitative finance" max_results=5

# 获取论文信息
get_paper_info paper_id="2111.09395v1"

# 下载论文
download_paper_file paper_id="2111.09395v1" output_dir="./papers"
```

### Python代码示例
```python
import asyncio
import arxiv_mcp

async def example():
    # 搜索论文
    papers = await arxiv_mcp.search_papers("machine learning", max_results=3)
    
    # 获取第一篇论文的详细信息
    if papers:
        paper_id = papers[0]['paper_id']
        paper_info = await arxiv_mcp.get_paper_info(paper_id)
        
        # 下载论文
        filepath = await arxiv_mcp.download_paper_file(
            paper_id=paper_id,
            output_dir="./downloads",
            paper_title=paper_info['title']
        )
        print(f"下载完成: {filepath}")

# 运行示例
asyncio.run(example())
```

## 环境变量

### `ARXIV_DOWNLOAD_DIR`
设置默认下载目录。如果未设置，将使用：
- Windows: 从注册表获取
- 其他系统: 使用`downloaded_papers`目录（在脚本同级目录下创建）

## 文件命名规则
下载的文件将根据论文标题自动命名，规则如下：
1. 移除所有特殊字符（<>:"/\|?*等）
2. 将空格替换为下划线
3. 限制文件名长度不超过150字符
4. 如果文件已存在，自动添加数字后缀

## 测试状态
✅ 所有功能测试通过：
- 搜索功能 ✓
- 获取论文信息 ✓
- 文件名生成 ✓
- MCP服务器启动 ✓

## 注意事项
1. 需要网络连接访问arXiv API
2. 下载功能需要写入权限
3. 搜索功能受arXiv API限制（最多返回1000条结果）
4. 文件名中的特殊字符会被自动处理

## 故障排除

### 常见问题
1. **搜索无结果**: 检查网络连接和搜索关键词
2. **下载失败**: 检查磁盘空间和写入权限
3. **MCP无法启动**: 检查Python环境和依赖

### 依赖检查
```bash
# 检查fastmcp是否安装
python -c "import fastmcp; print(f'fastmcp version: {fastmcp.__version__}')"

# 检查requests是否安装
python -c "import requests; print(f'requests version: {requests.__version__}')"
```

## 更新日志
- **2025-12-18**: 初始配置完成，所有功能测试通过