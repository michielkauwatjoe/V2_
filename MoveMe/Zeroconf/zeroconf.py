#!/usr/bin/env python

'''
Implemented at V2_ Lab, for documentation see

	* http://trac.v2.nl/wiki/MoveMeDocumentation

Functionality to access pybonjour package.
'''

try:
	import bonjour
except ImportError:
	raise ImportError("The bonjour python package needs to be installed")

import sys, socket
import gobject



SERVICE_TYPE = '_pillow._udp'
SERVICE_DOMAIN = 'local.'

# bonjour service references of the form: {repr(ref):(ref,source)}
active_refs = {}

# bonjour callbacks
def _fd_callback(source, condition, service):
	if service:
		bonjour.DNSServiceProcessResult(service)
	return True


def _register_callback(sdRef, flags, errorCode, name, regtype, domain, userdata):
	print "Service registered:", name, regtype

# these are defined by dns_sd.h but not reflected by bonjour-py
SERVICE_TYPE_A = 1
SERVICE_CLASS_IN = 1


def _query_callback(sdRef, flags, interface,
			errorCode, fullname, rrtype,
			rrclass, rdlen, rdata,
			ttl, args):

	# see FIXME in _browse_callback
	local_ref = args['ref']

	# get rid of the reference before passing **args to the adder
	args.pop('ref')

	if (rrtype == SERVICE_TYPE_A) and (rrclass == SERVICE_CLASS_IN):
		if rdlen < 4:
			return
		address = "%d.%d.%d.%d" % (ord(rdata[0]), ord(rdata[1]), ord(rdata[2]), ord(rdata[3]))
		if args['adder']:
			args['address'] = address
			args['adder'](**args)

	# were done with this service here but we can only remove
	# the source because we are still in the callback. But that
	# is ok because we are not listening to the source any longer.
	# The actual server reference will be deallocated as soon as
	# the destroy() method is issued
	source = _del_source(local_ref)
	if source:
		gobject.source_remove(source)


def _resolve_callback(sdRef, flags, interface,
			errorCode, fullname, host,
			port, txtLen, txtRecord, args):

	args['host'] = host
	args['port'] = socket.ntohs(port)
	args['fullname'] = fullname

	# extend args with txtRecord entries
	TXTdict = rentry_to_dict(txtRecord, txtLen)
	args.update(TXTdict)

	# see FIXME in _browse_callback
	local_ref = args['ref']
	service_ref = bonjour.AllocateDNSServiceRef()
	args['ref'] = service_ref

	# Find out the address by querying the DNS A record.
	# This solves the problem of resolving hostnames like:
	# myhostname.local. with gethostbyname()
	retval = bonjour.pyDNSServiceQueryRecord(service_ref,
						0,
						interface,
						host,
						SERVICE_TYPE_A,
						SERVICE_CLASS_IN,
						_query_callback,
						args)
	fd = bonjour.DNSServiceRefSockFD(service_ref)
	source = gobject.io_add_watch(fd, gobject.IO_IN, _fd_callback, service_ref)
	_add_ref(service_ref, source)

	# were done with this service here but we can only remove
	# the source because we are still in the callback. But that
	# is ok because we are not listening to the source any longer.
	# The actual server reference will be deallocated as soon as
	# the destroy() method is issued
	source = _del_source(local_ref)
	if source != None:
		gobject.source_remove(source)


def _browse_callback(sdRef, flags, interfaceIndex,
			errorCode, serviceName, regtype,
			replyDomain, priv):
	if flags & bonjour.kDNSServiceFlagsAdd:
		args = priv.copy()

		args['name'] = serviceName
		service_ref = bonjour.AllocateDNSServiceRef()

		# FIXME (or better bonjour-py)
		# Bug in bonjour-py gives corrupt sdRef in callbacks
		# referencing sdRef results in a segfault!
		# The only way now is to pass a valid reference by means
		# of the user args. Badaboom!
		args['ref'] = service_ref
		retval = bonjour.pyDNSServiceResolve(service_ref, 0, 0,
							serviceName, regtype,
							replyDomain, _resolve_callback,
							args)
		fd = bonjour.DNSServiceRefSockFD(service_ref)
		source = gobject.io_add_watch(fd, gobject.IO_IN, _fd_callback, service_ref)
		_add_ref(service_ref, source)

	elif flags == 0:
		if priv['remover']:
			args = {'name': serviceName}
			priv['remover'](**args)


# utility functions

def _add_ref(r,s):
	rr = repr(r)
	if not active_refs.has_key(rr):
		active_refs[rr] = (r,s)


def _del_ref(r):
	rr = repr(r)
	if active_refs.has_key(rr):
		t = active_refs.pop(rr)
		return t[1]
	return None


def _get_source(r):

	rr = repr(r)
	if active_refs.has_key(rr):
		t = active_refs[rr]
		return t[1]
	return None


def _del_source(r):

	rr = repr(r)
	if active_refs.has_key(rr):
		t = active_refs[rr]
		s = t[1]
		t = (r, None)
		active_refs[rr] = t
		return s
	return None


def create_rentry(_prop, _val):

	t = _prop + '=' + str(_val)
	l = chr(len(t))
	return (l + t)


def create_rentry_from_dict(_dict):

	rentry = ""
	for k,v in _dict.iteritems():
		rentry = rentry + create_rentry(k, v)
	return rentry


def rentry_to_dict(rentry, bytes):
	'''
	'''

	d = {}
	if bytes <= 1:
		return d
	while len(rentry):
		n = ord(rentry[0]) + 1
		tmp = rentry[1:n]
		rentry = rentry[n:bytes]
		bytes = bytes - n
		t,v = tmp.split('=')
		d[t] = v
	return d


# main functionality

def register(name, port, stype='', rentry='' , host=''):
	'''
	'''

	rdata = ""
	if type(rentry) == dict:
		rdata = create_rentry_from_dict(rentry)
	else:
		rdata = rentry

	service_ref = bonjour.AllocateDNSServiceRef()

	if type == '':
		stype = SERVICE_TYPE

	retval = bonjour.pyDNSServiceRegister(service_ref, 0, 0,
						name, stype, SERVICE_DOMAIN,
						host, socket.htons(port),
						len(rdata), rdata, _register_callback,
						None)

	if retval != bonjour.kDNSServiceErr_NoError:
		message = "Error registering service %s (%d)" % (name, retval)
		raise RegisterError(message, reference=service_ref, errorval=retval)

	fd = bonjour.DNSServiceRefSockFD(service_ref)
	source = gobject.io_add_watch(fd, gobject.IO_IN, _fd_callback, service_ref)
	_add_ref(service_ref, source)


def discover(stype='', adder=None, remover=None, *userdata):
	'''
	'''

	service_ref = bonjour.AllocateDNSServiceRef()

	args = {'adder': adder, 'remover': remover, 'other':userdata, 'ref': service_ref}

	if stype == '':
		stype = SERVICE_TYPE

	retval = bonjour.pyDNSServiceBrowse(service_ref, 0, 0,
						stype, SERVICE_DOMAIN,
						_browse_callback, args)

	if retval != bonjour.kDNSServiceErr_NoError:
		message = "unable to allocate service discovery"
		raise BrowseError(message, reference=service_ref, errorval=retval)

	fd = bonjour.DNSServiceRefSockFD(service_ref)
	source = gobject.io_add_watch(fd, gobject.IO_IN, _fd_callback, service_ref)
	_add_ref(service_ref, source)


def destroy():
	'''
	'''

	# first remove active sources as RefDeallocate leaves them in undefined state
	for r in active_refs.keys():
		t = active_refs.pop(r)
		if t[1] != None:
			gobject.source_remove(t[1])
		bonjour.DNSServiceRefDeallocate(t[0])


# exceptions
class ZeroconfError(Exception):
	def __init__(self, message, reference=None, errorval=None):
		self.message = message
		self.reference = reference
		self.errorval = errorval

	def __str__(self):
		return "%s (%d): %s" % (str(self.reference), self.errorval, self.message)
	
	def __repr__(self):
		return str(self)


class RegisterError(ZeroconfError):
	pass


class BrowseError(ZeroconfError):
	pass
