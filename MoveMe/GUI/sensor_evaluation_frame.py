#!/usr/bin/env python

'''
Implemented at V2_ Lab, for documentation see

	* http://trac.v2.nl/wiki/MoveMeDocumentation
'''

import pygtk, gtk

from frame import *
from MoveMe.Visualization import *

class SensorEvaluationFrame(Frame):
	'''
	Handles the pillow specific functionality in the bottom
	frame of the GUI.
	'''


	def __init__(self, gui, pillow, mode):
		'''
		Initializes globals and (re)loads the widgets.
		Connections are saved in a dictionary to be able to
		dynamically reconnect them on pillow change. The
		frame should be called with one of the following modes:

			* offline,
			* online-inactive or
			* online-active.

		Modes are later on switched according to the pillow state.
		'''

		self.gui = gui
		self.pillow = pillow
		self.mode = mode
		self.default_dimension = 50
		self.connected_to_processing = False
		self.accmag_factor = 40

		self.connections = self.connectHandlers()

		Frame.__init__(self, self.gui.widget_tree)
		self.setMode(mode)

		if mode == 'online-active' or mode == 'online-inactive':
			self.loadConfigurationTree()


	def loadConfigurationTree(self):
		''' Loads the sensor & actuator parameter treeview. '''

		model = self.gui.widget_tree.get_widget('sensor_evaluation_treeview').get_model()
		treeview_pillow = model.append(None, ('pillow', self.pillow.name))

		for module_name, module in self.pillow.modules.items():

			treeview_module = model.append(treeview_pillow, ('module', module_name))

			for key, value in self.pillow.modules[module_name].items():

				treeview_sensor = model.append(treeview_module, (key, None))

				for method_name, method in value.methods.items():

					treeview_method = model.append(treeview_sensor, ('method', method_name))

					model.append(treeview_method, ('name', method.name))
					model.append(treeview_method, ('rel. address', method.rel_address))
					model.append(treeview_method, ('address', method.address))
					model.append(treeview_method, ('types', method.types))
					model.append(treeview_method, ('direction', method.direction))
					model.append(treeview_method, ('description', method.description))

					for param in method.params:
						treeview_param = model.append(treeview_method, ('param', param.description))
						model.append(treeview_param, ('num', param.num))
						model.append(treeview_param, ('type', param.type))
						model.append(treeview_param, ('optional', param.optional))



	def connectHandlers(self):
		''' (Re)connect when new sensor evaluation is in place.
		Returns a dict containing connection id's for all connections. '''

		connections = {}

		# Pressure widgets.

		widget = self.gui.widget_tree.get_widget('cleaned_button')
		connections['cleaned_button'] = widget.connect('toggled', self.visualizationCB)

		widget = self.gui.widget_tree.get_widget('normalized_button')
		connections['normalized_button'] = widget.connect('toggled', self.visualizationCB)

		widget = self.gui.widget_tree.get_widget('sd_button')
		connections['sd_button'] = widget.connect('toggled', self.visualizationCB)

		widget = self.gui.widget_tree.get_widget('gesture_summaries')
		connections['gesture_summaries'] = widget.connect('toggled', self.summaryCB)

		widget = self.gui.widget_tree.get_widget('save_button')
		connections['save_button'] = widget.connect('clicked', self.saveCB)

		widget = self.gui.widget_tree.get_widget('restore_button')
		connections['restore_button'] = widget.connect('clicked', self.restoreCB)

		for key, value in self.pillow.config.dict.items():
			if value[4] == 'slider':
				name = key
				default_value = value[0]
				min = value[1]
				max = value[2]
				evaluator = value[3]

				try:
					connections[name] = self.connectSlider(name, evaluator, 'change_value', default_value, min, max)
				except:
					print '!!!Error: couldn\'t connect slider %s' % name
					raise

		# Motion widgets.
		widget = self.gui.widget_tree.get_widget('processing_button')
		connections['processing_button'] = widget.connect('clicked', self.processingCB)

		# LED widgets.
		widget = self.gui.widget_tree.get_widget('light_test_button')
		connections['light_test_button'] = widget.connect('clicked', self.lightTestCB)

		# Tone widgets.
		widget = self.gui.widget_tree.get_widget('tone_test_button')
		connections['tone_test_button'] = widget.connect('clicked', self.toneTestCB)

		# Buzzer widgets.
		widget = self.gui.widget_tree.get_widget('buzzer_test_button')
		connections['buzzer_test_button'] = widget.connect('clicked', self.buzzerTestCB)

		return connections


	def connectSlider(self, name, evaluator, signal, default_value, min, max):
		''' General function to connect sliders to the correct evaluator values. '''

		widget = self.gui.widget_tree.get_widget(name)
		widget.set_range(min, max)
		widget.set_value(default_value)

		return widget.connect(signal, self.sliderCB, evaluator, name, max)


	def pressureSlidersSensitive(self, boolean):
		''' Set pressure slider widgets to sensitive mode. '''

		for key, value in self.pillow.config.dict.items():
			if value[4] == 'slider':

				name = key

				widget = self.gui.widget_tree.get_widget(name)
				widget.set_sensitive(boolean)


	def summaryCB(self, button):
		if button.get_active():
			self.gui.context_manager.print_summary = True
		else:
			self.gui.context_manager.print_summary =  False

	def saveCB(self, widget):
		self.gui.context_manager.savePillowConfiguration(self.pillow)


	def restoreCB(self, widget):
		self.gui.context_manager.restorePillowDefaultConfiguration(self.pillow)

		for key, values in self.pillow.config.dict.items():
			widget = self.gui.widget_tree.get_widget(key)
			widget.set_value(values[0])
			#TODO: check if min & max values have changed


	def lightTestCB(self, widget):
		''' Function to test if a LED works. '''

		combobox = self.gui.widget_tree.get_widget('led_combobox')
		value = self.getComboboxText(combobox)

		r = int(self.gui.widget_tree.get_widget('red_hscale').get_value())
		g = int(self.gui.widget_tree.get_widget('red_hscale').get_value())
		b = int(self.gui.widget_tree.get_widget('red_hscale').get_value())

		if value == None:
			pass
		elif value == 'All':
			self.pillow.lightAll((r,g,b))
		else:
			self.pillow.light(int(value),(r,g,b))


	def toneTestCB(self, widget): self.pillow.beep(100, 100)


	def buzzerTestCB(self, widget): self.pillow.buzz(220, 1000)


	def unload(self):
		''' Clears the treeview and disconnects the buttons. '''

		self.unloadTreeView('sensor_evaluation_treeview')

		for key, value in self.connections.items():
			widget = self.gui.widget_tree.get_widget(key)
			widget.disconnect(value)

		self.gui.widget_tree.get_widget('pressure_vbox').set_sensitive(False)
		


	def setMode(self, mode):
		''' Determines button sensitivity and toggle settings dynamically. '''

		self.gui.widget_tree.get_widget('sensor_evaluation_config').set_sensitive(True)
		self.set_sensitive_values(mode)
		self.set_active_values(mode)


	def set_active_values(self, mode):
		''' '''

		cleaned_button = self.gui.widget_tree.get_widget('cleaned_button')
		normalized_button = self.gui.widget_tree.get_widget('normalized_button')
		sd_button = self.gui.widget_tree.get_widget('sd_button')


		if mode == 'online-active':
			if self.gui.windows.has_key(self.pillow.name):
				if self.gui.windows[self.pillow.name].has_key('cleaned'):
					cleaned_button.set_active(True)
				if self.gui.windows[self.pillow.name].has_key('normalized'):
					normalized_button.set_active(True)
				if self.gui.windows[self.pillow.name].has_key('standard_deviations'):
					sd_button.set_active(True)
			else:
				cleaned_button.set_active(False)
				normalized_button.set_active(False)
				sd_button.set_active(False)


	def set_sensitive_values(self, mode):
		''' '''

		cleaned_button = self.gui.widget_tree.get_widget('cleaned_button')
		normalized_button = self.gui.widget_tree.get_widget('normalized_button')
		sd_button = self.gui.widget_tree.get_widget('sd_button')
		pressure_vbox = self.gui.widget_tree.get_widget('pressure_vbox')
		motion_vbox = self.gui.widget_tree.get_widget('motion_vbox')
		led_vbox = self.gui.widget_tree.get_widget('led_vbox')
		tone_vbox = self.gui.widget_tree.get_widget('tone_vbox')
		buzzer_vbox = self.gui.widget_tree.get_widget('buzzer_vbox')

		if mode == 'offline':
			### parameters not tweakable, pressure visualization off
			pressure_vbox.set_sensitive(False)
			motion_vbox.set_sensitive(False)
			led_vbox.set_sensitive(False)
			tone_vbox.set_sensitive(False)
			buzzer_vbox.set_sensitive(False)
			cleaned_button.set_sensitive(False)
			normalized_button.set_sensitive(False)
			sd_button.set_sensitive(False)
			self.pressureSlidersSensitive(False)
		elif mode == 'online-inactive':
			### parameters tweakable, pressure visualization off
			pressure_vbox.set_sensitive(True)
			motion_vbox.set_sensitive(True)
			led_vbox.set_sensitive(True)
			tone_vbox.set_sensitive(True)
			buzzer_vbox.set_sensitive(True)
			cleaned_button.set_sensitive(False)
			normalized_button.set_sensitive(False)
			sd_button.set_sensitive(False)
			self.pressureSlidersSensitive(False)
		elif mode == 'online-active':
			### parameters tweakable, pressure visualization on

			pressure_vbox.set_sensitive(True)
			motion_vbox.set_sensitive(True)
			led_vbox.set_sensitive(True)
			tone_vbox.set_sensitive(True)
			buzzer_vbox.set_sensitive(True)
			cleaned_button.set_sensitive(True)
			normalized_button.set_sensitive(True)
			sd_button.set_sensitive(True)
			self.pressureSlidersSensitive(True)


	def activate(self):
		''' Change to 'online-active' status '''

		self.setMode('online-active')


	def deactivate(self):
		''' Change to 'online-inactive' status '''

		self.setMode('online-inactive')


	def visualizationCB(self, button):
		''' Button behaviour pressure visualization widget. '''

		# multiple visualization types possible, such as normalized,
		# standard_deviations...
		type = button.name.split('_')[0]
		if type == 'sd': type = 'standard_deviations'

		if button.get_active():

			if self.gui.windows.has_key(self.pillow.name) and self.gui.windows[self.pillow.name].has_key(type):
					pass
			else:
				widget = self.gui.widget_tree.get_widget('dimension_entry')
				dimension_text = widget.get_text()
				dimension = self.getDimension(dimension_text)
				checkbox = self.gui.widget_tree.get_widget('decorated')

				self.gui.createVisualization(self.pillow, type, dimension, checkbox.get_active())
		else:
			if self.gui.windows.has_key(self.pillow.name):
				if self.gui.windows[self.pillow.name].has_key(type):
					self.gui.destroyVisualization(self.pillow.name, type)


	def processingCB(self, button):
		''' Connect accelerometer data to processing with OSC. '''

		address = '127.0.0.1'
		port = 12000
		self.motion_visualization = Visualization(address, port)
		self.connected_to_processing = True
		print ' * Connecting %s motion data to processing, %s, %s' % (self.pillow.name, address, port)


	def setProcessingData(self, type, data):

		if self.connected_to_processing:

			processing_list = []
			processing_list.append(type)

			for value in data:
				value = int(value*self.accmag_factor)
				processing_list.append(value)

			self.motion_visualization.data(processing_list)


	def getDimension(self, str):
		''' Test if GUI dimension text entry is integer, else default to 360. '''

		try:
			s = int(str)
		except:
			s = self.default_dimension

		return s


	def resetVisualizationButton(self, type):
		''' Sets (sensitive) button to inactive state. '''

		if type == 'cleaned':
			cleaned_button = self.gui.widget_tree.get_widget('cleaned_button')
			cleaned_button.set_active(False)

		if type == 'normalized':
			normalized_button = self.gui.widget_tree.get_widget('normalized_button')
			normalized_button.set_active(False)

		elif type == 'standard_deviations':
			sd_button = self.gui.widget_tree.get_widget('sd_button')
			sd_button.set_active(False)


	def sliderCB(self, range, scroll, value, evaluator, name, max):
		''' Connect slider to according sensor evaluation parameter. '''

		if value > max: value = max

		self.pillow.adjustSensorParameter(evaluator, name, value)
