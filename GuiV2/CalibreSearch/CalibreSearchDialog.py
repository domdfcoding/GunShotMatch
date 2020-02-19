#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  CalibreSearchPanel.py
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
from GuiV2 import CalibreSearch


# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class CalibreSearchDialog(wx.Dialog):
	def __init__(
			self, parent, id=wx.ID_ANY, title="Calibre Search", pos=wx.DefaultPosition,
			 style=wx.DEFAULT_DIALOG_STYLE, name=wx.DialogNameStr
			):
		
		args = (parent, id, title, pos)
		kwds = {
				"style": style,
				"name": name,
				}
	
		# begin wxGlade: CalibreSearchDialog.__init__
		kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE | wx.MINIMIZE_BOX
		wx.Dialog.__init__(self, *args, **kwds)
		self.CalibreSearchPanel = CalibreSearch.SearchPanel(self, wx.ID_ANY, dialog=True)

		self.__set_properties()
		self.__do_layout()
		# end wxGlade
	
		self.Bind(wx.EVT_BUTTON, self.OnCancel, id=wx.ID_CANCEL)
		self.Bind(wx.EVT_BUTTON, self.OnSelect, id=wx.ID_ADD)

	def __set_properties(self):
		# begin wxGlade: CalibreSearchDialog.__set_properties
		pass
		# end wxGlade
	
	def __do_layout(self):
		# begin wxGlade: CalibreSearchDialog.__do_layout
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		main_sizer.Add(self.CalibreSearchPanel, 1, wx.EXPAND, 0)
		self.SetSizer(main_sizer)
		main_sizer.Fit(self)
		self.Layout()
		# end wxGlade
	
		self.SetSize(self.CalibreSearchPanel.GetMaxSize())
		self.SetMinSize(self.CalibreSearchPanel.GetMaxSize())
		self.SetMaxSize(self.CalibreSearchPanel.GetMaxSize())
		self.Refresh()
	
	def OnSelect(self, event):
		if self.IsModal():
			self.EndModal(wx.ID_ADD)
		else:
			self.Destroy()
	
	def OnCancel(self, event):
		if self.IsModal():
			self.EndModal(wx.ID_CANCEL)
		else:
			self.Destroy()
	
	def GetSelection(self):
		return self.CalibreSearchPanel.GetSelection()
	


# end of class CalibreSearchDialog
