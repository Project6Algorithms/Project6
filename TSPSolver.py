#!/usr/bin/python3

from which_pyqt import PYQT_VER

if PYQT_VER == 'PYQT5':
    from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT4':
    from PyQt4.QtCore import QLineF, QPointF
else:
    raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))

import time
import numpy as np
from TSPClasses import *
import heapq
import itertools


class TSPSolver:
    def __init__(self, gui_view):
        self._scenario = None

    def setupWithScenario(self, scenario):
        self._scenario = scenario

    ''' <summary>
		This is the entry point for the default solver
		which just finds a valid random tour.  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of solution, 
		time spent to find solution, number of permutations tried during search, the 
		solution found, and three null values for fields not used for this 
		algorithm</returns> 
	'''

    def defaultRandomTour(self, time_allowance=60.0):
        results = {}
        cities = self._scenario.getCities()
        ncities = len(cities)
        foundTour = False
        count = 0
        bssf = None
        start_time = time.time()
        while not foundTour and time.time() - start_time < time_allowance:
            # create a random permutation
            perm = np.random.permutation(ncities)
            route = []
            # Now build the route using the random permutation
            for i in range(ncities):
                route.append(cities[perm[i]])
            bssf = TSPSolution(route)
            count += 1
            if bssf.cost < np.inf:
                # Found a valid route
                foundTour = True
        end_time = time.time()
        results['cost'] = bssf.cost if foundTour else math.inf
        results['time'] = end_time - start_time
        results['count'] = count
        results['soln'] = bssf
        results['max'] = None
        results['total'] = None
        results['pruned'] = None
        return results

    ''' <summary>
		This is the entry point for the greedy solver, which you must implement for 
		the group project (but it is probably a good idea to just do it for the branch-and
		bound project as a way to get your feet wet).  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number of solutions found, the best
		solution found, and three null values for fields not used for this 
		algorithm</returns> 
	'''

    def greedy(self, time_allowance=60.0):
        import time
        results = {}
        cities = self._scenario.getCities()
        ncities = len(cities)
        count = 0
        startTime = time.time()
        startNode = random.randint(0, ncities - 1)
        bssf = None
        foundTour = False
        while foundTour is False and time.time() - startTime < time_allowance:
            route = [cities[startNode]]
            for i in range(ncities):
                min = np.inf
                nextNode = None
                for j in range(ncities):
                    if cities[j] not in route:
                        length = route[i].costTo(cities[j])
                        if length < math.inf and length < min:
                            min = length
                            nextNode = cities[j]
                if nextNode is not None:
                    route.append(nextNode)
                else:
                    break
            startNode += 1
            if len(route) == ncities:
                bssf = TSPSolution(route)
                count += 1
                if bssf.cost < np.inf:
                    foundTour = True

        time = time.time() - startTime

        results['cost'] = bssf.cost
        results['time'] = time
        results['count'] = count
        results['soln'] = bssf
        results['max'] = None
        results['total'] = None
        results['pruned'] = None
        return results
        pass

    ''' <summary>
		This is the entry point for the branch-and-bound algorithm that you will implement
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number solutions found during search (does
		not include the initial BSSF), the best solution found, and three more ints: 
		max queue size, total number of states created, and number of pruned states.</returns> 
	'''

    def branchAndBound(self, time_allowance=60.0):
        results = {}
        cities = self._scenario.getCities()
        ncities = len(cities)
        foundTour = False
        count = 0
        bssf = self.defaultRandomTour(time_allowance=60.0)['soln']
        pruned = 0
        max_q_size = 0
        num_states = 0
        Q = []
        start_time = time.time()

        matrix = np.empty(shape=(len(cities), len(cities)), dtype=float)

        root = TSPNode(0, matrix, [], 0)

        # Distances
        for i, c1 in enumerate(cities):
            for j, c2 in enumerate(cities):
                root.m[i, j] = c1.costTo(c2)

        root.reduceMatrix(0, 0)
        root.addCityAndUpdateCost(cities[0])

        # Adding the heap
        heapq.heappush(Q, root)

        while len(Q) != 0 and time.time() - start_time < time_allowance:
            node = heapq.heappop(Q)

            for i, dist in enumerate(node.m[node.city._index]):
                num_states += 1

                if dist != np.inf and cities[i] not in node.route:  # Unvisited cities

                    # Nodes creation
                    next_node = TSPNode(node.lower_bound, np.copy(node.m), node.route.copy(), node.cost)
                    next_node.addCityAndUpdateCost(cities[i])
                    next_node.reduceMatrix(node.city._index, next_node.city._index)

                    if len(next_node.route) == len(
                            cities):  # Checks to see if all cities has been visited and is accounted for in the travel
                        solution = TSPSolution(next_node.route)

                        if solution.cost < bssf.cost:
                            count += 1
                            bssf = solution  # Check bssf for the tour
                    else:  # And if the solution isn't the best cost

                        if next_node.lower_bound < bssf.cost:
                            heapq.heappush(Q, next_node)
                            max_q_size = max(max_q_size, len(Q))
                        else:
                            pruned += 1  # To see if pruning is necessary

        end_time = time.time()
        results['cost'] = bssf.cost
        results['time'] = end_time - start_time
        results['count'] = count
        results['soln'] = bssf
        results['max'] = max_q_size
        results['total'] = num_states
        results['pruned'] = pruned
        return results

        pass

    ''' <summary>
		This is the entry point for the algorithm you'll write for your group project.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number of solutions found during search, the 
		best solution found.  You may use the other three field however you like.
		algorithm</returns> 
	'''

    def fancy(self, time_allowance=60.0):
        import time
        startTime = time.time()
        results = {}
        pruned = 0
        cities = self._scenario.getCities()
        ncities = len(cities)
        population1 = [self.greedy(time_allowance).get('soln')]
        for y in range(ncities - 1):
            population1 = np.append(population1, self.defaultRandomTour(time_allowance).get('soln'))
        solutions = len(population1)
        newPopulation = []
        minArray = []
        # Selection
        for j in range(len(population1)):
            minArray.append(population1[j].cost)
        minimum = min(minArray)
        states = 0
        #print(minArray)
        first = second = np.inf
        firstIndex = 0
        secondIndex = 0
        for j in range(0, len(minArray)):
            if minArray[j] < first:
                second = first
                first = minArray[j]
                firstIndex = j
            elif minArray[j] < second:
                second = minArray[j]
                secondIndex = j

        parent1 = population1[firstIndex]
        parent2 = population1[secondIndex]

        newPopulation = []
        newPopulation = np.append(newPopulation, parent1)
        newPopulation = np.append(newPopulation, parent2)
        while len(population1) > len(newPopulation) and time.time() - startTime < time_allowance:
            minArray = []
            # Selection
            parent1 = 0
            parent2 = 0

            for j in range(len(newPopulation)):
                minArray.append(newPopulation[j].cost)
            first = second = np.inf
            firstIndex = 0
            secondIndex = 0
            for j in range(0, len(minArray)):
                if minArray[j] < first:
                    second = first
                    first = minArray[j]
                    firstIndex = j
                elif minArray[j] < second:
                    second = minArray[j]
                    secondIndex = j
            parent1 = newPopulation[firstIndex]
            parent2 = newPopulation[secondIndex]
            # Crossover
            child1Route = parent1.route
            child2Route = parent2.route
            for j in range(0, ncities // 2):
                point = random.randint(1, ncities - 1)
                if point == child1Route[len(child1Route) - 1] or point == child2Route[len(child2Route) - 1]:
                    point = random.randint(1, ncities - 1)

                swap1Index = None
                swap2Index = None
                for x in range(0, len(child1Route)):

                    if child1Route[x]._index == point:
                        swap1Index = x

                for x in range(0, len(child2Route)):
                    if child2Route[x]._index == point:
                        swap2Index = x
                child1Route[swap1Index], child1Route[swap2Index] = child1Route[swap2Index], child1Route[swap1Index]
                child2Route[swap1Index], child2Route[swap2Index] = child2Route[swap2Index], child2Route[swap1Index]
            # Mutation
            index1 = random.randint(1, ncities - 3)
            index2 = random.randint(1, ncities - 3)
            child1Route[index1], child1Route[index2] = child1Route[index2], child1Route[index1]
            child1 = TSPSolution(child1Route)

            index1 = random.randint(1, ncities - 3)
            index2 = random.randint(1, ncities - 3)

            child2Route[index1], child2Route[index2] = child2Route[index2], child2Route[index1]
            child2 = TSPSolution(child2Route)
            states += 2
            if child1.cost < parent1.cost or child1.cost < parent2.cost:
                # Add to new population
                newPopulation = np.append(population1, child1)
                solutions += 1
            elif child1.cost > parent1.cost and child1.cost > parent2.cost:
                pruned += 1
            if child2.cost < parent1.cost or child2.cost < parent2.cost:
                # Add to new population
                newPopulation = np.append(newPopulation, child2)
                solutions += 1
            elif child2.cost > parent1.cost and child2.cost > parent2.cost:
                pruned += 1
            array = []
            for x in range(len(newPopulation)):
                array = np.append(array, newPopulation[x].cost)
            #print(array)
            fittestIndex = np.argmin(array)
            fittest = newPopulation[fittestIndex]

        # Finding best solution

        time = time.time() - startTime
        results['cost'] = fittest.cost
        results['time'] = time
        results['count'] = solutions
        results['soln'] = fittest
        results['max'] = None
        results['total'] = states
        results['pruned'] = pruned
        return results

        pass
