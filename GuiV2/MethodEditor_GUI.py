#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  MethodEditor.py
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2019  Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
#
# generated by wxGlade 0.9.0 on Thu Feb  7 18:16:22 2019
#

__author__ = "Dominic Davis-Foster"
__copyright__ = "Copyright 2019 Dominic Davis-Foster"

__license__ = "GPLv3"
__version__ = "0.2.0"
__email__ = "dominic@davis-foster.co.uk"


# stdlib
import sys
sys.path.append("..")

# 3rd party
import wx
import wx.html2
import wx.richtext

# this package
from GuiV2.GSMatch2_Core import Method

sys.path.append("..")


# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


#if platform.system() == "Windows":
#	wx.html2.WebView.MSWSetEmulationLevel(level=wx.html2.WEBVIEW_EMU_IE11)


class GSM_App(wx.App):
	def OnInit(self):
		if len(sys.argv) > 1:
			self.MethodEditor = Method.MethodEditor(None, wx.ID_ANY, "", method=sys.argv[1])
			# if len(sys.argv) > 2 and sys.argv[2] == "--readonly":
			# 	self.MethodEditor.make_read_only()
		else:
			self.MethodEditor = Method.MethodEditor(None, wx.ID_ANY, "")
	
		self.SetTopWindow(self.MethodEditor)
		self.MethodEditor.Show()
		return True

# end of class GSM_App

def main():
	
	print("###")
	print(wx.Colour(wx.SYS_COLOUR_BACKGROUND))
	print(wx.Colour(240, 240, 240))
	print("###")
	
	if sys.platform == "win32":
		import ctypes
		myappid = "GunShotMatchMethodEditor"
		ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
		
	MethodEditor = GSM_App(False)
	MethodEditor.MainLoop()
	
	print("Goodbye :)")


#	if platform.system() == "Windows":
#		wx.html2.WebView.MSWSetEmulationLevel(level=wx.html2.WEBVIEW_EMU_DEFAULT)

if __name__ == "__main__":
	sys.exit(main())