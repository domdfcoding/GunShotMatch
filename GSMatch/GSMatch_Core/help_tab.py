#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  help_tab.py
"""Tab for viewing online help, GitHub repository and Readme"""
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
#

# stdlib
import webbrowser

# 3rd party
import wx
import wx.html2

from domdf_wxpython_tools.icons import get_toolbar_icon

# this package
from GSMatch.GSMatch_Core.constants import help_home_url, github_url, readme_path


# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class help_tab(wx.Panel):
	def __init__(self, *args, **kwds):
		# begin wxGlade: help_tab.__init__
		kwds["style"] = kwds.get("style", 0) | wx.TAB_TRAVERSAL
		wx.Panel.__init__(self, *args, **kwds)
		self.help_toolbar_panel = wx.Panel(self, wx.ID_ANY)
		self.help_toolbar_panel.SetMaxSize((-1,40))
		self.help_focus_thief = wx.Button(self.help_toolbar_panel, wx.ID_ANY, "")
		self.help_back_btn = wx.BitmapButton(self.help_toolbar_panel, wx.ID_ANY, get_toolbar_icon("ART_GO_BACK", 24), style=wx.BORDER_NONE | wx.BU_AUTODRAW | wx.BU_EXACTFIT | wx.BU_NOTEXT)
		self.help_forward_btn = wx.BitmapButton(self.help_toolbar_panel, wx.ID_ANY, get_toolbar_icon("ART_GO_FORWARD", 24), style=wx.BORDER_NONE | wx.BU_AUTODRAW | wx.BU_EXACTFIT | wx.BU_NOTEXT)
		self.help_home_btn = wx.BitmapButton(self.help_toolbar_panel, wx.ID_ANY, get_toolbar_icon("ART_GO_HOME", 24), style=wx.BORDER_NONE | wx.BU_AUTODRAW | wx.BU_EXACTFIT | wx.BU_NOTEXT)
		self.help_url_text_ctrl = wx.TextCtrl(self.help_toolbar_panel, wx.ID_ANY, "", style=wx.TE_NO_VSCROLL | wx.TE_PROCESS_ENTER)
		self.help_go_btn = wx.BitmapButton(self.help_toolbar_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/go_24.png", wx.BITMAP_TYPE_ANY), style=wx.BORDER_NONE | wx.BU_AUTODRAW | wx.BU_EXACTFIT | wx.BU_NOTEXT)
		self.help_readme_btn = wx.BitmapButton(self.help_toolbar_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/help_24.png", wx.BITMAP_TYPE_ANY), style=wx.BORDER_NONE | wx.BU_AUTODRAW | wx.BU_EXACTFIT | wx.BU_NOTEXT)
		self.help_github_btn = wx.BitmapButton(self.help_toolbar_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/GitHub-Mark_24.png", wx.BITMAP_TYPE_ANY), style=wx.BORDER_NONE | wx.BU_AUTODRAW | wx.BU_EXACTFIT | wx.BU_NOTEXT)
		self.help_open_browser_btn = wx.Button(self.help_toolbar_panel, wx.ID_ANY, "Open in browser")
		self.help_parent_panel = wx.Panel(self, wx.ID_ANY, style=wx.BORDER_SUNKEN)
		self.help_browser = wx.html2.WebView.New(self.help_parent_panel, wx.ID_ANY)

		self.__set_properties()
		self.__do_layout()

		self.Bind(wx.EVT_BUTTON, self.on_help_back, self.help_back_btn)
		self.Bind(wx.EVT_BUTTON, self.on_help_forward, self.help_forward_btn)
		self.Bind(wx.EVT_BUTTON, self.on_help_home, self.help_home_btn)
		self.Bind(wx.EVT_TEXT_ENTER, self.on_help_go, self.help_url_text_ctrl)
		self.Bind(wx.EVT_BUTTON, self.on_help_go, self.help_go_btn)
		self.Bind(wx.EVT_BUTTON, self.on_help_readme, self.help_readme_btn)
		self.Bind(wx.EVT_BUTTON, self.on_help_github, self.help_github_btn)
		self.Bind(wx.EVT_BUTTON, self.on_help_browser, self.help_open_browser_btn)
		# end wxGlade
		
		self.help_home = help_home_url
		self.help_browser.LoadURL(self.help_home)
	
		self.Bind(wx.html2.EVT_WEBVIEW_NAVIGATED, self.help_update_url, self.help_browser)

	def __set_properties(self):
		# begin wxGlade: help_tab.__set_properties
		self.help_focus_thief.SetMinSize((1, 1))
		self.help_back_btn.SetMinSize((38, 38))
		self.help_back_btn.SetToolTip("Go back")
		self.help_forward_btn.SetMinSize((38, 38))
		self.help_forward_btn.SetToolTip("Go forward")
		self.help_home_btn.SetMinSize((38, 38))
		self.help_home_btn.SetToolTip("Open the homepage")
		self.help_url_text_ctrl.SetMinSize((380, -1))
		self.help_go_btn.SetMinSize((38, 38))
		self.help_go_btn.SetToolTip("Go to URL")
		self.help_readme_btn.SetMinSize((38, 38))
		self.help_readme_btn.SetToolTip("View Readme")
		self.help_github_btn.SetMinSize((38, 38))
		self.help_github_btn.SetToolTip("View GitHub page")
		self.help_toolbar_panel.SetMaxSize((10000000,40))
		# end wxGlade

	def __do_layout(self):
		# begin wxGlade: help_tab.__do_layout
		help_parent_sizer = wx.BoxSizer(wx.VERTICAL)
		help_main_sizer = wx.BoxSizer(wx.VERTICAL)
		help_toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
		help_toolbar_sizer.Add(self.help_focus_thief, 0, 0, 0)
		help_toolbar_sizer.Add(self.help_back_btn, 0, 0, 0)
		help_toolbar_sizer.Add(self.help_forward_btn, 0, 0, 0)
		help_toolbar_sizer.Add(self.help_home_btn, 0, 0, 0)
		help_toolbar_spacer_1 = wx.StaticLine(self.help_toolbar_panel, wx.ID_ANY, style=wx.LI_VERTICAL)
		help_toolbar_sizer.Add(help_toolbar_spacer_1, 0, wx.EXPAND, 0)
		help_toolbar_sizer.Add(self.help_url_text_ctrl, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
		help_toolbar_sizer.Add(self.help_go_btn, 0, 0, 0)
		help_toolbar_spacer_2 = wx.StaticLine(self.help_toolbar_panel, wx.ID_ANY, style=wx.LI_VERTICAL)
		help_toolbar_sizer.Add(help_toolbar_spacer_2, 0, wx.EXPAND, 0)
		help_toolbar_sizer.Add(self.help_readme_btn, 0, 0, 0)
		help_toolbar_sizer.Add(self.help_github_btn, 0, 0, 0)
		help_toolbar_spacer_3 = wx.StaticLine(self.help_toolbar_panel, wx.ID_ANY, style=wx.LI_VERTICAL)
		help_toolbar_sizer.Add(help_toolbar_spacer_3, 0, wx.EXPAND, 0)
		help_toolbar_sizer.Add(self.help_open_browser_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
		self.help_toolbar_panel.SetSizer(help_toolbar_sizer)
		help_parent_sizer.Add(self.help_toolbar_panel, 1, wx.EXPAND, 0)
		help_main_sizer.Add(self.help_browser, 1, wx.EXPAND, 0)
		self.help_parent_panel.SetSizer(help_main_sizer)
		help_parent_sizer.Add(self.help_parent_panel, 1, wx.EXPAND, 10)
		self.SetSizer(help_parent_sizer)
		help_parent_sizer.Fit(self)
		self.Layout()
		# end wxGlade

	def on_help_back(self, event):  # wxGlade: help_tab.<event_handler>
		self.help_browser.GoBack()
		self.help_focus_thief.SetFocus()
		event.Skip()

	def on_help_forward(self, event):  # wxGlade: help_tab.<event_handler>
		self.help_browser.GoForward()
		self.help_focus_thief.SetFocus()
		event.Skip()

	def on_help_home(self, event):  # wxGlade: help_tab.<event_handler>
		self.help_browser.LoadURL(self.help_home)
		self.help_focus_thief.SetFocus()
		event.Skip()
	
	def on_help_go(self, event):  # wxGlade: help_tab.<event_handler>
		print(self.help_url_text_ctrl.GetValue())
		url = self.help_url_text_ctrl.GetValue()
		if not url.startswith('http'):
			url = f"http://{url}"
		self.help_browser.LoadURL(url)
		self.help_focus_thief.SetFocus()

	def on_help_readme(self, event):  # wxGlade: help_tab.<event_handler>
		self.help_browser.LoadURL(f"file://{readme_path}")
		self.help_focus_thief.SetFocus()
		event.Skip()

	def on_help_github(self, event):  # wxGlade: help_tab.<event_handler>
		self.help_browser.LoadURL(github_url)
		self.help_focus_thief.SetFocus()
		event.Skip()

	def on_help_browser(self, event):  # wxGlade: help_tab.<event_handler>
		webbrowser.open(self.help_url_text_ctrl.GetValue(), 2)
		self.help_focus_thief.SetFocus()
		event.Skip()
	
	def help_update_url(self, event):
		self.help_url_text_ctrl.SetValue(event.GetURL())

# end of class help_tab
