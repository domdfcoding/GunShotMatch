#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  ChartDesign.py
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2019  Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Based on "style_picker.py" from "domdf_wxpython_tools" by the above authour
#  github.com/domdfcoding/domdf_wxpython_tools
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
import sys

# 3rd party
import wx

# this package
from domdf_wxpython_tools import StylePickerPanel
from domdf_wxpython_tools import ColourPickerPanel


class StylePicker(wx.Panel):
	def __init__(
			self, parent, title="Choose Styles", label="Choose Styles: ",
			selection_choices=None, *args, **kwds
			):
		self.title = title
		
		args = (parent,) + args

		kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
		wx.Panel.__init__(self, *args, **kwds)
		self.StylePickerPanel = StylePickerPanel(self, label, selection_choices)
		self.button_panel = wx.Panel(self, wx.ID_ANY)
		self.reset_btn = wx.Button(self.button_panel, wx.ID_ANY, "Reset")
		self.apply_btn = wx.Button(self.button_panel, wx.ID_ANY, "Apply")
		
		self.__set_properties()
		self.__do_layout()
		
		self.Bind(wx.EVT_BUTTON, self.reset, self.reset_btn)
		self.Bind(wx.EVT_BUTTON, self.apply, self.apply_btn)
		
		# TODO: default value for style_list
	
	def __set_properties(self):
		pass

	def __do_layout(self):
		parent_sizer = wx.FlexGridSizer(2, 1, 0, 0)
		button_grid = wx.GridSizer(1, 2, 0, 5)
		parent_sizer.Add(self.StylePickerPanel, 1, wx.EXPAND, 0)
		button_grid.Add(self.reset_btn, 0, wx.ALIGN_CENTER, 0)
		button_grid.Add(self.apply_btn, 0, wx.ALIGN_CENTER, 0)
		self.button_panel.SetSizer(button_grid)
		parent_sizer.Add(self.button_panel, 1, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL, 5)
		self.SetSizer(parent_sizer)
		parent_sizer.Fit(self)
		self.Layout()
	
	def reset(self, event):
		# TODO
		event.Skip()
	
	def apply(self, event):
		self.style_list = [
				self.StylePickerPanel.markers[
					self.StylePickerPanel.selection_list_box.GetString(item)
				] for item in range(self.StylePickerPanel.selection_list_box.GetCount())
				]
		event.Skip()


class ColourPicker(StylePicker):
	def __init__(
			self, parent, title="Choose Colours", label="Choose Colours: ",
			picker_choices=None, selection_choices=None, *args, **kwds
			):
		self.title = title
		self.picker_choices = picker_choices
		
		args = (parent,) + args
		
		kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
		wx.Panel.__init__(self, *args, **kwds)
		self.StylePickerPanel = ColourPickerPanel(self, label, selection_choices)
		self.button_panel = wx.Panel(self, wx.ID_ANY)
		self.reset_btn = wx.Button(self.button_panel, wx.ID_ANY, "Reset")
		self.apply_btn = wx.Button(self.button_panel, wx.ID_ANY, "Apply")
		
		self.__set_properties()
		self.__do_layout()
		
		self.Bind(wx.EVT_BUTTON, self.reset, self.reset_btn)
		self.Bind(wx.EVT_BUTTON, self.apply, self.apply_btn)
	
		# TODO: default value for colour_list
	
	def apply(self, event):
		self.colour_list = [
				self.StylePickerPanel.selection_list_box.GetString(item) for item in range(
						self.StylePickerPanel.selection_list_box.GetCount()
						)
				]
		event.Skip()
	
	def __set_properties(self):
		pass
	
	def __do_layout(self):
		parent_sizer = wx.FlexGridSizer(2, 1, 0, 0)
		button_grid = wx.GridSizer(1, 2, 0, 5)
		parent_sizer.Add(self.StylePickerPanel, 1, wx.EXPAND, 0)
		button_grid.Add(self.reset_btn, 0, wx.ALIGN_CENTER, 0)
		button_grid.Add(self.apply_btn, 0, wx.ALIGN_CENTER, 0)
		self.button_panel.SetSizer(button_grid)
		parent_sizer.Add(self.button_panel, 1, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL, 5)
		self.SetSizer(parent_sizer)
		parent_sizer.Fit(self)
		self.Layout()

