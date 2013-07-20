#!/usr/bin/env python

'''
Implemented at V2_ Lab, for documentation see

	* http://trac.v2.nl/wiki/MoveMeDocumentation

GTK2/Glade implementation of a GUI for the Passepartout / Move.me server
application.
'''

import pygtk, gtk, gtk.glade, gobject

import MoveMe.Representation.context

from MoveMe.GUI.context_frame import *
from MoveMe.GUI.sensor_evaluation_frame import *
from MoveMe.GUI.visualization_cleaned import *
from MoveMe.GUI.visualization_nrml import *
from MoveMe.GUI.visualization_sds import *


class GUI(object):
	'''
	The 'GUI' object contains the top-level funtionality, this includes

		* linkage to the Representation module
		* widget building
		* menu behaviour
		* management of pop-up windows
	'''

	def __init__(self):
		'''
		Initializes global fields for GUI and ContextManager
		objects, builds and loads GUI.
		'''

		self.port = 9999
		self.context_manager = None
		self.context_frame = None
		self.se_frame = None
		self.windows = {}

		try:
			self.widget_tree = gtk.glade.XML("MoveMe/GUI/GUI.glade", "GUI")
		except Exception, e:
			print '!!!Problem loading glade XML'
			raise Exception(e)

		self.connectHandlers()

		self.buildTreeView('context_treeview')
		self.buildTreeView('sensor_evaluation_treeview')

		self.buildCombobox('pillows_combobox')
		self.buildCombobox('persons_combobox')
		self.buildCombobox('sessions_combobox')

		self.load()

		self.tmp_redraw_counter = 0


	def connectHandlers(self):
		''' Automatic connection of general GUI handlers. '''

		handlers = {
			'on_GUI_destroy': (self.quit),
			'on_quit_activate': (self.quit),
		}
		self.widget_tree.signal_autoconnect(handlers)


	def load(self):
		''' Loads GUI by initializing the context through the context
		manager, see representation module. Then creates a ContextFrame
		object which is a GTK Frame widget specificied for the context
		manager. '''

		self.context_manager = MoveMe.Representation.context.ContextManager(self, self.port)
		self.context_frame = ContextFrame(self)
		print ' * Finished loading'


	def quit(self, button):
		''' quits ContextManager, then kills GTK. '''

		if not self.context_manager == None:
			self.context_manager.quit()

		gtk.main_quit()


	def buildTreeView(self, name):
		''' Builds a treeview widget with 'Item' and 'Attributes'
		columns. '''

		widget = self.widget_tree.get_widget(name)
		widget.set_model(gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_STRING))
		widget.set_headers_visible(True)

		renderer = gtk.CellRendererText()
		column = gtk.TreeViewColumn("Item", renderer, text=0)
		column.set_resizable(True)
		widget.append_column(column)

		renderer = gtk.CellRendererText()
		column = gtk.TreeViewColumn("Attributes", renderer, text=1)
		column.set_resizable(True)
		widget.append_column(column)


	def buildCombobox(self, name):
		''' Initializes combobox by setting the model to liststore and
		packing it with a cell renderer. '''

		combobox = self.widget_tree.get_widget(name)
		combobox.set_model(gtk.ListStore(str))
		cell = gtk.CellRendererText()
		combobox.pack_start(cell, True)
		combobox.add_attribute(cell, 'text', 0)


	def activate(self, pillow):
		''' Calls activation functions in Pillow and SensorEvaluationFrame. '''

		pillow.activate()
		self.se_frame.activate()


	def deactivate(self, pillow):
		''' Is called from GUI ContextFrame.

			* Calls ContextManager,
			* calls deactivation function in SensorEvaluationFrame
			and destroys the Visualization window if it exists.
		'''

		self.context_manager.removeSessionForPillow(pillow)

		self.se_frame.deactivate()

		#TODO merge into one routine
		if self.windows.has_key(pillow.name):
			for key, value in self.windows[pillow.name].items():
				self.destroyVisualization(pillow.name, key)


	def remove(self, object):
		''' Object 'disappears' (=undetected) from Context, therefore
		current Context (treeview) information is deleted. '''

		if object == None:
			print '!!!WARNING: trying to remove \'None\' object'
		else:

			try:
				if type(object) == MoveMe.Representation.pillow.Pillow:

					self.context_frame.pillowRemove(object)

				if type(object) == MoveMe.Representation.person.Person:
					self.context_frame.personRemove(object)

				if type(object) == MoveMe.Representation.session.Session:
					self.context_frame.sessionRemove(object)

			except AttributeError, e:
				print '%s type could not be found' % object

			try:
				if type(object) == MoveMe.Representation.pillow.Pillow:
					if self.se_frame != None and self.se_frame.pillow.name == object.name:
						self.se_frame.unload()						
						self.se_frame = None

			except Exception, e:
				print e

	def test(self):
		pass


	def loadSensorEvaluationFrame(self, name, status):
		''' loads pillow settings into the GUI sensor evaluation
		section. A pillow is selected through the pillows-combobox in
		ContextFrame. '''

		if not self.se_frame == None:
			self.se_frame.unload()
			self.se_frame = None

		if status == 'offline':
			# if pillow not online, don't load the sensor
			# evaluation part of the GUI.
			pass
		else:
			# status == 'online-active' or 'online-inactive'
			pillow = self.context_manager.getPillowFromContext(name)
			self.se_frame = SensorEvaluationFrame(self, pillow, status)


	# Pressure visualization functions.

	def createVisualization(self, pillow, type, dimension, decorated):
		''' Creates a new gtk.Window, adds it to global windows dict. '''

		window = gtk.Window()
		drawing_area = None

		if type == 'cleaned':
			drawing_area = VisualizationCleaned(self, pillow, dimension)
			name = pillow.name + ' - cleaned data'
			window.set_title(name)
		if type == 'normalized':
			drawing_area = VisualizationNormalized(self, pillow, dimension)
			name = pillow.name + ' - normalized data'
			window.set_title(name)
		elif type == 'standard_deviations':
			drawing_area = VisualizationStandardDeviations(self, pillow, dimension)
			name = pillow.name + ' - standard deviations'
			window.set_title(name)

		if not drawing_area == None:
			width = pillow.matrix_rows * dimension
			height = pillow.matrix_cols * dimension

			window.add(drawing_area)
			window.set_default_size(height, width)
			window.set_decorated(decorated)

			# Keep track of windows in global dictionary
			#
			# 	self.windows[pillowname][type]
			#
			# where type can be e.g. normalized or standard_deviations

			if self.windows.has_key(pillow.name):
				try:
					if self.windows[pillow.name].has_key(type):
						message = 'Window %s already exists for %s' % (type, pillow.name)
						raise WindowExistsException(message)
					else:
						self.windows[pillow.name][type] = window
				except WindowExistsException, e:
					print e
			else:
				self.windows[pillow.name] = {type:window}

			window.show_all()
		else:
			print '!!!Error: visualization type not known'''


	def destroyVisualization(self, name, type):
		''' Destroys window and removes it from windows dict. '''

		try:
			window = self.windows[name][type]
		except:
			print 'window of type %s for %s could not be found' % (type, name)

		window.destroy()


	def removeVisualizationWindow(self, name, type):
		''' Deletes pressure-visualization window from dict. '''

		try:
			del self.windows[name][type]
		except:
			print '!!!Error: (in removeVisualizationWindow()) window of type %s for %s could not be found' % (type, name)


	def resetVisualizationButton(self, name, type):
		''' Sees if matching frame is currently open; if so calls
		resetVisualizationButtion() from SensorEvaluationFrame. '''

		if not self.se_frame == None:
			if self.se_frame.pillow.name == name:
				self.se_frame.resetVisualizationButton(type)


	def redrawProcessing(self, pillow, type, data):

		if not self.se_frame == None:
			if self.se_frame.pillow.name == pillow.name:
				self.se_frame.setProcessingData(type, data)


	def redrawVisualization(self, pillow, dict):
		''' Searches windows dict for window with pillow name, if found calls redraw. '''

		if self.windows.has_key(pillow.name):

			if self.windows[pillow.name].has_key('cleaned'):
				window = self.windows[pillow.name]['cleaned']

				try:
					window.get_children()[0].redraw(dict['center_of_gravity'], dict['visualization_cleaned'])

				except Exception, e:
					print '!!!Error drawing pillow data', e
					raise

			if self.windows[pillow.name].has_key('normalized'):
				window = self.windows[pillow.name]['normalized']

				try:
					window.get_children()[0].redraw(dict['center_of_gravity'], dict['visualization_normalized'])

				except Exception, e:
					print '!!!Error drawing pillow data', e
					raise

			if self.windows[pillow.name].has_key('standard_deviations'):
				window = self.windows[pillow.name]['standard_deviations']

				try:
					window.get_children()[0].redraw(dict)

				except Exception, e:
					print 'Error running standard deviations visualization', e
					raise

class GUIError(Exception):
	'''Base class for exceptions in this module.'''

	pass


class WindowExistsError(GUIError):

	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)
