#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  method_picker_mixin.py
#
#  This file is part of GunShotMatch
#
#  Copyright © 2019-2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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

# stdlib
import pathlib

# 3rd party
import wx

# this package
from GuiV2.GSMatch2_Core import utils
from GuiV2.GSMatch2_Core.Config import internal_config


class MethodPickerMixin:
	"""
	Mixin providing methods for selecting method files.
	
	The Class must have an attribute ``meth_picker`` that refers to a
	:class:`domdf_wxpython_tools.picker.file_picker` object
	"""
	def __init__(self):
		self.Bind(wx.EVT_BUTTON, self.on_new_method, self.new_meth_button)
		self.Bind(wx.EVT_BUTTON, self.on_edit_method, self.edit_meth_button)
	
	def on_method_change(self, _):
		internal_config.last_method = self.meth_picker.GetValue()
	
	def on_new_method(self, event):  # wxGlade: NewExperimentDialog.<event_handler>
		utils.method_editor()
	
	def on_edit_method(self, event):  # wxGlade: NewExperimentDialog.<event_handler>

		def set_warning(msg):
			wx.MessageBox(msg, "Error", style=wx.ICON_ERROR)
			
			self.meth_picker.SetBackgroundColour("pink")
			self.meth_picker.SetFocus()
			self.meth_picker.Refresh()
		
		filename = self.meth_picker.GetValue()
		
		if len(filename) == 0:
			set_warning("Please choose a Method for the Experiment.")
			return
		elif not pathlib.Path(filename).absolute().is_file():
			set_warning("The selected Method file does not exist.")
			return
			
		else:
			self.meth_picker.SetBackgroundColour((242, 241, 240, 255))
			self.meth_picker.Refresh()
		
		utils.method_editor(self.meth_picker.GetValue())

