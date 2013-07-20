#!/usr/bin/env python

# mcb - start

import math

def scale(x, xMin, xMax, yMin, yMax): # linear mapping
        y = (x - xMin) * (yMax - yMin) / ( xMax - xMin ) + yMin
        return y;

def enhance_lows(x): # input must be from 0 to 1
	if x > 1 or x < 0:
		print "WARNING: enhance_lows input out of range ", x
	x = max(0.0,min(1.0,x))
	return math.sin(scale(x,0.0,1.0,0.0,math.pi/2))

def mtof(midinote) : # map midi notes to frequency
        return 440.0 * math.exp(0.057762265 * (midinote - 69.0))

#mcb - end
