#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.9.3 on Wed Jun 12 20:46:57 2019
#

# This is an automatically generated file.
# Manual changes will be overwritten without warning!

import wx
from Launcher import Launcher


class GSM_App(wx.App):
	def OnInit(self):
		self.GunShotMatch = Launcher(None, wx.ID_ANY, "")
		self.SetTopWindow(self.GunShotMatch)
		self.GunShotMatch.Show()
		return True

# end of class GSM_App

if __name__ == "__main__":
	GunShotMatch = GSM_App(0)
	GunShotMatch.MainLoop()
