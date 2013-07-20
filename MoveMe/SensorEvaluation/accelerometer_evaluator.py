#!/usr/bin/env python

''' Implemented at V2_ Lab, for documentation see

	* http://trac.v2.nl/wiki/MoveMeDocumentation
'''


from MoveMe.SensorEvaluation.general_evaluators import *
from MoveMe.SensorEvaluation.accelerometer_preprocessing import AccelerometerPreprocessing


class AccelerometerEvaluator(CompositeEvaluator):

	def __init__(self, pillow):

		super(AccelerometerEvaluator, self).__init__("accelerometer_evaluator", pillow)
		self.pillow = pillow

		evaluator1 = AccelerometerPreprocessing(self)
		self.basic_evaluators[evaluator1.name] = evaluator1


	def evaluate(self, raw_data):

		list = self.basic_evaluators['accelerometer_preprocessing'].evaluate(raw_data)
		self.pillow.session.motion = list

		return list
