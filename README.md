For this project, I wanted to test a few strategies to determine what the optimal strategy for purchasing shares of an S&P500 etf 'VOO'
would be. 

The program starts by creating a table sp in an sqlite db that holds all the information in terms of open, close, high and low prices 
for the VOO etf obtained using the yfinance API. On all subsequent calls, the program will load the information stored in the table
into a pandas df. 

Refer to Strategy.py and DatePercentStrategy.py to observe the manner in which the different strategies are defined. There is the abstract base class 
Strategy which encapsulates all of the common elements that exist in all different etf purchasing strategies. Then, there is TimeStrategy that is 
derived from Strategy that represents a strategy for purchasing the etf every specified number of trading days. Finally, I have DatePercentageStrategy,
which is derived from Strategy and represents the basic elements of a strategy for purchasing the etf on days when it is down a specific percentage point.
Note that this could be accomplished by placing a limit market order based on the open price down the specified percentage points that it is assumed would 
be executed based on the low for that day exceeding that percentage down from the open. DatePercentStrategyLimitedFunds and DatePercentStrategyConstTrade 
are derived from DatePercentageStrategy, representing a DatePercentageStrategies with a fixed total amount and an assumed fixed amount that could be spent
per trade respectively.

ResultAccumulator accumulates results across trials for a strategy and OptimalStrategyFinder utilizes a min heap to find the n best strategies.

So far, I have only used an OptimalStrategyFinder object in get_best_time_strategies which I use to obtain the 10 best time interval strategies
in terms of performance over 200 random trials. Note make_test_df to observe the manner in which a random trial is created. Also note that I 
read to the database on 02/04/2022, and thus, strategies are evaluated in terms of returns with respect to the close that day and should be 
updated appropriately depending on the end date when read into the sqlite db. Note test_strategies in main.py to observe the way strategies are tested.

Observations: 
The 10 best time interval based strategies obtained from 200 trials with random start dates were dependent on the random start dates, thus, there was 
slight variation on the optimal intervals obtained but are typically in the range of every 120-140 days. 
From my tests, the best performing time interval strategies failed to outperform the date percentage strategies with limited funds.
Interestingly, the date percentage strategies with limited funds seem to outperform those with constant trade amounts. The limited funds strategies
operate with an estimate of how many days the specified percentage down will occur in a given year, and may run out of funds or not deploy all funds.
