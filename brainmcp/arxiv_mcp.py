import asyncio
from fastmcp import FastMCP
from typing import List, Dict, Optional
import requests
import xml.etree.ElementTree as ET
import os

# 初始化FastMCP实例
mcp = FastMCP("arxiv-mcp")

def search_arxiv(query: str, max_results: int = 10) -> str:
    """Search arXiv for papers"""
    base_url = "http://export.arxiv.org/api/query"
    params = {
        'search_query': query,
        'start': 0,
        'max_results': max_results
    }

    response = requests.get(base_url, params=params)
    return response.text

def parse_search_results(xml_content: str) -> List[Dict]:
    """Parse XML search results and extract paper information"""
    try:
        root = ET.fromstring(xml_content)
        papers = []

        # Find all entry elements
        for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
            paper_info = {}

            # Extract title
            title_elem = entry.find('.//{http://www.w3.org/2005/Atom}title')
            if title_elem is not None:
                paper_info['title'] = title_elem.text.strip()

            # Extract authors
            authors = []
            for author in entry.findall('.//{http://www.w3.org/2005/Atom}author'):
                name_elem = author.find('.//{http://www.w3.org/2005/Atom}name')
                if name_elem is not None:
                    authors.append(name_elem.text.strip())
            paper_info['authors'] = authors

            # Extract abstract
            summary_elem = entry.find('.//{http://www.w3.org/2005/Atom}summary')
            if summary_elem is not None:
                paper_info['abstract'] = summary_elem.text.strip()

            # Extract paper ID from the id field
            id_elem = entry.find('.//{http://www.w3.org/2005/Atom}id')
            if id_elem is not None:
                # Extract ID from URL like "http://arxiv.org/abs/2103.12345"
                paper_id = id_elem.text.split('/')[-1]
                paper_info['paper_id'] = paper_id

            # Extract published date
            published_elem = entry.find('.//{http://www.w3.org/2005/Atom}published')
            if published_elem is not None:
                paper_info['published'] = published_elem.text.strip()

            papers.append(paper_info)

        return papers
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return []

def get_paper_metadata(paper_id: str) -> Optional[Dict]:
    """Get paper metadata directly from arXiv API"""
    try:
        # Use the arXiv API to get paper metadata
        metadata_url = f"http://export.arxiv.org/api/query?id_list={paper_id}"
        response = requests.get(metadata_url)

        if response.status_code == 200:
            papers = parse_search_results(response.text)
            if papers and len(papers) > 0:
                return papers[0]
        return None
    except Exception as e:
        print(f"Error fetching paper metadata: {e}")
        return None

def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing/replacing problematic characters"""
    # Remove or replace problematic characters
    replacements = {
        '<': '_', '>': '_', ':': '_', '"': '_', '/': '_', '\\': '_', 
        '|': '_', '?': '_', '*': '_', ' ': '_', ':': '_', ';': '_', 
        ',': '_', '.': '_', '(': '_', ')': '_', '[': '_', ']': '_', 
        '{': '_', '}': '_', '!': '_', '@': '_', '#': '_', '$': '_', 
        '%': '_', '^': '_', '&': '_', '+': '_', '=': '_', '`': '_', 
        '~': '_', '\t': '_', '\n': '_', '\r': '_'
    }
    
    # Apply replacements
    for old, new in replacements.items():
        filename = filename.replace(old, new)
    
    # Remove consecutive underscores and trailing/leading underscores
    while '__' in filename:
        filename = filename.replace('__', '_')
    filename = filename.strip('_')
    
    # Limit length and ensure it's not empty
    if len(filename) > 150:
        filename = filename[:150].rstrip('_')
    
    return filename if filename else "untitled"

def generate_filename(paper_id: str, paper_title: str = None) -> str:
    """Generate a clean filename for the paper"""
    if paper_title:
        # Sanitize the title
        clean_title = sanitize_filename(paper_title)
        
        # If title is too short after sanitization, include paper ID
        if len(clean_title) < 10:
            return f"{clean_title}_{paper_id}.pdf"
        else:
            return f"{clean_title}.pdf"
    else:
        return f"{paper_id}.pdf"

def ensure_unique_filename(filepath: str) -> str:
    """Ensure filename is unique by adding suffix if file exists"""
    if not os.path.exists(filepath):
        return filepath
    
    base, ext = os.path.splitext(filepath)
    counter = 1
    while os.path.exists(f"{base}_{counter}{ext}"):
        counter += 1
    return f"{base}_{counter}{ext}"

def download_paper(paper_id: str, output_dir: str = ".", paper_title: str = None) -> Optional[str]:
    """Download a paper by its ID and rename it to the paper title"""
    pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"
    response = requests.get(pdf_url)

    if response.status_code == 200:
        # Generate filename using the new naming logic
        filename = generate_filename(paper_id, paper_title)
        filepath = os.path.join(output_dir, filename)
        
        # Ensure unique filename before downloading
        filepath = ensure_unique_filename(filepath)

        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded: {filepath}")
        return filepath
    else:
        print(f"Failed to download paper {paper_id}")
        return None

@mcp.tool()
async def search_papers(query: str, max_results: int = 10) -> List[Dict]:
    """
    搜索arXiv论文
    Args:
        query: 搜索关键词
        max_results: 最大返回结果数，默认10
    Returns:
        论文列表
    """
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(None, search_arxiv, query, max_results)
    papers = await loop.run_in_executor(None, parse_search_results, results)
    return papers

@mcp.tool()
async def get_paper_info(paper_id: str) -> Optional[Dict]:
    """
    获取论文详细信息
    Args:
        paper_id: 论文ID
    Returns:
        论文详细信息
    """
    loop = asyncio.get_event_loop()
    paper_info = await loop.run_in_executor(None, get_paper_metadata, paper_id)
    return paper_info


@mcp.tool()
async def download_paper_file(paper_id: str, output_dir: str = None, paper_title: str = None) -> Optional[str]:
    """
    下载论文PDF文件
    Args:
        paper_id: 论文ID
        output_dir: 输出目录，默认从ARXIV_DOWNLOAD_DIR环境变量获取，如未设置则使用当前目录
        paper_title: 论文标题（用于文件命名）
    Returns:
        下载文件路径
    """
    # 如果output_dir未指定，则从环境变量获取，否则使用当前目录
    if output_dir is None:
        # 首先尝试从环境变量获取
        output_dir = os.getenv('ARXIV_DOWNLOAD_DIR')
        
        # 如果环境变量不存在，尝试从注册表获取（Windows）
        if output_dir is None and os.name == 'nt':
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
                    output_dir, _ = winreg.QueryValueEx(key, "ARXIV_DOWNLOAD_DIR")
            except (FileNotFoundError, OSError):
                pass
        
        # 如果仍然没有找到，使用默认目录
        if output_dir is None:
            # 设置默认下载目录
            default_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloaded_papers")
            output_dir = default_dir

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    loop = asyncio.get_event_loop()
    filepath = await loop.run_in_executor(None, download_paper, paper_id, output_dir, paper_title)
    return filepath


if __name__ == "__main__":
    mcp.run()
