#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  __init__.py
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

# stdlib
import datetime
import pathlib
from decimal import Decimal
from io import BytesIO

# 3rd party
import wx
import wx.propgrid
from mathematical.utils import rounders

# this package
from GuiV2.GSMatch2_Core.InfoProperties.dialogs import MeasurementDialog
from GuiV2.GSMatch2_Core.InfoProperties.editors import ComboBoxEditor, MeasurementEditor
from GuiV2.GSMatch2_Core.InfoProperties.properties import CalibreProperty, MassRange, MeasurementProperty, RTRange
from GuiV2.GSMatch2_Core.utils import filename_only, lookup_filetype

# Valid types:
# str, int, float, datetime, longstr, dir, massrange, rtrange, CalibreProperty, Measurement

longstr = "longstring"
fixed_list = "fixed_list"


class Measurement:
	def __init__(self, decimal_places):
		self.decimal_places = decimal_places


class Property:
	def __init__(
			self, name, value, type, label=None, help=None, editable=True,
			immutable=False, decimal_format=None, dropdown_choices=None,
			):
		
		self._name = name
		self._value = value
		
		self._type = type
		self._help = help
		if label is None:
			self._label = name
		else:
			self._label = label
		self._editable = editable  # Only affects UI controls - can still change properties within the class
		self._immutable = immutable  # Prevents value from being changed at all
		self.decimal_format = decimal_format  # Format string for Decimal type
		self.dropdown_choices = dropdown_choices  # Dropdown choices for e.g. EnumProperty
		
		if self.type == bool:
			self._value = bool(self._value)
	
	@property
	def name(self):
		return self._name
	
	@property
	def label(self):
		"""
		Optional label for propgrid

		:return:
		:rtype:
		"""
		
		return self._label
	
	@property
	def value(self):
		# Special case for directories
		if self.type == dir and isinstance(self._value, pathlib.Path):
			return str(self._value)
		
		if self.type in {list, fixed_list}:
			# Special case for list
			if self._value == "---":
				# Separator in dropdown, set to empty string
				return ''
		
		return self._value
	
	@value.setter
	def value(self, value):
		if self.immutable:
			raise AttributeError("Cannot set value for Property; Property is immutable")
		
		# Special case for datetime
		if self.type == datetime:
			if isinstance(value, datetime.datetime):
				value = value.timestamp()
			elif isinstance(value, str):
				value = datetime.datetime.strptime(value, "%d/%m/%Y %H:%M:%S").timestamp()
			elif isinstance(value, (int, float)):
				pass
		
		# Special case for directories
		if self.type == dir and isinstance(value, str):
			value = pathlib.Path(value)
		
		# Special case for list:
		# Can specify value or index in list
		# TODO: Make list compatible with integers or create a new type for that
		if self.type in {list, fixed_list}:
			if isinstance(value, int):
				value = self.dropdown_choices[value]
		
		if self.type in {int, format}:
			value = int(value)
		elif self.type == float:
			value = float(value)
		
		self._value = value
	
	@property
	def type(self):
		return self._type
	
	@property
	def help(self):
		return self._help
	
	@property
	def editable(self):
		return self._editable
	
	@editable.setter
	def editable(self, value):
		self._editable = bool(value)
	
	@property
	def immutable(self):
		return self._immutable
	
	@property
	def propgrid(self):
		"""
		Returns a property for wx.propgrid.PropertyGrid
		:return:
		:rtype:
		"""
		
		if isinstance(self.type, Measurement):
			value = self.value
		else:
			value = str(self.value)
		
		arguments = dict()
		
		property_function = wx.propgrid.StringProperty
		
		# TODO: specify rounding format for floats
		if self.type == str:  # String
			if self.value is None:
				value = "Not Specified"
		
		elif self.type == longstr:  # LongString
			property_function = wx.propgrid.LongStringProperty
		
		elif self.type == datetime:  # Date and Time
			value = datetime.datetime.fromtimestamp(self.value).strftime("%d/%m/%Y %H:%M:%S")
		
		elif self.type in (int, float):
			if self.value is None:
				self.value = -1
			value = self.type(self.value)
			
			if self.type == int:  # Int
				property_function = wx.propgrid.IntProperty
			elif self.type == float:  # Float
				property_function = wx.propgrid.FloatProperty
		
		elif self.type == Decimal:
			# Decimal, displayed as a string with requested formatting
			if self.decimal_format:
				value = str(rounders(self.value, self.decimal_format))
			else:
				value = str(Decimal(self.value))
		
		elif self.type == format:  # Filetype
			value = lookup_filetype(self.value)
		
		elif self.type == dir:  # Directory
			property_function = wx.propgrid.DirProperty
		
		elif self.type in {MassRange, rtrange}:
			value = self.value
			
			if self.type == MassRange:  # Mass Range
				property_function = MassRange
			elif self.type == RTRange:  # Retention Time Range
				property_function = RTRange
		
		elif self.type in {list, fixed_list}:
			if self.editable:
				arguments = dict(
						labels=self.dropdown_choices,
						values=list(range(len(self.dropdown_choices))),
						)
				
				if self.type == list:  # EditEnumProperty
					# TODO: Finish ComboBoxProperty. wx.propgrid.EditEnumProperty will have to do for now
					property_function = wx.propgrid.EditEnumProperty
				
				elif self.type == fixed_list:  # EnumProperty
					value = self.dropdown_choices.index(self.value)
					property_function = wx.propgrid.EnumProperty
			else:
				if self.value is None:
					value = ""
		
		elif self.type == bool:
			value = bool(self.value)
			property_function = wx.propgrid.BoolProperty
		
		elif self.type == CalibreProperty:
			property_function = CalibreProperty
		
		elif isinstance(self.type, Measurement):
			property_function = MeasurementProperty
			arguments["decimal_places"] = self.type.decimal_places
		
		else:
			return NotImplemented
		
		prop = property_function(self.label, self.name, value=value, **arguments)
		
		if self.help:
			prop.SetHelpString(self.help)
		
		if self.type == bool:
			prop.SetAttribute(wx.propgrid.PG_BOOL_USE_CHECKBOX, True)
		
		return prop
	
	@property
	def tree_item(self):
		"""
		Returns a tuple containing the value of the property and the icon to use in a wx.TreeCtrl

		:return:
		:rtype:
		"""
		
		if self.name.endswith("method"):
			return filename_only(self.value), 3
		elif self.name == "Ammunition Details":
			return "Ammunition Details", 7
	
	@property
	def Path(self):
		"""
		Only for properties of type `dir`.
		Returns a pathlib.Path object representing the property

		:return:
		:rtype: pathlib.Path
		"""
		
		if self.type == dir:
			if isinstance(self.value, BytesIO):
				# Special case where the value is a BytesIO object
				self.value.seek(0)
				return self.value
			else:
				return pathlib.Path(self.value)
		else:
			return NotImplemented
	
	@property
	def filename(self):
		"""
		Only for properties of type `dir`.
		Returns just the filename of the value of the property

		:return:
		:rtype: str
		"""
		
		if self.type == dir:
			return filename_only(self.value)
		else:
			return NotImplemented
	
	def __str__(self):
		return str(self.value)
	
	def __repr__(self):
		return self.__str__()
	
	def __int__(self):
		if self.type in (int, float, datetime, format):
			return int(self.value)
		else:
			raise ValueError(f"Cannot convert Property with value '{self.value}' and type {self.type} to int")
	
	def __float__(self):
		if self.type in (int, float, datetime, format):
			return float(self.value)
		else:
			raise ValueError(f"Cannot convert Property with value '{self.value}' and type {self.type} to float")
	
	def format_time(self, strf="%d/%m/%Y %H:%M:%S"):
		if self.type == datetime:
			return datetime.datetime.fromtimestamp(self.value).strftime(strf)
		else:
			raise TypeError(f"This property does not represent a date & time. Type: {self.type}")
		

# TODO:
"""
class wxPGComboBox : public wxOwnerDrawnComboBox
{
public:

	wxPGComboBox()
		: wxOwnerDrawnComboBox()
	{
		m_dclickProcessor = NULL;
	}

	~wxPGComboBox()
	{
		if ( m_dclickProcessor )
		{
			RemoveEventHandler(m_dclickProcessor);
			delete m_dclickProcessor;
		}
	}

	bool Create(wxWindow *parent,
				wxWindowID id,
				const wxString& value,
				const wxPoint& pos,
				const wxSize& size,
				const wxArrayString& choices,
				long style = 0,
				const wxValidator& validator = wxDefaultValidator,
				const wxString& name = wxS("wxOwnerDrawnComboBox"))
	{
		if ( !wxOwnerDrawnComboBox::Create( parent,
											id,
											value,
											pos,
											size,
											choices,
											style,
											validator,
											name ) )
			return false;

		// Enabling double-click processor makes sense
		// only for wxBoolProperty.
		m_selProp = GetGrid()->GetSelection();
		wxASSERT(m_selProp);
		wxBoolProperty* boolProp = wxDynamicCast(m_selProp, wxBoolProperty);
		if ( boolProp )
		{
			m_dclickProcessor = new wxPGDoubleClickProcessor(this, boolProp);
			PushEventHandler(m_dclickProcessor);
		}

		return true;
	}

	virtual void OnDrawItem( wxDC& dc,
							 const wxRect& rect,
							 int item,
							 int flags ) const wxOVERRIDE
	{
		wxPropertyGrid* pg = GetGrid();

		// Handle hint text via super class
		if ( (flags & wxODCB_PAINTING_CONTROL) &&
			 ShouldUseHintText(flags) )
		{
			wxOwnerDrawnComboBox::OnDrawItem(dc, rect, item, flags);
		}
		else
		{
			pg->OnComboItemPaint( this, item, &dc, (wxRect&)rect, flags );
		}
	}

	virtual wxCoord OnMeasureItem( size_t item ) const wxOVERRIDE
	{
		wxPropertyGrid* pg = GetGrid();
		wxRect rect;
		rect.x = -1;
		rect.width = 0;
		pg->OnComboItemPaint( this, item, NULL, rect, 0 );
		return rect.height;
	}

	wxPropertyGrid* GetGrid() const
	{
		wxPropertyGrid* pg = wxDynamicCast(GetParent(),
										   wxPropertyGrid);
		wxASSERT(pg);
		return pg;
	}

	virtual wxCoord OnMeasureItemWidth( size_t item ) const wxOVERRIDE
	{
		wxPropertyGrid* pg = GetGrid();
		wxRect rect;
		rect.x = -1;
		rect.width = -1;
		pg->OnComboItemPaint( this, item, NULL, rect, 0 );
		return rect.width;
	}

#if defined(__WXMSW__)
#define wxPG_TEXTCTRLXADJUST3 0
#elif defined(__WXGTK__)
  #if defined(__WXGTK3__)
  #define wxPG_TEXTCTRLXADJUST3 2
  #else
  #define wxPG_TEXTCTRLXADJUST3 0
  #endif // wxGTK3/!wxGTK3
#elif defined(__WXOSX__)
#define wxPG_TEXTCTRLXADJUST3 6
#else
#define wxPG_TEXTCTRLXADJUST3 0
#endif

	virtual void PositionTextCtrl( int textCtrlXAdjust,
								   int WXUNUSED(textCtrlYAdjust) ) wxOVERRIDE
	{
	#ifdef wxPG_TEXTCTRLXADJUST
		textCtrlXAdjust = wxPG_TEXTCTRLXADJUST -
						  (wxPG_XBEFOREWIDGET+wxPG_CONTROL_MARGIN+1) - 1,
	#endif
		wxOwnerDrawnComboBox::PositionTextCtrl(
			textCtrlXAdjust + wxPG_TEXTCTRLXADJUST3,
			0
		);
	}

	wxPGProperty* GetProperty() const { return m_selProp; }

private:
	wxPGDoubleClickProcessor*   m_dclickProcessor;
	wxPGProperty*               m_selProp;
};

"""

# legacy type names
massrange = MassRange
rtrange = RTRange
calibre_type = CalibreProperty
