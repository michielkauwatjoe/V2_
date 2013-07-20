#!/usr/bin/env python

'''
Implemented at V2_ Lab, for documentation see

	* http://trac.v2.nl/wiki/MoveMeDocumentation
'''

from socket import socket, gethostname, AF_INET, SOCK_DGRAM
from select import select
from MoveMe.OSC import CallbackManager

try:
	import gobject
except:
	print "Need pyGTK"
	sys.exit(1)



class Server(CallbackManager):

	def __init__(self, port, host=''):

		super(Server,self).__init__()
		self._port = int(port)
		self._socket = socket(AF_INET, SOCK_DGRAM)
		#self._socket.bind((gethostname(), self._port))
		self._socket.bind((host, self._port))
		self._fd = self._socket.fileno()
		self.__install_oscqs_callbacks()
		gobject.io_add_watch(self._fd,
				gobject.IO_IN | gobject.IO_PRI,
				self.__read_callback, self)


	def __read_callback(self, source, condition, *args):
		''' This callback is called when there is data to be read on a
		listening socket:

			* source: the file descriptor to be read,
			* condition: the condition that triggered the callback,
			* server: the caller object.
		'''

		if source != self._fd:
			return False
		if (condition & gobject.IO_IN) | (condition & gobject.IO_PRI):
			msg, source = self._socket.recvfrom(1024)
			if msg:
				self.handle(msg, source)
		return True


	def __oscqs_reply_cb(self, data, source):
		''' Compose reply message. '''

		msg = []

		msg.append(' * reply (')
		msg.append(str(source[0]) + ':' + str(source[1]) + ')')
		msg.append('\n   - received ')
		msg.append(str(data[0]) + ', ' + str(data[1]))
		msg.append(' from ' + str(data[2]))

		print ''.join(msg)


	def __oscqs_error_cb(self, data, source):
		print "error from %s:%d: %s %s %s" % (source[0], source[1], data[0], data[1], data[2])


	def __install_oscqs_callbacks(self):
		self.add(self.__oscqs_reply_cb, "/reply")
		self.add(self.__oscqs_error_cb, "/error")


	def dup(self):
		return self._socket.dup()
