#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  events.py
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2019-2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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

import wx
from domdf_wxpython_tools import SimpleEvent

EVT_NEW_PROJECT_DIALOG_CLOSE = SimpleEvent()

EVT_PROJECT_CHANGE = SimpleEvent()
EVT_REMOVE_ALIGNMENT = SimpleEvent()
EVT_REMOVE_IDENT = SimpleEvent()

EVT_PROJ_NOTEBOOK_PAGE_CHANGED = SimpleEvent()
EVT_EXPR_NOTEBOOK_PAGE_CHANGED = SimpleEvent()

EVT_ALIGNMENT_PERFORMED = SimpleEvent()
EVT_REMOVE_PROJECT = SimpleEvent()

# Events for switching notebook tabs when tree selection changes
EVT_SWITCH_PROJ_REQ = SimpleEvent()
EVT_SWITCH_PROJ_CONTENT_REQ = SimpleEvent()
EVT_SWITCH_EXPR_CONTENT_REQ = SimpleEvent()


# Events for enabling and disabling controls
EVT_TOGGLE_VIEW_TOOLS = SimpleEvent()
EVT_TOGGLE_EXPR_TOOLS = SimpleEvent()

# Events for Experiment
myEVT_EXPERIMENT_LOG = wx.NewEventType()
EVT_EXPERIMENT_LOG = wx.PyEventBinder(myEVT_EXPERIMENT_LOG, 1)

#
# EVT_ALIGNMENT_PERFORMED
#
#
# EVT_ALIGNMENT_ID = wx.NewIdRef()
#
#
# class AlignmentEvent(wx.PyCommandEvent):
# 	"""Simple event to carry arbitrary data."""
# 	def __init__(self, data):
# 		"""Init Result Event."""
# 		wx.PyCommandEvent.__init__(self)
# 		self.SetEventType(EVT_ALIGNMENT_ID)
# 		self.data = data
#
# 	def GetValue(self):
# 		"""Returns the value from the event.
#
# 		:return: the value of this event
#
# 		"""
# 		return self.data
#
#
# EVT_ALIGNMENT = wx.PyEventBinder(AlignmentEvent, 1)
#
# # To trigger:
# # wx.PostEvent(receiver, AlignmentEvent(data))
