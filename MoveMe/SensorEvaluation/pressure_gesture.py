#!/usr/bin/env python

''' Implemented at V2_ Lab, for documentation see:

	* http://trac.v2.nl/wiki/MoveMe/SensorEvaluation/LabanAnalysis
	* http://trac.v2.nl/wiki/MoveMe/SensorEvaluation
	* http://trac.v2.nl/wiki/MoveMe
'''

from MoveMe.SensorEvaluation.moving_average import MovingAverage

import math
from copy import deepcopy
import datetime


class SurfaceEstimation(object):

	def __init__(self, time):

		self.surface = 0
		self.previous_value = 0
		self.t1 = time


	def __str__(self):
		return str(self.get())


	def get(self):
		''' Use this to get a currrent estimate of the surface. '''

		return round(self.surface, 0)


	def update(self, value, t2):

		td = t2 - self.t1
		td_micro = td.microseconds / 1000000.
		self.surface += (self.previous_value + (value - self.previous_value) / 2) * td_micro


		self.t1 = t2
		self.previous_value = value


class PressureGesture(object):

	def __init__(self, evaluator, thresholds, start_time, stamp, pressure_dict):

		self.evaluator = evaluator
		self.thresholds = thresholds
		self.start_time = start_time
		self.stamp = stamp
		self.end_time = None
		self.first_iteration = None
		self.cog_path = []
		self.convex_hull = None
		self.bounding_box = None
		self.diameter = None

		self.debug = False
		
		self.numeric_values = {}	# Collected numeric values.

		# Defaults.
		self.numeric_values['displacement'] = 0
		self.numeric_values['angle']        = 0
		self.numeric_values['delta_angle']  = 0

		# The following values are used to compute a sound
		# Please do not remove
		self.numeric_values['intensity'] = 0
		self.numeric_values['time']      = 0
		self.numeric_values['area']      = 0
		self.numeric_values['space']     = 0

		# Moving averages
		self.numeric_values['average_velocity'] = MovingAverage()
		self.numeric_values['average_acceleration'] = MovingAverage()
		self.numeric_values['average_displacement'] = MovingAverage()
		self.numeric_values['average_intensity'] = SurfaceEstimation(start_time)

		self.numeric_values['move_counter'] = 0
		#self.pause_counter = 0 # see comments categorizePath()

		# Collected Laban values that are derived from the numeric
		# values.
		self.laban_values = {
				'intensity': None,
				'time': None,
				'area': None,
				'space': 'stationary',
				'pattern': 'continuous',
				'path': 'straight',
				#'speed': None, # used indirectly to determine path
		}


		# Mapping from collected parameters to Laban matrix.
		self.parameter2matrix_mapping = ['intensity', 'time', 'area', 'number', 'space', 'pattern', 'path', 'intensity disposition']

		# Matrix for classification of Laban shapes. The order is important.
		self.laban_matrix = [
				['tap',		['soft', 'short', 'small', 'any', 'stationary', 'continuous', 'na', 'any']],
				['tapping',	['soft', 'short', 'small', 'any', 'stationary', 'repetitive', 'any', 'any']],
				['flick',	['soft', 'short', 'small', 'any', 'travelling', 'continuous', 'na', 'any']],
				['flicking',	['soft', 'short', 'small', 'any', 'travelling', 'repetitive', 'any', 'any']],
				['pat',		['soft', 'short', 'medium', 'one', 'any', 'continuous', 'any', 'any']],
				['patting',	['soft', 'short', 'medium', 'any', 'any', 'repetitive', 'any', 'any']],
				['pat',		['soft', 'short', 'big', 'one', 'any', 'continuous', 'any', 'any']],
				['patting',	['soft', 'short', 'big', 'any', 'any', 'repetitive', 'any', 'any']],
				['touch',	['soft', 'long', 'small', 'any', 'stationary', 'continuous', 'na', 'any']],
				['touches',	['soft', 'long', 'small', 'any', 'stationary', 'repetitive', 'na', 'any']],
				['hold',	['soft', 'long', 'big', 'one', 'stationary', 'continuous', 'na', 'any']],
				['holds',	['soft', 'long', 'big', 'one', 'stationary', 'repetitive', 'na', 'any']],
				['glide',	['soft', 'long', 'any', 'any', 'travelling', 'continuous', 'wandering', 'any']],
				['glides',	['soft', 'long', 'any', 'any', 'travelling', 'repetitive', 'wandering', 'any']],
				['stroke',	['soft', 'long', 'any', 'any', 'travelling', 'continuous', 'straight', 'any']],
				['stroking',	['soft', 'long', 'any', 'any', 'travelling', 'repetitive', 'straight', 'any']],
				['jab',		['hard', 'short', 'small', 'one', 'stationary', 'continuous', 'na', 'any']],
				['jabbing',	['hard', 'short', 'small', 'one', 'any', 'repetitive', 'na', 'any']],
				['cut',		['hard', 'short', 'small', 'one', 'travelling', 'continuous', 'na', 'any']],
				['knock',	['hard', 'short', 'medium', 'one', 'stationary', 'continuous', 'na', 'any']],
				['knocking',	['hard', 'short', 'medium', 'one', 'any', 'repetitive', 'na', 'any']],
				['slice',	['hard', 'short', 'medium', 'one', 'travelling', 'continuous', 'na', 'any']],
				['slap',	['hard', 'short', 'big', 'one', 'any', 'continuous', 'na', 'any']],
				['slapping',	['hard', 'short', 'big', 'one', 'any', 'repetitive', 'na', 'any']],
				['knead',	['hard', 'long', 'any', 'many', 'any', 'continuous', 'na', 'varying']],
				['kneads',	['hard', 'long', 'any', 'many', 'any', 'repetitive', 'na', 'varying']],
				['press',	['hard', 'long', 'any', 'any', 'stationary', 'continuous', 'na', 'constant']],
				['presses',	['hard', 'long', 'any', 'any', 'stationary', 'repetitive', 'na', 'any']],
				['rub',		['hard', 'long', 'any', 'any', 'travelling', 'continuous', 'any', 'any']],
				['rubbing',	['hard', 'long', 'any', 'any', 'travelling', 'repetitive', 'any', 'any']],
				['presses',	['hard', 'long', 'any', 'one', 'stationary', 'continuous', 'na', 'varying']],
				['knead',	['hard', 'long', 'any', 'many', 'stationary', 'continuous', 'na', 'varying']],
				['kneading',	['hard', 'long', 'any', 'many', 'stationary', 'repetitive', 'na', 'varying']],
				['unknown',	['hard', 'short', 'small', 'many', 'stationary', 'any', 'na', 'any']],
				['unknown',	['hard', 'short', 'small', 'many', 'travelling', 'repetitive', 'any', 'any']],
				['unknown',	['hard', 'short', 'medium', 'many', 'stationary', 'any', 'na', 'any']],
				['unknown',	['hard', 'short', 'medium', 'many', 'travelling', 'repetitive', 'any', 'any']],
				['unknown',	['hard', 'short', 'big', 'many', 'stationary', 'any', 'na', 'any']],
				['unknown',	['hard', 'short', 'big', 'many', 'travelling', 'repetitive', 'any', 'any']],
				['unknown',	['soft', 'short', 'small', 'one', 'travelling', 'continuous', 'straight', 'any']],
				['impossible',	['soft', 'short', 'small', 'one', 'travelling', 'continuous', 'wandering', 'any']],
				['impossible',	['soft', 'short', 'small', 'many', 'travelling', 'continuous', 'straight', 'any']],
				['unknown',	['soft', 'short', 'small', 'many', 'travelling', 'continuous', 'wandering', 'any']],
				['impossible',	['soft', 'short', 'big', 'one', 'travelling', 'continuous', 'straight', 'any']],
				['unknown',	['soft', 'short', 'big', 'one', 'travelling', 'continuous', 'wandering', 'any']],
				['impossible',	['soft', 'short', 'big', 'many', 'stationary', 'continuous', 'na', 'constant']],
				['unknown',	['soft', 'short', 'big', 'many', 'stationary', 'repetitive', 'na', 'constant']],
				['unknown',	['soft', 'short', 'big', 'many', 'stationary', 'continuous', 'na', 'varying']],
				['unknown',	['soft', 'short', 'big', 'many', 'stationary', 'repetitive', 'na', 'varying']],
				['impossible',	['soft', 'short', 'big', 'many', 'travelling', 'continuous', 'straight', 'any']],
				['unknown',	['soft', 'short', 'big', 'many', 'travelling', 'continuous', 'wandering', 'any']],
				['impossible',	['hard', 'short', 'small', 'any', 'travelling', 'continuous', 'straight', 'any']],
				['unknown',	['hard', 'short', 'small', 'any', 'travelling', 'continuous', 'wandering', 'any']],
				['impossible',	['hard', 'short', 'medium', 'any', 'travelling', 'continuous', 'straight', 'any']],
				['unknown',	['hard', 'short', 'medium', 'any', 'travelling', 'continuous', 'wandering', 'any']],
				['impossible',	['hard', 'short', 'big', 'any', 'travelling', 'continuous', 'straight', 'any']],
				['unknown',	['hard', 'short', 'big', 'any', 'travelling', 'continuous', 'wandering', 'any']]]

		# Will be derived from collected parameters and laban matrix once gesture is
		# finished.
		self.laban_shape = None

		self.first_iteration = True
		self.appendPoint(pressure_dict['center_of_gravity'])

		if self.debug:
			print '   > start of gesture analysis'


	def getDuration(self):
		''' Returns time difference from start but then only floating
		point microseconds converted to seconds.'''

		td = datetime.datetime.now() - self.start_time
		return td.seconds + td.microseconds / 1000000.


	def appendPoint(self, point):
		''' Appends a new center-of-gravity point to the path. The
		points have been multiplied (scaled) by 10 and then cast to
		integers. '''

		self.cog_path.append(point)


	def process(self, now, pressure_dict):
		''' Is called from PressureLabanAnalysis during an active
		event, i.e. after 'event_state' == 'started', before
		'event_state' == 'ended'. '''

		self.first_iteration = False
		self.appendPoint(pressure_dict['center_of_gravity'])

		try:
			self.updateLabanParameters(now, pressure_dict)

		except KeyError, e:
			print '!!!KeyError in Laban parameters,', e
			raise
		except Exception, e:
			print '!!!Error updating Laban parameters,', e
			raise


	def end(self, now):
		''' End of the gesture; look for matching Laban shapes. '''

		if self.debug:
			print '   > end of gesture analysis'

		self.first_iteration = False
		self.end_time = now
		self.convex_hull, self.bounding_box = self.convexHull(self.cog_path)

		self.categorizeArea()
		self.categorizeTime()
		self.categorizeIntensity()
		self.categorizeSpace()

		try:
			matching_shapes = self.labanMatrixLoop()

		except LabanParameterError, e:
			print e

		else:
			# Found one or more matching shapes, now we can
			# look if the shape was repetitive.
			self.categorizeRepetitive(matching_shapes)


	def printSummary(self):
		''' Prints out current contents of numeric values and Laban
		values dictionaries. '''

		print ' * Gesture summary:', self.evaluator.composite_evaluator.pillow.name, '#', self.stamp

		print '   - numeric values:'
		for key, value in self.numeric_values.items():
			if key == 'angle' or key == 'delta_angle':
				pass
			else:
				print '     * ', key, value

		print '   - Laban values:'
		for key, value in self.laban_values.items():
			print '     * ', key, value

		if self.laban_shape == None:
			print '   - unknown shape'
		else:
			print '   - matching Laban shape:', self.laban_shape[0]


	def updateLabanParameters(self, now, dict):
		''' Updates numeric parameters during gesture. '''

		if dict['area'] > self.numeric_values['area']: self.numeric_values['area'] = dict['area']

		self.numeric_values['displacement'] = self.calculateDisplacement() 

		self.numeric_values['average_displacement'].update(self.numeric_values['displacement'])
		self.numeric_values['average_velocity'].update(abs(dict['velocity']))
		self.numeric_values['average_acceleration'].update(dict['acceleration'])
		self.numeric_values['average_intensity'].update(dict['intensity'], now)

		self.numeric_values['delta_angle'] = abs(self.numeric_values['angle'] - dict['angle'])
		self.numeric_values['angle'] = dict['angle']

		self.categorizePath()


	def labanMatrixLoop(self):
		''' Runs through dictionary of derived values, except for

			* 'repetitive', which is derived afterwards,
			* 'number' (number of spots)
			* 'intensity disposition'

		Returns a list of matching indices.
		'''

		shapes = []
		shape = None

		number_of_qualities = len(self.laban_matrix)
		number_of_parameters = len(self.laban_matrix[0][1])

		for i in range(number_of_qualities):

			for j in range(number_of_parameters):
				# Order in mapping corresponds to order of
				# parameters in laban matrix.

				parameter_name = self.parameter2matrix_mapping[j]


				if parameter_name == 'pattern' or parameter_name == 'number' or parameter_name == 'intensity disposition':
					# We're discarding the values 'pattern', 'number'
					# and 'intensity disposition'. 'pattern' should be
					# derived after this function.
					if parameter_name == 'intensity disposition':

						# Last parameter matches; if
						# the loop ends up here the
						# current shape matches; add it
						# to the shapes list.
						shapes.append(self.laban_matrix[i])

					continue

				elif not self.laban_values.has_key(parameter_name):
					string = 'Laban parameter is missing: %s' % parameter_name
					raise LabanParameterError(string)
					break
				else:
					parameter_value = self.laban_values[parameter_name] # get derived value
					parameter_list_matrix = self.laban_matrix[i][1] # get list of parameters for this shape
					parameter_matrix = parameter_list_matrix[j] # get parameter for this shape

					if parameter_matrix == 'any' or parameter_matrix == 'na':
						continue

					elif parameter_value != parameter_matrix:
						# Parameter value doesn't match, this
						# isn't the correct shape -
						# break out of this loop!
						break
					else:
						continue

		return shapes



	def calculateDisplacement(self):
		''' Calculates displacement between current c.o.g. and previous
		one. '''

		if len(self.cog_path) >= 2:
			dx = self.cog_path[-1][0] - self.cog_path[-2][0]
			dy = self.cog_path[-1][1] - self.cog_path[-2][1]

			return math.sqrt(dx**2 + dy**2)

		else:
			return 0


	def getNumericIntensity(self):

		self.categorizeTime()

		if self.numeric_values['time'] == 0:
			numeric_intensity = 0
		else:
			numeric_intensity = int(self.numeric_values['average_intensity'].get() / self.numeric_values['time'])

		return numeric_intensity


	def categorizeIntensity(self):
		''' Compares numeric_intensity (which is the average pressure)
		to the soft-hard threshold to determine the Laban intensity.
		'''

		numeric_intensity = self.numeric_values['average_intensity'].get()

		if (numeric_intensity > self.thresholds['soft_hard'][0]):
			laban_intensity = 'hard'
		else:
			laban_intensity = 'soft'

		self.numeric_values['intensity'] = numeric_intensity
		self.laban_values['intensity'] = laban_intensity


	def categorizeTime(self):
		''' Compares dt (numeric time difference) to the short-long
		threshold to determine the Laban time. '''


		if self.end_time != None:
			dt = self.end_time - self.start_time
		else:
			dt = datetime.datetime.now() - self.start_time

		if (dt.seconds) == 0:
			dt = dt.microseconds / 1000000.

		else:
			dt = dt.seconds + dt.microseconds / 1000000.



		if (dt > self.thresholds['short_long'][0]):
			laban_time = 'long'

		else:
			laban_time = 'short'

		self.numeric_values['time'] = dt
		self.laban_values['time'] = laban_time


	def categorizeArea(self):
		''' Checks if the path is big enough to do an area calculation,
		then determines Laban area based on hull area and thresholds.'''

		if (self.numeric_values['area'] > self.thresholds['medium_large'][0]):
			laban_area = 'big'

		elif (self.numeric_values['area'] > self.thresholds['small_medium'][0]):
			laban_area = 'medium'

		else:
			laban_area = 'small'

		self.laban_values['area'] = laban_area


	def categorizeSpeed(self):
		''' Speed is not used yet. Seems to be identical to 'space',
		although space also takes negative speeds into account. '''

		if (self.numeric_values['average_velocity'] > self.thresholds['slow_fast'][0]):
			laban_speed = 'fast'
		else:
			laban_speed = 'slow'

		self.laban_values['speed']   = laban_speed


	def categorizeSpace(self):
		''' Space (stationary-travelling); is a function of (average) speed. If
		speed is (near) zero, then the gesture is stationary, otherwise
		it's traveling. Positive and negative threshold value.

		TODO: the algorithm filters out large values against large
		negative values. This seems to be undesirable behaviour.
		'''

		if self.numeric_values['average_velocity'].get() > self.thresholds['stationary_travelling'][0]:
			self.laban_values['space'] = 'travelling'
		else:
			self.laban_values['space'] = 'stationary'

		self.numeric_values['space'] = self.numeric_values['average_velocity'].get()

	def categorizePath(self):
		''' (straight-wandering) '''

		delta_angle = self.numeric_values['delta_angle']
		displacement = self.numeric_values['displacement']
		wandering_angle = self.thresholds['wandering_angle'][0]
		hard_move_length = self.thresholds['hard_move_length'][0]
		soft_move_length = self.thresholds['soft_move_length'][0]

		self.categorizeIntensity()
		intensity = self.laban_values['intensity']

		if self.numeric_values['move_counter'] > self.thresholds['move_count'][0]:
			return
		
		# Hard and soft moves have different threshold values:
		if delta_angle > wandering_angle and intensity == 'hard' and displacement > hard_move_length:
			self.numeric_values['move_counter'] += 1

		elif delta_angle > wandering_angle and intensity == 'soft' and displacement > soft_move_length:
			self.numeric_values['move_counter'] += 1

		if self.numeric_values['move_counter'] == self.thresholds['move_count'][0]:
			self.laban_values['path'] = 'wandering'


		# Norm also implements a pause counter, which looks at near
		# zero speed movement. It resets the move counter it there's
		# too much inactivity. We look at space for an entire gesture,
		# so every move counts, although we could implement
		# on-the-fly stationary-travelling detection and then look at
		# the number of flips between the two states for a gesture.

		'''
		elif self.nearZero(self.laban_values['speed'], self.thresholds['stationary_moving'][0]):
			# Start a counter. If the counter is above pause length
			# then reset displacement and set to stationary.

			self.pause_counter += 1

			if (self.pause_counter > self.thresholds['hard_pause_length'][0] and self.laban_values['intensity'] == 'hard'):
				self.laban_values['space'] = 'stationary'
				self.numeric_values['move_counter'] = 0

			elif (self.pause_counter > self.thresholds['soft_pause_length'][0] and self.laban_values['intensity'] == 'soft'):
				self.laban_values['space'] = 'stationary'
				self.numeric_values['move_counter'] = 0
		else:
			self.pause_counter = 0
		'''


	def categorizeRepetitive(self, shapes):
		''' See if previous laban shape was the same. '''

		if len(shapes) == 0:
			if self.debug:
				print ' * No Laban shape matches'
			return

		elif len(shapes) == 1:
			#TODO check if the shape isn't repetitive
			self.laban_shape = shapes[0]
			self.laban_values['pattern'] = 'continuous'

		else:

			# Filter continuous shapes.
			unknowns = []
			continuous_shapes = []
			repetitive_shapes = []
			any = []

			for i in range(len(shapes)):
				shape = shapes[i]
				shape_name = shape[0]
				shape_parameters = shape[1]

				if shape_name == 'unknown' or shape_name == 'impossible':
					unknowns.append(shape)
				else:
					if shape_parameters[5] == 'repetitive':
						repetitive_shapes.append(shape)	
					elif shape_parameters[5] == 'continuous':
						continuous_shapes.append(shape)	
					elif shape_parameters[5] == 'any':
						any.append(shape)	
					else:
						print '!!!shape %s could not be filtered' % shape

			if self.evaluator.previous_pressure_gesture == None or self.evaluator.previous_pressure_gesture.laban_shape == None:
				# No previous gesture or shape; this is the
				# first gesture and is categorized incorrectly.
				# Highest ranking continuous shape is chosen.

				self.laban_shape = continuous_shapes[-1]
				self.laban_values['pattern'] = 'continuous'

			else:
				previous_shape = self.evaluator.previous_pressure_gesture.laban_shape
				if self.debug:
					print ' * Previous shape was:', previous_shape[0]

				# select highest ranking
				if len(continuous_shapes) > 0:
					highest_continuous_shape = continuous_shapes[-1]
					if self.debug:
						print ' * Highest ranking continuous shape:', highest_continuous_shape[0]
				else:
					highest_continuous_shape = None
					if self.debug:
						print ' * No continuous shape found'

				if len(repetitive_shapes) > 0:
					highest_repetitive_shape = repetitive_shapes[-1]
					if self.debug:
						print ' * Highest ranking repetitive shape:', highest_repetitive_shape[0]
				else:
					highest_repetitive_shape = None
					if self.debug:
						print ' * No repetitive shape found'

				if len(any) > 0:
					highest_any = any[-1]
					if self.debug:
						print ' * Highest ranking shape shape with \'any\' pattern value:', highest_any[0]
				else:
					highest_any = None
					if self.debug:
						print ' * No shape with \'any\' pattern value found'

				if not highest_any == None and previous_shape[0] == highest_any[0]:
					# 'Any' ranks highest (is this desirable?)
					self.laban_shape = highest_any

				elif not highest_repetitive_shape == None and previous_shape[0] == highest_repetitive_shape[0]:
					# Previous and current both same, repetitive, shape
					self.laban_values['pattern'] = 'repetitive'
					self.laban_shape = highest_repetitive_shape

				elif not highest_continuous_shape == None and not highest_repetitive_shape == None:
					# Previous is either current highest
					# ranking continuous or repetitive
					# shape.
					if previous_shape[0] == highest_continuous_shape[0] or previous_shape[0] == highest_repetitive_shape[0]:
						self.laban_values['pattern'] = 'repetitive'
						self.laban_shape = highest_repetitive_shape

					else:
						# No match, set to continuous.
						self.laban_shape = highest_continuous_shape
						self.laban_values['pattern'] = 'continuous'



		'''

		# See if shapes are the same
		if self.laban_shape[0] == self.evaluator.previous_pressure_gesture.laban_shape[0]:
			repetitive = True

		else:
			# See if current shape follows up previous shape.
			current_description = self.laban_shape[0]

			for i in range(self.number_of_known_qualities):
				if laban_matrix[i][0] == previous_description and laban_matrix[i+1][0] == current_description:
					repetitive = True

		if repetitive == True:
			self.laban_values['pattern'] = 'repetitive'
			print ' > laban: derived repetitive'
		else:
			self.laban_values['pattern'] = 'continuous'
			print ' > laban: derived continuous'
		'''


	def nearZero(self, value, threshold):
		''' Qualitative math function, looks if value is near zero. '''

		if value > threshold or value < -threshold:
			return False
		else:
			return True


	def signOf(self, value):
		''' Returns the sign of a float or an integer. '''

		if value < 0:
			return -1

		elif value == 0:
			return 0

		else:
			return 1



	''' Some auxilary math functions. '''

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

		hull = [U, L]
		bounding_box = [(x1, y1), (x2, y2)]

		return hull, bounding_box


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


class PressureGestureError(Exception):
	'''Base class for exceptions in this module.'''

	pass


class LabanParameterError(PressureGestureError):

	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)
