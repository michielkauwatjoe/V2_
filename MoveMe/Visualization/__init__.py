#!/usr/bin/env python

'''
Implemented at V2_ Lab, for documentation see

 http://trac.v2.nl/wiki/MoveMeDocumentation
'''

from MoveMe.OSC import client


class Visualization(client.Client):

	def __init(self, host, port):
		''' Connects to processing, http://www.processing.org. '''

		client.Client.__init__(self, host, port, None)


	'''
	def register(self, pillow):
		# Sends the name of the pillow to the processing program.

		self.send('/move-me', pillow.name)
	'''

	def data(self, data):
		self.send('/data', data)
