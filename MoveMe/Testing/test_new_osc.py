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

import time, sys
from MoveMe.OSC import server, client, client_new



oscserver = None
osc_port = 7771

def sensor_list_callback(message, source):
	print "sensor: ", message, source

def actuator_list_callback(message, source):
	print "actuator: ", message, source


if __name__ == '__main__':
	oscserver = server.Server(osc_port)
	oscserver.add(sensor_list_callback, "/sios/sensors/matrix/data")
	oscserver.add(actuator_list_callback, "/actuators/")

	try:
		osc_client = client_new.Client("localhost", 7770, oscserver)
		osc_client_old = client.Client("localhost", 7770, oscserver)
	except client_new.OSCClientError, e:
		print "error: ", e
	else:
		try:
			# construct list of args
			args = range(0, 10)

			# trigger OSCConstructMsgError exception 
			#osc_client.send("/sios/actuators/light/rgb", [220, 300, 300], [300, 220, 220])

			# send normal message
			osc_client.send({'address': '/to/address/one', 'args': args})

			# send bundel message
			osc_client.send({'address': '/to/address/one', 'args': args}, 
					{'address': '/to/address/two', 'args': args})

			# send bundel messages as list
			osc_client.send([{'address': '/to/address/one', 'args': args}, 
					 {'address': '/to/address/two', 'args': args}])

			# nested lists are possible
			args = [1, 2, [3, 'foo', 5], 6, (7, 8, [9.0, 10])]
			osc_client.send({'address': '/to/address/one', 'args': args})

			# or only a single argument
			osc_client.send({'address': '/to/address/one', 'args': 'a single arg'}, 
					{'address': '/to/address/two', 'args': 2})

			# it is also possible to give type hints in the form of a dict
			# however, because dicts are unsorted only give one argument per dict otherwise
			# the order of argument appearance is unpredictible
			# 
			# and a FIXME, the OSC implementation we use only supports typehints for blob ('b')
			# anyway it is used as follows
			args = [1, 2, {'i':3}, 6, {'b':'bar'}, [7, 8, [9, 10]]]
			osc_client.send({'address': '/to/address/one', 'args': args})

		except client_new.OSCClientError, e:
			# all OSC client exceptions are derived from OSCCLientError
			print e

		else:
			try:
				gtk.main()
			except KeyboardInterrupt:
				print 'exiting'
				sys.exit(0)
