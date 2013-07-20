from xml.dom.ext.reader import Sax2
from xml.dom.NodeFilter import NodeFilter

class uCodeFalsifier(object):
	def __setattr__(self, key, value):
		if type(value) == unicode:
			value = str(value)
		self.__dict__[key] = value
	

class siosOscMethod(uCodeFalsifier):
	def __init__(self, name="", address="", types="", description=""):
		self.name = name
		self.address = address
		self.types = types
		self.description = description
		self._oscClient = None
	
	def __str__(self):
		return str(self.__dict__)

	def setOscClient(self, oscClient=None):
		self._oscClient = oscClient

	def send(self, *args):
		try: self._oscClient.send(args)
		except Exception, e: 
			msg = "Method %s could not send '%s': %s" % (self.name, args, str(e))
			raise siosMethodError(msg)


class siosOscParameter(siosOscMethod):
	pass


class siosModule(uCodeFalsifier):
	def __init__(self, klass="", name="", description="", syspath="", address=""):
		self.klass = klass
		self.name = name
		self.description = description
		self.syspath = syspath
		self.address = address
		self._reader = None
	
	def __str__(self):
		return str(self.__dict__)

	def _parseDoc(self, doc):
		try:
			self.name = doc.getAttribute('name')
			self.klass = doc.getAttribute('class')

			node = doc.getElementsByTagName('description')
			if node: self.description = node[0].firstChild.nodeValue.strip()

			node = doc.getElementsByTagName('syspath')
			if node: self.syspath = node[0].getAttribute('value')
			
			node = doc.getElementsByTagName('address')
			if node: self.address = node[0].getAttribute('value')

			for methodsElements in doc.getElementsByTagName('methods'):
				for methodElement in methodsElements.getElementsByTagName('method'):
					node = methodElement.getElementsByTagName('description')
					if node:
						descr = node[0].firstChild.nodeValue.strip()
					method = siosOscMethod(name=methodElement.getAttribute('name'),
							       address=methodElement.getAttribute('address'),
							       types=methodElement.getAttribute('types'),
							       description=descr)
					try: self.addMethod(method)
					except Exception, e: print str(e)

			for paramElements in doc.getElementsByTagName('params'):
				for paramElement in methodsElements.getElementsByTagName('param'):
					node = methodElement.getElementsByTagName('description')
					if node:
						descr = node[0].firstChild.nodeValue.strip()
					param = siosOscParameter(name=paramElement.getAttribute('name'),
							       	 address=paramElement.getAttribute('address'),
							       	 types=paramElement.getAttribute('types'),
							       	 description=descr)
					try: self.addParameter(param)
					except Exception, e: print str(e)

		except Exception, e:
			raise siosParseError(str(e))

	def fromUri(self, uri, validate=1):
		self.uri = uri
		self._reader = Sax2.Reader(validate=validate)

		try: 
			doc = self._reader.fromUri(self.uri)
		except Exception, e:
			msg = "%s: %s" % (self.uri, str(e))
			raise siosUriError(msg)

	def fromElement(self, element):
		self._parseDoc(element)

	def addMethod(self, method):
		try: self.__dict__[method.name]
		except: self.__dict__[method.name] = method
		else: 
			msg = "method '%s' already exists for module '%s'" % (method.name, self.name)
			raise siosModuleError(msg)

	def addParameter(self, parameter):
		try: self.__dict__[parameter.name]
		except: self.__dict__[parameter.name] = parameter
		else: 
			msg = "parameter '%s' already exists for module '%s'" % (parameter.name, self.name)
			raise siosModuleError(msg)



class siosOscService(uCodeFalsifier):
	def __init__(self, port=0, proto="udp", root="/"):
		self.port = int(port)
		self.proto = proto
		self.root = root
	
	def __str__(self):
		return str(self.__dict__)


class siosDevice(uCodeFalsifier):
	def __init__(self):
		self.classes = []
		self.oscServices = []
		self.modules = {}
		self._reader = None
		self.uri = ""

	def __str__(self):
		return str(self.__dict__)

	def _parseDoc(self, doc):
		try:
			self._oscElements = doc.getElementsByTagName("osc")
			self._classElements = doc.getElementsByTagName("class")
			self._modulesElements = doc.getElementsByTagName("module")

			for classElement in self._classElements:
				self.addClass(str(classElement.getAttribute('name')))

			for oscElement in self._oscElements:	
				service = siosOscService(port=oscElement.getAttribute('port'),
							 proto=oscElement.getAttribute('proto'),
							 root=oscElement.getAttribute('root'))
				self.addOscService(service)

			for moduleElement in self._modulesElements:
				module = siosModule()
				module.fromElement(moduleElement)
				self.addModule(module)
		except Exception, e:
			raise siosParseError(str(e))

	def fromUri(self, uri, validate=1):
		self.uri = uri
		self._reader = Sax2.Reader(validate=validate)

		try: 
			doc = self._reader.fromUri(self.uri)
		except Exception, e:
			msg = "%s: %s" % (self.uri, str(e))
			raise siosUriError(msg)
		else:
			self._parseDoc(doc)
		
	def addOscService(self, service):
		self.oscServices.append(service)

	def addClass(self, klass):
		self.classes.append(klass)

	def addModule(self, module):
		self.modules[module.name] = module
		self.__dict__[module.name] = module
		
class siosError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)


class siosModuleError(siosError):
	pass

class siosMethodError(siosError):
	pass

class siosUriError(siosError):
	pass

class siosParseError(siosError):
	pass

if __name__ == '__main__':
	dev = siosDevice()
	try:
		dev.fromUri("/Users/simon/Development/V2_/SIOS/testxml.xml")
	except Exception, e:
		print "ouch: %s" % str(e)

	print dev
	for module in dev.modules:
		print dev.modules[module]
	for osc in dev.oscServices:
		print osc

	print ''
	try:
		if hasattr(dev, 'matrix'):
			print dev.matrix.syspath
			print dev.matrix.listen
		print hasattr(dev, 'foo')
		print dev.accmag.mag_listen.send('bla')
		print dev.accmag.bla
	except Exception, e:
		print "exception '%s'" % str(e)
