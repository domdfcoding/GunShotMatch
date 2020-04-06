#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  prog_dialog_indeterminate.py
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


# stdlib
import threading
import time

# 3rd party
import wx
from importlib_resources import path
from pubsub import pub
from wx.adv import Animation, AnimationCtrl

# this package
import GuiV2.GSMatch2_Core.GUI


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


class AnimatedProgDialog(wx.Dialog):
	def __init__(
			self, title, parent=None,
			style=wx.DEFAULT_DIALOG_STYLE):
		"""
		:param parent: Can be None, a frame or another dialog box.
		:type parent: wx.Window
		:param title: The title of the dialog.
		:type title: str
		:param style: The window style.
		:type style: int
		"""
		
		self.parent = parent
		
		wx.Dialog.__init__(self, parent, wx.ID_ANY, title, style=style)
		
		# Prevent closing of dialog
		self.Bind(wx.EVT_CLOSE, lambda event: None)
		
		with path(GuiV2.GSMatch2_Core.GUI, "loading_animation.gif") as loading_gif:
			ani = Animation(name=str(loading_gif))
		ctrl = AnimationCtrl(self, -1, ani)
		ctrl.SetBackgroundColour(self.GetBackgroundColour())
		
		if wx.Platform == "__WXMSW__":
			self.Fit()
		
		ctrl.Play()

#
# class AnimatedProgDialogCancel(AnimatedProgDialog):
# 	def __init__(
# 			self, title, parent=None,
# 			style=wx.DEFAULT_DIALOG_STYLE):
# 		"""
# 		:param title:
# 		:type title: str
# 		:param parent:
# 		:type parent: wx.Window
# 		:param style:
# 		:type style: int
# 		"""
#
# 		AnimatedProgDialog.__init__(self, title, parent, style)
#
# 		dialog_size = self.GetSize()
#
# 		self.button = wx.Button(self, wx.ID_CANCEL)
# 		button_size = self.button.GetSize()
# 		self.button.SetPosition((
# 				dialog_size.x - button_size.x - 10,
# 				dialog_size.y - button_size.y - 10,
# 				))
#
# 		self.focus_thief = wx.Button(self, wx.ID_ANY)
# 		self.focus_thief.SetPosition((dialog_size.x, dialog_size.y))
# 		self.focus_thief.SetFocus()
#
# 		self.focus_thief.Bind(wx.EVT_BUTTON, self.on_button)
#
# 	def on_button(self, event):
# 		pub.sendMessage("AnimatedProgDialogCancel", dialog=self)
#


class AnimatedSplash(wx.Dialog):
	"""
	Possible animated splash screen
	"""
	
	def __init__(self, parent=None):
		"""
		:param parent: Can be None, a frame or another dialog box.
		:type parent: wx.Window
		"""
		
		wx.Dialog.__init__(self, parent, style=0)
		
		with path(GuiV2.GSMatch2_Core.GUI, "loading_animation.gif") as loading_gif:
			ani = Animation(name=str(loading_gif))
		sizer = wx.BoxSizer(wx.VERTICAL)
		ctrl = AnimationCtrl(self, -1, ani)
		ctrl.SetBackgroundColour(self.GetBackgroundColour())
		
		sizer.Add(ctrl, 1, wx.EXPAND, 0)
		self.SetSizer(sizer)
		ctrl.Play()
		
		if wx.Platform == "__WXMSW__":
			self.Fit()
		self.CenterOnScreen()


class MessageAnimatedProgDialog(AnimatedSplash):
	def __init__(self, message="Loading...", parent=None, ):
		"""
		Possible animated splash screen
		"""
		
		AnimatedSplash.__init__(self, parent)
		
		self.msg = message
		
		self.message = wx.StaticText(self, label=message)
		self.message.SetForegroundColour(wx.Colour(255, 255, 255))
		self.message.SetPosition((10, 10))
		
		dialog_size = self.GetSize()
		
		self.button = wx.Button(self, wx.ID_CANCEL)
		button_size = self.button.GetSize()
		self.button.SetPosition((
				dialog_size.x - button_size.x - 10,
				dialog_size.y - button_size.y - 10,
				))
		
		self.focus_thief = wx.Button(self, wx.ID_ANY)
		self.focus_thief.SetPosition((dialog_size.x, dialog_size.y))
		self.focus_thief.SetFocus()
		
		self.focus_thief.Bind(wx.EVT_BUTTON, self.on_button)
	
		self.value = 0
	
	def Update(self, value=None, newmsg=''):
		"""
		Updates the dialog, setting the progress bar to the new value and updating the message if new one is specified.

		:param value: The new value of the progress, between 0 and 100.
		:type value: int
		:param newmsg: The new messages for the progress dialog text, if it is empty (which is the default) the message is not changed.
		:type newmsg: str
		"""
		
		if value is None:
			self.value += 1
		else:
			self.value = value
		
		if newmsg:
			self.msg = newmsg
		
		self.message.SetLabel(f"{self.msg} {self.value}%")
	
	def on_button(self, event):
		self.Update()
		

if __name__ == '__main__':
	app = wx.App()
	splash = MessageAnimatedProgDialog()
	splash.ShowModal()

	# AnimatedProgDialog("Something in Progress").ShowModal()
