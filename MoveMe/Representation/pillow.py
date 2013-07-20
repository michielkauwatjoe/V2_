#!/usr/bin/env python

'''
Implemented at V2_ Lab, for documentation see

	* http://trac.v2.nl/wiki/MoveMeDocumentation
'''

#from MoveMe.OSC import client
from MoveMe.OSC import client_new as client
from MoveMe.SensorEvaluation import *
from MoveMe.SensorEvaluation.pressure_evaluator import PressureEvaluator
from MoveMe.SensorEvaluation.accelerometer_evaluator import AccelerometerEvaluator
from MoveMe.SensorEvaluation.magnetometer_evaluator import MagnetometerEvaluator
from MoveMe.Sios import device

from MoveMe.Representation.config import *
from MoveMe.Representation.Sound import Sound
from MoveMe.Representation.Gesture import *

import random
import pygame


class Peek:
	def __init__(self):
		self.up    = None
		self.value = None
		self.peek  = False
		self.threshold = 0.2
		self.count = 0
				
	def update(self, value):

		if self.value != None:
			# descending
			if self.value - value > self.threshold:
				if self.up:
					self.peek = True
					self.up   = False
				else:
					self.peek = False
					self.up   = False
			else:
				self.peek = False
			
			# ascending
			if value - self.value > self.threshold:
				self.up    = True
				self.peek = False
		
			
		self.value = value
		
		
class Pillow(client.Client):
	'''
	Pillow can send and receive OSC messages through inheritance from
	MoveMe.OSC.client.
	'''

	def __init__(self, context_manager, oscserver, dict):
		''' Any Pillow object should contain:

			* dict - pillow specific information (contextual)
			* sensor object(s)
		'''

		self.context_manager = context_manager
		self.oscserver = oscserver
		self.config = DefaultConfig()
				
		try:
			self.name = dict['name']
			self.host = dict['host']
			self.address = dict['address']
			self.port = dict['port']
			self.uri = dict['uri']
			self.device_description = self.getDeviceDescription(self.uri)

		except KeyError, e:
			raise PillowError(self.name, "Error in bonjour parameter: %s" % str(e))

		except Exception, e:
			raise PillowError(self.name, str(e))

		if not self.device_description:
			raise PillowError(self.name, "failed loading device description: %s" % self.uri)

		# if port from xml and propagated by zeroconf differ give preference 
		# to the zereoconf port because the xml not be generated properly
		if self.port != self.device_description.osc.port:
			print """
			Warning: port propagated by zeroconf (%d) does not match
			device description (%d). Using bonjour port.
			""" % (self.port, self.device_description.osc.port)

			self.device_description.osc.port = self.port

		self.id = self.device_description.id
		self.oscroot = self.device_description.osc.root

		# sort modules by class type (sensors / actuators / system)
		self.modules = {}

		# Contains general sensor evaluation objects.
		self.sensors = {}

		for c in self.device_description.classes:
			self.modules[c] = {}

		for item in self.device_description.modules.values():
			try:
				self.modules[item.sclass][item.name] = item
			except Exception, e:
				print '%s: module class mismatch (%s)' % (self.name, str(e))

		# FIXME: Visualization crashes if rows || cols are None (or 0) though this is a valid situation!!
		self.matrix_rows = self.matrix_cols = None 

		if self.modules['sensors'].has_key('matrix'):
			# Use pressure matrix description to connect pillow parameters.
			try: self.matrix_rows, self.matrix_cols = self.getTouchpadDimensions()
			except Exception, e:
				print "!!!!WARNING: %s: unable to get matrix dimensions (%s)" % (self.name, str(e))
				print "#####################################################################"
				print "#            FIXME: visualization will now crash!!!!                #"
				print "#####################################################################"
			else:
				self.oscserver.add(self.context_manager.pressureCB,
						self.modules['sensors']['matrix'].methods['data'].address)

				self.sensors['pressure'] = PressureEvaluator(self)

		if self.modules['sensors'].has_key('accmag'):
			if self.modules['sensors']['accmag'].methods.has_key('acc/data'):
				# Use accelerometer description to connect pillow parameters.
				self.oscserver.add(self.context_manager.accCB,
						self.modules['sensors']['accmag'].methods['acc/data'].address)

				self.sensors['acc'] = AccelerometerEvaluator(self)

			else:
				print '!!!WARNING: %s has no acc module ' % self.name

			if self.modules['sensors']['accmag'].methods.has_key('mag/data'):
				# Use magnetometer description to connect pillow parameters.
				self.oscserver.add(self.context_manager.magCB,
					self.modules['sensors']['accmag'].methods['mag/data'].address)

				self.sensors['mag'] = MagnetometerEvaluator(self)

			else:
				print '!!!WARNING: %s has no mag module' % self.name
		else:
			print '!!!WARNING: %s has no accmag module' % self.name
			
					
		client.Client.__init__(self, self.address, self.port, self.oscserver)

		self.active = False
		self.session = None

		# Number of packages received before pillow is considered being
		# active.
		self.minimum_package_count = 5
		self.initial_package_count = 0

		''' START RUI: added properties '''
		self.nextUpdateTime = 0
		self.mag = False
		self.acc = False
		self.accTimeStamp = 0
		self.nextLonelyTime = pygame.time.get_ticks() + random.randint(30,120)*1000
		
		self.tmp = None
		
		self.color = (0,0,0)
		self.buzzer = (0,0)
		self.__buzzer = True 
		self.__color = (0,0,0)
		self.gestureStamp = -1

		self.realtime		= RealTime()
		self.gesture 		= Gesture()
		self.motion 		= Peek()
		self.sound			= Sound()
		self.cog 			= (0, 0)		
		self.nextUpdateTime = 0

		self.debug = False
		''' END RUI '''

	def show(self, msg):
		if self.debug:
			print msg
		
	def activate(self):
		''' Handles the activation functionality within object and for
		OSC, partially depends on demo behaviour. '''

		# Pressure matrix activation.
		if self.sensors.has_key('pressure') and self.modules['sensors'].has_key('matrix'):
			self.show( " * %s: activating matrix" % self.name)
			#self.send(self.modules['sensors']['matrix'].methods['listen'].address)
			self.send({'address': self.modules['sensors']['matrix'].methods['listen'].address, 'args':[]})

		# Accelerometer/magnetometer activation.
		if self.modules['sensors'].has_key('accmag'):

			accmag = self.modules['sensors']['accmag']

#			if self.sensors.has_key('mag') and accmag.methods.has_key('mag/listen'): 
#				self.show( " * %s: activating magnetometer" % self.name )
#				#self.send(accmag.methods['mag/listen'].address)
#				self.send({'address':accmag.methods['mag/listen'].address, 'args':[]})
			if self.sensors.has_key('acc') and accmag.methods.has_key('acc/listen'): 
				self.show( " * %s: activating accelerometer" % self.name)
				#self.send(accmag.methods['acc/listen'].address)
				self.send({'address':accmag.methods['acc/listen'].address, 'args':[]})
				
		self.active = True

		self.show( ' * %s activated' % self.name )


	def getDeviceDescription(self, uri="http://isp.v2.nl/~simon/data/sios.xml"):
		''' Pillow should be initialized with an URI that refers to the
		Sios configuration XML, which is done automatically through the
		zeroconf adder in the context.

		If an uri is missing, a standard sios.xml is downloaded but
		this should not occur.
		'''

		# URI from initial dictionary.
		if uri.startswith('http://'):
			descr = device.from_uri(uri)
		else:
			descr = device.from_uri("http://" + self.address + "/" + uri)
		return descr


	def getTouchpadDimensions(self):
		''' Gets matrix row number and colnumber from configuration. '''

		try:
			rows = self.matrix_rows = int(self.modules['sensors']['matrix'].params['rows'].value)
			cols = self.matrix_cols = int(self.modules['sensors']['matrix'].params['cols'].value)

		except Exception, e:
			raise e
		else:
			return rows, cols


	def deactivate(self):
		''' Handles the deactivation functionality within object and
		for OSC, partially depends on demo behaviour. '''

		# currently de-activating all sensor data....
		for sensor in self.modules['sensors'].values():
			for method in sensor.methods.values():
				if method.name == 'silence':
					self.show( " * deactivating: %s: %s" % (sensor.name, method.address))
					#self.send(str(method.address))
					self.send({'address': str(method.address), 'args':[]})

		#self.send('/sios/sensors/matrix/silence')
		self.active = False
		self.initial_package_count = 0
		self.show( ' * pillow \'%s\' deactivated' % (self.name))


	def isActive(self):
		''' Returns the activity status as a boolean. '''

		return self.active


	def isInSession(self):
		''' Boolean to check if the pillow is currently in a session. '''

		return not self.session == None


	def adjustSensorParameter(self, sensor, parameter_name, value):
		''' interface from GUI to sensor parameters. '''

		self.sensors[sensor].adjustParameter(parameter_name, value)


	def evaluate(self, type, data):
		''' Interface to the sensor evaluation. '''

		if type == 'pressure':
			return self.sensors['pressure'].evaluate(data)

		elif type == 'acc':
			return self.sensors['acc'].evaluate(data)

		elif type == 'mag':
			return self.sensors['mag'].evaluate(data)

		else:
			print '!!!WARNING: unknown type %s, ignoring' % type


	''' ----------------------- Methods to control actuators ----------------------- '''

	def quit(self):
		#Turn off light
		self.lightFadeSingle((0,0,0))
		self.sweep(100, 50, 10, 16, 20, 500)
	
	''' *************** '''
	''' Sound           '''
	''' *************** '''


	def sweep_new(self, bug=False):
		''' duty range [0,50] and freq range [0,1500]'''

		if self.modules['actuators'].has_key('beep'):
			if bug:
				msg = 'sweepbug ', self.sound.freq_from, self.sound.freq_to, self.sound.duty_from, self.sound.duty_to, self.sound.freq_duration, self.sound.duration
				self.show(msg)
				self.send({ 'address': self.modules['actuators']['beep'].methods['sweepbug'].address
						  , 'args': [  self.sound.freq_from
								    , self.sound.freq_to
								    , self.sound.duty_from
								    , self.sound.duty_to
								    , self.sound.freq_duration
								    , self.sound.duration
								    , self.sound.sustain]
						  })
			else:
				address = self.modules['actuators']['beep'].methods['sweep'].address
				sounds  = []
				sound   = self.sound.fifo.get()
				while sound:
					(freq_from, freq_to, duty_from, duty_to, freq_duration, duration, sustain) = sound
					sounds.append({ 'address': address, 'args': sound })
					sound = self.sound.fifo.get()

				if sounds != []:
					self.show( 'sweep %s' % len(sounds))#, self.sound.freq_from, self.sound.freq_to, self.sound.duty_from, self.sound.duty_to, self.sound.freq_duration, self.sound.duration
					self.send(sounds)
				


	def sweep(self, freq_from, freq_to, duty_from, duty_to, freq_duration, duration, bug=False):
		''' duty range [0,50] and freq range [0,1500]'''
		self.sound.set(freq_from, freq_to, duty_from, duty_to, freq_duration, duration)
		if self.modules['actuators'].has_key('beep'):
			if bug:
				msg = 'sweepbug ', freq_from, freq_to, duty_from, duty_to, freq_duration, duration
				self.show(msg)
				self.send({ 'address': self.modules['actuators']['beep'].methods['sweepbug'].address
						  , 'args': [freq_from, freq_to, duty_from, duty_to, freq_duration, duration]})
			else:
				msg = 'sweep ', freq_from, freq_to, duty_from, duty_to, freq_duration, duration
				self.show(msg)
				self.send({ 'address': self.modules['actuators']['beep'].methods['sweep'].address
						  , 'args': [freq_from, freq_to, duty_from, duty_to, freq_duration, duration]})
	def playCooWee(self) :
		#print self.name, " lonely: CooWee! now = ", pygame.time.get_ticks()
		self.lightFadeInOut()	# chose new lights to blink
		if random.randint(0,1) : self.sweep(1210,1791,32,13,0,300)
		self.sweep(1050,959,13,0,0,221)

	def beep(self, volume, tone):
		''' Manages Beeper OSC calls. '''
		import random

		msecs = random.randrange(21,31)
		if self.modules['actuators'].has_key('beep'):
			self.send({ 'address': self.modules['actuators']['beep'].methods['beep'].address
					  , 'args': [tone,volume, msecs, 0]})
		
		msg= 'Beep ',volume,', ',tone, 'msecs',msecs
		self.show(msg)

	''' *************** '''
	''' Light           '''
	''' *************** '''
	def light(self, color, ledNum=-1):
		''' Interface to LED actuator. '''		
		(_1, _2, _3) = color
		color = (_1, _2, _3)

		if self.modules['actuators'].has_key('light') and color != self.color:
			self.color = color
			newColor = self.convertColor(color)
			
			if newColor != self.__color:
				self.__color = newColor
				(r,g,b) = newColor
				
				ledArg = []
				if ledNum != -1:
					ledArg = [ledNum]
					
				self.show('send to sios %s %s' % (self.__color, self.color))
				self.send({ 'address': self.modules['actuators']['light'].methods['rgb'].address
						  , 'args': (ledArg+[r,g,b])})

	def lightFadeSingle(self, color, msec=500):
		self.lightFade(False, color, msec, False)
		
	def lightFade(self, icolor, tcolor, msec, bounce=True, leds=False):

		if self.modules['actuators'].has_key('light') and tcolor != self.color:
			self.color = tcolor
			newColor = self.convertColor(tcolor)

			if newColor != self.__color:
				(tr, tg, tb) = self.__color = newColor

				if icolor == False:
					if bounce:
						self.show('blink %s' % newColor)
						self.send({ 'address': self.modules['actuators']['light'].methods['blink'].address
					  			  , 'args': [tr, tg, tb, msec]})
					else:
						self.show('trans %s' % newColor)
						self.send({ 'address': self.modules['actuators']['light'].methods['trans'].address
					  			  , 'args': [tr, tg, tb, msec]})
				else:
					(r, g, b) 	 = map(convert,icolor)
					if bounce:
						print 'blink ',(r, g, b),'-->',(tr, tg, tb) 
						self.send({ 'address': self.modules['actuators']['light'].methods['blink'].address
					  			  , 'args': [r, g, b, tr, tg, tb, msec]})
					else:
						print 'trans ',(r, g, b),'-->',(tr, tg, tb)
						self.send({ 'address': self.modules['actuators']['light'].methods['trans'].address
					  			  , 'args': [ r, g, b, tr, tg, tb, msec]})

	def convertColor(self, tcolor):
		''' Values in the range [0,255] are converted to [0,15]'''
		convert = lambda x: int(round(x*0.0588))
		return map(convert,tcolor)	
	
	def lightFadeInOut(self):
		if self.modules['actuators'].has_key('light') and self.modules['actuators']['light'].methods.has_key('blink'):
			#print 'Inactive lights on!'
			''' One led blinks faster '''
			
			# blink only a FEW lights when inactive, to save battery-power.
			
			# fade all lights to off first
			self.send({'address': self.modules['actuators']['light'].methods['trans'].address,
					'args': [0, 0, 0, 300]})
					
			bundle = []
			lights = range(8)
			while len(lights) > (8-3):
				l = random.choice(lights)
				lights.remove(l)
				duration = 1000 + random.randrange(1000)
				bundle.append({'address': self.modules['actuators']['light'].methods['blink'].address,
					'args':[l, 1, 1, 1, 15, 15, 15, duration]})
				#bundle.append({'address': self.modules['actuators']['light'].methods['flash'].address,
				#	'args':[l, 3, 100]})
				
			self.send(bundle)
				
			#self.send([{'address': self.modules['actuators']['light'].methods['blink'].address
				   	   #, 'args':[1, 1, 1, 15, 15, 15, 2000]}
					  #, {'address': self.modules['actuators']['light'].methods['blink'].address
					   #, 'args':[1, 1, 1, 1, 15, 15, 15, 1000]}
			 	      #])

	''' *************** '''
	''' Buzz			'''
	''' *************** '''
	def buzz(self, intensity, duration):
		''' The perceptible range of the buzzer is [100,255]. '''
		self.buzzer = (intensity, duration)
		if self.modules['actuators'].has_key('buzz'):
			print 'buzz ',self.buzzer,self.name
			self.send({ 'address': self.modules['actuators']['buzz'].methods['buzz'].address
		  			  , 'args': [intensity,duration]})

	def buzzFadeInOut(self):	
		''' The perceptible range of the buzzer is [100,255]. '''
		if self.modules['actuators'].has_key('buzz'):
			if self.modules['actuators']['buzz'].methods.has_key('sweep'):
				# print 'buzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz'
				self.send([{ 'address': self.modules['actuators']['buzz'].methods['sweep'].address
				  			, 'args':   [100,240,1000]}
						  ,{ 'address': self.modules['actuators']['buzz'].methods['sweep'].address
						    , 'args':   [240,235,5000]}
						  ,{ 'address': self.modules['actuators']['buzz'].methods['sweep'].address
						    , 'args':   [240,100,1000]}
						  ])


class PillowError(Exception):
	def __init__(self, pillow, msg):
		self.pillow = pillow
		self.msg = msg

	def __str__(self):
		return "pillowError '%s': %s" % (self.pillow, self.msg)

	def __repr__(self):
		return str(self)
