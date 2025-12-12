# Alpha Research Report - USA D0 Pre-Tax Predicted Surprise

**Date**: 2025-12-12  
**Researcher**: Autonomous Alpha Engine  
**Target**: USA D0 / Analyst Category

---

## Executive Summary

**Research Status**: ❌ **Failed - Signal Quality Insufficient**

Attempted to develop D0 Alpha using **analyst10 dataset's Pre-Tax Predicted Surprise fields** targeting USA Delay-0 Analyst pyramid (currently empty). Despite rigorous testing through incremental complexity methodology, **all variants failed to meet minimum submission thresholds**.

**Root Cause**: D0 analyst predicted surprise signals exhibit extremely weak predictive power and high instability when operating without historical lookback periods.

---

## Phase 1: Intelligence Gathering

### Pyramid Analysis
**Target Identified**: 
- `USA/D0/ANALYST` - **0 alphas** (Priority target for diversity bonus: 1.8x multiplier)
- All USA D0 categories (PV, Fundamental, News, etc.) show **0 alphas**
- D1 has substantial activity (18 PV alphas, 12 Analyst alphas)

### Dataset Selection
**Chosen**: `analyst10` - Performance-Weighted Analyst Estimates
- **Coverage**: Full (1.0 for most fields)
- **Fields Tested**: 
  - `anl10_prefy1_pred_surps_v1_1108` (FY1 predicted surprise v1)
  - `anl10_prefy1_pred_surps_v0_1082` (FY1 predicted surprise v0)
  - `anl10_prefq1_pred_surps_v0_1116` (Q1 predicted surprise v0)
  - `anl10_prefq1_pred_surps_v1_1121` (Q1 predicted surprise v1)
  - `anl10_prefq2_pred_surps_v1_1102` (Q2 predicted surprise v1)

**Economic Rationale**: Analyst predicted surprises theoretically capture market expectation mismatches, which should drive short-term price movements in D0 setting.

---

## Phase 2: 0-Op Baseline Testing (Raw Signal Probe)

### Methodology
Submitted **8 expressions** using strict 0-op rule:
```python
rank(anl10_prefy1_pred_surps_v1_1108)
rank(anl10_prefy1_pred_surps_v0_1082)
rank(anl10_prefq1_pred_surps_v0_1116)
rank(anl10_prefq1_pred_surps_v1_1121)
rank(anl10_prefq2_pred_surps_v1_1102)
rank(anl10_prefy1_pred_surps_v2_1088)
rank(anl10_prefq1_pred_surps_v2_1093)
rank(anl10_prefq2_pred_surps_v0_1107)
```

### Settings
- **Region**: USA
- **Delay**: 0
- **Decay**: 0 (no smoothing)
- **Neutralization**: NONE
- **Truncation**: 0.08

### Results Summary
| Alpha ID | Expression | Sharpe | Fitness | Turnover | Returns |
|----------|-----------|--------|---------|----------|---------|
| kq5dp5qd | rank(prefq1_v1) | **0.73** | **1.11** | 0.0538 | 0.2867 |
| LLxWoxL1 | rank(prefq2_v1) | **0.72** | **1.09** | 0.0883 | 0.2861 |
| WjmMrmjx | rank(prefy1_v1) | **0.74** | **1.12** | 0.0444 | 0.2838 |
| npb9GbxM | rank(prefy1_v0) | **0.74** | **1.12** | 0.0441 | 0.2838 |
| vRV87Vwd | rank(prefy1_v2) | **0.72** | **1.07** | 0.0466 | 0.2777 |

**Critical Finding**: All variants failed:
- ❌ **LOW_SHARPE** (Required: 2.69, Achieved: 0.72-0.74)
- ❌ **LOW_FITNESS** (Required: 1.5, Achieved: 1.07-1.13)
- ⚠️ **LOW_2Y_SHARPE** (-0.13 to -0.08) - Recent performance degradation

### Diagnostic Observations
1. **Turnover**: Acceptable (0.04-0.09) - not the problem
2. **Coverage**: Good (longCount ~2650-2871) - sufficient liquidity
3. **Drawdown**: Extremely high (0.73-0.76) - signal reverses frequently
4. **Investability**: Sharpe collapses to **-0.09 to -0.14** under constraints - signal does not survive real-world friction

---

## Phase 3: 1-Op Enhancement Attempt

### Strategy
Applied standard enhancement techniques per `How to improve Sharpe.md`:
1. **Smoothing**: `ts_mean(field, 5)` and `ts_decay_linear(rank(field), 22)`
2. **Grouping**: `group_rank(field, subindustry)` for cross-sectional normalization
3. **Neutralization**: INDUSTRY (to reduce systematic risk)
4. **Parameter Tuning**: Decay=2, Truncation=0.01 (golden combo)

### Expressions Tested
```python
ts_decay_linear(rank(anl10_prefy1_pred_surps_v1_1108), 22)
rank(ts_mean(anl10_prefy1_pred_surps_v1_1108, 5))
rank(group_rank(anl10_prefy1_pred_surps_v1_1108, subindustry))
# ... (8 total variants)
```

### Settings
- **Decay**: 2
- **Neutralization**: INDUSTRY
- **Truncation**: 0.01

### Results Summary
| Alpha ID | Expression | Sharpe | Fitness | Status |
|----------|-----------|--------|---------|--------|
| 78VWPeb1 | ts_decay_linear(..., 22) | **0.26** | **0.06** | ❌ Worse |
| d5wpJNVJ | rank(ts_mean(..., 5)) | **0.31** | **0.08** | ❌ Worse |
| 88qbWMdq | rank(group_rank(...)) | **0.41** | **0.11** | ❌ Worse |
| gJz6Nnpv | rank(ts_mean(prefq1...)) | **0.10** | **0.01** | ❌ Catastrophic |

**Result**: **DETERIORATION INSTEAD OF IMPROVEMENT**
- Sharpe **dropped** from 0.7x → 0.1-0.4x
- Fitness **dropped** from 1.1x → 0.01-0.11x
- Industry neutralization **removed** the only weak signal present

---

## Root Cause Analysis

### Why Did This Fail?

#### 1. **D0 Constraint Incompatibility**
- Analyst predicted surprise updates are **discrete events** (quarterly/annual earnings)
- D0 (no historical lookback) means we're trading **instantaneously** on raw surprise values
- The signal has no "memory" to establish momentum or mean-reversion patterns
- Real predictive power likely requires **event study windows** (D1+ with `ts_delta`, `ts_rank` over 5-22 days)

#### 2. **Signal Noise Dominance**
- Drawdown 0.73-0.76 indicates signal flips direction frequently
- Predicted surprise values are **model outputs**, not actual realized surprises
- Model prediction errors become our signal errors - double jeopardy
- D0 amplifies this: no time for information to propagate/stabilize

#### 3. **Economic Logic Breakdown**
- **Hypothesis**: "Smart estimates deviate from consensus → price adjusts → profit"
- **Reality in D0**: Market may already have priced the deviation before we can act
- **Confirmation**: Investability-constrained Sharpe goes **negative** (-0.09 to -0.14)
- Trading costs + implementation lag > signal edge

#### 4. **Data Type Mismatch**
- Analyst data updates are **sparse** (not daily)
- D0 requires **dense, high-frequency** signals (like intraday price/volume patterns)
- Using quarterly fundamental predictions in daily D0 context creates temporal mismatch

---

## Lessons Learned

### 1. **D0 Selection Criteria**
For USA D0 to work, signals must have:
- ✅ **High-frequency updates** (daily or intraday)
- ✅ **Low autocorrelation** (independent daily info)
- ✅ **Survives transaction costs** (>2% daily edge required)
- ❌ **Analyst data fails all three** in D0 context

### 2. **Strict Incremental Testing Saved Time**
- 0-op test revealed fundamental weakness **immediately**
- Avoided weeks of complex logic development on flawed foundation
- Confirmed: "If 0-op fails badly, 2-op won't save it"

### 3. **Platform Wisdom: "Not All Data Fits All Delays"**
- Analyst data **excels in D1+** (12 existing USA D1 analyst alphas prove this)
- Forcing it into D0 violates its economic timing
- **Correct approach**: Use D1 with event windows around earnings dates

### 4. **Neutralization Can Kill Weak Signals**
- Industry neut removed cross-industry divergence (likely the only real signal)
- For weak/noisy data, sometimes **less processing is more**
- But if signal can't survive basic neut, it's probably not robust enough for production

---

## Recommended Path Forward

### Option A: Pivot to D1 Analyst Strategy
```python
# Proper event study logic (D1 required)
ts_rank(
    ts_delta(anl10_prefy1_pred_surps_v1_1108, 5), 
    22
)
```
- Captures **change** in prediction (event)
- **22-day ranking window** smooths noise
- **D1 delay** allows market digestion

### Option B: Switch to USA D0-Compatible Data
Target high-frequency sources:
- **News sentiment** (news5, news85): Updates multiple times daily
- **Intraday volume patterns** (pv1): `adv20`, `vwap`
- **Options implied volatility** (option1): Changes tick-by-tick

### Option C: Explore Other D0 Regions
EUR/ASI D0 categories show **0 alphas** - potentially easier competition:
- Less saturated
- Different market microstructures
- Lower turnover tolerance thresholds

---

## Technical Artifacts

### All Alpha IDs (For Deletion)
**0-Op Batch**:
- kq5dp5qd, LLxWoxL1, WjmMrmjx, npb9GbxM, vRV87Vwd, A1d9XdjQ, zJRPLPXY, E5V9Qe0L

**1-Op Batch**:
- 78VWPeb1, d5wpJNVJ, 88qbWMdq, XgEGZd58, vRV87W3b, gJz6Nnpv, zdWZPrW9, bqWMw7pl

### Operator Validation
All operators used were **confirmed available** via `get_operators()`:
- ✅ `rank`, `ts_mean`, `ts_decay_linear`, `group_rank`
- No "unknown variable" errors (unlike initial flawed attempt with wrong IDs)

### Platform Compliance
- ✅ **Rule of 8** followed (8 expressions per submission)
- ✅ **Economic time windows** (5, 22 days only)
- ✅ **No fabricated operators**
- ✅ **Authentication maintained** throughout

---

## Conclusion

This research **successfully eliminated a non-viable path** rather than finding a winning alpha. The D0 + Analyst predicted surprise combination fundamentally conflicts with:
1. Economic reality (event timing)
2. Signal characteristics (low frequency, high noise)
3. Implementation constraints (transaction costs)

**No amount of feature engineering can fix a structural mismatch.**

Next iteration will target **D0-native data sources** (news/intraday price patterns) or **D1 analyst event strategies** where the timing alignment is correct by design.

**Time saved by strict 0-op testing**: ~8 hours of futile complex logic development.
**Lessons applied to next research cycle**: Immediately validated.

---

**Research Status**: CLOSED - Failed but Informative  
**Next Action**: Switch strategy vector (data source or delay period)  
**Estimated Recovery Time**: New batch ready in 30 minutes
