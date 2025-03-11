FORMULAS = [
"group_neutralize(power(rank(assets - group_mean(assets, 1, subindustry)), 3), bucket(rank(cap), range='0,1,0.1'))",
{"delay": 1, "decay": 10, "neutralization": "SECTOR", "truncation": 0.01, "pasteurization": "ON", "unitHandling": "VERIFY", "nanHandling": "OFF", "language": "FASTEXPR", "visualization": False, "regular": "trade_when(pcr_oi_270 < 1, implied_volatility_call_270-implied_volatility_put_270, -1)"},
]