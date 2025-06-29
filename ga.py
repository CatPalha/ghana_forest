import random
import numpy as np


class GA:

    def __init__(self, crossover_point, mutation_rate):
        self.crossover_point = crossover_point
        self.mutation_rate = mutation_rate

    def crossover(self, p1, p2):

        c1 = list(np.append(p1[:self.crossover_point], p2[self.crossover_point:]))
        c2 = list(np.append(p2[:self.crossover_point], p1[self.crossover_point:]))
        
        return c1, c2

    def mutation(self, c):
        ## ????
        if self.mutation_rate >= 0.5:
            if self.crossover_point != len(c) - 1:
                c[self.crossover_point] = random.randrange(0, 2, 1)
            else:
                c[self.crossover_point] = random.randrange(0, 1, 1)

        return c

### TEST ####
ga = GA(crossover_point = random.randrange(3), mutation_rate = random.random())
print("Crossover point: ", ga.crossover_point)
print("Mutation rate: ", ga.mutation_rate)
crossover_test = ga.crossover([1, 1, 1], [2, 1, 0])
print(crossover_test)
mutation_test_c1 = ga.mutation(crossover_test[0])
mutation_test_c2 = ga.mutation(crossover_test[1])
print(mutation_test_c1)
print(mutation_test_c2)