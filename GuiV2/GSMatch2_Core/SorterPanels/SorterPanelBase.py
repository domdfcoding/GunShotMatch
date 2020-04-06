#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  SorterPanelBase.py
#
"""
wx.Panel containing a wx.ListCtrl that can be sorted by clicking the column headers
"""
#
#  This file is part of GunShotMatch
#
#  Copyright © 2019-2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  ColSelectMixin based on wx.lib.mixins.listctrl.TextEditMixin
#  © 2001-2018 by Total Control Software
#  Licensed under the wxWindows license
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
from bisect import bisect
import locale

# 3rd party
import wx
from wx.lib.mixins.listctrl import ColumnSorterMixin


# begin wxGlade: dependencies
# end wxGlade
# begin wxGlade: extracode
# end wxGlade

EVT_SORTER_PANEL_DCLICK = wx.NewEventType()
myEVT_SORTER_PANEL_DCLICK = wx.PyEventBinder(EVT_SORTER_PANEL_DCLICK, 1)
EVT_SORTER_PANEL_RCLICK = wx.NewEventType()
myEVT_SORTER_PANEL_RCLICK = wx.PyEventBinder(EVT_SORTER_PANEL_RCLICK, 1)


# TODO: Right click menu does not appear under wxMSW, and clicking header to sort columns results in an error.

class ColSelectMixin:
	"""
	A mixin class that triggers an EVT_DCLICK event whenever the control is double clicked, and allows the indices of the selected row and column to be accessed with the method 'GetDoubleClickedCell'
	
	To use the mixin you have to include it in the class definition
	and call the __init__ function::

	class TestListCtrl(wx.ListCtrl, ColSelectMixin):
		def __init__(self, parent, ID, pos=wx.DefaultPosition,
					size=wx.DefaultSize, style=0):
			wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
			ColSelectMixin.__init__(self)

	Authors:     Steve Zatz, Pim Van Heuven (pim@think-wize.com), Dominic Davis-Foster
	"""
	
	def __init__(self):
		
		self.OnLeftClick()
		
		self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftClick)
		if wx.Platform == "__WXGTK__":
			self.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)
		elif wx.Platform == "__WXMSW__":
			self.Parent.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnRightClick, self)
		self.Bind(wx.EVT_LEFT_DCLICK, self.OnDoubleClick)
	
	def OnLeftClick(self, event=None):
		
		self.curRow = 0
		self.curCol = 0
		if event:
			event.Skip()
	
	def OnDoubleClick(self, event):
		"""
		Examine the double click events to see if a row has been click on twice.
		If so, determine the current row and column and open the editor.
		"""
		print("On Double Click")
		x, y = event.GetPosition()
		row, flags = self.HitTest((x, y))
		
		# the following should really be done in the mixin's init but
		# the wx.ListCtrl demo creates the columns after creating the
		# ListCtrl (generally not a good idea) on the other hand,
		# doing this here handles adjustable column widths
		
		self.col_locs = [0]
		loc = 0
		for n in range(self.GetColumnCount()):
			loc = loc + self.GetColumnWidth(n)
			self.col_locs.append(loc)
		
		col = bisect(self.col_locs, x + self.GetScrollPos(wx.HORIZONTAL)) - 1
		
		self.curRow = row
		self.curCol = col
		
		wx.PostEvent(self, wx.PyCommandEvent(EVT_SORTER_PANEL_DCLICK, -1))
		
		event.Skip()
	
	def OnRightClick(self, event):
		"""
		Determine the current row and column
		"""
		print("Right Click")
		if wx.Platform == "__WXMSW__":
			x, y = wx.GetMousePosition()
		elif wx.Platform == "__WXGTK__":
			x, y = event.GetPosition()
		else:
			raise NotImplementedError
		
		row, flags = self.HitTest((x, y))
			
		
		# the following should really be done in the mixin's init but
		# the wx.ListCtrl demo creates the columns after creating the
		# ListCtrl (generally not a good idea) on the other hand,
		# doing this here handles adjustable column widths
		
		self.col_locs = [0]
		loc = 0
		for n in range(self.GetColumnCount()):
			loc = loc + self.GetColumnWidth(n)
			self.col_locs.append(loc)
		
		col = bisect(self.col_locs, x + self.GetScrollPos(wx.HORIZONTAL)) - 1

		self.curRow = row
		self.curCol = col
		
		wx.PostEvent(self, wx.PyCommandEvent(EVT_SORTER_PANEL_RCLICK, -1))
		
		event.Skip()
		
	def GetDoubleClickedCell(self):
		"""
		Returns the row and column index of the double clicked cell
		
		:return:
		:rtype: typle
		"""
		return self.curRow, self.curCol


class ColSelectListCtrl(wx.ListCtrl, ColSelectMixin):
	def __init__(
			self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
			style=wx.TAB_TRAVERSAL | wx.BORDER_DEFAULT | wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES,
			validator=wx.DefaultValidator, name=wx.ListCtrlNameStr
			):
		
		wx.ListCtrl.__init__(self, parent, id, pos, size, style, validator, name)
		ColSelectMixin.__init__(self)


class SorterPanel(wx.Panel, ColumnSorterMixin):
	def __init__(
			self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
			style=wx.TAB_TRAVERSAL | wx.BORDER_DEFAULT | wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES | wx.LC_SINGLE_SEL,
			validator=wx.DefaultValidator, name=wx.ListCtrlNameStr
			):
		
		wx.Panel.__init__(self, parent, id, pos, size, )
		
		self.listCtrl = ColSelectListCtrl(self, id, pos, size, style, validator, name)
		
		listCtrl_sizer = wx.GridSizer(1, 1, 0, 0)
		listCtrl_sizer.Add(self.listCtrl, 1, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.LEFT | wx.TOP, 5)
		self.SetSizer(listCtrl_sizer)
		listCtrl_sizer.Fit(self)
		self.Layout()
		
		self.itemDataMap = {}
		
		ColumnSorterMixin.__init__(self, 0)
		
		self.default_column_headers = []
		
		self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick, self.listCtrl)
	
	def Append(self, entry):
		"""
		Append an item to the list control. The entry parameter should be a sequence with an item for each column

		:param entry:
		:type entry:

		:return:
		:rtype:
		"""
		
		if len(entry):
			pos = self.listCtrl.InsertItem(self.GetItemCount(), str(entry[0]))
			for i in range(1, len(entry)):
				self.listCtrl.SetItem(pos, i, str(entry[i]))
			
			self.itemDataMap[self.GetItemCount() - 1] = [x for x in entry]
			self.listCtrl.SetItemData(self.GetItemCount() - 1, self.GetItemCount() - 1)

			return pos
	
	def AppendColumn(self, heading, format=wx.LIST_FORMAT_LEFT, width=-1):
		"""
		Adds a new column to the list control in report view mode.

		This is just a convenient wrapper for InsertColumn which adds the new
		column after all the existing ones without having to specify its
		position explicitly.

		:param heading:
		:type heading: str
		:param format:
		:type format: wx.ListColumnFormat
		:param width:
		:type width: int
		
		:return:
		:rtype: int
		"""
		
		self.default_column_headers.append(heading)
		self.SetColumnCount(self.GetColumnCount() + 1)
		return self.listCtrl.AppendColumn(f"{heading}  ", format, width)
	
	def ClearAll(self):
		"""
		Deletes all items and all columns.

		Note This sends an event of type wxEVT_LIST_DELETE_ALL_ITEMS under all platforms.
		
		:return:
		:rtype:
		"""
		
		return self.listCtrl.ClearAll()
	
	def DeleteAllColumns(self):
		"""
		Delete all columns in the list control.

		:return: True if all columns were successfully deleted, False otherwise.
		:rtype: bool
		"""
		
		return self.listCtrl.DeleteAllColumns()
	
	def DeleteAllItems(self):
		"""
		Deletes all items in the list control.

		This function does not send the wxEVT_LIST_DELETE_ITEM event because
		deleting many items from the control would be too slow then (unlike
		wx.ListCtrl.DeleteItem ) but it does send the special
		wxEVT_LIST_DELETE_ALL_ITEMS event if the control was not empty. If it
		was already empty, nothing is done and no event is sent.

		:return: True if the items were successfully deleted or if the control
			was already empty, False if an error occurred while deleting the items.
		:rtype: bool
		"""
		
		return self.listCtrl.DeleteAllItems()
	
	def DeleteColum(self, col):
		"""
		Deletes a column
		
		:param col:
		:type col: int
		
		:return:
		:rtype: bool
		"""
		
		return self.listCtrl.DeleteColumn(col)
	
	def DeleteItem(self, item):
		"""
		Deletes the specified item.
		
		This function sends the wxEVT_LIST_DELETE_ITEM event for the item being deleted.

		:param item:
		:type item: int
		
		:return:
		:rtype: bool
		"""
		
		return self.listCtrl.DeleteItem(item)
	
	def EnableAlternateRowColours(self, enable=True):
		"""
		Enable alternating row background colours (also called zebra striping).

		This method can only be called for the control in virtual report mode, i.e. having LC_REPORT and LC_VIRTUAL styles.
		
		When enabling alternating colours, the appropriate colour for the even rows is chosen automatically depending on the default foreground and background colours which are used for the odd rows.

		:param enable: If True, enable alternating row background colours, i.e. different colours for the odd and even rows. If False, disable this feature and use the same background colour for all rows.
		:type enable: bool
		
		:return:
		:rtype:
		"""
		
		return self.listCtrl.EnableAlternateRowColours(enable)
	
	def GetAlternateRowColour(self):
		"""
		Get the alternative row background colour.

		:return:
		:rtype: wx.Colour
		"""
		
		return self.listCtrl.GetAlternateRowColour()
	
	def GetColumn(self, col):
		"""
		Gets information about this column. See SetItem() for more information.
		
		:param col:
		:type col: wx.ListItem
		
		:return:
		:rtype:
		"""
		
		return self.listCtrl.GetColumn(col)
	
	def GetColumnCount(self):
		"""
		Returns the number of columns.

		:return:
		:rtype: int
		"""
		
		return self.listCtrl.GetColumnCount()
	
	def GetColumnWidth(self, col):
		"""
		Gets the column width (report view only).

		:param col:
		:type col: int
		
		:return:
		:rtype: int
		"""
		
		return self.listCtrl.GetColumnWidth(col)
	
	def GetFirstSelected(self, *args):
		"""
		Returns the first selected item, or -1 when none is selected.
		"""
		
		return self.listCtrl.GetFirstSelected(*args)
	
	def GetFocusedItem(self, *args):
		"""
		Gets the currently focused item or -1 if none is focused.
		"""
		
		return self.listCtrl.GetFocusedItem()
	
	def GetItem(self, itemIdx, col=0):
		"""
		Gets information about the item. See SetItem() for more information.

		:param itemIdx:
		:type itemIdx:
		:param col:
		:type col:
		
		:return:
		:rtype: wx.ListItem
		"""
		
		return self.listCtrl.GetItem(itemIdx, col)
	
	def GetItemCount(self):
		"""
		Returns the number of items in the list control.

		:return:
		:rtype: int
		"""
		
		return self.listCtrl.GetItemCount()
	
	def GetItemData(self, item):
		"""
		Gets the application-defined data associated with this item.

		:param item:
		:type item: int
		
		:return:
		:rtype: int
		"""
		
		return self.listCtrl.GetItemData(item)
	
	def GetItemText(self, item, col=0):
		"""
		Gets the item text for this item.

		:param item: Item (zero-based) index.
		:type item: int
		:param col: Item column (zero-based) index. Column 0 is the default. This parameter is new in wxWidgets 2.9.1.
		:type col: int
		
		:return:
		:rtype: str
		"""
		
		return self.listCtrl.GetItemText(item, col)
	
	def GetTopItem(self):
		"""
		Gets the index of the topmost visible item when in list or report view.

		:return:
		:rtype: long
		"""
		
		return self.listCtrl.GetTopItem()
	
	# TODO: intert item and insert column
	
	def IsEmpty(self):
		"""
		Returns True if the control doesn’t currently contain any items.

		Note that the control with some columns is still considered to be empty if it has no rows.
		
		:return:
		:rtype: bool
		"""
		
		return self.listCtrl.IsEmpty()
	
	def Select(self, idx, on=1):
		"""
		Selects/deselects an item.

		:param idx:
		:type idx:
		:param on:
		:type on:
		
		:return:
		:rtype:
		"""
		
		return self.listCtrl.Select(idx, on)
	
	# TODO: rest of methods
	
	def GetListCtrl(self):
		return self.listCtrl
	
	def refresh_col_headers(self):
		sorted_col_idx, ascending = self.GetSortState()
		ascending = bool(ascending)
		
		for col_idx, col_label in enumerate(self.default_column_headers):
			header = self.listCtrl.GetColumn(col_idx)
			
			if col_idx == sorted_col_idx:
				header.SetText(f"{col_label} {'⭡' if ascending else '⭣'}")
			else:
				header.SetText(f"{col_label}  ")
			self.listCtrl.SetColumn(col_idx, header)
	
	def OnColClick(self, event):
		"""
		Handler for clicking column header
		"""
		print("Header clicked")
		
		self.refresh_col_headers()
		
	def GetDoubleClickedCell(self):
		"""
		Returns the row and column index of the double clicked cell

		:return:
		:rtype: typle
		"""
		return self.listCtrl.curRow, self.listCtrl.curCol
	
	# def SetItemData(self, item, data):
	# 	self.listCtrl.SetItemData(item, data)

	def FindItem(self, start=-1, *args, **kwargs):
		"""
		FindItem(start, str, partial=False) -> long
		FindItem(start, data) -> long
		FindItem(start, pt, direction) -> long
		
		Find an item whose label matches this string, starting from start or
		the beginning if start is -1.

		:param start:
		:type start:
		:param args:
		:type args:
		:return:
		:rtype:
		"""
		
		return self.listCtrl.FindItem(start, *args, **kwargs)
	
	def SortListItems(self, col=-1, ascending=1):
		"""
		Sort the list on demand.  Can also be used to set the sort column and order.
		"""
		
		ColumnSorterMixin.SortListItems(self, col, ascending)
		self.refresh_col_headers()

# end of class ExperimentSorterPanel


