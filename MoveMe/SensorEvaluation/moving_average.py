#!/usr/bin/env python

'''
Implemented at V2_ Lab, for documentation see

	* http://trac.v2.nl/wiki/MoveMeDocumentation

'''

class MovingAverage(object):
	''' Updates a small buffer to keep track of average. '''

	def __init__(self):

		self.sum = 0.
		self.average = 0.
		self.buffer_size = 10
		self.buffer = []

	def __str__(self):
		return str(self.get())


	def get(self):
		''' Use this to get a currrent estimate of the average. '''

		return self.average


	def update(self, value):
		''' Use this to update moving average. '''

		# Buffer full.
		if len(self.buffer) == self.buffer_size:
			# Pop oldest.
			self.sum -= self.buffer.pop(0)

		# Add new.
		self.buffer.append(value)
		self.sum += value

		if len(self.buffer) > 0:
			self.average = self.sum / len(self.buffer)
