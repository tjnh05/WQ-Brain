机缘巧合下发现了一些适用IND的优化方法，对其他Region的适用性可能不够强，但也可以作为一定程度的参考吧

注：以下将weight concentration简称为wc

- 建议的默认setting配置：

Neutralization: MARKET
Max trade: OFF
 
从个人回测和提交结果看，market的出货率最高，切换其他neut后更容易出现wc问题或Robust Sharpe偏低，以及更低的IS指标，小概率能发现其他neut可能存在较低的相关性，因此只在最终优化阶段才尝试；
Max trade一般也会带来wc问题，即使是IS较高，打开后指标基本不变的alpha，甚至略有提升的alpha，也会产生wc10-wc15的fail，或叠加Robust Sharpe fail而导致无法提交的情况，如果wc能放宽到15，或许打开max能有很多可提交的alpha(doge)
 
- 通用手搓法：
1.反转信号：https://support.worldquantbrain.com/hc/zh-cn/community/posts/35698887416983--%E5%93%A5%E5%B8%83%E6%9E%97-%E6%9D%82%E8%AE%BA1-%E5%85%B3%E4%BA%8Esetting%E9%85%8D%E7%BD%AE%E5%92%8Cops%E9%80%89%E6%8B%A9%E4%BD%BF%E7%94%A8%E6%96%B9%E9%9D%A2%E7%9A%84%E4%B8%AA%E4%BA%BA%E7%BB%8F%E9%AA%8C 
2.ts系列时间参数选用：fnd数据使用长期回溯起步(例如252)，非fnd数据使用短期回溯起步(例如5)
3.group系列分组参数选用：遍历sector, industry, subindustry和pv系的50分组，即分组命名中带50的分组，此类分组一旦有一个存在信号，其余同类分组必定存在相对更强或较弱的信号范围，因此初步尝试时无需全部遍历
4.ops选用：仅使用一元运算符。遍历所有可用的一元运算符，专注于探索该数据的运算关系；出现高turnover时，再考虑使用能降turnover的二元运算符
5.哥布林鲁棒：即对目前使用的运算符做A(n)全排序。当使用2个以上运算符时，可尝试使用此法遍历，小概率可获得相关性更低的alpha，也有可能同时提升IS指标
6.使用自相似的表达式构建，即在相邻层或间隔层再次使用相同的运算符，达成在更小的颗粒度尝试提升指标且不拉伸六维的目的，例如经典的加速度模板ts_delta(ts_delta(x, d), d)
 
- 如何有效解决wc问题
1.降低truncation，非常适用IND，往往能发现越低的truncation，IS指标会越高
2.通过ts_mean/ts_median/ts_sum这几种统计层面的时序运算符规避wc，理论上回溯时间越长wc越低，但IS指标可能会急剧下降
3.增大ts运算符的时间参数
4.略微提升decay+微调truncation
5.使用group_neutralize + pv分组或bucket组合一些特别的分组
6.对fnd数据可尝试使用group_mean，分组参数可尝试market以外的所有分组
 
- 其他的细节
1.在IND中，None的中性化似乎相较其他region具有更强的适用性
2.Robust Sharpe <= 0.5的可直接放弃，其优化上限大概率无法达到1.0
3.当wc的fail提示出现wc50，wc100甚至wc too strong，其实并不意味着无法解决，许多时候使用一个ts_mean就可以降低到正常水平，若同时组合使用了几种方法仍然出现wc too strong，才可能真正说明它存在严重的wc问题
4.当Sector呈现wc问题时，Industry和Subindustry大概率会产生更高的wc问题
5.IND似乎不大适用Sector + Subindustry这种双重中性化的组合
6.IND存在一个天然优势，所有类型的pyramid都是1.5，那么就可以将所有类型的数据集都基于genius的规则两两组合，在相当程度上助力了出货的可能性，而不必像其余region只能对相同pyramid的进行组合，对不同类型的数据可能性研究十分有限，在数据集本身上的局限性也较大