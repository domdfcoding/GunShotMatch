#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  My_Axes.py
#
#  Copyright 2013 simonb
#  From https://stackoverflow.com/a/16709952/3092681
#  Licensed under CC-BY-SA
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
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

import matplotlib
from matplotlib import axes

class My_Axes(matplotlib.axes.Axes):
	"""Constrain pan to x-axis"""
	
	name = "My_Axes"
	def drag_pan(self, button, key, x, y):
		matplotlib.axes.Axes.drag_pan(self, button, 'x', x, y) # pretend key=='x'


