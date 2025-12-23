# Broker Estimates (analyst7)

## 数据集描述
该数据集包含汇总形式的分析师预测和实际基本面数据。

## 主要特点
- **汇总数据**: 分析师预测和实际值的聚合
- **覆盖广泛**: 全球公司数据
- **定期更新**: 跟随财报周期
- **历史数据**: 提供历史对比

## 主要字段
- 分析师预测值
- 实际公布值
- 预测偏差
- 修正历史
- 汇总统计

## 使用场景
1. 预测准确性分析
2. 市场预期管理
3. 基本面因子构建
4. 趋势分析

## 使用示例
```
# 预测偏差
estimate_error = analyst7_actual - analyst7_estimate

# 预测修正趋势
estimate_revision = analyst7_estimate - ts_mean(analyst7_estimate, 20)

# 预测准确性
accuracy_score = -abs(estimate_error) / analyst7_estimate
```

## 相关研究
- [Getting started with Analyst Datasets](https://support.worldquantbrain.com/hc/en-us/community/posts/25238159368215-Getting-started-with-Analyst-Datasets)
- [Research Paper: Investor Learning, Earnings Signals, and Stock Returns](https://support.worldquantbrain.com/hc/en-us/community/posts/13801504994455-Research-Paper-Investor-Learning-Earnings-Signals-and-Stock-Returns)

## 数据集信息
- **区域**: USA
- **延迟**: 1
- **股票池**: TOP3000
- **覆盖率**: 0.5
- **价值评分**: 1.0
- **用户数**: 1,747
- **Alpha数量**: 73,767
- **字段数**: 1,317