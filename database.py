PRICES = [
    'open', 'high', 'low', 'close',
    'vwap', 'returns'
]

PRICES += ['adj_close']  # 增加复权价格

VOLUMES = [
    'volume', 'adv20', 'cap'
]

one_OP_one = [
    '+', '-', '*', '/', '^'
]

OP_one = [
    '', 'rank', 'sigmoid', 'exp',
    'fraction', 'log', 'log_diff', 'scale',
    'zscore'
]

UNARY_OP = ['', '-']

TS_OP_1D1P = [
    'ts_product', 'ts_std_dev', 'ts_rank',
    'ts_sum', 'ts_av_diff', 'ts_arg_max',
    'ts_decay_linear', 'ts_delay', 'ts_delta',
]

TS_OP_1D1P += ['ts_mean', 'ts_std', 'ts_max']  # 扩展时间序列操作符

TS_OP_1D2P = [
    'ts_corr'
]

GROUP_OP_1D1P = [
    'group_zscore', 'group_rank',
]

GROUP_OP_1D1P += ['group_mean']

GROUP_DT = [
    'market', 'sector', 'industry', 'subindustry'
]

P_or_M = [
    '', '-'
]

DEAL_WITH_WEIGHT = [
    'rank', 'sigmoid', ''
]

IF_ELSE = [
    '?', ':'
]

CONDITION = [
    '>', '<', '='
]

# 新增情绪数据字段
SENTIMENT_FEATURES = ['news_sentiment', 'social_volume']

# 根据实际支持的算子补充
# 支持的算子
VALID_OPERATORS = {
    'group_neutralize', 'ts_mean',
    'rank', 'ts_corr', 'ts_std_dev', 'ts_arg_max', 'signed_power',
    'log', 'ts_delta',
    'ts_sum', 'ts_std', 'ts_av_diff',
    'ts_decay_linear', 'ts_delay', 'ts_product', 'ts_scale',
    'ts_zscore', 'ts_rank', 'Ts_Rank', 'group_zscore', 'group_rank', 'group_mean',
    'group_max', 'abs', 'sign', 'ts_covariance', 'ts_step',
    'scale', 'min', 'max', 'Sign', 'Log', 'ts_arg_min', 'trade_when',
    'last_diff_value', 'ts_regression', 'power', 'if'
}

BLACKLIST_OPERATORS = {
    'pasteurize', 'sigmoid', 'ts_max', 'ts_min',
}