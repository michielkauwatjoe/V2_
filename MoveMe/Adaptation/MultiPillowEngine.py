#!/usr/bin/env python

'''
Implemented at V2_ Lab, for documentation see

 http://trac.v2.nl/wiki/MoveMeDocumentation
'''

import time, datetime
import gobject
import MoveMe.MultiPillow.GUI.Simulator
import colorsys
import string
import random
from time import sleep

import pygame

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
		
		''' Creates a graphic scenario '''	
		self.simulator = MoveMe.MultiPillow.GUI.Simulator.Simulator()
		self.context_manager = context_manager
		self.history = []
		self.detectedPillows = {}
		self.debug = False
		
		gobject.timeout_add(20, self.listen)

		self.keyValues  = (0,0,0,0,0)

	def quit(self): 
		print 'Quiting...'
		for session in self.context_manager.context.sessions.values():
			if session.pillow.isActive():
				session.pillow.quit()

	def append(self, item):
		self.history.append(item)

	def listen(self):
		'''
		Main loop callback.
		Walks through open sessions, calls self.adapt() for each.
		'''
		activePillows = []
		for session in self.context_manager.context.sessions.values():
			if session.pillow.isActive():
				activePillows.append(session.pillow.name)
				self.adapt(session)

		''' remove inactive pillows '''
		self.removeInactivePillows(activePillows)

		''' Updates the room and then the graphic scenario '''
		self.simulator.update()
		return True

	def removeInactivePillows(self, activePillows):
		# TODO: BUG: I think pillows are not being removed correctly
		for pillowName in self.detectedPillows.keys():
			if not pillowName in activePillows:
				statePillowId = self.detectedPillows[pillowName]
				print ' *',pillowName,'removed from simulator.'
				self.simulator.removePillow(statePillowId)
				del self.detectedPillows[pillowName]

	def adapt(self, session):
		''' Main adaptation function. '''
		person = session.person
		pillow = session.pillow

		''' Detect pillow and connect it with a state pillow '''
		if not pillow.name in self.detectedPillows.keys():
			self.detectedPillows[pillow.name] = self.simulator.insertPillow(pillow.name)
			print ' * %s added to simulator.'%pillow.name

		self.updateStatePillow(person, pillow, session)


	def updateStatePillow(self, person, realPillow, session):

		''' 0. Get state pillow corresponding to real pillow '''
		statePillow = self.simulator.room.getPillow(self.detectedPillows[realPillow.name])
		statePillow.now = pygame.time.get_ticks()

		''' 1. Update state Pillow with sensor data '''
		self.updateMatrixSensor(statePillow, realPillow, session)
		realPillow.realtime.update(session)
		
		''' 2. Update actuactors of real Pillow '''
		
		self.updateBuzz(statePillow, realPillow)
		self.updateLight(statePillow, realPillow)
		##self.updateSound(statePillow, realPillow)
		
		self.motion2sound(statePillow, realPillow, session)

		''' TEST STUFF '''
		self.test(statePillow, realPillow)
		self.key2FadeBuzz(realPillow)

			
	''' 1. '''
	def motion2sound(self, statePillow, realPillow, session):	
		if session.motion:
			acc = session.motion[4]-1

			old_up = realPillow.motion.count			
			imp = False
			if acc > 0.33:
				#print 'up ---------------- ', acc, session.motion[0], realPillow.motion.count
				realPillow.motion.count +=1
				imp = True
				
			if acc < -0.66:
				#print 'dw ---------------- ', acc, session.motion[0], realPillow.motion.count
				realPillow.motion.count=0
				imp = True
		
			''' Pick detection '''
			if imp:
				old_acc = realPillow.motion.value
				realPillow.motion.update(round(acc,1))
				if realPillow.motion.peek:
					#print '/\\ ---------------- /\\', old_up
					#print old_acc
					#print realPillow.motion.value
					''' transform acceleration to sound '''
					if old_up > 13 and old_acc > 1: # and realPillow.motion.value<0.5):
						
						duration  = int(2250*(old_acc-1)/3.0)
						realPillow.sweep(650, 1169, 0, 26, 20, int(duration * 2./3.),1)
						realPillow.sweep(1169, 959, 26, 0, 20, int(duration * 1./3.))
						'''
						Intial Fly Sound

						highStart = 200 * 2
						highMid = 240 * 2
						highEnd = 250 * 2'
						realPillow.send(  [
								{ 'address': realPillow.modules['actuators']['beep'].methods['sweep'].address
									, 'args':   [highStart,highMid,0,26,0,500,0]
								}
								,
								{ 'address': realPillow.modules['actuators']['beep'].methods['sweep'].address
									, 'args':   [highMid,highEnd,26,24,0,900,0]
								}

							] )			
						'''
# Rui's Sound
#						freqLow	  = int(1000*(old_acc-1)/3.0)
#						if self.debug:
#							print '-----------',freqLow
#						duration  = int(1000*(old_acc-1)/3.0)
#						freqHigh  = freqLow+100
#						
#						realPillow.sweep(freqHigh, freqLow, 10, 16, 20, duration)
#						realPillow.sweep(freqLow,freqHigh, 10, 16, 20, duration)
#						'''
#						realPillow.sweep(600, 500, 10, 16, 20, 500)
#						realPillow.sweep(500, 600, 10, 16, 20, 500)
#						'''

	def	updateMatrixSensor(self, statePillow, realPillow, session):
		''' Update sounds after a touch. '''

		#if session.last_gesture != None:
		#	if session.last_gesture.numeric_values['area'] != None:
		#		print '--------->',session.last_gesture.numeric_values['area'] 


		#print self.simulator.room.groups[0].pillows

		index = 0 # hop count
		master_id = False
	
		''' updated touch info '''
		if realPillow.realtime.area.norm > 0.1 and realPillow.realtime.intensity.norm > 0.1:
			statePillow.touch.intensity = True
		else:
			statePillow.touch.intensity = False
		
		
		''' gesture is converted to chord and sended to pillow '''
		if session.last_gesture != None: #Simon's SIOS platform 2.0.3

			if realPillow.gestureStamp != session.last_gesture.stamp:
				# A new gesture occured.

				#statePillow.touch.intensity = True
				realPillow.gestureStamp = session.last_gesture.stamp
				
				#self.printGesture(session)
				self.touch2light(statePillow, realPillow, session.last_gesture)
							
				''' convert gesture to chord and send it to pillow '''
			
				gesture = session.last_gesture.laban_shape
	 
				realPillow.sound.convertGesture(gesture, realPillow, index)
				realPillow.sweep_new()

				master_id = self.detectedPillows[realPillow.name]

				for key, value in self.detectedPillows.items() :
					if index > 2 : # 0,1,2
						break
					slave = self.simulator.room.getPillow(self.detectedPillows[key]) # is-a StatePillow
				
					if slave.getSourceId() == master_id:
						index += 1
						print 'master %s has slave %s' % (realPillow.name, key)

						realSlavePillow = self.context_manager.getPillowFromContext(key)
						realSlavePillow.sound.convertGesture(gesture, realPillow, index)
						realSlavePillow.sweep_new()

			else:
				#statePillow.touch.intensity = False
				pass
			
	def printGesture(self, session):
		print 'Gesture values:'
		print '\t\t area: \t',session.last_gesture.numeric_values['area']
		print '\t\t intensity: ',session.last_gesture.numeric_values['intensity']
		print '\t\t space: \t',session.last_gesture.numeric_values['space']
		print '\t\t time: \t',session.last_gesture.numeric_values['time']
		# print session.last_gesture.stamp, session.last_gesture.laban_shape
			
	
	''' 2. '''
	def updateSound(self, statePillow, realPillow):
		#self.key2Light(realPillow)
		#self.touch2Beep(statePillow, realPillow)
		pass
		

	def updateLight(self, statePillow, realPillow):
		''' Pillow just become inactive '''
		if statePillow.state == "INACTIVE" and statePillow.state != statePillow.prevState:
			#print '- Pillow is inactive'
			realPillow.lightFadeInOut()

		''' Pillow is not inactive '''
		if statePillow.state != "INACTIVE":
			# print 'Pillow is not inactive'
			realPillow.lightFadeSingle(statePillow.color)


	def updateBuzz(self, statePillow, realPillow): ## HERE - mcb
		''' Buzz if acc inverted but maximum only once per second '''
		now = pygame.time.get_ticks()
		if realPillow.accTimeStamp < now: # accTimeStamp is the last time it vibrated + 60 sec
			if realPillow.realtime.area.norm > 0.5 and realPillow.realtime.intensity.norm > 0.5 :
				realPillow.buzzFadeInOut()
				if self.debug:
					print '*',realPillow.name,'Buzz: '
					print realPillow.realtime.show()
				realPillow.accTimeStamp = now + 60000
				realPillow.nextLonelyTime = now + random.randint(60,120) * 1000
			else :
				if statePillow.state == 'INACTIVE' :
					# did not buzz but could have, then we are lonely
					if now - realPillow.nextLonelyTime > 120*1000 :
						# we have not been lonely for a long time, must have
						# been active so to prevent sound immediate with all the
						# others delay for up to 1 min
						realPillow.nextLonelyTime = now + random.randint(10,50) * 1000
						print "Lonely Soon"
					else :
						# in a lonely cycle
						if realPillow.nextLonelyTime <= now :
							realPillow.playCooWee()
							realPillow.nextLonelyTime = now + random.randint(60,120) * 1000
			'''
			# print realPillow.accTimeStamp, '<', now 
			tmp = realPillow.sensors['pressure'].basic_evaluators['pressure_event_detection'].locate()
			#print tmp ,'!=', statePillow.touch.corners
			if tmp != statePillow.touch.corners and tmp != 0:
				realPillow.accTimeStamp = now + 60000
				print 'buzzFadeInOut ',realPillow.name
				realPillow.buzzFadeInOut()
			'''
		#self.buzzFadeInOut(realPillow)
	def touch2light(self, statePillow, realPillow, gesture):
		'''
			Given a touch quality analysis a color is derived
			(The colour of your touch.)

			Color Space = HLS (Hue Lightness Saturation) 
			Touch Space = ITANPS(Intensity, time, area, number, space, path)
			
			Color			Touch
			
			Hue			=> Area [Inverse]
			Lightness	=> Intensity
			Saturation	=> 1
			Duration*	=> Time
			
			*Duration is the time that takes to fade from a initial color to a target color.
		'''
		realPillow.gesture.update(gesture)
		if self.debug:
			print realPillow.name
			realPillow.gesture.show()

		area  = realPillow.gesture.area.norm
		time  = realPillow.gesture.time.norm
		space = realPillow.gesture.space.norm
		intensity = realPillow.gesture.intensity.norm

		if area!=0 and time!=0 and intensity!=0:
			''' Convert touch to color '''

			rgb = colorsys.hls_to_rgb(0.5*area, intensity, 1.0)
			
			# hack to avoid very small numbers 
			(r,g,b) = rgb
			if r < 0.0005:
				r = 0
			if g < 0.0005:
				g = 0
			if b < 0.0005:
				b = 0
			rgb = (r,g,b)
						
			#print (1.0 - area, intensity, 1),'-->',rgb
			
			convert = lambda x: int(round(x*255))
			new_rgb = map(convert, rgb)	
			
			#print 'new_rgb ',new_rgb
			(a, b, c) = new_rgb 
			if a >= 0 and b >= 0 and c >= 0:
				statePillow.color = new_rgb
			else:
				print "warning: a negative value for color. (touch2light)"

	def minmax(self, val, values):
		(min,max) = values
		if   val > max: res = [min, val]
		elif val < min: res = [val, max]
		else: res = [min, max]
		return res
			
	''' ---------------------------------------------------------- '''
	''' -- Test Stuff											-- '''
	''' ---------------------------------------------------------- '''

	def test(self, statePillow, realPillow):	
			##self.key2Light(realPillow)
			self.key2FadeBuzz(realPillow)
			##self.key2FadeLight(realPillow)
			#self.testNewBeep(realPillow)
			''' turn off lights '''
			##realPillow.light((0,0,0))	
			##realPillow.lightFade((0,0,0), (0,0,0), 2000)	
			''' turn sound off '''
			##realPillow.beep(0, 0)


	def testNewBeep(self, realPillow):
		if self.simulator.key in ['s']: #and realPillow.name=='Rui soft object vers. 2.0.1':
			self.simulator.key = ''
			
			# Initial test
			note 		= 24
			duty_to		= 8
			duty_from	= 8
			duration	= 100
			
			f = open('sound.txt')
			sounds = f.readlines()
			f.close()
			
			print 'Number of sounds:',range(len(sounds)/5)
			for x in range(len(sounds)/5):
				note 		= int(sounds.pop(0)) 
				chord		= sounds.pop(0).strip('\n')
				duty_to		= int(sounds.pop(0))
				duty_from	= int(sounds.pop(0))
				duration	= int(sounds.pop(0))
				
				realPillow.chord(note, chord, duty_to, duty_from, duration)
								
	def testNewBeep_old(self, realPillow):
		if self.simulator.key in ['s']: #and realPillow.name=='Rui soft object vers. 2.0.1':

			# Initial test
			freq_from 		= 20
			freq_to			= 20 
			duty_from		= 20  
			duty_to			= 20
			freq_duration	= 50
			duration		= 1000
			bounce			= 0
			
			f = open('sound.txt')
			sounds = map(int, f.readlines())
			f.close()
			
			print 'Number of sounds:',range(len(sounds)/8)
			for x in range(len(sounds)/8):
				freq_from 		= sounds.pop(0) 
				freq_to			= sounds.pop(0) 
				duty_from		= sounds.pop(0)
				duty_to			= sounds.pop(0)
				freq_duration	= sounds.pop(0)
				duration		= sounds.pop(0)
				bounce   		= sounds.pop(0)
				bug   			= sounds.pop(0)
				

				#realPillow.sweep(freq_from, freq_to, duty_from, duty_to, freq_duration, duration, bug)
				#if bounce == 1:
				#	realPillow.sweep(freq_to, freq_from, duty_to, duty_from, freq_duration, duration, bug)

		freq_duration=50
		if self.simulator.key in ['z'] and realPillow.name=='Rui soft object vers. 2.0.1':
			realPillow.beep(0,0)

		if self.simulator.key == 't':
			(freq_from, duty_from), (freq_to, duty_to), freq_duration = realPillow.sound
			realPillow.sweep(freq_from+100, freq_from+100, duty_from, duty_from, freq_duration, 1000)
		#if self.simulator.key == 'b': 
			#(freq_from, duty_from), (freq_to, duty_to), freq_duration = realPillow.sound
			#realPillow.sweep(freq_from-100, freq_from-100, duty_from, duty_from, freq_duration, 1000)
		if self.simulator.key == 'y':
			(freq_from, duty_from), (freq_to, duty_to), freq_duration = realPillow.sound
			realPillow.sweep(freq_from, freq_from, duty_from+1, duty_from+1, freq_duration, 1000)
		if self.simulator.key == 'h':
			(freq_from, duty_from), (freq_to, duty_to), freq_duration = realPillow.sound
			realPillow.sweep(freq_from, freq_from, duty_from-1, duty_from-1, freq_duration, 1000)


	# HERE - mcb
	def key2FadeBuzz(self, realPillow):
		if self.simulator.key == 't':
			realPillow.buzz(realPillow.buzzer[0]+1, 1000)	
		if self.simulator.key == 'b': # and realPillow.name == "Soft(4)":
			self.simulator.key = ''
			print 'test:',realPillow.name

			if 1: # touch (poke)
				realPillow.send(  [
						{ 'address': realPillow.modules['actuators']['beep'].methods['sweep'].address
				  			, 'args':   [90,402,0,124,0,2,0]
						}
					] )			

			if 0: # touch (complex)
				highStart = 200 * 2
				highMid = 240 * 2
				highEnd = 250 * 2
				realPillow.send(  [
						{ 'address': realPillow.modules['actuators']['beep'].methods['sweep'].address
				 			, 'args':   [highStart,highMid,0,26,0,500,0]
			        		}
						,
						{ 'address': realPillow.modules['actuators']['beep'].methods['sweep'].address
				  			, 'args':   [highMid,highEnd,26,24,0,900,0]
						}

					] )			

			
		if self.simulator.key == 'p':
			print '--------------------------------------------------'
			print realPillow.tmp
			realPillow.realtime.area.max = 100
			realPillow.buzzFadeInOut()
			'''
			realPillow.send({ 'address': realPillow.modules['actuators']['buzz'].methods['sweep'].address
				  			, 'args':   [100,240,1000]
							})	
			print realPillow.tmp
			realPillow.send({ 'address': realPillow.modules['actuators']['buzz'].methods['sweep'].address
				  			, 'args':   [240,100,1000]
							})
			'''
			#realPillow.buzz(200, 1000)#realPillow.buzzer[1]+1)	
			#realPillow.send({ 'address': realPillow.modules['actuators']['beep'].methods['buzz'].address
		  	#		  , 'args':   [[200,2000],[200,2000]]
			#					 })	
		if self.simulator.key == 'y':
			print 'sweep'
			#realPillow.sweep(10, 50, 10, 20, 16, 50)
			#realPillow.sweep(50, 10, 20, 10, 16, 50)
			realPillow.sweep(600, 500, 10, 16, 20, 500)
			realPillow.sweep(500, 600, 10, 16, 20, 500)
			#realPillow.buzzFadeInOut()
			#realPillow.buzz(200, realPillow.buzzer[1]-1)

	def key2Light(self, realPillow):
		if self.simulator.key in ['u','j','i','k','o','l']:
			self.keyValues = {
				'u': (self.keyValues[0], self.keyValues[1], self.keyValues[2]+1,self.keyValues[3],	self.keyValues[4]),
				'j': (self.keyValues[0], self.keyValues[1], self.keyValues[2]-1,self.keyValues[3],	self.keyValues[4]),
				'i': (self.keyValues[0], self.keyValues[1], self.keyValues[2],  self.keyValues[3]+1,	self.keyValues[4]),
				'k': (self.keyValues[0], self.keyValues[1], self.keyValues[2],	self.keyValues[3]-1,	self.keyValues[4]),
				'o': (self.keyValues[0], self.keyValues[1], self.keyValues[2],	self.keyValues[3],	self.keyValues[4]+1),
				'l': (self.keyValues[0], self.keyValues[1], self.keyValues[2],	self.keyValues[3],	self.keyValues[4]-1),
				'' : self.keyValues,
				}[self.simulator.key]

			#print self.simulator.key
			if realPillow.name=='Another unstable pillow':
				print 'light ',self.keyValues
				realPillow.light(0, (self.keyValues[2], self.keyValues[3], self.keyValues[4]))				
	
