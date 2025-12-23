# Real Time Estimates (analyst16)

## 数据集描述
提供对行业标准预测的实时访问，包括SmartEstimate和预测惊喜。能够在市场对新闻定价之前行动和交易。

## 主要特点
- **实时访问**: 行业标准预测
- **SmartEstimate**: 智能预测模型
- **预测惊喜**: 超预期的预测
- **抢先交易**: 在市场反应前行动

## 主要字段
- 实时预测数据
- SmartEstimate值
- 预测惊喜指标
- 行业标准预测
- 实际值对比

## 使用场景
1. D0策略（当日交易）
2. 盈利惊喜交易
3. 实时事件响应
4. 超前市场反应

## 使用示例
```
# SmartEstimate与标准预测差异
smart_vs_consensus = analyst16_smart_estimate - analyst16_consensus_estimate

# 预测惊喜策略
earnings_surprise = analyst16_actual - analyst16_predicted
surprise_signal = rank(earnings_surprise) * ts_mean(volume, 20)

# 实时交易信号
real_time_alpha = ts_rank(analyst16_smart_estimate_change, 5)
```

## 数据集信息
- **区域**: USA
- **延迟**: 1
- **股票池**: TOP3000
- **覆盖率**: 0.8252
- **价值评分**: 2.0
- **用户数**: 1,039
- **Alpha数量**: 8,725
- **字段数**: 107