#!/usr/bin/env python

'''
Implemented at V2_ Lab, for documentation see

	* http://trac.v2.nl/wiki/MoveMeDocumentation
'''

import pygtk, gtk
import numpy


class VisualizationNormalized(gtk.DrawingArea):
	''' This object handles the drawing of the pressure visualization.
	It shows the statistically derived pressure as fill greyscales, while
	the border greyscales represent the absolute pressure values. '''

	def __init__(self, gui, pillow, dimension):

		self.type = 'normalized'
		self.gui = gui
		self.pillow = pillow
		self.width  = 0				# updated in size-allocate handler
		self.height = 0				# idem

		gtk.DrawingArea.__init__(self)
		self.gc = None				# initialized in realize-event handler


		self.connect('size-allocate', self.on_size_allocate)
		self.connect('expose-event',  self.on_expose_event)
		self.connect('realize',   self.on_realize)
		self.connect('destroy',   self.on_destroy)

		self.square_width = dimension
		self.square_height = dimension


		self.rects = self.buildRectangles(self.pillow.matrix_rows, self.pillow.matrix_cols)

		self.data = numpy.zeros((self.pillow.matrix_rows,self.pillow.matrix_cols), int)
		self.cog = [0,0]
		self.motion_vector = None


	def buildRectangles(self, rows, cols):
		rects = []

		for i in range(rows):

			row = []

			for j in range(cols):
				rect = []
				rect.append(j*self.square_width)
				rect.append(i*self.square_height)
				rect.append(self.square_width)
				rect.append(self.square_height)
				row.append(rect)

			rects.append(row)

		return rects


	def on_size_allocate(self, widget, allocation):
		''' Size allocation is assigned on startup. '''

		self.width = allocation.width
		self.height = allocation.height


	def on_realize(self, widget):
		''' Realization called on startup; initializes the graphical context (GC). '''

		self.gc = widget.window.new_gc()
		self.gc.set_line_attributes(1, gtk.gdk.LINE_SOLID, gtk.gdk.CAP_ROUND, gtk.gdk.CAP_ROUND)


	def on_destroy(self, widget):
		''' Some extras to make sure the GUI module knows the window is
		gone and that the visualization button is in the correct state
		after a destroy. '''

		self.gui.removeVisualizationWindow(self.pillow.name, self.type)
		self.gui.resetVisualizationButton(self.pillow.name, self.type)


	def redraw(self, cog, data):
		''' Requests drawingarea redraw. '''

		self.data = data
		self.cog = cog

		# Standard gtk (re)draw request; actual redrawing is handled by
		# on_expose_event.
		self.queue_draw_area(0, 0, self.width, self.height)


	def on_expose_event(self, widget, event):
		''' Standard GTK expose-event callback, use this for efficient
		GUI memory distribution. (Re)draws visualization widget. '''

		# In this for loop the square fills and borders are drawn:
		for x in range(len(self.rects)):
			row = self.rects[x]

			for y in range(len(row)):

				# Fills coloured.
				colormap = self.get_colormap()
				channel_value = self.data[x][y]
				color = colormap.alloc_color(0, channel_value*255, channel_value*255)
				self.gc.set_foreground(color)

				square = row[y]
				widget.window.draw_rectangle(self.gc, True, square[0], square[1], square[2], square[3])

				# Borders black.
				colormap = self.get_colormap()
				color = colormap.alloc_color(0, 0, 0)
				self.gc.set_foreground(color)

				width = square[2] - 1
				height = square[3] - 1
				widget.window.draw_rectangle(self.gc, False, square[0], square[1], width, height)

		# This draws the center of gravity square border:
		color = colormap.alloc_color('red')
		self.gc.set_foreground(color)
		x = int(self.cog[0]*self.square_width)
		y = int(self.cog[1]*self.square_height)
		widget.window.draw_rectangle(self.gc, False, x, y, width, height)
