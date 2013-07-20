#!/usr/bin/env python

'''
Implemented at V2_ Lab, for documentation see

	* http://trac.v2.nl/wiki/MoveMeDocumentation

'''

import numpy, math

from MoveMe.SensorEvaluation.general_evaluators import *



class PressurePreprocessing(BasicEvaluator):
	''' Calculates various basic statistic values such as mean, difference,
	variance and standard deviation. '''

	def __init__(self,
			composite_evaluator,
			name,
			maximum_taxel_value=4096., minimum_taxel_value=0., max_color_value=255,):

		self.name = name
		self.maximum_taxel_value = maximum_taxel_value
		self.minimum_taxel_value = minimum_taxel_value
		self.max_color_value = max_color_value
		self.config_dict = composite_evaluator.pillow.config.dict

		#self.lowpass_neighbours = 70	# Lowpass value for Norm's
						# average-neigbours algorithm.

		super(PressurePreprocessing, self).__init__(composite_evaluator, name)

		# Touchpad matrix dimensions.
		self.width = self.composite_evaluator.pillow.matrix_rows
		self.height = self.composite_evaluator.pillow.matrix_cols

		# Session minimum and maximum for cleaned data.
		self.min = numpy.zeros((self.width, self.height), float)
		self.min.fill(maximum_taxel_value)
		self.max = numpy.zeros((self.width, self.height), float)

		# Data from which outliers have been substituted with
		# corresponding taxel value from previous buffer item
		self.cleaned_data = numpy.zeros((self.width, self.height), float)

		# Session minimum and maximum for standard deviations data.
		self.sd_min = numpy.zeros((self.width, self.height), float)
		self.sd_min.fill(maximum_taxel_value)
		self.sd_max = numpy.zeros((self.width, self.height), float)

		# Matrices for statistics parameters.
		self.mean = numpy.zeros((self.width, self.height), float)
		self.diff = numpy.zeros((self.width, self.height), float)
		self.var = numpy.zeros((self.width, self.height), float)
		self.sd = numpy.zeros((self.width, self.height), float)

		# Data that has been normalized against session maximums /
		# minimums.
		self.normalized_data = numpy.zeros((self.width, self.height), float)
		self.normalized_sd = numpy.zeros((self.width, self.height), float)

		# Matrices that have been scaled between 0 and max_color_value
		# (256 for RGB)
		self.visualization_cleaned = numpy.zeros((self.width, self.height), int)
		self.visualization_nrml = numpy.zeros((self.width, self.height), int)
		self.visualization_sds = numpy.zeros((self.width, self.height), int)



	def evaluate(self, raw_data):
		''' Main function to be called externally, return standard deviations matrix. '''

		raw_data = raw_data.astype(float) # Numpy type cast.

		# Stall preprocessing if the size of the buffer has changed.
		if self.config_dict['buffer_size'][0] == 0:
			print '!!!Empty buffer is not allowed'

		elif self.config_dict['buffer_size'][0] > len(self.buffer):
			# Building up new buffer with raw data.
			self.append(raw_data)

		elif self.config_dict['buffer_size'][0] < len(self.buffer):
			# Remove oldest buffer item.
			self.buffer.pop(0)

		elif self.config_dict['buffer_size'][0] == len(self.buffer):

			lowpassed_data = self.numpyLowPassFilter(raw_data, self.config_dict['lowpass_previous'][0])	# Some denoising.
			self.cleaned_data = self.statistics(lowpassed_data)				# Do the actual processing.
			self.append(self.cleaned_data)							# Append raw data with outliers removed.

		# Most important stuff is returned in a dictionary, the rest
		# (such as mean or variance) could be used by accessing the
		# class globals.

		dict = {}

		dict['normalized_data'] = self.normalized_data
		dict['cleaned_data'] = self.cleaned_data
		dict['mean'] = self.mean
		dict['standard_deviations'] = self.sd
		dict['visualization_cleaned'] = self.visualization_cleaned
		dict['visualization_normalized'] = self.visualization_nrml
		dict['visualization_standard_deviations'] = self.visualization_sds

		return dict


	def statistics(self, data):
		''' Numpy implementation of statistical analysis of the
		touchpad pressure data. This is the main matrix calculation
		loop, another one is located in pressure_center_of_gravity.py
		(but might need to be moved here as well).

		It is based on Stock's ideas and common standard deviation
		math, see:

			http://en.wikipedia.org/wiki/Standard_deviation
		'''

		n = len(self.buffer)
		denumeration = numpy.ndenumerate(data)

		for position, value in denumeration:

			if value > self.mean[position] + 2*self.sd[position] or value < self.mean[position] - 2*self.sd[position]:
				# Remove outliers; We assume an outlier has a
				# deviation outside -2sigma and 2sigma of a
				# normal distribution. If found it resets
				# previous value (last buffer item).
				data[position] = self.buffer[-1][position]

			if data[position] > self.maximum_taxel_value:
				self.maximum_taxel_value = data[position]
				string = 'data is larger than maximum-taxel-value preset, resetting to: %d' % data[position]
				raise MaximumTaxelValueError(string)

			else:
				self.visualization_cleaned[position] = self.scale4Visualization(data[position])

			if value < self.min[position]: self.min[position] = value
			if value > self.max[position]: self.max[position] = value

			if not self.max[position] - self.min[position] > 0:
				# In case minimum and maximum values have not
				# yet been updated.
				self.normalized_data[position] = 0

			else:
				self.normalized_data[position] = (value - self.min[position]) / (self.max[position] - self.min[position])


			self.mean[position] = (value + self.mean[position] * n) / (n + 1)
			self.diff[position] = (value - self.mean[position]) ** 2
			self.var[position] = (self.diff[position] + self.var[position] * n) / (n + 1)

			sd = numpy.sqrt(self.var[position])

			self.sd[position] = sd

			if sd < self.sd_min[position]: self.sd_min[position] = sd
			if sd > self.sd_max[position]: self.sd_max[position] = sd

			self.visualization_nrml[position] = int(self.normalized_data[position] * self.max_color_value)

			if self.sd[position] < self.config_dict['sd_calibration'][0]:
				self.visualization_sds[position] = 0
			else:
				self.normalized_sd = (self.sd[position] - self.sd_min[position]) / (self.sd_max[position] - self.sd_min[position])
				self.visualization_sds[position] = int(self.normalized_sd * self.max_color_value)

		return data


	def scale4Visualization(self, value):
		''' Convert to a scaled (rgb) value for the visualization.'''

		range = self.maximum_taxel_value - self.minimum_taxel_value
		scaled = value / range

		return int(scaled * self.max_color_value)


	def numpyLowPassFilter(self, data, percentage):
		''' A heuristic filter to smoothen signal change. Assumes a
		full buffer. '''

		percentage1 = percentage/100
		percentage2 = 0.5 * percentage/100 # TODO? Connect to slider.

		if len(self.buffer) >= 2:
			lowpass1 = (1-percentage1) * data + percentage1 * self.buffer[-1]

			lowpass2 = (1-percentage2) * lowpass1 + percentage2 * self.buffer[-2]
			return lowpass2

		else:
			return data


	def changeBufferSize(self, value):
		''' Changes buffer size, see evaluate() routine for actual buffer resizing. '''

		self.config_dict['buffer_size'][0] = value



	def averageWithNeighbours(self, data, position):
		''' Numpy implementation of Norm Jaffe's averaging algorithm. Not used because of heavy CPU load. '''

		# In principle x corresponds to the (touch)matrix width. However, in
		# numpy x corresponds to first item in first onedimensional
		# array (the first row or data[0]).  Therefore the mapping of
		# positional coordinates rather unintuitively reads (y,x)
		# instead of (x,y)
		y = position[0]
		x = position[1]

		width = self.width - 1
		height = self.height - 1

		value = 0

		# Point not on the edge of matrix; average
		# pressure calculated from nine points;
		#
		#	+---+---+---+---+--
		#	|   |   |   |   |
		#	+---+---+---+---+--
		#	|   | x0| x1| x2|
		#	+---+---+---+---+--
		#	|   | x3| x4| x5|
		#	+---+---+---+---+--
		#	|   | x6| x7| x8|
		#	+---+---+---+---+--
		#	|   |   |   |   |
		#
		# average = x0 + x1 + x2 + x3 + x4 + x5 + x6 + x7 + x8 / 9
		#
		# This should apply to the majority of points.
		#
		if not (x == 0 or y == 0 or x == width or y == height):
			slice = data[(y-1):(y+2),(x-1):(x+2)]

		# Point in the top-left corner;
		# calculates average pressure from four points
		#
		#	+---+---+---+---+--
		#	| x0| x1|   |   |
		#	+---+---+---+---+--
		#	| x2| x3|   |   |
		#	+---+---+---+---+--
		#	|   |   |   |   |
		#
		# average = x0 + x1 + x2 + x3 / 4
		#
		elif x == 0 and y == 0:
			slice = data[:2,:2]

		# Point in the top-right corner;
		elif x == width and y == 0:
			slice = data[:2,-2:]

		# Point in the bottom-left corner;
		elif x == 0 and y == height:
			slice = data[-2:,:2]

		# Point in the bottom-right corner;
		elif x == width and y == height:
			slice = data[-2:,-2:]

		# Averaging Edges; calulates edges from five points.
		#
		#	+---+---+---+---+--
		#	|   | x1| x0| x5|
		#	+---+---+---+---+--
		#	|   | x2| x3| x4|
		#	+---+---+---+---+--
		#	|   |   |   |   |
		#
		# average = x0 + x1 + x2 + x3 + x4 + x5 / 6

		elif x == 0:
			slice = data[(y-1):(y+2),:2]
		elif x == width:
			slice = data[(y-1):(y+2),-2:]
		elif y == 0:
			slice = data[:2,(x-1):(x+2)]
		elif y == height:
			slice = data[-2:,(x-1):(x+2)]

		return numpy.sum(slice) / len(numpy.ravel(slice))


	def double(self, data, width, height):
		''' Doubles the data matrix for better resolution. Not used
		yet: the CPU load gets too high...

		Example:

		+---+---+
		| 1 | 2 |
		+---+---+
		| 3 | 4 |
		+---+---+

			>>>

		+---+---+---+---+
		| 1 | 1 | 2 | 2 |
		+---+---+---+---+
		| 1 | 1 | 2 | 2 |
		+---+---+---+---+
		| 3 | 3 | 4 | 4 |
		+---+---+---+---+
		| 3 | 3 | 4 | 4 |
		+---+---+---+---+

		Note:

		if numpy.array:

			array([[0,0,0,0],[0,0,0,0]])

		then width == 4, height == 2; rows iterate over height, cols over width.

		'''

		doubled_data = numpy.zeros((2*width, 2*height), int)

		denumeration = numpy.ndenumerate(data)

		for position, value in denumeration:
			doubled_position_row_index1 = position[0]*2
			doubled_position_row_index2 = position[0]*2 + 1
			doubled_position_col_index1 = position[1]*2
			doubled_position_col_index2 = position[1]*2 + 1

			doubled_data[(doubled_position_row_index1, doubled_position_col_index1)] = data[position]
			doubled_data[(doubled_position_row_index2, doubled_position_col_index1)] = data[position]
			doubled_data[(doubled_position_row_index1, doubled_position_col_index2)] = data[position]
			doubled_data[(doubled_position_row_index2, doubled_position_col_index2)] = data[position]

		return doubled_data
