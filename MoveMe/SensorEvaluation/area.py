#!/usr/bin/env python

''' Implemented at V2_ Lab, for documentation see

	* http://trac.v2.nl/wiki/MoveMeDocumentation
'''

from copy import deepcopy


class Area(object):
	'''  '''

	def __init__(self, path):
		self.path = path


	def get(self):
		if self.path == []:
			return 0
		else:
			hull = self.convexHull(self.path)
			return self.areaConvexHull(hull)


	def orientation(self, p,q,r):
		'''Return positive if p-q-r are clockwise, neg if ccw, zero if
		colinear.'''

		return (q[1]-p[1])*(r[0]-p[0]) - (q[0]-p[0])*(r[1]-p[1])


	def convexHull(self, points):
		''' Andrew's Monotone Chain Algorithm. Nicked here:

			http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/117225
		'''

		U = []
		L = []

		sorted_points = deepcopy(points)
		sorted_points.sort()

		# Minimum & maximum values for x & y.
		x1 = sorted_points[0][0]
		x2 = sorted_points[0][0]
		y1 = sorted_points[0][1]
		y2 = sorted_points[0][1]

		for point in sorted_points:

			while len(U) > 1 and self.orientation(U[-2],U[-1], point) <= 0: U.pop()
			while len(L) > 1 and self.orientation(L[-2],L[-1], point) >= 0: L.pop()

			U.append(point)
			L.append(point)

			# Calculate bounding box coordinates of hull.
			if point[0] < x1: x1 = point[0]
			elif point[0] > x2: x2 = point[0]

			if point[1] < y1: y1 = point[1]
			elif point[1] > y2: y2 = point[1]

		self.bounding_box = [(x1, y1), (x2, y2)]

		return [U, L]


	def areaConvexHull(self, hull):
		''' http://mathworld.wolfram.com/PolygonArea.html '''

		hull = self.joinCCW(hull)

		sum = 0

		for i in range(len(hull)-1):
			point1 = hull[i]
			point2 = hull[i+1]

			sum += point1[0]*point2[1] - point2[0]*point1[1]

		determinant = sum / 2

		return abs(determinant)


	def joinCCW(self, hull):
		''' Make a single hull out of upper and lower part by
		discarding first and last point of upper hull and appending the
		points from back to front to lower hull.  '''

		lower_hull = hull[0]

		try:
			upper_hull = hull[1][1:-1]
		except:
			print 'upper hull is smaller than 2 points long.'

		for i in range(len(upper_hull)-1, -1, -1):
			lower_hull.append(upper_hull[i]) # Now becoming entire hull.

		return lower_hull


	def rotatingCalipers(self, hull):
		'''Given a list of 2d points, finds all ways of sandwiching the
		points between two parallel lines that touch one point each,
		and yields the sequence of pairs of points touched by each pair
			of lines.'''

		U,L = hull[0], hull[1]
		i = 0
		j = len(L) - 1

		while i < len(U) - 1 or j > 0:
			yield U[i],L[j]

			# if all the way through one side of hull, advance the other side
			if i == len(U) - 1: j -= 1
			elif j == 0: i += 1

			# still points left on both lists, compare slopes of next hull edges
			# being careful to avoid divide-by-zero in slope calculation
			elif (U[i+1][1]-U[i][1])*(L[j][0]-L[j-1][0]) > \
					(L[j][1]-L[j-1][1])*(U[i+1][0]-U[i][0]):
				i += 1
			else: j -= 1


	def diameter(self, hull):
		'''Given a list of 2d points, returns the pair that's farthest apart.'''

		diam, pair = max([((p[0]-q[0])**2 + (p[1]-q[1])**2, (p,q))
					for p,q in self.rotatingCalipers(hull)])

		return pair


