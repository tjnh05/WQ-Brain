# Getting started with Earnings Datasets

## 概述
Earnings 数据类别提供公司表现和市场预期信息，包括分析师预测与实际盈利对比、财务报告时间和公司事件时间表。

## 核心技巧
- **数据回填**: 使用 ts_backfill() 处理不同公司不规律的报告日期
- **盈利意外**: 报告盈利高于分析师预测的公司通常会看到股价上涨
- **盈利公告后漂移(PEAD)**: 对高标准化意外盈利和正面盈利公告回报的股票做多
- **过度反应**: 公司宣布令人失望的盈利后，股价下跌有时可能是过度反应

## Alpha 示例
1. 买入报告盈利高于分析师预测的公司股票
2. 利用 PEAD 效应，对高标准化意外盈利和正面盈利公告回报的股票做多
3. 识别宣布令人失望盈利后股价过度下跌的公司，等待反弹

## 推荐数据集
- Actuals and Estimates Earnings Data
- Earnings Date Data
- Effect of earnings announcement model
- Earnings Date Breaks
- Horizon Earnings and Calendar North America

## 关键概念
- **每股收益(EPS)**: 公司盈利能力的关键指标
- **盈利增长**: 跟踪一段时间内的盈利增长
- **盈利意外**: 实际盈利与分析师预期的差异
- **盈利时机**: 盈利报告预定发布日期