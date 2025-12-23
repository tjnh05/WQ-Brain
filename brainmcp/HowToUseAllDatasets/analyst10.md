# Performance-Weighted Analyst Estimates (analyst10)

## 数据集描述
提供"智能预测"，即机构分析师财务预测的智能加权平均值。基于分析师历史表现得分和预测时效性进行加权。

## 主要特点
- **智能加权**: 基于历史表现和时效性
- **表现驱动**: 优秀分析师权重更高
- **时效性考虑**: 近期预测权重更大
- **共识优化**: 更准确的预测共识

## 主要字段
- 智能预测值
- 分析师权重
- 历史表现得分
- 时效性权重
- 优化共识值

## 使用场景
1. 提高预测准确性
2. 识别优秀分析师
3. 时效性分析
4. 预期管理

## 使用示例
```
# 智能预测与标准预测差异
smart_vs_standard = analyst10_smart_estimate - analyst10_standard_estimate

# 分析师权重影响
weight_impact = analyst10_analyst_weight * analyst10_estimate_accuracy

# 时效性效应
recency_effect = analyst10_recency_weight * analyst10_estimate_change
```

## 数据集信息
- **区域**: USA
- **延迟**: 1
- **股票池**: TOP3000
- **覆盖率**: 0.8405
- **价值评分**: 3.0
- **用户数**: 588
- **Alpha数量**: 1,738
- **字段数**: 1,074