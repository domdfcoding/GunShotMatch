#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  spectrum_panel.py
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2019-2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import matplotlib
import wx.html2
from matplotlib.figure import Figure
from pyms.Display import Display

# this package
from GSMatch.GSMatch_Core.Projections import XPanAxes
from GuiV2.GSMatch2_Core.chartpanel import ChartPanelBase
from GuiV2.GSMatch2_Core import Experiment
from GuiV2.GSMatch2_Core.IDs import *

matplotlib.projections.register_projection(XPanAxes)


class SpectrumPanel(Experiment.ChromatogramPanel):
	"""
	Panel for displaying a Mass Spectrum that can be zoomed, panned etc.
	"""
	
	def __init__(
			self, experiment, parent, id=wx.ID_ANY,
			pos=wx.DefaultPosition, size=wx.DefaultSize,
			style=0, name=wx.PanelNameStr):
		"""
		:param experiment:
		:type experiment:
		:param parent: The parent window.
		:type parent: wx.Window
		:param id: An identifier for the panel. wx.ID_ANY is taken to mean a default.
		:type id: wx.WindowID, optional
		:param pos: The panel position. The value ::wxDefaultPosition indicates a default position,
		:type pos: wx.Point, optional
			chosen by either the windowing system or wxWidgets, depending on platform.
		:param size: The panel size. The value ::wxDefaultSize indicates a default size, chosen by
		:type size: wx.Size, optional
			either the windowing system or wxWidgets, depending on platform.
		:param style: The window style. See wxPanel.
		:type style: int, optional
		:param name: Window name.
		:type name: str, optional
		"""
		
		self.experiment = experiment
		
		fig = Figure()
		ax = fig.add_subplot(111, projection="XPanAxes")  # 1x1 grid, first subplot

		ChartPanelBase.__init__(self, parent, fig, ax, id, pos, size, style, name)

		self._do_layout()
	
		self.scan_number = None
	
		# self.display()
		
		self.Bind(wx.EVT_SIZE, self.on_size_change, self)
		self.Bind(wx.EVT_MAXIMIZE, self.on_size_change)
	
	def load_by_retention_time(self, retention_time):
		pass
		# determine scan number from RT
		self.scan_number = None
		self.display()
	
	def load_by_scan_number(self, scan_number):
		self.scan_number = scan_number
		self.display()
	
	# def save(self, event):
	#
	# 	self.focus_thief.SetFocus()
	#
	# 	filetypes = []
	# 	if self.png_button.GetValue():
	# 		filetypes.append("png")
	# 	if self.svg_button.GetValue():
	# 		filetypes.append("svg")
	# 	if self.pdf_button.GetValue():
	# 		filetypes.append("pdf")
	#
	# 	if len(filetypes) == 0:
	# 		wx.MessageBox("Please choose one or more filetypes", "Error", wx.ICON_ERROR | wx.OK)
	# 		return
	#
	# 	pathname = os.path.splitext(file_dialog(
	# 			self, "*", "Save Chart", "",
	# 			# defaultDir=self.Config.get("main", "resultspath")))[0]
	# 			defaultDir=self._parent.Config.results_dir))[0]
	#
	# 	# Do any of the files already exist?
	# 	try:
	# 		for filetype in filetypes:
	# 			if os.path.isfile(f"{pathname}.{filetype}"):
	# 				alert = wx.MessageDialog(
	# 						self,
	# 						f'A file named "{pathname}.{filetype}" already exists.\nDo you want to replace it?',
	# 						"Overwrite File?",
	# 						wx.ICON_QUESTION | wx.OK | wx.CANCEL
	# 						)
	#
	# 				alert.SetOKLabel("Replace")
	# 				if alert.ShowModal() != wx.YES:
	# 					return
	#
	# 			self.spectrum_figure.savefig(f"{pathname}.{filetype}")
	#
	# 	except:
	# 		wx.LogError("Cannot save file '%s'." % pathname)
	# 		traceback.print_exc()
	
	# Display Function
	def display(self):
		"""
		Display the Spectrum
		"""

		self.constrain_zoom("x")
		
		display = Display(self.spectrum_figure, self.spectrum_axes)
		
		if self.scan_number:
			self.spectrum_axes.clear()
			
			# Do plotting of spectrum
			
			#display.plot_tic(tic, label=sample_name, minutes=True)
			# display.plot_peaks(filtered_peak_list, "Peaks")
			# display.do_plotting('TIC and PyMS Detected Peaks')
			# display.do_plotting(f'{sample_name} TIC')
			#display.do_plotting('')
			
			#y = tic.get_intensity_array()
			#x = [time / 60 for time in tic.get_time_list()]
			
			#self.spectrum_axes.set_xlim(left=0, right=max(x))
		
		else:
			self.spectrum_axes.text(
					0.5,
					0.5,
					f"Current Experiment: {self.experiment.name}\n\nPlease select a Spectrum using the buttons above",
					horizontalalignment="center",
					fontsize='32',
					transform=self.spectrum_axes.transAxes
					)
		

		self.spectrum_axes.set_ylim(bottom=0)
		self.spectrum_axes.set_xlabel("m/z") # todo: make italic
		self.spectrum_axes.set_ylabel("Intensity")
		
		self.spectrum_figure.subplots_adjust(left=0.1, bottom=0.125, top=0.9, right=0.97)
		# figure.tight_layout()
		self.canvas.draw()
		
		#self.setup_ylim_refresher(y, x)

	
	def on_size_change(self, event):
		"""
		Event Handler for size change events
		"""
		
		print(f"Size changed: {self.experiment}")
		self.size_change()
