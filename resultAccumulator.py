# class that will be used to accumulate the results across random start dates
# for different strategies
class ResultAccumulator:
    def __init__(self, name):
        self.name = name
        self.total_trades = 0.0
        self.total_spent = 0.0
        self.final_total = 0.0
        self.net_return_total = 0.0
        self.return_percentage_total = 0.0
        self.results_accumulated = 0

    # method that will accumulate results
    def accum_results(self, results):
        self.results_accumulated += 1
        self.total_trades += results[0]
        self.total_spent += results[1]
        self.final_total += results[2]
        self.net_return_total += results[3]

    # method that will return the average over accumulated totals for a metric
    def get_average(self, metric):
        return metric/self.results_accumulated

    # method that will return the average percentage return
    def get_avg_total(self):
        return self.net_return_total/self.total_spent

    # method that will print the accumulated results
    def print_strategy_results(self):
        print("\nPerformance Summary for " + self.name)
        print("Average Number of trades: " + str(self.get_average(self.total_trades)))
        print("Average Total spent: $" + str(self.get_average(self.total_spent)))
        print("Average Final total: $" + str(self.get_average(self.final_total)))
        print("Average Total net return: $" + str(self.get_average(self.net_return_total)))
        print("Average Percentage return: " + str(self.net_return_total/self.total_spent * 100) + '%')

    def clear(self):
        self.total_trades = 0.0
        self.total_spent = 0.0
        self.final_total = 0.0
        self.net_return_total = 0.0
        self.return_percentage_total = 0.0
        self.results_accumulated = 0