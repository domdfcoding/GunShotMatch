#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
# 
#  experiment_data_panel.py
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
import time
import webbrowser

# 3rd party
import wx
import wx.propgrid
from domdf_wxpython_tools import file_dialog_wildcard
# from GuiV2.GSMatch2_Core.SpectrumFrame import SpectrumFrame
from mathematical.utils import rounders

# this package
from GuiV2.GSMatch2_Core import Experiment, Method, SorterPanels
from GuiV2.GSMatch2_Core.Base import ProjExprPanelBase
from GuiV2.GSMatch2_Core.Config import internal_config
from GuiV2.GSMatch2_Core.SpectrumFrame import SpectrumFrame


class ExperimentDataPanel(ProjExprPanelBase):
	def __init__(
			self, experiment, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
			size=wx.DefaultSize, style=0, name="ExperimentDataPanel"):
		"""
		:param parent: The parent window.
		:type parent: wx.Window
		:param id: An identifier for the panel. wx.ID_ANY is taken to mean a default.
		:type id: wx.WindowID, optional
		:param pos: The panel position. The value wx.DefaultPosition indicates a default position,
		chosen by either the windowing system or wxWidgets, depending on platform.
		:type pos: wx.Point, optional
		:param size: The panel size. The value wx.DefaultSize indicates a default size, chosen by
		either the windowing system or wxWidgets, depending on platform.
		:type size: wx.Size, optional
		:param style: The window style. See wx.Panel.
		:type style: int, optional
		:param name: Window name.
		:type name: str, optional
		"""
		
		self.experiment = experiment
		
		ProjExprPanelBase.__init__(self, parent, id=id, pos=pos, size=size, style=style | wx.TAB_TRAVERSAL, name=name)
		
		# Make tabs
		self.experiment_tic = None
		self.make_tic_tab()
		
		self.method_tab = None
		self.make_method_tab()
		
		self.experiment_peaks = None
		self.make_peak_list_tab()

		self.ident_panel = None
		if self.experiment.identification_performed:
			self.add_ident_tab()
		
		self.experiment._unsaved_changes = False
		self.experiment.ammo_details_unsaved = False
		self.experiment.method_unsaved = False

	def add_experiment_peak_list_tab(self):
		for tab_idx in range(self.notebook.GetPageCount()):
			if self.notebook.GetPageText(tab_idx) == "Peak List":
				# tab is already open
				return
		
		# Tab is not open
		self.notebook.AddPage(self.experiment_peaks, "Peak List", select=True)
	
	def add_tab(self, tab_name):
		
		if tab_name == "Method":
			self.add_method_tab()
		elif tab_name == "Peak List":
			self.add_experiment_peak_list_tab()
	
	def add_ident_tab(self):
		if self.notebook.GetPageIndex(self.ident_panel) != wx.NOT_FOUND:
			# Tab already exists
			return
		
		self.ident_panel = Experiment.IdentificationPanel(self, self.experiment.ident_peaks)
		self.notebook.AddPage(self.ident_panel, "Compounds", select=True)
	
	def export_compounds_pdf(self, input_filename, output_filename):
		Experiment.CompoundsPDFExporter(
				self.experiment,
				input_filename=input_filename,
				output_filename=output_filename,
				)
		
	def export_pdf(self, input_filename):
		selected_page = self.get_selected_page()
		
		exportable_pages = {self.experiment_peaks, self.ident_panel}
		
		if (selected_page in exportable_pages) or hasattr(selected_page, "export_pdf"):
			
			filename = file_dialog_wildcard(
					self,
					title="Export PDF",
					wildcard="PDF Files (*.pdf)|*.pdf;*.PDF",
					defaultDir=str(internal_config.last_export)
					)
			
			if filename:
				internal_config.last_export = filename[0]
				
				if selected_page == self.experiment_peaks:
					self.export_peak_list_pdf(input_filename, output_filename=filename[0])
				if selected_page == self.ident_panel:
					self.export_compounds_pdf(input_filename, output_filename=filename[0])
				elif hasattr(selected_page, "export_pdf"):
					selected_page.export_pdf(input_filename, output_filename=filename[0])
				
				time.sleep(1)
				webbrowser.open(filename[0])
		
		else:
			wx.MessageBox("The current page does not support exporting to PDF.", "Unsupported")
	
	def export_peak_list_pdf(self, input_filename, output_filename):
		Experiment.PeakListPDFExporter(
				self.experiment,
				input_filename=input_filename,
				output_filename=output_filename,
				)

	def make_tic_tab(self):
		self.experiment_tic = Experiment.ChromatogramPanel(self.experiment, self.notebook, wx.ID_ANY)
		self.notebook.AddPage(self.experiment_tic, "TIC")
	
	def make_method_tab(self):
		self.do_make_method_tab(self.experiment.method_data, editable=False)
		self.method_tab.filename_value.SetValue(str(self.experiment.method))
	
	def do_make_method_tab(self, method, editable=True):
		self.method_tab = Method.MethodPGPanel(self.notebook, method=method, editable=editable)
		self.notebook.AddPage(self.method_tab, "Method", select=True)
	
	def make_peak_list_tab(self):
		self.experiment_peaks = SorterPanels.SorterPanel(self.notebook, wx.ID_ANY)
		self.experiment_peaks.AppendColumn("UID", format=wx.LIST_FORMAT_LEFT, width=150)
		self.experiment_peaks.AppendColumn("RT", format=wx.LIST_FORMAT_RIGHT, width=80)
		self.experiment_peaks.AppendColumn("Area", format=wx.LIST_FORMAT_RIGHT, width=130)
		
		for peak_idx, peak in enumerate(self.experiment.peak_list_data):
			peak_data = (peak.UID, rounders(peak.rt / 60, "0.000"), f'{rounders(peak.area, "0.000"):,}')
			self.experiment_peaks.Append(peak_data)
		
		self.notebook.AddPage(self.experiment_peaks, "Peak List")
	
	@property
	def name(self):
		return self.experiment.name
	
	def view_spectrum(self, *, rt=None, num=None):
		"""

		:param rt: Retention Time in minutes
		:type rt: float
		:param num: Scan Number
		:type num: int
		:return:
		:rtype:
		"""
		
		if not rt and not num:
			raise ValueError("Either 'rt' or 'num' is required!")
		
		if rt and num:
			raise ValueError("Only specify one of 'rt' or 'num'!")
		
		if rt:
			if not isinstance(rt, float):
				raise TypeError("'rt' must be a float")
			print(f"Loading Spectrum at retention time: {rt} minutes")
		
		if num:
			if not isinstance(num, int):
				raise TypeError("'num' must be an int")
			print(f"Loading Spectrum with scan number: {num}")
			# TODO: Get the scan from the experiment and pass it to the spectrum frame
			# SpectrumFrame(self, self.experiment, scan_number=num).Show()
		
# end of class ExperimentDataPanel
