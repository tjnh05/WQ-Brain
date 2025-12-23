# Smart Conference Call Transcript Data (analyst83)

## 数据集描述
该数据集提供公司事件和宏观经济事件的全面覆盖，包括盈利发布、电话会议、IPO、SEC文件和经济指标。它包括详细的事件元数据、逐字稿、分析师简报和支持材料，如演示文稿和录音。数据使用RIC、CUSIP、SEDOL和ISIN等标识符进行结构化，并频繁更新当前和历史记录。通过跟踪关键公司事件和宏观经济公告的时间、内容和情感，该数据集使投资者和分析师能够预测市场驱动新闻、评估管理层语调和指导，并识别可能影响股票价格和市场波动的催化剂。

## 主要特点
- **全面事件覆盖**: 盈利、电话会议、IPO、SEC文件
- **详细元数据**: 事件状态、时间、参与者
- **逐字稿**: 完整的文字记录
- **情感分析**: 管理层语调和指导
- **多标识符**: RIC、CUSIP、SEDOL、ISIN

## 主要字段
- 事件元数据
- 逐字稿内容
- 分析师简报
- 演示文稿
- 音频记录链接
- 情感评分

## 使用场景
1. 事件驱动策略
2. 情感分析
3. 管理层语调分析
4. 催化剂识别

## 使用示例
```
# 电话会议情感分析
sentiment_score = analyst83_conference_call_sentiment

# 管理层指导变化
guidance_change = analyst83_guidance_revision

# 事件驱动交易
earnings_event = analyst83_is_earnings_call
event_alpha = sentiment_score * earnings_event
```

## 相关研究
- [Getting started with Analyst Datasets](https://support.worldquantbrain.com/hc/en-us/community/posts/25238159368215-Getting-started-with-Analyst-Datasets)

## 数据集信息
- **区域**: USA
- **延迟**: 1
- **股票池**: TOP3000
- **覆盖率**: 0.5299
- **价值评分**: 3.0
- **用户数**: 209
- **Alpha数量**: 513
- **字段数**: 383