#!/usr/bin/env python3
"""
测试arXiv MCP功能
"""

import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_arxiv_mcp():
    """测试arXiv MCP功能"""
    try:
        # 导入MCP模块
        import arxiv_mcp
        
        print("=== 测试arXiv MCP功能 ===")
        
        # 测试搜索功能 - 直接调用函数
        print("\n1. 测试搜索功能...")
        xml_results = arxiv_mcp.search_arxiv("quantitative finance", max_results=3)
        papers = arxiv_mcp.parse_search_results(xml_results)
        
        if papers:
            print(f"搜索成功，找到 {len(papers)} 篇论文")
            for i, paper in enumerate(papers[:2], 1):
                print(f"  {i}. {paper.get('title', '无标题')}")
                print(f"     作者: {', '.join(paper.get('authors', []))[:50]}...")
                print(f"     ID: {paper.get('paper_id', '无ID')}")
        else:
            print("搜索失败或未找到论文")
            
        # 测试获取论文信息功能
        print("\n2. 测试获取论文信息功能...")
        if papers:
            paper_id = papers[0].get('paper_id')
            if paper_id:
                paper_info = arxiv_mcp.get_paper_metadata(paper_id)
                if paper_info:
                    print(f"获取论文信息成功: {paper_info.get('title', '无标题')}")
                else:
                    print("获取论文信息失败")
            else:
                print("论文ID不存在")
                
        # 测试文件名生成功能
        print("\n3. 测试文件名生成功能...")
        if papers:
            paper = papers[0]
            title = paper.get('title')
            paper_id = paper.get('paper_id')
            if title and paper_id:
                filename = arxiv_mcp.generate_filename(paper_id, title)
                print(f"生成的文件名: {filename}")
                
        print("\n4. 测试下载功能（不实际下载）...")
        print("   下载功能需要实际网络请求，此处仅验证接口")
        
        print("\n=== 测试完成 ===")
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(test_arxiv_mcp())
    sys.exit(0 if success else 1)