from MoveMe.MultiPillow.Pillow import FIFO
from MoveMe.Util.softmath import *

import random

class Sound:
    def __init__(self):
        self.freq_from     = 0
        self.freq_to       = 0
        self.duty_from     = 0
        self.duty_to       = 0
        self.duration      = 0
        self.sustain       = 0
        self.freq_duration = 20
        self.fifo          = FIFO()
        
        self.chords = {'maj' : (0,4,7)
                      ,'min' : (0,3,7)
                      ,'dim' : (0,3,6)
                      ,'maj-': (7,4,0)
                      ,'min-': (7,3,0)
                      ,'dim-': (6,3,0)
                      ,'maj+': (0,7,4)
                      ,'min+': (0,7,3)
                      ,'dim+': (0,6,3)
		      }

	self.keys = { 'Soft(0)' : 71-7*2  # all pillows are different cycle of fifths
		   , 'Soft(1)'  : 71-7*1
		   , 'Soft(2)'  : 71-7*3
		   , 'Soft(3)'  : 71-7*3
		   , 'Soft(4)'  : 71-7*4
		   , 'Soft(5)'  : 71-7*5
		   , 'Soft(6)'  : 71-7*6
		   , 'Soft(7)'  : 71-7*2
		   , 'Soft(8)'  : 71-7*0
		   , 'Soft(9)'  : 71-7*4
		   , 'Soft(10)' : 71-7*5
		   , 'Soft(11)' : 71-7*6
		   , 'Soft(12)' : 71-7*2
		   , 'Soft(13)' : 71-7*3
		   , 'Soft(14)' : 71-7*4
		   }

	self.modes = {    'Chroma' : (0,1,2,3,4,5,6,7,8,9,10,11,12)
			, 'Ionian' : (0,2,4,5,7,9,11,12) # Major
			, 'Dorian' : (0,2,3,5,7,9,10,12)
			, 'Phrygi' : (0,1,3,5,7,8,10,12)
			, 'Lydian' : (0,2,4,6,7,9,11,12)
			, 'MixLyd' : (0,2,4,5,7,9,10,12)
			, 'Aeolia' : (0,2,3,5,7,8,10,12)
			, 'Locria' : (0,1,3,5,6,8,10,12)
			, 'MBlues' : (0,3,4,7,9,10,12)
			, 'mBlues' : (0,3,5,6,7,10,12)
			, 'Dim'	   : (0,2,3,5,6,8,9,11,12)
			, 'ComDim' : (0,1,3,4,6,7,9,10,12)
			, 'MPenta' : (0,2,4,7,9,12)
			, 'mPenta' : (0,3,5,7,10,12)
			, 'Raga1'  : (0,1,4,5,7,8,11,12)
			, 'Raga2'  : (0,1,4,6,7,9,11,12)
			, 'Raga3'  : (0,1,3,6,7,8,11,12)
			, 'Spansh' : (0,1,3,4,5,7,8,10,12)
			, 'Gypsy'  : (0,2,3,6,7,8,11,12)
			, 'Arabia' : (0,2,4,5,6,8,10,12)
			, 'Egypt'  : (0,2,5,7,10,12)
			, 'Hawaii' : (0,2,3,7,9,12)
			, 'Pelog'  : (0,1,3,7,8,12)
			, 'Japan'  : (0,1,5,7,8,12)
			, 'Ryukyu' : (0,4,5,7,11,12)
			, 'Whole'  : (0,2,4,6,8,10,12)
			, 'M3rd'   : (0,4,8,12)
			, 'm3rd'   : (0,3,6,9,12)
			, '4th'    : (0,5,10,12)
			, '5th'    : (0,7,12)
			, 'Oct'	   : (0,12)
		}


    def set(self, freq_from, freq_to, duty_from, duty_to, freq_duration, duration, sustain = 0):
        ''' Changes sound proprities and adds it to the fifo'''
        self.freq_from     = freq_from
        self.freq_to       = freq_to
        self.duty_from     = duty_from
        self.duty_to       = duty_to
        self.freq_duration = freq_duration
        self.duration      = duration
	self.sustain	   = sustain
        
        self.fifo.put((freq_from, freq_to, duty_from, duty_to, freq_duration, duration, sustain))

    def note(self, midinote_from, midinote_to, duty_to=-1, duty_from=-1, duration=-1, sustain = 0):
        ''' a single tone of definite pitch made '''
        
        #freq_to = int(55 * 2**(note/12.))
        freq_to = int(mtof(midinote_to) + .5)
        freq_from = int(mtof(midinote_from) + .5)

        duty_lim = int((freq_to - 880) / 12)

        if duty_from < 0 : duty_from = self.duty_from
        if duty_to   < 0 : duty_to   = self.duty_to
        if duration  < 0 : duration  = self.duration
        
        if duty_from < duty_lim : duty_from = duty_lim    
        if duty_to   < duty_lim : duty_to   = duty_lim

        self.set(freq_from, freq_to, duty_from, duty_to, 20, duration, sustain)

    def chord(self, note, mode, note_count, duty_to=-1, duty_from=-1, duration=-1):
        ''' a group of (typically three or more) notes sounded together '''
        if mode in self.modes.keys() :
	    duration = int(float(duration)/note_count + .5)
	    i = 0
	    while (i < note_count) :
		    for interval in self.modes[mode] :
			df = duty_from
			dt = duty_to

			if note_count != 1 and i == 0 :
				df = 1 # fade in

			sustain = (note_count-1 != i)

			if i == 0 : # first note
				self.note(note + interval, note + interval, dt, df, duration, sustain)
			elif i == note_count -1: # last note
				self.note(note + interval, note + interval + random.randint(-1,+1) , dt, df, duration,sustain)
				# random up or down slide in an attempt to make
				# a questioning, to definitive statement sound
			else :	# middle notes, modulate pulse width
				self.note(note + interval, note + interval, dt*2, df, duration,sustain)
			i += 1
			if i == note_count : break
        
        # notes should be sent to pillow here




    def convertGesture(self, gesture, realPillow, index): # index dowm generation chain
        if type(gesture)==list and len(gesture)==2:
            
            cog = realPillow.cog
            gestureName, quality = gesture
            newSound = True

	    intensity = enhance_lows(realPillow.gesture.intensity.norm)
	    intensity_en = enhance_lows(intensity)
	    echo_factor  =  1. / float(index + 1)
            duty = scale(intensity_en, 0, 1, 2, 30. * echo_factor)	   # PULSE WIDTH
	    duty = int(min(127,max(0,duty)))

            inc_duty_to   = duty # random.randrange(10,20)#18
            inc_duty_from = duty  # random.randrange(10,20)#6

            # duty Rui Style
            # inc_duty_to   = 0 # random.randrange(10,20)#18
            # inc_duty_from = 0 # random.randrange(10,20)#6

            duration = scale(realPillow.gesture.time.raw, 3, .4, 580, 150) # DURATION
            note_count = min(3,max(1,int(max(1,scale(duration, 580, 150, 4, 2)))))
	    duration = int(max(2*note_count,min(400*note_count,duration)))
	    note = self.keys[realPillow.name]-7*index  # musical key of the Pillow,
    
            ok = True
            try:
                mode = {
                  'tap':     'Oct',
                  'tapping': '4th',
                  'flick':   '5th',
                  'flicking':'5th',
                  'pat':     'Lydian',
                  'patting': 'MixLyd',
                  'touch':   'Aeolia',
                  'touches': 'Locria',
                  'hold':    'MBlues',
                  'holds':   'mBlues',
                  'glide':   'Dim'   ,
                  'glides':  'ComDim',
                  'stroke':  'MPenta',
                  'stroking':'mPenta',
                  'jab':     'Raga1' ,
                  'jabbing': 'Raga2' ,
                  'knock':   'Raga3' ,
                  'knocking':'Spansh',
                  'slice':   'Gypsy' ,
                  'slap':    'Arabia',
                  'slapping':'Egypt' ,
                  'cut':     'Hawaii',
                  'knead':   'Pelog' ,
                  'kneading':'Japan' ,
                  'press':   'Ryukyu',
                  'presses': 'Whole' ,
                  'rub':     'M3rd'  ,
                  'rubbing': 'm3rd'  ,
                }[gestureName]

            except KeyError:
               ok = False
                
	    self.chord(0,'5th',1,0,0,800*index) # silence/delay tome to stagger sounds

            if ok:
                self.chord(note, mode, note_count, inc_duty_to, inc_duty_from, duration)
            else:
                mode = '5th'
                self.chord(note, mode, note_count, inc_duty_to, inc_duty_from, duration)
                print ' * Warning: Touch %s cannot be converted to sound.'%gestureName
     
            return mode
# tap, flick, pat, touch, hold, glide, stroke, stroking, jab, jabbing, cut, knock, knocking, 
# slice, slap, slapping, knead, kneads, press, presses, rub, rubbing, presses, knead, kneading                         
