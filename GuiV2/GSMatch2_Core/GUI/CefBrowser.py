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

import platform
import sys

import wx
from cefpython3 import cefpython as cef


def init_cefpython(settings=None):
	"""
	Setup for CEF Python

	:param settings:
	:type settings:

	:return:
	:rtype:
	"""

	if settings is None:
		settings = {}
	
	# CEF Python version requirement
	assert cef.__version__ >= "66.0", "CEF Python v66.0+ required to run this"
	sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
	
	if platform.system() == "Windows":
		# noinspection PyUnresolvedReferences, PyArgumentList
		cef.DpiAware.EnableHighDpiSupport()
	cef.Initialize(settings)
	
	return cef

def scale_window_size_for_high_dpi(width, height):
	"""Scale window size for high DPI devices. This func can be
	called on all operating systems, but scales only for Windows.
	If scaled value is bigger than the work area on the display
	then it will be reduced."""
	if not platform.system() == "Windows":
		return width, height
	(_, _, max_width, max_height) = wx.GetClientDisplayRect().Get()
	# noinspection PyUnresolvedReferences
	(width, height) = cef.DpiAware.Scale((width, height))
	if width > max_width:
		width = max_width
	if height > max_height:
		height = max_height
	return width, height


class BrowserPanel(wx.Panel):
	def __init__(self, url, *args, **kwargs):
		
		self.timer = None
		self.timer_id = 1
		self.url = url
		
		self.browser = None
		
		if platform.system() == "Linux":
			# Must ignore X11 errors like 'BadWindow' and others by
			# installing X11 error handlers. This must be done after
			# wx was intialized.
			cef.WindowUtils.InstallX11ErrorHandlers()
		
		if platform.system() == "Windows":
			# noinspection PyUnresolvedReferences, PyArgumentList
			print(f"[wxpython.py] System DPI settings: {str(cef.DpiAware.GetSystemDpi())}")
		
		wx.Panel.__init__(self, *args, **kwargs)
		
		self.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)
		self.Bind(wx.EVT_SIZE, self.OnSize)
		
		self.create_timer()
	
	def embed_browser(self, parent=None):
		if parent is None:
			parent = self
			
		window_info = cef.WindowInfo()
		(width, height) = self.GetClientSize().Get()
#		assert parent.GetHandle(), "Window handle not available"
		# window_info.SetAsChild(parent.GetHandle(),
		# 					   [0, 0, width, height])
		self.browser = cef.CreateBrowserSync(window_info, url=self.url)
		self.browser.SetClientHandler(FocusHandler())
	
	def LoadUrl(self, url):
		if self.browser is None:
			raise ValueError("'embed_browser' must be called first")
		self.browser.LoadUrl(url)
	
	def OnSetFocus(self, _):
		if not self.browser:
			return
		if platform.system() == "Windows":
			cef.WindowUtils.OnSetFocus(self.GetHandle(),
									   0, 0, 0)
		self.browser.SetFocus(True)
	
	def OnSize(self, _):
		if not self.browser:
			return
		
		self.Freeze()
		self.timer.Stop()
		
		if platform.system() == "Windows":
			cef.WindowUtils.OnSize(self.GetHandle(),
								   0, 0, 0)
		elif platform.system() == "Linux":
			(x, y) = (0, 0)
			(width, height) = self.GetSize().Get()
			self.browser.SetBounds(x, y, width, height)
		
		self.Thaw()
		self.timer.Start(10)  # 10ms timer
		wx.CallAfter(self.browser.NotifyMoveOrResizeStarted)
	
	def clear_browser_references(self):
		# Clear browser references that you keep anywhere in your
		# code. All references must be cleared for CEF to shutdown cleanly.
		self.browser = None
	
	def create_timer(self):
		self.timer = wx.Timer(self, self.timer_id)
		self.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
		self.timer.Start(10)  # 10ms timer
	
	def on_timer(self, _):
		cef.MessageLoopWork()
	
	def Destroy(self):
		self.timer.Stop()
		if self.browser:
			self.browser.ParentWindowWillClose()
			self.clear_browser_references()
		
		wx.Panel.Destroy(self)
		wx.CallAfter(cef.Shutdown)

class FocusHandler(object):
	def OnGotFocus(self, browser, **_):
		# Temporary fix for focus issues on Linux (Issue #284).
		if (platform.system() == "Linux"):
			print("[wxpython.py] FocusHandler.OnGotFocus:"
				  " keyboard focus fix (Issue #284)")
			browser.SetFocus(True)

