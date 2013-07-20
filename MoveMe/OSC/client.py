#!/usr/bin/env python

'''
Implemented at V2_ Lab, for documentation see

	* http://trac.v2.nl/wiki/MoveMeDocumentation
'''

from socket import socket, AF_INET, SOCK_DGRAM
from select import select
from MoveMe.OSC import OSCMessage
from MoveMe import OSC



class Client(object):


	def __init__(self, host=None, port=0, server=None):
		''' Construct a OSC client.

		When host and port arguments are given this client is
		bound to a specific server. Otherwise it acts as a generic
		client:

			* host: hostname of the OSC server,
			* port: port the OSC server listens to,
			* server: server sockets to use instead of creating new ones.
		'''

		if server:
			if server.__module__ != "MoveMe.OSC.server":
				raise invalidServerError("server argument is not a valid OSCServer object")
			self._socket = server.dup()
			self._server = server
		else:
			self._socket = socket(AF_INET, SOCK_DGRAM)
			self._server = None

		self._fd = self._socket.fileno()

		if host != None and port != 0:
			self._address = (host, port)
			self._bound = True
		else:
			self._address = None
			self._bound = False


	def __cmp__(self, _client):
		''' Compare function. '''

		if isinstance(_client, Client):
			isequal = cmp(self._address, _client.address())
			if self._server or _client.server():
				return isequal or cmp(self._server, _client.server())
			return isequal
		else:
			return -1


	def _sendMessage(self, address, message, timeout=None):
		''' Can raise a timeoutError when timing out while waiting for
		the file descriptor. '''

		ret = select([],[self._fd], [], timeout)
		try:
			ret[1].index(self._fd)
		except:
			# for the very rare case this might happen
			raise timeoutError("Timed out waiting for file descriptor")
		try:
			self._socket.sendto(message, address)
		except:
			print "Error while sending to: ", address


	def server(self):
		''' Returns the attached server of this client, or None if no
		server is attached. '''

		if self._server:
			return self._server
		else:
			return None


	def address(self):
		''' Returns a (host,port) tuple of the server this client is
		bound to or None if not bound to any server.  '''

		if self._bound:
			return self._address
		else:
			return None


	def rebind(self, host, port):
		''' Rebinds to a specific OSC server:

			* host: hostname of the OSC server,
			* port: port the OSC server listens to.
		'''

		self._address = (host, port)
		self._bound = True


	def bind(self, host, port):
		''' Bind to a specific OSC server:

		host: hostname of the OSC server,
		port: port the OSC server listens to.
		'''

		if not self._bound:
			self._address = (host, port)
			self._bound = True
		else:
			return -1


	def constructMessage(self, pattern, *args):
		''' Constructs a OSC message:

			* addr: The OSC message address pattern,
			* *args: a tuple of arguments to be appended (in order of
			appearance) to the message as OSC arguments.
		'''

		msg = OSCMessage()

		# check if for bundle messages
		if len(args) and type(args[0]) == list:
			msg.setAddress("#bundle")
			msg.append(0)
			for bundle_msg_list in args:
				if not type(bundle_msg_list) == list:
					pass
				bundle_msg = OSCMessage()
				bundle_msg.setAddress(pattern)
				for param in bundle_msg_list:
					bundle_msg.append(param)
				msg.append(bundle_msg.getBinary(), 'b')
		else:
			msg.setAddress(pattern)
			for arg in args:
				msg.append(arg)
		return msg


	def send(self, pattern, *args):
		''' Construct and send a OSC message;

			* pattern: the OSC address pattern.
			* *args: A tuple of arguments to be appended (in order
			of appearance) to the message as OSC arguments.

		Raises OSCClient.BoundError if trying to use this function
		illegaly.
		'''

		if self._bound:
			msg = self.constructMessage(pattern, *args)
			self._sendMessage(self._address, msg.getBinary())
		else:
			raise boundError("Client not bound to any server")


	def sendUnbound(self, host, port, pattern, *args):
		''' Construct and send a OSC message to an arbitrary OSC
		server:

			* host: hostname of the OSC server.
			* port: port the OSC server listens to.
			* pattern: The OSC address pattern.
			* *args: A list of arguments to be appended (in order
			of appearance) to the message as OSC arguments.
		'''

		msg = self.constructMessage(pattern, *args)
		self._sendMessage((host, port), msg.getBinary())


class clientError(Exception):
	def __init__(self, message):
		self.message = message


class invalidServerError(clientError):
	pass


class boundError(clientError):
	pass


class timeoutError(clientError):
	pass
