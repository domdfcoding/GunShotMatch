#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  SpectrumPanel.py
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
import wx
from domdf_wxpython_tools.projections import XPanAxes
from matplotlib.figure import Figure
from pubsub import pub
from pyms.Display import plot_head2tail, plot_mass_spec
from pyms.Spectrum import normalize_mass_spec

# this package
from GuiV2.GSMatch2_Core.GUI.chartpanel import ChartPanelBase
from GuiV2.GSMatch2_Core.IDs import *

matplotlib.projections.register_projection(XPanAxes)


# TODO: Zoom should rescale y-axis
#  Reset View and Previous View buttons


class SpectrumPanel(ChartPanelBase):
	"""
	Panel for displaying a Spectrum that can be zoomed, panned etc.
	"""
	
	def __init__(
			self, parent, mass_spec=None, label='', id=wx.ID_ANY,
			pos=wx.DefaultPosition, size=wx.DefaultSize,
			style=0, name="SpectrumPanel"):
		"""
		:param parent: The parent window.
		:type parent: wx.Window
		:param mass_spec: The Mass Spectrum to plot in the panel, or None for two-stage plotting
		:type mass_spec: :class:`pyms.Spectrum.MassSpectrum` or None
		:param label: A label for the spectrum
		:type label: str, optional
		:param id: An identifier for the panel. wx.ID_ANY is taken to mean a default.
		:type id: wx.WindowID, optional
		:param pos: The panel position. The value wx.DefaultPosition indicates a default position,
			chosen by either the windowing system or wxWidgets, depending on platform.
		:type pos: wx.Point, optional
		:param size: The panel size. The value wx.DefaultSize indicates a default size,
			chosen by either the windowing system or wxWidgets, depending on platform.
		:type size: wx.Size, optional
		:param style: The window style. See wxPanel.
		:type style: int, optional
		:param name: Window name.
		:type name: str, optional
		"""
		
		fig = Figure()
		ax = fig.add_subplot(111, projection="XPanAxes")  # 1x1 grid, first subplot
		
		ChartPanelBase.__init__(self, parent, fig, ax, id, pos, size, style, name)
		
		pub.subscribe(self.view_mode_changed, "view_mode_changed")
		
		self.constrain_zoom("x")
		
		self.mass_spec = None
		self.label = None
		self.legend = None
		self.plotted = False
		
		if mass_spec:
			self.plot_mass_spec(mass_spec, label)
	
	def view_mode_changed(self):
		"""
		Event handler for a toolbar button being being clicked
		"""
		
		print(f"Tool Changed from {self.Name}")
		
		tb_view = self.FindWindowById(ID_View_Toolbar)
		
		self.pan(tb_view.GetToolState(ID_View_Pan))
		self.zoom(tb_view.GetToolState(ID_View_Zoom))
	
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
	
	def set_mass_spec(self, mass_spec, label=''):
		"""
		Sets the mass spectrum for the SpectrumPanel for two step creation.
		Call plot_mass_spec without the mass_spec argument to actually plot the chart

		:param mass_spec: The Mass Spectrum to plot in the panel
		:type mass_spec: :class:`pyms.Spectrum.MassSpectrum`
		:param label: A label for the spectrum
		:type label: str, optional
		"""

		ChartPanelBase.clear(self)
		
		self.mass_spec = mass_spec
		if label:
			self.label = label
		self.plotted = False
	
	def plot_mass_spec(self, mass_spec=None, label=''):
		"""
		Display the Spectrum
		
		:param mass_spec: The Mass Spectrum to plot in the panel, or None
		:type mass_spec: :class:`pyms.Spectrum.MassSpectrum` or None, optional
		:param label: A label for the spectrum
		:type label: str, optional
		
		If mass_spec and/or label are unspecified, the values from __init__ or set_mass_spec are used.
		
		:raises: ValueError if mass_spec is None and it was not defined in either __init__ or set_mass_spec
		"""
		
		if mass_spec:
			self.set_mass_spec(mass_spec, label)
		
		if self.mass_spec is None:
			raise ValueError("`mass_spec` cannot be None")
		
		self.ax.clear()
		
		plot_mass_spec(self.ax, self.mass_spec, label=self.label)
		
		self.legend = self.ax.legend()
		
		y = self.mass_spec.intensity_list
		x = self.mass_spec.mass_list
		
		# self.ax.set_xlim(left=0, right=max(x))
		# self.ax.set_ylim(bottom=0)
		self.ax.set_xlabel("m/z", style="italic")
		self.ax.set_ylabel("Intensity")
		
		# self.fig.subplots_adjust(left=0.1, bottom=0.125, top=0.9, right=0.97)
		self.fig.tight_layout()
		# figure.tight_layout()
		self.canvas.draw()
		
		self.setup_ylim_refresher(y, x)
		
		self.plotted = True
	
	def clear(self):
		self.mass_spec = None
		self.label = None
		self.legend = None
		self.plotted = False
		ChartPanelBase.clear(self)
	
	def rescale_y(self, *_):
		self.do_rescale_y(self.mass_spec.mass_list, self.mass_spec.intensity_list)
	
	def rescale_x(self, *_):
		self.do_rescale_x(self.mass_spec.mass_list)


class Head2TailSpectrumPanel(ChartPanelBase):
	"""
	Panel for displaying a two Spectra head2tail that can be zoomed, panned etc.
	"""
	
	def __init__(
			self, parent, top_mass_spec=None, bottom_mass_spec=None,
			top_label='', bottom_label='', id=wx.ID_ANY,
			pos=wx.DefaultPosition, size=wx.DefaultSize,
			style=0, name="Head2TailSpectrumPanel",
			):
		"""
		:param parent: The parent window.
		:type parent: wx.Window
		:param top_mass_spec: The Mass Spectrum to plot in the top half of the panel,
			or None for two-stage plotting
		:type top_mass_spec: :class:`pyms.Spectrum.MassSpectrum` or None
		:param bottom_mass_spec: The Mass Spectrum to plot in the bottom half of the panel,
			or None for two-stage plotting
		:type bottom_mass_spec: :class:`pyms.Spectrum.MassSpectrum` or None
		:param top_label: A label for the spectrum in the top half of the panel
		:type top_label: str, optional
		:param bottom_label: A label for the spectrum in the bottom half of the panel
		:type bottom_label: str, optional
		:param id: An identifier for the panel. wx.ID_ANY is taken to mean a default.
		:type id: wx.WindowID, optional
		:param pos: The panel position. The value wx.DefaultPosition indicates a default position,
			chosen by either the windowing system or wxWidgets, depending on platform.
		:type pos: wx.Point, optional
		:param size: The panel size. The value wx.DefaultSize indicates a default size,
			chosen by either the windowing system or wxWidgets, depending on platform.
		:type size: wx.Size, optional
		:param style: The window style. See wxPanel.
		:type style: int, optional
		:param name: Window name.
		:type name: str, optional
		"""
		
		fig = Figure()
		ax = fig.add_subplot(111, projection="XPanAxes")  # 1x1 grid, first subplot
		
		ChartPanelBase.__init__(self, parent, fig, ax, id, pos, size, style, name)
		
		pub.subscribe(self.view_mode_changed, "view_mode_changed")
		
		self.constrain_zoom("x")
		
		self.top_mass_spec = None
		self.bottom_mass_spec = None
		self.top_label = None
		self.bottom_label = None
		self.all_masses = None
		self.legend = None
		self.plotted = False
		
		if top_mass_spec and bottom_mass_spec:
			self.plot_head2tail(top_mass_spec, bottom_mass_spec, top_label, bottom_label)
		
		# print(f"Current Canvas Mode: {self.current_canvas_mode}")
	
	def view_mode_changed(self):
		"""
		Event handler for a toolbar button being being clicked
		"""
		
		print(f"Tool Changed from {self.Name}")
		
		tb_view = self.FindWindowById(ID_View_Toolbar)
		
		self.pan(tb_view.GetToolState(ID_View_Pan))
		self.zoom(tb_view.GetToolState(ID_View_Zoom))
	
	def set_mass_specs(self, top_mass_spec, bottom_mass_spec, top_label='', bottom_label=''):
		"""
		Sets the mass spectra for the SpectrumPanel for two step creation.
		Call plot_mass_spec without the mass_spec argument to actually plot the chart

		:param top_mass_spec: The Mass Spectrum to plot in the top half of the panel
		:type top_mass_spec: :class:`pyms.Spectrum.MassSpectrum`
		:param bottom_mass_spec: The Mass Spectrum to plot in the bottom half of the panel
		:type bottom_mass_spec: :class:`pyms.Spectrum.MassSpectrum`
		:param top_label: A label for the spectrum in the top half of the panel
		:type top_label: str, optional
		:param bottom_label: A label for the spectrum in the bottom half of the panel
		:type bottom_label: str, optional
		"""
		
		ChartPanelBase.clear(self)
		
		self.top_mass_spec = top_mass_spec
		if top_label:
			self.top_label = top_label
		self.bottom_mass_spec = bottom_mass_spec
		if bottom_label:
			self.bottom_label = bottom_label
		self.plotted = False
	
	def set_top_mass_spec(self, top_mass_spec, top_label=''):
		"""
		Sets the mass spectrum for the top of the SpectrumPanel for two step creation.
		Call plot_mass_spec without the mass_spec argument to actually plot the chart

		:param top_mass_spec: The Mass Spectrum to plot in the top half of the panel
		:type top_mass_spec: :class:`pyms.Spectrum.MassSpectrum`
		:param top_label: A label for the spectrum in the top half of the panel
		:type top_label: str, optional
		"""
		
		ChartPanelBase.clear(self)
		
		# Normalize the mass spectrum
		self.top_mass_spec = normalize_mass_spec(top_mass_spec)
		
		if top_label:
			self.top_label = top_label
		self.plotted = False
		
	def set_bottom_mass_spec(self, bottom_mass_spec, bottom_label=''):
		"""
		Sets the mass spectrum for the bottom of the SpectrumPanel for two step creation.
		Call plot_mass_spec without the mass_spec argument to actually plot the chart

		:param bottom_mass_spec: The Mass Spectrum to plot in the bottom half of the panel
		:type bottom_mass_spec: :class:`pyms.Spectrum.MassSpectrum`
		:param bottom_label: A label for the spectrum in the bottom half of the panel
		:type bottom_label: str, optional
		"""
		
		ChartPanelBase.clear(self)
		
		# Normalize the mass spectrum
		self.bottom_mass_spec = normalize_mass_spec(bottom_mass_spec)
		if bottom_label:
			self.bottom_label = bottom_label
		self.plotted = False
	
	def plot_head2tail(self, top_mass_spec=None, bottom_mass_spec=None, top_label='', bottom_label=''):
		"""
		Display the Spectrum

		:param top_mass_spec: The Mass Spectrum to plot in the top half of the panel, or None
		:type top_mass_spec: :class:`pyms.Spectrum.MassSpectrum` or None, optional
		:param bottom_mass_spec: The Mass Spectrum to plot in the bottom half of the panel, or None
		:type bottom_mass_spec: :class:`pyms.Spectrum.MassSpectrum` or None, optional
		:param top_label: A label for the spectrum in the top half of the panel
		:type top_label: str, optional
		:param bottom_label: A label for the spectrum in the bottom half of the panel
		:type bottom_label: str, optional

		If any of top_mass_spec, bottom_mass_spec, top_label and/or bottom_label are unspecified,
		the values from __init__, set_mass_specs, set_top_mass_spec and/or set_bottom_mass_spec are used.

		:raises: ValueError if top_mass_spec is None and it was not defined previously.
		:raises: ValueError if bottom_mass_spec is None and it was not defined previously.
		"""
		
		if top_mass_spec:
			self.set_top_mass_spec(top_mass_spec, top_label)
		if self.top_mass_spec is None:
			raise ValueError("`top_mass_spec` cannot be None")
		
		if bottom_mass_spec:
			self.set_bottom_mass_spec(bottom_mass_spec, bottom_label)
		if self.bottom_mass_spec is None:
			raise ValueError("`bottom_mass_spec` cannot be None")
		
		self.ax.clear()
		
		plot_head2tail(
				self.ax,
				top_mass_spec=self.top_mass_spec,
				bottom_mass_spec=self.bottom_mass_spec,
				top_spec_kwargs=dict(label=self.top_label),
				bottom_spec_kwargs=dict(label=self.bottom_label),
				)
		
		top_spec_masses = set(self.top_mass_spec.mass_list)
		bottom_spec_masses = set(self.bottom_mass_spec.mass_list)
		self.all_masses = list(top_spec_masses | bottom_spec_masses)
		self.all_masses.sort()
		
		self.legend = self.ax.legend()
		
		self.ax.set_xlabel("m/z", style="italic")
		self.ax.set_ylabel("Normalized Intensity")
		
		self.fig.tight_layout()
		self.canvas.draw()
		
		self.setup_ylim_refresher()
		
		self.plotted = True
	
	def clear(self):
		self.top_mass_spec = None
		self.bottom_mass_spec = None
		self.top_label = None
		self.bottom_label = None
		self.all_masses = None
		self.legend = None
		self.plotted = False
		ChartPanelBase.clear(self)
	
	def rescale_y(self, *_):
		min_x_index, max_x_index = self.get_current_x_index_range(self.all_masses)
		
		# Find y values
		top_spec_int_for_range = self.get_int_for_range(
				mass_spec=self.top_mass_spec,
				min_x_index=min_x_index,
				max_x_index=max_x_index,
				)
		
		# Find y values for bottom mass spec
		bottom_spec_int_for_range = self.get_int_for_range(
				mass_spec=self.bottom_mass_spec,
				min_x_index=min_x_index,
				max_x_index=max_x_index,
				)
		
		self.ax.set_ylim(
				bottom=-max(bottom_spec_int_for_range) * 1.1,
				top=max(top_spec_int_for_range) * 1.1,
				)
		
		self.fig.canvas.draw()
		self.size_change()
		
	def rescale_x(self, *_):
		top_spec_masses = set(self.top_mass_spec.mass_list)
		bottom_spec_masses = set(self.bottom_mass_spec.mass_list)
		all_masses = list(top_spec_masses | bottom_spec_masses)
		all_masses.sort()
		
		self.do_rescale_x(all_masses)
	
	def setup_ylim_refresher(self, *args, **kwargs):

		def update_ylim(*args):
			print("update_ylim")
			# print(*args)
			# print(str(*args).startswith("MPL MouseEvent")) # Pan
			if (
					str(*args).startswith("XPanAxesSubplot") and self.current_canvas_mode != "PAN"
				) or (
					str(*args).startswith("MPL MouseEvent") and self.current_canvas_mode != "ZOOM"
				):
				
				self.rescale_y()
		
		self.ax.callbacks.connect('xlim_changed', update_ylim)
		self.fig.canvas.callbacks.connect("button_release_event", update_ylim)

	def get_int_for_range(self, mass_spec, min_x_index, max_x_index):
		# Find y values for range
		y_vals_for_range = []
		
		for idx in range(min_x_index, max_x_index):
			mass = self.all_masses[idx]
			try:
				y_vals_for_range.append(mass_spec.get_intensity_for_mass(mass))
			except ValueError:
				pass
		
		return y_vals_for_range
