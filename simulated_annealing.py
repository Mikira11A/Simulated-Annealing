import random
from time import sleep

class SimulatedAnnealing:
    def __init__(self, edges, mode="current_route"):
        self.mode = mode

        self.edges = edges
        random.seed()

        self.iterations = 1000
        self.temperature = self.iterations + 1
        self.shuffle_iterations = self.iterations // 5
        self.two_opt_iterations = (self.iterations // 5) * 3
        self.swap_iterations = self.iterations // 5
        self.acceptance_rate = 1

        self.cooling_rate = 1
        self.current_route = ([c for c in "ABCDEFGHIA"], self.route_weight([c for c in "ABCDEFGHIA"]))
        #self.current_route = ("ABCDEFGHIA", self.route_weight("ABCDEFGHIA"))
        self.route_length = len(self.current_route[0])

        self.new_route = self.current_route

        self.best_route = self.current_route

    def route_weight(self, route):
        weight = 0
        for i in range(len(route) - 1):
            edge = (route[i], route[i + 1])
            if edge in self.edges:
                weight += self.edges[edge]["weight"]
            else:
                return float('inf')  # Invalid route
            
        return weight
    
    def shuffle(self, route):
        route_list = route[1:-1]
        idx1, idx2 = random.sample(range(len(route_list)+1), 2)

        if idx1 > idx2:
            idx1, idx2 = idx2, idx1

        return route[0:1] + route_list[:idx1] + random.sample(route_list[idx1:idx2], k=len(route_list[idx1:idx2])) + route_list[idx2:] + route[-1:]
    
    def two_opt(self, route):
        route_list = route[1:-1]
        idx1, idx2 = random.sample(range(len(route_list)+1), 2)

        if idx1 > idx2:
            idx1, idx2 = idx2, idx1

        route_list[idx1:idx2] = reversed(route_list[idx1:idx2])
        return route[0:1] + route_list + route[-1:]
    
    def swap(self, route):
        route_list = route[1:-1]
        idx1, idx2 = random.sample(range(len(route_list)), 2)

        if idx1 > idx2:
            idx1, idx2 = idx2, idx1

        route_list[idx1], route_list[idx2] = route_list[idx2], route_list[idx1]
        return route[0:1] + route_list + route[-1:]
    
    def start(self, callback):
        print("Shuffling...")
        for _ in range(self.shuffle_iterations):
            new_route = self.shuffle(self.current_route[0])
            self.new_route = (new_route, self.route_weight(new_route))

            callback(getattr(self, self.mode)[0])
            #print(f"{_} Current route: {self.current_route[0]} with weight {self.current_route[1]} temperature: {self.temperature:.2f} acceptance probability: {self.acceptance_rate:.2f}")


            if self.accept(self.new_route[1], self.new_route[0]):
                self.current_route = self.new_route
            
            self.temperature -= self.cooling_rate

        print("2-opt...")
        for _ in range(self.two_opt_iterations):
            new_route = self.two_opt(self.current_route[0])
            self.new_route = (new_route, self.route_weight(new_route))

            callback(getattr(self, self.mode)[0])
            #print(f"{_+(self.shuffle_iterations)} Current route: {self.current_route[0]} with weight {self.current_route[1]} temperature: {self.temperature:.2f} acceptance probability: {self.acceptance_rate:.2f}")

            if self.accept(self.new_route[1], self.new_route[0]):
                self.current_route = self.new_route
            
            self.temperature -= self.cooling_rate

        print("Swapping...")
        for _ in range(self.swap_iterations):
            new_route = self.swap(self.current_route[0])
            self.new_route = (new_route, self.route_weight(new_route))

            callback(getattr(self, self.mode)[0])
            #print(f"{_+(self.shuffle_iterations+self.two_opt_iterations)} Current route: {self.current_route[0]} with weight {self.current_route[1]} temperature: {self.temperature:.2f} acceptance probability: {self.acceptance_rate:.2f}")

            if self.accept(self.new_route[1], self.new_route[0]):
                self.current_route = self.new_route
            
            self.temperature -= self.cooling_rate

        print(f"Best route: {self.best_route[0]} with weight {self.best_route[1]}")
        callback(self.best_route[0])
        

    def accept(self, new_weight, new_route):
        if new_weight < self.current_route[1]:
            if new_weight < self.best_route[1]:
                self.best_route = (new_route, new_weight)
            return True
        else:
            acceptance_probability = random.random()
            self.acceptance_rate = (self.temperature / self.iterations) ** 3
            return acceptance_probability < self.acceptance_rate