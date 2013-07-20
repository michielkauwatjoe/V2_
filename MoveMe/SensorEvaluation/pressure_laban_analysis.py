#!/usr/bin/env python

'''
Implemented at V2_ Lab, for documentation see

	* http://trac.v2.nl/wiki/MoveMeDocumentation

'''

import numpy
import datetime

from MoveMe.SensorEvaluation.general_evaluators import *
from MoveMe.SensorEvaluation.pressure_gesture import *



class PressureLabanAnalysis(BasicEvaluator):
	''' Laban analysis for a pressure signal created by a touch pad. This
	code is based on the Exhale implementation for the Whisper project by
	Norman Jaffe in cooperation with Thecla Schiphorst. '''


	def __init__(self, composite_evaluator, name):


		### Static global values

		self.current_pressure_gesture = None
		self.previous_pressure_gesture = None

		self.stamp_counter = 0
		self.gesture_parameter_interval = 0.5

		super(PressureLabanAnalysis, self).__init__(composite_evaluator, name)


	def evaluate(self, dict):
		''' Main function to be called from outside evaluator. '''

		now = datetime.datetime.now()


		if dict['event_state'] == 'started':
			stamp = self.stamp_counter
			self.current_pressure_gesture = PressureGesture(self, self.composite_evaluator.pillow.config.dict, now, stamp, dict)
			self.stamp_counter += 1
			return None

		elif dict['event_state'] == 'ended' and self.current_pressure_gesture != None:

			self.current_pressure_gesture.end(now)

			if self.previous_pressure_gesture == None:
				# The first gesture always gives incorrect
				# values because the statistics algorithms need
				# to calibrate.
				print ' * First gesture for %s (calibrating)' % self.composite_evaluator.pillow.name

				self.previous_pressure_gesture = self.current_pressure_gesture
				self.current_pressure_gesture = None

				dict = {'type': 'calibration'}
	
				return dict
			else:
				# Valid gesture, return it to pressure evaluator.
				complete_gesture = self.previous_pressure_gesture = self.current_pressure_gesture
				self.current_pressure_gesture = None

				if self.composite_evaluator.pillow.context_manager.print_summary == True:
					complete_gesture.printSummary()

				dict = {'type': 'gesture', 'gesture': complete_gesture}

				return dict

		elif dict['event_state'] == 'during' and self.current_pressure_gesture != None:
			
			self.current_pressure_gesture.process(now, dict)

			return None
