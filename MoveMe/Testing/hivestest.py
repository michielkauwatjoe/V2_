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

def gesture_list_callback(message, source):
	print "gesture: ", message, source


if __name__ == '__main__':
	oscserver = server.Server(osc_port)
	oscserver.add(gesture_list_callback, "/softn/laban")

	client = client.Client("127.0.0.1", 9999, oscserver)
	client.send("/softn/add")
	gtk.main()
