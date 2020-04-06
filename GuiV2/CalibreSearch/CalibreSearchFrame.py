#!/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  CalibreSearchFrame.py
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

# 3rd party
import wx

# this package
from GuiV2 import CalibreSearch


class CalibreSearchFrame(wx.Frame):
	
	def __init__(
			self, parent, id=wx.ID_ANY, title="Calibre Search", pos=wx.DefaultPosition,
			style=wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN | wx.NO_FULL_REPAINT_ON_RESIZE,
			name=wx.FrameNameStr
			):
		"""
		:param parent: The window parent. This may be, and often is, None. If it is not None, the frame will be minimized when its parent is minimized and restored when it is restored (although it will still be possible to minimize
		:type parent: wx.Window
		:param id: The window identifier. It may take a value of -1 to indicate a default value.
		:type id: wx.WindowID, optional
		:param title: The caption to be displayed on the frame’s title bar.
		:type title: str, optional
		:param pos: The window position. The value DefaultPosition indicates a default position, chosen by either the windowing system or wxWidgets, depending on platform.
		:type pos: wx.Point, optional
		:param style: The window style. See wx.Frame class description.
		:type style: int, optional
		:param name: The name of the window. This parameter is used to associate a name with the item, allowing the application user to set Motif resource values for individual windows.
		:type name: str, optional
		"""
		
		wx.Frame.__init__(self, parent, id=id, title=title, pos=pos, style=style, name=name)
		
		self.CalibreSearchPanel = CalibreSearch.SearchPanel(self)
		
		self.SetSize(self.CalibreSearchPanel.GetSize())
		self.SetMinSize(self.CalibreSearchPanel.GetSize())

		grid_sizer = wx.GridSizer(1, 1, 0, 0)
		grid_sizer.Add(self.CalibreSearchPanel, 1, wx.EXPAND, 0)
		self.SetSizer(grid_sizer)
		self.Layout()
		
		self.Bind(wx.EVT_CLOSE, self.on_close_window)
		self.Bind(wx.EVT_ICONIZE, self.on_iconfiy)
		self.Bind(wx.EVT_MAXIMIZE, self.on_maximize)
		
		# self.CalibreSearchPanel.buttons.show_select_cancel_grid(False)
		# cur_min_size = self.GetMinSize()
		#
		# self.SetMinSize((cur_min_size.x, cur_min_size.y-34))
		# self.SetSize((size.x, size.y-34))
		
		# self.Centre(wx.BOTH)
		
		wx.GetApp().Bind(wx.EVT_ACTIVATE_APP, self.on_app_activate)
	
	def on_close_window(self, _):
		self.Destroy()
	
	def on_iconfiy(self, evt):
		print(f"on_iconfiy: {evt.IsIconized()}")
		evt.Skip()
	
	def on_maximize(self, evt):
		print("on_maximize")
		evt.Skip()

	def on_app_activate(self, evt):
		print(f"on_app_activate: {evt.GetActive()}")
		evt.Skip()


if __name__ == '__main__':
	class MyApp(wx.App):
		def OnInit(self):
			# For debugging
			# self.SetAssertMode(wx.PYAPP_ASSERT_DIALOG|wx.PYAPP_ASSERT_EXCEPTION)
			
			wx.SystemOptions.SetOption("mac.window-plain-transition", 1)
			self.SetAppName("Calibre Search")
			
			dialog = CalibreSearch.SearchDialog(None)
			if dialog.ShowModal() == wx.ID_ADD:
				print(dialog.GetSelection())
				print("^^^^^")
			
			frame = CalibreSearchFrame(None, title="Calibre Search Frame")
			frame.Show()
			
			return True
	
	app = MyApp(False)
	app.MainLoop()
