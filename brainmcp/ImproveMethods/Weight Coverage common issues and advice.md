Weight Coverage common issues and advice
 NL41370
2 years ago Updated ~3 minute read
Not yet followed by anyone
The weight test simply measures the capital concentration in a single stock of an Alpha. In BRAIN, the limit is 10% of the total book size. The weight test is important to limit drawdown risk created by the fluctuation of the stock price, especially in Out-of-Sample.

Use lower truncation value in the settings: BRAIN provides truncation to control the concentration of the stock weight in the Alpha simulation. The value 0.1 means the cut off limit is 10% of the book size.

Coverage

One of the major factors leading to failing weight test is coverage. For example, if the number of stocks on the long or short size at any point in the simulation is less than 10, or the total of the stocks is less than 20. Often Alphas with low-coverage and/or unbalanced long-short count fail the weight test.

How to handle low coverage

Use visualization to detect abnormal changes in the coverage. Pay attention to any low coverage at the beginning of your simulation; it could be better to remove the beginning period with coverage lower than 60% of your final stock count.
Try: group_count(is_nan (a),market)> 40 ? a:nan.  This operator detects an abnormal drop in the count due to missing data in short horizon.
Try: Ts_backfill(a, 2) if the data is missing for one day. This operator detects low coverage due to infrequently updated data, such as fundamental data.
Try: Ts_backfill(a, 60) for quarterly updated fundamental data. This operator detects abnormal changes in the coverage for the idea depending on news.
You can also detect NaN values and conduct your own backfill using is_nan(), last_diff_value(), days_from_last_change().

Be creative, you might create a new Alpha with proper filling techniques and there are more to explore than what's listed here.

Alpha magnitude distribution

Not all the weight test failures are due to data coverage problems. Another major factor that may contribute to the failure comes from Alpha ideas that rely heavily on data distribution. The weight problem appears when the data is widespread, having outliers or errors in the data. So reduce outliers

Often, the weight test setting helps in general with infrequent outliers but there is no guarantee. Another approach is to change the data distribution using rank (or group_rank) functions. Range normalized functions such as rank, log, scale and zscore are helpful here, too.

Rank is designed to balance the long-short count. Rank makes the data distribution look like uniform distribution. Make sure you understand and control the range of the data as well. It is a good practice to normalize data range before working with it. 

Extra notes:

Don’t overuse backfill functions with a large back-day since it may hurt performance.
Understand the data using the visualization tool and use the proper back-day number.
Rank is used as a part of a robust test (rank test), so Alphas with rank function are more likely to pass the rank test.
One piece of final advice: If you tried all the methods that mentioned and still failed the weight test, please move on to another idea. Although the idea may be good, the capacity to express it in such a way to make it pass the weight test may not be possible, and opportunities to create new Alphas that could pass the weight test always exist.
Was this article