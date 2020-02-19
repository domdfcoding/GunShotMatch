#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  prog_dialog_indeterminate.py
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import threading
import time

# 3rd party
import wx
from pubsub import pub
from wx.adv import Animation, AnimationCtrl


class ThreadProgPulser(threading.Thread):
	"""
	Thread for pulsing ProgDialogThread
	"""
	
	def __init__(self, parent):
		
		threading.Thread.__init__(self)
		
		self.parent = parent
		self.start()
	
	def run(self):
		"""
		Starts the Thread. Don't call this directly; use ``Thread.start()`` instead.
		"""
		
		parent_id = id(self.parent)
		
		while not self.parent.stop_thread:
			if self.parent.thread.ident:
				if self.parent.thread.isAlive():
					wx.CallAfter(pub.sendMessage, f"pulse_{parent_id}", msg='')
				else:
					wx.CallAfter(pub.sendMessage, f"pulse_{parent_id}", msg='Dead')
					break
			time.sleep(0.05)
			
			
class ProgDialogThread(wx.ProgressDialog):
	def __init__(
			self, thread, title, message, maximum=100, parent=None,
			style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE):
		"""
		:param thread:
		:type thread: threading.Thread
		:param title:
		:type title: str
		:param message:
		:type message: str
		:param maximum:
		:type maximum: int
		:param parent:
		:type parent: wx.Window
		:param style:
		:type style: int
		"""
		
		self.parent = parent
		self.stop_thread = False
		
		wx.ProgressDialog.__init__(self, title, message, maximum, parent, style)
		self.Pulse()
		
		# Subscribe for events
		pub.subscribe(self.updateProgress, f"pulse_{id(self)}")
		
		# Run threads
		self.thread = thread
		ThreadProgPulser(self)
		self.thread.start()
	
	def updateProgress(self, msg):
		"""
		Event handler for updating the progress bar
		"""
		
		self.Pulse()
	
	def Destroy(self):
		self.stop_thread = True
		wx.Dialog.Destroy(self)


#
#
# class ProgDialogThread(wx.Dialog):
# 	def __init__(
# 			self, thread, title, message, maximum=100, parent=None,
# 			style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE):
# 		"""
# 		:param thread:
# 		:type thread: threading.Thread
# 		:param title:
# 		:type title: str
# 		:param message:
# 		:type message: str
# 		:param maximum:
# 		:type maximum: int
# 		:param parent:
# 		:type parent: wx.Window
# 		:param style:
# 		:type style: int
# 		"""
#
# 		self.parent = parent
# 		self.stop_thread = False
#
# 		wx.Dialog.__init__(self, parent, wx.ID_ANY, title, style=style)
# 		ani = Animation(name="/home/domdf/GunShotMatch/GunShotMatch/loading_animation.gif")
# 		ctrl = AnimationCtrl(self, -1, ani)
# 		ctrl.SetBackgroundColour(self.GetBackgroundColour())
# 		ctrl.Play()
#
# 		pub.subscribe(self.updateProgress, f"pulse_{id(self)}")
#
# 		self.Show()
#
# 	def Pulse(self):
# 		pass
#
# 	def updateProgress(self, msg):
# 		"""
# 		Event handler for updating the progress bar
# 		"""
#
# 		self.Pulse()
#
# 	def Destroy(self):
# 		self.stop_thread = True
# 		wx.Dialog.Destroy(self)


class AnimatedProgDialog(wx.Dialog):
	def __init__(
			self, title, parent=None,
			style=wx.DEFAULT_DIALOG_STYLE):
		"""
		:param title:
		:type title: str
		:param parent:
		:type parent: wx.Window
		:param style:
		:type style: int
		"""
		
		self.parent = parent
		
		wx.Dialog.__init__(self, parent, wx.ID_ANY, title, style=style)
		ani = Animation(name="/home/domdf/GunShotMatch/GunShotMatch/loading_animation.gif")
		ctrl = AnimationCtrl(self, -1, ani)
		ctrl.SetBackgroundColour(self.GetBackgroundColour())
		ctrl.Play()


class TestDialog(wx.Dialog):
	def __init__(self, title, parent=None, id=wx.ID_ANY, style=wx.DEFAULT_DIALOG_STYLE):
		"""
		:param title:
		:type title: str
		:param parent:
		:type parent: wx.Window
		:param style:
		:type style: int
		"""
		
		wx.Dialog.__init__(self, parent, id, title, style=style)
		ani = Animation(name="/home/domdf/GunShotMatch/GunShotMatch/loading_animation.gif")
		ctrl = AnimationCtrl(self, -1, ani)
		ctrl.SetBackgroundColour(self.GetBackgroundColour())
		ctrl.Play()


class AnimatedSplash(wx.Dialog):
	def __init__(self, title, parent=None, style=0):
		"""
		Possible animated splash screen
		"""
		
		wx.Dialog.__init__(self, parent, -1, title, style=style)
		
		ani = Animation(name="/home/domdf/GunShotMatch/GunShotMatch/loading_animation.gif")
		ctrl = AnimationCtrl(self, -1, ani)
		ctrl.SetBackgroundColour(self.GetBackgroundColour())
		ctrl.Play()


if __name__ == '__main__':
	app = wx.App()
	TestDialog("Something in Progress").ShowModal()

