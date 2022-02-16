from strategy import Strategy
from abc import ABC, abstractmethod
import math


# base class for a date percent strategy
class DatePercentStrategy(Strategy):
    def __init__(self, name, percent_down, duration):
        super().__init__(name)
        self.percent_down = percent_down
        # the duration is the number of trading days that the strategy is to purchase shares over
        self.duration = duration
        self.num_trades = 0
        self.purchase_df = None

    def execute_strategy(self, stock_df):
        # generate the row identifiers to obtain the information for purchase
        self.purchase_df = self.generate_purchase_ids(stock_df)
        self.purchase_from_purchase_df()

    @abstractmethod
    # return the row identifiers of the days that will correspond to stock purchases for this strategy
    def generate_purchase_ids(self, stock_df):
        pass

    @abstractmethod
    def purchase_from_purchase_df(self):
        pass

    # method that will clear the results from a strategy for a new trial
    def clear(self):
        super().clear()
        self.purchase_df = None


# class that will be a strategy for trading based on the s & p being down a specfic percentage point during a day
# with a limited amount of funds to trade
class DatePercentStrategyLimitedFunds(DatePercentStrategy):
    def __init__(self, name, percent_down, duration, total_to_spend):
        super().__init__(name, percent_down, duration)
        self.to_spend = total_to_spend
        self.funds = total_to_spend
        self.order_amount = None

    # return the row identifiers of the days that will correspond to stock purchases for this strategy
    def generate_purchase_ids(self, stock_df):
        # compute the ceiling of the average number of days where the percentage down is expected to be satisfied
        # and return the df that has been filtered to here to avoid unnecessary computation
        temp = self.get_average_times(stock_df)
        temp = temp[temp.index < self.duration]
        down_percent = temp["Open"] * (1 - self.percent_down / 100)
        temp["PurchasePrice"] = down_percent
        # note that due to the manner in which order_amount is defined it will likely be the case
        # that the total number of dollars will not be fully allocated
        self.order_amount = self.to_spend / self.num_trades
        # print(temp)

        return temp

    # method that will determine the average number of times that the specific percentage down is met
    # for the duration in the whole df
    def get_average_times(self, stock_df):
        # obtain the total number of examples
        total_ex = len(stock_df.index)
        # obtain the proportion of the total examples are captured in the duration
        proportion_duration = total_ex / self.duration
        # obtain df with all the times that the specified percentage down has occured
        temp = stock_df[stock_df["Low"] / stock_df["Open"] < (1 - self.percent_down / 100)]
        # take the ceiling of the average number of times this percentage down was observed
        # over the duration period => try to deploy all capital for trading
        self.num_trades = math.ceil(len(temp.index) / proportion_duration)

        # note that we have a df with only the examples satisfying the percentage down condition
        # return this to be used in generate purchase_ids
        return temp

    def purchase_from_purchase_df(self):
        # ensure that if the strategy runs out of funds it terminates
        for price in self.purchase_df['PurchasePrice']:
            if self.funds < self.order_amount:
                break
            self.buy_in_dollars(self.order_amount, price)
            self.funds -= self.order_amount

    # method that will clear the results from a strategy for a new trial
    def clear(self):
        super().clear()
        self.funds = self.to_spend
        self.order_amount = None


# class that will be a strategy for trading based on the s&p being down a specfic percentage point during a day
# with an assumed constant amount of funds being avaiable to purchase the etf on all such days
class DatePercentStrategyConstTrade(DatePercentStrategy):
    def __init__(self, name, percent_down, duration, order_amount):
        super().__init__(name, percent_down, duration)
        self.order_amount = order_amount

    # return the row identifiers of the days that will correspond to stock purchases for this strategy
    def generate_purchase_ids(self, stock_df):
        # get all the days in which the low is over the specified percentage down as compared to the open
        # ie a limit market order could have been placed at the open that would execute
        temp = stock_df[stock_df.index < self.duration]
        temp = temp[temp["Low"] / temp["Open"] < (1 - self.percent_down / 100)]
        down_percent = temp["Open"] * (1 - self.percent_down / 100)
        temp["PurchasePrice"] = down_percent
        # print(temp)

        return temp

    def purchase_from_purchase_df(self):
        # ensure that if the strategy runs out of funds it terminates
        for price in self.purchase_df['PurchasePrice']:
            self.buy_in_dollars(self.order_amount, price)
