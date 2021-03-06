#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  CalibreButtonPanel.py
#
#  This file is part of GunShotMatch
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
# generated by wxGlade 0.9.3 on Fri Dec  6 20:32:07 2019
#


# 3rd party
import wx

# this package
from GuiV2.GSMatch2_Core.utils import create_button


ID_NEW_CALIBRE = wx.NewIdRef()


class CalibreButtonPanel(wx.Panel):
	def __init__(
			self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
			style=wx.TAB_TRAVERSAL, name="CalibreButtonPanel"
			):
		"""
		:param parent: The parent window.
		:type parent: wx.Window
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
		
		wx.Panel.__init__(
				self, parent, id=id, pos=pos, size=size,
				name=name, style=style | wx.TAB_TRAVERSAL)
		
		grid_sizer = wx.GridSizer(2, 1, 10, 0)
		
		sizer_flags = wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM
		
		self.new_calibre_btn = create_button(
				self, ID_NEW_CALIBRE, "New Calibre", sizer=grid_sizer, sizer_flags=sizer_flags)
		self.new_calibre_btn.Enable(False)

		self.select_cancel_panel = wx.Panel(self, wx.ID_ANY)
		self.select_cancel_grid = wx.GridSizer(1, 2, 0, 5)

		self.cancel_btn = create_button(
				self.select_cancel_panel, wx.ID_CANCEL, sizer=self.select_cancel_grid, sizer_flags=sizer_flags)
		self.select_btn = create_button(
				self.select_cancel_panel, wx.ID_ADD, "Select", sizer=self.select_cancel_grid, sizer_flags=sizer_flags)
		
		self.select_cancel_panel.SetSizer(self.select_cancel_grid)
		
		grid_sizer.Add(self.select_cancel_panel, 1, sizer_flags, 0)
		
		self.SetSizer(grid_sizer)
		grid_sizer.Fit(self)
		self.Layout()
		

class NewCalibreButtonPanel(wx.Panel):
	def __init__(
			self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
			size=wx.DefaultSize, style=wx.TAB_TRAVERSAL,
			name="NewCalibreButtonPanel"
			):
		"""
		:param parent: The parent window.
		:type parent: wx.Window
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
		
		wx.Panel.__init__(
				self, parent, id=id, pos=pos, size=size,
				name=name, style=style | wx.TAB_TRAVERSAL)

		grid_sizer = wx.BoxSizer(wx.VERTICAL)
		
		self.new_calibre_btn = create_button(
				self, ID_NEW_CALIBRE, "New Calibre", sizer=grid_sizer, sizer_flags=wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM)
		self.new_calibre_btn.Enable(False)

		self.SetSizer(grid_sizer)
		grid_sizer.Fit(self)
		self.Layout()
