#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  paths_dialog.py
"""Dialog for configuring directories of GunShotMatch"""
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2017-2019 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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

import sys
import webbrowser
import configparser as ConfigParser

from domdf_python_tools.paths import relpath

import wx

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class paths_dialog(wx.Dialog):
	def __init__(self, *args, **kwds):
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
	
	def on_nistpath_clear(self, event):  # wxGlade: paths_dialog.<event_handler>
		self.nistpath.Clear()
		self.nistpath.SetFocus()
		event.Skip()
	
	def on_nistpath_browse(self, event):  # wxGlade: paths_dialog.<event_handler>
		nistpath_dlg = wx.DirDialog(None, "Choose a directory:", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
		if nistpath_dlg.ShowModal() == wx.ID_OK:
			self.nistpath.SetValue((nistpath_dlg.GetPath()))
		nistpath_dlg.Destroy()
		self.nistpath.SetFocus()
		event.Skip()
	
	def on_nistpath_help(self, event):  # wxGlade: paths_dialog.<event_handler>
		webbrowser.open("https://chemdata.nist.gov/mass-spc/ms-search/", 2)
		self.nistpath.SetFocus()
		event.Skip()
	
	def on_resultspath_clear(self, event):  # wxGlade: paths_dialog.<event_handler>
		self.resultspath.Clear()
		self.resultspath.SetFocus()
		event.Skip()
	
	def on_resultspath_browse(self, event):  # wxGlade: paths_dialog.<event_handler>
		resultspath_dlg = wx.DirDialog(None, "Choose a directory:", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
		if resultspath_dlg.ShowModal() == wx.ID_OK:
			self.resultspath.SetValue((resultspath_dlg.GetPath()))
		resultspath_dlg.Destroy()
		self.resultspath.SetFocus()
		event.Skip()
	
	def on_rawpath_clear(self, event):  # wxGlade: paths_dialog.<event_handler>
		self.rawpath.Clear()
		self.rawpath.SetFocus()
		event.Skip()
	
	def on_rawpath_browse(self, event):  # wxGlade: paths_dialog.<event_handler>
		rawpath_dlg = wx.DirDialog(None, "Choose a directory:", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON,
								   defaultPath=self.resultspath.GetValue())
		if rawpath_dlg.ShowModal() == wx.ID_OK:
			self.rawpath.SetValue((rawpath_dlg.GetPath()))
		rawpath_dlg.Destroy()
		self.rawpath.SetFocus()
		event.Skip()
	
	def on_csvpath_clear(self, event):  # wxGlade: paths_dialog.<event_handler>
		self.csvpath.Clear()
		self.csvpath.SetFocus()
		event.Skip()
	
	def on_csvpath_browse(self, event):  # wxGlade: paths_dialog.<event_handler>
		csvpath_dlg = wx.DirDialog(None, "Choose a directory:", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON,
								   defaultPath=self.resultspath.GetValue())
		if csvpath_dlg.ShowModal() == wx.ID_OK:
			self.csvpath.SetValue((csvpath_dlg.GetPath()))
		csvpath_dlg.Destroy()
		self.csvpath.SetFocus()
		event.Skip()
	
	def on_spectrapath_clear(self, event):  # wxGlade: paths_dialog.<event_handler>
		self.spectrapath.Clear()
		self.spectrapath.SetFocus()
		event.Skip()
	
	def on_spectrapath_browse(self, event):  # wxGlade: paths_dialog.<event_handler>
		spectrapath_dlg = wx.DirDialog(None, "Choose a directory:", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON,
									   defaultPath=self.resultspath.GetValue())
		if spectrapath_dlg.ShowModal() == wx.ID_OK:
			self.spectrapath.SetValue((spectrapath_dlg.GetPath()))
		spectrapath_dlg.Destroy()
		self.spectrapath.SetFocus()
		event.Skip()
	
	def on_msppath_clear(self, event):  # wxGlade: paths_dialog.<event_handler>
		self.msppath.Clear()
		self.msppath.SetFocus()
		event.Skip()
	
	def on_msppath_browse(self, event):  # wxGlade: paths_dialog.<event_handler>
		msppath_dlg = wx.DirDialog(None, "Choose a directory:", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON,
								   defaultPath=self.resultspath.GetValue())
		if msppath_dlg.ShowModal() == wx.ID_OK:
			self.msppath.SetValue((msppath_dlg.GetPath()))
		msppath_dlg.Destroy()
		self.msppath.SetFocus()
		event.Skip()
	
	def do_path_reset(self, event):  # wxGlade: paths_dialog.<event_handler>
		# Read the configuration from the file
		Config = ConfigParser.ConfigParser()
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
		self.expr_path.Clear()
		self.expr_path.SetFocus()
		event.Skip()
	
	def on_expr_path_browse(self, event):  # wxGlade: paths_dialog.<event_handler>
		expr_path_dlg = wx.DirDialog(None, "Choose a directory:", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON,
									 defaultPath=self.resultspath.GetValue())
		if expr_path_dlg.ShowModal() == wx.ID_OK:
			self.expr_path.SetValue((expr_path_dlg.GetPath()))
		expr_path_dlg.Destroy()
		self.expr_path.SetFocus()
		event.Skip()
	
	def on_charts_path_clear(self, event):  # wxGlade: paths_dialog.<event_handler>
		self.charts_path.Clear()
		self.charts_path.SetFocus()
		event.Skip()
	
	def on_charts_path_browse(self, event):  # wxGlade: paths_dialog.<event_handler>
		chartspath_dlg = wx.DirDialog(None, "Choose a directory:", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON,
									  defaultPath=self.resultspath.GetValue())
		if chartspath_dlg.ShowModal() == wx.ID_OK:
			self.charts_path.SetValue((chartspath_dlg.GetPath()))
		chartspath_dlg.Destroy()
		self.charts_path.SetFocus()
		event.Skip()

# end of class paths_dialog
