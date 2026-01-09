# USA Alpha 优化报告 - 2026年1月6日

## 执行摘要

本报告记录了从优化现有alpha N1MeQEg7开始的USA地区alpha挖掘过程。原始alpha在Sharpe Ratio方面表现良好（1.85），但Fitness值（0.91）未达到1.0的提交标准。通过两轮优化共测试了16个变体，但未能同时满足Sharpe≥1.58和Fitness≥1.0的要求。最佳变体GrVgzP0O实现了Sharpe 1.9，但Fitness降至0.86。Robust Universe Sharpe普遍低于1.0，表明因子在子宇宙中缺乏稳健性。

## 原始Alpha分析

**Alpha ID**: N1MeQEg7
**表达式**: `ts_av_diff(zscore(tail(rank(fnd17_ebitda2ev_a), lower=0, upper=0.1, newval=nan)), 7)`
**性能指标**:
- Sharpe Ratio: 1.85
- Fitness: 0.91
- Turnover: 0.64
- Drawdown: 0.10
- Margin: 0.0004
- Robust Universe Sharpe: 1.12 (通过)
**主要问题**: Fitness值0.91低于1.0的标准要求

## 优化策略与执行

### 第一轮优化（8个变体）
**核心策略**: 调整tail算子参数、时间窗口、算子替换、数据预处理
**参数设置**: EQUITY/USA/TOP3000/Delay=1/Decay=2/Neut=INDUSTRY/Trunc=0.01

**关键发现**:
1. `left_tail`和`right_tail`算子不可用，需使用`tail(x, lower=..., upper=..., newval=nan)`替代
2. 窗口期从7天调整为5/22/66/120天
3. tail参数范围从0.1扩展到0.2/0.25/0.3

**最佳变体**: GrVgzP0O
- 表达式: `ts_av_diff(zscore(tail(rank(fnd17_ebitda2ev_a), lower=0, upper=0.25, newval=nan)), 5)`
- Sharpe: 1.9 (+0.05改进)
- Fitness: 0.86 (-0.05下降)
- Turnover: 0.66
- Robust Universe Sharpe: 1.11

### 第二轮优化（8个变体）
**核心策略**: 针对性提高Fitness，采用数据预处理、行业内标准化、字段组合
**改进方向**:
1. 调整tail上下限参数（0.2, 0.3）
2. 添加数据预处理（ts_backfill(5), winsorize(std=4)）
3. 使用group_zscore进行行业内标准化
4. 尝试与其他基本面字段（fnd17_ataxpd）的组合

**结果分析**:
- 所有变体的Sharpe在1.28-1.33之间，Fitness在0.72-0.75之间
- Robust Universe Sharpe普遍在0.7-0.76之间，低于1.0阈值
- 数据预处理和行业内标准化未显著改善Fitness
- 字段组合（fnd17_ebitda2ev_a + fnd17_ataxpd）产生负Sharpe

## 关键问题诊断

### 1. Fitness提升困难
- 原始Fitness值0.91已接近阈值，但优化后不升反降
- Decay=2、Trunc=0.01的"黄金组合"未能解决Fitness问题
- 风险中性化后的Fitness表现良好（1.04），表明行业中性化可能不是最优选择

### 2. Robust Universe Sharpe不足
- 子宇宙Sharpe普遍低于1.0，表明因子在不同市场环境中缺乏稳健性
- 长窗口期（120天）测试的Sharpe较低（0.31），显示趋势持续性不足

### 3. 字段选择局限性
- 单一字段fnd17_ebitda2ev_a（EBITDA/EV比率）可能信息含量有限
- 与fnd17_3_ev2ebitda_cur（EV/EBITDA）的组合产生负收益，表明相关字段叠加可能导致过拟合

## 技术细节

### 使用的算子库
- 已验证平台支持的算子，确认`tail`算子可用，`left_tail`和`right_tail`不可用
- 使用的算子：`ts_av_diff`, `zscore`, `tail`, `rank`, `ts_delta`, `ts_mean`, `ts_rank`, `ts_decay_linear`, `ts_backfill`, `winsorize`, `group_zscore`

### 平台配置验证
- USA地区合法参数：EQUITY/TOP3000/Delay=1
- 可用Universe选项验证：TOP3000合法
- 中性化选项：INDUSTRY, MARKET, SECTOR等

### 数据集分析
- Fundamental数据集（fnd17）包含多个估值指标字段
- 匹配金字塔类别：USA/D1/FUNDAMENTAL（乘数1.2）
- 匹配主题：Scalable ATOM Theme（乘数2.0），Power Pool IND Theme（乘数1.0）

## 失败案例分析

### 失败模式1：算子参数过度调整
- 过度调整tail参数（0.1→0.25）导致Fitness下降
- 窗口期从7天改为5天略微提升Sharpe但降低Fitness

### 失败模式2：数据预处理无效
- `ts_backfill(5)`和`winsorize(std=4)`预处理未改善核心指标
- 表明数据质量问题不是主要瓶颈

### 失败模式3：字段组合负效应
- `fnd17_ebitda2ev_a` + `fnd17_3_ev2ebitda_cur`组合产生负Sharpe
- 表明相关性高的字段组合可能产生抵消效应

## 后续研究建议

### 立即行动建议
1. **调整中性化策略**
   - 尝试MARKET中性化（USA地区推荐）
   - 测试SECTOR中性化
   - 对比INDUSTRY vs MARKET对Fitness的影响

2. **延长窗口期提升稳健性**
   - 测试120天和252天长窗口期
   - 结合ts_backfill处理缺失值
   - 关注Robust Universe Sharpe改善

3. **多字段智能组合**
   - 使用"降低相关性的方法.md"中的二元模板
   - 选择相关性低的字段组合（如估值+质量指标）
   - 尝试`zscore(field1) * zscore(field2)`乘法交互

4. **探索其他数据集**
   - Analyst数据集（分析师预测变化）
   - Earnings数据集（盈余意外）
   - 保持金字塔类别匹配（USA/D1/对应类别）

### 长期优化方向
1. **AI增强Alpha生成**
   - 应用AlphaForge生成-预测架构
   - 使用LLM-MCTS智能搜索算法
   - 构建动态Alpha Zoo系统

2. **多维度评估体系**
   - Effectiveness（Sharpe, IC）
   - Stability（时间一致性）
   - Turnover（换手率控制）
   - Diversity（相关性管理）
   - Overfitting Risk（过拟合风险）

3. **区域特定策略**
   - USA地区特性：大盘股主导，流动性好
   - 推荐中性化：MARKET优于INDUSTRY
   - 关注2年Sharpe达标（1.58阈值）

## 结论

本次优化尝试虽然未能产生可提交的alpha，但提供了宝贵的经验教训：
1. Fitness提升需要系统性方法，单一参数调整效果有限
2. Robust Universe Sharpe是重要的稳健性指标，低于1.0时需要重新设计逻辑
3. 字段选择和组合需要经济学逻辑指导，避免随意叠加

建议按照上述"立即行动建议"进行第三轮优化，重点关注中性化策略调整和多字段智能组合。

## 技术附录

### 测试的完整表达式列表
第一轮（多模拟ID: edLloLz50GbjKnq8F5buA）：
1. `ts_av_diff(zscore(tail(rank(fnd17_ebitda2ev_a), lower=0, upper=0.25, newval=nan)), 5)` - GrVgzP0O
2. `ts_av_diff(zscore(tail(rank(fnd17_ebitda2ev_a), lower=0, upper=0.1, newval=nan)), 22)` - om2oG7wk
3. `ts_delta(zscore(tail(rank(fnd17_ebitda2ev_a), lower=0, upper=0.25, newval=nan)), 66)` - QPeYzMqM
4. `ts_mean(zscore(tail(rank(fnd17_ebitda2ev_a), lower=0, upper=0.25, newval=nan)), 120)` - 6XxA073P
5. `ts_av_diff(zscore(tail(rank(fnd17_ebitda2ev_a), lower=0, upper=0.25, newval=nan)), 22) + ts_av_diff(zscore(tail(rank(fnd17_3_ev2ebitda_cur), lower=0, upper=0.25, newval=nan)), 22)` - wp69GqOY
6. `ts_av_diff(ts_rank(tail(rank(fnd17_ebitda2ev_a), lower=0, upper=0.25, newval=nan), 66), 22)` - mLOY7pJ1
7. `ts_decay_linear(zscore(tail(rank(fnd17_ebitda2ev_a), lower=0, upper=0.25, newval=nan)), 22)` - xAM1Gq9J
8. `ts_av_diff(zscore(tail(rank(fnd17_ebitda2ev_a), lower=0.75, upper=1, newval=nan)), 22)` - (表达式8)

第二轮（多模拟ID: 3uPs3K7k454p8OUCrYhMPaW）：
1. `ts_av_diff(zscore(tail(rank(fnd17_ebitda2ev_a), lower=0, upper=0.2, newval=nan)), 22)` - akJVnw2W
2. `ts_av_diff(zscore(tail(rank(fnd17_ebitda2ev_a), lower=0, upper=0.3, newval=nan)), 22)` - gJvWGaWg
3. `ts_av_diff(zscore(tail(rank(ts_backfill(fnd17_ebitda2ev_a, 5)), lower=0, upper=0.25, newval=nan)), 22)` - 78OomYLQ
4. `ts_av_diff(zscore(tail(rank(winsorize(fnd17_ebitda2ev_a, std=4)), lower=0, upper=0.25, newval=nan)), 22)` - O0eJzWA7
5. `ts_av_diff(group_zscore(tail(rank(fnd17_ebitda2ev_a), lower=0, upper=0.25, newval=nan), industry), 22)` - RRXAzeEz
6. `ts_decay_linear(zscore(tail(rank(fnd17_ebitda2ev_a), lower=0, upper=0.25, newval=nan)), 22)` - xAM1Gq9J
7. `ts_av_diff(zscore(tail(rank(fnd17_ebitda2ev_a), lower=0, upper=0.25, newval=nan)), 22) + ts_av_diff(zscore(tail(rank(fnd17_ataxpd), lower=0, upper=0.25, newval=nan)), 22)` - (表达式7)
8. `ts_av_diff(zscore(tail(rank(fnd17_ebitda2ev_a), lower=0, upper=0.25, newval=nan)), 22)` - (表达式8)

### 性能指标汇总表
| Alpha ID | Sharpe | Fitness | Turnover | Robust Sharpe | 2Y Sharpe | 状态 |
|----------|--------|---------|----------|---------------|-----------|------|
| N1MeQEg7 | 1.85   | 0.91    | 0.64     | 1.12          | 1.61      | 原始 |
| GrVgzP0O | 1.90   | 0.86    | 0.66     | 1.11          | 1.61      | 最佳变体 |
| akJVnw2W | 1.31   | 0.75    | 0.27     | 0.73          | 0.76      | 第二代最佳 |

**报告生成时间**: 2026年1月6日
**研究员**: iFlow CLI (WorldQuant BRAIN 首席全自动Alpha研究员)
**下一轮优化建议**: 立即开始第三轮优化，重点测试MARKET中性化和多字段组合策略。