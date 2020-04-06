#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
#  ExperimentSorterPanel.py
"""
wx.Panel for the New Project Dialog containing a wx.ListCtrl
	that can be sorted by clicking the column headers
"""
#
#  This file is part of GunShotMatch
#
#  Copyright © 2019-2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
# generated by wxGlade 0.9.3 on Sun Dec  1 10:22:25 2019
#
#

# 3rd party
import wx
from wx.lib.mixins.listctrl import ColumnSorterMixin


# begin wxGlade: dependencies
# end wxGlade
# begin wxGlade: extracode
# end wxGlade


class ExperimentSorterPanel(wx.Panel, ColumnSorterMixin):
	def __init__(self, *args, **kwds):
		# begin wxGlade: ExperimentSorterPanel.__init__
		kwds["style"] = kwds.get("style", 0) | wx.TAB_TRAVERSAL
		wx.Panel.__init__(self, *args, **kwds)
		self.expr_list = wx.ListCtrl(self, wx.ID_ANY, style=wx.BORDER_DEFAULT | wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)

		self.__set_properties()
		self.__do_layout()
		# end wxGlade
		self._itemDataMap = {}
		self.default_column_headers = ["Name", "Filename", "Original Filename", "Original Filetype", "Date", "User"]

	def __set_properties(self):
		# begin wxGlade: ExperimentSorterPanel.__set_properties
		self.expr_list.AppendColumn(u"Name ⭡", format=wx.LIST_FORMAT_LEFT, width=200)
		self.expr_list.AppendColumn("Filename", format=wx.LIST_FORMAT_LEFT, width=400)
		self.expr_list.AppendColumn("Original Filename", format=wx.LIST_FORMAT_LEFT, width=400)
		self.expr_list.AppendColumn("Original Filetype", format=wx.LIST_FORMAT_LEFT, width=150)
		self.expr_list.AppendColumn("Date Created", format=wx.LIST_FORMAT_LEFT, width=150)
		self.expr_list.AppendColumn("User", format=wx.LIST_FORMAT_LEFT, width=150)
		# end wxGlade

	def __do_layout(self):
		# begin wxGlade: ExperimentSorterPanel.__do_layout
		expr_list_sizer = wx.GridSizer(1, 1, 0, 0)
		expr_list_sizer.Add(self.expr_list, 1, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.LEFT | wx.TOP, 5)
		self.SetSizer(expr_list_sizer)
		expr_list_sizer.Fit(self)
		self.Layout()
		# end wxGlade
	
	@property
	def itemDataMap(self):
		return self._itemDataMap
	
	@itemDataMap.setter
	def itemDataMap(self, value):
		if self._itemDataMap == {}:
			self._itemDataMap = value
			ColumnSorterMixin.__init__(self, 6)
			self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick, self.expr_list)
		else:
			self._itemDataMap = value
	
	def GetListCtrl(self):
		return self.expr_list
	
	def OnColClick(self, event):
		"""
		Handler for clicking column header
		"""
		print("Header clicked")

		sorted_col_idx, ascending = self.GetSortState()
		ascending = bool(ascending)
		# print(sorted_col_idx, ascending)
		
		for col_idx, col_label in enumerate(self.default_column_headers):
			header = self.expr_list.GetColumn(col_idx)
			# print(header.GetText())
			
			if col_idx == sorted_col_idx:
				header.SetText(f"{col_label} {'⭡' if ascending else '⭣'}")
			else:
				header.SetText(f"{col_label}")
			self.expr_list.SetColumn(col_idx, header)

# end of class ExperimentSorterPanel
