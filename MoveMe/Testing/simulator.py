#!/usr/bin/env python

'''
Implemented at V2_ Lab, for documentation see

	* http://trac.v2.nl/wiki/MoveMeDocumentation

Program for testing out the MoveMe server application without a physical
pillow. Supports Zeroconf registration and OSC activation / deactivation of
pressure sensor.

	./simulator.py  --data=FILE [-p PORT, --port=PORT] [-r Hz, --rate=Hz]
		[-n, --name] [-i, --id]

Test data can be found in the subversion repositories. Checking out the data
and running the script:

	svn co http://svn.v2.nl/passepartout/branches/data
	export PYTHONPATH=../../
	./simulator.py --d data/workshopMay2006/person03.dat -p 9876

Note: When running multiple simulator scripts, it is required to specify
differnt portnumbers.
'''

import sys, os, getopt
import socket, select

from time import sleep
from datetime import *
from math import floor

try:
	import gtk, gobject
except ImportError:
	print "error import gobject"
	sys.exit(-1)


from MoveMe.OSC import client, server
try:
	import MoveMe.Zeroconf.zeroconf

except ImportError:
	print "The bonjour python package needs to be installed"
	sys.exit(-1)



# Global definitions.

oscserver = None
default_osc_port = 7770

data_file = None
file_data = None

last_sample = datetime.today()
sample_rate = 50000 # equals 20Hz

listeners = {}


def matrixListenCallback(message, source):
	''' Start listening to pressure matrix.
		* Creates a list of listening clients for matrix if there are no listeners yet,
		* adds adds new client to it.
	'''

	category = 'matrix'
	address = parseFromAddress(message, source)
	client = MoveMe.OSC.client.Client(address[0], address[1], oscserver)

	if listeners.has_key(category):

		# Do nothing if the client is already listening.
		if client in listeners[category]: pass

		# Add the client to the listeners list.
		else:
			try:
				listeners[category].add(client)
			except AttributeError, e:
				print 'trying to add list?'
			except Exception, e:
				raise

	# Create a list with a new client.
	else:
		listeners[category] = list([client])

	# Reply standard rfid number.
	#client.send('/pillow/rfid/found', 'test-rfid')

	print ' * added listener @ %s, %d' % (client.address()[0], client.address()[1])


def matrixSilenceCallback(message, source):
	''' Silence pressure matrix. '''

	category = 'matrix'
	address = parseFromAddress(message, source)

	#TODO: get client from listeners['matrix'] instead of making a new one
	client = MoveMe.OSC.client.Client(address[0], address[1], oscserver)
	rc = None

	if listeners.has_key(category):

		# If client exists for this sender pop it
		if client in listeners[category]:

			rc = listeners[category].pop(listeners[category].index(client))
			if len(listeners[category]) == 0: del listeners[category] # Remove category if no more clients

	#client.send("/reply", "/sios/sensors/matrix/silence", category, client.address()[0] + ":" + str(client.address()[1]))
	if rc: print ' * removed listener @ %s, %d' % (rc.address()[0], rc.address()[1])


def parseFromAddress(message, source):
	''' Split second argument from message into host and port. On error
	take source as address. '''

	try:
		address = message[1]
		host, port = address.split(':')
		address = (host, int(port))
	except IndexError:
		address = source

		return address


def simulatePressureX8Callback():
	''' Send 8-channel pressure data over OSC; rolls trough the data file
	row by row. '''

	global last_sample

	now = datetime.today()
	td = now - last_sample

	if td.microseconds >= sample_rate:

		# check if any listeners exist with 'matrix' (pressure) category
		if listeners.has_key('matrix'):
			line = file_data.readline()

			if len(line) > 0:

				line = line.strip()
				if line:

					channels = line.split('\t') # split on tabs
					channels = map(int, channels)

					if len(channels) > 1:

						# send channel data to clients in the notification listz
						for client in listeners['matrix']: client.send("/sios/sensors/matrix/data", *channels)
			# End of file.
			else:
				print 'rotate'
				file_data.seek(0, 0)

		last_sample = datetime.today()

	# Give us a break...
	sleep(0.00001)
	return True


def otherOSCCallback(message, source):
	''' Catches left over OSC messages. '''

	print '!!!WARNING: osc message catched by simulator pillow, however no specific callback function!\n'
	print message, source


def usage():
	''' Explanation of the commandline arguments. '''

	print "./simulator.py [-p PORT, --port=PORT] [-r Hz, --rate=Hz] [-n, --devname] [-i, --id=00:00:00:00:00:00] --data=FILE"
	sys.exit()


def getCommandlineOptions():
	''' Parses commandline options and adds them to a dict, returns the
	dict. '''

	global file_data

	options = {}

	# Default values.
	options['osc_port'] = default_osc_port
	options['pillow_name'] = 'Simulated Pillow'
	options['pillow_id'] = "test-pillow-id"


	try:
		opts, args = getopt.getopt(sys.argv[1:],
			"p:d:r:n:i:h",
			["port=",
			"data=",
			"rate=",
			"id=",
			"devname=",
			"help"])

	except getopt.GetoptError: usage()

	for opt, arg in opts:

		if opt in ("-p", "--port"): options['osc_port'] = int(arg)

		elif opt in ("-d", "--data"):
			data_file = arg

			if not os.path.isfile(data_file):
				print "'%s' is not a valid data file" % (data_file)
				sys.exit(1)
			else:
				file_data = open(data_file, 'r')

		elif opt in ("-r", "--rate"):
			sample_rate = int(arg)
			sample_rate = floor((1.0 / sample_rate) * 1000000)
			options['sample_rate'] = sample_rate

		elif opt in ("-i", "--id"): options['pillow_id'] = arg
		elif opt in ("-n", "--devname"): options['pillow_name'] = arg
		elif opt in ("-h", "--help"): usage()

	if not data_file: usage() # Required!

	return options


def main():
	''' Main function, handles commandline options, sets up OpenSound
	Control and Zeroconf. '''

	global oscserver

	options = getCommandlineOptions()
	oscserver = MoveMe.OSC.server.Server(options['osc_port'])

	# Callbacks for pressure matrix.
	oscserver.add(matrixListenCallback, "/sios/sensors/matrix/listen")
	oscserver.add(matrixSilenceCallback, "/sios/sensors/matrix/silence")

	try:
		# Register with mDNS service.
		MoveMe.Zeroconf.zeroconf.register(options['pillow_name'],
				options['osc_port'], "_sios._udp",
				{'id':options['pillow_id'], 'extra_type':'simulator', 'oscroot': '/sios', 'uri': 'http://isp.v2.nl/~simon/data/sios_simulator.xml'})

	except MoveMe.Zeroconf.zeroconf.RegisterError, e:
		print e.message
		sys.exit(e.errorval)

	# Perform pressure callback when idle.
	gobject.idle_add(simulatePressureX8Callback)

	gtk.main()


if __name__ == '__main__':
	main()
	print "Pillow simulator terminated."
