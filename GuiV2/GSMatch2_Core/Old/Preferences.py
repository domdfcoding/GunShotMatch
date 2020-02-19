#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  Preferences.py
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


class GeneralPage(wx.StockPreferencesPage):
	def CreateWindow(self, parent):
		panel = wx.Panel(parent)
		panel.SetMinSize((600, 300))

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(wx.StaticText(panel, -1, "general page"),
				  wx.SizerFlags(1).TripleBorder())
		panel.SetSizer(sizer)
		return panel


class PathsPage(wx.PreferencesPage):
	def __init__(self):
		wx.PreferencesPage.__init__(self)

	def GetName(self):
		"""
		Overload this method to set the name of the page
		:return:
		:rtype:
		"""
		return "Paths"
	
	def CreateWindow(self, parent):
		panel = wx.Panel(parent)
		panel.SetMinSize((600, 300))

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(wx.StaticText(panel, -1, "advanced page"),
				  wx.SizerFlags(1).TripleBorder())
		panel.SetSizer(sizer)
		return panel


class Preferences(wx.PreferencesEditor):
	def __init__(self):
		super().__init__(title="GunShotMatch Preferences")

		self.AddPage(GeneralPage(kind=wx.StockPreferencesPage.Kind_General))
		self.AddPage(PathsPage())


app = wx.App()
prefs = Preferences()
prefs.Show(None)
app.MainLoop()