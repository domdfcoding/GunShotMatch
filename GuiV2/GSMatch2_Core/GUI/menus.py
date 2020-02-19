#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  menus.py
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2019  Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
from GuiV2.GSMatch2_Core.IDs import *


class SpectrumViewerMenu(wx.MenuBar):
	"""
	MenuBar for Spectrum Viewer
	"""
	def __init__(self, parent, style=0):
		self.parent = parent
		self.id = id
		wx.MenuBar.__init__(self, style)
		self.__populate_menubar()
	
	def __populate_menubar(self):
		file_menu = wx.Menu()
		file_menu.Append(ID_Spec_Viewer_Save, "&Save As Image\tCtrl+S", "")
		self.Bind(wx.EVT_MENU, self.parent.on_save, id=ID_Spec_Viewer_Save)
		file_menu.Append(wx.ID_EXIT, "&Quit", "")
		self.Bind(wx.EVT_MENU, self.parent.OnExit, id=wx.ID_EXIT)
		self.Append(file_menu, "&File")
		
		edit_menu = wx.Menu()
		edit_menu.Append(ID_Spec_Viewer_Copy_Image, "&Copy Image\tCtrl+C", "")
		self.Bind(wx.EVT_MENU, self.parent.on_copy, id=ID_Spec_Viewer_Copy_Image)
		edit_menu.Append(ID_Spec_Viewer_Copy_Data, "Copy &Data\tCtrl+Shift+C", "")
		self.Bind(wx.EVT_MENU, self.parent.on_copy_data, id=ID_Spec_Viewer_Copy_Data)
		self.Append(edit_menu, "&Edit")
		
		view_menu = wx.Menu()
		view_menu.Append(ID_Spec_Viewer_View_Reset, "&Reset View\tCtrl+Shift+R", "")
		self.Bind(wx.EVT_MENU, self.parent.reset_view, id=ID_Spec_Viewer_View_Reset)
		view_menu.Append(ID_Spec_Viewer_View_Previous, "&Previous View", "")
		self.Bind(wx.EVT_MENU, self.parent.previous_view, id=ID_Spec_Viewer_View_Previous)
		view_menu.Append(ID_Spec_Viewer_View_Default, "&Select", "")
		self.Bind(wx.EVT_MENU, self.parent.tool_select, id=ID_Spec_Viewer_View_Default)
		view_menu.Append(ID_Spec_Viewer_View_Zoom, "&Zoom\tCtrl+Shift+Z", "")
		self.Bind(wx.EVT_MENU, self.parent.tool_zoom, id=ID_Spec_Viewer_View_Zoom)
		view_menu.Append(ID_Spec_Viewer_View_Pan, "&Pan\tCtrl+Shift+P", "")
		self.Bind(wx.EVT_MENU, self.parent.tool_pan, id=ID_Spec_Viewer_View_Pan)
		self.Append(view_menu, "&View")
		
		menu_spectrum = wx.Menu()
		menu_spectrum.Append(ID_Spec_Viewer_by_num, "View Spectrum by Scan &Number", "")
		self.Bind(wx.EVT_MENU, self.parent.spectrum_by_number, id=ID_Spec_Viewer_by_num)
		menu_spectrum.Append(ID_Spec_Viewer_by_rt, "View Spectrum by Retention &Time", "")
		self.Bind(wx.EVT_MENU, self.parent.spectrum_by_rt, id=ID_Spec_Viewer_by_rt)
		self.Append(menu_spectrum, "&Spectrum")
		
		menu_experiment = wx.Menu()
		menu_experiment.Append(ID_Spec_Viewer_Previous_Experiment, "&Previous Experiment\tCtrl+<", "")
		self.Bind(wx.EVT_MENU, self.parent.previous_experiment, id=ID_Spec_Viewer_Previous_Experiment)
		menu_experiment.Append(ID_Spec_Viewer_Next_Experiment, "&Next Experiment\tCtrl+>", "")
		self.Bind(wx.EVT_MENU, self.parent.next_experiment, id=ID_Spec_Viewer_Next_Experiment)
		self.Append(menu_experiment, "E&xperiment")
