#!/usr/bin/env python

''' Implemented at V2_ Lab, for documentation see

	* http://trac.v2.nl/wiki/MoveMeDocumentation

The SensorEvaluation module implements preprocessing of data from hardware
sensors. The module is needed by the Pillow object in the Representation
module.
'''



class AbstractEvaluator(object):
	''' All Evaluator classes inherit from this one. Name should be
	specified by the implementing CompositeEvaluator object. '''

	def __init__(self, name):
		self.name = name


class BasicEvaluator(AbstractEvaluator):
	''' A BasicEvaluator processes the raw signal data for a certain
	modularity.  This base class contains the buffer, which should be set
	correctly to optimize performance. For example, at a frame rate of 20
	Hz the buffer is cleaned and the contents evaluated every 0.25s. '''

	def __init__(self, composite_evaluator, name, buffer_size=6):
		''' The BasicEvaluator object is always wrapped by a
		CompositeEvaluator object. It has a local buffer. '''

		self.composite_evaluator = composite_evaluator

		self.buffer = []
		self.buffer_size = buffer_size

		super(BasicEvaluator, self).__init__(name)


	def append(self, data):
		''' Adds numarray to buffer, if the buffer is full, pops the
		first one. '''

		if len(self.buffer) == self.buffer_size: self.buffer.pop(0)

		self.buffer.append(data)


	def lowPassFilter(self, value1, value2, percentage):
		''' A heuristic filter to smoothen signal change. '''

		percentage = float(percentage/100)
		return (1-percentage) * value1 + percentage * value2


class CompositeEvaluator(AbstractEvaluator):
	''' CompositeEvaluator is an abstract class that wraps several
	BasicEvaluator objects. '''

	def __init__(self, name, pillow):
		''' Initializes an empty dictionary of BasicEvaluator objects
		plus a reference to the parent Pillow object. '''

		self.pillow = pillow
		self.basic_evaluators = {}
		super(CompositeEvaluator, self).__init__(name)
