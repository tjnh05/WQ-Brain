# Getting started with Analyst Datasets

## 概述
Analyst 数据集提供结构化的数据字段，可视为分析师对各种基本面比率的情感评分。

## 核心技巧
- **时间序列操作**: 应用 ts_rank、zscore、rank 等操作
- **跨期比较**: 使用 ts_delta 比较不同时间点的分析师评分
- **组操作**: 使用 group_rank、group_neutralize、group_normalize、group_zscore
- **预测能力评估**: 通过数据字段与回报/收盘价的相关性评估预测潜力
- **收益变化检测**: 使用 ts_delta 检测 EPS 变化等盈利意外

## 注意事项
- 处理股票分割事件
- 使用 group_neutralize 降低组别暴露
- 国家和行业中性化通常效果良好

## Alpha 示例
1. 比较长期与短期预测差异，设置反转或动量信号
2. 基于预测值、delta(预测)或相关性(预测,回报)分配 Alpha
3. 在预测分散度高或不同时间跨度预测时分配 Alpha

## 推荐数据集
- Fundamental Analyst Estimates
- Analyst Estimate Daily Data
- ESG scores
- Broker Estimates
- Alternative Analyst Investment Insight Data