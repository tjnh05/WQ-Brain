How to smooth the PnL curve to minimize sudden fluctuations?
 NL41370
2 years ago ~3 minute read
Not yet followed by anyone
There can be some reasons for sudden jumps:

Because the Alpha values are frequently changing from NaN to non-NaN or vice versa. You can use backfill function to take care of this.
The other reason is that the Alpha values change rapidly from time to time. Thus decay or taking average in Alpha formula can help you in making the curve smoother.
It also may be because of too much money on one stock and if the stock value has a jump then the PNL will also have a jump in it. To tackle this you can set stock weight (Truncation) in sim settings to non-zero value between 0 and 1, preferably less than 0.1.
Encountering fluctuating results while researching Alphas is common. Sometimes, Alphas may show poor performance (dips in PNL) in specific years, which can be confusing. You can improve your Alpha's performance by looking not just at the in-sample (IS) summary section but also the year-by-year results (under the ‘Aggregate Data’). Here are some tips:

Why do performance dips happen?
When Alphas show frequent poor performance, they might pose a greater risk in the future
A decline in the PnL chart over a few years (image below) can be a warning sign for your Alpha’s robustness and OS performance
This decline could be due to:
Random noise or overfitting
The Alpha being used by many quants, making it unviable
Major events like the COVID-19 crash in 2020, could also affect Alpha performance if the Alpha is not robust.
If an Alpha performs poorly during the in-sample period, it's generally safer not to utilize it. This is why the IS-ladder test is one of the consultant submission tests. 
How to improve dips in the in-sample period?
To address the dip in specific years, consider eliminating risks not associated with your main Alpha idea.
If your Alpha idea is strong, but the Alpha is volatile and less robust during certain periods, try neutralizing these risks. For example, if you want to assign more weight on stocks with high ROE, remember that ROE can differ by industry: internet service companies may have higher ROE than manufacturing companies. Then, a decline in internet service industry might severely impact your Alpha. So, neutralizing these risks can be one of the solutions to remove temporal poor performance.
Here are some ways to neutralize:
Neutralization option in the settings
Besides Market to Subindustry neutralization, try using Slow factors and Fast factors.
Neutralizing operators
Group_neutralize, group_rank or group_zscore operators
Vector_neut operator
Regression_neut operator
Ts_vector_neut operator
Other types of dips/spikes issues
If your turnover chart shows short-period spikes, this could be due to using datafields with low coverage. See the example below.



If the low coverage datafields lack some data at certain timestamps, the Alpha using this datafield would change all its positions. This situation may result in a large reduction in coverage for these days, causing the Alpha to fail the concentrated weight test. To tackle this, try filling operators like ts_backfill or group_backfill to lower spiking turnover and prevent low coverage.