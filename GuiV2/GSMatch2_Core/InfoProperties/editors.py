#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  editors.py
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

# 3rd party
import wx
import wx.propgrid


class MeasurementEditor(wx.propgrid.PGTextCtrlAndButtonEditor):
	def __init__(self):
		wx.propgrid.PGTextCtrlEditor.__init__(self)
	
	def CreateControls(self, propgrid, property, pos, size):
		controls = wx.propgrid.PGTextCtrlAndButtonEditor.CreateControls(self, propgrid, property, pos, size)
		
		textctrl = controls.m_primary
		textctrl.SetEditable(False)
		
		# TODO: Show tooltip when trying to type
		
		return controls


class ComboBoxEditor(wx.propgrid.PGComboBoxEditor):
	def __init__(self):
		wx.propgrid.PGComboBoxEditor.__init__(self)
	
	def CreateControls(self, propgrid, property, pos, size):
		
		# Since it is not possible (yet) to create a read-only combo box in
		# the same sense that wxTextCtrl is read-only, simply do not create
		# the control in this case.
		
		if property.HasFlag(wx.propgrid.PG_PROP_READONLY):
			return
		
		choices = property.GetChoices()
		
		index = property.GetChoiceSelection()
		
		argFlags = 0
		
		if (not property.HasFlag(wx.propgrid.PG_PROP_READONLY)) and (not property.IsValueUnspecified()):
			argFlags |= wx.propgrid.PG_EDITABLE_VALUE
		
		defString = property.GetValueAsString(argFlags)
		
		labels = choices.GetLabels()
		
		po = wx.Point(pos)
		si = wx.Size(size)
		po.y -= 3
		si.y += 6
		
		po.x -= 3
		si.x += 6
		ctrlParent = propgrid.GetPanel()
		
		odcbFlags = wx.BORDER_NONE | wx.TE_PROCESS_ENTER
		
		# if property.HasFlag(wx.propgrid.PG_PROP_USE_DCC): #and wxDynamicCast(property, wxBoolProperty) )
		# 	odcbFlags |= wxODCB_DCLICK_CYCLES
		#
		
		# If common value specified, use appropriate index
		cmnVals = property.GetDisplayedCommonValueCount()
		if cmnVals:
			if not property.IsValueUnspecified():
				cmnVal = property.GetCommonValue()
				if cmnVal >= 0:
					index = labels.size() + cmnVal
			
			for i in range(0, cmnVals):
				labels.Add(propgrid.GetCommonValueLabel(i))
		
		cb = wx.ComboBox()
		
		cb.Create(ctrlParent, wx.ID_ANY, wx.EmptyString, po, si, labels, odcbFlags)
		
		# cb.SetButtonPosition(si.y, 0, wx.RIGHT)
		
		# cb.SetMargins(wxPG_XBEFORETEXT-1)
		
		# Set hint text
		# cb.SetHint(property.GetHintText())
		
		#  wxPGChoiceEditor_SetCustomPaintWidth( propGrid, cb,
		#                                           property->GetCommonValue() );
		
		if index >= 0 and index < cb.GetCount():
			cb.SetSelection(index)
			if defString:
				cb.SetValue(defString)
			#  else if ( !(extraStyle & wxCB_READONLY) && !defString.empty() )
			#     {
			#         propGrid->SetupTextCtrlValue(defString);
			#         cb->SetValue( defString );
			#     }
			else:
				cb.SetSelection(-1)
		
		cb.Show()
		
		return cb
		
		PGWindowList = wx.propgrid.PGComboBoxEditor.CreateControls(self, propgrid, property, pos, size)
		print(PGWindowList)
		print(PGWindowList.m_primary)
		return PGWindowList
