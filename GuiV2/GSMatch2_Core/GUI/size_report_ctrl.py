#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  size_report_ctrl.py
#
#  This file is part of GunShotMatch
#
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

# 3rd party
import wx
import wx.grid
import wx.html

# this package


# -- wx.SizeReportCtrl --
# (a utility control that always reports it's client size)

class SizeReportCtrl(wx.Control):

	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
				 size=wx.DefaultSize, mgr=None):

		wx.Control.__init__(self, parent, id, pos, size, wx.NO_BORDER)

		self._mgr = mgr

		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)


	def OnPaint(self, event):

		dc = wx.PaintDC(self)

		size = self.GetClientSize()
		s = ("Size: %d x %d")%(size.x, size.y)

		dc.SetFont(wx.NORMAL_FONT)
		w, height = dc.GetTextExtent(s)
		height = height + 3
		dc.SetBrush(wx.WHITE_BRUSH)
		dc.SetPen(wx.WHITE_PEN)
		dc.DrawRectangle(0, 0, size.x, size.y)
		dc.SetPen(wx.LIGHT_GREY_PEN)
		dc.DrawLine(0, 0, size.x, size.y)
		dc.DrawLine(0, size.y, size.x, 0)
		dc.DrawText(s, (size.x-w)/2, ((size.y-(height*5))/2))

		if self._mgr:

			pi = self._mgr.GetPane(self)

			s = ("Layer: %d")%pi.dock_layer
			w, h = dc.GetTextExtent(s)
			dc.DrawText(s, (size.x-w)/2, ((size.y-(height*5))/2)+(height*1))

			s = ("Dock: %d Row: %d")%(pi.dock_direction, pi.dock_row)
			w, h = dc.GetTextExtent(s)
			dc.DrawText(s, (size.x-w)/2, ((size.y-(height*5))/2)+(height*2))

			s = ("Position: %d")%pi.dock_pos
			w, h = dc.GetTextExtent(s)
			dc.DrawText(s, (size.x-w)/2, ((size.y-(height*5))/2)+(height*3))

			s = ("Proportion: %d")%pi.dock_proportion
			w, h = dc.GetTextExtent(s)
			dc.DrawText(s, (size.x-w)/2, ((size.y-(height*5))/2)+(height*4))


	def OnEraseBackground(self, event):
		# intentionally empty
		pass


	def OnSize(self, event):

		self.Refresh()
		event.Skip()
