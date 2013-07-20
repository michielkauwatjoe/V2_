#!/usr/bin/env python

'''
Implemented at V2_ Lab, for documentation see

 http://trac.v2.nl/wiki/MoveMeDocumentation
'''

import time, datetime
import gobject

from time import sleep


class Engine(object):
	'''
	Sample code for a Engine that uses the ContextManager object to
	access information from the Representation module.
	'''

	def __init__(self, context_manager):
		'''
		Sets up globals and adds a callback with timeout to
		a listener.
		'''

		self.context_manager = context_manager
		self.history = []

		gobject.timeout_add(2, self.listen)


	def quit(self): pass


	def append(self, item):
		self.history.append(item)


	def listen(self):
		'''
		Main loop callback.
		Walks through open sessions, calls self.adapt() for each.
		'''

		for session in self.context_manager.context.sessions.values():
			if session.pillow.isActive():
				self.adapt(session)

		return True


	def adapt(self, session):
		''' Main adaptation function. '''

		person = session.person
		pillow = session.pillow

		self.do_something()

	def do_something(self): pass
