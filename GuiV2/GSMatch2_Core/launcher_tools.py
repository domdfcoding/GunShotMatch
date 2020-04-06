#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  launcher_tools.py
"""
Shared tools for app launchers
"""
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
import os
import pathlib
import sys

# 3rd party
import wx
from appdirs import user_config_dir
from pid import PidFile, PidFileAlreadyLockedError


def make_pid_dir():
	pid_dir = pathlib.Path(user_config_dir("GunShotMatch")) / ".pid"
	if not pid_dir.exists():
		pid_dir.mkdir()
	
	return pid_dir


def switch_process(name, pid_file):
	other_pid = int(pid_file.read_text())
	print(f"{name} already running")
	print(f"The other PID is: {other_pid}")
	
	# TODO: Send SIGUSR1 and configure GSMatch to show window when signal received
	#  See PySetWacom for example
	# os.kill(other_pid, signal.SIGUSR1)
	
	return


def launch_app(name, pidname, appid, wxapp, **app_kwargs):
	print(f"Starting {name}")
	
	pid_dir = make_pid_dir()
	
	print('My PID is:', os.getpid())
	
	try:
		with PidFile(pidname=pidname, piddir=str(pid_dir)) as p:
			print("###")
			print(wx.Colour(wx.SYS_COLOUR_BACKGROUND))
			print(wx.Colour(240, 240, 240))
			print("###")
			
			if sys.platform == "win32":
				import ctypes
				
				ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
				# wx.html2.WebView.MSWSetEmulationLevel(level=wx.html2.WEBVIEW_EMU_DEFAULT)
			
			App = wxapp(**app_kwargs)
			App.MainLoop()
			
			print("Goodbye :)")
			
			return 0
	
	except (BlockingIOError, PidFileAlreadyLockedError):
		switch_process(name, pid_dir / f"{pidname}.pid")
		return 1


class SimpleLauncher(wx.App):
	def __init__(self, gui_class, redirect=False, filename=None, useBestVisual=False, clearSigInt=True):
		self.gui_class = gui_class
		
		super().__init__(redirect, filename, useBestVisual, clearSigInt)
	
	def OnInit(self):
		if len(sys.argv) > 1:
			self.gui_instance = self.gui_class(None, sys.argv[1], id=wx.ID_ANY, )
		# if len(sys.argv) > 2 and sys.argv[2] == "--readonly":
		# 	self.MethodEditor.make_read_only()
		else:
			self.gui_instance = self.gui_class(None, id=wx.ID_ANY)
		
		self.SetTopWindow(self.gui_instance)
		self.gui_instance.Show()
		return True
