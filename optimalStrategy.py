from heapq import heapify, heappush, heappop
from strategy import TimeStrategy


# class that will retain copies of the top_n strategies
class OptimalStrategyFinder:
    def __init__(self, top_n):
        # using a min heap for the top n best strategies
        heap = []
        heapify(heap)
        self.best_strategies = heap
        self.num_strategies = top_n

    # method that will either add an optimal strategy or discard if not optimal
    def add_or_discard(self, accum_results):
        # discard strategy if accum_results.get_avg_total() <= self.best_strategies[0] and there are more
        # than num_strategies stored

        # only a push if there are not yet the proper number of top strategies in the heap
        if len(self.best_strategies) < self.num_strategies:
            heappush(self.best_strategies, (accum_results.get_avg_total(), accum_results))
        # otherwise if greater than head of heap, remove the head and add
        elif accum_results.get_avg_total() > self.best_strategies[0][0]:
            heappop(self.best_strategies)
            heappush(self.best_strategies, (accum_results.get_avg_total(), accum_results))

    # get the optimal strategies
    def get_strategies(self):
        return self.best_strategies

    # method that will print the optimal strategies from least to greatest return
    def print_optimal(self):
        print(self.best_strategies)
        while len(self.best_strategies) != 0:
            to_print = heappop(self.best_strategies)[1]
            to_print.print_strategy_results()

    # method that will return a list with the optimal time strategies
    def get_optimal_list_time(self, duration, total_to_spend, time):
        optimal_list = []
        while len(self.best_strategies) != 0:
            time_string = heappop(self.best_strategies)[1].name
            interval = float(time_string[6:9])
            temp_strat = TimeStrategy(time_string, interval, duration, total_to_spend, time)
            optimal_list.append(temp_strat)

        return optimal_list
