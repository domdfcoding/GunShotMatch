#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  paths_dialog.py
"""Dialog for configuring directories of GunShotMatch"""
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

# stdlib
import sys
import webbrowser
import configparser

# 3rd party
import wx
from domdf_python_tools.paths import relpath


# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class paths_dialog(wx.Dialog):
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
		
		# begin wxGlade: paths_dialog.__init__
		kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
		wx.Dialog.__init__(self, *args, **kwds)
		self.SetSize((849, 437))
		self.prefs_panel = wx.Panel(self, wx.ID_ANY)
		self.paths_panel = wx.Panel(self.prefs_panel, wx.ID_ANY)
		self.nistpath = wx.TextCtrl(self.paths_panel, wx.ID_ANY, "", style=wx.TE_NO_VSCROLL)
		self.nistpath_clear = wx.BitmapButton(self.paths_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/go_back_16.png", wx.BITMAP_TYPE_ANY))
		self.nistpath_browse = wx.BitmapButton(self.paths_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/open_16.png", wx.BITMAP_TYPE_ANY))
		self.nistpath_help = wx.BitmapButton(self.paths_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/information_16.png", wx.BITMAP_TYPE_ANY))
		self.resultspath = wx.TextCtrl(self.paths_panel, wx.ID_ANY, "", style=wx.TE_NO_VSCROLL)
		self.resultspath_clear = wx.BitmapButton(self.paths_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/go_back_16.png", wx.BITMAP_TYPE_ANY))
		self.resultspath_browse = wx.BitmapButton(self.paths_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/open_16.png", wx.BITMAP_TYPE_ANY))
		self.rawpath = wx.TextCtrl(self.paths_panel, wx.ID_ANY, "", style=wx.TE_NO_VSCROLL)
		self.rawpath_clear = wx.BitmapButton(self.paths_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/go_back_16.png", wx.BITMAP_TYPE_ANY))
		self.rawpath_browse = wx.BitmapButton(self.paths_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/open_16.png", wx.BITMAP_TYPE_ANY))
		self.csvpath = wx.TextCtrl(self.paths_panel, wx.ID_ANY, "", style=wx.TE_NO_VSCROLL)
		self.csvpath_clear = wx.BitmapButton(self.paths_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/go_back_16.png", wx.BITMAP_TYPE_ANY))
		self.csvpath_browse = wx.BitmapButton(self.paths_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/open_16.png", wx.BITMAP_TYPE_ANY))
		self.spectrapath = wx.TextCtrl(self.paths_panel, wx.ID_ANY, "", style=wx.TE_NO_VSCROLL)
		self.spectrapath_clear = wx.BitmapButton(self.paths_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/go_back_16.png", wx.BITMAP_TYPE_ANY))
		self.spectrapath_browse = wx.BitmapButton(self.paths_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/open_16.png", wx.BITMAP_TYPE_ANY))
		self.msppath = wx.TextCtrl(self.paths_panel, wx.ID_ANY, "", style=wx.TE_NO_VSCROLL)
		self.msppath_clear = wx.BitmapButton(self.paths_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/go_back_16.png", wx.BITMAP_TYPE_ANY))
		self.msppath_browse = wx.BitmapButton(self.paths_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/open_16.png", wx.BITMAP_TYPE_ANY))
		self.expr_path = wx.TextCtrl(self.paths_panel, wx.ID_ANY, "", style=wx.TE_NO_VSCROLL)
		self.expr_clear = wx.BitmapButton(self.paths_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/go_back_16.png", wx.BITMAP_TYPE_ANY))
		self.expr_browse = wx.BitmapButton(self.paths_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/open_16.png", wx.BITMAP_TYPE_ANY))
		self.charts_path = wx.TextCtrl(self.paths_panel, wx.ID_ANY, "", style=wx.TE_NO_VSCROLL)
		self.charts_clear = wx.BitmapButton(self.paths_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/go_back_16.png", wx.BITMAP_TYPE_ANY))
		self.charts_browse = wx.BitmapButton(self.paths_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/open_16.png", wx.BITMAP_TYPE_ANY))
		self.reset_button_panel = wx.Panel(self.prefs_panel, wx.ID_ANY)
		self.paths_reset = wx.Button(self.reset_button_panel, wx.ID_ANY, "Reset")

		self.__set_properties()
		self.__do_layout()

		self.Bind(wx.EVT_BUTTON, self.on_nistpath_clear, self.nistpath_clear)
		self.Bind(wx.EVT_BUTTON, self.on_nistpath_browse, self.nistpath_browse)
		self.Bind(wx.EVT_BUTTON, self.on_nistpath_help, self.nistpath_help)
		self.Bind(wx.EVT_BUTTON, self.on_resultspath_clear, self.resultspath_clear)
		self.Bind(wx.EVT_BUTTON, self.on_resultspath_browse, self.resultspath_browse)
		self.Bind(wx.EVT_BUTTON, self.on_rawpath_clear, self.rawpath_clear)
		self.Bind(wx.EVT_BUTTON, self.on_rawpath_browse, self.rawpath_browse)
		self.Bind(wx.EVT_BUTTON, self.on_csvpath_clear, self.csvpath_clear)
		self.Bind(wx.EVT_BUTTON, self.on_csvpath_browse, self.csvpath_browse)
		self.Bind(wx.EVT_BUTTON, self.on_spectrapath_clear, self.spectrapath_clear)
		self.Bind(wx.EVT_BUTTON, self.on_spectrapath_browse, self.spectrapath_browse)
		self.Bind(wx.EVT_BUTTON, self.on_msppath_clear, self.msppath_clear)
		self.Bind(wx.EVT_BUTTON, self.on_msppath_browse, self.msppath_browse)
		self.Bind(wx.EVT_BUTTON, self.on_expr_path_clear, self.expr_clear)
		self.Bind(wx.EVT_BUTTON, self.on_expr_path_browse, self.expr_browse)
		self.Bind(wx.EVT_BUTTON, self.on_charts_path_clear, self.charts_clear)
		self.Bind(wx.EVT_BUTTON, self.on_charts_path_browse, self.charts_browse)
		self.Bind(wx.EVT_BUTTON, self.do_path_reset, self.paths_reset)
		# end wxGlade

		# Read the configuration from the file
		self.do_path_reset(0)

	def __set_properties(self):
		# begin wxGlade: paths_dialog.__set_properties
		self.SetTitle("Configure Paths")
		_icon = wx.NullIcon
		_icon.CopyFromBitmap(wx.Bitmap("./lib/icons/GunShotMatch logo256.png", wx.BITMAP_TYPE_ANY))
		self.SetIcon(_icon)
		self.SetSize((849, 437))
		self.nistpath.SetMinSize((512, 29))
		self.nistpath_clear.SetMinSize((29, 29))
		self.nistpath_browse.SetMinSize((29, 29))
		self.nistpath_help.SetMinSize((29, 29))
		self.resultspath.SetMinSize((512, 29))
		self.resultspath_clear.SetMinSize((29, 29))
		self.resultspath_browse.SetMinSize((29, 29))
		self.rawpath.SetMinSize((512, 29))
		self.rawpath_clear.SetMinSize((29, 29))
		self.rawpath_browse.SetMinSize((29, 29))
		self.csvpath.SetMinSize((512, 29))
		self.csvpath_clear.SetMinSize((29, 29))
		self.csvpath_browse.SetMinSize((29, 29))
		self.spectrapath.SetMinSize((512, 29))
		self.spectrapath_clear.SetMinSize((29, 29))
		self.spectrapath_browse.SetMinSize((29, 29))
		self.msppath.SetMinSize((512, 29))
		self.msppath_clear.SetMinSize((29, 29))
		self.msppath_browse.SetMinSize((29, 29))
		self.expr_path.SetMinSize((512, 29))
		self.expr_clear.SetMinSize((29, 29))
		self.expr_browse.SetMinSize((29, 29))
		self.charts_path.SetMinSize((512, 29))
		self.charts_clear.SetMinSize((29, 29))
		self.charts_browse.SetMinSize((29, 29))
		# end wxGlade

	def __do_layout(self):
		# begin wxGlade: paths_dialog.__do_layout
		prefs_parent_sizer = wx.BoxSizer(wx.VERTICAL)
		paths_parent_sizer = wx.BoxSizer(wx.VERTICAL)
		sizer_1 = wx.BoxSizer(wx.VERTICAL)
		paths_sizer = wx.FlexGridSizer(8, 5, 0, 0)
		nistpath_label = wx.StaticText(self.paths_panel, wx.ID_ANY, "NIST MS Search: ")
		paths_sizer.Add(nistpath_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.nistpath, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.nistpath_clear, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.nistpath_browse, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.nistpath_help, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		resultspath_label = wx.StaticText(self.paths_panel, wx.ID_ANY, "Results: ")
		paths_sizer.Add(resultspath_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.resultspath, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.resultspath_clear, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.resultspath_browse, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add((0, 0), 0, 0, 0)
		rawpath_label = wx.StaticText(self.paths_panel, wx.ID_ANY, ".RAW Files: ")
		paths_sizer.Add(rawpath_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.rawpath, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.rawpath_clear, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.rawpath_browse, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add((0, 0), 0, 0, 0)
		csvpath_label = wx.StaticText(self.paths_panel, wx.ID_ANY, "CSV Reports: ")
		paths_sizer.Add(csvpath_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.csvpath, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.csvpath_clear, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.csvpath_browse, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add((0, 0), 0, 0, 0)
		spectrapath_label = wx.StaticText(self.paths_panel, wx.ID_ANY, "Spectra Images: ")
		paths_sizer.Add(spectrapath_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.spectrapath, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.spectrapath_clear, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.spectrapath_browse, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add((0, 0), 0, 0, 0)
		msppath_label = wx.StaticText(self.paths_panel, wx.ID_ANY, "MSP Spectra: ")
		paths_sizer.Add(msppath_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.msppath, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.msppath_clear, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.msppath_browse, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add((0, 0), 0, 0, 0)
		expr_label = wx.StaticText(self.paths_panel, wx.ID_ANY, "Experiment Files:")
		paths_sizer.Add(expr_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.expr_path, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.expr_clear, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.expr_browse, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add((0, 0), 0, 0, 0)
		charts_label = wx.StaticText(self.paths_panel, wx.ID_ANY, "Charts: ")
		paths_sizer.Add(charts_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.charts_path, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.charts_clear, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add(self.charts_browse, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		paths_sizer.Add((0, 0), 0, 0, 0)
		self.paths_panel.SetSizer(paths_sizer)
		paths_parent_sizer.Add(self.paths_panel, 5, wx.ALL | wx.EXPAND, 5)
		sizer_1.Add(self.paths_reset, 0, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.RIGHT, 9)
		self.reset_button_panel.SetSizer(sizer_1)
		paths_parent_sizer.Add(self.reset_button_panel, 1, wx.EXPAND, 0)
		self.prefs_panel.SetSizer(paths_parent_sizer)
		prefs_parent_sizer.Add(self.prefs_panel, 1, wx.ALL | wx.EXPAND, 10)
		self.SetSizer(prefs_parent_sizer)
		self.Layout()
		# end wxGlade
		
		self.btns = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)
		prefs_parent_sizer.Add(self.btns, 0, wx.ALL | wx.EXPAND, 5)
		self.SetMinSize((755, 400))
		self.SetSize((755, 400))
	
	@staticmethod
	def browse_dialog():
		"""
		Opens a dialog to browse for a directory
		:return:
		:rtype:
		"""
		dlg = wx.DirDialog(None, "Choose a directory:", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
		if dlg.ShowModal() == wx.ID_OK:
			selected_value = dlg.GetPath()
		else:
			selected_value = None
		
		dlg.Destroy()
		
		return selected_value
	
	def on_nistpath_clear(self, event):  # wxGlade: paths_dialog.<event_handler>
		"""
		Handler for clearing the value of the nistpath field
		
		:param event:
		:type event:
		"""
		
		self.nistpath.Clear()
		self.nistpath.SetFocus()
		event.Skip()
		
	def on_nistpath_browse(self, event):  # wxGlade: paths_dialog.<event_handler>
		"""
		Handler for browsing for the directory containing the NIST MS Search program
		
		:param event:
		:type event:
		"""
		
		selected_value = self.browse_dialog()
		if selected_value:
			self.nistpath.SetValue(selected_value)
		self.nistpath.SetFocus()
		event.Skip()
	
	def on_nistpath_help(self, event):  # wxGlade: paths_dialog.<event_handler>
		"""
		Handler for opening the URL from which NIST MS Search can be downloaded
		
		:param event:
		:type event:
		"""
		
		webbrowser.open("https://chemdata.nist.gov/mass-spc/ms-search/", 2)
		self.nistpath.SetFocus()
		event.Skip()
	
	def on_resultspath_clear(self, event):  # wxGlade: paths_dialog.<event_handler>
		"""
		Handler for clearing the value of the resultspath field

		:param event:
		:type event:
		"""
		
		self.resultspath.Clear()
		self.resultspath.SetFocus()
		event.Skip()
	
	def on_resultspath_browse(self, event):  # wxGlade: paths_dialog.<event_handler>
		"""
		Handler for browsing for the directory in which to store the results

		:param event:
		:type event:
		"""
		
		selected_value = self.browse_dialog()
		if selected_value:
			self.resultspath.SetValue(selected_value)
		self.resultspath.SetFocus()
		event.Skip()
	
	def on_rawpath_clear(self, event):  # wxGlade: paths_dialog.<event_handler>
		"""
		Handler for clearing the value of the rawpath field

		:param event:
		:type event:
		"""

		self.rawpath.Clear()
		self.rawpath.SetFocus()
		event.Skip()
	
	def on_rawpath_browse(self, event):  # wxGlade: paths_dialog.<event_handler>
		"""
		Handler for browsing for the directory in which .RAW files are stored

		:param event:
		:type event:
		"""
		
		selected_value = self.browse_dialog()
		if selected_value:
			self.rawpath.SetValue(selected_value)
		self.rawpath.SetFocus()
		event.Skip()
	
	def on_csvpath_clear(self, event):  # wxGlade: paths_dialog.<event_handler>
		"""
		Handler for clearing the value of the csvpath field

		:param event:
		:type event:
		"""

		self.csvpath.Clear()
		self.csvpath.SetFocus()
		event.Skip()
	
	def on_csvpath_browse(self, event):  # wxGlade: paths_dialog.<event_handler>
		"""
		Handler for browsing for the directory in which to store the CSV files

		:param event:
		:type event:
		"""
		
		selected_value = self.browse_dialog()
		if selected_value:
			self.csvpath.SetValue(selected_value)
		self.csvpath.SetFocus()
		event.Skip()
	
	def on_spectrapath_clear(self, event):  # wxGlade: paths_dialog.<event_handler>
		"""
		Handler for clearing the value of the spectrapath field

		:param event:
		:type event:
		"""

		self.spectrapath.Clear()
		self.spectrapath.SetFocus()
		event.Skip()
	
	def on_spectrapath_browse(self, event):  # wxGlade: paths_dialog.<event_handler>
		"""
		Handler for browsing for the directory in which to store the spectra images

		:param event:
		:type event:
		"""
		
		selected_value = self.browse_dialog()
		if selected_value:
			self.spectrapath.SetValue(selected_value)
		self.spectrapath.SetFocus()
		event.Skip()
	
	def on_msppath_clear(self, event):  # wxGlade: paths_dialog.<event_handler>
		"""
		Handler for clearing the value of the msppath field

		:param event:
		:type event:
		"""

		self.msppath.Clear()
		self.msppath.SetFocus()
		event.Skip()
	
	def on_msppath_browse(self, event):  # wxGlade: paths_dialog.<event_handler>
		"""
		Handler for browsing for the directory in which to store the MSP files for NIST MS Search

		:param event:
		:type event:
		"""

		selected_value = self.browse_dialog()
		if selected_value:
			self.msppath.SetValue(selected_value)
		self.msppath.SetFocus()
		event.Skip()
	
	def do_path_reset(self, _):  # wxGlade: paths_dialog.<event_handler>
		"""
		Reverts to the last values saved to the configuration file
		"""

		Config = configparser.ConfigParser()
		Config.read("config.ini")
		if sys.platform == "win32":
			self.nistpath.SetValue(relpath(Config.get("main", "nistpath")))
		else:
			self.nistpath.SetValue(relpath(Config.get("main", "linuxnistpath")))
		self.resultspath.SetValue(relpath(Config.get("main", "resultspath")))
		self.rawpath.SetValue(relpath(Config.get("main", "rawpath")))
		self.csvpath.SetValue(relpath(Config.get("main", "csvpath")))
		self.spectrapath.SetValue(relpath(Config.get("main", "spectrapath")))
		self.msppath.SetValue(relpath(Config.get("main", "msppath")))
		self.charts_path.SetValue(relpath(Config.get("main", "chartspath")))
		self.expr_path.SetValue(relpath(Config.get("main", "exprdir")))
	
	def on_expr_path_clear(self, event):  # wxGlade: paths_dialog.<event_handler>
		"""
		Handler for clearing the value of the expr_path field

		:param event:
		:type event:
		"""
		
		self.expr_path.Clear()
		self.expr_path.SetFocus()
		event.Skip()
	
	def on_expr_path_browse(self, event):  # wxGlade: paths_dialog.<event_handler>
		"""
		Handler for browsing for the directory in which to store the experiment files

		:param event:
		:type event:
		"""
		
		selected_value = self.browse_dialog()
		if selected_value:
			self.expr_path.SetValue(selected_value)
		self.expr_path.SetFocus()
		event.Skip()
	
	def on_charts_path_clear(self, event):  # wxGlade: paths_dialog.<event_handler>
		"""
		Handler for clearing the value of the charts_path field

		:param event:
		:type event:
		"""
		
		self.charts_path.Clear()
		self.charts_path.SetFocus()
		event.Skip()
	
	def on_charts_path_browse(self, event):  # wxGlade: paths_dialog.<event_handler>
		"""
		Handler for browsing for the directory in which to store the chart images

		:param event:
		:type event:
		"""
		
		selected_value = self.browse_dialog()
		if selected_value:
			self.charts_path.SetValue(selected_value)
		self.charts_path.SetFocus()
		event.Skip()

# end of class paths_dialog
