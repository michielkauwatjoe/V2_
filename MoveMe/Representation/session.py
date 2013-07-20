#!/usr/bin/env python

'''
Implemented at V2_ Lab, for documentation see

 http://trac.v2.nl/wiki/MoveMeDocumentation
'''

import datetime, time
import gobject



class Session(object):
	'''
	Session object contains a person, a pillow, and the buffer with the
	measurement results.
	'''

	def __init__(self, person, pillow):
		'''
		A session object consists of:

			* a timestamp
			* a reference to a person
			* a reference to a pillow
			* a buffer

		Recorded pressure data is stored here.
		'''

		self.timestamp = datetime.datetime.now()
		self.person = person
		self.pillow = pillow
		self.buffer = []
		self.last_gesture = None
		self.lock = True		# locked while calibrating.
		self.realtime_intensity = 0.
		self.realtime_area = 0.
		self.motion = None

		self.recording = False


	def updateData(self, modularity, data):
		'''
		Stores proccessed numpy matrices from the pillow
		sensors with a timestamp.
		'''
		# TODO: connect to GUI record button

		ts = time.time()

		if self.recording == True:
			self.buffer.append([modularity, ts, data])
		else:
			if not len(self.buffer) == 0:
				for i in range(len(self.buffer)):
					if self.buffer[i][0] == modularity:
						del self.buffer[i]

			self.buffer.append([modularity, ts, data])


	def getCurrentPressure(self):
		ts = None
		data = None
		data = (0, 0)

		for i in range(len(self.buffer)):
			if self.buffer[i][0] == 'pressure':
				ts = self.buffer[i][1]
				data = self.buffer[i][2]
				break

		return ts, data[0], data[1]
