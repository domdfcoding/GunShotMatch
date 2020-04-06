#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  ChartDesign.py
#
#  This file is part of GunShotMatch
#
#  Copyright © 2019 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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


# 3rd party
import wx
from domdf_wxpython_tools import ColourPickerPanel, StylePickerPanel

from GuiV2.GSMatch2_Core.utils import create_button


class StylePicker(wx.Panel):
	def __init__(
			self, parent, title="Choose Styles", label="Choose Styles: ",
			selection_choices=None, *args, **kwds,
			):
		"""
		:param parent: The parent window.
		:type parent: wx.Window
		:param title:
		:type title: str
		:param label:
		:type label: str
		:param selection_choices:
		:type selection_choices:
		:param id: An identifier for the panel. wx.ID_ANY is taken to mean a default.
		:type id: wx.WindowID, optional
		:param pos: The panel position. The value wx.DefaultPosition indicates a default position,
		chosen by either the windowing system or wxWidgets, depending on platform.
		:type pos: wx.Point, optional
		:param size: The panel size. The value wx.DefaultSize indicates a default size, chosen by
		either the windowing system or wxWidgets, depending on platform.
		:type size: wx.Size, optional
		:param style: The window style. See wx.Panel.
		:type style: int, optional
		:param name: Window name.
		:type name: str, optional
		"""
		
		self.title = title
		
		kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
		wx.Panel.__init__(self, parent, *args, **kwds)
		self.StylePickerPanel = StylePickerPanel(self, label, selection_choices)
		self.button_panel = wx.Panel(self, wx.ID_ANY)
		self.reset_btn = create_button(self.button_panel, label="Reset", handler=self.reset)
		self.apply_btn = create_button(self.button_panel, label="Apply", handler=self.apply)
		
		self._do_layout()
		
		# TODO: default value for style_list

	def _do_layout(self):
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
		
		kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
		wx.Panel.__init__(self, parent, *args, **kwds)
		self.StylePickerPanel = ColourPickerPanel(self, label, selection_choices)
		self.button_panel = wx.Panel(self, wx.ID_ANY)
		self.reset_btn = create_button(self.button_panel, label="Reset", handler=self.reset)
		self.apply_btn = create_button(self.button_panel, label="Apply", handler=self.apply)
		
		self._do_layout()
		
		# TODO: default value for colour_list
	
	def apply(self, event):
		self.colour_list = [
				self.StylePickerPanel.selection_list_box.GetString(item) for item in range(
						self.StylePickerPanel.selection_list_box.GetCount()
						)
				]
		event.Skip()
	
	def _do_layout(self):
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
