#!/usr/bin/env python

''' Implemented at V2_ Lab, for documentation see

	* http://trac.v2.nl/wiki/MoveMeDocumentation
'''


from MoveMe.SensorEvaluation.general_evaluators import *
from MoveMe.SensorEvaluation.magnetometer_preprocessing import MagnetometerPreprocessing


class MagnetometerEvaluator(CompositeEvaluator):

	def __init__(self, pillow):
		''' '''

		super(MagnetometerEvaluator, self).__init__("magnetometer_evaluator", pillow)
		self.pillow = pillow

		evaluator1 = MagnetometerPreprocessing(self)
		self.basic_evaluators[evaluator1.name] = evaluator1


	def evaluate(self, raw_data):
		''' '''
		return self.basic_evaluators['magnetometer_preprocessing'].evaluate(raw_data)
