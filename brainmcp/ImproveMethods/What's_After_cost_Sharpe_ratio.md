What's After cost Sharpe ratio?
 SH71033
1 year ago ~1 minute read
Not yet followed by anyone
The "After-cost Sharpe ratio" is an adjustment of the traditional Sharpe ratio that accounts for transaction costs in illiquid markets. These costs, such as market impact and higher broker fees, can significantly reduce net returns. For Alphas generated in illiquid regions, this ratio measures performance after deducting trading costs, providing a more exact assessment of efficiency in generating excess returns per unit of risk considering liquidity constraints.

 

Additionally, the After-cost Sharpe test evaluates the performance of illiquid instruments by comparing the after-cost Sharpe ratio of the more illiquid half of the universe to the original universe. The test ensures that this illiquid part meets a minimum Sharpe ratio threshold, defined as:

Threshold=0.525×After-Cost Original Sharpe

If the after-cost Sharpe ratio of the illiquid portions falls below this threshold, the Alpha can fail the test.

 

Tips to improve Alpha performance in the most illiquid quantiles:

-     Try to allocate capital evenly across different liquidity buckets, so that they have more on-par     performance
-     High turnover generally increase trading cost, consider lowering the turnover without hurting the performance

The illiquid universe is affected by the size and the liquidity risk factor. One way to enhance your alpha’s Performance could be to neutralize it against these factors, using group_neutralize() or vector_neut() operators, or you can try the risk-neutral settings!