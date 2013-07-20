#!/usr/bin/env python

'''
Implemented at V2_ Lab, for documentation see

 http://trac.v2.nl/wiki/MoveMeDocumentation
'''

import pygtk, gtk, gtk.glade, gobject

from MoveMe.GUI.frame import *
import MoveMe.Representation.context


class ContextFrame(Frame):
	''' Handles GUI Context functionality. '''


	def __init__(self, gui):
		''' Loads new Context settings and connects the handlers. '''

		self.gui = gui

		Frame.__init__(self, self.gui.widget_tree)

		self.load()
		self.connectHandlers()


	def load(self):
		''' Loads database values into comboboxes. '''

		list = self.gui.context_manager.memory_db_interface.getAllTables(True)
		pillows, persons, sessions = list

		self.loadCombobox('pillows_combobox', pillows)
		self.loadCombobox('persons_combobox', persons)
		self.loadCombobox('sessions_combobox', sessions)


	def connectHandlers(self):
		''' Connects all the context buttons and combobox callbacks. '''

		widget = self.gui.widget_tree.get_widget('pillows_combobox')
		widget.connect('changed', self.pillowsComboboxChangedCB)
		widget = self.gui.widget_tree.get_widget('pillow_activate_button')
		widget.connect('toggled', self.pillowActivateCB)

		widget = self.gui.widget_tree.get_widget('persons_combobox')
		widget.connect('changed', self.personsComboboxChangedCB)
		widget = self.gui.widget_tree.get_widget('person_add_button')
		widget.connect('clicked', self.personAddCB)
		widget = self.gui.widget_tree.get_widget('person_remove_button')
		widget.connect('clicked', self.personDeleteCB)

		widget = self.gui.widget_tree.get_widget('sessions_combobox')
		widget.connect('changed', self.sessionsComboboxChangedCB)

		# TODO move to __init__.py
		handlers = {
			'on_clear_pillows_activate': (self.clearTable, 'pillows'),
			'on_clear_persons_activate': (self.clearTable, 'persons'),
			'on_clear_sessions_activate': (self.clearTable, 'sessions'),
			'on_save_button_toggled': (self.save),
		}

		self.gui.widget_tree.signal_autoconnect(handlers)


	def new(self, object):
		''' New, unknown object is detected, rerouted to correct GUI
		functionality. '''

		if object == None:
			print '!!!WARNING: trying to add \'None\' object'

		else:
			try:
				if type(object) == MoveMe.Representation.pillow.Pillow:
					self.addToCombobox('pillows_combobox', object.name)

				elif type(object) == MoveMe.Representation.person.Person:
					self.addToCombobox('persons_combobox', object.name)

				elif type(object) == MoveMe.Representation.session.Session:
					self.addToCombobox('sessions_combobox', object.timestamp)

			except AttributeError, e:
				print '%s type could not be found', object


	def register(self, object):
		''' Object has been detected by Contextmanager, so is rerouted
		to correct GUI functionality.  '''

		if object == None:
			print '!!!WARNING: trying to add \'None\' object'

		else:
			try:
				if type(object) == MoveMe.Representation.pillow.Pillow:
					self.registerPillow(object)

				elif type(object) == MoveMe.Representation.person.Person:
					self.registerPerson(object)

				elif type(object) == MoveMe.Representation.session.Session:
					self.registerSession(object)

			except AttributeError, e:
				print '%s type could not be found', object


	# FIXME move to graphical_user_interface.py
	def clearTable(self, menuItem, tablename): self.resetTable(tablename)


	# FIXME move to graphical_user_interface.py
	def resetTable(self, tablename):
		''' Resets SQL table contents in GUI, calls resetTable from context manager. '''

		combobox_name = tablename + '_combobox'
		self.unloadCombobox(combobox_name)

		list = self.gui.context_manager.resetTable(tablename)
		self.loadCombobox(combobox_name, list)

		print ' * %s table cleared.' % tablename


	''' Pillow Functionality '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	def registerPillow(self, pillow):
		''' Adds pillow name and information to context tree (on
		detection). Does _not_ add it to the database section. '''

		try:
			model = self.gui.widget_tree.get_widget('context_treeview').get_model()
			parent = model.append(None, (pillow.name, None))
			attr = model.append(parent, ('Status', 'active'))

			combobox = self.gui.widget_tree.get_widget('pillows_combobox')
			widget = self.gui.widget_tree.get_widget("pillow_activate_button")

			# check if the currently selected pillow from the drop-down box
			# is identical to the pillow being registered
			if not combobox.get_active_text() == None:
				name = combobox.get_active_text()
				if pillow.name == name:
					widget.set_sensitive(True)
					self.showPillowValues(pillow.name)
					
					self.gui.loadSensorEvaluationFrame(pillow.name, 'online-active')

		except Exception, e:
			print '\'%s\' not added to tree.' % (pillow.name)
			raise Exception(e)


	def pillowRemove(self, pillow):
		'''
			* Removes pillow from context tree,
			* disables 'activate' button.
		'''

		self.removeFromTreeView(pillow.name, 'context_treeview')
		combobox = self.gui.widget_tree.get_widget('pillows_combobox')
		button = self.gui.widget_tree.get_widget("pillow_activate_button")


		if self.isSelectedInCombobox(pillow.name, combobox):
			self.setButtonSensitive(button, False)


	def pillowsComboboxChangedCB(self, combobox):
		''' Pillow combobox callback.

			* shows pillow values
			* enables/disables 'activate' button
			* enables sensor evaluation frame
		'''

		name = self.getComboboxText(combobox)
		pillow = self.gui.context_manager.getPillowFromContext(name)
		activate_button = self.gui.widget_tree.get_widget("pillow_activate_button")
		status = None

		self.showPillowValues(name)
		self.current_pillowname = name

		if pillow == None:
			self.setButtonSensitive(activate_button, False)
			status = 'offline'
		else:
			self.setButtonSensitive(activate_button, True)
			if pillow.isActive():
				activate_button.set_active(True)
				status = 'online-active'
			else:
				activate_button.set_active(False)
				status = 'online-inactive'

		self.gui.loadSensorEvaluationFrame(name, status)


	def showPillowValues(self, name):
		''' Displays pillow parameter values. '''

		result = self.gui.context_manager.memory_db_interface.getRow('pillows', 'name', name)[0]
		id = result[1]

		if len(id) > 21:
			id = id[0:17] + '...'

		self.gui.widget_tree.get_widget('id_label').set_text(id)
		self.gui.widget_tree.get_widget('address_label').set_text(result[2])
		self.gui.widget_tree.get_widget('host_label').set_text(result[3])
		self.gui.widget_tree.get_widget('port_label').set_text(str(result[4]))


	def pillowActivateCB(self, button):
		'''
		Toggles pillow active / inactive.
		'''

		pillow = self.gui.context_manager.getPillowFromContext(self.current_pillowname)
		status = None
		tree_store = self.gui.widget_tree.get_widget('context_treeview').get_model()

		for x in range(len(tree_store)):
			iter = tree_store.get_iter(x)
			name = tree_store.get_value(iter, 0)
			if name == self.current_pillowname:
				status = tree_store.iter_nth_child(iter, 0)

		if button.get_active():
			if not pillow.isActive():
				self.gui.activate(pillow)
				tree_store.set_value(status, 1, 'active')
		else:
			if pillow.isActive():
				self.gui.deactivate(pillow)
				tree_store.set_value(status, 1, 'inactive')


	''' Person Functionality '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	def registerPerson(self, person):
		'''
		Adds person name and information to context tree (on detection).
		Does _not_ add it to the database section.
		'''

		try:

			tree_store = self.gui.widget_tree.get_widget('context_treeview').get_model()
			parent = tree_store.append(None, (person.name, None))
			attr = tree_store.append(parent, ("Status", 'detected'))

		except Exception, e:
			print '%s not added to GUI.' % (person.name)
			raise Exception(e)


	def personAddCB(self, button):
		''' Placeholder, strips button parameter. '''

		self.personAddDialog()


	def personAddDialog(self, *args):
		''' Adds a new person to the database. '''

		widget_tree = gtk.glade.XML('MoveMe/GUI/GUI.glade', 'personEntry')
		dialog = widget_tree.get_widget('personEntry')
		firstname_entry = widget_tree.get_widget('firstname_entry')
		lastname_entry = widget_tree.get_widget('lastname_entry')
		okbutton = widget_tree.get_widget('okbutton')
		label = widget_tree.get_widget('label')

		# write commentary argument to label
		if len(args) > 0: label.set_text(args[0])

		okbutton.grab_default()
		result = dialog.run()
		dialog.destroy()

		if result == gtk.RESPONSE_CANCEL:
			return

		elif result == gtk.RESPONSE_OK:
			firstname = firstname_entry.get_text().strip()
			lastname = lastname_entry.get_text().strip()

			fullname = firstname + ' ' + lastname

			if firstname == '' or lastname == '':
				self.personAddDialog('A first and last name are required.')
			elif not self.gui.context_manager.getPersonFromDB(fullname) == None:
				self.personAddDialog('person already exists')
			else:
				person = self.gui.context_manager.addPerson(firstname, lastname, None)
				self.addToCombobox('persons_combobox', person.name)


	def personSelect(self, rfid):
		''' Placeholder, opens dialog. '''

		return self.personSelectDialog(rfid)


	def personSelectDialog(self, rfid):
		''' Dialog that selects a person from the list of known persons
		in the database. If there are no persons in the database, opens
		personAddDialog(). '''

		widget_tree = gtk.glade.XML('MoveMe/GUI/GUI.glade', 'personSelection')
		dialog = widget_tree.get_widget('personSelection')
		label = widget_tree.get_widget('rfid_label')

		label.set_text(rfid)

		persons = self.getNonEmptyPersonsList()

		self.buildDialogCombobox(widget_tree, 'persons_combobox')
		self.loadDialogCombobox(widget_tree, 'persons_combobox', persons)

		result = dialog.run()

		#TODO set line: if result == gtk.RESPONSE_CANCEL:
		# deactivate pillow
		if result == -4:
			dialog.destroy()
			return self.personSelectDialog(rfid)

		if result == gtk.RESPONSE_OK:

			combobox = widget_tree.get_widget('persons_combobox')
			name = self.getComboboxText(combobox)

			dialog.destroy()

			if name == None:
				return self.personSelectDialog(rfid)
			else:
				return name


	def getNonEmptyPersonsList(self):
		''' gets the list of persons from the database, if empty calls
		personAddDialog(). '''

		persons = self.gui.context_manager.getTable('persons')

		if len(persons) == 0:
			self.personAddDialog("No person in database yet")

		return self.gui.context_manager.getTable('persons')


	def personsComboboxChangedCB(self, combobox):
		'''
			* Shows parameter values in GUI,
			* sensitizes remove button.
		'''

		name = self.getComboboxText(combobox)
		self.showPersonValues(name)
		widget = self.gui.widget_tree.get_widget("person_remove_button")
		widget.set_sensitive(True)


	def showPersonValues(self, name):
		''' Displays Person parameter values. '''

		result = self.gui.context_manager.memory_db_interface.getRow('persons', 'fullname', name)[0]
		context_person = self.gui.context_manager.getPersonFromContext(name)

		if context_person ==  None:
			rfid = '<not detected yet>'
		elif context_person.rfid == None:
			rfid = '<not detected yet>'
		else:
			rfid = context_person.rfid

		self.gui.widget_tree.get_widget('firstname').set_text(result[1])
		self.gui.widget_tree.get_widget('lastname').set_text(result[2])
		self.gui.widget_tree.get_widget('person_rfid').set_text(rfid)


	def personDeleteCB(self, button):
		''' Removes single person from database. If person is in
		current context, nothing is removed.  '''

		combobox = self.widget_tree.get_widget('persons_combobox')
		name = self.getComboboxText(combobox)

		if not self.gui.context_manager.getPersonFromContext(name) == None:
			print 'Cannot remove %s, currently active' % name
		else:
			self.gui.context_manager.removePerson(name)
			self.removeFromCombobox(name, 'persons_combobox')


	def personRemove(self, person):
		''' Removes a person from GUI, not to be confused with
		personDeleteCB().

		Note: RFID is stored until it is overwritten. '''

		combobox = self.gui.widget_tree.get_widget('persons_combobox')
		self.removeFromTreeView(name, 'context_treeview')



	''' Session Functionality '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	def save(self, button):

		if button.get_active():
			self.gui.context_manager.save_sessions = True
		else:
			self.gui.context_manager.save_sessions = False

	def registerSession(self, session):
		''' Adds session timestamp and information to context tree (on
		detection).  Does _not_ add it to the database section. '''

		model = self.gui.widget_tree.get_widget('context_treeview').get_model()

		parent = model.append(None, (session.timestamp, None))
		attr = model.append(parent, ("Pillow", session.pillow.name))
		attr = model.append(parent, ("Person", session.person.name))

		# Using showPersonValues to update the person RFID nr.

		combobox = self.gui.widget_tree.get_widget('persons_combobox')

		if self.isSelectedInCombobox(session.person.name, combobox):
			self.showPersonValues(session.person.name)


	def sessionsComboboxChangedCB(self, combobox):
		''' Displays parameter values.

		Any session is either:

			* open - in current context, or
			* closed - in database.
		'''

		name = self.getComboboxText(combobox)
		self.showSessionValues(name)


	def showSessionValues(self, name):
		''' Displays Session parameter values. '''


		values = self.gui.context_manager.getSessionValues(name)


		if values == None:

			self.gui.widget_tree.get_widget('label_start').set_text('')
			self.gui.widget_tree.get_widget('label_pillow').set_text('')
			self.gui.widget_tree.get_widget('label_person').set_text('')
			self.gui.widget_tree.get_widget('label_status').set_text('')
		else:
			s = str(values['pillowname']) + '@' + str(values['pillowid'])

			if len(s) > 35:
				s = s[0:31] + '...'

			self.gui.widget_tree.get_widget('label_start').set_text(values['ts'])
			self.gui.widget_tree.get_widget('label_pillow').set_text(s)

			if values['personrfid'] == None:
				s = str(values['personname'])
			else:
				s = str(values['personname']) + '@' + str(values['personrfid'])

			if len(s) > 31:
				s = s[0:27] + '...'

			self.gui.widget_tree.get_widget('label_person').set_text(s)
			self.gui.widget_tree.get_widget('label_status').set_text(values['status'])


	def sessionRemove(self, session):

		name = str(session.timestamp)
		combobox = self.gui.widget_tree.get_widget('sessions_combobox')

		self.removeFromTreeView(name, 'context_treeview')

		if self.isSelectedInCombobox(name, combobox):
			self.showSessionValues(name)
