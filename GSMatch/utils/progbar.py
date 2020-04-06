#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  progbar.py
#  

# From http://wxpython-users.1045709.n5.nabble.com/Gauge-in-Statusbar-td2321906.html
# Adapted by Dominic Davis-Foster


"""
Test program for Progsbar.ProgressStatusBar.

	Ray Pasco       2005-05-20
"""

import wx


class ProgressStatusBar:
	"""
	wx.Gauge placement into a single or multi-fielded wx.Statusbar.
	Will completely fill the statusbar field. Note that the field size
	should be fixed or the frame size should be fixed so that the
	field dimension for the gauge do not change. Fixing the frame size
	can be done by:

		def on_size (self, event):
			self.SetSize (self.size)
			event.Skip ()
		#end def

	Ray Pasco 2005-05-21        ver. 1.00
	"""
	
	def __init__(self, parent, statusbar, sbarfields=1, sbarfield=0, maxcount=100):
		
		rect = statusbar.GetFieldRect(sbarfield)
		barposn = (rect[0], rect[1])
		
		print(barposn)
		
		# On MSW the X dimension returned from GetFieldRect for the last field is too small.
		#   This hack fills the field but covers over the lower right frame resize handle,
		#   but that's OK since the field size should be unchangeable.
		if (sbarfield + 1 == sbarfields) and (wx.Platform == '__WXMSW__'):
			barsize = (rect[2] + 35, rect[3])  # completely fill the last field
		else:
			barsize = (rect[2], rect[3])
		
		self.progbar = wx.Gauge(statusbar, -1, maxcount, barposn, barsize)
	
	def SetValue(self, value):
		self.progbar.SetValue(value)

# end class ProgressStatusBar


class MainFrame(wx.Frame):
	
	def __init__(
			self, parent, id=-1, title='Default Frame Title',
			size=(200, 150), pos=(100, 75)
			):
		"""
		:param parent: The window parent. This may be, and often is, None. If it is not None, the frame will be
			minimized when its parent is minimized and restored when it is restored (although it will still be
			possible to minimize.
		:type parent: wx.Window, or None
		:param id: The window identifier. It may take a value of -1 to indicate a default value.
		:type id: wx.WindowID, optional
		:param title: The caption to be displayed on the frame’s title bar.
		:type title: str, optional
		:param pos: The window position. The value DefaultPosition indicates a default position,
			chosen by either the windowing system or wxWidgets, depending on platform.
		:type pos: wx.Point, optional
		:param size: The window size. The value DefaultSize indicates a default size,
			chosen by either the windowing system or wxWidgets, depending on platform.
		:type size: wx.Size, optional
		"""
		
		wx.Frame.__init__(self, parent, id, title=title, size=size, pos=pos)
		
		self.SetBackgroundColour((235, 245, 245))  # gotta love these pastels
		
		panel = wx.Panel(self, -1)
		
		# This is one way to avoid the resizing problem when having
		# a fixed length gauge widget in a variably-sized statusbar segment.
		# Otherwise, the statusbar field size could simply be fixed.
		self.size = size
		self.Bind(wx.EVT_SIZE, self.on_size)
		
		sbarfields = 2  # total number statusbar fields
		self.statusbar = wx.StatusBar(self, -1)  # no need to subclass
		self.statusbar.SetFieldsCount(sbarfields)
		self.statusbar.SetStatusWidths([-1 for _ in range(sbarfields)])  # equal field sizes
		self.SetStatusBar(self.statusbar)
		
		self.textfield = 0  # statusbar field to write messages to
		self.statusbar.SetStatusText('Press <Enter> or click button to start.', self.textfield)
		
		sbarfield = 1  # put progressbar (gauge) in this statusbar field
		self.maxcount = 50  # arbitrary full-scale count
		self.progbar = ProgressStatusBar(self, self.statusbar, sbarfields, sbarfield, self.maxcount)
		
		xsize, ysize = self.GetClientSize()
		self.btnstartstop = wx.Button(panel, -1, 'Start', pos=(xsize / 2 - 35, ysize / 2 - 15))
		self.Bind(wx.EVT_BUTTON, self.on_start_stop, self.btnstartstop)
		
		self.CenterOnScreen()
		self.Show(True)
	
	def on_size(self, event):
		
		self.SetSize(self.size)
		event.Skip()
	
	def on_start_stop(self, _):
		
		try:
			self.started  # variables been instantiated yet ?
		except AttributeError:
			self.started = False  # instantiate
			self.evenodd = 0
		
		if not self.started:
			self.statusbar.SetStatusText('In progress ...', self.textfield)
			
			self.psbctr = 0
			self.timer = wx.PyTimer(self.on_timer)
			self.timer.Start(25)  # mseconds counter increment interval
			self.on_timer()  # call it once right away
			
			self.btnstartstop.SetLabel('Stop')
			self.started = True
		
		else:
			self.statusbar.SetStatusText('Press <Enter> or click button to start.', self.textfield)
			
			if self.evenodd:
				self.progbar.SetValue(0)
				self.evenodd = 0
			else:
				self.progbar.SetValue(self.maxcount)
				self.evenodd = 1
			
			del self.timer
			
			self.btnstartstop.SetLabel('Start')
			self.started = False
		
	def on_timer(self):
		
		self.psbctr += 1
		self.progbar.SetValue(self.psbctr)
		if self.psbctr >= self.maxcount:
			self.psbctr = 0

# end class MainFrame


if __name__ == '__main__':
	myApp = wx.PySimpleApp()
	myFrame = MainFrame(
			None, -1, 'Progress Bar Gauge in the Statusbar Test',
			size=(600, 300), pos=(0, 0))
	myApp.MainLoop()
