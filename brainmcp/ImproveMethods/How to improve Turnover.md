How to improve Turnover?
 NL41370
1 year ago Updated ~2 minute read
Not yet followed by anyone
What's Turnover?
Turnover signifies how often an Alpha simulates trades. It's defined as the ratio of value traded to book size. Daily Turnover = Dollar trading volume/Booksize. Good Alphas tend to have lower turnover, since low turnover means lower transaction costs.
 
Is it necessary to have Turnover <40% for the Alpha to be evaluated?
It's not necessary, but it's advisable. High turnover Alphas may be hard to trade in the real world where transaction costs involved. You can focus on Alphas with decent Sharpe (>2.5) and reasonable turnover (< 40%). And keep trying out new ideas.
 
Ways to improve Turnover
You should try to keep Turnover below 40% in your Alphas, and definitely below 70%. Ways to reduce turnover include:

Use Decay simulation setting. If your Alpha is changing rapidly, using a decay setting equal to N days tend to average out the Alpha over N days, and reduce the daily turnover. However, the performance could change substantially.
Use "Rank" function on your Alpha.
Use trade_when operator
Implement thresholds using hump operator
Ways to increase turnover include:
User lower values for Decay setting
Work on more liquid (smaller) universes in the alpha settings
Use smaller time periods (e.g. use 20 days instead of 200 days) as parameters within your time series and cross-sectional operators
Work with dataset categories that may be updated frequently ( e.g. news, sentiment). This could also help you create some unique Alphas with high value score datasets