#!/usr/bin/env python

'''
Implemented at V2_ Lab, for documentation see

 http://trac.v2.nl/wiki/MoveMeDocumentation

Small program for testing out the pillow OSC functionality.
'''

try:
	import gtk
except ImportError:
	print "error import gobject"
	sys.exit(-1)

import time
from MoveMe.OSC import server, client



oscserver = None
osc_port = 7771

def sensor_list_callback(message, source):
	print "sensor: ", message, source

def actuator_list_callback(message, source):
	print "actuator: ", message, source


if __name__ == '__main__':
	oscserver = server.Server(osc_port)
	oscserver.add(sensor_list_callback, "/sios/sensor/list")
	oscserver.add(actuator_list_callback, "/sios/actuator/list")

	client = client.Client("192.168.255.216", 7770, oscserver)
	client.send("/sios/actuators/buzz/buzz", 220, 300)
	client.send("/sios/actuators/buzz/buzz", 220, 300)
	client.send("/sios/actuators/beep/beep", 95, 8, 50)
	client.send("/sios/actuators/beep/beep", 90, 8, 50)
	client.send("/sios/actuators/beep/beep", 85, 8, 50)
	client.send("/sios/actuators/beep/beep", 80, 8, 50)
	client.send("/sios/actuators/beep/beep", 80, 8, 50)

	client.send("/sios/actuators/buzz/buzz", 220, 300)
	client.send("/sios/actuators/buzz/buzz", 220, 300)
	client.send("/sios/actuators/buzz/buzz", 220, 300)
	client.send("/sios/sensors/matrix/listen");
	time.sleep(1)
	client.send("/sios/actuators/beep/beep", 95, 8, 50)
	client.send("/sios/actuators/beep/beep", 90, 8, 50)
	client.send("/sios/actuators/beep/beep", 85, 8, 50)
	client.send("/sios/actuators/beep/beep", 80, 8, 50)
	client.send("/sios/actuators/beep/beep", 80, 8, 50)
	client.send("/sios/actuators/beep/beep", 85, 8, 50)
	client.send("/sios/actuators/beep/beep", 90, 8, 50)
	client.send("/sios/actuators/beep/beep", 95, 8, 50)
	client.send("/sios/actuators/beep/beep", 100, 8, 50)
	time.sleep(1)
	client.send("/sios/sensors/matrix/silence");
	gtk.main()
