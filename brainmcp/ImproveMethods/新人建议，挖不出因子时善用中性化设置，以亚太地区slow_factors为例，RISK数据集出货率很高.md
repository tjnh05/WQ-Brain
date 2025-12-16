新人建议，挖不出因子时善用中性化设置，以亚太地区slow_factors为例，RISK数据集出货率很高
Followed by 19 people

XW35731
Gold consultant
1 month ago
第一次发帖有点不知道该说什么，怕老人看了觉得内容太简单在灌水，又怕新人看了我的描述一头雾水。就讲讲我目前每天挖因子的流程吧，以及我的心路历程（不知道为什么发不了图，就用文字和代码描述了）

最开始还是用户阶段的时候，因为没有登录论坛不知道原来还可以用api挖因子，我挖因子都是手动写的逻辑因子（这点还是很有前途的，我打算用mcp重构逻辑因子），当时很爱用量价因子算和各个因子的相关性，并且这个相关性很多时候都可以作为alpha提交，但作为正式顾问开始提交因子后遇到一个麻烦，这种操作符大于8个或者使用数据类型大于3个的因子会比之前严格很多，而且因为我之前用户阶段提交了快200个这种因子，现在重新开始提交时不仅会和我自己的因子算相关性，并且还会和池子里其他顾问提交的因子算相关性，并且一个数据集用多了还会被ban，我果断放弃了用了很久的usa的量价数据。当时那天我特别迷茫，陷入了没有因子可交的阶段。

后面刷论坛帖子，不仅看到了可以使用api批量回测，而且如果提交Power Pool Alpha 要求会比之前宽容很多，夏普提交只需要满足大于1，后两年的夏普大于1，并且fitness没有要求，于是我开始了批量回测提交Power Pool Alpha的路。

由于上周的主题是ASI双倍因子的活动，并且要求风格中性化，于是我直接设定回测时使用SLOW(毕竟所有因子表现都要看样本外，低换手率还是很重要的），开始从ASI地区开始刷alpha。模板是我总结的，对因子本身，一阶，二阶,以及斜率作为alpha模板开始

'factor'
rank('factor')
rank(ts_delta('factor',7))
rank(ts_delta('factor',30))
rank(ts_delta('factor',90))
rank(ts_regression(ts_zscore('factor', 7), ts_step(1), 7, rettype=2))
rank(ts_regression(ts_zscore('factor', 30), ts_step(1), 30, rettype=2))
rank(ts_regression(ts_zscore('factor', 90), ts_step(1), 90, rettype=2))
可能是因为目前用slow_factors这种风格中性化的顾问还比较少，每个数据集每天我都能提交三个alpha，而且在ASI地区我提交了挺多和池子里相关性小于0.6的alpha，并且在risk这个数据集里尤为明显，非常建议新人一起试试