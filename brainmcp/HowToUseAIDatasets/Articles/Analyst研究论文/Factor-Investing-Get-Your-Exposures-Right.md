# Factor Investing: Get Your Exposures Right!

## 摘要
本文致力于股票因子投资的最优组合构建问题。第一部分关注如何确保给定的股票投资组合具有目标因子暴露，甚至在施加任何约束之前。

## 关键发现
- 基于因子信息以稳健方式构建的股票预期回报可以用于均值-方差优化
- 这种方法在应用现实约束(如仅多头)前后都能保持目标因子暴露
- 其他更简单的方法无法达到这一效果

## 实际应用
1. 以务实方式决定因子的风险预算分配
2. 构建仅多头约束投资组合，保持对知名资产定价股票模型四个因子的目标暴露：
   - High-minus-Low (HML)
   - Robust-minus-Weak (RMW)
   - Conservative-minus-Aggressive (CMA)
   - Momentum (MOM)

## 核心观点
- 第3页第1段
- 第23页第2段

## BRAIN有用数据字段

| 术语 | 数据字段 | 数据集 |
|------|----------|--------|
| 均值-方差优化 | mdl175_variance120 | Model175 |
| 波动率 | mdl175_realizedvolatility | Model175 |
| 股票回报 | anl14_high_roa_fp1 | Analyst14 |
| 因子回报 | mdl175_revs10 | Model175 |

## 作者
François Soupé, Xiao Lu, Raul Leote de Carvalho

## 发表年份
2018

## 论文链接
https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3276006