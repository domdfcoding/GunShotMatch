#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  SpectrumFrame.py
#
#  This file is part of GunShotMatch
#
#  Copyright © 2019 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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

# generated by wxGlade 0.9.3 on Tue Dec 10 16:31:18 2019
#


# 3rd party
import wx
from wx import aui
# from wx.lib.agw.aui import framemanager

# this package
from GuiV2.GSMatch2_Core import Experiment
from GuiV2.GSMatch2_Core.GUI.menus import SpectrumViewerMenu
from GuiV2.GSMatch2_Core.GUI.toolbars import SpectrumViewerToolBar
from GuiV2.GSMatch2_Core.IDs import *


# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


# TODO: Finish off
class SpectrumFrame(wx.Frame):
	def __init__(
			self, parent, mass_spec, label='', id=wx.ID_ANY, title="Calibre Search", pos=wx.DefaultPosition,
			style=0, name=wx.FrameNameStr
			):
		"""
		:param parent: The window parent. This may be, and often is, None. If it is not None, the frame will be minimized when its parent is minimized and restored when it is restored (although it will still be possible to minimize
		:type parent: wx.Window
		:param mass_spec:
		:type mass_spec:
		:param label:
		:type label: str, optional
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
		
		args = (parent, id)
		kwds = {
				"pos": pos,
				"size": (1000, 600),
				"title": title,
				"style": style,
				"name": name,
				}
		
		# begin wxGlade: SpectrumFrame.__init__
		kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
		wx.Frame.__init__(self, *args, **kwds)
		self.SetSize((1000, 600))

		self.__set_properties()
		self.__do_layout()
		# end wxGlade
		
		self.menubar = SpectrumViewerMenu(self)
		self.SetMenuBar(self.menubar)

		self.SpectrumPanel = Experiment.SpectrumPanel(self, mass_spec)
		# self.SpectrumPanel2 = SpectrumPanel(self, None, wx.ID_ANY)
		
		self._mgr.AddPane(
				self.SpectrumPanel,	aui.AuiPaneInfo().Name("Spectrum Panel").Caption("Spectrum").CenterPane())
		# self._mgr.AddPane(
		# 		self.SpectrumPanel2,
		# 		aui.AuiPaneInfo().Name("Spectrum Panel2").Caption("Spectrum2").CloseButton(True).
		# 							MaximizeButton(True).Bottom().Layer(1).Position(1)
		# 		)
		
		self.toolbar.add_to_manager(self._mgr)
		
		self._mgr.Update()
		
		# self.Bind(wx.EVT_SIZE, self.size_change)
		# self.Bind(wx.EVT_MAXIMIZE, self.size_change)
		self.Bind(wx.EVT_CLOSE, self.OnClose)
	
	def OnClose(self, event):
		self.OnExit(event)
	
	def __set_properties(self):
		# tell FrameManager to manage this frame
		# self._mgr = wx.lib.agw.aui.framemanager.AuiManager_DCP()
		self._mgr = aui.AuiManager(flags=wx.aui.AUI_MGR_LIVE_RESIZE | wx.aui.AUI_MGR_DEFAULT)
		self._mgr.SetManagedWindow(self)
		# begin wxGlade: SpectrumFrame.__set_properties
		self.SetTitle("Spectrum Viewer")
		# end wxGlade
	
	def __do_layout(self):
		self.toolbar = SpectrumViewerToolBar(self)
		# begin wxGlade: SpectrumFrame.__do_layout
		sizer = wx.FlexGridSizer(1, 1, 0, 0)
		sizer.Add((0, 0), 0, 0, 0)
		self.SetSizer(sizer)
		self.Layout()
		# end wxGlade
	
	def size_change(self, _):
		# code to run whenever window resized
		# self.canvas.SetMinSize(self.GetSize())
		self.SpectrumPanel.SetSize(self.GetSize())
		self.Refresh()
		self.SpectrumPanel.Refresh()
	
	# if event.ClassName == "wxSizeEvent":
	# 	event.Skip()
	
	def previous_experiment(self, event):
		pass
	
	def next_experiment(self, event):
		pass
	
	def reset_view(self, event):
		pass
	
	def previous_view(self, event):
		pass
	
	def tool_select(self, event):
		pass
	
	def tool_zoom(self, event):
		pass
	
	def tool_pan(self, event):
		pass
	
	def spectrum_by_number(self, event):
		pass
	
	def spectrum_by_rt(self, event):
		pass
	
	def on_save(self, event):
		pass
	
	def on_copy(self, event):
		pass
	
	def on_copy_data(self, event):
		pass
	
	def OnExit(self, _):
		self._mgr.UnInit()
		del self._mgr
		self.Destroy()

# end of class SpectrumFrame
