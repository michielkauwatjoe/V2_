#!/usr/bin/env python

''' Implemented at V2_ Lab, for documentation see

	* http://trac.v2.nl/wiki/MoveMeDocumentation
'''

from __future__ import generators

import math
import numpy
import datetime

from MoveMe.SensorEvaluation.general_evaluators import *
from MoveMe.SensorEvaluation.pressure_preprocessing import PressurePreprocessing
from MoveMe.SensorEvaluation.pressure_sd_evaluator import PressureSdEvaluator
from MoveMe.SensorEvaluation.pressure_laban_analysis import PressureLabanAnalysis



class PressureEvaluator(CompositeEvaluator):
	''' CompositeEvaluator implementation for pressure analysis. Chains several
	BasicEvaluator objects for pressure. '''

	def __init__(self, pillow):
		''' Creates new evaluator objects and puts them in the
		basic_evaluators dictionary. Derives:

			* statistics,
			* center of gravity (incl. speed & direction),
			* location events,
			* relative location (5 areas).
		'''

		super(PressureEvaluator, self).__init__("pressure_evaluator", pillow)

		self.basic_evaluators['pressure_preprocessing'] = PressurePreprocessing(self, 'pressure_preprocessing')
		self.basic_evaluators['pressure_sd_evaluator'] = PressureSdEvaluator(self, 'pressure_sd_evaluator', 150.)
		self.basic_evaluators['pressure_laban_analysis'] = PressureLabanAnalysis(self, 'pressure_laban_analysis')

		self.package_counter = 0

		#TODO link to slider in GUI
		self.refresh_rate = 1 # data rate (20hz) / 2 (~ 10 fps)

		# trajectory of center-of-gravity
		self.path = []


	def evaluate(self, raw_data):
		''' Main function to be called from outside the object. Transforms the data into
		a numpy array of the correct dimension, then runs it through a
		pipeline of evaluator objects. '''

		try:
			width = self.pillow.matrix_rows
			height = self.pillow.matrix_cols

		except:
			print 'Fatal Error: matrix dimensions not set (configuration file probably not received).'

		try:
			# Try to scale linear array to a numpy array.
			if not self.pillow.matrix_rows*self.pillow.matrix_cols == len(raw_data):
				msg = '!!!Incompatible dimensions: matrix dimensions don\'t match the dimensions specified in the configuration XML.'
				raise incompatibleDimensionsError(msg)

			else:
				raw_data = numpy.array(raw_data)
				raw_data = numpy.reshape(raw_data, (self.pillow.matrix_rows, self.pillow.matrix_cols))

		except Exception, e:
			print e
			print '!!!for', self.pillow.name
			print '!!!data length:', len(raw_data)
			print '!!!XML uri:', self.pillow.uri
			print '!!!XML configuration dimensions:', self.pillow.matrix_rows, '(rows)', self.pillow.matrix_cols, '(cols)'
			return None
		else:

			# Only process every 2nd package to optimize
			# multi-pillow scenario.  Results in a lower resolution
			# but in practice not much difference in signal
			# analysis accuracy.

			if self.package_counter == self.refresh_rate:

				pp_dict = self.basic_evaluators['pressure_preprocessing'].evaluate(raw_data)
				sd_dict = self.basic_evaluators['pressure_sd_evaluator'].evaluate(pp_dict)
				laban_dict = None

				try:
					laban_dict = self.basic_evaluators['pressure_laban_analysis'].evaluate(sd_dict)

				except Exception, e:
					print '!!!Error in Laban evaluator,', e

				joindict = dict(pp_dict, **sd_dict)

				# Writing preprocessed data (norm & sd) to the session buffer.
				# TODO: might want to add entire dict instead.
				self.pillow.session.updateData('pressure', [pp_dict['normalized_data'], pp_dict['standard_deviations']])
	
				# Only write when unlocked (i.e. after calibration).
				if self.pillow.session.lock == False:
					self.pillow.session.realtime_intensity = sd_dict['intensity']
					self.pillow.session.realtime_area = sd_dict['area']

				# Write gesture to session buffer once it is
				# finished.
				if laban_dict != None:

					if laban_dict['type'] == 'calibration':
						self.pillow.session.lock = False
					elif laban_dict['type'] == 'gesture':
						gesture = laban_dict['gesture']
						joindict['gesture'] = gesture
						self.pillow.session.realtime_parameters = None
						self.pillow.session.last_gesture = gesture


				self.package_counter = 0

				return joindict
			else:
				# Skipping a loop.
				self.package_counter += 1
				return None


	def adjustParameter(self, parameter_name, value):
		''' Interface from GUI to evaluation parameters; routes the
		variables to the various basic evaluators. '''

		if type(self.pillow.config.dict[parameter_name][0]) == float:
			self.pillow.config.dict[parameter_name][0] = float(value)
		elif type(self.pillow.config.dict[parameter_name][0]) == int:
			self.pillow.config.dict[parameter_name][0] = int(round(value))


class PressureEvaluatorError(Exception):
	'''Base class for exceptions in this module.'''

	pass


class incompatibleDimensionsError(PressureEvaluatorError):

	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)
