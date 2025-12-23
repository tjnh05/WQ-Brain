# Analyst Estimate Prediction Data (analyst82)

## 数据集描述
机器学习驱动的基本面信息预测数据集

## 主要特点
- **ML驱动**: 使用机器学习预测
- **基本面预测**: 预测关键基本面指标
- **前瞻性**: 提供未来预测
- **高精度**: ML模型提高预测准确度

## 主要字段
- 预测的基本面指标
- 预测置信度
- 模型特征重要性
- 历史预测准确性

## 使用场景
1. 基本面预测
2. 模型驱动策略
3. 预测准确性提升
4. 前瞻性分析

## 使用示例
```
# 使用ML预测数据
ml_prediction = analyst82_predicted_eps

# 预测置信度加权
confidence_weighted = analyst82_prediction * analyst82_confidence_score

# 与传统预测对比
ml_vs_traditional = analyst82_ml_estimate - analyst82_traditional_estimate
```

## 相关研究
- [Creating D0 Alphas with Model Data](https://support.worldquantbrain.com/hc/en-us/community/posts/18426141505431-Creating-D0-Alphas-with-Model-Data)
- [Getting started with Analyst Datasets](https://support.worldquantbrain.com/hc/en-us/community/posts/25238159368215-Getting-started-with-Analyst-Datasets)

## 数据集信息
- **区域**: USA
- **延迟**: 1
- **股票池**: TOP3000
- **覆盖率**: 0.7186
- **价值评分**: 2.0
- **用户数**: 566
- **Alpha数量**: 2,576
- **字段数**: 488