from abc import ABC, abstractmethod


# creating a robust interface for a strategy
class Strategy(ABC):
    def __init__(self, name):
        self.name = name
        self.returns = 0.0
        self.return_percentage = 0.0
        self.cost_basis_total = 0.0
        self.num_shares = 0.0
        self.share_price = 0.0
        self.total_orders = 0

    # method that will compute the total price of all the shares that are currently held
    def current_total_price(self):
        return self.share_price * self.num_shares

    # method that will return the net returns
    def get_net_returns(self):
        self.returns = self.current_total_price() - self.cost_basis_total
        return self.returns

    # method that will return the percentage returns
    def get_percent_return(self):
        if self.cost_basis_total != 0:
            self.return_percentage = self.current_total_price() / self.cost_basis_total - 1
        else:
            self.return_percentage = 0
        return self.return_percentage

    # method that will update the share price
    def update_share_price(self, price):
        self.share_price = price

    # method that will "buy" shares at a certain price
    def buy_shares(self, num_shares, stock_price):
        self.cost_basis_total += stock_price * num_shares
        self.num_shares += num_shares
        self.total_orders = self.total_orders + 1

    # method that will "buy" a certain dollar amount of shares at a specified price
    def buy_in_dollars(self, num_dollars, stock_price):
        self.cost_basis_total += num_dollars
        self.num_shares += num_dollars / stock_price
        self.total_orders = self.total_orders + 1

    # method that will execute the given trading strategy on the dataframe that is passed in
    @abstractmethod
    def execute_strategy(self, stock_df):
        pass

    # method that will print the results for a strategy
    def print_strategy_results(self):
        print("\nPerformance Summary for " + self.name)
        print("Number of trades: " + str(self.total_orders))
        print("Total spent: $" + str(self.cost_basis_total))
        print("Final total: $" + str(self.current_total_price()))
        print("Total net return: $" + str(self.get_net_returns()))
        print("Percentage return: " + str(self.get_percent_return() * 100) + '%')

    # returns a list copy of the results in the form
    # [num trades, total spent, final total, total net returns, percentage return]
    def results_copy(self):
        return [self.total_orders, self.cost_basis_total, self.current_total_price(),
                self.get_net_returns(), self.get_percent_return()]

    # method that will clear the results from a strategy for a new trial
    def clear(self):
        self.returns = 0.0
        self.return_percentage = 0.0
        self.cost_basis_total = 0.0
        self.num_shares = 0.0
        self.share_price = 0.0
        self.total_orders = 0


# class that will be a strategy for trading based on specific time intervals for investment
class TimeStrategy(Strategy):
    def __init__(self, name, interval, duration, total_to_spend, time):
        super().__init__(name)
        # interval is the number of trading days to wait in between stock purchases note that
        self.interval = interval
        # the duration is the number of trading days that the strategy is to purchase shares over
        self.duration = duration
        # note that time must be either open or close
        # it is implausible to create a strategy that will correctly for example purchase the shares at their low
        # for the day every day
        self.time = time
        self.to_spend = total_to_spend
        self.purchase_df = None
        self.order_amount = None

    def execute_strategy(self, stock_df):
        # generate the row identifiers to obtain the information for purchase
        self.purchase_df = self.generate_purchase_ids(stock_df)
        self.purchase_from_purchase_df()

    # return the row identifiers of the days that will correspond to stock purchases for this strategy
    def generate_purchase_ids(self, stock_df):
        temp = stock_df[stock_df.index < self.duration]
        temp = temp[temp.index % self.interval == 0]
        # note that due to the manner in which order_amount is defined it will likely be the case
        # that the total number of dollars will not be fully allocated
        self.order_amount = self.to_spend / len(temp.index)
        # print(temp)

        return temp

    def purchase_from_purchase_df(self):
        # note that I do not perform checking to determine if the capital is available for this trade as the exact
        # amount to be traded for the duration has been computed
        for price in self.purchase_df[self.time]:
            self.buy_in_dollars(self.order_amount, price)

    # method that will clear the results from a strategy for a new trial
    def clear(self):
        super().clear()
        self.purchase_df = None
        self.order_amount = None
