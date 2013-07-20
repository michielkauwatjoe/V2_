#!/usr/bin/env python

'''
Implemented at V2_ Lab, for documentation see

	* http://trac.v2.nl/wiki/MoveMeDocumentation
'''

import pygtk, gtk
import numpy
import math
import datetime


class VisualizationStandardDeviations(gtk.DrawingArea):
	''' This object handles the drawing of the pressure visualization.
	It shows the statistically derived pressure as fill greyscalePoints, while
	the border greyscalePoints represent the absolute pressure values. '''

	def __init__(self, gui, pillow,  dimension):

		self.type = 'standard_deviations'
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
		self.cog = (0,0)
		self.incomplete_path = []
		self.velocity = 0.
		self.acceleration = 0.
		self.angle = 0.
		self.gesture = None

		self.cog_path = None
		self.upper_hull = None
		self.lower_hull = None

		self.draw_gesture_start = None


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


	def redraw(self, dict):
		''' Requests drawingarea redraw. '''

		try:
			self.data = dict['visualization_standard_deviations']
			self.cog = self.scalePoint(dict['center_of_gravity'])
			self.velocity = dict['velocity']
			self.acceleration = dict['acceleration']
			self.angle = dict['angle']

		except Exception, e:
			print '(In visualization_sds.py) some parameters could not be assigned, parameter is:', e

		if dict.has_key('gesture'):
			self.gesture = dict['gesture']

			self.cog_path = self.scale(self.gesture.cog_path)

			if self.gesture.convex_hull != None:	
				self.upper_hull = self.scale(self.gesture.convex_hull[0])
				self.lower_hull = self.scale(self.gesture.convex_hull[1])

			self.incomplete_path = []
			self.draw_gesture_start = datetime.datetime.now()
		else:
			self.incomplete_path.append(self.cog)

		# Standard gtk (re)draw request; actual redrawing is handled by
		# on_expose_event.

		self.queue_draw_area(0, 0, self.width, self.height)


	def scale(self, points):


		scaled_points = []

		for point in points:
			point = self.scalePoint(point)
			scaled_points.append(point)

		return scaled_points


	def scalePoint(self, point):

		# Points have been multiplied by 10 and rounded / integered to
		# remember one decimal point. Here the points are scalePointd
		# back.

		x = int(float(point[0]*self.square_width / 10 + self.square_width*0.5))
		y = int(float(point[1]*self.square_height / 10 + self.square_width*0.5))

		return (x, y)


	def on_expose_event(self, widget, event):
		''' Standard GTK expose-event callback, use this for efficient
		GUI memory distribution. (Re)draws visualization widget. '''

		now = datetime.datetime.now()

		if not self.draw_gesture_start == None:
			dt = now - self.draw_gesture_start
			dt = dt.seconds
		else:
			dt = None

		try:
			self.drawRects(widget)
			self.drawSpeed(widget)

			# Draw gesture for 5 seconds.
			if not dt == None and dt < 5:
				self.drawHull(widget)
				self.drawMotionVector(widget, 'complete')
				self.drawBoundingBox(widget)
			else:
				self.drawMotionVector(widget, 'incomplete')

			self.drawCog(widget)

		except Exception, e:
			print 'ERROR: sds visualization expose-event'
			print e
			raise


	def drawRects(self, widget):

		for x in range(len(self.rects)):

			row = self.rects[x]

			for y in range(len(row)):

				colormap = self.get_colormap()
				self.gc.set_line_attributes(1, gtk.gdk.LINE_SOLID, gtk.gdk.CAP_ROUND, gtk.gdk.JOIN_ROUND)
				channel_value = int(self.data[x][y])
				square = row[y]

				x0 = square[0]
				y0 = square[1]
				width = square[2]
				height = square[3]


				if channel_value > 0:
					# Fills coloured.

					self.gc.set_foreground(colormap.alloc_color(channel_value*255, channel_value*255, 0))
					widget.window.draw_rectangle(self.gc, True, x0, y0, width, height)

					# Borders.
					width = width - 1
					height = height - 1

					self.gc.set_foreground(colormap.alloc_color(0, 0, 0))
					widget.window.draw_rectangle(self.gc, False, x0, y0, width, height)
				else:
					self.gc.set_foreground(colormap.alloc_color('black'))
					widget.window.draw_rectangle(self.gc, True, x0, y0, width, height)

					self.gc.set_foreground(colormap.alloc_color('gray'))

					x1 = x0
					y1 = y0
					x2 = x0 + width
					y2 = y0 + height

					widget.window.draw_line(self.gc, x1, y1, x2, y2)

					x1 = x0 + width
					y1 = y0
					x2 = x0
					y2 = y0 + height

					widget.window.draw_line(self.gc, x1, y1, x2, y2)


	def drawCog(self, widget):
		''' This draws the center of gravity square. '''

		colormap = self.get_colormap()
		self.gc.set_foreground(colormap.alloc_color('red'))

		x = int(self.cog[0] - 0.5 * self.square_width)
		y = int(self.cog[1] - 0.5 * self.square_height)

		self.gc.set_line_attributes(1, gtk.gdk.LINE_SOLID, gtk.gdk.CAP_ROUND, gtk.gdk.JOIN_ROUND)
		widget.window.draw_rectangle(self.gc, False, x, y, self.square_width, self.square_height)


	def drawMotionVector(self, widget, mode):
		''' This draws the center of gravity square. '''

		colormap = self.get_colormap()

		if mode == 'complete':
			self.gc.set_foreground(colormap.alloc_color('white'))
			self.gc.set_line_attributes(1, gtk.gdk.LINE_ON_OFF_DASH, gtk.gdk.CAP_ROUND, gtk.gdk.JOIN_ROUND)
			if not self.cog_path == None:
				widget.window.draw_lines(self.gc, self.cog_path)

			else:
				print '!!!Warning: no complete center of gravity path could be found'

		elif mode == 'incomplete':
			self.gc.set_foreground(colormap.alloc_color('gray'))
			self.gc.set_line_attributes(1, gtk.gdk.LINE_ON_OFF_DASH, gtk.gdk.CAP_ROUND, gtk.gdk.JOIN_ROUND)
			if len(self.incomplete_path) > 0:
				widget.window.draw_lines(self.gc, self.incomplete_path)


	def drawHull(self, widget):
		''' Draws convex hull of the cog path. '''

		if not self.lower_hull == None and not self.upper_hull == None:

			colormap = self.get_colormap()

			self.gc.set_line_attributes(1, gtk.gdk.LINE_SOLID, gtk.gdk.CAP_ROUND, gtk.gdk.JOIN_ROUND)
			self.gc.set_foreground(colormap.alloc_color(0, 100*255 ,200*255))
			self.gc.set_fill(gtk.gdk.SOLID)

			widget.window.draw_polygon(self.gc, True, self.upper_hull)
			widget.window.draw_polygon(self.gc, True, self.lower_hull)


	def drawBoundingBox(self, widget):
		''' Draws bounding box for convex hull of the cog path. '''

		if not self.gesture.bounding_box == None:

			colormap = self.get_colormap()

			self.gc.set_line_attributes(1, gtk.gdk.LINE_ON_OFF_DASH, gtk.gdk.CAP_ROUND, gtk.gdk.JOIN_ROUND)
			self.gc.set_foreground(colormap.alloc_color('red'))

			point1 = self.scalePoint(self.gesture.bounding_box[0])
			point2 = self.scalePoint(self.gesture.bounding_box[1])
			width = point2[0] - point1[0]
			height = point2[1] - point1[1]

			widget.window.draw_rectangle(self.gc, False, point1[0], point1[1], width, height)


	def drawSpeed(self, widget):

		colormap = self.get_colormap()
		self.gc.set_foreground(colormap.alloc_color('blue'))
		self.gc.set_line_attributes(3, gtk.gdk.LINE_SOLID, gtk.gdk.CAP_ROUND, gtk.gdk.JOIN_ROUND)

		width = int(self.square_width - 0.2*self.square_width)
		height = int(self.square_height - 0.2*self.square_height)

		radians = math.radians(self.angle)

		hypotenuse = int(abs(self.velocity)) * width

		x0 = int(self.width - self.square_width*0.5)
		y0 = int(self.height - self.square_height*0.5)


		dy = math.sin(radians)*hypotenuse
		dx = math.cos(radians)*hypotenuse

		x1 = int(x0 + dx)
		y1 = int(y0 + dy)

		widget.window.draw_line(self.gc, x0, y0, x1, y1)

		offset = 5 # pixels

		hypotenuse = int(abs(self.acceleration)) * width

		dy = math.sin(radians)*hypotenuse
		dx = math.cos(radians)*hypotenuse

		x0 = int(self.width - self.square_width*1.5)

		x1 = int(x0 + dx)
		y1 = int(y0 + dy)

		self.gc.set_foreground(colormap.alloc_color('green'))
		widget.window.draw_line(self.gc, x0, y0, x1, y1)
