#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#

# From wxPython Demo.
# Licenced under the wxWindows Library Licence, Version 3.1

# stdlib
import os.path
import sys

# 3rd party
import wx
import wx.adv
from wx.propgrid import PropertyGrid

# Register custom editors
if not getattr(sys, '_PropGridEditorsRegistered', False):
	self.property_grid_1.RegisterEditor(TrivialPropertyEditor)
	self.property_grid_1.RegisterEditor(SampleMultiButtonEditor)
	self.property_grid_1.RegisterEditor(LargeImageEditor)
	# ensure we only do it once
	sys._PropGridEditorsRegistered = True


class SingleChoiceProperty(wx.propgrid.StringProperty):
	def __init__(self, label, name=wx.propgrid.PG_LABEL, value=''):
		wx.propgrid.StringProperty.__init__(self, label, name, value)

		# Prepare choices
		dialog_choices = []
		dialog_choices.append("Cat")
		dialog_choices.append("Dog")
		dialog_choices.append("Gibbon")
		dialog_choices.append("Otter")

		self.dialog_choices = dialog_choices

	def DoGetEditorClass(self):
		return wx.propgrid.PropertyGridInterface.GetEditorByName("TextCtrlAndButton")

	def GetEditorDialog(self):
		# Set what happens on button click
		return SingleChoiceDialogAdapter(self.dialog_choices)

class SingleChoiceDialogAdapter(wx.propgrid.PGEditorDialogAdapter):
	""" This demonstrates use of wx.propgrid.PGEditorDialogAdapter.
	"""
	def __init__(self, choices):
		wx.propgrid.PGEditorDialogAdapter.__init__(self)
		self.choices = choices

	def DoShowDialog(self, propGrid, property):
		s = wx.GetSingleChoice("Message", "Caption", self.choices)

		if s:
			self.SetValue(s)
			return True

		return False

class IntProperty2(wx.propgrid.PGProperty):
	"""\
	This is a simple re-implementation of wxIntProperty.
	"""
	def __init__(self, label, name = wx.propgrid.PG_LABEL, value=0):
		wx.propgrid.PGProperty.__init__(self, label, name)
		self.SetValue(value)

	def GetClassName(self):
		"""\
		This is not 100% necessary and in future is probably going to be
		automated to return class name.
		"""
		return "IntProperty2"

	def DoGetEditorClass(self):
		return wx.propgrid.PropertyGridInterface.GetEditorByName("TextCtrl")

	def ValueToString(self, value, flags):
		return str(value)

	def StringToValue(self, s, flags):
		""" If failed, return False or (False, None). If success, return tuple
			(True, newValue).
		"""
		try:
			v = int(s)
			if self.GetValue() != v:
				return (True, v)
		except (ValueError, TypeError):
			if flags & wx.propgrid.PG_REPORT_ERROR:
				wx.MessageBox("Cannot convert '%s' into a number."%s, "Error")
		return False

	def IntToValue(self, v, flags):
		""" If failed, return False or (False, None). If success, return tuple
			(True, newValue).
		"""
		if (self.GetValue() != v):
			return (True, v)
		return False

	def ValidateValue(self, value, validationInfo):
		""" Let's limit the value to range -10000 and 10000.
		"""
		# Just test this function to make sure validationInfo and
		# wx.propgridVFBFlags work properly.
		oldvfb__ = validationInfo.GetFailureBehavior()

		# Mark the cell if validation failed
		validationInfo.SetFailureBehavior(wx.propgrid.PG_VFB_MARK_CELL)

		if value < -10000 or value > 10000:
			return False

		return (True, value)



class PyObjectPropertyValue:
	"""\
	Value type of our sample PyObjectProperty. We keep a simple dash-delimited
	list of string given as argument to constructor.
	"""
	def __init__(self, s=None):
		try:
			self.ls = [a.strip() for a in s.split('-')]
		except:
			self.ls = []

	def __repr__(self):
		return ' - '.join(self.ls)


class PyObjectProperty(wx.propgrid.PGProperty):
	"""\
	Another simple example. This time our value is a PyObject.

	NOTE: We can't return an arbitrary python object in DoGetValue. It cannot
		  be a simple type such as int, bool, double, or string, nor an array
		  or wxObject based. Dictionary, None, or any user-specified Python
		  class is allowed.
	"""
	def __init__(self, label, name = wx.propgrid.PG_LABEL, value=None):
		wx.propgrid.PGProperty.__init__(self, label, name)
		self.SetValue(value)

	def GetClassName(self):
		return self.__class__.__name__

	def GetEditor(self):
		return "TextCtrl"

	def ValueToString(self, value, flags):
		return repr(value)

	def StringToValue(self, s, flags):
		""" If failed, return False or (False, None). If success, return tuple
			(True, newValue).
		"""
		v = PyObjectPropertyValue(s)
		return (True, v)


class SampleMultiButtonEditor(wx.propgrid.PGTextCtrlEditor):
	def __init__(self):
		wx.propgrid.PGTextCtrlEditor.__init__(self)

	def CreateControls(self, propGrid, property, pos, sz):
		# Create and populate buttons-subwindow
		buttons = wx.propgrid.PGMultiButton(propGrid, sz)

		# Add two regular buttons
		buttons.AddButton("...")
		buttons.AddButton("A")
		# Add a bitmap button
		buttons.AddBitmapButton(wx.ArtProvider.GetBitmap(wx.ART_FOLDER))

		# Create the 'primary' editor control (textctrl in this case)
		wnd = super(SampleMultiButtonEditor, self).CreateControls(
								   propGrid,
								   property,
								   pos,
								   buttons.GetPrimarySize())
		wnd = wnd.m_primary

		# Finally, move buttons-subwindow to correct position and make sure
		# returned wx.propgridWindowList contains our custom button list.
		buttons.Finalize(propGrid, pos);

		# We must maintain a reference to any editor objects we created
		# ourselves. Otherwise they might be freed prematurely. Also,
		# we need it in OnEvent() below, because in Python we cannot "cast"
		# result of wxPropertyGrid.GetEditorControlSecondary() into
		# PGMultiButton instance.
		self.buttons = buttons

		return wx.propgrid.PGWindowList(wnd, buttons)

	def OnEvent(self, propGrid, prop, ctrl, event):
		if event.GetEventType() == wx.wxEVT_COMMAND_BUTTON_CLICKED:
			buttons = self.buttons
			evtId = event.GetId()

			if evtId == buttons.GetButtonId(0):
				# Do something when the first button is pressed
				wx.LogDebug("First button pressed")
				return False  # Return false since value did not change
			if evtId == buttons.GetButtonId(1):
				# Do something when the second button is pressed
				wx.MessageBox("Second button pressed")
				return False  # Return false since value did not change
			if evtId == buttons.GetButtonId(2):
				# Do something when the third button is pressed
				wx.MessageBox("Third button pressed")
				return False  # Return false since value did not change

		return super(SampleMultiButtonEditor, self).OnEvent(propGrid, prop, ctrl, event)

class TrivialPropertyEditor(wx.propgrid.PGEditor):
	"""\
	This is a simple re-creation of TextCtrlWithButton. Note that it does
	not take advantage of wx.TextCtrl and wx.Button creation helper functions
	in wx.PropertyGrid.
	"""
	def __init__(self):
		wx.propgrid.PGEditor.__init__(self)

	def CreateControls(self, propgrid, property, pos, sz):
		""" Create the actual wxPython controls here for editing the
			property value.

			You must use propgrid.GetPanel() as parent for created controls.

			Return value is either single editor control or tuple of two
			editor controls, of which first is the primary one and second
			is usually a button.
		"""
		try:
			x, y = pos
			w, h = sz
			h = 64 + 6

			# Make room for button
			bw = propgrid.GetRowHeight()
			w -= bw

			s = property.GetDisplayedString();

			tc = wx.TextCtrl(propgrid.GetPanel(), wx.propgrid.PG_SUBID1, s,
							 (x,y), (w,h),
							 wx.TE_PROCESS_ENTER)
			btn = wx.Button(propgrid.GetPanel(), wx.propgrid.PG_SUBID2, '...',
							(x+w, y),
							(bw, h), wx.WANTS_CHARS)
			return wx.propgrid.PGWindowList(tc, btn)
		except:
			import traceback
			print(traceback.print_exc())

	def UpdateControl(self, property, ctrl):
		ctrl.SetValue(property.GetDisplayedString())

	def DrawValue(self, dc, rect, property, text):
		if not property.IsValueUnspecified():
			dc.DrawText(property.GetDisplayedString(), rect.x+5, rect.y)

	def OnEvent(self, propgrid, property, ctrl, event):
		""" Return True if modified editor value should be committed to
			the property. To just mark the property value modified, call
			propgrid.EditorsValueWasModified().
		"""
		if not ctrl:
			return False

		evtType = event.GetEventType()

		if evtType == wx.wxEVT_COMMAND_TEXT_ENTER:
			if propgrid.IsEditorsValueModified():
				return True
		elif evtType == wx.wxEVT_COMMAND_TEXT_UPDATED:
			#
			# Pass this event outside wxPropertyGrid so that,
			# if necessary, program can tell when user is editing
			# a textctrl.
			event.Skip()
			event.SetId(propgrid.GetId())

			propgrid.EditorsValueWasModified()
			return False

		return False

	def GetValueFromControl(self, property, ctrl):
		""" Return tuple (wasSuccess, newValue), where wasSuccess is True if
			different value was acquired successfully.
		"""
		tc = ctrl
		textVal = tc.GetValue()

		if property.UsesAutoUnspecified() and not textVal:
			return (True, None)

		res, value = property.StringToValue(textVal, wx.propgrid.PG_FULL_VALUE)

		# Changing unspecified always causes event (returning
		# True here should be enough to trigger it).
		if not res and value is None:
			res = True

		return (res, value)

	def SetValueToUnspecified(self, property, ctrl):
		ctrl.Remove(0,len(ctrl.GetValue()))

	def SetControlStringValue(self, property, ctrl, text):
		ctrl.SetValue(text)

	def OnFocus(self, property, ctrl):
		ctrl.SetSelection(-1,-1)

class LargeImageEditor(wx.propgrid.PGEditor):
	"""
	Double-height text-editor with image in front.
	"""
	def __init__(self):
		wx.propgrid.PGEditor.__init__(self)

	def CreateControls(self, propgrid, property, pos, sz):
		try:
			x, y = pos
			w, h = sz
			h = 64 + 6

			# Make room for button
			bw = propgrid.GetRowHeight()
			w -= bw

			self.property = property

			self.RefreshThumbnail()
			self.statbmp = wx.StaticBitmap(propgrid.GetPanel(), -1, self.bmp, (x,y))
			self.tc = wx.TextCtrl(propgrid.GetPanel(), -1,  "",
								  (x+h,y), (2048,h), wx.BORDER_NONE)

			btn = wx.Button(propgrid.GetPanel(), wx.propgrid.PG_SUBID2, '...',
							(x+w, y),
							(bw, h), wx.WANTS_CHARS)

			# When the textctrl is destroyed, destroy the statbmp too
			def _cleanupStatBmp(evt):
				if self.statbmp:
					self.statbmp.Destroy()
			self.tc.Bind(wx.EVT_WINDOW_DESTROY, _cleanupStatBmp)

			return wx.propgrid.PGWindowList(self.tc, btn)
		except:
			import traceback
			print(traceback.print_exc())


	def GetName(self):
		return "LargeImageEditor"


	def UpdateControl(self, property, ctrl):
		s = property.GetDisplayedString()
		self.tc.SetValue(s)
		self.RefreshThumbnail()
		self.statbmp.SetBitmap(self.bmp)


	def DrawValue(self, dc, rect, property, text):
		if not property.IsValueUnspecified():
			dc.DrawText(property.GetDisplayedString(), rect.x+5, rect.y)


	def OnEvent(self, propgrid, property, ctrl, event):
		""" Return True if modified editor value should be committed to
			the property. To just mark the property value modified, call
			propgrid.EditorsValueWasModified().
		"""
		if not ctrl:
			return False

		evtType = event.GetEventType()

		if evtType == wx.wxEVT_COMMAND_TEXT_ENTER:
			if propgrid.IsEditorsValueModified():
				return True
		elif evtType == wx.wxEVT_COMMAND_TEXT_UPDATED:
			#
			# Pass this event outside wxPropertyGrid so that,
			# if necessary, program can tell when user is editing
			# a textctrl.
			event.Skip()
			event.SetId(propgrid.GetId())

			propgrid.EditorsValueWasModified()
			return False

		return False

	def GetValueFromControl(self, property, ctrl):
		""" Return tuple (wasSuccess, newValue), where wasSuccess is True if
			different value was acquired succesfully.
		"""
		textVal = self.tc.GetValue()

		if property.UsesAutoUnspecified() and not textVal:
			return (None, True)

		res, value = property.StringToValue(textVal,
											wx.propgrid.PG_EDITABLE_VALUE)

		# Changing unspecified always causes event (returning
		# True here should be enough to trigger it).
		if not res and value is None:
			res = True

		return (res, value)


	def SetValueToUnspecified(self, property, ctrl):
		ctrl.Remove(0, len(ctrl.GetValue()))
		self.RefreshThumbnail()
		self.statbmp.SetBitmap(self.bmp)


	def SetControlStringValue(self, property, ctrl, txt):
		self.tc.SetValue(txt)
		self.RefreshThumbnail()
		self.statbmp.SetBitmap(self.bmp)


	def CanContainCustomImage(self):
		return True


	def RefreshThumbnail(self):
		"""
		We use here very simple image scaling code.
		"""
		def _makeEmptyBmp():
			bmp = wx.Bitmap(64,64)
			dc = wx.MemoryDC()
			dc.SelectObject(bmp)
			dc.SetPen(wx.Pen(wx.BLACK))
			dc.SetBrush(wx.WHITE_BRUSH)
			dc.DrawRectangle(0, 0, 64, 64)
			return bmp

		if not self.property:
			self.bmp = _makeEmptyBmp()
			return

		path = self.property.DoGetValue()

		if not os.path.isfile(path):
			self.bmp = _makeEmptyBmp()
			return

		image = wx.Image(path)
		image.Rescale(64, 64)
		self.bmp = wx.Bitmap(image)


class SizeProperty(wx.propgrid.PGProperty):
	""" Demonstrates a property with few children.
	"""
	
	def __init__(self, label, name=wx.propgrid.PG_LABEL, value=wx.Size(0, 0)):
		wx.propgrid.PGProperty.__init__(self, label, name)
		
		value = self._ConvertValue(value)
		
		self.AddPrivateChild(wx.propgrid.IntProperty("X", value=value.x))
		self.AddPrivateChild(wx.propgrid.IntProperty("Y", value=value.y))
		
		self.m_value = value
	
	def GetClassName(self):
		return self.__class__.__name__
	
	def DoGetEditorClass(self):
		return wx.propgrid.PropertyGridInterface.GetEditorByName("TextCtrl")
	
	def RefreshChildren(self):
		size = self.m_value
		self.Item(0).SetValue(size.x)
		self.Item(1).SetValue(size.y)
	
	def _ConvertValue(self, value):
		""" Utility convert arbitrary value to a real wx.Size.
		"""
		import collections
		if isinstance(value, collections.Sequence) or hasattr(value, '__getitem__'):
			value = wx.Size(*value)
		return value
	
	def ChildChanged(self, thisValue, childIndex, childValue):
		size = self._ConvertValue(self.m_value)
		if childIndex == 0:
			size.x = childValue
		elif childIndex == 1:
			size.y = childValue
		else:
			raise AssertionError
		
		return size


class DirsProperty(wx.propgrid.ArrayStringProperty):
	""" Sample of a custom custom ArrayStringProperty.

		Because currently some of the C++ helpers from wxArrayStringProperty
		and wxProperytGrid are not available, our implementation has to quite
		a bit 'manually'. Which is not too bad since Python has excellent
		string and list manipulation facilities.
	"""
	
	def __init__(self, label, name=wx.propgrid.PG_LABEL, value=None):
		if value is None:
			value = []
		wx.propgrid.ArrayStringProperty.__init__(self, label, name, value)
		self.m_display = ''
		# Set default delimiter
		self.SetAttribute("Delimiter", ',')
	
	# NOTE: In the Classic version of the propgrid classes, all of the wrapped
	# property classes override DoGetEditorClass so it calls GetEditor and
	# looks up the class using that name, and hides DoGetEditorClass from the
	# usable API. Jumping through those hoops is no longer needed in Phoenix
	# as Phoenix allows overriding all necessary virtual methods without
	# special support in the wrapper code, so we just need to override
	# DoGetEditorClass here instead.
	def DoGetEditorClass(self):
		return wx.propgrid.PropertyGridInterface.GetEditorByName("TextCtrlAndButton")
	
	def ValueToString(self, value, flags):
		# let's just use the cached display value
		return self.m_display
	
	def OnSetValue(self):
		self.GenerateValueAsString()
	
	def DoSetAttribute(self, name, value):
		retval = super(DirsProperty, self).DoSetAttribute(name, value)
		
		# Must re-generate cached string when delimiter changes
		if name == "Delimiter":
			self.GenerateValueAsString(delim=value)
		
		return retval
	
	def GenerateValueAsString(self, delim=None):
		""" This function creates a cached version of displayed text
			(self.m_display).
		"""
		if not delim:
			delim = self.GetAttribute("Delimiter")
			if not delim:
				delim = ','
		
		ls = self.GetValue()
		if delim == '"' or delim == "'":
			text = ' '.join(['%s%s%s' % (delim, a, delim) for a in ls])
		else:
			text = ', '.join(ls)
		self.m_display = text
	
	def StringToValue(self, text, argFlags):
		""" If failed, return False or (False, None). If success, return tuple
			(True, newValue).
		"""
		delim = self.GetAttribute("Delimiter")
		if delim == '"' or delim == "'":
			# Proper way to call same method from super class
			return super(DirsProperty, self).StringToValue(text, 0)
		v = [a.strip() for a in text.split(delim)]
		return (True, v)
	
	def OnEvent(self, propgrid, primaryEditor, event):
		if event.GetEventType() == wx.wxEVT_COMMAND_BUTTON_CLICKED:
			dlg = wx.DirDialog(propgrid,
							   _("Select a directory to be added to "
								 "the list:"))
			
			if dlg.ShowModal() == wx.ID_OK:
				new_path = dlg.GetPath()
				old_value = self.m_value
				if old_value:
					new_value = list(old_value)
					new_value.append(new_path)
				else:
					new_value = [new_path]
				self.SetValueInEvent(new_value)
				retval = True
			else:
				retval = False
			
			dlg.Destroy()
			return retval
		
		return False


# Example Password
sp = self.property_grid_1.Append(wx.propgrid.StringProperty('StringProperty_as_Password', value='ABadPassword'))
sp.SetAttribute('Hint', 'This is a hint')
sp.SetAttribute('Password', True)

# Examples of lists, dropdowns and multiple choice
self.property_grid_1.Append(wx.propgrid.ArrayStringProperty("ArrayString", value=['A', 'B', 'C']))
self.property_grid_1.Append(wx.propgrid.EnumProperty("Enum", "Enum",
											  ['wxPython Rules',
											   'wxPython Rocks',
											   'wxPython Is The Best'],
											  [10, 11, 12],
											  0))
self.property_grid_1.Append(wx.propgrid.EditEnumProperty("EditEnum", "EditEnumProperty",
												  ['A', 'B', 'C'],
												  [0, 1, 2],
												  "Text Not in List"))
self.property_grid_1.Append(wx.propgrid.MultiChoiceProperty("MultiChoice",
													 choices=['wxWidgets', 'QT', 'GTK+']))
self.property_grid_1.Append(SingleChoiceProperty("SingleChoiceProperty"))

# Example of date picker
self.property_grid_1.Append(wx.propgrid.DateProperty("Date", value=wx.DateTime.Now()))
self.property_grid_1.SetPropertyAttribute("Date", wx.propgrid.PG_DATE_PICKER_STYLE,
										  wx.adv.DP_DROPDOWN | wx.adv.DP_SHOWCENTURY)

# Examples of font and colour
self.property_grid_1.Append(wx.propgrid.FontProperty("Font", value=self.GetFont()))
self.property_grid_1.Append(wx.propgrid.ColourProperty("Colour",
												value=self.GetBackgroundColour()))
self.property_grid_1.Append(wx.propgrid.SystemColourProperty("SystemColour"))

# Examples of choosing images
self.property_grid_1.Append(wx.propgrid.ImageFileProperty("ImageFile"))
self.property_grid_1.Append(wx.propgrid.ImageFileProperty("ImageFileWithLargeEditor"))
self.property_grid_1.SetPropertyEditor("ImageFileWithLargeEditor", "LargeImageEditor")

# Don't know what these do
# pg.Append( wx.propgrid.PointProperty("Point",value=panel.GetPosition()) )
# pg.Append( wx.propgrid.FontDataProperty("FontData") )
# prop = self.property_grid_1.Append(wx.propgrid.StringProperty("StringWithCustomEditor",
# Doesn't render properly							   value="test value"))
# self.property_grid_1.SetPropertyEditor(prop, "TrivialPropertyEditor")
# self.property_grid_1.Append(IntProperty2("IntProperty2", value=1024))
# self.property_grid_1.Append(PyObjectProperty("PyObjectProperty"))

# Example of text field with three buttons
self.property_grid_1.Append(wx.propgrid.LongStringProperty("MultipleButtons"))
self.property_grid_1.SetPropertyEditor("MultipleButtons", "SampleMultiButtonEditor")

# Examples of int, float, bool and checkbox
self.property_grid_1.Append(wx.propgrid.IntProperty("Int", value=100))
self.fprop = self.property_grid_1.Append(wx.propgrid.FloatProperty("Float", value=123.456))
self.property_grid_1.Append(wx.propgrid.BoolProperty("Bool", value=True))
boolprop = self.property_grid_1.Append(wx.propgrid.BoolProperty("Bool_with_Checkbox", value=True))
self.property_grid_1.SetPropertyAttribute(
	"Bool_with_Checkbox",  # You can find the property by name,
	# boolprop,               # or give the property object itself.
	"UseCheckbox", True)  # The attribute name and value
self.property_grid_1.Append(wx.propgrid.IntProperty("IntWithSpin", value=256))
self.property_grid_1.SetPropertyEditor("IntWithSpin", "SpinCtrl")
# Doesn't render properly
self.property_grid_1.Append(SizeProperty("Size", value=self.GetSize()))

# Examples of files and directories
self.property_grid_1.Append(wx.propgrid.DirProperty("Dir", value=r"C:\Windows"))
self.property_grid_1.Append(wx.propgrid.FileProperty("File", value=r"C:\Windows\system.ini"))
self.property_grid_1.SetPropertyAttribute("File", wx.propgrid.PG_FILE_SHOW_FULL_PATH, 0)
self.property_grid_1.SetPropertyAttribute(
	"File", wx.propgrid.PG_FILE_INITIAL_PATH,
	r"C:\Program Files\Internet Explorer"
)
self.property_grid_1.Append(DirsProperty("Dirs1", value=['C:/Lib', 'C:/Bin']))
self.property_grid_1.Append(DirsProperty("Dirs2", value=['/lib', '/bin']))
self.property_grid_1.SetPropertyAttribute("Dirs2", "Delimiter", '"')
