#!/usr/bin/env python

'''
Implemented at V2_ Lab, for documentation see

	* http://trac.v2.nl/wiki/MoveMeDocumentation

'''

import sys, os, getopt, traceback

try:
	import pygtk
	pygtk.require("2.0")
except:
	pass

try: import gtk
except:
	print "Need pyGTK or GTKv2"
	sys.exit(1)

import MoveMe.GUI.graphical_user_interface



class Main(object):

	def __init__(self):
		gui = MoveMe.GUI.graphical_user_interface.GUI()
		gtk.main()


def usage():
	''' Explanation of command line arguments usage. '''

	print "./main.py [-p PORT, --port=PORT] [-h, --help]"
	sys.exit()


if __name__ == '__main__':
	'''
	Program startup.
	Gets commandline options, initialises contextmanager and adaptation engine.
	'''


	try:
		opts, args = getopt.getopt(sys.argv[1:], "-h:", ["help"])
	except getopt.GetoptError:
		usage()

	for opt, arg in opts:
		if opt in ("--help"): usage()

	Main()
	print " * Application terminated [ok]"
