import random
import yfinance as yf
import sqlite3
import os.path
from os import path
import pandas as pd
from strategy import Strategy, TimeStrategy
from DatePercentStrategy import DatePercentStrategyLimitedFunds, DatePercentStrategyConstTrade
from resultAccumulator import ResultAccumulator
from optimalStrategy import OptimalStrategyFinder


# method that will format the s and p 500 object so that it can be written to the db
def convert_to_db_form(stock_hist):
    records = []
    for i in range(len(stock_hist["Open"])):
        records.append((str(stock_hist.index[i])[0:10], stock_hist["Open"][i], stock_hist["High"][i],
                        stock_hist["Low"][i], stock_hist["Close"][i]))
    return records


# method that will make an s and p 500 database
# note that I am using the vanguard etf for the s and p 500
def make_sp_sqlite():
    VOO = yf.Ticker("VOO")
    VOO_historical = VOO.history(period="max")
    sp_hist_records = convert_to_db_form(VOO_historical)

    con = sqlite3.connect('sp.db')
    cur = con.cursor()

    # create the table that will hold the stock information for the s and p 500
    cur.execute('''CREATE TABLE sp
                       (date text, open real, high real, low real, close real)''')
    cur.executemany('INSERT INTO sp VALUES(?,?,?,?,?);', sp_hist_records)

    # commit the changes to db
    con.commit()
    # close the connection
    con.close()


# method that will load the historical data into a dataframe
# much faster to load the data from db than query yfinance API
def load_db():
    con = sqlite3.connect('sp.db')
    cur = con.cursor()

    # the column headers for the dataframe
    data_sp = {"Date": [], "Open": [], "High": [], "Low": [], "Close": []}

    # read in all of the data from the db
    for row in cur.execute('SELECT * FROM sp'):
        i = 0
        for header in data_sp.keys():
            data_sp[header].append(row[i])
            i = i + 1

    # close the connection
    con.close()

    # create the df
    sp_df = pd.DataFrame(data=data_sp)

    # return the pandas df that now contains information on the
    # open, high, low, and close values for the S&P(VOO) for a particular date
    return sp_df


# method that will make a test df starting on a random date that is at least as many
# days as passed in as a parameter
def make_test_df(sp_df, days):
    rand_start = random.randint(0, len(sp_df.index) - days - 1)
    test_df = sp_df[sp_df.index > rand_start]
    test_df.reset_index(inplace=True)

    return test_df


# method that will take in the specified strategies and test them from random start dates
def test_strategies(strategies, sp_df, days, num_trials, print):
    # create a list of result accumulators
    accumulated_results = []
    for strategy in strategies:
        accumulated_results.append(ResultAccumulator(strategy.name))

    for i in range(num_trials):
        test_df = make_test_df(sp_df, days)
        j = 0
        for strategy in strategies:
            strategy.execute_strategy(test_df)
            # equal to the close on 02/04/2022
            strategy.update_share_price(412.519989)
            # strategy.print_strategy_results()
            accumulated_results[j].accum_results(strategy.results_copy())
            strategy.clear()
            j += 1

    if print:
        print_accum_results(accumulated_results)

    return accumulated_results


# method that will print the accumulated results
def print_accum_results(accumulated_results):
    print("\n---------------------------\n")
    print("Testing complete!!!")
    for accumulate_result in accumulated_results:
        accumulate_result.print_strategy_results()


# method that will determine the n best time strategies
def get_best_time_strategies(sp_df, trial_days, capital, time, trials):
    # create an instance of the OptimalStrategyFinder class that will hold
    # the 10 best time interval  strategies
    optimal_finder = OptimalStrategyFinder(10)

    # create a strategy corresponding to daily to one trade per year
    strategies = []
    for i in range(253):
        strat_name = "every " + str(i+1) + " days"
        strat = TimeStrategy(strat_name, i+1, trial_days, capital, time)
        strategies.append(strat)

    # obtain the results of all of these strategies
    all_accum = test_strategies(strategies, sp_df, trial_days, trials, False)
    # use optimal_finder to obtain the 5 best time interval strategies
    for accum in all_accum:
        optimal_finder.add_or_discard(accum)

    return optimal_finder


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # create the database if it doesn't exist else connect to existing db
    if path.exists("sp.db"):
        print("Loading VOO stock prices...")
        sp_df = load_db()
    # if this is the first execution load the stock
    else:
        print("Creating VOO stock prices db...")
        make_sp_sqlite()
        sp_df = load_db()

    # the number of days in which stock purchases will be made
    trial_days = 254
    # the number of random trials to accumulate over
    trials = 200
    # if quick results are desired, set trials to 1
    # note that the top strategies will be dependent only on a single trial and thus, are a reflection of the single
    # trial rather than broader behavior
    # trials = 1
    # the amount to spend over the total trial
    to_spend = 100000
    # the amount per trade in
    trade_amount = 500

    # obtain the 10 best time interval based strategies from 200 trials with random start dates
    # note that the optimal strategies are dependent upon 200 random start dates, thus, there is slight
    # variation on the optimal intervals obtained but are typically in every 120-140 days
    optimal = get_best_time_strategies(sp_df, trial_days, to_spend, "Open", trials)
    # optimal.print_optimal()

    # create a strategies for the highest performing time strategies
    strats = optimal.get_optimal_list_time(trial_days, to_spend, "Open")

    # create percent strategies and append to strats
    one_percent = DatePercentStrategyLimitedFunds("1% down limited", 1, trial_days, to_spend)
    one_five = DatePercentStrategyLimitedFunds("1.5% down limited", 1.5, trial_days, to_spend)
    one_seven_five = DatePercentStrategyLimitedFunds("1.75% down limited", 1.75, trial_days, to_spend)
    point_nine = DatePercentStrategyLimitedFunds("0.9% down limited", 0.9, trial_days, to_spend)
    point_nine_const = DatePercentStrategyConstTrade("0.9% down const trade", 0.9, trial_days, trade_amount)

    strats.append(one_percent)
    strats.append(one_five)
    strats.append(one_seven_five)
    strats.append(point_nine)
    strats.append(point_nine_const)
    test_strategies(strats, sp_df, trial_days, 200, True)
