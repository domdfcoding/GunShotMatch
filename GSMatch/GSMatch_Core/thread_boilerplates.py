#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  thread_boilerplates.py
"""Boilerplate code for creating threads and events"""
#
#  This file is part of GunShotMatch
#
#  Copyright © 2019 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  GunShotMatch is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  GunShotMatch is distributed in the hope that it will be useful,
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

import wx


class LogEventBoilerplate(wx.PyCommandEvent):
	"""Event to signal that a the conversion is complete"""
	
	def __init__(self, etype, eid, log_text):
		"""Creates the event object"""
		wx.PyCommandEvent.__init__(self, etype, eid)
		self.log_text = log_text
	
	def GetValue(self):
		"""Returns the value from the event.
		@return: the value of this event

		"""
		return self.log_text
