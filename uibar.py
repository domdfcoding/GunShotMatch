#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  uibar.py
#  
#  Copyright 2019 dom13 <dom13@DOM-XPS>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

import time

class ProgressBar():
	def __init__(self, start_message, max_value, main_window, end_message = "Analysis complete"):
		self.step = 1000 / max_value
		self.main_window = main_window

		if type(start_message) == list:
			self.start_message = [x for x in start_message if not isinstance(x, int)]
		else:
			self.start_message = start_message
			
		self.end_message = end_message
		self.main_window.progbar.SetValue(0)
		self.main_window.rest_message = self.start_message
		self.last_val = 0
		
	def update(self, value):
		for i in range(self.last_val, int(self.step*value)):
			self.main_window.progbar.SetValue(i)
		self.last_val = int(self.step*value)

	def start(self):
		return self

	def finish(self):
		for i in range(self.last_val, 1000):
			self.main_window.progbar.SetValue(i)
		self.main_window.rest_message = "Ready"
		self.main_window.status(self.end_message)
		time.sleep(5)
		self.main_window.progbar.SetValue(0)

class widgets():
	def __init__(self):
		return 0
	def AnimatedMarker():
		return 0

def Timer():
	return 0

UnknownLength = 1000
