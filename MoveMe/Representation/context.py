#!/usr/bin/env python

'''
Implemented at V2_ Lab, for documentation see

	* http://trac.v2.nl/wiki/MoveMeDocumentation

Representation module, implements the model of the Multi-Pillow, Multi-Person
environment. __init__.py contains the Context and the ContextManager objects.

Other objects:

	* Pillow in pillow.py (TODO change to SoftObject)
	* Person in person.py
	* Session in session.py
	* MemoryDBInterface in memory.py
'''

import sys
import datetime, time
import gobject

import MoveMe.Zeroconf.zeroconf
from MoveMe.Representation.pillow import *
from MoveMe.Representation.person import *
from MoveMe.Representation.session import *
from MoveMe.Representation.memory import *
from MoveMe.Representation.config import *

from MoveMe.OSC import server, client
from MoveMe.Adaptation import *
from MoveMe.Sios import device
#from MoveMe.Visualization import *


class Context(object):
	''' Contains the three important dictionaries containing the Person,
	Pillow and Session objects.  '''

	def __init__(self):
		'''
		Initializes empty dictionaries for the Person, Pillow and Session
		objects.
		'''

		self.persons = {}
		self.pillows = {}
		self.sessions = {}


class ContextManager(object):
	''' 'ContextManager' provides an interface to the 'Context' object. It
	also manages the OSC callbacks to the system as well as the data
	exchange with the GUI and the database (DB). '''

	def __init__(self, gui, port):
		''' Creates an empty Context and fills it with objects from the
		database.  Sets up connections to various server functions such
		as OSC pressure data callback and the adaptation engine.
		Currently RFID and visualization are embedded in the design but
		not used. '''

		# Core functionality.
		self.gui = gui
		self.context = Context()
		self.oscserver = MoveMe.OSC.server.Server(port)
		self.memory_db_interface = MemoryDBInterface('memory.db')
		self.save_sessions = False
		self.print_summary = False

		self.adaptation_engine = Engine(self)

		# Uncomment this to connect to the Processing
		# visualization software. Has been tested to work.
		#self.visualization = Visualization('127.0.0.1', 12000)

		# This would be the connection to AMICO, was used for
		# the Paris Demonstrator.
		#self.amico = OSC.client('127.0.0.1', 57110, None)

		# Zeroconf pillow detection/deletion callback
		try:
			MoveMe.Zeroconf.zeroconf.discover(stype='_sios._udp', adder=self.addPillowSynced, remover=self.removePillowSynced)
		except Exception, e:
			print "Error with zeroconf discover (%s)" % str(e)
			print "Is mdnsd running?"

		# Hives stuff.
		self.hivesClients = {}
		self.oscserver.add(self.hivesAddCB, "/softn/add")
		self.oscserver.add(self.hivesDelCB, "/softn/del")


	def quit(self):
		''' Writes data to DB and deactivates all pillows. '''

		self.adaptation_engine.quit()

		for key, value in self.context.pillows.items():
			if value.isActive():

				# save session data
				self.closeSession(value)

				# log off pillows (OSC)
				value.deactivate()

		# commit, close cursor & connection
		self.memory_db_interface.quit()

		MoveMe.Zeroconf.zeroconf.destroy()


	def resetTable(self, name):
		''' Manages table deletions;

			* clears pillows, persons or sessions table from database,
			* re-adds pillows and persons in current context (if any).
		'''

		if name == 'pillows':
			self.memory_db_interface.deleteTable(name)

			for pillow in self.context.pillows.values():
				self.memory_db_interface.insertPillow(pillow)

		elif name == 'persons':
			self.memory_db_interface.deleteTable(name)
			for person in self.context.persons.values():
				self.memory_db_interface.insertPerson(person)

		elif name == 'sessions':
			self.memory_db_interface.deleteTable(name)

		return self.getTable(name)


	def getTable(self, name):
		''' Returns database table pillows, persons or sessions. '''

		return self.memory_db_interface.getTable(name)


	''' Hives Functionality '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	def hivesAddCB(self, data, source):
		''' Adding a Hives client to self.hivesClients dictionary. '''

		try:
			host = data[0]
			port = int(data[1])
		except Exception, e:
			print "Hives: error adding client '%s'" % str(e)

		try:
			# Host known.
			if self.hivesClients.has_key(host):

				list = self.hivesClients[host]

				if list != None:
					if list.count(port) > 0:
						print 'hives client already registered, host %s, port %s' % (host, port)
					else:
						self.hivesClients[host].append(port)
						print ' * added Hives client for known host ip, host %s, port %s' % (host, port)
			# Host unknown.
			else:
				self.hivesClients[host] = [port]
				print ' * added Hives client for new host ip, host %s, port %s' % (host, port)

		except Exception, e:
			print e



	def hivesDelCB(self, data, source):
		try:
			host = data[0]
			port = int(data[1])
		except Exception, e:
			try:
				host = source[0]
				port = int(source[1])
			except Exception, e:
				print "Hives: error delling client '%s'" % str(e)

		try:
			ports = self.hivesClients[host]
			if len(ports) <= 1:
				del self.hivesClients[host]
			else:
				for i in range(0, len(ports)):
					if clients[i] == port:
						del clients[i]
		except Exception, e:
			print "Hives: error delling client '%s'" % str(e)


	''' Pillow Functionality '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	def pressureCB(self, data, source):
		''' OSC pressure data callback handler.

		This is where the unprocessed pressure data enters the server
		application.  Determines which source the data is coming from
		and passes it to the correct pillow in the device model. '''

		pillow = self.getPillowBySource(source)

		if pillow == None:
			self.staleCB('pressure', source)
			
		elif pillow.isInSession():
			session = pillow.session
			dict = pillow.evaluate('pressure', data)

			# Received a dictionary with evaluation results.	
			if not dict == None:
				self.gui.redrawVisualization(pillow, dict)
			

				for host, ports in self.hivesClients.items():

					try:
						for port in ports:
							# Send intensity and
							# area after
							# calibration has
							# finished.
							if pillow.session.lock == False:
								intensity = int(round(dict['intensity']))
								area = int(round(dict['area']))
								pillow.sendUnbound(host, port, {'address': '/softn/pressure', 'args': [pillow.name, intensity, area]})

							# Send a gesture to
							# hives clients if any
							# exists.
							if dict.has_key('gesture'):
								if dict['gesture'].laban_shape != None:
									shape = dict['gesture'].laban_shape[0]
									pillow.sendUnbound(host, port, {'address': '/softn/laban', 'args': [pillow.name, shape]})
					except Exception, e:
						print '!!!WARNING: error sending to hives client: %s' % str(e)

				# FIXME: older link to person object, probably obsolete.	
				if dict.has_key('event_state'):
					session.person.update(dict['event_state'])


		else:
			# using a package count buffer in pillow;
			# pillow keeps sending a couple of packages after
			# deactivation due to network latency, check if number
			# of packages greater than n
			if pillow.initial_package_count < pillow.minimum_package_count:
				pillow.initial_package_count += 1
			else:
				print ' * pillow not in session yet, creating a new one'
				self.createSession(pillow)


	def magCB(self, data, source):
		''' OSC magnetometer data callback handler.

		This is where the unprocessed magnetometer data enters the
		server application.  Determines which source the data is coming
		from and passes it to the correct pillow in the device model. '''

		pillow = self.getPillowBySource(source)
				
		if pillow == None:
			self.staleCB('mag', source)

		else:
			if pillow.isInSession():
				list = pillow.evaluate('mag', data)
				self.gui.redrawProcessing(pillow, 'mag', list)

				motion_data = []
				motion_data.append(pillow.name)

				for value in list:
					value = int(value*40)
					motion_data.append(value)


				for host, ports in self.hivesClients.items():

					try:
						for port in ports:
							pillow.sendUnbound(host, port, {'address': '/softn/mag', 'args': motion_data})

					except Exception, e:
						print '!!!WARNING: error sending mag data to hives client: %s' % str(e)
			

	def accCB(self, data, source):
		''' OSC accelerometer data callback handler.

		This is where the unprocessed accelerometer data enters the 
		server application.  Determines which source the data is coming
		from and passes it to the correct pillow in the device model. ''' 

		pillow = self.getPillowBySource(source)

		if pillow == None:
			self.staleCB('acc', source)

		else:
			if pillow.isInSession():
				list = pillow.evaluate('acc', data)

				self.gui.redrawProcessing(pillow, 'acc', list)

				motion_data = []
				motion_data.append(pillow.name)

				for value in list:
					value = int(value*40)
					motion_data.append(value)


				for host, ports in self.hivesClients.items():

					try:
						for port in ports:
							pillow.sendUnbound(host, port, {'address': '/softn/acc', 'args': motion_data})

					except Exception, e:
						print '!!!WARNING: error sending acc data to hives client: %s' % str(e)


	def staleCB(self, type, source):
		'''Stale callback from unknown pillow; caused after force quit.'''

		(a,b) = source
		print "!!!WARNING: Stale callback %s from unknown pillow (%s:%d): sending deletion" % (type, a, b)
		c = client.Client(source[0], source[1], self.oscserver)
		if type == 'pressure':
			c.send("/sios/sensors/matrix/silence")
		elif type == 'acc':
			c.send("/sios/sensors/accmag/acc/silence")
		elif type == 'mag':
			c.send("/sios/sensors/accmag/mag/silence")


	def addPillowSynced(self, **dict):
		''' Hack to synchronize zeroconf callback threads with our main thread '''

		gobject.timeout_add(1, self.addPillow, dict)


	def addPillow(self, dict):
		''' Zeroconf handler.

		- See if pillow is already loaded in the context,
		- compare with other pillows on field uniqueness,
		- add new DB entry or update existing one.

		Exception should not be raised from within Zeroconf adder and remover callbacks.
		They are not caught and make non-fatals fatal. '''

		pillow = Pillow(self, self.oscserver, dict)

			
		# Already a pillow in context with that name.
		if self.context.pillows.has_key(pillow.name):
			print '!!!WARNING: pillow already loaded into context (name not unique)'
		else:
			# Get stored values.
			list = self.memory_db_interface.getRow('pillows', 'name', pillow.name)

			if len(list) == 0:
				# Pillow not recognized, add to database.
				self.memory_db_interface.insertPillow(pillow)
				self.gui.context_frame.new(pillow)
			else:
				# Pillow recognized from previous use.
				pillow.config = self.memory_db_interface.getPillowConfig(pillow.name)

				# See if values have changed.
				self.updatePillowFields(list[0], pillow)

			# Add to current context and GUI.
			self.context.pillows[pillow.name] = pillow
			self.gui.context_frame.register(pillow)

			# Uncomment when visualization is enabled.
			#self.visualization.register(pillow)

			print " * %s registered to context environment" % pillow.name

			pillow.activate()


	def removePillowSynced(self, **dict):
		''' Hack to synchronize zeroconf callback threads with our main thread '''

		gobject.timeout_add(1, self.removePillow, dict)


	def removePillow(self, dict):
		''' Zeroconf handler. Removes a pillow with name 'name' from
		context and GUI. '''

		try:
			name = dict['name']
			pillow = self.getPillowFromContext(name)

			if pillow == None:
				print '!!!Warning: No pillow %s in context to remove (%s)' % (name, str(dict))
			else:
				self.removeSessionForPillow(pillow)
				self.gui.remove(pillow)
				del self.context.pillows[name]
				print " * removed %s" % name

		except KeyError, e:
			print '!!!Warning: zeroconf removal message contains no pillow name: %s.' % str(e)
		except Exception, e:
			print '!!!Warning: exception during removal of pillow %s: %s.' % (name, str(e))



	def updatePillowFields(self, list, pillow):
		''' Check if some pillow parameters have changed since last
		time. '''

		if not pillow.id == list[1]:
			self.memory_db_interface.setValue('pillows', 'id', pillow.id, pillow.name)
		if not pillow.address == list[2]:
			self.memory_db_interface.setValue('pillows', 'address', pillow.address, pillow.name)
		if not pillow.host == list[3]:
			self.memory_db_interface.setValue('pillows', 'host', pillow.host, pillow.name)
		if not pillow.port == list[4]:
			self.memory_db_interface.setValue('pillows', 'port', str(pillow.port), pillow.name)


	def transformListToPillows(self, list):
		''' Gets a list of pillow parameters, transforms to pillows if
		possible then returns list of results. '''

		try:
			for set in list:
				dict = {}
				dict['name'] = set[0]
				dict['id'] = set[1]
				dict['addres'] = set[2]
				dict['host'] = set[3]
				dict['port'] = set[4]
				pillow = Pillow(self, self.oscserver, dict)
		except:
			return None


	def getPillowBySource(self, source):
		'''
		Used to identify a pillow by the OSC callback 'source' field,
		which contains only the 'address' and 'port' values and not 'name'.
		'''

		for p in self.context.pillows.values():
			if p.address == source[0] and p.port == source[1]:
				return p

		return None


	def getPillowFromContext(self, name):
		'''
		Looks up and returns pillow from context pillow list.
		'''

		if self.context.pillows.has_key(name):
			return self.context.pillows[name]
		else:
			return None


	def noPillows(self):
		''' True if context.pillows dictionary is empty. '''

		return self.context.pillows == {}


	def savePillowConfiguration(self, pillow):
		self.memory_db_interface.savePillowConfiguration(pillow)


	def restorePillowDefaultConfiguration(self, pillow):
		pillow.config = DefaultConfig()



	''' Person Functionality '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	def rfidActiveCB(self, rfid, source): pass


	def registerPerson(self, fullname, rfid):
		''' Handles the 'live' aspects of person detection:

			* extracts Person from database
			* assigns current rfid
			* adds Person to context.
			* adds Person to GUI.
		'''

		person = self.getPersonFromDB(fullname)
		person.rfid = rfid
		self.addPersonToContext(person)
		self.gui.context_frame.register(person)

		print ' * registered %s' % fullname
		return person


	def addPerson(self, firstname, lastname, rfid):
		''' Adds a new Person object:

			* is called from personnameDialog in GUI,
			* checks if person already exists in DB,
			* else inserts new person.
		'''

		person = Person(firstname, lastname, rfid)

		if self.memory_db_interface.insertPerson(person):
			return person
		else:
			return None


	def addPersonToContext(self, person):
		''' Simply adds object to Person dictionary in Context. '''

		self.context.persons[person.name] = person


	def getPersonFromContext(self, fullname):
		''' Get Person with key fullname from current Context if it exists. '''

		if self.context.persons.has_key(fullname):
			return self.context.persons[fullname]
		else:
			return None


	def getPersonFromDB(self, fullname):
		'''
			* Gets Person row with key name from database
			* returns 'firstname' and 'lastname' fields if 'fullname' exists,
			* else returns None.
		'''

		result = self.memory_db_interface.getRow('persons', 'fullname', fullname)
		if not result == []:
			return Person(result[0][1], result[0][2], None)
		else:
			return None


	def getPersonByRFID(self, rfid):
		'''
		Checks if a person exists with the rfid assigned to him/her.
			* Returns Person from the Context if rfid is assigned,
			* else returns None.
		'''

		for p in self.context.persons.values():
			if p.rfid == rfid: return p
			else: return None


	def removePerson(self, fullname):
		'''
		Removes Person object with fullname 'fullname' from database.
		'''
		self.memory_db_interface.deleteRow('persons', 'fullname', fullname)
		print " * removed %s from the database" % fullname


	''' Session Functionality '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''


	# FIXME disambiguate names createSession / addSession
	def createSession(self, pillow):
		''' Called before addSession. Here the RFID number from the XML
		config file, if any, will be coupled to a person object and a
		session is created. '''

		# substitute RFID string, not implemented in hardware
		rfid = 'test-rfid'
		person = self.getPersonByRFID(rfid)

		if person == None:
			# always select person 'Workshop Test' if exists

			name = 'Workshop Test'

			if not self.getPersonFromDB(name):
				name = self.gui.context_frame.personSelect(rfid)

			person = self.getPersonFromContext(name)

			if person == None:
				person = self.registerPerson(name, rfid)

		self.addSession(person, pillow)


	# FIXME disambiguate names createSession / addSession
	def addSession(self, person, pillow):
		''' Called when a pillow detects a user through RFID:
			* Creates new Session,
			* adds it to Context,
			* adds it to GUI
		'''

		try:
			session = Session(person, pillow)
			pillow.session = session
			person.session = session

			self.context.sessions[session.timestamp] = session
			self.gui.context_frame.new(session)
			self.gui.context_frame.register(session)

		except Exception, e:
			print 'Failed to add session.'
			raise Exception(e)


	def removeSessionForPillow(self, pillow):
		if pillow != None:
			if pillow.isInSession(): self.closeSession(pillow)
			if pillow.isActive(): pillow.deactivate()

			pillow.session = None


	def closeSession(self, pillow):
		'''
			* Adds Session to the database,
			* removes Session from GUI,
			* removes Session from Context.
		'''
		session = pillow.session

		if session == None:
			print '!!!WARNING: %s is not associated with any session!' % pillow.name
			return
		else:
			timestamp = session.timestamp

			if self.save_sessions == True:
				self.memory_db_interface.insertSession(session)

			try:
				del self.context.sessions[session.timestamp]
			except Exception, e:
				print '!!!Error: can\'t delete session (timestamp doesn\'t exist?)', e

			self.gui.remove(session)

			print " * removed session %s" % timestamp


	def getSessionValues(self, ts):
		''' Looks up Session parameters from either the Context or the database. '''

		values = {}
		values['ts'] = ts

		session = self.getSessionFromContext(ts)

		if not session == None:
			values['personname'] = session.person.name
			values['personrfid'] = session.person.rfid
			values['pillowname'] = session.pillow.name
			values['pillowid'] = session.pillow.id
			values['status'] = 'open'
		else:
			result = self.getSessionFromDB(ts)
			if result == None:
				return None

			else:
				values['personname'] = result[1]
				values['personrfid'] = result[2]
				values['pillowname'] = result[3]
				values['pillowid'] = result[4]
				values['status'] = 'closed'

				return values


	def getSessionFromContext(self, string):
		''' Returns Session with key 'ts' from current Context if it
		exists, else returns None. '''

		ts = self.string2ts(string)

		if self.context.sessions.has_key(ts):
			return self.context.sessions[ts]
		else:
			return None


	def string2ts(self, string):
		''' Auxilary function to convert timestamp in tring format to datetime object. '''

		time_format = "%Y-%m-%d %H:%M:%S"
		time_string, ms = string.split('.')
		i = 0
		ts_args = []

		stripped_args = time.strptime(time_string, time_format)
		ts_args[:6] = stripped_args[:6]
		ts_args.append(int(ms)) # strptime doesn't parse smaller floating point values.

		return datetime.datetime(*ts_args)


	def getSessionFromDB(self, ts):
		''' Returns parameters from Session with key 'ts' from the
		database if it exists, else returns None. '''

		result = self.memory_db_interface.getRow('sessions', 'ts', ts)

		if result == []:
			return None
		else:
			return result[0]



class ContextError(Exception):
	'''Base class for exceptions in this module.'''

	pass


class FalsePillowRemovalError(ContextError):

	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)
