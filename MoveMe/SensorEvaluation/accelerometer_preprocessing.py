#!/usr/bin/env python

'''
Implemented at V2_ Lab, for documentation see

	* http://trac.v2.nl/wiki/MoveMeDocumentation

'''

import numpy, math

from MoveMe.SensorEvaluation.general_evaluators import *


class AccelerometerPreprocessing(BasicEvaluator):

	def __init__(self,
			composite_evaluator,
			name='accelerometer_preprocessing', max_color_value=255):

		self.name = name
		self.max_color_value = max_color_value
		self.g_unit = 16384. # = 2**14
		super(AccelerometerPreprocessing, self).__init__(composite_evaluator, name)

		self.motion = 0


	def evaluate(self, raw_data):


		# First value is device index, always zero because there's only
		# one acc/mag inside the pillow.
		vector = numpy.array(raw_data[1:], float)

		raw_acc = vector / self.g_unit
		raw_l  = math.sqrt(numpy.inner(raw_acc, raw_acc))

		gravity_vector = self.numpyLowPassFilter(raw_acc, 95)

		l = math.sqrt(numpy.inner(gravity_vector, gravity_vector))

		p = 0
		normalized = gravity_vector / (l*p + (1-p))

		motion = raw_acc - normalized

		self.motion = motion + self.motion*0.9

		speed = math.sqrt(numpy.inner(self.motion, self.motion))

		self.append(gravity_vector)

		list = []

		list.append(speed)
		list.append(self.motion[0])
		list.append(self.motion[1])
		list.append(self.motion[2])
		list.append(raw_l)

		return list


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
