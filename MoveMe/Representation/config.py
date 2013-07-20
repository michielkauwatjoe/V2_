#!/usr/bin/env python

'''
Implemented at V2_ Lab, for documentation see

 http://trac.v2.nl/wiki/MoveMeDocumentation
'''


class DefaultConfig(object):

	def __init__(self):
		self.dict = {
			'sd_calibration': [150., 0., 1000., 'pressure', 'slider'],
			'buffer_size': [2, 1, 10,'pressure', 'slider'],
			'lowpass_previous': [5., 0., 100.,'pressure', 'slider'],
			'dt_cog': [0.3, 0., 1., 'pressure', 'slider'],
			'slow_fast': [2., 0., 10., 'pressure', 'slider'],
			'soft_hard': [300., 0., 500., 'pressure', 'slider'],
			'short_long': [1., 0., 10.0 ,'pressure', 'slider'], # seconds
			'small_medium': [25., 0., 64.0 ,'pressure', 'slider'],
			'medium_large': [45., 0., 64.0 ,'pressure', 'slider'],
			'wandering_angle': [60, 0., 180 ,'pressure', 'slider'],
			'hard_move_length': [3., 0., 10. ,'pressure', 'slider'],
			'soft_move_length': [1., 0., 10. ,'pressure', 'slider'],
			'move_count': [3, 0., 10,'pressure', 'slider'],
			'stationary_travelling': [0.5, 0., 2.0 ,'pressure', 'slider'],
			'active_taxels': [10, 0., 64.,'pressure', 'slider'],
			'max_event_duration': [3., 0., 10., 'pressure', 'slider'],
			'max_lock_duration': [1.5, 0., 10.,'pressure', 'slider'],
			'sd_sustain': [66., 0., 100.0,'pressure', 'slider'],
		}
