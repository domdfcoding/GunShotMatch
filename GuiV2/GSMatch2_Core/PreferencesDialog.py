#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  PreferencesDialog.py
#
"""
Dialog for configuring GunShotMatch preferences
"""
#
#  This file is part of GunShotMatch
#
#  Copyright © 2017-2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import webbrowser

# 3rd party
import wx
# from domdf_wxpython_tools.picker import dir_picker
from domdf_wxpython_tools import DirBrowseCtrl
from domdf_wxpython_tools.ColourPickerPanel import ColourPickerPanel
from domdf_wxpython_tools.StylePickerPanel import StylePickerPanel

# this package
from GuiV2.GSMatch2_Core.Config import internal_config
from GuiV2.icons import get_icon


# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade

# TODO: include chart colours and markers in the preferences dialog

class PreferencesDialog(wx.Dialog):
	def __init__(self, *args, **kwds):
		"""
		:param parent: Can be None, a frame or another dialog box.
		:type parent: wx.Window
		:param id: An identifier for the dialog. A value of -1 is taken to mean a default.
		:type id: wx.WindowID
		:param title: The title of the dialog.
		:type title: str
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
		
		# begin wxGlade: PreferencesDialog.__init__
		kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
		wx.Dialog.__init__(self, *args, **kwds)
		self.SetSize((680, 400))
		self.preferences_notebook = wx.Notebook(self, wx.ID_ANY)
		self.general_page = wx.Panel(self.preferences_notebook, wx.ID_ANY)
		self.show_welcome_dialog = wx.CheckBox(self.general_page, wx.ID_ANY, "Show 'Welcome' Dialog when starting GunShotMatch")
		self.close_with_welcome_dialog = wx.CheckBox(self.general_page, wx.ID_ANY, "Exit GunShotMatch when closing 'Welcome' dialog")
		self.paths_page = wx.Panel(self.preferences_notebook, wx.ID_ANY)
		self.paths_panel = wx.Panel(self.paths_page, wx.ID_ANY)
		self.nistpath = DirBrowseCtrl(self.paths_panel, wx.ID_ANY, labelText='')
		self.nistpath_help = wx.BitmapButton(self.paths_panel, wx.ID_ANY, get_icon("information", 16))
		self.resultspath = DirBrowseCtrl(self.paths_panel, wx.ID_ANY, labelText='')
		self.csvpath = DirBrowseCtrl(self.paths_panel, wx.ID_ANY, labelText='')
		self.spectrapath = DirBrowseCtrl(self.paths_panel, wx.ID_ANY, labelText='')
		self.msppath = DirBrowseCtrl(self.paths_panel, wx.ID_ANY, labelText='')
		self.charts_path = DirBrowseCtrl(self.paths_panel, wx.ID_ANY, labelText='')
		self.chart_colours_page = wx.Panel(self.preferences_notebook, wx.ID_ANY)
		self.colour_picker = ColourPickerPanel(self.chart_colours_page, wx.ID_ANY, selection_choices=internal_config.chart_colours)
		self.chart_markers_page = wx.Panel(self.preferences_notebook, wx.ID_ANY)
		self.marker_picker = StylePickerPanel(self.chart_markers_page, wx.ID_ANY, selection_choices=internal_config.chart_styles)

		self.__set_properties()
		self.__do_layout()

		self.Bind(wx.EVT_BUTTON, self.on_nistpath_help, self.nistpath_help)
		# end wxGlade
	
		# Populate the settings
		self.load_preferences()
		self.Bind(wx.EVT_BUTTON, self.on_ok, id=wx.ID_OK)

	def __set_properties(self):
		# begin wxGlade: PreferencesDialog.__set_properties
		self.SetTitle("GunShotMatch Preferences")
		self.SetSize((680, 400))
		self.show_welcome_dialog.SetValue(1)
		self.nistpath.SetMinSize((512, -1))
		self.nistpath_help.SetSize(self.nistpath_help.GetBestSize())
		# end wxGlade

	def __do_layout(self):
		# begin wxGlade: PreferencesDialog.__do_layout
		outer_sizer = wx.BoxSizer(wx.VERTICAL)
		markers_page_sizer = wx.BoxSizer(wx.HORIZONTAL)
		colours_page_sizer = wx.BoxSizer(wx.HORIZONTAL)
		paths_page_sizer = wx.BoxSizer(wx.HORIZONTAL)
		paths_sizer = wx.FlexGridSizer(6, 3, 0, 0)
		general_sizer = wx.BoxSizer(wx.VERTICAL)
		general_sizer.Add((20, 5), 0, 0, 0)
		general_sizer.Add(self.show_welcome_dialog, 0, wx.ALL, 5)
		general_sizer.Add(self.close_with_welcome_dialog, 0, wx.ALL, 5)
		general_sizer.Add((0, 0), 0, 0, 0)
		general_sizer.Add((0, 0), 0, 0, 0)
		self.general_page.SetSizer(general_sizer)
		paths_page_sizer.Add((5, 20), 0, 0, 0)
		nistpath_label = wx.StaticText(self.paths_panel, wx.ID_ANY, "NIST MS Search: ")
		paths_sizer.Add(nistpath_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.nistpath, 1, wx.EXPAND, 0)
		paths_sizer.Add(self.nistpath_help, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		resultspath_label = wx.StaticText(self.paths_panel, wx.ID_ANY, "Results: ")
		paths_sizer.Add(resultspath_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.resultspath, 1, wx.EXPAND, 0)
		paths_sizer.Add((0, 0), 0, 0, 0)
		csvpath_label = wx.StaticText(self.paths_panel, wx.ID_ANY, "CSV Reports: ")
		paths_sizer.Add(csvpath_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.csvpath, 1, wx.EXPAND, 0)
		paths_sizer.Add((0, 0), 0, 0, 0)
		spectrapath_label = wx.StaticText(self.paths_panel, wx.ID_ANY, "Spectra Images: ")
		paths_sizer.Add(spectrapath_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.spectrapath, 1, wx.EXPAND, 0)
		paths_sizer.Add((0, 0), 0, 0, 0)
		msppath_label = wx.StaticText(self.paths_panel, wx.ID_ANY, "MSP Spectra: ")
		paths_sizer.Add(msppath_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.msppath, 1, wx.EXPAND, 0)
		paths_sizer.Add((0, 0), 0, 0, 0)
		charts_label = wx.StaticText(self.paths_panel, wx.ID_ANY, "Charts: ")
		paths_sizer.Add(charts_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.charts_path, 1, wx.EXPAND, 0)
		paths_sizer.Add((0, 0), 0, 0, 0)
		self.paths_panel.SetSizer(paths_sizer)
		paths_page_sizer.Add(self.paths_panel, 5, wx.ALL | wx.EXPAND, 5)
		paths_page_sizer.Add((5, 20), 0, 0, 0)
		self.paths_page.SetSizer(paths_page_sizer)
		colours_page_sizer.Add(self.colour_picker, 1, wx.ALL | wx.EXPAND, 5)
		self.chart_colours_page.SetSizer(colours_page_sizer)
		markers_page_sizer.Add(self.marker_picker, 1, wx.ALL | wx.EXPAND, 5)
		self.chart_markers_page.SetSizer(markers_page_sizer)
		self.preferences_notebook.AddPage(self.general_page, "General")
		self.preferences_notebook.AddPage(self.paths_page, "Paths")
		self.preferences_notebook.AddPage(self.chart_colours_page, "Colours")
		self.preferences_notebook.AddPage(self.chart_markers_page, "Markers")
		outer_sizer.Add(self.preferences_notebook, 1, wx.EXPAND, 0)
		self.SetSizer(outer_sizer)
		self.Layout()
		# end wxGlade
		
		self.btns = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
		outer_sizer.Add(self.btns, 0, wx.ALL | wx.EXPAND, 5)
		# self.SetMinSize((755, 400))
		# self.SetSize((755, 400))

	def on_nistpath_help(self, event):  # wxGlade: PreferencesDialog.<event_handler>
		"""
		Handler for opening the URL from which NIST MS Search can be downloaded

		:param event:
		:type event:
		"""
		
		webbrowser.open("https://chemdata.nist.gov/mass-spc/ms-search/", 2)
		self.nistpath.SetFocus()
		event.Skip()
	
	def load_preferences(self):
		# General Page
		self.show_welcome_dialog.SetValue(internal_config.show_welcome_dialog)
		self.close_with_welcome_dialog.SetValue(internal_config.exit_on_closing_welcome_dialog)
		
		# Paths Page
		self.nistpath.SetValue(internal_config.nist_path)
		self.resultspath.SetValue(internal_config.results_dir)
		self.csvpath.SetValue(internal_config.csv_dir)
		self.spectrapath.SetValue(internal_config.spectra_dir)
		self.msppath.SetValue(internal_config.msp_dir)
		self.charts_path.SetValue(internal_config.charts_dir)
	
	def on_ok(self, _):
		"""
		Handler for user pressing OK button
		"""
		
		print("OK pressed")
		
		# General Page
		internal_config.show_welcome_dialog = self.show_welcome_dialog.GetValue()
		internal_config.exit_on_closing_welcome_dialog = self.close_with_welcome_dialog.GetValue()
		
		# Paths Page
		internal_config.nist_path = self.nistpath.GetValue()
		internal_config.results_dir = self.resultspath.GetValue()
		internal_config.csv_dir = self.csvpath.GetValue()
		internal_config.spectra_dir = self.spectrapath.GetValue()
		internal_config.msp_dir = self.msppath.GetValue()
		internal_config.charts_dir = self.charts_path.GetValue()
		
		# Colours and markers
		internal_config.chart_styles = self.marker_picker.get_selection()
		internal_config.chart_colours = self.colour_picker.get_selection()
		
		# TODO: self.replot_chart()
		
		if self.IsModal():
			self.EndModal(wx.ID_OK)
		else:
			self.Destroy()

# end of class PreferencesDialog
