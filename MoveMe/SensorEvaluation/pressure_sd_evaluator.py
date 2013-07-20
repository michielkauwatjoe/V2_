#!/usr/bin/env python

'''
Implemented at V2_ Lab, for documentation see

	* http://trac.v2.nl/wiki/MoveMeDocumentation

'''

import datetime
import numpy
import math

from MoveMe.SensorEvaluation.general_evaluators import *
from MoveMe.SensorEvaluation.area import *



class PressureSdEvaluator(BasicEvaluator):
	''' Operations that use sd-matrix from preprocessing.  '''


	def __init__(self,
				composite_evaluator,
				name,
				bottom_threshold,
				maximum_pad_value=4096,
				DT=0.2):

		self.name =                    name
		self.sustain_threshold =       66.6
		self.bottom_threshold =        bottom_threshold
		self.maximum_pad_value =       maximum_pad_value
		self.DT =                      DT
		self.active_taxels_threshold = 10

		super(PressureSdEvaluator, self).__init__(composite_evaluator, name)

		self.last_sampled =   datetime.datetime.now()
		self.center_of_gravity =  (0., 0.)
		self.displacement =  0.
		self.velocity =      0.
		self.acceleration =  0.
		self.angle =         0.
		self.event_state =   'nothing-happening'
		self.max_event_duration = 3.0
		self.event_start =   None
		self.event_lock =    False
		self.max_lock_duration = 2.0
		self.lock_start = None

		self.width =  self.composite_evaluator.pillow.matrix_rows
		self.height = self.composite_evaluator.pillow.matrix_cols
		self.center = self.setCenter(self.width, self.height)



	def setCenter(self, width, height):
		''' Center value should be set by composite evaluator before
		evaluation can be done. Value is 2.5 for 6x6 matrix.

		. 0   1   2   3   4   5
		+---+---+---+---+---+---+
		|top|left . | .top.right| 0
		+---+---+---+---+---+---+
		|top|left . | .top.right| 1
		+---+---+---+---+---+---+
		| . | . | . | . | . | . | 2
		+---+---+--2.5--+---+---+
		| . | . | . | . | . | . | 3
		+---+---+---+---+---+---+
		|bot.left . | .bot.right| 4
		+---+---+---+---+---+---+
		|bot.left . | .bot.right| 5
		+---+---+---+---+---+---+
		'''


		x = (float(width) - 1) / 2
		y = (float(height) - 1) / 2

		return (x, y)


	def evaluate(self, dict):

		now = datetime.datetime.now()
		center_of_gravity, intensity, area, event_state = self.standardDeviationsLoop(dict['cleaned_data'],
											dict['mean'],
											dict['standard_deviations'])

		if event_state == 'started':
			self.resetSpeed()
			self.last_sampled = now

		elif event_state == 'during':
			# Calculate time difference and convert to seconds.
			dt = now - self.last_sampled
			if dt.days > 0:
				raise TimeDeltaError('!!!ERROR: time elapsed longer than a day !?!')
			else:
				dt = dt.seconds + dt.microseconds * 0.000001

			# (Re)determine parameters every DT interval.
			if dt >= self.DT:
				self.getParameters(dt, center_of_gravity)
				self.last_sampled = now # reset

		self.center_of_gravity = center_of_gravity

		dict = {}

		dict['center_of_gravity'] = self.scaleCenterOfGravity(self.center_of_gravity)
		dict['intensity'] = intensity
		dict['area'] = area
		dict['angle'] = self.angle
		dict['velocity'] = self.velocity
		dict['acceleration'] = self.acceleration
		dict['displacement'] = self.displacement
		dict['event_state'] = event_state

		return dict


	def standardDeviationsLoop(self, data, mean, sd):
		''' Second important numpy loop, compares standard
		deviation matrix to:

		 * a threshold value
		 * absolute data values,
		 * mean data values.

		Calculates center of gravity and intensity.

		The algorithm looks at the centerpoints (.) and multiplies their
		values with their positions.

		. 0   1   2   3   4   5
		+---+---+---+---+---+---+
		| . | . | . | . | . | . | 0
		+---+---+---+---+---+---+
		| . | . | . | . | . | . | 1
		+---+---+---+---+---+---+
		| . | . | . | . | . | . | 2
		+---+---+---+---+---+---+
		| . | . | . | . | . | . | 3
		+---+---+---+---+---+---+
		| . | . | . | . | . | . | 4
		+---+---+---+---+---+---+
		| . | . | . | . | . | . | 5
		+---+---+---+---+---+---+

		'''

		Cx = cx = 0. # Total center value x, loop center value x.
		Cy = cy = 0. # Total center value y, loop center value y.

		event_state = None
		total = 0 # sum of all standard deviations above the threshold
		active_taxels = 0 # number of taxels that have a stable high or increasing value.
		area_list = []

		denumeration = numpy.ndenumerate(sd)

		for position, value in denumeration:

			x = position[1]
			y = position[0]

			if value < self.bottom_threshold:
				# Below sd threshold, value is too small.
				value = 0
				cx = cx + (x + 1)
				cy = cy + (y + 1)

			else:
				# Above threshold.

				# actual value of taxel larger than x
				# percent of mean plus standard deviation.
				# Guarantees relatively stable of increasing
				# average intensity.
				if data[position] > (mean[position] + sd[position]) * self.sustain_threshold / 100.:
					active_taxels += 1
					area_list.append(position)

				# Weighted average (give larger values more weight (**3)).
				cx = cx + (value**3) * (x + 1)
				cy = cy + (value**3) * (y + 1)

			total = total + value**3 + 1

		Cx = (cx / total) - 1
		Cy = (cy / total) - 1

		intensity = total / (self.width * self.height) / 1000000.
		area = Area(area_list)

		self.setEventState(active_taxels)
		return (Cx, Cy), intensity, area.get(), self.event_state



	def setEventState(self, active_taxels):

		if active_taxels >= self.active_taxels_threshold:

			if self.event_state == 'nothing-happening':
				if self.event_lock == False:
					self.event_state = 'started'
					self.event_start = datetime.datetime.now()
				else:
					# Lock timeout
					if self.lock_start != None:
						td = datetime.datetime.now() - self.lock_start
						td = td.seconds + td.microseconds / 1000000.

						if td > self.max_lock_duration:
							self.event_lock = False

			elif self.event_state == 'started':
				# After first loop state change to 'during'.
				self.event_state = 'during'

			elif self.event_state == 'during':

				if self.event_start != None:
					td = datetime.datetime.now() - self.event_start
					td = td.seconds + td.microseconds / 1000000.

					if td > self.max_event_duration:
						self.event_state = 'ended'
						self.event_lock = True
						self.lock_start = datetime.datetime.now()

			elif self.event_state == 'ended' and self.event_lock == True:
				self.event_state = 'nothing-happening'
		else:

			if self.event_lock == True:
				self.event_lock = False
				self.event_state = 'nothing-happening'

			elif self.event_state == 'during' or self.event_state == 'started':
				self.event_state = 'ended'

			elif self.event_state == 'ended':
				self.event_state = 'nothing-happening'


	def getParameters(self, dt, center_of_gravity):
		''' Calculates the following properties of the center of gravity:

			* displacement,
			* movement angle,
			* velocity,
			* acceleration,
		'''

		dx = center_of_gravity[0] - self.center_of_gravity[0]
		dy = center_of_gravity[1] - self.center_of_gravity[1]

		self.displacement = math.sqrt(dx**2 + dy**2)
		self.angle = self.getAngle(dx, dy, self.displacement)
		velocity = self.displacement / dt
		self.acceleration = (velocity - self.velocity) / dt
		self.velocity = velocity

		#print round(dt, 2), round(self.displacement, 2), round(velocity, 2), round(self.acceleration, 2), self.angle


	def resetSpeed(self):
		self.angle = 0
		self.velocity = 0.
		self.acceleration = 0.


	def scaleCenterOfGravity(self, center_of_gravity):
		''' Scale center-of-gravity points and cast to int, thus
		remembering one decimal point. '''

		x = int(center_of_gravity[0]*10)
		y = int(center_of_gravity[1]*10)

		return (x, y)


	def getAngle(self, p, r, q):
		''' Goniometric math to deduce CCW angle if p = x and r = y and
		q is their hypotenuse. '''

		if p == 0 and q == 0:
			return 0.
		else:

			if r == 0.:
				angle = math.degrees(math.asin(0))
			else:
				angle = math.degrees(math.asin(abs(r)/q))

		if p < 0 and p < 0:
			angle += 180
		elif p < 0:
			angle += 90
		elif q < 0:
			angle += 270

		return int(angle)


class PressureSdEvaluatorError(Exception):
	'''Base class for exceptions in this module.'''

	pass


class TimeDeltaError(PressureSdEvaluatorError):

	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)
