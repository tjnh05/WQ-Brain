操作符研究之tail家族
Followed by 5 people

SJ65808
GrandMaster consultant
2 days ago
在WQ平台中left_tail, right_tail 和 tail三个相近的操作符，都是用来处理尾部数据的操作符，具体说明如下图所示：



从函数说明中可以看到这几个操作符都需要相关的最大值、最小值等参数，但是实际数据字段的取值范围在没有仔细探查之前是无从得知的，也就没有办法设定相关的参数了。但是平台中的rank类函数(rank,ts_rank、group_rank)可以将数据压缩到[0,1]这一区间，因此这两类函数连用往往能起到意想不到的的妙处

left_tail(rank(close), maximum = 0.02)
left_tail(ts_rank(close,120), maximum = 0.02)
left_tail(group_rank(close,industry), maximum = 0.02)

此外，通过操作符说明可以发现这几个操作之间是可以相互替换的，具体关系如下

tai(x,lower =0 ,upper =0.2 ,newval=nan) = left_tail(x,maximum = 0.2)
tai(x,lower =0.2 ,upper =1 ,newval=nan) = right_tail(x,minimum = 0.2)
其中x的取值范围是[0,1]