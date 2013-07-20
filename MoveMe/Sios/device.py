from xml.dom.ext.reader import Sax2
from xml.dom.NodeFilter import NodeFilter

class osc_param(object):
	def __init__(self, name, rel_address, address, type, perms, value, description):
		self.name = str(name)
		self.rel_address = str(rel_address)
		self.address = str(address)
		self.type = str(type)
		self.perms = str(perms)
		self.value = str(value)
		self.description = str(description)

	def __str__(self):
		return "param: " + self.name + ", " + ", " + self.rel_address + ", " + self.address + ", " + self.type + ", " + self.perms + ", " + str(self.value) + ", " + self.description

class osc_method_param(object):
	def __init__(self, num, type, optional, description):
		self.num = int(num)
		self.type = str(type)
		self.optional = str(optional)
		self.description = str(description)

	def __str__(self):
		return "param: " + str(self.num) + ", " + self.type + ", " + self.optional + ", " + self.description


class osc_method(object):

	def __init__(self, name, rel_path, types, direction, description):
		self.name = str(name)
		self.address = ''
		self.types = str(types)
		self.direction = str(direction)
		self.description = str(description)
		self.params = []

		if rel_path != '':
			self.rel_address = str(rel_path) + "/" + self.name
		else:
			self.rel_address = self.name

	def add_param(self, num, type, optional, description):
		param = osc_method_param(num, type, optional, description)
		self.params.append(param)

	def __str__(self):
		rep = "method: " + self.name + ", " + ", " + self.rel_address + ", " +self.address + ", " + self.types + ", " + self.direction + ", " + self.description
		for p in self.params:
			rep = rep + "\n\t" + str(p)
		return rep

class osc_class(object):
	def __init__(self, root, port):
		self.port = int(port)

		self.root = str(root)
		if self.root[len(self.root)-1] != '/':
			self.root = self.root + '/'

	def __str__(self):
		return "osc: " + self.root + ", " + str(self.port)

class module_class(object):
	def __init__(self, sclass, name):
		self.sclass = str(sclass)
		self.name = str(name)
		self.syspath = ""
		self.address = ""
		self.description = ""
		self.params = {}
		self.methods = {}

	def set_phys_path(self, path):
		self.phys_path = path

	def set_osc_path(self, path):
		self.osc_path = path

	def set_description(self, str):
		self.description = str

	def add_param(self, name, rel_path, type, perms, value, description):
		if rel_path != '':
			rel_address = str(rel_path) + "/" + str(name)
		else:
			rel_address = str(name)
		addr = self.address + "/" + rel_address
		param = osc_param(name, rel_address, addr, type, perms, value, description)
		self.params[param.rel_address] = param

	def add_method(self, method):
		self.methods[method.rel_address] = method

	def __str__(self):
		rep = "module: " + self.name + ", " + self.sclass + ", " + self.syspath + ", " + self.address + ", " + self.description
		for p in self.params.values():
			rep = rep + "\n\t" + str(p)
		for m in self.methods.values():
			rep = rep + "\n\t" + str(m)
		return rep

class device_class(object):
	def __init__(self, id):
		self.id = str(id)
		self.osc = None
		self.modules = {}
		self.classes = []

	def set_osc(self, root, port):
		self.osc = osc_class(root, port)

	def add_module(self, module):
		self.modules[module.name] = module

	def add_class(self, sclass):
		self.classes.append(str(sclass))

	def __str__(self):
		rep = "device: " + self.id + "\n\t" + str(self.osc)
		for c in self.classes:
			rep = rep + "\n\t" + "class: " + c
		rep = rep + "\n"
		for m in self.modules.values():
			rep = rep + "\n\t" + str(m) +"\n"
		return rep


reader = Sax2.Reader()

def from_uri(uri):
	global reader

	try:
		doc = reader.fromUri(uri)
	except Exception, e:
		msg = "%s: %s" % (uri, str(e))
		raise SiosURLError(msg)

	syst = doc.getElementsByTagName("sys")
	osc = doc.getElementsByTagName("osc")
	modules = doc.getElementsByTagName("module")
	classes = doc.getElementsByTagName("class")

	id = syst[0].getAttribute('id')
	device = device_class(id)

	if osc:
		root = osc[0].getAttribute('root')
		port = osc[0].getAttribute('port')
		device.set_osc(root, port)

	for c in classes:
		device.add_class(c.getAttribute('name'))

	for m in modules:
		name = m.getAttribute('name')
		sclass = m.getAttribute('class')

		module = module_class(sclass, name)
		module.syspath = m.getElementsByTagName('syspath')[0].getAttribute('value')
		module.address = device.osc.root + sclass + "/" + m.getElementsByTagName('address')[0].getAttribute('value')

		node = m.getElementsByTagName('description')
		module.description = node[0].firstChild.nodeValue

		for params in m.getElementsByTagName('params'):
			for param in params.getElementsByTagName('param'):
				name = param.getAttribute('name')
				type = param.getAttribute('type')
				perms = param.getAttribute('perms')
				value = param.getAttribute('value')
				relpath = param.getAttribute('relative_path')
				value_node = param.getElementsByTagName('value')
				if value_node:
					value = []
					for node in value_node:
						value.append(node.firstChild.nodeValue)
				module.add_param(name, relpath, type, perms, value, "")

		for methods in m.getElementsByTagName('methods'):
			for method in methods.getElementsByTagName('method'):
				name = method.getAttribute('name')
				relpath = method.getAttribute('relative_path')
				types = method.getAttribute('types')
				direction = method.getAttribute('direction')

				description = ""
				node = method.getElementsByTagName('description')
				if node:
					description = node[0].firstChild.nodeValue.strip()

				new_method = osc_method(name, relpath, types, direction, description)
				new_method.address = str(module.address) + "/" + new_method.rel_address

				for param in method.getElementsByTagName('param'):
					num = param.getAttribute('n')
					type = param.getAttribute('type')
					optional = param.getAttribute('optional')
					description = param.getAttribute('description')

					new_method.add_param(num, type, optional, description)

				module.add_method(new_method)
		device.add_module(module)

	return device


class SiosError(Exception):
	'''Base class for exceptions in this module.'''

	pass


class SiosURLError(SiosError):

	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)
