#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  properties.py
#
#  This file is part of GunShotMatch
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import decimal
import statistics

# 3rd party
import wx
import wx.propgrid
from mathematical.utils import rounders

# this package
from GuiV2 import CalibreSearch
from GuiV2.GSMatch2_Core.InfoProperties.dialogs import MeasurementDialog
from GuiV2.GSMatch2_Core.InfoProperties.editors import MeasurementEditor


class RangeProperty(wx.propgrid.PGProperty):
	def __init__(
			self, label, name=wx.propgrid.PG_LABEL,
			value=(0, 0), start_label="Start", end_label="End",
			):
		
		wx.propgrid.PGProperty.__init__(self, label, name)
		
		# value = self._ConvertValue(value)
		
		self.AddPrivateChild(wx.propgrid.FloatProperty(start_label, value=value[0]))
		self.AddPrivateChild(wx.propgrid.FloatProperty(end_label, value=value[1]))
		
		self.m_value = value
	
	def GetClassName(self):
		return self.__class__.__name__
	
	def DoGetEditorClass(self):
		return wx.propgrid.PropertyGridInterface.GetEditorByName("TextCtrl")
	
	def RefreshChildren(self):
		target_range = self.m_value
		self.Item(0).SetValue(target_range[0])
		self.Item(1).SetValue(target_range[1])
	
	def ChildChanged(self, thisValue, childIndex, childValue):
		the_range = self.m_value
		if childIndex == 0:
			the_range[0] = childValue
		elif childIndex == 1:
			the_range[1] = childValue
		else:
			raise AssertionError
		
		return the_range


class RTRange(RangeProperty):
	def __init__(self, label, name=wx.propgrid.PG_LABEL, value=(0, 0)):
		RangeProperty.__init__(self, label, name, value, "Start Time (minutes)", "End Time (minutes)")


class MassRange(RangeProperty):
	def __init__(self, label, name=wx.propgrid.PG_LABEL, value=(0, 0)):
		RangeProperty.__init__(self, label, name, value, "Minimum Mass (m/z)", "Maximum Mass (m/z)")


class MeasurementProperty(wx.propgrid.LongStringProperty):
	"""
	Property to represent a series of measurements.
	The value shows the mean, standard deviation, number of counts and range of the data.
	The value cannot be edited directly, rather the button must be clicked to open the editor dialog
	"""
	
	def __init__(self, label=wx.propgrid.PG_LABEL, name=wx.propgrid.PG_LABEL, value=None, decimal_places=-1):
		"""

		:param label:
		:type label:
		:param name:
		:type name:
		:param value: A list of measurement values
		:type value:
		"""
		
		self.decimal_places = decimal_places
		
		if value is None:
			value = []
		
		if isinstance(value, (int, float)):
			value = [value]
		elif isinstance(value, str):
			value = [decimal.Decimal(value)]
		
		value = [decimal.Decimal(x) for x in value]
		
		self.CalculateStatistics(value)
		
		wx.propgrid.LongStringProperty.__init__(self, label, name, self.StringValue)
		self.SetValue(self.StringValue)
		
		# Register Editor
		try:
			wx.propgrid.PropertyGridInterface.RegisterEditor(self, MeasurementEditor)
		except wx.wxAssertionError:
			pass
	
	def CalculateStatistics(self, values):
		# Calculate Mean, Stdev, Range and n
		
		self.values = values[:]
		
		# Calculate Mean, Stdev, Range and n
		self.n = len(values)
		
		if self.n == 0:
			self.mean = 0
			self.stdev = 0
		elif self.n == 1:
			self.mean = values[0]
			self.stdev = values[0]
		else:
			self.mean = statistics.mean(values)
			self.stdev = statistics.stdev(values)
	
		# TODO: range
	
	@property
	def StringValue(self):
		return f"x̄ = {rounders(self.mean, '0.000')}, σ = {rounders(self.stdev, '0.00000')}, n = {self.n}"
	
	def GetValue(self):
		return [str(x) for x in self.values]
	
	def GetClassName(self):
		"""
		This is not 100% necessary and in future is probably going to be
		automated to return class name.
		"""
		return "MeasurementProperty"
	
	def DoGetEditorClass(self):
		return wx.propgrid.PropertyGridInterface.GetEditorByName("MeasurementEditor")
	
	def GetDisplayedCommonValueCount(self):
		return 0
	
	def OnButtonClick(self, propGrid, value):
		"""
		Create dialog dlg at dlgPos. Use value as initial string value.
		"""
		
		with MeasurementDialog(
				parent=None,
				values=self.values,
				title=self.GetLabel(),
				size=(250, -1),
				decimal_places=self.decimal_places
				) as dlg:
			if dlg.ShowModal() == wx.ID_OK:
				self.CalculateStatistics(dlg.GetValues())
				return True, self.StringValue
			
			return False, self.StringValue


class CalibreProperty(wx.propgrid.LongStringProperty):
	def __init__(self, label=wx.propgrid.PG_LABEL, name=wx.propgrid.PG_LABEL, value=""):
		wx.propgrid.LongStringProperty.__init__(self, label, name, value)
		self.SetValue(value)
	
	def GetClassName(self):
		"""
		This is not 100% necessary and in future is probably going to be
		automated to return class name.
		"""
		return "CalibreProperty"
	
	def GetDisplayedCommonValueCount(self):
		return 0
	
	def OnButtonClick(self, propGrid, value):
		# Create dialog dlg at dlgPos. Use value as initial string value.
		# with CalibreSearch.SearchDialog(None, pos=dlgPos) as dlg:
		with CalibreSearch.SearchDialog(None) as dlg:
			if dlg.ShowModal() == wx.ID_ADD:
				return True, dlg.GetSelection()
			
			return False, value


class ComboBoxProperty(wx.propgrid.EditEnumProperty):
	
	def __init__(
			self, label=wx.propgrid.PG_LABEL, name=wx.propgrid.PG_LABEL,
			labels=None, values=None, value=""):
		
		if labels is None:
			labels = []
		
		if values is None:
			values = []
		
		wx.propgrid.EditEnumProperty.__init__(self, label, name, labels, values, value)
		self.SetValue(value)
	
		# Register Editor
		# wx.propgrid.PropertyGridInterface.RegisterEditor(self, ComboBoxEditor)
	
	def GetClassName(self):
		"""
		This is not 100% necessary and in future is probably going to be
		automated to return class name.
		"""
		return "ComboBoxProperty"
	
	def DoGetEditorClass(self):
		
		return wx.propgrid.PropertyGridInterface.GetEditorByName("ComboBoxEditor")
	
	def GetDisplayedCommonValueCount(self):
		return 0
