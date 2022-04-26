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
		startNode = 0
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

		startTime = time.time()
		result = {}
		cities = self._scenario.getCities()
		ncities = len(cities)
		population1 = [self.greedy(time_allowance).get('soln'), self.defaultRandomTour(time_allowance).get('soln'), self.defaultRandomTour(time_allowance).get('soln'), self.defaultRandomTour(time_allowance).get('soln'), self.defaultRandomTour(time_allowance).get('soln'), self.defaultRandomTour(time_allowance).get('soln')]

		for i in range(ncities):
			newPopulation = [] # Not sure if i'll usethis
			minArray = []
			#Selection
			for j in range(len(population1)):
				minArray.append(population1[j].cost)
			minimum = min(minArray)
			parent1 = 0
			parent2 = 0
			minIndex1 = np.argmin(minArray)
			minArray = np.delete(minArray, minIndex1)
			minIndex2 = np.argmin(minArray) + 1
			parent1 = population1[minIndex1]
			parent2 = population1[minIndex2]
			print(parent1.cost)
			print(parent2.cost)
			# Crossover
			child1Route = parent1.route
			child2Route = parent2.route

			point = random.randint(1, ncities)
			print("test")

			for x in range(len(child1Route)):
				if child1Route[x]._index == point:
					swap1Index = x
				elif child2Route[x]._index == point:
					swap2Index = x
			print(swap1Index)
			print(swap2Index)

			print("Original:")
			for x in range(len(child1Route)):
				print(child1Route[x]._index)
			child1Route[swap1Index], child1Route[swap2Index] = child1Route[swap2Index], child1Route[swap1Index]
			child2Route[swap1Index], child2Route[swap2Index] = child2Route[swap2Index], child2Route[swap1Index]
			child1 = TSPSolution(child1Route)
			child2 = TSPSolution(child2Route)
			print("New: ")
			for x in range(len(child1Route)):
				print(child1Route[x]._index)


		pass
