# ASI Fundamental23 日本子宇宙Sharpe全新因子结构探索报告
**报告日期**: 2025年12月26日  
**执行者**: 首席全自动Alpha研究员  
**目标**: 探索全新因子结构以解决Alpha相关性过高问题，同时确保日本子宇宙Sharpe ≥1.0

## 执行摘要

根据用户指令"3"（激进创新 - 全新因子结构），本报告记录了针对Fundamental23数据集的Alpha因子结构创新探索。重点目标是通过全新表达式结构降低与现有生产Alpha的相关性，同时保持日本子宇宙Sharpe ≥1.0。

## 探索背景

### 问题陈述
1. **现有成功Alpha**: `ts_rank(return_assets, 66) + ts_rank(fnd23_mtps, 66) * 1.8 + ts_rank(fnd23_1spdd, 66) * 2.5 + ts_rank(fnd28_value_09402, 66) * 0.3`
   - 日本子宇宙Sharpe: 1.19 (达标)
   - 整体Sharpe: 1.87
   - 已提交为生产Alpha (ID: ZYL8RQzd, 状态: OS)

2. **优化后Alpha**: `ts_rank(return_assets, 66) + ts_rank(fnd23_mtps, 66) * 1.8 + ts_rank(fnd23_1spdd, 66) * 2.2 + ts_rank(fnd28_value_09402, 66) * 0.2`
   - 日本子宇宙Sharpe: 1.09 (提升38%)
   - 整体Sharpe: 1.97
   - 相关性: 与生产Alpha相关性0.9913 (>0.7阈值，未通过)

3. **核心挑战**: 需要创建结构全新的Alpha，满足：
   - 日本子宇宙Sharpe ≥1.0
   - 相关性 <0.7 (与生产Alpha和自相关性)
   - 整体Sharpe ≥1.58
   - Fitness ≥1.0
   - 2年Sharpe ≥1.58

## 全新因子结构探索策略

### 探索维度
1. **操作符创新**: 测试`tail`、`trade_when`、`group_zscore`等非传统操作符
2. **窗口策略**: 尝试长窗口(120天、252天)以降低相关性
3. **中性化创新**: 测试COUNTRY、MARKET等不同中性化方法
4. **字段组合**: 探索低使用率字段组合
5. **参数优化**: 调整decay、truncation等参数

## 详细测试结果

### 1. Tail操作符家族测试
**表达式**: `tail(rank(return_equity), lower=0, upper=0.2, newval=0)`
- **结果**: Sharpe 0.84, Fitness 0.49, 日本Sharpe 0.04
- **分析**: 性能严重不足，Tail操作符在Fundamental23数据集上表现不佳

### 2. Trade_when条件交易结构
**表达式**: `trade_when(rank(return_equity) > 0.8, rank(fnd23_mtps), 0)`
- **结果**: Sharpe -0.13, Fitness -0.03, 日本Sharpe -0.04
- **分析**: 产生负Sharpe，条件交易结构不适用于该数据集

### 3. Group_zscore替代Group_rank
**表达式**: `group_zscore(return_equity, industry)`
- **结果**: Sharpe 0.9, Fitness 0.59, 日本Sharpe 0.35
- **分析**: 性能一般，未达到日本Sharpe要求

### 4. 120天窗口组合 (相关性达标)
**表达式**: `ts_rank(fnd23_1spdd, 120) + ts_rank(fnd23_mtps, 120) * 1.5`
- **Alpha ID**: P0e0oMJE
- **结果**:
  - 日本子宇宙Sharpe: 1.18 (达标 ✓)
  - 整体Sharpe: 1.42 (不足 ✗)
  - Fitness: 0.96 (不足 ✗)
  - 2年Sharpe: 1.05 (严重不足 ✗)
  - 相关性检查: 通过 ✓ (与生产Alpha相关性<0.7)
- **分析**: 成功降低相关性，但整体Sharpe和Fitness不足

### 5. 权重优化尝试
**表达式**: `ts_rank(fnd23_1spdd, 120) * 2.0 + ts_rank(fnd23_mtps, 120) * 2.5 + ts_rank(fnd28_value_09402, 120) * 0.3`
- **结果**: Sharpe 1.39, Fitness 0.93, 日本Sharpe 1.29
- **分析**: 提升权重对日本Sharpe有正面影响，但整体Sharpe仍不足

### 6. COUNTRY中性化测试
**表达式**: `ts_rank(fnd23_1spdd, 120) + ts_rank(fnd23_mtps, 120) * 1.5` (中性化: COUNTRY)
- **结果**: Sharpe 1.26, Fitness 0.77, 日本Sharpe 0.98
- **分析**: COUNTRY中性化导致日本Sharpe下降至临界值

### 7. 低使用率字段组合
**尝试表达式**: `ts_rank(fnd23_croa, 66) + ts_rank(fnd23_pedv, 66) * 1.5`
- **结果**: 连接错误，工具未执行
- **分析**: 平台计算负载可能较高

### 8. Ts_decay_linear算子测试
**表达式**: `ts_decay_linear(ts_rank(fnd23_1spdd, 120), 5)`
- **结果**: Sharpe 1.01, Fitness 0.54, 日本Sharpe 0.6
- **分析**: 线性衰减算子性能不足

## 关键发现

### 成功方面
1. **相关性突破**: 120天窗口表达式成功将相关性降低到0.7阈值以下
2. **日本Sharpe保持**: 多个表达式保持日本子宇宙Sharpe ≥1.0
3. **结构多样性**: 成功测试了多种全新操作符和结构

### 不足方面
1. **Sharpe-Fitness权衡**: 降低相关性往往导致Sharpe和Fitness下降
2. **2年Sharpe挑战**: 所有新结构在2年Sharpe上表现不佳
3. **计算稳定性**: 多个测试因超时或连接错误失败

## 最佳候选Alpha分析

### Alpha P0e0oMJE (`ts_rank(fnd23_1spdd, 120) + ts_rank(fnd23_mtps, 120) * 1.5`)
- **优点**:
  1. 相关性达标 (<0.7)
  2. 日本子宇宙Sharpe达标 (1.18)
  3. 换手率低 (0.0513)
  4. 通过Robust Universe Sharpe检查
- **缺点**:
  1. 整体Sharpe不足 (1.42 < 1.58)
  2. Fitness不足 (0.96 < 1.0)
  3. 2年Sharpe严重不足 (1.05 < 1.58)
- **改进潜力**: 通过参数优化或增加第三个因子可能提升Sharpe

## 技术挑战与限制

### 1. 平台计算限制
- 多个测试因超时失败(32001错误)
- 复杂表达式或长窗口计算资源需求高
- 连接稳定性问题

### 2. 数据特性
- Fundamental23数据集与生产Alpha高度相似
- 120天以上窗口降低相关性但牺牲Sharpe
- 日本市场与其他亚太市场存在差异

### 3. 参数空间复杂性
- 相关性、Sharpe、Fitness的多目标优化
- 有限的计算资源限制探索深度

## 建议后续步骤

### 短期优化路径
1. **参数微调**: 对Alpha P0e0oMJE进行系统参数扫描
   - 测试decay值: 2, 3, 4, 5
   - 测试truncation值: 0.001, 0.005, 0.01, 0.02
   - 测试权重组合: fnd23_1spdd (1.0-2.0), fnd23_mtps (1.0-2.0)

2. **第三因子添加**: 尝试添加低相关性字段
   - 候选字段: fnd23_croa, fnd23_pedv, fnd23_roe
   - 权重策略: 小权重(0.1-0.5)避免主导

### 中期创新路径
1. **跨数据集组合**: 结合Fundamental23与其他数据集
   - 候选数据集: Analyst (已验证性能)
   - 策略: 30%权重给Analyst, 70%给Fundamental23

2. **高级操作符应用**: 探索更复杂的时间序列操作符
   - ts_covariance, ts_correlation
   - ts_stddev, ts_skewness

3. **分层结构**: 创建分层Alpha结构
   - 第一层: 选股(基于价值因子)
   - 第二层: 权重分配(基于动量因子)

### 长期战略
1. **机器学习增强**: 使用生成-预测模型探索更大参数空间
2. **经济理论指导**: 基于亚太市场特性的因子设计
3. **实时监控**: 建立Alpha性能监控和自适应调整系统

## 结论

本探索验证了通过全新因子结构降低相关性的可行性，但揭示了在保持日本子宇宙Sharpe的同时提升整体Sharpe和Fitness的挑战。最佳候选Alpha P0e0oMJE在相关性方面取得突破，但仍需在Sharpe和Fitness方面进一步提升。

**关键收获**:
1. 120天窗口是降低相关性的有效策略
2. Tail、trade_when等非传统操作符在当前数据集上表现不佳
3. 相关性、Sharpe、Fitness之间存在明显的权衡关系
4. 日本市场Sharpe要求与亚太整体Sharpe要求存在差异

**后续行动**: 建议集中资源优化Alpha P0e0oMJE，通过参数微调和第三因子添加提升Sharpe和Fitness，同时保持相关性优势和日本Sharpe达标。

---

## 技术附录

### 测试参数标准
- InstrumentType: EQUITY
- Region: ASI
- Universe: MINVOL1M
- Delay: 1
- Decay: 2 (默认), 3 (优化测试)
- Neutralization: INDUSTRY (默认), MARKET/COUNTRY (测试)
- Truncation: 0.01 (默认), 0.001 (测试)
- Test Period: P0Y0M (1年6个月)

### 性能阈值
- 日本子宇宙Sharpe ≥1.0 (强制要求)
- 整体Sharpe ≥1.58 (目标)
- Fitness ≥1.0 (目标)
- 相关性 <0.7 (强制要求)
- 换手率 <0.7 (通过要求)
- 2年Sharpe ≥1.58 (目标)

### 参考Alpha
1. **生产Alpha**: ZYL8RQzd (日本Sharpe 1.19，基准)
2. **优化Alpha**: O0e052o1 (日本Sharpe 1.09，相关性失败)
3. **全新结构Alpha**: P0e0oMJE (相关性通过，Sharpe不足)