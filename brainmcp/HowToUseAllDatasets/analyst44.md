# Integrated Broker Estimates (analyst44)

## 数据集描述
WQ SmartData是一个中间数据平台，提供增值的、嵌入想法的数据管理器和财务及事件数据集的分析。它包括高级处理，如事件分类（例如，并购、盈利）、组聚类、文本数据的自然语言处理（例如，EDGAR文件、新闻情感）和图/网络分析。通过整合和转换来自FactSet、RavenPack和EDGAR等来源的原始数据，它使研究人员能够提取难以从原始数据流中获得的特征、信号和事件驱动alpha，支持创新的量化策略并提高价格变动模型的预测能力。

## 主要特点
- **智能数据**: 增值的、嵌入想法的数据
- **事件分类**: M&A、盈利等事件自动分类
- **NLP处理**: EDGAR文件、新闻情感分析
- **图分析**: 网络关系分析
- **多源整合**: FactSet、RavenPack、EDGAR

## 主要字段
- 事件分类结果
- 组聚类信息
- NLP情感评分
- 网络分析指标
- 处理后的特征

## 使用场景
1. 事件驱动策略
2. 情感分析
3. 网络效应
4. 创新量化策略

## 使用示例
```
# 事件分类信号
m_a_signal = analyst44_is_m_a_event
earnings_signal = analyst44_is_earnings_event

# NLP情感分析
sentiment_alpha = analyst44_news_sentiment

# 网络分析
network_centrality = analyst44_network_centrality_score
```

## 相关研究
- [Getting started with Analyst Datasets](https://support.worldquantbrain.com/hc/en-us/community/posts/25238159368215-Getting-started-with-Analyst-Datasets)
- [Research Paper: Non-GAAP Earnings and the Earnings Quality Trade-off](https://support.worldquantbrain.com/hc/en-us/community/posts/14760799705879-Research-Paper-Non-GAAP-Earnings-and-the-Earnings-Quality-Trade-off)

## 数据集信息
- **区域**: USA
- **延迟**: 1
- **股票池**: TOP3000
- **覆盖率**: 0.7743
- **价值评分**: 3.0
- **用户数**: 724
- **Alpha数量**: 6,860
- **字段数**: 797