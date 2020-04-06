#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  launcher_tab.py
"""Main tab, for choosing different tasks to perform"""
#
#  This file is part of GunShotMatch
#
#  Copyright © 2017-2019 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import wx.richtext

from domdf_wxpython_tools import coming_soon
from domdf_wxpython_tools import file_dialog

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class launcher_tab(wx.Panel):
	def __init__(self, parent, *args, **kwds):
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
		
		self._parent = parent
		# begin wxGlade: launcher_tab.__init__
		kwds["style"] = kwds.get("style", 0) | wx.TAB_TRAVERSAL
		wx.Panel.__init__(self, *args, **kwds)
		self.launcher_parent_panel = wx.Panel(self, wx.ID_ANY, style=wx.BORDER_SUNKEN)
		self.import_raw_button = wx.Button(self.launcher_parent_panel, wx.ID_ANY, "", style=wx.BU_AUTODRAW)
		self.import_raw_button.Bind(wx.EVT_SET_FOCUS, self.refresh_launcher)
		self.import_info_button = wx.BitmapButton(self.launcher_parent_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/info_48.png", wx.BITMAP_TYPE_ANY))
		self.new_project_button = wx.BitmapButton(self.launcher_parent_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/new_project_110.png", wx.BITMAP_TYPE_ANY), style=wx.BU_AUTODRAW | wx.BU_EXACTFIT)
		self.new_info_button = wx.BitmapButton(self.launcher_parent_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/info_48.png", wx.BITMAP_TYPE_ANY))
		self.open_project_button = wx.BitmapButton(self.launcher_parent_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/open_project_110.png", wx.BITMAP_TYPE_ANY))
		self.open_info_button = wx.BitmapButton(self.launcher_parent_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/info_48.png", wx.BITMAP_TYPE_ANY))
		self.comparison_button = wx.BitmapButton(self.launcher_parent_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/comparison_green_110.png", wx.BITMAP_TYPE_ANY))
		self.comparison_info_button = wx.BitmapButton(self.launcher_parent_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/info_48.png", wx.BITMAP_TYPE_ANY))
		self.launcher_right_panel = wx.Panel(self, wx.ID_ANY, style=wx.BORDER_SUNKEN)
		self.messages_panel = wx.Panel(self.launcher_right_panel, wx.ID_ANY)
		self.messages = wx.richtext.RichTextCtrl(self.messages_panel, wx.ID_ANY, style=wx.richtext.RE_MULTILINE | wx.richtext.RE_READONLY)

		self.__set_properties()
		self.__do_layout()

		self.Bind(wx.EVT_BUTTON, self.on_import, self.import_raw_button)
		self.Bind(wx.EVT_BUTTON, self.do_import_info, self.import_info_button)
		self.Bind(wx.EVT_BUTTON, self.on_new_project, self.new_project_button)
		self.Bind(wx.EVT_BUTTON, self.do_new_info, self.new_info_button)
		self.Bind(wx.EVT_BUTTON, self.on_open_project, self.open_project_button)
		self.Bind(wx.EVT_BUTTON, self.do_open_info, self.open_info_button)
		self.Bind(wx.EVT_BUTTON, self.on_open_comparison, self.comparison_button)
		self.Bind(wx.EVT_BUTTON, self.do_comparison_info, self.comparison_info_button)
		# end wxGlade

	def __set_properties(self):
		# begin wxGlade: launcher_tab.__set_properties
		self.SetBackgroundColour(wx.Colour(240, 240, 240))
		self.import_raw_button.SetMinSize((128, 128))
		self.import_raw_button.SetToolTip("Import .RAW Files")
		self.import_raw_button.SetBitmap(wx.Bitmap("./lib/icons/import_110.png", wx.BITMAP_TYPE_ANY))
		self.import_info_button.SetToolTip("Show help for \"Import\"")
		self.import_info_button.SetSize(self.import_info_button.GetBestSize())
		self.new_project_button.SetMinSize((128, 128))
		self.new_project_button.SetToolTip("Create New Project")
		self.new_info_button.SetToolTip("Show help for \"New Project\"")
		self.new_info_button.SetSize(self.new_info_button.GetBestSize())
		self.open_project_button.SetMinSize((128, 128))
		self.open_project_button.SetToolTip("Open Project")
		self.open_info_button.SetToolTip("Show help for \"Open Project\"")
		self.open_info_button.SetSize(self.open_info_button.GetBestSize())
		self.comparison_button.SetMinSize((128, 128))
		self.comparison_button.SetToolTip("Open Project")
		self.comparison_info_button.SetToolTip("Show help for \"Comparison\"")
		self.comparison_info_button.SetSize(self.comparison_info_button.GetBestSize())
		self.launcher_parent_panel.SetBackgroundColour(wx.Colour(240, 240, 240))
		# end wxGlade

	def __do_layout(self):
		# begin wxGlade: launcher_tab.__do_layout
		launcher_parent_sizer = wx.BoxSizer(wx.HORIZONTAL)
		launcher_right_sizer = wx.BoxSizer(wx.VERTICAL)
		messages_sizer = wx.BoxSizer(wx.VERTICAL)
		launcher_sizer = wx.BoxSizer(wx.HORIZONTAL)
		launcher_grid = wx.GridSizer(4, 3, 20, 20)
		launcher_grid.Add(self.import_raw_button, 0, wx.ALIGN_CENTER, 64)
		import_description_label = wx.StaticText(self.launcher_parent_panel, wx.ID_ANY, "Import PerkinElmer/Waters .RAW files and convert to JCAMP-DX format.", style=wx.ALIGN_LEFT)
		import_description_label.Wrap(256)
		launcher_grid.Add(import_description_label, 0, wx.ALIGN_CENTER_VERTICAL, 64)
		launcher_grid.Add(self.import_info_button, 0, wx.ALIGN_CENTER, 1)
		launcher_grid.Add(self.new_project_button, 0, wx.ALIGN_CENTER, 64)
		new_project_description_label = wx.StaticText(self.launcher_parent_panel, wx.ID_ANY, "Create a new project for a set of samples, performing pre-processing before extracting spectra and generating reports.", style=wx.ALIGN_LEFT)
		new_project_description_label.Wrap(256)
		launcher_grid.Add(new_project_description_label, 0, wx.ALIGN_CENTER_VERTICAL, 64)
		launcher_grid.Add(self.new_info_button, 0, wx.ALIGN_CENTER, 1)
		launcher_grid.Add(self.open_project_button, 0, wx.ALIGN_CENTER, 64)
		open_project_description_label = wx.StaticText(self.launcher_parent_panel, wx.ID_ANY, "Open an existing project for viewing", style=wx.ALIGN_LEFT)
		open_project_description_label.Wrap(256)
		launcher_grid.Add(open_project_description_label, 0, wx.ALIGN_CENTER_VERTICAL, 64)
		launcher_grid.Add(self.open_info_button, 0, wx.ALIGN_CENTER, 0)
		launcher_grid.Add(self.comparison_button, 0, wx.ALIGN_CENTER, 64)
		comparison_description_label = wx.StaticText(self.launcher_parent_panel, wx.ID_ANY, "Compare two projects", style=wx.ALIGN_LEFT)
		comparison_description_label.Wrap(256)
		launcher_grid.Add(comparison_description_label, 0, wx.ALIGN_CENTER_VERTICAL, 64)
		launcher_grid.Add(self.comparison_info_button, 0, wx.ALIGN_CENTER, 1)
		launcher_sizer.Add(launcher_grid, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 10)
		self.launcher_parent_panel.SetSizer(launcher_sizer)
		launcher_parent_sizer.Add(self.launcher_parent_panel, 3, wx.ALL | wx.EXPAND, 10)
		messages_label = wx.StaticText(self.messages_panel, wx.ID_ANY, "Messages")
		messages_label.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
		messages_sizer.Add(messages_label, 0, wx.ALL, 5)
		messages_sizer.Add(self.messages, 1, wx.EXPAND, 0)
		self.messages_panel.SetSizer(messages_sizer)
		launcher_right_sizer.Add(self.messages_panel, 1, wx.ALL | wx.EXPAND, 5)
		self.launcher_right_panel.SetSizer(launcher_right_sizer)
		launcher_parent_sizer.Add(self.launcher_right_panel, 2, wx.BOTTOM | wx.EXPAND | wx.RIGHT | wx.TOP, 10)
		self.SetSizer(launcher_parent_sizer)
		launcher_parent_sizer.Fit(self)
		self.Layout()
		# end wxGlade
	
	def on_import(self, _):  # wxGlade: launcher_tab.<event_handler>
		self._parent.notebook_1.SetSelection(1)
	
	def on_new_project(self, _):  # wxGlade: launcher_tab.<event_handler>
		self._parent.notebook_1.SetSelection(2)
	
	def on_open_project(self, *args):  # wxGlade: launcher_tab.<event_handler>
		selected_project = file_dialog(self, "info", "Choose a Project to Open", "info files",
									   style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
									   # defaultDir=self.Config.get("main", "resultspath"))
									   defaultDir=self._parent.Config.results_dir)
		if selected_project != None:
			self._parent.browse_tab.setup_browser(selected_project)
			self._parent.notebook_1.SetSelection(3)
	
	def on_open_comparison(self, _):  # wxGlade: launcher_tab.<event_handler>
		self._parent.notebook_1.SetSelection(4)
	
	def do_import_info(self, event):  # wxGlade: launcher_tab.<event_handler>
		coming_soon()
		event.Skip()
	
	def do_new_info(self, event):  # wxGlade: launcher_tab.<event_handler>
		coming_soon()
		event.Skip()
	
	def do_open_info(self, event):  # wxGlade: launcher_tab.<event_handler>
		coming_soon()
		event.Skip()
	
	def do_comparison_info(self, event):  # wxGlade: launcher_tab.<event_handler>
		coming_soon()
		event.Skip()
	
	def refresh_launcher(self, _):
		self.launcher_parent_panel.Layout()
		self.launcher_parent_panel.Update()
		self.launcher_parent_panel.Refresh()


# end of class launcher_tab
