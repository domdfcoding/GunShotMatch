#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  custom_bitmap_button.py
#  Based on wx.lib.buttons.
#  Copyright (c) 1999-2018 by Total Control Software
#  Licenced under the wxWindows license
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

import wx
from wx.lib.buttons import GenBitmapButton


class CustomBitmapButton(GenBitmapButton):
	""" A generic bitmapped button with text label. """
	
	def __init__(
			self, parent, id=-1, bitmap=wx.NullBitmap, label='',
			pos=wx.DefaultPosition, size=wx.DefaultSize,
			style=wx.BORDER_RAISED, validator=wx.DefaultValidator,
			name="genbutton"):
		"""
		Default class constructor.

		:param wx.Window `parent`: parent window. Must not be ``None``;
		:param integer `id`: window identifier. A value of -1 indicates a default value;
		:param wx.Bitmap `bitmap`: the button bitmap;
		:param string `label`: the button text label;
		:param `pos`: the control position. A value of (-1, -1) indicates a default position,
		 chosen by either the windowing system or wxPython, depending on platform;
		:type `pos`: tuple or :class:`wx.Point`
		:param `size`: the control size. A value of (-1, -1) indicates a default size,
		 chosen by either the windowing system or wxPython, depending on platform;
		:type `size`: tuple or :class:`wx.Size`
		:param integer `style`: the button style;
		:param wx.Validator `validator`: the validator associated to the button;
		:param string `name`: the button name.

		.. seealso:: :class:`wx.Button` for a list of valid window styles.
		"""
		# TODO: Positioning of text relative to bitmap
		
		self._mouse_over = False

		GenBitmapButton.__init__(self, parent, id, bitmap, pos, size, style, validator, name)
		if style & wx.BORDER_RAISED:
			self.SetBezelWidth(0)
		self.original_style = style
		self.SetLabel(label)
		self.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEnter)
		self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)
		self._original_background_colour = self.GetBackgroundColour()
	
	def SetBackgroundColour(self, colour):
		self._original_background_colour = colour
		if not self._mouse_over:
			GenBitmapButton.SetBackgroundColour(self, colour)
	
	def OnMouseEnter(self, event):
		self._mouse_over = True
		self._original_background_colour = self.GetBackgroundColour()
		r, g, b = self._original_background_colour.Get(False)
		hover_background = wx.Colour(r + 9, g + 10, b + 10)
		GenBitmapButton.SetBackgroundColour(self, hover_background)
		
	def OnMouseLeave(self, event):
		self._mouse_over = False
		self.SetBackgroundColour(self._original_background_colour)
	
	def _GetLabelSize(self):
		""" Used internally. """
		
		w, h = self.GetTextExtent(self.GetLabel())
		if not self.bmpLabel:
			return w, h, True  # if there isn't a bitmap use the size of the text
		
		w_bmp = self.bmpLabel.GetWidth() + 2
		h_bmp = self.bmpLabel.GetHeight() + 2
		width = w + w_bmp
		if h_bmp > h:
			height = h_bmp
		else:
			height = h
		return width, height, True
	
	def DrawLabel(self, dc, width, height, dx=0, dy=0):
		bmp = self.bmpLabel
		if bmp is not None:  # if the bitmap is used
			if self.bmpDisabled and not self.IsEnabled():
				bmp = self.bmpDisabled
			if self.bmpFocus and self.hasFocus:
				bmp = self.bmpFocus
			if self.bmpSelected and not self.up:
				bmp = self.bmpSelected
			bw, bh = bmp.GetWidth(), bmp.GetHeight()
			if not self.up:
				dx = dy = self.labelDelta
			hasMask = bmp.GetMask() is not None
		else:
			bw = bh = 0  # no bitmap -> size is zero
			hasMask = False
		
		dc.SetFont(self.GetFont())
		if self.IsEnabled():
			dc.SetTextForeground(self.GetForegroundColour())
		else:
			dc.SetTextForeground(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT))
		
		label = self.GetLabel()
		tw, th = dc.GetTextExtent(label)  # size of text
		if not self.up:
			dx = dy = self.labelDelta
		
		pos_y = (width - bw - th) / 2 + dy  # adjust for bitmap and text to centre
		if bmp is not None:
			dc.DrawBitmap(bmp, (width - bw) / 2 + dx, pos_y, hasMask)  # draw bitmap if available
			pos_y = pos_y + 2  # extra spacing from bitmap
		
		dc.DrawText(label, (width - tw) / 2 + dx, pos_y + dy + bh)  # draw the text
	
	def OnGainFocus(self, event):
		"""
		Handles the ``wx.EVT_SET_FOCUS`` event for :class:`GenButton`.

		:param `event`: a :class:`wx.FocusEvent` event to be processed.
		"""
		self.SetWindowStyleFlag(wx.BORDER_DEFAULT)
		self.SetBezelWidth(1)
		self.SetUseFocusIndicator(True)
		GenBitmapButton.OnGainFocus(self, event)
	
	def OnLoseFocus(self, event):
		"""
		Handles the ``wx.EVT_KILL_FOCUS`` event for :class:`GenButton`.

		:param `event`: a :class:`wx.FocusEvent` event to be processed.
		"""
		self.SetWindowStyleFlag(self.original_style)
		self.SetUseFocusIndicator(False)
		self.SetBezelWidth(0)
		GenBitmapButton.OnLoseFocus(self, event)
	
	def DrawBezel(self, dc, x1, y1, x2, y2):
		# draw the upper left sides
		if self._mouse_over:
			dc.SetPen(wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT), 2))
		else:
			dc.SetPen(wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT), 1))
		
		for i in range(self.bezelWidth):
		
			if self._mouse_over:
				dc.DrawRoundedRectangle(1, 1, self.GetSize().x - 3, self.GetSize().y - 3, 4)
			else:
				dc.DrawRoundedRectangle(0, 0, self.GetSize().x - 2, self.GetSize().y - 2, 5)
