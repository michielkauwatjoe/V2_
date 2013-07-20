#!/usr/bin/env python

'''
Implemented at V2_ Lab, for documentation see

 http://trac.v2.nl/wiki/MoveMeDocumentation
'''

import time, datetime


class Person(object):
	'''
	Representation of a person within the user environment space.
	'''

	def __init__(self,
			firstname,
			lastname,
			rfid = None
			):
		''' Initializes a subset of the User Model. '''

		self.firstname = firstname
		self.lastname = lastname
		self.name = self.firstname + ' ' + self.lastname  #FIXME name should be fullname
		self.rfid = None
		self.session = None
		#self.location = 0
		self.event_buffer = [] # history of event actions
		self.event_trigger = False

		self.facts = {}
		self.facts['event_state'] = 'ended'
		self.facts['event_state_last_changed'] = datetime.datetime.now()


	def update(self, event_state):
		''' Evaluator data is converted to time related event_states .'''

		#if not location == None:
		#	if location != 0:
		#		self.location = location

		if not event_state == None:
			self.setEventStateDuration(event_state)


	def setEventStateDuration(self, event_state):
		''' Keeps track of duration current state. '''

		now = datetime.datetime.now()
		duration = now - self.facts['event_state_last_changed']


		if self.facts['event_state'] == 'started' and event_state == 'ended':
			#self.event_buffer.append([self.location, duration])
			self.event_trigger = True


		self.facts['event_state'] = event_state
		self.facts['event_state_last_changed'] = now


	def numberOfEvents(self):
		''' Returns entire number of events. '''

		n = 0

		for event in self.event_buffer:
			if event[1].seconds > 1.0:
				n += 1
		return n


	def numberOfCornerEvents(self):
		''' Returns number of events in corners (not in center, i.e.,
		not location value 0).  '''

		n = 0

		for event in self.event_buffer:
			if not event[0] == 0 and event[1].seconds > 1.0:
				n += 1
		return n


	def clearEventBuffer(self):
		''' Empties the event_buffer list object in Person (self). '''

		self.event_buffer = []


	def getEventStateDuration(self, event_state):
		''' Returns timedelta. '''

		if self.facts['event_state'] == event_state:
			now = datetime.datetime.now()
			return (now - self.facts['event_state_last_changed'])

		else:
			return None


	def isActive(self):
		if self.facts['event_state'] == 'started': return True
		else: return False


	def isInSession(self):
		''' Boolean to check if the pillow is currently in a session. '''

		return not self.session == None
