# -*- coding: UTF-8 -*-

#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  filename.py
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2020  Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
# generated by wxGlade 0.9.3 on Tue Jan 14 13:09:20 2020
#

# stdlib
from decimal import Decimal

# 3rd party
import wx
from domdf_wxpython_tools import FloatValidator
from mathematical.utils import rounders


# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class CalibreMeasurementPanel(wx.Panel):
	def __init__(
			self, parent, label, value='', id=wx.ID_ANY,
			pos=wx.DefaultPosition, size=wx.DefaultSize,
			style=wx.TAB_TRAVERSAL, name=wx.PanelNameStr
			):
		args = (parent, id, pos, size)
		kwds = {
				"style": style,
				"name": name,
				}
		
		self.label = label
		if value:
			self.value = Decimal(value)
		else:
			self.value = ''
		
		# begin wxGlade: CalibreMeasurementPanel.__init__
		kwds["style"] = kwds.get("style", 0) | wx.TAB_TRAVERSAL
		wx.Panel.__init__(self, *args, **kwds)
		self.metric_value = wx.TextCtrl(self, wx.ID_ANY, "")
		self.inches_value = wx.TextCtrl(self, wx.ID_ANY, "")

		self.__set_properties()
		self.__do_layout()

		self.Bind(wx.EVT_TEXT, self.on_metric_change, self.metric_value)
		self.Bind(wx.EVT_TEXT_ENTER, self.on_metric_change, self.metric_value)
		self.Bind(wx.EVT_TEXT, self.on_inches_change, self.inches_value)
		self.Bind(wx.EVT_TEXT_ENTER, self.on_inches_change, self.inches_value)
		# end wxGlade
		
		self.set_label(self.label)
		if self.value:
			self.metric_value.SetValue(str(rounders(self.value, "0.0000")))
	
	def __set_properties(self):
		# begin wxGlade: CalibreMeasurementPanel.__set_properties
		self.metric_value.SetMinSize((128, -1))
		self.metric_value.SetValidator(FloatValidator(4))
		self.inches_value.SetMinSize((128, -1))
		self.inches_value.SetValidator(FloatValidator(3))
		# end wxGlade


	def __do_layout(self):
		# begin wxGlade: CalibreMeasurementPanel.__do_layout
		self.staticbox_sizer = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, ""), wx.VERTICAL)
		grid = wx.FlexGridSizer(2, 2, 5, 2)
		grid.Add(self.metric_value, 1, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)
		metric_label = wx.StaticText(self, wx.ID_ANY, "mm")
		grid.Add(metric_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		grid.Add(self.inches_value, 1, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)
		inches_label = wx.StaticText(self, wx.ID_ANY, "inches")
		grid.Add(inches_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		self.staticbox_sizer.Add(grid, 1, wx.ALL | wx.EXPAND, 3)
		self.SetSizer(self.staticbox_sizer)
		self.staticbox_sizer.Fit(self)
		self.Layout()
		# end wxGlade
	
	def set_label(self, label):
		self.staticbox_sizer.StaticBox.SetLabel(label)
	
	def __dict__(self):
		return {
				"name": self.label,
				"value": self.value,
				}
	
	def on_metric_change(self, event):  # wxGlade: CalibreMeasurementPanel.<event_handler>
		value = self.metric_value.GetValue()

		if value == ".":
			self.metric_value.ChangeValue("0.")
			wx.CallAfter(self.metric_value.SetInsertionPointEnd)
			pass
		elif value:
			self.value = str(rounders(value, "0.0000"))
			self.inches_value.ChangeValue(inch(self.value))
		else:
			self.value = ''
			self.inches_value.ChangeValue('')
		event.Skip()
		
	def on_inches_change(self, event):  # wxGlade: CalibreMeasurementPanel.<event_handler>
		value = self.inches_value.GetValue()
		
		if value == ".":
			self.inches_value.ChangeValue("0.")
			wx.CallAfter(self.inches_value.SetInsertionPointEnd)
			pass
		elif value:
			self.value = mm(str(rounders(value, "0.000")))
		else:
			self.value = ''
		self.metric_value.ChangeValue(self.value)
		event.Skip()
	
	def SetValue(self, value):
		self.value = value
		if self.value:
			self.metric_value.SetValue(str(rounders(self.value, "0.0000")))
		else:
			self.metric_value.ChangeValue('')
			self.inches_value.ChangeValue('')
	
	def Clear(self):
		self.metric_value.ChangeValue('')
		self.inches_value.ChangeValue('')
	
	def GetValue(self):
		return self.value
	
	def SetEditable(self, editable=True):
		self.metric_value.SetEditable(editable)
		self.inches_value.SetEditable(editable)
		
	def IsEditable(self):
		return self.metric_value.IsEditable() and self.inches_value.IsEditable()
		
# end of class CalibreMeasurementPanel


_conversion_factor = Decimal("25.4")

def inch(mm):
	return str(rounders(Decimal(mm) / _conversion_factor, "0.000"))


def mm(inch):
	return str(rounders(Decimal(inch) * _conversion_factor, "0.0000"))


