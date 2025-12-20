【Community Leader -因子构造 💎】Alpha模板库，来自社区的馈赠，为你的72变添砖加瓦 Alpha Template
Followed by 8 people

FF56620
Master consultant
1 day ago
最近大趋势下，想必大家都在使用 72变之类的功能，而72变中，作者提供了一套模板，出货率还不错，不过在此基础上，我通过论坛，让大模型又总结了一份Alpha模板，如标题所言，这份模板均来自社区，所以是来自社区的馈赠

我自己用下来，出货率还不错，和内置模板相当，甚至还能更好一点，不过大家还是要自行评估一下，部分来自社区的论坛也存在过拟合的风险，如有帮助，欢迎点赞，如有错漏，请帮忙指出

    ## 模板格式说明

    每个模板使用以下占位符格式：
    - `<ts_op/>` - 时间序列操作符，如 `ts_rank`, `ts_mean`, `ts_delta`, `ts_ir`, `ts_stddev`, `ts_zscore`
    - `<group_op/>` - 分组操作符，如 `group_rank`, `group_neutralize`, `group_zscore`
    - `<vec_op/>` - 向量操作符，如 `vec_avg`, `vec_sum`, `vec_max`, `vec_min`, `vec_stddev`
    - `<field/>` - 数据字段占位符
    - `<d/>` - 时间窗口参数，常用值: `{5, 22, 66, 126, 252, 504}`
    - `<group/>` - 分组字段，如 `industry`, `sector`, `subindustry`, `market`

    ---

    ## 第一部分：基础结构模板 (TPL-001 ~ TPL-010)

    ### TPL-001: 基本面时序排名
    ```
    模板: <group_op/>(<ts_op/>(<field/>, <d/>), <group/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<ts_op/>` | `ts_rank`, `ts_zscore`, `ts_delta`, `ts_ir` | 时序比较操作 |
    | `<group_op/>` | `group_rank`, `group_zscore`, `group_neutralize` | 截面比较操作 |
    | `<field/>` | 基本面字段: `eps`, `sales`, `assets`, `roe`, `roa` | 公司财务数据 |
    | `<d/>` | `66`, `126`, `252` | 季度/半年/年 |
    | `<group/>` | `industry`, `sector` | 行业分组 |

    **示例**:
    ```
    group_rank(ts_rank(eps, 252), industry)
    group_zscore(ts_ir(sales, 126), sector)
    ```

    ---

    ### TPL-002: 利润/规模比率模板
    ```
    模板: <ts_op/>(<profit_field/>/<size_field/>, <d/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<ts_op/>` | `ts_rank`, `ts_zscore`, `ts_mean`, `ts_delta` | 时序操作 |
    | `<profit_field/>` | `net_income`, `ebitda`, `operating_income`, `gross_profit` | 利润类字段 |
    | `<size_field/>` | `assets`, `cap`, `sales`, `equity` | 规模类字段 |
    | `<d/>` | `66`, `126`, `252` | 中长期窗口 |

    **示例**:
    ```
    ts_rank(net_income/assets, 252)
    ts_zscore(ebitda/cap, 126)
    ts_rank(operating_income/cap, 252)^2
    ```

    ---

    ### TPL-003: 向量数据处理模板 (VECTOR字段必用)
    ```
    模板: <ts_op/>(<vec_op/>(<vector_field/>), <d/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<ts_op/>` | `ts_rank`, `ts_mean`, `ts_delta`, `ts_ir`, `ts_zscore` | 时序操作 |
    | `<vec_op/>` | `vec_avg`, `vec_sum`, `vec_max`, `vec_min`, `vec_stddev` | 向量聚合 |
    | `<vector_field/>` | 分析师数据: `anl4_*`, `analyst_*`, `oth41_*` | VECTOR类型字段 |
    | `<d/>` | `22`, `66`, `126` | 短中期窗口 |

    **示例**:
    ```
    ts_delta(vec_avg(anl4_eps_mean), 22)
    ts_rank(vec_sum(analyst_estimate), 66)
    ts_ir(vec_avg(oth41_s_west_eps_ftm_chg_3m), 126)
    ```

    ---

    ### TPL-004: 双重中性化模板
    ```
    模板:
    a = <ts_op/>(<field/>, <d/>);
    a1 = group_neutralize(a, bucket(rank(cap), range="<range/>"));
    group_neutralize(a1, <group/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<ts_op/>` | `ts_zscore`, `ts_rank`, `ts_ir` | 时序操作 |
    | `<field/>` | 任意数据字段 | 主信号 |
    | `<d/>` | `66`, `126`, `252` | 时间窗口 |
    | `<range/>` | `"0.1,1,0.1"`, `"0,1,0.1"` | 市值分组范围 |
    | `<group/>` | `industry`, `sector`, `subindustry` | 行业分组 |

    **示例**:
    ```
    a = ts_zscore(fnd72_s_pit_or_is_q_spe_si, 252);
    a1 = group_neutralize(a, bucket(rank(cap), range="0.1,1,0.1"));
    group_neutralize(a1, subindustry)
    ```

    ---

    ### TPL-005: 回归中性化模板
    ```
    模板:
    a = <ts_op/>(<field/>, <d/>);
    a1 = group_neutralize(a, bucket(rank(cap), range="<range/>"));
    a2 = group_neutralize(a1, <group/>);
    b = ts_zscore(cap, <d/>);
    b1 = group_neutralize(b, <group/>);
    regression_neut(a2, b1)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<ts_op/>` | `ts_zscore`, `ts_rank` | 时序操作 |
    | `<field/>` | 基本面或其他字段 | 主信号 |
    | `<d/>` | `252`, `504` | 长期窗口 |
    | `<range/>` | `"0.1,1,0.1"` | 市值分组 |
    | `<group/>` | `subindustry`, `sector` | 行业分组 |

    ---

    ### TPL-006: 基本面动量模板
    ```
    模板: log(ts_mean(<field/>, <d_short/>)) - log(ts_mean(<field/>, <d_long/>))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field/>` | `anl4_{data}_{stats}`, 基本面字段 | 数据字段 |
    | `<d_short/>` | `20`, `44` | 短期窗口 |
    | `<d_long/>` | `44`, `126` | 长期窗口 |

    **示例**:
    ```
    log(ts_mean(anl4_eps_mean, 44)) - log(ts_mean(anl4_eps_mean, 20))
    ```

    ---

    ### TPL-007: 财报事件驱动模板
    ```
    模板:
    event = ts_delta(<fundamental_field/>, -1);
    if_else(event != 0, <alpha/>, nan)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<fundamental_field/>` | `assets`, `sales`, `eps` | 基本面字段 |
    | `<alpha/>` | 主信号表达式 | 事件发生时的Alpha |

    **扩展版**:
    ```
    change = if_else(days_from_last_change(<field/>) == <days/>, ts_delta(close, <d/>), nan)
    ```

    ---

    ### TPL-008: 标准化回填模板
    ```
    模板: <ts_op/>(winsorize(ts_backfill(<field/>, <d_backfill/>), std=<std/>), <d/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<ts_op/>` | `ts_rank`, `ts_decay_linear`, `ts_zscore` | 时序操作 |
    | `<field/>` | 低频数据字段 | 需要回填的字段 |
    | `<d_backfill/>` | `115`, `120`, `180` | 回填窗口 |
    | `<std/>` | `4`, `3`, `5` | winsorize标准差 |
    | `<d/>` | `10`, `22`, `60` | 操作窗口 |

    **示例**:
    ```
    ts_decay_linear(-densify(zscore(winsorize(ts_backfill(anl4_adjusted_netincome_ft, 115), std=4))), 10)
    ts_rank(winsorize(ts_backfill(<data>, 120), std=4), 60)
    ```

    ---

    ### TPL-009: 信号质量分组模板
    ```
    模板:
    signal = <ts_op/>(<field/>, <d/>);
    credit_quality = bucket(rank(ts_delay(signal, 1), rate=0), range="<range/>");
    group_neutralize(<decay_op/>(signal, k=<k/>), credit_quality)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<ts_op/>` | `ts_rank`, `ts_zscore` | 信号计算 |
    | `<field/>` | 任意数据字段 | 主字段 |
    | `<d/>` | `60`, `120` | 窗口 |
    | `<range/>` | `"0.2,1,0.2"` | 分组范围 |
    | `<decay_op/>` | `ts_weighted_decay` | 衰减操作 |
    | `<k/>` | `0.5`, `0.3` | 衰减系数 |

    ---

    ### TPL-010: 复合分组中性化
    ```
    模板: group_neutralize(<alpha/>, densify(<group1/>)*1000 + densify(<group2/>))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<alpha/>` | 主信号 | 原始Alpha |
    | `<group1/>` | `subindustry`, `sector` | 主分组 |
    | `<group2/>` | `country`, `exchange` | 次分组 |

    ---

    ## 第二部分：量价类模板 (TPL-101 ~ TPL-120)

    ### TPL-101: 换手率反转
    ```
    模板: -<ts_op/>(volume/sharesout, <d/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<ts_op/>` | `ts_mean`, `ts_rank`, `ts_std_dev` | 时序统计 |
    | `<d/>` | `5`, `22`, `66` | 短中期窗口 |

    **示例**:
    ```
    -ts_mean(volume/sharesout, 22)
    -ts_std_dev(volume/sharesout, 22)
    ```

    ---

    ### TPL-102: 量稳换手率 (STR)
    ```
    模板: -ts_std_dev(volume/sharesout, <d1/>)/ts_mean(volume/sharesout, <d2/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<d1/>` | `20`, `22` | 波动计算窗口 |
    | `<d2/>` | `20`, `22` | 均值计算窗口 |

    **优化版**:
    ```
    模板: -group_neutralize(ts_std_dev(volume/sharesout, <d/>)/ts_mean(volume/sharesout, <d/>), bucket(rank(cap), range="0.1,1,0.1"))
    ```

    ---

    ### TPL-103: 价格反转模板
    ```
    模板: -<ts_op/>(<price_field/>, <d/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<ts_op/>` | `ts_delta`, `ts_mean`, `ts_rank` | 时序操作 |
    | `<price_field/>` | `close`, `returns`, `close/open-1`, `open/ts_delay(close,1)-1` | 价格/收益字段 |
    | `<d/>` | `3`, `5`, `22` | 短期窗口 |

    **示例**:
    ```
    -ts_delta(close, 5)                    # 价格变化反转
    -ts_mean(returns, 22)                  # 收益均值反转
    -ts_mean(close/open-1, 22)             # 日内收益反转
    -(open/ts_delay(close,1)-1)            # 隔夜收益反转
    ```

    ---

    ### TPL-104: 价格乖离率
    ```
    模板: -(close - ts_mean(close, <d/>))/ts_mean(close, <d/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<d/>` | `5`, `22`, `66` | MA周期 |

    ---

    ### TPL-105: 量价相关性
    ```
    模板: -ts_corr(<price_field/>, <volume_field/>, <d/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<price_field/>` | `close`, `returns`, `abs(returns)` | 价格类 |
    | `<volume_field/>` | `volume`, `volume/sharesout`, `adv20` | 成交量类 |
    | `<d/>` | `22`, `66`, `126` | 相关性窗口 |

    ---

    ### TPL-106: 跳跃因子
    ```
    模板: -group_neutralize(ts_mean((close/open-1) - log(close/open), <d/>), bucket(rank(cap), range="0.1,1,0.1"))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<d/>` | `22`, `30`, `66` | 平均窗口 |

    **带成交量增强版**:
    ```
    模板: -group_neutralize(ts_mean((close/open-1) - log(close/open), <d/>) * ts_rank(volume, 5), bucket(rank(cap), range="0.1,1,0.1"))
    ```

    ---

    ### TPL-107: 指数衰减动量
    ```
    模板: -ts_decay_exp_window(<field/>, <d/>, factor=<f/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field/>` | `returns`, `returns*(volume/sharesout)`, `close/open-1` | 收益类字段 |
    | `<d/>` | `22`, `66`, `126` | 衰减窗口 |
    | `<f/>` | `0.04`, `0.1`, `0.5`, `0.9` | 衰减因子，越小衰减越快 |

    ---

    ### TPL-108: 成交量周期函数 (VOC)
    ```
    模板:
    m_minus = ts_mean(volume, <d_long/>) - ts_mean(volume, <d_short/>);
    delta = (ts_max(m_minus, <d_short/>) - m_minus)/(ts_max(m_minus, <d_short/>) - ts_min(m_minus, <d_short/>));
    <weight1/>*delta + <weight2/>*ts_delay(delta, 1)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<d_long/>` | `30`, `66` | 长期均值窗口 |
    | `<d_short/>` | `10`, `22` | 短期均值窗口 |
    | `<weight1/>` | `0.33`, `0.5` | 当日权重 |
    | `<weight2/>` | `0.67`, `0.5` | 前日权重 |

    ---

    ### TPL-109: 市场相关性因子
    ```
    模板:
    mkt_ret = group_mean(returns, 1, market);
    pt = ts_corr(returns, mkt_ret, <d/>);
    rank(1/(2*(1-pt)))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<d/>` | `10`, `22`, `66` | 相关性窗口 |

    ---

    ### TPL-110: 成交量趋势模板
    ```
    模板: ts_decay_linear(volume/ts_sum(volume, <d_long/>), <d_short/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<d_long/>` | `252`, `504` | 长期总量窗口 |
    | `<d_short/>` | `10`, `22` | 衰减窗口 |

    ---

    ### TPL-111: VWAP收益相关
    ```
    模板:
    returns > -<threshold/> ? (ts_ir(ts_corr(ts_returns(vwap, 1), ts_delay(group_neutralize(<field/>, market), <d1/>), <d2/>), <d2/>)) : -1
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<threshold/>` | `0.1`, `0.05` | 收益阈值 |
    | `<field/>` | 任意数据字段 | 信号字段 |
    | `<d1/>` | `30`, `60` | 延迟窗口 |
    | `<d2/>` | `90`, `120` | 相关性窗口 |

    ---

    ### TPL-112: 动量因子创建
    ```
    模板: ts_sum(winsorize(ts_backfill(<data/>, <day/>), std=4.0), <n/>*21) - ts_sum(winsorize(ts_backfill(<data/>, <day/>), std=4.0), <m/>*21)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<data/>` | `returns`, 基本面字段 | 数据字段 |
    | `<day/>` | `120`, `180` | 回填窗口 |
    | `<n/>` | `6`, `12` | 长期月数 |
    | `<m/>` | `1`, `0.1*n` | 短期月数 |

    ---

    ### TPL-113: 线性衰减排名
    ```
    模板: -ts_rank(ts_decay_linear(<field/>, <d1/>), <d2/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field/>` | `percent`, 任意时序信号 | 输入信号 |
    | `<d1/>` | `10`, `22`, `150` | 衰减窗口 |
    | `<d2/>` | `50`, `126` | 排名窗口 |

    ---

    ## 第三部分：情绪/新闻类模板 (TPL-201 ~ TPL-220)

    ### TPL-201: 情绪差值模板
    ```
    模板: <ts_op/>(rank(ts_backfill(<positive_sentiment/>, <d/>)) - rank(ts_backfill(<negative_sentiment/>, <d/>)), <d2/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<ts_op/>` | `ts_mean`, `ts_rank`, `ts_zscore` | 时序操作 |
    | `<positive_sentiment/>` | 正面情绪字段 | 积极信号 |
    | `<negative_sentiment/>` | 负面情绪字段 | 消极信号 |
    | `<d/>` | `20`, `30` | 回填窗口 |
    | `<d2/>` | `5`, `22` | 比较窗口 |

    ---

    ### TPL-202: 新闻情绪回归残差
    ```
    模板:
    sentiment = ts_backfill(ts_delay(<vec_op/>(<sentiment_field/>), 1), <d1/>);
    vhat = ts_regression(volume, sentiment, <d2/>);
    ehat = -ts_regression(returns, vhat, <d3/>);
    group_rank(ehat, bucket(rank(cap), range="0,1,0.1"))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<vec_op/>` | `vec_avg`, `vec_sum` | 情绪聚合方式 |
    | `<sentiment_field/>` | `scl12_sentiment`, `snt_buzz_ret`, `nws18_relevance` | 情绪数据 |
    | `<d1/>` | `20`, `30` | 回填窗口 |
    | `<d2/>` | `120`, `250` | 成交量回归窗口 |
    | `<d3/>` | `250`, `750` | 收益回归窗口 |

    ---

    ### TPL-203: 社交媒体情绪
    ```
    模板: rank(<vec_op/>(scl12_alltype_buzzvec) * <vec_op/>(scl12_sentiment))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<vec_op/>` | `vec_sum`, `vec_avg` | 向量聚合 |

    **带条件版**:
    ```
    模板:
    sent_vol = vec_sum(scl12_alltype_buzzvec);
    trade_when(rank(sent_vol) > 0.95, -zscore(scl12_buzz)*sent_vol, -1)
    ```

    ---

    ### TPL-204: 条件情绪过滤
    ```
    模板:
    group_rank(
    sigmoid(if_else(ts_zscore(<sentiment_field/>, <d/>) > <threshold/>, ts_zscore(<sentiment_field/>, <d/>), 0)),
    <group/>
    )
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<sentiment_field/>` | 情绪字段 | 情绪数据 |
    | `<d/>` | `22`, `30`, `66` | zscore窗口 |
    | `<threshold/>` | `1`, `1.5`, `2` | z-score阈值 |
    | `<group/>` | `industry`, `sector` | 分组字段 |

    ---

    ### TPL-205: 情绪+波动率复合
    ```
    模板: log(1 + sigmoid(ts_zscore(<sentiment_field/>, <d1/>)) * sigmoid(ts_zscore(<volatility_field/>, <d2/>)))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<sentiment_field/>` | 情绪字段 | 情绪数据 |
    | `<volatility_field/>` | `option8_*`, 波动率字段 | 波动率数据 |
    | `<d1/>` | `30`, `66` | 情绪窗口 |
    | `<d2/>` | `30`, `66` | 波动率窗口 |

    ---

    ### TPL-206: 指数衰减情绪
    ```
    模板: ts_decay_exp_window(vec_avg(<sentiment_field/>), <d/>, <factor/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<sentiment_field/>` | `mws85_sentiment`, `nws18_ber` | 情绪向量字段 |
    | `<d/>` | `10`, `22` | 衰减窗口 |
    | `<factor/>` | `0.9`, `0.7` | 衰减因子 |

    **双情绪组合**:
    ```
    decayed_sentiment_1 = ts_decay_exp_window(vec_avg(mws85_sentiment), 10, 0.9);
    decayed_sentiment_2 = ts_decay_exp_window(vec_avg(nws18_ber), 10, 0.9);
    decayed_sentiment_1 + decayed_sentiment_2
    ```

    ---

    ### TPL-207: 新闻结果排名
    ```
    模板:
    percent = ts_rank(vec_stddev(<news_field/>), <d1/>);
    -ts_rank(ts_decay_linear(percent, <d2/>), <d1/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<news_field/>` | `nws12_prez_result2` | 新闻数据 |
    | `<d1/>` | `50`, `66` | 排名窗口 |
    | `<d2/>` | `150`, `252` | 衰减窗口 |

    ---

    ### TPL-208: 分组行业提取情绪
    ```
    模板: scale(group_extra(ts_sum(sigmoid(ts_backfill(<data/>, <d1/>)), <d2/>) - ts_sum(sigmoid(ts_backfill(<data/>, <d1/>)), <d2/>), 0.5, densify(industry)))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<data/>` | 情绪或基本面字段 | 数据字段 |
    | `<d1/>` | `180`, `252` | 回填窗口 |
    | `<d2/>` | `3`, `5` | 求和窗口 |

    ---

    ## 第四部分：期权类模板 (TPL-301 ~ TPL-320)

    ### TPL-301: 期权希腊字母差值
    ```
    模板: <group_op/>(<put_greek/> - <call_greek/>, <group/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<group_op/>` | `group_rank`, `group_neutralize`, `group_zscore` | 分组操作 |
    | `<put_greek/>` | `put_delta`, `put_gamma`, `put_theta`, `put_vega` | Put希腊字母 |
    | `<call_greek/>` | `call_delta`, `call_gamma`, `call_theta`, `call_vega` | Call希腊字母 |
    | `<group/>` | `industry`, `sector` | 分组字段 |

    ---

    ### TPL-302: 期权价格信号
    ```
    模板: group_rank(<ts_op/>(<vec_op/>(<option_price_field/>)/close, <d/>), <group/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<ts_op/>` | `ts_scale`, `ts_rank`, `ts_zscore` | 时序操作 |
    | `<vec_op/>` | `vec_max`, `vec_avg` | 向量操作 |
    | `<option_price_field/>` | 期权价格字段 | 期权数据 |
    | `<d/>` | `66`, `120`, `252` | 时间窗口 |
    | `<group/>` | `industry`, `sector` | 分组字段 |

    ---

    ### TPL-303: 期权波动率信号
    ```
    模板: sigmoid(<ts_op/>(<opt_high/> - <opt_close/>, <d/>))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<ts_op/>` | `ts_ir`, `ts_stddev`, `ts_zscore`, `ts_mean` | 波动性操作 |
    | `<opt_high/>` | 期权高价字段 | 期权最高价 |
    | `<opt_close/>` | 期权收盘价字段 | 期权收盘价 |
    | `<d/>` | `120`, `250`, `504` | 长期窗口 |

    **说明**: 期权波动类因子通常需要较长窗口(120-504天)来捕捉稳定信号

    ---

    ### TPL-304: 隐含波动率比率
    ```
    模板: <ts_op/>(implied_volatility_call_<tenor/>/parkinson_volatility_<tenor/>, <d/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<ts_op/>` | `ts_rank`, `ts_zscore`, `ts_delta` | 时序操作 |
    | `<tenor/>` | `120`, `270` | 期权期限 |
    | `<d/>` | `66`, `126`, `252` | 窗口 |

    ---

    ### TPL-305: Put-Call成交量比
    ```
    模板: <ts_op/>(pcr_vol_<tenor/>, <d/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<ts_op/>` | `ts_rank`, `ts_delta`, `ts_zscore` | 时序操作 |
    | `<tenor/>` | `10`, `30`, `60` | 期限 |
    | `<d/>` | `22`, `66`, `126` | 窗口 |

    ---

    ### TPL-306: 期权盈亏平衡点
    ```
    模板: group_rank(ts_zscore(<breakeven_field/>/close, <d/>), <group/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<breakeven_field/>` | `call_breakeven_10`, `put_breakeven_10` | 盈亏平衡字段 |
    | `<d/>` | `66`, `126`, `252` | 窗口 |
    | `<group/>` | `sector`, `industry` | 分组 |

    ---

    ## 第五部分：分析师类模板 (TPL-401 ~ TPL-420)

    ### TPL-401: 分析师预期变化
    ```
    模板: <vec_op/>(tail(tail(<analyst_change_field/>, lower=<low/>, upper=<high/>, newval=<low/>), lower=-<high/>, upper=-<low/>, newval=-<low/>))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<vec_op/>` | `vec_avg`, `vec_sum` | 向量聚合 |
    | `<analyst_change_field/>` | `oth41_s_west_eps_ftm_chg_3m`, `anl4_eps_chg` | 预期变化字段 |
    | `<low/>` | `0.25`, `0.1` | 下截断值 |
    | `<high/>` | `1000`, `100` | 上截断值 |

    ---

    ### TPL-402: 剥离动量的分析师因子
    ```
    模板:
    afr = <vec_op/>(<analyst_field/>);
    short_mom = ts_mean(returns - group_mean(returns, 1, market), <d_short/>);
    long_mom = ts_delay(ts_mean(returns - group_mean(returns, 1, market), <d_long/>), <d_long/>);
    regression_neut(regression_neut(afr, short_mom), long_mom)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<vec_op/>` | `vec_avg`, `vec_sum` | 向量聚合 |
    | `<analyst_field/>` | 分析师数据字段 | 一致预期等 |
    | `<d_short/>` | `5`, `10` | 短期动量窗口 |
    | `<d_long/>` | `20`, `22` | 长期动量窗口 |

    ---

    ### TPL-403: 分析师覆盖度过滤
    ```
    模板:
    coverage_filter = ts_sum(<vec_op/>(<analyst_field/>), <d/>) > <min_count/>;
    if_else(coverage_filter, <alpha/>, nan)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<vec_op/>` | `vec_count` | 统计分析师数量 |
    | `<analyst_field/>` | 分析师向量字段 | 分析师数据 |
    | `<d/>` | `66`, `90`, `126` | 统计窗口 |
    | `<min_count/>` | `2`, `3`, `5` | 最小覆盖数量 |
    | `<alpha/>` | 主信号表达式 | 待过滤的Alpha |

    ---

    ### TPL-404: 老虎哥回归模板
    ```
    模板: group_rank(ts_regression(ts_zscore(<field1/>, <d/>), ts_zscore(vec_sum(<field2/>), <d/>), <d/>), densify(sector))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field1/>` | 任意MATRIX字段 | Y变量 |
    | `<field2/>` | 任意VECTOR字段 | X变量 |
    | `<d/>` | `252`, `504` | 回归窗口 |

    **说明**: 经典回归模板，适用于基本面与分析师数据组合

    ---

    ### TPL-405: 分析师预期时序变化
    ```
    模板: ts_mean(vec_avg(<analyst_field/>), <d_short/>) - ts_mean(vec_avg(<analyst_field/>), <d_long/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<analyst_field/>` | `anl4_eps_mean`, `anl4_revenue_mean` | 分析师预测 |
    | `<d_short/>` | `22`, `44` | 短期窗口 |
    | `<d_long/>` | `66`, `126` | 长期窗口 |

    ---

    ### TPL-406: 三因子组合模板
    ```
    模板:
    my_group = market;
    rank(
    group_rank(ts_decay_linear(volume/ts_sum(volume, 252), 10), my_group) *
    group_rank(ts_rank(vec_avg(<fundamental/>), <d/>), my_group) *
    group_rank(-ts_delta(close, 5), my_group)
    )
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<fundamental/>` | 基本面VECTOR字段 | 基本面数据 |
    | `<d/>` | `252`, `504` | 排名窗口 |

    ---

    ### TPL-407: 分析师FCF比率
    ```
    模板: ts_rank(vec_avg(<fcf_field/>) / vec_avg(<profit_field/>), <d/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<fcf_field/>` | `anl4_fcf_value` | 自由现金流预测 |
    | `<profit_field/>` | `anl4_netprofit_low`, `anl4_netprofit_mean` | 利润预测 |
    | `<d/>` | `66`, `126`, `252` | 排名窗口 |

    ---

    ## 第六部分：中性化技术模板 (TPL-501 ~ TPL-515)

    ### TPL-501: 市值分组中性化
    ```
    模板: group_neutralize(<alpha/>, bucket(rank(cap), range="<range/>"))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<alpha/>` | 主信号表达式 | 待中性化的Alpha |
    | `<range/>` | `"0.1,1,0.1"`, `"0,1,0.1"` | 分组范围 |

    ---

    ### TPL-502: 双重中性化 (行业+市值)
    ```
    模板:
    a1 = group_neutralize(<alpha/>, bucket(rank(cap), range="<range/>"));
    group_neutralize(a1, <group/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<alpha/>` | 主信号 | 原始Alpha |
    | `<range/>` | `"0.1,1,0.1"` | 市值分组 |
    | `<group/>` | `industry`, `sector`, `subindustry` | 行业分组 |

    ---

    ### TPL-503: 回归中性化
    ```
    模板: regression_neut(<alpha/>, <factor/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<alpha/>` | 主信号 | 原始Alpha |
    | `<factor/>` | `log(cap)`, `ts_ir(returns, 126)`, `ts_std_dev(returns, 22)` | 待剥离因子 |

    **多层回归中性化**:
    ```
    模板: regression_neut(regression_neut(<alpha/>, <factor1/>), <factor2/>)
    ```

    ---

    ### TPL-504: 中性化顺序优化
    ```
    模板:
    a = ts_zscore(<field/>, <d/>);
    a1 = group_neutralize(a, <group/>);
    a2 = group_neutralize(a1, bucket(rank(cap), range="<range/>"))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field/>` | 任意数据字段 | 主信号 |
    | `<d/>` | `252` | zscore窗口 |
    | `<group/>` | `industry`, `subindustry` | 行业分组 |
    | `<range/>` | `"0.1,1,0.1"` | 市值分组 |

    **说明**: 先行业中性化再市值中性化，与反向顺序效果可能不同

    ---

    ### TPL-505: sta1分组中性化
    ```
    模板: group_neutralize(<alpha/>, sta1_top3000c20)
    ```
    **说明**: 使用预定义的sta1分组进行中性化

    ---

    ## 第七部分：条件交易模板 (TPL-601 ~ TPL-620)

    ### TPL-601: 流动性过滤
    ```
    模板: trade_when(volume > adv20 * <threshold/>, <alpha/>, -1)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<threshold/>` | `0.618`, `0.5`, `1` | 流动性阈值 |
    | `<alpha/>` | 主信号 | 原始Alpha |

    **反向流动性**:
    ```
    trade_when(volume < adv20, <alpha/>, -1)
    ```

    ---

    ### TPL-602: 波动率过滤
    ```
    模板: trade_when(ts_rank(ts_std_dev(returns, <d1/>), <d2/>) < <threshold/>, <alpha/>, -1)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<d1/>` | `5`, `10`, `22` | 波动计算窗口 |
    | `<d2/>` | `126`, `180`, `252` | 排名窗口 |
    | `<threshold/>` | `0.8`, `0.9` | 波动率阈值 |
    | `<alpha/>` | 主信号 | 原始Alpha |

    ---

    ### TPL-603: 极端收益过滤
    ```
    模板: trade_when(abs(returns) < <entry/>, <alpha/>, abs(returns) > <exit/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<entry/>` | `0.075`, `0.05` | 入场阈值 |
    | `<exit/>` | `0.1`, `0.095` | 出场阈值 |
    | `<alpha/>` | 主信号 | 原始Alpha |

    ---

    ### TPL-604: 市值过滤
    ```
    模板: trade_when(rank(cap) > <threshold/>, <alpha/>, -1)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<threshold/>` | `0.3`, `0.5` | 市值排名阈值 |
    | `<alpha/>` | 主信号 | 原始Alpha |

    ---

    ### TPL-605: 触发条件交易
    ```
    模板:
    triggerTradeexp = (ts_arg_max(volume, <d/>) < 1) && (volume > ts_sum(volume, <d/>)/<d/>);
    triggerExitexp = -1;
    trade_when(triggerTradeexp, <alpha/>, triggerExitexp)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<d/>` | `5`, `10` | 判断窗口 |
    | `<alpha/>` | `-rank(ts_delta(close, 2))` | 主信号 |

    ---

    ### TPL-606: 组合条件交易
    ```
    模板:
    my_group2 = bucket(rank(cap), range="0,1,0.1");
    trade_when(volume > adv20, group_neutralize(<alpha/>, my_group2), -1)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<alpha/>` | 复合信号 | 主信号 |

    ---

    ### TPL-607: 条件排名交易
    ```
    模板:
    a = <ts_op/>(<field/>, <d/>);
    trade_when(rank(a) > <threshold_low/>, -zscore(<field2/>)*a, <threshold_high/>-rank(a))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<ts_op/>` | `ts_rank`, `ts_zscore` | 时序操作 |
    | `<field/>` | 任意字段 | 条件字段 |
    | `<field2/>` | 任意字段 | 信号字段 |
    | `<d/>` | `25`, `66` | 窗口 |
    | `<threshold_low/>` | `0.03`, `0.1` | 下阈值 |
    | `<threshold_high/>` | `0.25`, `0.5` | 上阈值 |

    ---

    ## 第八部分：复合多因子模板 (TPL-701 ~ TPL-720)

    ### TPL-701: 三因子乘积
    ```
    模板:
    my_group = market;
    rank(
    group_rank(<ts_op1/>(<field1/>, <d1/>), my_group) *
    group_rank(<ts_op2/>(<field2/>, <d2/>), my_group) *
    group_rank(<ts_op3/>(<field3/>, <d3/>), my_group)
    )
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<ts_op1/>` | `ts_decay_linear`, `ts_rank` | 第一因子操作 |
    | `<ts_op2/>` | `ts_rank`, `ts_zscore` | 第二因子操作 |
    | `<ts_op3/>` | `-ts_delta` | 第三因子操作(反转) |
    | `<field1/>` | `volume/ts_sum(volume, 252)` | 成交量趋势 |
    | `<field2/>` | `vec_avg({Fundamental})` | 基本面信号 |
    | `<field3/>` | `close` | 价格信号 |
    | `<d1/>`, `<d2/>`, `<d3/>` | 各因子窗口 | 时间参数 |

    ---

    ### TPL-702: 波动率条件反转
    ```
    模板:
    vol = ts_std_dev(<ret_field/>, <d/>);
    vol_mean = group_mean(vol, 1, market);
    flip_ret = if_else(vol < vol_mean, -<ret_field/>, <ret_field/>);
    -ts_mean(flip_ret, <d/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<ret_field/>` | `returns`, `close/open-1` | 收益字段 |
    | `<d/>` | `20`, `22` | 窗口参数 |

    **说明**: 低波动环境做反转，高波动环境做动量

    ---

    ### TPL-703: 恐惧指标组合
    ```
    模板:
    fear = ts_mean(
    abs(returns - group_mean(returns, 1, market)) /
    (abs(returns) + abs(group_mean(returns, 1, market)) + 0.1),
    <d/>
    );
    -group_neutralize(fear * <signal/>, bucket(rank(cap), range="0.1,1,0.1"))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<d/>` | `20`, `22` | 恐惧指标窗口 |
    | `<signal/>` | 主信号表达式 | 待组合信号 |

    ---

    ### TPL-704: 债务杠杆相关性
    ```
    模板: group_neutralize(ts_zscore(<leverage_field/>, <d1/>) * ts_corr(<leverage_field/>, returns, <d2/>), sector)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<leverage_field/>` | `debt_to_equity`, `debt/assets` | 杠杆字段 |
    | `<d1/>` | `60`, `126` | zscore窗口 |
    | `<d2/>` | `20`, `66` | 相关性窗口 |

    ---

    ### TPL-705: 模型数据信号
    ```
    模板: -<model_field/>
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<model_field/>` | `mdl175_01dtsv`, `mdl175_01icc` | 模型字段 |

    **带排名版**:
    ```
    rank(group_rank(ts_rank(ts_backfill(<model_field/>, 5), 5), sta1_top3000c20))
    ```

    ---

    ### TPL-706: 回归zscore模板
    ```
    模板: ts_regression(ts_zscore(<field1/>, <d/>), ts_zscore(<field2/>, <d/>), <d/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field1/>` | MATRIX字段 | Y变量 |
    | `<field2/>` | MATRIX字段或vec_sum(VECTOR) | X变量 |
    | `<d/>` | `252`, `500`, `504` | 回归窗口 |

    ---

    ### TPL-707: 分组Delta模板
    ```
    模板: group_neutralize(ts_delta(<field/>, <d/>), sector)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field/>` | 任意数据字段 | 主字段 |
    | `<d/>` | `22`, `66`, `126` | 差分窗口 |

    ---

    ## 第九部分：数据预处理模板 (TPL-801 ~ TPL-815)

    ### TPL-801: Winsorize截断
    ```
    模板: winsorize(<field/>, std=<std/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field/>` | 任意字段 | 原始数据 |
    | `<std/>` | `3`, `4`, `5` | 截断标准差 |

    ---

    ### TPL-802: Sigmoid归一化
    ```
    模板: sigmoid(<ts_op/>(<field/>, <d/>))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<ts_op/>` | `ts_zscore`, `ts_ir`, `ts_rank` | 时序操作 |
    | `<field/>` | 任意字段 | 原始数据 |
    | `<d/>` | `22`, `66`, `252` | 窗口 |

    ---

    ### TPL-803: 数据回填
    ```
    模板: ts_backfill(<field/>, <d/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field/>` | 低频数据字段 | 需要回填的字段 |
    | `<d/>` | `115`, `120`, `180`, `252` | 回填窗口 |

    ---

    ### TPL-804: 条件替换
    ```
    模板: if_else(is_not_nan(<field/>), <field/>, <alternative/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field/>` | 主字段 | 可能有NaN的字段 |
    | `<alternative/>` | 替代字段或值 | NaN时的替代 |

    ---

    ### TPL-805: 极端值替换
    ```
    模板: tail(tail(<field/>, lower=<low/>, upper=<high/>, newval=<low/>), lower=-<high/>, upper=-<low/>, newval=-<low/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field/>` | 任意字段 | 原始数据 |
    | `<low/>` | `0.25`, `0.1` | 下界 |
    | `<high/>` | `100`, `1000` | 上界 |

    ---

    ### TPL-806: 组合预处理
    ```
    模板: <ts_op/>(winsorize(ts_backfill(<field/>, <d_backfill/>), std=<std/>), <d/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<ts_op/>` | `ts_rank`, `ts_zscore`, `ts_mean` | 时序操作 |
    | `<field/>` | 低频字段 | 需要处理的字段 |
    | `<d_backfill/>` | `120`, `180` | 回填窗口 |
    | `<std/>` | `4` | winsorize参数 |
    | `<d/>` | `22`, `66` | 操作窗口 |

    ---

    ### TPL-807: ts_min/ts_max替代
    ```
    模板: ts_backfill(if_else(ts_arg_min(<field/>, <d/>) == 0, <field/>, nan), 120)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field/>` | 任意字段 | 原始数据 |
    | `<d/>` | `22`, `66`, `126` | 窗口 |

    **说明**: 当ts_min/ts_max不可用时的替代方案

    ---

    ## 第十部分：高级统计模板 (TPL-901 ~ TPL-920)

    ### TPL-901: 高阶矩模板 (ts_moment)
    ```
    模板: <ts_op/>(<group_op/>(ts_moment(<field/>, <d/>, k=<k/>), <group/>))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<ts_op/>` | `rank`, `zscore`, `sigmoid` | 标准化操作 |
    | `<group_op/>` | `group_rank`, `group_zscore` | 分组操作 |
    | `<field/>` | 任意MATRIX字段 | 数据字段 |
    | `<d/>` | `22`, `66`, `126` | 窗口 |
    | `<k/>` | `2`, `3`, `4` | k=2方差, k=3偏度, k=4峰度 |

    **说明**: ts_moment(x, d, k)计算k阶中心矩

    ---

    ### TPL-902: 协偏度/协峰度模板
    ```
    模板: <group_op/>(ts_co_skewness(<field1/>, <field2/>, <d/>), <group/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<group_op/>` | `group_rank`, `group_zscore` | 分组操作 |
    | `<field1/>` | `returns`, `close` | 第一变量 |
    | `<field2/>` | `volume`, `vwap` | 第二变量 |
    | `<d/>` | `66`, `126`, `252` | 窗口 |

    **协峰度版**:
    ```
    模板: <group_op/>(ts_co_kurtosis(<field1/>, <field2/>, <d/>), <group/>)
    ```

    ---

    ### TPL-903: 偏相关模板 (ts_partial_corr)
    ```
    模板: group_rank(ts_partial_corr(<field1/>, <field2/>, <control/>, <d/>), <group/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field1/>` | `returns`, 收益相关 | Y变量 |
    | `<field2/>` | 任意字段 | X变量 |
    | `<control/>` | `group_mean(returns, 1, market)` | 控制变量(市场收益) |
    | `<d/>` | `60`, `126`, `252` | 窗口 |
    | `<group/>` | `sector`, `industry` | 分组 |

    **说明**: 计算两变量偏相关，控制第三变量影响

    ---

    ### TPL-904: 三元相关模板 (ts_triple_corr)
    ```
    模板: group_rank(ts_triple_corr(<field1/>, <field2/>, <field3/>, <d/>), <group/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field1/>` | `returns` | 第一变量 |
    | `<field2/>` | `volume` | 第二变量 |
    | `<field3/>` | 基本面字段 | 第三变量 |
    | `<d/>` | `60`, `126` | 窗口 |
    | `<group/>` | `sector`, `industry` | 分组 |

    ---

    ### TPL-905: Theil-Sen回归模板
    ```
    模板: group_rank(ts_theilsen(<field1/>, <field2/>, <d/>), <group/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field1/>` | 任意MATRIX字段 | Y变量 |
    | `<field2/>` | 任意MATRIX字段或`ts_step(1)` | X变量 |
    | `<d/>` | `126`, `252`, `500` | 窗口 |
    | `<group/>` | `sector`, `industry` | 分组 |

    **说明**: Theil-Sen回归比普通回归更鲁棒

    ---

    ### TPL-906: 多项式回归残差
    ```
    模板: ts_poly_regression(<field1/>, <field2/>, <d/>, k=<k/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field1/>` | Y变量 | 被解释变量 |
    | `<field2/>` | X变量 | 解释变量 |
    | `<d/>` | `126`, `252` | 窗口 |
    | `<k/>` | `1`, `2`, `3` | 多项式阶数, k=2为二次回归 |

    **说明**: 返回 y - Ey (残差)

    ---

    ### TPL-907: 向量中性化模板
    ```
    模板: ts_vector_neut(<alpha/>, <risk_factor/>, <d/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<alpha/>` | 主信号 | 待中性化Alpha |
    | `<risk_factor/>` | `returns`, `cap` | 风险因子 |
    | `<d/>` | `22`, `66`, `126` | 窗口(不宜过长，计算慢) |

    **分组向量中性化**:
    ```
    模板: group_vector_neut(<alpha/>, <risk_factor/>, <group/>)
    ```

    ---

    ### TPL-908: 加权衰减模板
    ```
    模板: group_neutralize(ts_weighted_decay(<alpha/>, k=<k/>), <group/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<alpha/>` | 主信号 | 待衰减Alpha |
    | `<k/>` | `0.3`, `0.5`, `0.7` | 衰减系数 |
    | `<group/>` | `bucket(rank(cap), range="0.1,1,0.1")` | 分组 |

    ---

    ### TPL-909: 回归斜率模板
    ```
    模板: ts_regression(ts_zscore(<field/>, <d/>), ts_step(1), <d/>, rettype=2)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field/>` | 任意MATRIX字段 | 数据字段 |
    | `<d/>` | `252`, `500` | 窗口 |

    **说明**: rettype=2返回斜率，用于检测趋势

    ---

    ### TPL-910: 最小最大压缩模板
    ```
    模板: ts_min_max_cps(<field/>, <d/>, f=<f/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field/>` | 任意字段 | 数据字段 |
    | `<d/>` | `22`, `66`, `126` | 窗口 |
    | `<f/>` | `2`, `0.5` | 压缩因子 |

    **等价公式**: `x - f * (ts_min(x, d) + ts_max(x, d))`

    ---

    ## 第十一部分：事件驱动模板 (TPL-1001 ~ TPL-1020)

    ### TPL-1001: 数据变化天数模板
    ```
    模板: if_else(days_from_last_change(<field/>) == <days/>, <alpha/>, nan)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field/>` | 基本面字段 | 监测变化的字段 |
    | `<days/>` | `1`, `2`, `5` | 距离变化的天数 |
    | `<alpha/>` | `ts_delta(close, 5)`, 主信号 | 事件触发时的Alpha |

    **动态衰减版**:
    ```
    模板: <alpha/> / (1 + days_from_last_change(<field/>))
    ```

    ---

    ### TPL-1002: 最近差值模板
    ```
    模板: <ts_op/>(last_diff_value(<field/>, <d/>), <d2/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<ts_op/>` | `ts_rank`, `ts_zscore` | 时序操作 |
    | `<field/>` | 任意字段 | 数据字段 |
    | `<d/>` | `60`, `90`, `120` | 回溯窗口 |
    | `<d2/>` | `22`, `66` | 操作窗口 |

    **说明**: 返回过去d天内最近一次不同于当前值的历史值

    ---

    ### TPL-1003: 缺失值计数模板
    ```
    模板: -ts_count_nans(ts_backfill(<field/>, <d1/>), <d2/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field/>` | 分析师数据等 | 可能有缺失的字段 |
    | `<d1/>` | `5`, `10` | 回填窗口 |
    | `<d2/>` | `20`, `30` | 计数窗口 |

    **应用**: 分析师覆盖度信号，缺失越少覆盖越好

    ---

    ### TPL-1004: 位置最大/最小模板
    ```
    模板: if_else(ts_arg_max(<field/>, <d/>) == <position/>, <alpha/>, nan)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field/>` | `volume`, 任意字段 | 监测字段 |
    | `<d/>` | `5`, `10` | 窗口 |
    | `<position/>` | `0`, `1` | 0表示今天是最大值 |
    | `<alpha/>` | 主信号 | 条件满足时的Alpha |

    **组合条件**:
    ```
    模板: (ts_arg_max(<field1/>, <d/>) == ts_arg_max(<field2/>, <d/>)) * (<alpha1/> + <alpha2/>)
    ```

    ---

    ### TPL-1005: 财报发布事件模板
    ```
    模板:
    event_signal = if_else(ts_delta(<fundamental_field/>, 1) != 0, <alpha/>, nan);
    ts_decay_linear(event_signal, <decay_d/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<fundamental_field/>` | `assets`, `sales`, `eps` | 基本面字段 |
    | `<alpha/>` | `ts_delta(close, 5)`, 主信号 | 事件Alpha |
    | `<decay_d/>` | `10`, `22` | 衰减窗口 |

    ---

    ### TPL-1006: 动态Decay事件驱动
    ```
    模板:
    decay_weight = 1 / (1 + days_from_last_change(<event_field/>));
    <alpha/> * decay_weight
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<event_field/>` | 任意字段 | 事件触发字段 |
    | `<alpha/>` | 主信号 | 原始Alpha |

    ---

    ### TPL-1007: 盈利公告模板
    ```
    模板:
    surprise = <actual_field/> - <estimate_field/>;
    if_else(days_from_last_change(<actual_field/>) < <window/>, surprise, nan)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<actual_field/>` | `eps` | 实际值 |
    | `<estimate_field/>` | `vec_avg(anl4_eps_mean)` | 预测值 |
    | `<window/>` | `5`, `10` | 事件有效窗口 |

    ---

    ## 第十二部分：信号处理模板 (TPL-1101 ~ TPL-1120)

    ### TPL-1101: 黄金比例幂变换
    ```
    模板: signed_power(<alpha/>, 0.618)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<alpha/>` | 主信号表达式 | 原始Alpha |

    **其他幂次**:
    ```
    signed_power(<alpha/>, 0.5)   # 平方根
    signed_power(<alpha/>, 2)     # 平方增强
    ```

    ---

    ### TPL-1102: 尾部截断模板
    ```
    模板: right_tail(<alpha/>, minimum=<min/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<alpha/>` | 主信号 | 原始Alpha |
    | `<min/>` | `0`, `0.1` | 最小阈值 |

    **左尾版**:
    ```
    模板: left_tail(<alpha/>, maximum=<max/>)
    ```

    ---

    ### TPL-1103: Clamp边界限制
    ```
    模板: clamp(<alpha/>, lower=<low/>, upper=<high/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<alpha/>` | 主信号 | 原始Alpha |
    | `<low/>` | `-1`, `-0.5` | 下界 |
    | `<high/>` | `1`, `0.5` | 上界 |

    ---

    ### TPL-1104: 分数映射模板
    ```
    模板: fraction(<alpha/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<alpha/>` | 主信号 | 原始Alpha |

    **说明**: 将连续变量映射到分布内的相对位置

    ---

    ### TPL-1105: NaN外推模板
    ```
    模板: nan_out(<field/>, lower=<low/>, upper=<high/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field/>` | 任意字段 | 数据字段 |
    | `<low/>` | `-3`, `-5` | 下界 |
    | `<high/>` | `3`, `5` | 上界 |

    **说明**: 将超出范围的值替换为NaN

    ---

    ### TPL-1106: Purify数据清洗
    ```
    模板: purify(<field/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field/>` | 任意字段 | 需要清洗的数据 |

    **说明**: 自动化数据清洗，减少噪声和异常值

    ---

    ### TPL-1107: 条件保留模板
    ```
    模板: keep(<field/>, <condition/>, period=<d/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field/>` | 任意字段 | 数据字段 |
    | `<condition/>` | `<field/> > 0` | 保留条件 |
    | `<d/>` | `3`, `5`, `10` | 滚动窗口 |

    **示例**:
    ```
    keep(returns, returns > 0, period=3)  # 只保留正收益
    ```

    ---

    ### TPL-1108: 缩放降维模板
    ```
    模板: -scale_down(<ts_op/>(<field/>, <d1/>), constant=<c/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<ts_op/>` | `ts_mean`, `ts_rank` | 时序操作 |
    | `<field/>` | `returns`, 任意字段 | 数据字段 |
    | `<d1/>` | `2`, `5` | 窗口 |
    | `<c/>` | `0.1`, `0.05` | 缩放常数 |

    ---

    ### TPL-1109: Truncate截断模板
    ```
    模板: truncate(<alpha/>, maxPercent=<percent/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<alpha/>` | 主信号 | 原始Alpha |
    | `<percent/>` | `0.01`, `0.05` | 截断百分比 |

    ---

    ### TPL-1110: 组合Normalize模板
    ```
    模板: group_normalize(<alpha/>, <group/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<alpha/>` | 主信号 | 原始Alpha |
    | `<group/>` | `sector`, `industry` | 分组 |

    **等价公式**: `alpha / group_sum(abs(alpha), group)`

    ---

    ## 第十三部分：Turnover控制模板 (TPL-1201 ~ TPL-1215)

    ### TPL-1201: 目标换手率Hump
    ```
    模板: ts_target_tvr_hump(<alpha/>, lambda_min=0, lambda_max=1, target_tvr=<target/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<alpha/>` | 主信号 | 原始Alpha |
    | `<target/>` | `0.1`, `0.15`, `0.2` | 目标换手率 |

    ---

    ### TPL-1202: Delta限制换手率
    ```
    模板: ts_target_tvr_delta_limit(<alpha/>, <factor/>, lambda_min=0, lambda_max=1, target_tvr=<target/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<alpha/>` | 主信号 | 原始Alpha |
    | `<factor/>` | 辅助因子 | 限制因子 |
    | `<target/>` | `0.1`, `0.15` | 目标换手率 |

    ---

    ### TPL-1203: Hump衰减组合
    ```
    模板: hump_decay(<alpha/>, hump=<h/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<alpha/>` | 主信号 | 原始Alpha |
    | `<h/>` | `0.001`, `0.01` | Hump参数 |

    **嵌套版**:
    ```
    hump(hump_decay(<alpha/>, hump=0.001))
    ```

    ---

    ### TPL-1204: 平均+Hump模板
    ```
    模板: -ts_mean(ts_target_tvr_hump(group_rank(<field/>, country), lambda_min=0, lambda_max=1, target_tvr=<target/>), <d/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field/>` | 任意字段 | 数据字段 |
    | `<target/>` | `0.1` | 目标换手率 |
    | `<d/>` | `5`, `10` | 平均窗口 |

    ---

    ### TPL-1205: 简单Hump模板
    ```
    模板: hump(<alpha/>, hump=<h/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<alpha/>` | 主信号 | 原始Alpha |
    | `<h/>` | `0.01`, `0.001`, `0.0001` | Hump参数 |

    **示例**:
    ```
    hump(-ts_delta(close, 5), hump=0.01)
    ```

    ---

    ## 第十四部分：回填与覆盖模板 (TPL-1301 ~ TPL-1315)

    ### TPL-1301: 分组回填模板
    ```
    模板: group_backfill(<field/>, <group/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field/>` | 任意字段 | 需要回填的字段 |
    | `<group/>` | `sector`, `industry`, `market` | 分组字段 |

    **说明**: 使用组内最近值填充NaN

    ---

    ### TPL-1302: 嵌套回填排名
    ```
    模板: rank(group_backfill(<field/>, <group/>))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field/>` | 任意字段 | 数据字段 |
    | `<group/>` | `sector`, `industry` | 分组 |

    ---

    ### TPL-1303: 覆盖度过滤
    ```
    模板: group_count(is_nan(<field/>), market) > <threshold/> ? <alpha/> : nan
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field/>` | 任意字段 | 检测字段 |
    | `<threshold/>` | `40`, `50` | 最小覆盖数 |
    | `<alpha/>` | 主信号 | 原始Alpha |

    ---

    ### TPL-1304: NaN替换模板
    ```
    模板: if_else(is_not_nan(<field/>), <field/>, <default/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field/>` | 任意字段 | 数据字段 |
    | `<default/>` | `0`, `0.5`, `nan` | 默认值 |

    ---

    ### TPL-1305: 综合数据清洗
    ```
    模板: <ts_op/>(winsorize(group_backfill(ts_backfill(<field/>, <d1/>), <group/>), std=<std/>), <d2/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<ts_op/>` | `ts_rank`, `ts_zscore` | 时序操作 |
    | `<field/>` | 低频字段 | 数据字段 |
    | `<d1/>` | `120`, `180` | 时序回填窗口 |
    | `<group/>` | `sector`, `industry` | 分组回填 |
    | `<std/>` | `4` | winsorize参数 |
    | `<d2/>` | `66`, `126` | 操作窗口 |

    ---

    ## 第十五部分：组合提取模板 (TPL-1401 ~ TPL-1415)

    ### TPL-1401: group_extra填补模板
    ```
    模板: group_extra(<field/>, <weight/>, <group/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field/>` | 任意字段 | 数据字段 |
    | `<weight/>` | `0.5`, `1` | 权重 |
    | `<group/>` | `densify(industry)`, `sector` | 分组 |

    **说明**: 用组均值填补缺失值

    ---

    ### TPL-1402: 组合提取sigmoid
    ```
    模板: scale(group_extra(ts_sum(sigmoid(ts_backfill(<field/>, <d1/>)), <d2/>) - ts_sum(sigmoid(ts_backfill(<field/>, <d1/>)), <d2/>), 0.5, densify(industry)))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field/>` | 任意字段 | 数据字段 |
    | `<d1/>` | `180` | 回填窗口 |
    | `<d2/>` | `3` | 求和窗口 |

    ---

    ### TPL-1403: PnL反馈模板
    ```
    模板: if_else(inst_pnl(<alpha/>) > <threshold/>, <alpha/>, nan)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<alpha/>` | 主信号 | 原始Alpha |
    | `<threshold/>` | `0`, `-0.05` | PnL阈值 |

    **说明**: 基于单标的PnL进行条件交易

    ---

    ### TPL-1404: 流动性加权模板
    ```
    模板: <alpha/> * log(volume)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<alpha/>` | 主信号 | 原始Alpha |

    **说明**: 将仓位偏向高流动性股票

    ---

    ### TPL-1405: 市值回归中性化
    ```
    模板: regression_neut(<alpha/>, log(cap))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<alpha/>` | 主信号 | 原始Alpha |

    **说明**: 剥离市值因子影响

    ---

    ## 第十六部分：百分位与分位数模板 (TPL-1501 ~ TPL-1510)

    ### TPL-1501: 时序百分位模板
    ```
    模板: ts_percentage(<field/>, <d/>, percentage=<p/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field/>` | 任意字段 | 数据字段 |
    | `<d/>` | `22`, `66`, `126` | 窗口 |
    | `<p/>` | `0.5`, `0.25`, `0.75` | 百分位 |

    ---

    ### TPL-1502: 分位数模板
    ```
    模板: <ts_op/>(ts_quantile(<field/>, <d/>, <q/>), <d2/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<ts_op/>` | `rank`, `zscore` | 标准化 |
    | `<field/>` | 任意字段 | 数据字段 |
    | `<d/>` | `66`, `126` | 窗口 |
    | `<q/>` | `0.25`, `0.5`, `0.75` | 分位数 |
    | `<d2/>` | `22` | 操作窗口 |

    ---

    ### TPL-1503: Max-Min比率模板
    ```
    模板: ts_max_diff(<field/>, <d/>) / ts_av_diff(<field/>, <d/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field/>` | 任意字段 | 数据字段 |
    | `<d/>` | `22`, `66` | 窗口 |

    ---

    ### TPL-1504: 中位数模板
    ```
    模板: <field/> - ts_median(<field/>, <d/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<field/>` | 任意字段 | 数据字段 |
    | `<d/>` | `22`, `66`, `252` | 窗口 |

    ---

    ### TPL-1505: 累积乘积模板
    ```
    模板: ts_product(1 + <ret_field/>, <d/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<ret_field/>` | `returns`, 收益率字段 | 收益字段 |
    | `<d/>` | `5`, `22`, `66` | 窗口 |

    **说明**: 计算累积收益

    ---

    ## 第十七部分：实战表达式模板 (TPL-1601 ~ TPL-1700)

    **说明**: 以下模板从社区高票帖子中提取，为实际验证过的表达式格式。

    ### TPL-1601: ts_max/ts_min替代公式
    ```
    模板: {data} - ts_max_diff({data}, {d})                      # 等效于 ts_max
    模板: (({data} - ts_max_diff({data}, {d})) * ts_scale({data}, {d}) - {data}) / (ts_scale({data}, {d}) - 1)  # 等效于 ts_min
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{data}` | 任意MATRIX字段 | 数据字段 |
    | `{d}` | `22`, `66`, `126` | 窗口 |

    **应用**: 当平台不支持ts_max/ts_min时的替代方案

    ---

    ### TPL-1602: 线性衰减权重公式
    ```
    模板: weight = {d} + ts_step(0); ts_sum({data} * weight, {d}) / ts_sum(weight, {d})  # 等效于 ts_decay_linear
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{data}` | 任意字段 | 数据字段 |
    | `{d}` | `10`, `22`, `66` | 衰减窗口 |

    ---

    ### TPL-1603: 组归一化公式
    ```
    模板: {data} / group_sum(abs({data}), {group})  # 等效于 group_normalize
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{data}` | 任意字段 | 数据字段 |
    | `{group}` | `industry`, `sector` | 分组字段 |

    ---

    ### TPL-1604: IR+峰度组合模板
    ```
    模板:
    rank_data = rank({field});
    ts_ir(rank_data, {d}) + ts_kurtosis(rank_data, {d})
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{field}` | `volume`, `returns`, 任意字段 | 数据字段 |
    | `{d}` | `22`, `66` | 窗口 |

    **说明**: IR和峰度组合捕捉信号强度和分布特征

    ---

    ### TPL-1605: VWAP相关性信号
    ```
    模板: returns > -{threshold} ? (ts_ir(ts_corr(ts_returns(vwap, 1), ts_delay(group_neutralize({field}, market), {d1}), {d2}), {d2})) : -1
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{field}` | 任意数据字段 | 信号字段 |
    | `{threshold}` | `0.1`, `0.05` | 收益过滤阈值 |
    | `{d1}` | `30`, `60` | 延迟窗口 |
    | `{d2}` | `90`, `120` | 相关性窗口 |

    ---

    ### TPL-1606: 球队硬币因子 (ballteam_coin)
    ```
    模板:
    # 基础版
    rank(ballteam_coin)

    # 市值中性化版
    group_neutralize(rank(ballteam_coin), bucket(rank(assets), range='0.1,1,0.1'))
    ```
    **说明**: 经典球队vs硬币因子，用于捕捉收益持续性

    ---

    ### TPL-1607: 偏度因子模板
    ```
    模板: -group_rank(ts_skewness(returns, {d}), {group})
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{d}` | `22`, `66`, `126` | 偏度计算窗口 |
    | `{group}` | `sector`, `industry` | 分组 |

    **说明**: 负偏度股票往往表现更好

    ---

    ### TPL-1608: 熵信号模板
    ```
    模板: ts_zscore({field}, {d1}) * ts_entropy({field}, {d2})
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{field}` | `returns`, 任意字段 | 信号字段 |
    | `{d1}` | `14`, `22` | zscore窗口 |
    | `{d2}` | `14`, `22` | 熵窗口 |

    **说明**: 结合标准化和不确定性度量

    ---

    ### TPL-1609: 分析师动量短长差模板
    ```
    模板: log(ts_mean(anl4_{data}_{stats}, {d_short})) - log(ts_mean(anl4_{data}_{stats}, {d_long}))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{data}` | `eps`, `revenue`, `netprofit` | 分析师预测类型 |
    | `{stats}` | `mean`, `low`, `high` | 统计量类型 |
    | `{d_short}` | `20`, `44` | 短期窗口 |
    | `{d_long}` | `44`, `126` | 长期窗口 |

    ---

    ### TPL-1610: 目标换手率分组排名
    ```
    模板: -ts_mean(ts_target_tvr_hump(group_rank({field}, country), lambda_min=0, lambda_max=1, target_tvr={target}), {d})
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{field}` | 任意字段 | 数据字段 |
    | `{target}` | `0.1`, `0.15` | 目标换手率 |
    | `{d}` | `5`, `10` | 平均窗口 |

    ---

    ### TPL-1611: 最大差/均值差比率
    ```
    模板: ts_max_diff({field}, {d}) / ts_av_diff({field}, {d})
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{field}` | 任意字段 | 数据字段 |
    | `{d}` | `22`, `66` | 窗口 |

    **说明**: 捕捉极端值相对于平均变化的幅度

    ---

    ### TPL-1612: 模型数据三层嵌套
    ```
    模板:
    a = rank(group_rank(ts_rank(ts_backfill({model_field}, 5), 5), sta1_top3000c20));
    trade_when(rank(a) > 0.03, -zscore(ts_zscore({model_field}, 25)) * a, 0.25 - rank(a))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{model_field}` | `mdl175_01icc`, `mdl175_01dtsv` | 模型字段 |

    ---

    ### TPL-1613: 量价触发条件交易
    ```
    模板:
    triggerTradeexp = (ts_arg_max(volume, {d}) < 1) && (volume > ts_sum(volume, {d}) / {d});
    triggerExitexp = -1;
    alphaexp = -rank(ts_delta(close, 2));
    trade_when(triggerTradeexp, alphaexp, triggerExitexp)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{d}` | `5`, `10` | 窗口 |

    **说明**: 今日成交量为近期最大且高于均值时交易

    ---

    ### TPL-1614: 情绪成交量交易
    ```
    模板:
    sent_vol = vec_sum(scl12_alltype_buzzvec);
    trade_when(rank(sent_vol) > 0.95, -zscore(scl12_buzz) * sent_vol, -1)
    ```
    **说明**: 高情绪量时反向交易情绪

    ---

    ### TPL-1615: 双层中性化模板
    ```
    模板:
    a = ts_zscore({field}, 252);
    a1 = group_neutralize(a, industry);
    a2 = group_neutralize(a1, bucket(rank(cap), range='0.1,1,0.1'))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{field}` | 任意字段 | 数据字段 |

    **说明**: 先行业后市值的双重中性化

    ---

    ### TPL-1616: 相关性计算公式
    ```
    模板:
    a = {field1};
    b = {field2};
    p = {d};
    c = ts_mean(ts_av_diff(a, p) * ts_av_diff(b, p), p);
    c / ts_std_dev(a, p) / ts_std_dev(b, p)  # 近似 ts_corr
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{field1}` | `close`, `returns` | 第一字段 |
    | `{field2}` | `volume`, `open` | 第二字段 |
    | `{d}` | `5`, `22` | 窗口 |

    ---

    ### TPL-1617: 回归中性化双因子
    ```
    模板:
    afr = vec_avg({analyst_field});
    short_mom = ts_mean(returns - group_mean(returns, 1, market), {d_short});
    long_mom = ts_delay(ts_mean(returns - group_mean(returns, 1, market), {d_long}), {d_long});
    regression_neut(regression_neut(afr, short_mom), long_mom)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{analyst_field}` | 分析师VECTOR字段 | 分析师数据 |
    | `{d_short}` | `5`, `10` | 短期动量窗口 |
    | `{d_long}` | `20`, `22` | 长期动量窗口 |

    **说明**: 剥离短期和长期动量后的分析师因子

    ---

    ### TPL-1618: 回归斜率趋势检测
    ```
    模板: ts_regression(ts_zscore({field}, {d}), ts_step(1), {d}, rettype=2)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{field}` | 任意MATRIX字段 | 数据字段 |
    | `{d}` | `252`, `500` | 窗口 |

    **说明**: rettype=2返回回归斜率，检测长期趋势

    ---

    ### TPL-1619: 三因子乘积组合
    ```
    模板:
    my_group = market;
    rank(
    group_rank(ts_decay_linear(volume / ts_sum(volume, 252), 10), my_group) *
    group_rank(ts_rank(vec_avg({fundamental}), {d}), my_group) *
    group_rank(-ts_delta(close, 5), my_group)
    )
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{fundamental}` | 基本面VECTOR字段 | 基本面数据 |
    | `{d}` | `252`, `504` | 排名窗口 |

    **说明**: 成交量趋势 × 基本面排名 × 价格反转

    ---

    ### TPL-1620: 波动率条件反转
    ```
    模板:
    vol = ts_std_dev(returns, {d});
    vol_mean = group_mean(vol, 1, market);
    flip_ret = if_else(vol < vol_mean, -returns, returns);
    -ts_mean(flip_ret, {d})
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{d}` | `20`, `22` | 窗口 |

    **说明**: 低波动做反转，高波动做动量

    ---

    ### TPL-1621: 恐惧指标复合
    ```
    模板:
    fear = ts_mean(
    abs(returns - group_mean(returns, 1, market)) /
    (abs(returns) + abs(group_mean(returns, 1, market)) + 0.1),
    {d}
    );
    -group_neutralize(fear * {signal}, bucket(rank(cap), range='0.1,1,0.1'))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{d}` | `20`, `22` | 窗口 |
    | `{signal}` | 主信号 | 待组合信号 |

    ---

    ### TPL-1622: 财务质量单因子
    ```
    模板: group_neutralize(rank({fundamental_field}), bucket(rank(cap), range='0,1,0.1'))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{fundamental_field}` | `roe`, `roa`, `net_income/assets` | 财务质量指标 |

    ---

    ### TPL-1623: 老虎哥回归模板
    ```
    模板: group_rank(ts_regression(ts_zscore({field1}, {d}), ts_zscore(vec_sum({field2}), {d}), {d}), densify(sector))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{field1}` | 任意MATRIX字段 | Y变量 |
    | `{field2}` | 任意VECTOR字段 | X变量 |
    | `{d}` | `252`, `504` | 回归窗口 |

    ---

    ### TPL-1624: 综合数据清洗模板
    ```
    模板: ts_decay_linear(-densify(zscore(winsorize(ts_backfill({field}, 115), std=4))), 10)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{field}` | 低频字段如 `anl4_adjusted_netincome_ft` | 需要处理的字段 |

    ---

    ### TPL-1625: 延迟最大值位置模板
    ```
    模板: ts_max({field}, {d}) = ts_delay({field}, ts_arg_max({field}, {d}))  # 等效公式
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{field}` | 任意字段 | 数据字段 |
    | `{d}` | `22`, `66` | 窗口 |

    ---

    ### TPL-1626: 数据探索通用模板
    ```
    模板: zscore(ts_delta(rank(ts_zscore({field}, {d1})), {d2}))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{field}` | 任意MATRIX字段 | 待探索数据字段 |
    | `{d1}` | `60`, `126`, `252` | zscore窗口 |
    | `{d2}` | `5`, `10`, `22` | delta窗口 |

    **说明**: 顾问推荐的新数据探索模板，可替换op和时间参数

    ---

    ### TPL-1627: 自定义衰减权重模板
    ```
    模板:
    weight = {d} + ts_step(0);                       # 线性递增权重
    ts_sum({data} * weight, {d}) / ts_sum(weight, {d})  # 加权平均

    # 替代版 (ts_step递减)
    ts_sum({alpha} * ts_step(1), {d}) / ts_sum(ts_step(1), {d})
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{data}` | 任意字段 | 数据字段 |
    | `{alpha}` | 主信号 | 原始Alpha |
    | `{d}` | `10`, `22`, `66` | 衰减窗口 |

    **说明**: 当没有ts_decay_linear权限时的替代方案

    ---

    ### TPL-1628: log_diff相对增长模板
    ```
    模板: group_rank(log_diff({field}), {group})
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{field}` | 财务指标如 `sales`, `eps`, `assets` | 数据字段 |
    | `{group}` | `sector`, `industry` | 分组 |

    **说明**: 检测相对增长率，对乘性变化更敏感

    ---

    ### TPL-1629: ts_product累积收益模板
    ```
    模板: group_rank(ts_product(1 + {ret_field}, {d}), {group})
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{ret_field}` | `returns`, 收益率字段 | 收益字段 |
    | `{d}` | `22`, `66`, `126` | 窗口 |
    | `{group}` | `sector`, `industry` | 分组 |

    **说明**: 计算累积收益排名

    ---

    ### TPL-1630: ts_percentage阈值模板
    ```
    模板:
    high_threshold = ts_percentage({field}, {d}, percentage=0.5);
    low_threshold = ts_percentage({field}, {d}, percentage=0.5);
    {signal}
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{field}` | `close`, 价格字段 | 阈值计算字段 |
    | `{d}` | `22`, `66` | 窗口 |
    | `{signal}` | 主信号 | 条件信号 |

    **说明**: 用于震荡带突破策略的阈值构建

    ---

    ### TPL-1631: 动量反转切换模板
    ```
    模板:
    mom = ts_sum(returns, {d_long}) - ts_sum(returns, {d_short});
    reversal = -ts_delta(close, {d_short});
    if_else(ts_rank(ts_std_dev(returns, {d_short}), {d_long}) > 0.5, mom, reversal)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{d_short}` | `5`, `10` | 短期窗口 |
    | `{d_long}` | `22`, `66` | 长期窗口 |

    **说明**: 高波动环境用动量，低波动环境用反转

    ---

    ### TPL-1632: 市场收益率近似模板 (CHN)
    ```
    模板:
    value = rank(cap) > 0.9 ? cap : 0;
    market_return = group_sum(returns * value, country) / group_sum(value, country);
    market_return
    ```
    **说明**: 用市值加权近似沪深300指数收益率，设置neutralization=NONE, decay=0

    ---

    ### TPL-1633: Beta回归中性化模板
    ```
    模板:
    market_return = group_mean(returns, 1, market);
    ts_regression({field}, market_return, {d})  # 返回残差(Y - E[Y])
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{field}` | 任意MATRIX字段 | 待中性化字段 |
    | `{d}` | `126`, `252` | 回归窗口 |

    **说明**: 使用一元线性回归剥离市场因子

    ---

    ### TPL-1634: ts_moment高阶矩k值模板
    ```
    模板: ts_moment({field}, {d}, k={k})

    k=2: 方差 (等价于 ts_std_dev^2)
    k=3: 偏度 (等价于 ts_skewness)
    k=4: 峰度 (等价于 ts_kurtosis)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{field}` | 任意MATRIX字段 | 数据字段 |
    | `{d}` | `22`, `66`, `126` | 窗口 |
    | `{k}` | `2`, `3`, `4` | 阶数 |

    ---

    ### TPL-1635: 龙头股因子增强模板
    ```
    模板: sigmoid(rank(star_pm_global_rank))
    ```
    **说明**: 对龙头股因子进行sigmoid增强

    ---

    ### TPL-1636: purify数据清洗嵌套模板
    ```
    模板: group_rank(ts_rank(purify({field}), {d}), {group})
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{field}` | 任意字段 | 待清洗数据 |
    | `{d}` | `22`, `66` | 排名窗口 |
    | `{group}` | `sector`, `industry` | 分组 |

    **说明**: purify自动化清洗异常值和噪声

    ---

    ### TPL-1637: 理想振幅因子模板
    ```
    模板:
    amplitude = (high - low) / close;
    ideal_amp = ts_percentage(amplitude, {d}, percentage=0.5);
    group_rank(amplitude - ideal_amp, {group})
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{d}` | `22`, `66` | 百分位窗口 |
    | `{group}` | `sector`, `industry` | 分组 |

    **说明**: 实际振幅偏离理想振幅的程度

    ---

    ### TPL-1638: 异同离差乖离率因子 (MACD风格)
    ```
    模板:
    ema_short = ts_decay_exp_window({field}, {d_short}, 0.9);
    ema_long = ts_decay_exp_window({field}, {d_long}, 0.9);
    dif = ema_short - ema_long;
    ts_zscore(dif, {d_signal})
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{field}` | `close`, 价格字段 | 数据字段 |
    | `{d_short}` | `12`, `22` | 短期EMA窗口 |
    | `{d_long}` | `26`, `66` | 长期EMA窗口 |
    | `{d_signal}` | `9`, `22` | 信号线窗口 |

    ---

    ### TPL-1639: 收益率条件筛选反转
    ```
    模板:
    high_ret = ts_rank(returns, {d1}) > 0.8;
    low_ret = ts_rank(returns, {d1}) < 0.2;
    if_else(high_ret, -returns, if_else(low_ret, returns, 0))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{d1}` | `22`, `66` | 排名窗口 |

    **说明**: 只对极端收益做反转

    ---

    ### TPL-1640: 三阶模板优化版
    ```
    模板: <group_op/>(<ts_op1/>(<ts_op2/>(<field/>, <d1/>), <d2/>), <group/>)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `<group_op/>` | `group_rank`, `group_zscore` | 外层分组操作 |
    | `<ts_op1/>` | `ts_rank`, `ts_delta`, `ts_mean` | 中层时序操作 |
    | `<ts_op2/>` | `ts_zscore`, `ts_rank`, `ts_ir` | 内层时序操作 |
    | `<field/>` | 任意字段 | 数据字段 |
    | `<d1/>` | `60`, `126`, `252` | 内层窗口 |
    | `<d2/>` | `5`, `22`, `66` | 外层窗口 |
    | `<group/>` | `sector`, `industry` | 分组 |

    **说明**: 经典三阶嵌套结构，可灵活替换各层操作符

    ---

    ### TPL-1641: ts_entropy信号检测模板
    ```
    模板: ts_entropy({field}, {d})
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{field}` | `returns`, `volume`, 任意MATRIX字段 | 数据字段 |
    | `{d}` | `14`, `22`, `66` | 窗口 |

    **说明**: 衡量时序数据的不确定性，高熵值表示更多随机性

    ---

    ### TPL-1642: 熵+ZScore组合模板
    ```
    模板: ts_zscore({field}, {d}) * ts_entropy({field}, {d})
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{field}` | 任意MATRIX字段 | 数据字段 |
    | `{d}` | `14`, `22` | 窗口 |

    **说明**: RSI超买超卖 + 熵不确定性组合，捕捉可能的修正

    ---

    ### TPL-1643: ts_ir+ts_entropy信号组合
    ```
    模板:
    signal = ts_ir({field}, {d}) + ts_entropy({field}, {d});
    group_rank(signal, {group})
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{field}` | 任意MATRIX字段 | 数据字段 |
    | `{d}` | `22`, `66` | 窗口 |
    | `{group}` | `sector`, `industry` | 分组 |

    **说明**: IR(信息比率)和Entropy组合捕捉信号稳定性和分布特征

    ---

    ### TPL-1644: trade_when市值过滤模板
    ```
    模板: trade_when(rank(cap) > {threshold}, {alpha}, -1)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{threshold}` | `0.3`, `0.5`, `0.7` | 市值排名阈值 |
    | `{alpha}` | 主信号 | 原始Alpha |

    **说明**: 仅交易大市值股票，降低prod corr

    ---

    ### TPL-1645: trade_when盈利过滤模板
    ```
    模板: trade_when(eps > {threshold} * est_eps, group_rank((eps - est_eps)/est_eps, industry), -1)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{threshold}` | `1.0`, `1.1`, `1.2` | 盈利超预期比例 |

    **说明**: 只交易盈利超预期的股票

    ---

    ### TPL-1646: trade_when量价触发模板
    ```
    模板:
    triggerTrade = (ts_arg_max(volume, {d}) < 1) && (volume > ts_sum(volume, {d})/{d});
    trade_when(triggerTrade, {alpha}, -1)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{d}` | `5`, `10` | 判断窗口 |
    | `{alpha}` | `-rank(ts_delta(close, 2))` | 主信号 |

    **说明**: 量价突破触发条件交易

    ---

    ### TPL-1647: trade_when情绪量过滤模板
    ```
    模板:
    sent_vol = vec_sum({sentiment_vec});
    trade_when(rank(sent_vol) > {threshold}, -zscore({sentiment_field}) * sent_vol, -1)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{sentiment_vec}` | `scl12_alltype_buzzvec` 等VECTOR字段 | 情绪向量 |
    | `{sentiment_field}` | `scl12_buzz`, `scl12_sentiment` | 情绪字段 |
    | `{threshold}` | `0.9`, `0.95` | 情绪量阈值 |

    **说明**: 高情绪量时反向交易情绪

    ---

    ### TPL-1648: bucket市值分组中性化模板
    ```
    模板:
    my_group2 = bucket(rank(cap), range='{range}');
    group_neutralize({alpha}, my_group2)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{range}` | `'0,1,0.1'`, `'0.1,1,0.1'` | 分桶范围 |
    | `{alpha}` | 主信号 | 原始Alpha |

    **说明**: 按市值分桶进行中性化，去除规模效应

    ---

    ### TPL-1649: group_zscore时序组合模板
    ```
    模板: group_zscore(ts_ir({field}, {d}), {group})
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{field}` | 任意MATRIX字段 | 数据字段 |
    | `{d}` | `22`, `66`, `126` | IR窗口 |
    | `{group}` | `sector`, `industry` | 分组 |

    **说明**: 在分组内进行IR的Z-score标准化

    ---

    ### TPL-1650: scale+rank+ts组合模板
    ```
    模板: scale(rank(ts_zscore({field}, {d})))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{field}` | 任意MATRIX字段 | 数据字段 |
    | `{d}` | `66`, `126`, `252` | 窗口 |

    **说明**: 多层标准化处理信号

    ---

    ### TPL-1651: Betting Against Beta模板
    ```
    模板:
    market_return = group_mean(returns, 1, market);
    beta = ts_regression(returns, market_return, {d}, rettype=2);
    -group_rank(beta, industry)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{d}` | `126`, `252` | 回归窗口 |

    **说明**: 反Beta投注因子，做多低Beta股票

    ---

    ### TPL-1652: 跳跃因子模板
    ```
    模板:
    jump_up = ts_count(returns > ts_std_dev(returns, {d}) * {threshold}, {d});
    jump_down = ts_count(returns < -ts_std_dev(returns, {d}) * {threshold}, {d});
    group_rank(jump_down - jump_up, {group})
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{d}` | `22`, `66` | 统计窗口 |
    | `{threshold}` | `2`, `2.5`, `3` | 标准差倍数 |
    | `{group}` | `sector`, `industry` | 分组 |

    **说明**: 统计尾部跳跃事件的不对称性

    ---

    ### TPL-1653: 量小换手率模板
    ```
    模板:
    turnover = volume / sharesout;
    low_turnover = ts_percentage(turnover, {d}, percentage=0.2);
    group_rank(turnover < low_turnover, {group})
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{d}` | `22`, `66` | 百分位窗口 |
    | `{group}` | `sector`, `industry` | 分组 |

    **说明**: 识别低换手率状态

    ---

    ### TPL-1654: 隔夜收益因子模板
    ```
    模板:
    overnight_ret = open / ts_delay(close, 1) - 1;
    group_rank(ts_mean(overnight_ret, {d}), {group})
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{d}` | `5`, `22`, `66` | 平均窗口 |
    | `{group}` | `sector`, `industry` | 分组 |

    **说明**: 隔夜"拉锯战"因子

    ---

    ### TPL-1655: sta1分组三因子模板
    ```
    模板:
    a = rank(group_rank(ts_rank(ts_backfill({field1}, {d1}), {d2}), sta1_top3000c20));
    trade_when(rank(a) > {threshold}, -zscore(ts_zscore({field2}, {d3})) * a, {exit_threshold} - rank(a))
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{field1}` | 任意字段 | 第一因子字段 |
    | `{field2}` | 模型字段如`mdl175_01dtsv` | 第二因子字段 |
    | `{d1}`, `{d2}`, `{d3}` | 各窗口参数 | 时间窗口 |
    | `{threshold}` | `0.03`, `0.1` | 入场阈值 |
    | `{exit_threshold}` | `0.25`, `0.5` | 出场阈值 |

    **说明**: 使用sta1预定义分组的复合策略

    ---

    ### TPL-1656: macro泛化模板
    ```
    模板: group_rank(ts_delta(ts_zscore({macro_field}, {d1}), {d2}), country)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{macro_field}` | 宏观数据字段 | 宏观数据 |
    | `{d1}` | `126`, `252` | zscore窗口 |
    | `{d2}` | `5`, `22` | delta窗口 |

    **说明**: 基于Labs分析macro的泛化模板

    ---

    ### TPL-1657: ASI broker模板
    ```
    模板:
    signal = group_rank(ts_rank({broker_field}, {d}), market);
    trade_when(volume > adv20, signal, -1)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{broker_field}` | broker数据字段 | 券商数据 |
    | `{d}` | `22`, `66` | 排名窗口 |

    **说明**: ASI区域broker因子，需设置max_trade=ON

    ---

    ### TPL-1658: Earnings超预期模板
    ```
    模板:
    surprise = (actual_eps - est_eps) / abs(est_eps);
    group_rank(ts_zscore(surprise, {d}), industry)
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{d}` | `66`, `126` | zscore窗口 |

    **说明**: 盈利超预期因子

    ---

    ### TPL-1659: CCI技术指标模板
    ```
    模板:
    tp = (high + low + close) / 3;
    cci = (tp - ts_mean(tp, {d})) / (0.015 * ts_mean(abs(tp - ts_mean(tp, {d})), {d}));
    group_rank(-cci, {group})
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{d}` | `14`, `20` | CCI窗口 |
    | `{group}` | `sector`, `industry` | 分组 |

    **说明**: 商品通道指数(CCI)反转策略

    ---

    ### TPL-1660: 0.618黄金比例幂变换模板
    ```
    模板:
    power_signal = signed_power({field}, 0.618);
    group_rank(ts_zscore(power_signal, {d}), {group})
    ```
    | 占位符 | 可选值 | 说明 |
    |--------|--------|------|
    | `{field}` | 任意MATRIX字段 | 数据字段 |
    | `{d}` | `66`, `126` | zscore窗口 |
    | `{group}` | `sector`, `industry` | 分组 |

    **说明**: 使用黄金比例0.618进行幂次变换

    ---

    ## 附录A：标准时间窗口

    | 窗口代号 | 天数 | 含义 |
    |---------|------|------|
    | `d_week` | 5 | 一周 |
    | `d_month` | 22 | 一月 |
    | `d_quarter` | 66 | 一季度 |
    | `d_half` | 126 | 半年 |
    | `d_year` | 252 | 一年 |
    | `d_2year` | 504 | 两年 |

    **使用规则**:
    - 反转因子: 短窗口 `{3, 5, 22}`
    - 动量因子: 中窗口 `{22, 66}`
    - 长期趋势: 长窗口 `{126, 252, 504}`
    - 回归/波动: 超长窗口 `{250, 500, 750}`

    ---

    ## 附录B：常用操作符分类

    ### 时序操作符 `<ts_op/>`
    | 操作符 | 用途 |
    |--------|------|
    | `ts_mean` | 移动平均 |
    | `ts_rank` | 时序排名 |
    | `ts_delta` | 差分 |
    | `ts_std_dev` | 移动标准差 |
    | `ts_ir` | 信息比率 |
    | `ts_zscore` | 时序Z-score |
    | `ts_corr` | 滚动相关性 |
    | `ts_regression` | 滚动回归 |
    | `ts_decay_linear` | 线性衰减 |
    | `ts_decay_exp_window` | 指数衰减 |
    | `ts_sum` | 滚动求和 |
    | `ts_backfill` | 数据回填 |
    | `ts_arg_min` | 最小值位置 |
    | `ts_arg_max` | 最大值位置 |
    | `ts_max` | 滚动最大值 |
    | `ts_min` | 滚动最小值 |
    | `ts_delay` | 延迟 |
    | `ts_moment` | k阶中心矩 |
    | `ts_co_skewness` | 协偏度 |
    | `ts_co_kurtosis` | 协峰度 |
    | `ts_partial_corr` | 偏相关 |
    | `ts_triple_corr` | 三元相关 |
    | `ts_theilsen` | Theil-Sen回归 |
    | `ts_poly_regression` | 多项式回归残差 |
    | `ts_vector_neut` | 向量中性化 |
    | `ts_weighted_decay` | 加权衰减 |
    | `ts_min_max_cps` | 最小最大压缩 |
    | `ts_max_diff` | 与最大值差 |
    | `ts_av_diff` | 与均值差 |
    | `ts_quantile` | 分位数 |
    | `ts_percentage` | 百分位 |
    | `ts_median` | 中位数 |
    | `ts_product` | 累积乘积 |
    | `ts_count_nans` | NaN计数 |
    | `ts_scale` | 时序缩放 |
    | `ts_target_tvr_hump` | 目标换手率Hump |
    | `ts_target_tvr_delta_limit` | Delta换手率限制 |

    ### 分组操作符 `<group_op/>`
    | 操作符 | 用途 |
    |--------|------|
    | `group_rank` | 分组排名 |
    | `group_neutralize` | 分组中性化 |
    | `group_zscore` | 分组Z-score |
    | `group_mean` | 分组均值 |
    | `group_sum` | 分组求和 |
    | `group_extra` | 分组提取/填补 |
    | `group_backfill` | 分组回填 |
    | `group_normalize` | 分组归一化 |
    | `group_vector_neut` | 分组向量中性化 |
    | `group_vector_proj` | 分组向量投影 |
    | `group_count` | 分组计数 |
    | `group_std_dev` | 分组标准差 |

    ### 向量操作符 `<vec_op/>`
    | 操作符 | 用途 |
    |--------|------|
    | `vec_avg` | 向量平均 |
    | `vec_sum` | 向量求和 |
    | `vec_max` | 向量最大 |
    | `vec_min` | 向量最小 |
    | `vec_stddev` | 向量标准差 |
    | `vec_count` | 向量计数 |
    | `vec_norm` | 向量归一化 |
    | `vec_zscore` | 向量Z-score |
    | `vec_range` | 向量范围 |

    ### 事件/时间操作符
    | 操作符 | 用途 |
    |--------|------|
    | `days_from_last_change` | 距离上次变化天数 |
    | `last_diff_value` | 最近不同值 |
    | `ts_step` | 时间步长 |

    ### 信号处理操作符
    | 操作符 | 用途 |
    |--------|------|
    | `signed_power` | 带符号幂变换 |
    | `clamp` | 边界限制 |
    | `left_tail` | 左尾截断 |
    | `right_tail` | 右尾截断 |
    | `fraction` | 分数映射 |
    | `nan_out` | NaN外推 |
    | `purify` | 数据清洗 |
    | `keep` | 条件保留 |
    | `scale_down` | 缩放降维 |
    | `hump` | Hump平滑 |
    | `hump_decay` | Hump衰减 |

    ### 其他常用操作符
    | 操作符 | 用途 |
    |--------|------|
    | `rank` | 截面排名 |
    | `zscore` | 截面Z-score |
    | `sigmoid` | Sigmoid归一化 |
    | `winsorize` | 极端值截断 |
    | `truncate` | 截断 |
    | `tail` | 尾部处理 |
    | `scale` | 缩放 |
    | `filter` | 过滤 |
    | `densify` | 稠密化 |
    | `bucket` | 分桶 |
    | `log` | 对数 |
    | `abs` | 绝对值 |
    | `if_else` | 条件判断 |
    | `trade_when` | 条件交易 |
    | `regression_neut` | 回归中性化 |
    | `regression_proj` | 回归投影 |
    | `is_nan` | NaN检测 |
    | `is_not_nan` | 非NaN检测 |
    | `inst_pnl` | 单标的PnL |
    | `convert` | 单位转换 |
    | `pasteurize` | 去无效值 |

    ---

    ## 附录C：数据字段分类

    ### 量价类 `<pv_field/>`
    ```
    close, open, high, low, vwap
    returns, volume, adv20, sharesout, cap
    ```

    ### 基本面类 `<fundamental_field/>`
    ```
    assets, sales, ebitda, net_income, eps, operating_income
    goodwill, debt, cash, equity, gross_profit
    fnd6_*, fnd72_*, mdl175_*, mdl163_*
    debt_to_equity, roe, roa
    ```

    ### 分析师类 `<analyst_field/>` (VECTOR)
    ```
    anl4_eps_mean, anl4_eps_low, anl4_eps_high
    anl4_revenue_mean, anl4_fcf_value, anl4_netprofit_mean
    anl4_adjusted_netincome_ft, anl4_bvps_flag
    oth41_s_west_*, analyst_*
    ```

    ### 情绪类 `<sentiment_field/>`
    ```
    scl12_sentiment, scl12_buzz, scl12_alltype_buzzvec
    snt_value, snt_buzz, snt_buzz_ret, snt_buzz_bfl
    nws18_relevance, nws18_ber
    nws12_prez_result2, nws12_prez_short_interest
    mws85_sentiment, mws46_mcv
    ```

    ### 期权类 `<option_field/>`
    ```
    option8_*, option14_*
    implied_volatility_call_120, implied_volatility_call_270
    parkinson_volatility_120, parkinson_volatility_270
    pcr_vol_10, pcr_vol_30
    put_delta, call_delta, put_gamma, call_gamma
    put_theta, call_theta, put_vega, call_vega
    call_breakeven_10, put_breakeven_10
    ```

    ### 模型类 `<model_field/>`
    ```
    mdl175_01dtsv, mdl175_01icc
    mdl163_*, mdl*
    ```

    ### 分组类 `<group/>`
    ```
    industry, sector, subindustry
    market, country, exchange
    sta1_top3000c20, sta1_*
    pv13_*, pv27_*
    ```