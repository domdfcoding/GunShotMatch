#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  AboutDialog.py
"""Dialog providing information about GunShotMatch, including the license"""
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2019 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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

import os
import wx
import wx.html2
import webbrowser

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class AboutDialog(wx.Dialog):
	def __init__(self, *args, **kwds):
		# begin wxGlade: AboutDialog.__init__
		kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
		wx.Dialog.__init__(self, *args, **kwds)
		self.about_top_panel = wx.Panel(self, wx.ID_ANY)
		self.focus_thief = wx.Button(self.about_top_panel, wx.ID_ANY, "")
		self.about_tabs = wx.Notebook(self, wx.ID_ANY)
		self.about_info = wx.Panel(self.about_tabs, wx.ID_ANY)
		self.SetSize((530, 447))
		self.SetMinSize((530, 447))
		self.info_panel = wx.Panel(self.about_info, wx.ID_ANY)
		self.githib_button = wx.Button(self.info_panel, wx.ID_ANY, "github.com/domdfcoding/GunShotMatch", style=wx.BORDER_NONE)
		self.githib_button.Bind(wx.EVT_SET_FOCUS, self.take_focus)
		self.website_button = wx.Button(self.info_panel, wx.ID_ANY, "http://dominic.davis-foster.co.uk/GSR", style=wx.BORDER_NONE)
		self.Credits = wx.Panel(self.about_tabs, wx.ID_ANY)
		self.credits_browser = wx.html2.WebView.New(self.Credits, wx.ID_ANY)
		self.credits_browser.LoadURL("file://{}".format(os.path.join(os.getcwd(),"AUTHORS")))
		self.License = wx.Panel(self.about_tabs, wx.ID_ANY)
		self.license_notebook = wx.Notebook(self.License, wx.ID_ANY)
		self.GPL_V3 = wx.Panel(self.license_notebook, wx.ID_ANY)
		self.gpl_v3_browser = wx.html2.WebView.New(self.GPL_V3, wx.ID_ANY)
		self.gpl_v3_browser.LoadURL("file://{}".format(os.path.join(os.getcwd(),"LICENSE")))
		self.GPL_V2 = wx.Panel(self.license_notebook, wx.ID_ANY)
		self.gpl_v2_browser = wx.html2.WebView.New(self.GPL_V2, wx.ID_ANY)
		self.gpl_v2_browser.LoadURL("file://{}".format(os.path.join(os.getcwd(),"LICENSE_GPL2")))
		self.CC_BY_SA = wx.Panel(self.license_notebook, wx.ID_ANY)
		self.cc_by_sa_browser = wx.html2.WebView.New(self.CC_BY_SA, wx.ID_ANY)
		self.cc_by_sa_browser.LoadURL("file://{}".format(os.path.join(os.getcwd(),"LICENSE_CC_BY_SA")))
		self.MIT = wx.Panel(self.license_notebook, wx.ID_ANY)
		self.mit_browser = wx.html2.WebView.New(self.MIT, wx.ID_ANY)
		self.mit_browser.LoadURL("file://{}".format(os.path.join(os.getcwd(),"LICENSE_MIT")))

		self.__set_properties()
		self.__do_layout()

		self.Bind(wx.EVT_BUTTON, self.on_about_github, self.githib_button)
		self.Bind(wx.EVT_BUTTON, self.on_about_website, self.website_button)
		# end wxGlade
		size = (650, 447)
		self.SetMaxSize(size)
		self.SetMinSize(size)
		self.SetSize(size)

	def __set_properties(self):
		# begin wxGlade: AboutDialog.__set_properties
		self.SetTitle("About GunShotMatch")
		_icon = wx.NullIcon
		_icon.CopyFromBitmap(wx.Bitmap("./lib/icons/GunShotMatch logo256.png", wx.BITMAP_TYPE_ANY))
		self.SetIcon(_icon)
		self.focus_thief.SetMinSize((1, 1))
		self.about_top_panel.SetBackgroundColour(wx.Colour(240, 240, 240))
		self.about_info.SetBackgroundColour(wx.Colour(240, 240, 240))
		self.Credits.SetBackgroundColour(wx.Colour(240, 240, 240))
		self.License.SetBackgroundColour(wx.Colour(240, 240, 240))
		self.about_tabs.SetBackgroundColour(wx.Colour(240, 240, 240))
		# end wxGlade
		self.about_top_panel.SetMinSize((530, 52))
		self.about_top_panel.SetMaxSize((530, 52))
		self.about_top_panel.SetSize((530, 52))
		self.about_info.SetMinSize((500, 200))
		self.about_info.SetMaxSize((500, 200))
		self.about_info.SetSize((500, 200))
		#self.text_ctrl_2.SetBackgroundColour(self.panel_3.GetBackgroundColour())
	
	def __do_layout(self):
		# begin wxGlade: AboutDialog.__do_layout
		about_parent_sizer = wx.BoxSizer(wx.VERTICAL)
		license_sizer = wx.BoxSizer(wx.HORIZONTAL)
		mit_sizer = wx.BoxSizer(wx.HORIZONTAL)
		cc_by_sa_sizer = wx.BoxSizer(wx.HORIZONTAL)
		gpl_v2_sizer = wx.BoxSizer(wx.HORIZONTAL)
		gpl_v3_sizer = wx.BoxSizer(wx.HORIZONTAL)
		credits_sizer = wx.BoxSizer(wx.HORIZONTAL)
		info_parent_sizer = wx.BoxSizer(wx.VERTICAL)
		info_sizer = wx.BoxSizer(wx.VERTICAL)
		about_top_sizer = wx.FlexGridSizer(1, 3, 0, 0)
		logo = wx.StaticBitmap(self.about_top_panel, wx.ID_ANY, wx.Bitmap("lib/icons/GunShotMatch logo48.png", wx.BITMAP_TYPE_ANY))
		about_top_sizer.Add(logo, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
		program_name_label = wx.StaticText(self.about_top_panel, wx.ID_ANY, "GunShotMatch")
		program_name_label.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, "Ubuntu"))
		about_top_sizer.Add(program_name_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 10)
		about_top_sizer.Add(self.focus_thief, 0, 0, 0)
		self.about_top_panel.SetSizer(about_top_sizer)
		about_parent_sizer.Add(self.about_top_panel, 1, wx.LEFT | wx.TOP, 5)
		tagline_label = wx.StaticText(self.info_panel, wx.ID_ANY, "Organic GunShot Residue Analysis", style=wx.ALIGN_CENTER)
		tagline_label.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, "Ubuntu"))
		info_sizer.Add(tagline_label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 15)
		version_label = wx.StaticText(self.info_panel, wx.ID_ANY, "Version <version string goes here>", style=wx.ALIGN_CENTER)
		info_sizer.Add(version_label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)
		info_sizer.Add(self.githib_button, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.LEFT | wx.RIGHT | wx.TOP, 10)
		info_sizer.Add(self.website_button, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM | wx.LEFT | wx.RIGHT, 10)
		copyright_label = wx.StaticText(self.info_panel, wx.ID_ANY, "Copyright (c) 2017-2019\nDominic Davis-Foster\nAll rights reserved.", style=wx.ALIGN_CENTER)
		info_sizer.Add(copyright_label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 20)
		self.info_panel.SetSizer(info_sizer)
		info_parent_sizer.Add(self.info_panel, 1, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 5)
		self.about_info.SetSizer(info_parent_sizer)
		credits_sizer.Add(self.credits_browser, 1, wx.EXPAND, 0)
		self.Credits.SetSizer(credits_sizer)
		gpl_v3_sizer.Add(self.gpl_v3_browser, 1, wx.EXPAND, 0)
		self.GPL_V3.SetSizer(gpl_v3_sizer)
		gpl_v2_sizer.Add(self.gpl_v2_browser, 1, wx.EXPAND, 0)
		self.GPL_V2.SetSizer(gpl_v2_sizer)
		cc_by_sa_sizer.Add(self.cc_by_sa_browser, 1, wx.EXPAND, 0)
		self.CC_BY_SA.SetSizer(cc_by_sa_sizer)
		mit_sizer.Add(self.mit_browser, 1, wx.EXPAND, 0)
		self.MIT.SetSizer(mit_sizer)
		self.license_notebook.AddPage(self.GPL_V3, "GPL v3")
		self.license_notebook.AddPage(self.GPL_V2, "GPL v2")
		self.license_notebook.AddPage(self.CC_BY_SA, "CC-BY-SA")
		self.license_notebook.AddPage(self.MIT, "MIT")
		license_sizer.Add(self.license_notebook, 1, wx.EXPAND, 0)
		self.License.SetSizer(license_sizer)
		self.about_tabs.AddPage(self.about_info, "Info")
		self.about_tabs.AddPage(self.Credits, "Credits")
		self.about_tabs.AddPage(self.License, "Licence")
		about_parent_sizer.Add(self.about_tabs, 1, wx.ALL | wx.EXPAND, 3)
		self.SetSizer(about_parent_sizer)
		about_parent_sizer.Fit(self)
		self.Layout()
		# end wxGlade
		self.btns = self.CreateSeparatedButtonSizer(wx.CLOSE)
		about_parent_sizer.Add(self.btns, 0, wx.ALL | wx.EXPAND, 5)
		self.SetSizer(about_parent_sizer)
		about_parent_sizer.Fit(self)
		self.SetMaxSize((530, 447))
		self.SetMinSize((530, 447))
		self.SetSize((530, 447))
	
	def on_about_github(self, event):  # wxGlade: AboutDialog.<event_handler>
		webbrowser.open("http://github.com/domdfcoding/GunShotMatch", 2)
		self.focus_thief.SetFocus()
		event.Skip()
	
	def on_about_website(self, event):  # wxGlade: AboutDialog.<event_handler>
		webbrowser.open("http://dominic.davis-foster.co.uk/GSR", 2)
		self.focus_thief.SetFocus()
		event.Skip()
	
	def take_focus(self, event):
		self.focus_thief.SetFocus()
		event.Skip()

# end of class AboutDialog
