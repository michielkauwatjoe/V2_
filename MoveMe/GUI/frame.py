#!/usr/bin/env python

'''
Implemented at V2_ Lab, for documentation see

 http://trac.v2.nl/wiki/MoveMeDocumentation
'''

import pygtk, gtk, gtk.glade, gobject


class Frame(object):
	'''
	Abstract parent, contains general functions for
	pyGTK treeviews and comboboxes
	'''

	def __init__(self, widget_tree):
		''' Needs the general GUI widget tree. '''

		self.widget_tree = widget_tree


	''' Treeview Functionality '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	def removeFromTreeView(self, item_name, tree_name):
		''' Removes an item from a GTK treeview object. '''

		try:
			tree_store = self.widget_tree.get_widget(tree_name).get_model()
			for x in range(len(tree_store)):
				iter = tree_store.get_iter(x)
				if tree_store.get_value(iter, 0) == item_name:
					tree_store.remove(iter)
					return
		except Exception, e:
			s = '\'%s\' not removed from GUI.' % item_name
			raise Exception(e)


	def unloadTreeView(self, name):
		''' Gets treeview object that matches name and clears it. '''

		treeview = self.widget_tree.get_widget(name)
		tree_store = treeview.get_model()
		tree_store.clear()


	''' Combobox Functionality '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

	def buildDialogCombobox(self, widget_tree, name):
		'''
		Initializes combobox by setting the model to liststore and
		packing it with a cell renderer.
		'''

		combobox = widget_tree.get_widget(name)
		combobox.set_model(gtk.ListStore(str))
		cell = gtk.CellRendererText()
		combobox.pack_start(cell, True)
		combobox.add_attribute(cell, 'text', 0)


	def loadCombobox(self, name, list):
		''' Adds a list of names to a combobox. '''

		combobox = self.widget_tree.get_widget(name)
		liststore = combobox.get_model()
		for row in list:
			liststore.append([row[0]])


	def loadDialogCombobox(self, widget_tree, name, list):
		'''
		Adds a list of names to a combobox.
		This one is for dialogs (their widget tree
		is different from the main window).
		'''

		combobox = widget_tree.get_widget(name)
		liststore = combobox.get_model()
		for row in list:
			liststore.append([row[0]])


	def unloadCombobox(self, name):
		''' Clears contents of a combobox. '''

		combobox = self.widget_tree.get_widget(name)
		liststore = combobox.get_model()
		liststore.clear()


	def addToCombobox(self, combo_name, item_name):
		''' Adds a single item to a combobox. '''

		try:
			combobox = self.widget_tree.get_widget(combo_name)
			liststore = combobox.get_model()
			liststore.append([item_name])
		except Exception, e:
			print '%s not added to %s.' % (item_name, combo_name) 
			raise Exception(e)


	def removeFromCombobox(self, item_name, combo_name):
		''' Removes a single item from a combobox. '''

		try:
			list_store = self.widget_tree.get_widget(combo_name).get_model()
			for x in range(len(list_store)):
				iter = list_store.get_iter(x)
				if list_store.get_value(iter, 0) == item_name:
					list_store.remove(iter)
					return
		except Exception, e:
			s = '\'%s\' not removed from GUI.' % item_name
			raise Exception(e)


	def getComboboxText(self, combobox):
		''' Returns text of active combobox item if any. '''

		model = combobox.get_model()
		active = combobox.get_active()
		if active < 0: return None
		return model[active][0]


	def isSelectedInCombobox(self, name, combobox):
		''' Returns true if the itemname is identical to the name
		that is currently in the combobox. '''

		selected_name = self.getComboboxText(combobox)

		if selected_name == name:
			return True
		else:
			return False


	def setButtonSensitive(self, button, boolean):
		''' Basic function to set button sensitive / insensitive:

			* if state is insensitive (4) then set sensitive,
			* if state is not sensitive (not 4) then set insensitive.
		'''

		if boolean == True:
			if button.state == 4: button.set_sensitive(True)
		elif boolean == False:
			if not button.state == 4: button.set_sensitive(False)
