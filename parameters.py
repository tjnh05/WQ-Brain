from commands import *

# Just a sample
DATA = [{
    'neutralization': 'SUBINDUSTRY',
    'decay': 10,
    'truncation': 0.1,
    'delay': 1,
    'universe': 'TOP3000',
    'region': 'USA',
    'code': '(rank(ts_arg_max(signed_power(((returns < 0) ? ts_std_dev(returns, 20) : close), 2.), 5)) -0.5)'
}]
