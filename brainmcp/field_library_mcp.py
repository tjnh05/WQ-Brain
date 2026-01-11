#!/usr/bin/env python3
"""
Alpha字段库MCP服务器（FastMCP版本）
提供字段推荐、变体生成、表达式分析等功能的MCP工具接口
使用FastMCP框架简化开发
"""

import json
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP

# 导入现有字段库
try:
    from alpha_field_library import AlphaFieldLibrary
    FIELD_LIBRARY_AVAILABLE = True
except ImportError as e:
    FIELD_LIBRARY_AVAILABLE = False
    print(f"警告: 无法导入 AlphaFieldLibrary: {e}")

# 创建FastMCP应用
app = FastMCP(
    name="field-library",
    version="1.0.0"
)

class FieldLibraryManager:
    """字段库管理器"""
    
    def __init__(self):
        """初始化字段库管理器"""
        if FIELD_LIBRARY_AVAILABLE:
            try:
                self.library = AlphaFieldLibrary()
                self.initialized = True
            except Exception as e:
                print(f"初始化字段库失败: {e}")
                self.initialized = False
        else:
            self.initialized = False
    
    def recommend_fields(self, region: str = 'IND', alpha_type: str = 'REGULAR', 
                        num_fields: int = 3) -> Dict[str, Any]:
        """推荐适合的字段"""
        if not self.initialized:
            return {"success": False, "error": "字段库未初始化"}
        
        try:
            fields = self.library.recommend_fields(region, alpha_type, num_fields)
            return {
                "success": True,
                "fields": fields,
                "count": len(fields),
                "region": region,
                "alpha_type": alpha_type
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def generate_variants(self, region: str = 'IND', alpha_type: str = 'REGULAR',
                         num_variants: int = 8, strategy: str = 'balanced') -> Dict[str, Any]:
        """生成多个Alpha表达式变体"""
        if not self.initialized:
            return {"success": False, "error": "字段库未初始化"}
        
        try:
            variants = self.library.generate_variants(region, alpha_type, num_variants, strategy)
            return {
                "success": True,
                "variants": variants,
                "count": len(variants),
                "region": region,
                "alpha_type": alpha_type,
                "strategy": strategy
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def optimize_alpha(self, original_expr: str, original_field: str) -> Dict[str, Any]:
        """优化高相关性Alpha"""
        if not self.initialized:
            return {"success": False, "error": "字段库未初始化"}
        
        try:
            optimizations = self.library.optimize_high_correlation_alpha(original_expr, original_field)
            return {
                "success": True,
                "optimizations": optimizations,
                "count": len(optimizations),
                "original_expression": original_expr,
                "original_field": original_field
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def analyze_expression(self, expression: str) -> Dict[str, Any]:
        """分析表达式特征"""
        if not self.initialized:
            return {"success": False, "error": "字段库未初始化"}
        
        try:
            analysis = self.library.analyze_expression(expression)
            return {
                "success": True,
                "analysis": analysis,
                "expression": expression
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_fields(self, dataset: str = None, data_type: str = None,
                     max_risk: str = 'MEDIUM', min_success_rate: float = 0.0) -> Dict[str, Any]:
        """搜索符合条件的字段"""
        if not self.initialized:
            return {"success": False, "error": "字段库未初始化"}
        
        try:
            fields = self.library.search_fields(dataset, data_type, max_risk, min_success_rate)
            return {
                "success": True,
                "fields": fields,
                "count": len(fields),
                "dataset": dataset,
                "data_type": data_type,
                "max_risk": max_risk,
                "min_success_rate": min_success_rate
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

# 创建字段库管理器实例
manager = FieldLibraryManager()

# FastMCP工具定义

@app.tool(name="field_library_recommend")
def recommend_fields(
    region: str = "IND",
    alpha_type: str = "REGULAR",
    num_fields: int = 3
) -> str:
    """
    智能字段推荐
    
    Args:
        region: 区域代码 (如 IND, USA, EUR)
        alpha_type: Alpha类型 (REGULAR 或 POWER_POOL)
        num_fields: 推荐的字段数量
    """
    result = manager.recommend_fields(region, alpha_type, num_fields)
    return json.dumps(result, indent=2, ensure_ascii=False)


@app.tool(name="field_library_generate_variants")
def generate_variants(
    region: str = "IND",
    alpha_type: str = "REGULAR",
    num_variants: int = 8,
    strategy: str = "balanced"
) -> str:
    """
    生成Alpha表达式变体
    
    Args:
        region: 区域代码 (如 IND, USA, EUR)
        alpha_type: Alpha类型 (REGULAR 或 POWER_POOL)
        num_variants: 生成的变体数量
        strategy: 生成策略 (balanced, conservative, aggressive)
    """
    result = manager.generate_variants(region, alpha_type, num_variants, strategy)
    return json.dumps(result, indent=2, ensure_ascii=False)


@app.tool(name="field_library_optimize_alpha")
def optimize_alpha(
    original_expr: str,
    original_field: str
) -> str:
    """
    优化高相关性Alpha
    
    Args:
        original_expr: 原始Alpha表达式
        original_field: 原始字段名称
    """
    result = manager.optimize_alpha(original_expr, original_field)
    return json.dumps(result, indent=2, ensure_ascii=False)


@app.tool(name="field_library_analyze")
def analyze_expression(
    expression: str
) -> str:
    """
    分析表达式特征
    
    Args:
        expression: 要分析的Alpha表达式
    """
    result = manager.analyze_expression(expression)
    return json.dumps(result, indent=2, ensure_ascii=False)


@app.tool(name="field_library_search")
def search_fields(
    dataset: Optional[str] = None,
    data_type: Optional[str] = None,
    max_risk: str = "MEDIUM",
    min_success_rate: float = 0.0
) -> str:
    """
    高级字段搜索
    
    Args:
        dataset: 数据集名称 (如 Model, Analyst, Risk)
        data_type: 数据类型 (如 RANK, SCORE, VALUE)
        max_risk: 最大风险等级 (LOW, MEDIUM, HIGH)
        min_success_rate: 最低成功率 (0.0-1.0)
    """
    result = manager.search_fields(dataset, data_type, max_risk, min_success_rate)
    return json.dumps(result, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # 运行FastMCP应用，使用stdio传输，禁用横幅
    app.run(transport="stdio", show_banner=False)
