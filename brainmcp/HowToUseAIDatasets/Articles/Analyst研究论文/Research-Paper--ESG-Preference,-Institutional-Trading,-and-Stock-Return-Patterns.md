# Research Paper: ESG Preference, Institutional Trading, and Stock Return Patterns

## 文章信息
- **文章ID**: 14603831291415-Research-Paper-ESG-Preference-Institutional-Trading-and-Stock-Return-Patterns
- **分类**: Analyst研究论文
- **URL**: https://support.worldquantbrain.com/hc/en-us/community/posts/14603831291415-Research-Paper-ESG-Preference-Institutional-Trading-and-Stock-Return-Patterns

## 内容
Research Paper: ESG Preference, Institutional Trading, and Stock Return Patterns Pinned
Followed by 18 people

KA64574
2 months ago
Abstract:

Socially responsible (SR) institutions tend to focus more on the ESG performance and less on quantitative signals of value. Consistent with this difference in focus, we find that SR institutions react less to quantitative mispricing signals. Our evidence suggests that the increased focus on ESG may have influenced stock return patterns. Specifically, abnormal returns associated with these mispricing signals are greater for stocks held more by SR institutions. The link between SR ownership and the efficacy of mispricing signals only emerges in recent years with the rise of ESG investing, and is significant only when there are arbitrage-related funding constraints.

Key ideas:

Page 5 paragraph 2
Page 14 paragraph 2
Page 24 paragraph 3
 

Useful datafields on BRAIN:

Term

Datafield

Dataset

stock

mdl7_price

Model7

shares held by institutions

mdf_fnd

Fundamental12

esg score

anl11_2_gse

Analyst11

Institutional ownership

mdl10_inst_ownership

Model10

 

Author: Jie (Jay) Cao, Sheridan Titman, Xintong (Eunice) Zhan Weiming (Elaine) Zhang

Year : 2021

Link: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3353623


19
Comments
1 commentSort by 

TN67143
Expert consultant
1 year ago
Hi,

From the abstract of this paper, can we look at them in the following ways?

1. First, From the third sentence of the paragraph: Our evidence suggests that the increased focus on ESG may have influenced stock return patterns. It may be inferred from this sentence that the author find some causal/influential relations between [the increased focus on ESG] and [stock returns patterns].

We can realized [the increased focus on ESG] with datafield anl11_2_gse (esg score) and operator ts_delta that measures the change in the specified datafields, with the formula: ts_delta(anl11_2_gse, t).

To reflect the causal/influential relations between these two index, we can use correlation-related operators (such as ts_corr,...) and regression-related operators (such as ts_regression,...).

2. From the fourth sentence: Specifically, abnormal returns associated with these mispricing signals are greater for stocks held more by SR institutions. This may means that the above effects, influential relations are conditioned on/magnified by/correlated with the stocks shares held by SR institutions.

To realize this phenomenon, we shall use the datafield mdl10_inst_ownership (institutional ownership).

We can either use * operator: mdl10_inst_ownership*anl11_2_gse to reflect the institutional ownership of the ESG institution.

Or We can use condition: When mdl_inst_ownership (institutional ownership) > a threshold, trade according to our alpha formula (ts_corr(anl11_2_gse, mdl17_price, t) and vice versa)).

Or we can simply use a correlation class (ts_corr(),...) operators of mdl_inst_ownership (institutional ownsership) with the brief alpha formula above to reflect their association relationship.

What do you think about the above process?

Thank you.


19

Post is closed for comments.
Didn't find what you were looking for?
