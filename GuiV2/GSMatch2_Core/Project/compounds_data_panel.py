#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
# 
#  compounds_data_panel.py
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
from domdf_wxpython_tools import file_dialog_wildcard

# this package
from GuiV2.GSMatch2_Core import Experiment
from GuiV2.GSMatch2_Core.Base import NotebookPanelBase
from GuiV2.GSMatch2_Core.Config import internal_config
from GuiV2.GSMatch2_Core.Project.consolidate import (
	ConsolidatedResultsPanel,
	)
from GuiV2.GSMatch2_Core.Project.DataViewer import DataViewer
# from GuiV2.GSMatch2_Core.SpectrumFrame import SpectrumFrame


class CompoundsDataPanel(NotebookPanelBase):
	def __init__(
			self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
			size=wx.DefaultSize, style=0, name="CompoundsDataPanel"):
		"""
		:param parent: The parent window.
		:type parent: :class:`GuiV2.GSMatch2_Core.Project.project_data_panel.ProjectDataPanel`
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
		
		NotebookPanelBase.__init__(self, parent, id=id, pos=pos, size=size, style=style | wx.TAB_TRAVERSAL, name=name)

		self._do_layout()
		
		self.ident_panel = None
		self.consolidate_panel = None
		self.data_panel = None
		
		if any(experiment.identification_performed for experiment in self.project.experiment_objects):
			self.add_ident_tab()
		
		if self.project.consolidate_performed:
			self.add_consolidate_tab()
		
			self.add_data_tab()
		
		self.notebook.SetSelection(0)
	
	@property
	def project(self):
		# Case for parent being a notebook
		if self.Parent.Name == "ProjectDataPanel":
			return self.Parent.project
		else:
			return self.Parent.Parent.project
	
	def show_single_peak(self, peak_number):
		self.switch_to_content("Single Peak")
		self.ident_panel.set_peak(peak_number)
		self.ident_panel.peak_number_combo.SetValue(str(peak_number))
		
	def view_in_dataviewer(self, peak_number):
		self.switch_to_content("Data Viewer")
		self.data_panel.set_peak(peak_number)
		self.data_panel.peak_number_combo.SetValue(str(peak_number))
	
	def add_tab(self, tab_name):
		
		if tab_name == "Consolidated":
			self.add_consolidate_tab()
		elif tab_name == "Single Peak":
			self.add_ident_tab()
	
	def add_ident_tab(self):
		if self.notebook.GetPageIndex(self.ident_panel) != wx.NOT_FOUND:
			# Tab already exists
			return
		
		self.ident_panel = Experiment.SinglePeakIdentificationPanel(self, self.project.experiment_objects)
		self.notebook.AddPage(self.ident_panel, "Single Peak", select=True)
	
	def remove_ident_tab(self):
		for tab_idx in range(self.notebook.GetPageCount()):
			if self.notebook.GetPage(tab_idx) == self.ident_panel:
				self.notebook.RemovePage(tab_idx)
				self.ident_panel.Destroy()
				self.ident_panel = None
				return
	
	def add_consolidate_and_data_tabs(self):
		print("Adding Consolidate tab")
		self.add_consolidate_tab()
		print("Adding Data tab")
		self.add_data_tab()
		print("Done adding tabs")
	
	def add_consolidate_tab(self):
		if self.notebook.GetPageIndex(self.consolidate_panel) != wx.NOT_FOUND:
			# Tab already exists
			return
		
		self.consolidate_panel = ConsolidatedResultsPanel(self, self.project.consolidated_peaks)
		self.notebook.AddPage(self.consolidate_panel, "Consolidated", select=True)
	
	def add_data_tab(self):
		if self.notebook.GetPageIndex(self.data_panel) != wx.NOT_FOUND:
			# Tab already exists
			return

		self.data_panel = DataViewer(self)
		self.notebook.AddPage(self.data_panel, "Data Viewer", select=True)

	def remove_consolidate_tab(self):
		for tab_idx in range(self.notebook.GetPageCount()):
			if self.notebook.GetPage(tab_idx) == self.consolidate_panel:
				self.notebook.RemovePage(tab_idx)
				self.consolidate_panel.Destroy()
				self.consolidate_panel = None
				return
			
	def remove_data_tab(self):
		for tab_idx in range(self.notebook.GetPageCount()):
			if self.notebook.GetPage(tab_idx) == self.data_panel:
				self.notebook.RemovePage(tab_idx)
				self.data_panel.Destroy()
				self.data_panel = None
				return
	
	def remove_consolidate_and_data_tabs(self):
		self.remove_consolidate_tab()
		self.remove_data_tab()
	
	def export_pdf(self, input_filename):
		selected_page = self.get_selected_page()
		
		if hasattr(selected_page, "export_pdf"):
			
			filename = file_dialog_wildcard(
					self,
					title="Export PDF",
					wildcard="PDF Files (*.pdf)|*.pdf;*.PDF",
					defaultDir=str(internal_config.last_export)
					)
			
			if filename:
				internal_config.last_export = filename[0]
				
				selected_page.export_pdf(input_filename, output_filename=filename[0])
				
				time.sleep(1)
				webbrowser.open(filename[0])
		
		else:
			wx.MessageBox("The current page does not support exporting to PDF.", "Unsupported")

# end of class ExperimentDataPanel
