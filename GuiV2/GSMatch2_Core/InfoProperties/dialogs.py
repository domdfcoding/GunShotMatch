#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  dialogs.py
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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

# 3rd party
import wx
from domdf_wxpython_tools import EditableNumericalListBox


class MeasurementDialog(wx.Dialog):
	def __init__(
			self, parent, id=wx.ID_ANY, title='', values=None, decimal_places=-1,
			pos=wx.DefaultPosition, size=(180, -1), style=wx.DEFAULT_DIALOG_STYLE,
			name=wx.DialogNameStr):
		"""

		:param parent: Can be None, a frame or another dialog box.
		:type parent: wx.Window
		:param id: An identifier for the dialog. A value of -1 is taken to mean a default.
		:type id: wx.WindowID
		:param title: The title of the dialog.
		:type title: str
		:param values:
		:type values:
		:param decimal_places:
		:type decimal_places:
		:param pos: The dialog position. The value DefaultPosition indicates a
		default position, chosen by either the windowing system or wxWidgets,
		depending on platform.
		:type pos: wx.Point
		:param size: The dialog size. The value DefaultSize indicates a default
		size, chosen by either the windowing system or wxWidgets, depending on
		platform.
		:type size: wx.Size
		:param style: The window style.
		:type style: int
		:param name: Used to associate a name with the window, allowing the
		application user to set Motif resource values for individual dialog boxes.
		:type name: str
		"""
		
		wx.Dialog.__init__(self, parent, id, title, pos, size, style, name)
		
		self.SetMaxSize(size)
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.listbox = EditableNumericalListBox(self, decimal_places=decimal_places)
		
		self.btns = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
		
		sizer.Add(self.listbox, 0)
		sizer.Add(self.btns, 0, wx.EXPAND)
		self.SetSizer(sizer)
		self.Fit()
		
		if values is not None:
			self.listbox.SetValues(values)
		
		self.listbox.SetFocus()
	
	def GetValues(self):
		return self.listbox.GetValues()

