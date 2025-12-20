【Alpha模版】模版群助我60天点亮60个塔 Alpha Template
Followed by 130 people

LR93609
GrandMaster consultant
2 months ago
一、前言

我是一位freshman，7月1日转正，至今提交295个atom，点亮64座塔。







二、方法论

1. 经济学原理是静态框架，而股市运行于人性的动态博弈之中。  
2. 任何超额收益（Alpha）一旦被广泛追逐，便会因拥挤而失效。  
3. 故兵无常势，水无常形，唯有因时应变者，方能持续制胜。

具体做法：

1. 穷举所有：挑选可用的模版。比如，一元、二元或三元模版

2. 避免重复：从模版层降低相关性。比如scale、rank、zscore等单操作符模版，多数情况下是重复的，不要堆叠，浪费回测资源。

3. 先随机再深入：首先，对准一个想要点亮的数据集；先用shuffle的方法，随机取样80个组合，计算每个模版的因子密度；如果某个模版因子密度大，就深入挖掘。

参考虎哥模版实证及其改进效果评价

三、模版框架（举例）

1. 一元模版（模版层面尽量不要有重复，从模版底层降低self-corr）

for a in data_fields:
    if index == 0:
        # 斜率
        expr = f"ts_regression(ts_zscore({a}, 500), ts_step(1), 500, rettype=2)"
        factor_expressions.append(expr)
    elif index == 1:
        # 增长率
        expr = f"ts_delta(ts_delta({a}, 252)/ts_delay({a}, 252),252)"
        factor_expressions.append(expr)
    elif index == 2:
        # 增长率
        expr = f"ts_delta({a}, 252)/ts_delay({a}, 252)"
        factor_expressions.append(expr)
    elif index == 3:
        # 自回归斜率
        expr = f"ts_regression(ts_delta({a}, 252), ts_delta({a}, 500), 500, rettype=2)"
        factor_expressions.append(expr)
    elif index == 4:
        # 平方动量
        expr = f"ts_mean(signed_power(ts_delta({a}, 252), 2), 500)"
        factor_expressions.append(expr)
    elif index == 5:
        # 衰减加权动量
        expr = f"ts_decay_linear(ts_delta({a}, 252), 500)"
        factor_expressions.append(expr)
    elif index == 6:
        # 排名反转
        expr = f"reverse(ts_rank(ts_zscore({a}, 500), 500))"
        factor_expressions.append(expr)
    elif index == 7:
        # 对数平滑
        expr = f"log(abs(ts_delta({a}, 500)) + 0.000001)"
        factor_expressions.append(expr)
    elif index == 8:
        # 符号保留幂
        expr = f"signed_power(ts_delta({a}, 500), 2)"
        factor_expressions.append(expr)
    elif index == 9:
        # 差分层叠
        expr = f"ts_delta(ts_delta({a}, 252), 500)"
        factor_expressions.append(expr)
2. 二元模版（降self-corr）

    for a, b in combinations(data_fields, 2):
        if index == 0:
            expr = f"ts_regression(ts_zscore({a}, 500), ts_zscore({b}, 500), 500)"
            factor_expressions.append(expr)
        elif index == 1:
            expr = f"ts_regression(ts_zscore({a}, 500), ts_zscore({b}, 500), 500, rettype=2)"
            factor_expressions.append(expr)
        elif index == 2:
            expr = f"ts_regression(ts_zscore({a}, 500), ts_zscore({b}, 500), 500, rettype=6)"
            factor_expressions.append(expr)
        elif index == 3:
            expr = f"ts_regression({a}, {b}, 252, rettype=2)"
            factor_expressions.append(expr)
        elif index == 4:
            expr = f"ts_regression({a}, {b}, 500, rettype=2)"
            factor_expressions.append(expr)
        elif index == 5:
            expr = f"regression_neut(s_log_1p({a}), s_log_1p({b}))"
            factor_expressions.append(expr)
        elif index == 6:
            expr = f"vector_neut({a}, {b})"
            factor_expressions.append(expr)
        elif index == 7:
            expr = f"ts_delta_limit({a}, {b}, limit_volume=0.1)"
            factor_expressions.append(expr)
        else:
            continue
3. 三元模版（去self-corr）

    for a, b, c in combinations(data_fields, 3):
        if index == 0:
            # 联合中性化：a 在 b 和 c 上的向量正交
            expr = f"vector_neut(vector_neut({a}, {b}), {c})"
        elif index == 1:
            # 分层回归残差（先对 b 中性化，再对 c）
            expr = f"regression_neut(regression_neut({a}, {b}), {c})"
        elif index == 2:
            # 带约束的时序变化（delta limit，以 b 和 c 的均值为基准）
            expr = f"ts_delta_limit({a}, ({b} + {c}) / 2, limit_volume=0.1)"
        elif index == 3:
            # 三变量时序相关性（a 与 b 的相关性，用 c 作权重或窗口调节）
            expr = f"ts_corr(ts_zscore({a}, 252), ts_zscore({b}, 252), 252) * {c}"
        elif index == 4:
            # 动态排序择时（a 在 b 和 c 构成的分组中做 ts_rank）
            expr = f"ts_rank(group_mean({a}, {b}), 500) * {c}"  # 假设 b 为分组字段
        elif index == 5:
            # 三重交互项（非线性放大）
            expr = f"ts_zscore({a}, 500) * ts_zscore({b}, 500) * ts_zscore({c}, 500)"
        elif index == 6:
            # 条件切换（c 为条件，选择 a 或 b）
            expr = f"if_else({c} > ts_mean({c}, 500), {a}, {b})"
        else:
            continue  # 超出范围跳过
四、应用举例（CHN很难，但实际上也扛不住几次冲锋，突破只是时间问题）

1.analyst举例

2. fundamental举例



3. model举例

4. pv举例



五、总结（任正非同志的经典语录——与君共勉）

“华为坚定不移28年只对准通信领域这个‘城墙口’冲锋。我们成长起来后，坚持只做一件事，在一个方面做大。华为只有几十人的时候就对着一个‘城墙口’进攻，几百人、几万人的时候也是对着这个‘城墙口’进攻，现在十几万人还是对着这个‘城墙口’冲锋。密集炮火，饱和攻击。” 