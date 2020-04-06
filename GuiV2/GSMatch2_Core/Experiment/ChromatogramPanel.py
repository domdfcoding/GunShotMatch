#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  ChromatogramPanel.py
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

# 3rd party
import matplotlib
from domdf_wxpython_tools import coming_soon
from domdf_wxpython_tools.projections import XPanAxes
from matplotlib.figure import Figure
from pubsub import pub
from pyms.Display import Display
import wx

# this package
from GuiV2.GSMatch2_Core.GUI.chartpanel import ChartPanelBase
from GuiV2.GSMatch2_Core.IDs import *


matplotlib.projections.register_projection(XPanAxes)


class ChromatogramPanel(ChartPanelBase):
	"""
	Panel for displaying a Chromatogram that can be zoomed, panned etc.
	"""
	
	def __init__(
			self, experiment, parent, id=wx.ID_ANY,
			pos=wx.DefaultPosition, size=wx.DefaultSize,
			style=0, name="ChromatogramPanel",
			):
		"""
		:param experiment:
		:type experiment:
		:param parent: The parent window.
		:type parent: wx.Window
		:param id: An identifier for the panel. wx.ID_ANY is taken to mean a default.
		:type id: wx.WindowID, optional
		:param pos: The panel position. The value wx.DefaultPosition indicates a default position, chosen by either the windowing system or wxWidgets, depending on platform.
		:type pos: wx.Point, optional
		:param size: The panel size. The value wx.DefaultSize indicates a default size, chosen by, either the windowing system or wxWidgets, depending on platform.
		:type size: wx.Size, optional
		:param style: The window style. See wxPanel.
		:type style: int, optional
		:param name: Window name.
		:type name: str, optional
		"""
		
		self.experiment = experiment
		
		fig = Figure()
		ax = fig.add_subplot(111, projection="XPanAxes")  # 1x1 grid, first subplot

		ChartPanelBase.__init__(self, parent, fig, ax, id, pos, size, style, name)
		
		pub.subscribe(self.view_mode_changed, "view_mode_changed")
		
		self.display()
		self._view_spectrum_enabled = False

	def view_mode_changed(self):
		"""
		Event handler for a toolbar button being being clicked
		"""
		
		print(f"Tool Changed from {self.experiment.name}")
		
		tb_view = self.FindWindowById(ID_View_Toolbar)
		
		self.pan(tb_view.GetToolState(ID_View_Pan))
		self.zoom(tb_view.GetToolState(ID_View_Zoom))
		self.view_spectrum_on_click(tb_view.GetToolState(ID_View_Spectrum))
	
	def view_spectrum_on_click(self, enable=True):
		"""
		Toggle "View Spectrum On Click" mode
		
		:param enable: Whether to enable the mode
		:type enable: bool
		"""
		
		if enable or (not enable and self._view_spectrum_enabled):
			coming_soon("'view_spectrum_on_click' has not been implemented yet")
			
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
	# 			self.chromatogram_figure.savefig(f"{pathname}.{filetype}")
	#
	# 	except:
	# 		wx.LogError("Cannot save file '%s'." % pathname)
	# 		traceback.print_exc()
	
	def display(self):
		"""
		Display the Chromatogram
		"""
		
		self.constrain_zoom("x")
		
		display = Display(self.fig, self.ax)
		self.ax.clear()
		
		# Read the TIC from the tic.dat file in the experiment tarfile
		intensity_array, tic = self.experiment.tic_data
		
		# peak_list = load_peaks(os.path.join(ExprDir, "{}_peaks.dat".format(self.experiment.name)))
		
		display.plot_tic(tic, label=self.experiment.name, minutes=True)
		# display.plot_peaks(filtered_peak_list, "Peaks")
		# display.do_plotting('TIC and PyMS Detected Peaks')
		# display.do_plotting(f'{self.experiment.name} TIC')
		display.do_plotting('')
		
		x = [time / 60 for time in tic.time_list]
		
		self.ax.set_xlim(left=0, right=max(x))
		self.ax.set_ylim(bottom=0)
		self.ax.set_xlabel("Retention Time")
		self.ax.set_ylabel("Intensity")
		
		self.fig.subplots_adjust(left=0.1, bottom=0.125, top=0.9, right=0.97)
		# figure.tight_layout()
		self.canvas.draw()
		
		self.setup_ylim_refresher(intensity_array, x)
	
	def rescale_y(self, *_):
		intensity_array, tic = self.experiment.tic_data
		x = [time / 60 for time in tic.time_list]
		
		self.do_rescale_y(x, intensity_array)
		
	def rescale_x(self, *_):
		intensity_array, tic = self.experiment.tic_data
		x = [time / 60 for time in tic.time_list]
		
		self.do_rescale_x(x)
