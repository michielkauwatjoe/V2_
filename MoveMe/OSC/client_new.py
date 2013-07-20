#!/usr/bin/env python

'''
Implemented at V2_ Lab, for documentation see

	* http://trac.v2.nl/wiki/MoveMeDocumentation
'''

import socket 
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

		self._server = None
		if server:
			if server.__module__ != "MoveMe.OSC.server":
				raise OSCServerError("server argument is not a valid OSCServer object")
			self._socket = server.dup()
			self._server = server
		else:
			try:
				self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			except socket.error, e:
				raise OSCClientError(e)

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
		def sendIntern(address, message, retries=3):
			cntr = 0
			while True:
				try:
					cntr = (cntr + 1) % retries
					self._socket.sendto(message, address)
				except socket.error, e:
					no = e.args[0]                      
					if no == EINTR:
						yield cntr
					elif no == EMSGSIZE:
						raise OSCClientError, "Message too long"
					elif no == ECONNREFUSED:
						raise OSCClientError, "Connection refused"
				except Exception, e:
					raise OSCClientError, "Unknown error while sending to: %s:%d" % address
				else:
					return
		
		sender = sendIntern(address, message).next
		try:
			while sender():
				pass
		except StopIteration:
			pass
		except:
			raise

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

	
	def _create_msg(self, d):

		def flatten(*args):
			''' Generator to flatten nested containers.
			e.g.: for i in flatten(args) : print i '''

			for arg in args: 
				if type(arg) in (type(()),type([])):
					for elem in arg:
						for f in flatten(elem):
							yield f
				else: yield arg

		if type(d) != dict:
			raise OSCConstructMsgError, 'Message is not a dict: %s' % (str(d))

		try:
			addr = d['address']
			args = d['args']		
		except KeyError, e:
			raise OSCConstructMsgError, "OSC msg has no key %s" % (e)
	
		msg = OSCMessage()
		msg.setAddress(addr)
		
		for arg in flatten(args):
			if type(arg) == dict:
				for t, a in arg.iteritems():
					msg.append(a, t)
			else:
				msg.append(arg)
				
		return msg

	def constructBundle(self, *msgs):
		bundle = OSCMessage()
		bundle.setAddress("#bundle")
		bundle.append(0)

		def internCreate(d):
			try: return self._create_msg(d)
			except: raise 

		for arg in msgs:
			if type(arg) == list:
				for d in arg:
					msg = internCreate(d)
					bundle.append(msg.getBinary(), 'b')
			else:
				msg = internCreate(arg)
				bundle.append(msg.getBinary(), 'b')

		return bundle
	

	def constructMessage(self, *msgs):
		if len(msgs) < 1:
			raise OSCConstructMsgError, 'Empty message'

		if len(msgs) > 1 or type(msgs[0]) == list:
			try: 
				return self.constructBundle(*msgs)
			except: 
				raise

		try: msg = self._create_msg(msgs[0])
		except: raise

		return msg


	def send(self, *args):
		''' Construct and send a OSC message;

			* pattern: the OSC address pattern.
			* *args: A tuple of arguments to be appended (in order
			of appearance) to the message as OSC arguments.

		Raises OSCClient.BoundError if trying to use this function
		illegaly.
		'''

		if self._bound:
			try:
				msg = self.constructMessage(*args)
				if msg != None:
#					print " * sending: ", OSC.decodeOSC(msg.getBinary())
					self._sendMessage(self._address, msg.getBinary())
			except OSCConstructMsgError, e:
				raise OSCConstructMsgError, "exception building OSC message (%s): %s" % (str(args), e)
			except OSCClientError, e:
				raise OSCClientError, "error while sending (%s): %s" % (OSC.decodeOSC(msg.getBinary()), e)
		else:
			raise OSCBoundError, "Client not bound to any server"


	def sendUnbound(self, host, port, *args):
		''' Construct and send a OSC message to an arbitrary OSC
		server:

			* host: hostname of the OSC server.
			* port: port the OSC server listens to.
			* pattern: The OSC address pattern.
			* *args: A list of arguments to be appended (in order
			of appearance) to the message as OSC arguments.
		'''
		try:
			msg = self.constructMessage(*args)
			if msg != None:
				self._sendMessage((host, port), msg.getBinary())
		except OSCConstructMsgError, e:
			raise OSCConstructMsgError, "exception building OSC message (%s): %s" % (str(args), e)
		except OSCClientError, e:
			raise OSCClientError, "error while sending (%s): %s" % (OSC.decodeOSC(msg.getBinary()), e)
	



class OSCClientError(Exception):
	def __init__(self, message):
		self.message = message

	def __str__(self):
		return str(self.message)

class OSCConstructMsgError(OSCClientError):
	pass

class OSCServerError(OSCClientError):
	pass

class OSCBoundError(OSCClientError):
	pass

class OSCTimeout(OSCClientError):
	pass
