# ASI地区Alpha挖掘策略报告
## 生成日期：2025年12月25日

## 执行摘要
基于对ASI地区的深入分析，本报告制定了系统的Alpha因子挖掘策略。ASI地区具有以下特点：
- **Region**: ASI
- **Delay**: 1 (仅D1可用)
- **Universe**: MINVOL1M, ILLIQUID_MINVOL1M
- **Neutralization**: 支持多种中性化选项，特别是SLOW中性化在ASI地区效果显著

## 市场特性分析
根据论坛信息，ASI地区具有以下特点：
1. **SLOW中性化优势**：使用SLOW中性化在ASI地区效果很好，出货率高
2. **RISK数据集表现优异**：RISK数据集在ASI地区出货率很高，特别是多因子模型数据集
3. **竞争相对较少**：使用SLOW中性化的顾问相对较少，提供了较好的机会窗口

## 数据集优先级排序
基于分析，推荐以下数据集优先级：

### 第一优先级：RISK数据集
- **risk70** (Multi-Factor Model)：多因子模型，包含32个字段，覆盖全面
- **risk72** (Specific return of extended factors)：扩展因子特定收益
- **risk60** (Securities Lending Insight Data)：证券借贷洞察数据

### 第二优先级：Analyst数据集
- **analyst15** (Earnings forecasts)：盈利预测，覆盖率高(99.51%)
- **analyst69** (Fundamental Analyst Estimates)：基本面分析师预测
- **analyst4** (Analyst Estimate Data for Equity)：分析师估计数据

### 第三优先级：Fundamental数据集
- **fundamental23** (Fundamental Point in Time Data)：时点基本面数据
- **fundamental28** (Global Fundamental Data)：全球基本面数据
- **fundamental17** (Direct Fundamental Data)：直接基本面数据

## Alpha表达式模板库
基于论坛成功经验，推荐以下模板：

### 基础模板（8个变体）
1. `'factor'`
2. `rank('factor')`
3. `rank(ts_delta('factor', 7))`
4. `rank(ts_delta('factor', 30))`
5. `rank(ts_delta('factor', 90))`
6. `rank(ts_regression(ts_zscore('factor', 7), ts_step(1), 7, rettype=2))`
7. `rank(ts_regression(ts_zscore('factor', 30), ts_step(1), 30, rettype=2))`
8. `rank(ts_regression(ts_zscore('factor', 90), ts_step(1), 90, rettype=2))`

### RISK70数据集特定字段推荐
从risk70数据集中选择以下高潜力字段：

1. **分析师情绪类**：
   - `rsk70_mfm2_asetrd_anlystsn` (Analysts' Sentiment Style Factor Loading)
   - 使用率：1580用户，12874个Alpha

2. **动量反转类**：
   - `rsk70_mfm2_asetrd_momentum` (Momentum Style Factor Loading)
   - `rsk70_mfm2_asetrd_ltrevrsl` (Long-Term Reversal Style Factor Loading)
   - `rsk70_mfm2_asetrd_strevrsl` (Short-Term Reversal Style Factor Loading)

3. **价值收益类**：
   - `rsk70_mfm2_asetrd_earnyild` (Earnings Yield Style Factor Loading)
   - `rsk70_mfm2_asetrd_divyild` (Dividend Yield Style Factor Loading)
   - `rsk70_mfm2_asetrd_btop` (Book-to-Price Style Factor Loading)

4. **质量风险类**：
   - `rsk70_mfm2_asetrd_profit` (Profit Style Factor Loading)
   - `rsk70_mfm2_asetrd_earnqlty` (Earnings Quality Style Factor Loading)
   - `rsk70_mfm2_asetrd_dsrt` (Specific returns)

## 模拟参数配置
### 基础配置
- **Instrument Type**: EQUITY
- **Region**: ASI
- **Universe**: MINVOL1M
- **Delay**: 1
- **Neutralization**: SLOW (优先推荐)
- **Decay**: 2 (黄金组合)
- **Truncation**: 0.001 (黄金组合)
- **Test Period**: P0Y0M (1年6个月)
- **Unit Handling**: VERIFY
- **Nan Handling**: OFF
- **Language**: FASTEXPR
- **Visualization**: true
- **Pasteurization**: ON
- **Max Trade**: OFF

### 备选中性化策略
如果SLOW中性化效果不佳，可尝试：
1. **INDUSTRY**：行业中性化
2. **MARKET**：市场中性化  
3. **SECTOR**：板块中性化
4. **COUNTRY**：国家中性化（ASI地区支持）

## 执行工作流
### Phase 1: 批量测试（8个表达式）
使用多模拟工具创建8个不同字段的Alpha表达式进行初步筛选。

### Phase 2: 深度优化
对表现良好的Alpha进行：
1. **参数调优**：调整decay(0-5)、truncation(0.001-0.01)
2. **中性化优化**：尝试不同的中性化组合
3. **时间窗口优化**：调整ts_delta和ts_regression的窗口期

### Phase 3: 相关性检查
对所有通过初步测试的Alpha进行：
1. **生产相关性检查** (PC < 0.7)
2. **自相关性检查** (SC < 0.7)
3. **多样性检查**：确保与现有Alpha库的相关性<0.6

### Phase 4: 提交前验证
1. **性能指标验证**：
   - Sharpe > 1.58
   - Fitness > 1.0
   - Turnover < 70%
   - Diversity > 0.3
   - Robust Universe Sharpe > 1.0
   - 2Y Sharpe > 1.58 (如有)

2. **提交检查**：调用get_submission_check确保通过

## 风险管理
1. **及时止损**：如果Robust Sharpe < 0.5，直接停止调试
2. **相关性控制**：确保PC和SC都低于0.7
3. **多样性维护**：避免过度集中在单一数据集或逻辑
4. **性能监控**：定期检查Alpha的OS表现

## 预期成果
基于论坛经验，使用此策略预期：
1. **每日提交量**：每个数据集每天可提交3个Alpha
2. **成功率**：相关性小于0.6的Alpha提交成功率高
3. **多样性**：可在不同数据集间轮换，避免被ban

## 后续优化方向
1. **AI增强**：应用AlphaForge和LLM-MCTS技术
2. **模板工程**：开发更复杂的多字段组合模板
3. **跨区域测试**：将成功的ASI Alpha应用到其他区域
4. **动态权重**：基于时效性调整因子权重

---
**备注**：本策略基于2025年12月25日的市场分析和论坛信息。实际执行时需根据网络连接状态和平台响应进行调整。