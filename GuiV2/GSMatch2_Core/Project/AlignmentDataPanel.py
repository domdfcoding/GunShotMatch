#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  AlignmentDataPanel.py
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
# generated by wxGlade 0.9.3 on Wed Dec  4 09:44:16 2019
#


# stdlib
from collections import Counter

# 3rd party
import numpy
import wx
import wx.propgrid
from mathematical.utils import rounders
from pubsub import pub

# this package
from GuiV2.GSMatch2_Core import Project, SorterPanels
from GuiV2.icons import get_icon


# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class AlignmentDataPanel(wx.Panel):
	def __init__(
			self, parent, project, id=wx.ID_ANY, pos=wx.DefaultPosition,
			size=wx.DefaultSize, style=0, name="AlignmentDataPanel"
			):
		"""
		TODO: Does this need to be a sorter panel or would a simple listctrl suffice?
		
		:param parent: The parent window.
		:type parent: wx.Window
		:param project:
		:type project:
		:param id: An identifier for the panel. ID_ANY is taken to mean a default.
		:type id: wx.WindowID, optional
		:param pos: The panel position. The value wx.DefaultPosition indicates a default position, chosen by either the windowing system or wxWidgets, depending on platform.
		:type pos: wx.Point, optional
		:param size: The panel size. The value wx.DefaultSize indicates a default size, chosen by either the windowing system or wxWidgets, depending on platform.
		:type size: wx.Size, optional
		:param style: The window style. See wx.Panel.
		:type style: int, optional
		:param name: Window name
		:type name: str, optional
		"""
		
		args = (parent, id)
		kwds = dict(pos=pos, size=size, style=style, name=name)
		
		self.parent = parent
		self.project = project
		
		# begin wxGlade: AlignmentDataPanel.__init__
		kwds["style"] = kwds.get("style", 0) | wx.TAB_TRAVERSAL
		wx.Panel.__init__(self, *args, **kwds)
		self.filter_button = wx.BitmapButton(self, wx.ID_ANY, get_icon("data-filter", 32))
		self.alignment_table = SorterPanels.SorterPanel(self, wx.ID_ANY)

		self.__set_properties()
		self.__do_layout()

		self.Bind(wx.EVT_BUTTON, self.on_filter_peaks, self.filter_button)
		# end wxGlade
		
		self.alignment_table.AppendColumn("Peak No.", format=wx.LIST_FORMAT_LEFT, width=80)
		
		for experiment in self.project.experiment_name_list:
			self.alignment_table.AppendColumn(experiment, format=wx.LIST_FORMAT_RIGHT, width=120)
		
		self.Bind(SorterPanels.myEVT_SORTER_PANEL_DCLICK, self.on_item_dclick)
		self.Bind(SorterPanels.myEVT_SORTER_PANEL_RCLICK, self.on_right_click)
		self.Bind(wx.EVT_BUTTON, self.apply_filter, id=wx.ID_APPLY)
		self.Bind(wx.EVT_BUTTON, self.apply_filter, id=wx.ID_OK)
		
		self.default_filter_settings()
		
		self._populate_table()
		
		self.filter_dialog = Project.AlignmentFilterDialog(self)
		
		# self.alignment_table.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)
		
	def __set_properties(self):
		# begin wxGlade: AlignmentDataPanel.__set_properties
		self.filter_button.SetToolTip("Filter")
		self.filter_button.SetSize(self.filter_button.GetBestSize())
		# end wxGlade

	def __do_layout(self):
		# begin wxGlade: AlignmentDataPanel.__do_layout
		outer_sizer = wx.BoxSizer(wx.VERTICAL)
		grid_sizer_1 = wx.FlexGridSizer(1, 2, 0, 0)
		explanatory_text = wx.StaticText(self, wx.ID_ANY, "The table below shows the retention times, in minutes, for the aligned peaks in each of the Experiments. \n\nDouble click on a retention time to view the mass spectrum for that peak.")
		grid_sizer_1.Add(explanatory_text, 1, wx.ALL | wx.EXPAND, 10)
		grid_sizer_1.Add(self.filter_button, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT | wx.ALL, 10)
		outer_sizer.Add(grid_sizer_1, 0, wx.EXPAND, 0)
		outer_sizer.Add(self.alignment_table, 1, wx.EXPAND, 0)
		self.SetSizer(outer_sizer)
		outer_sizer.Fit(self)
		self.Layout()
		# end wxGlade
	
	def default_filter_settings(self):
		self.filter_min_experiments = 1
		self.min_rt = 0
		self.max_rt = 0
		
		for peak in self.project.rt_alignment.itertuples():
			row_max_rt = numpy.nanmax(peak[1:])
			row_min_rt = numpy.nanmin(peak[1:])
			if row_max_rt > self.max_rt:
				self.max_rt = row_max_rt
			if row_min_rt < self.min_rt:
				self.min_rt = row_min_rt
				
		self.filter_min_rt = self.min_rt
		self.filter_max_rt = self.max_rt
		self.n_experiments = len(peak)-1

	def _populate_table(self):
		for peak in self.project.rt_alignment.itertuples():
			
			row_data = []
			
			for experiment in peak:
				rt = rounders(experiment, "0.00000")
				if rt.is_nan():
					rt = "-"
				row_data.append(rt)
			
			row_data[0] = peak.Index
			if self.n_experiments - Counter(row_data)["-"] >= self.filter_min_experiments:
				for experiment in row_data[1:]:
					if experiment != "-":
						if self.filter_min_rt <= experiment <= self.filter_max_rt:
							self.alignment_table.Append(row_data)
							break  # As long as one of the peaks is in range, add the peak

	def on_item_dclick(self, event):
		self.on_view_spectra(event)
		
	def on_view_spectra(self, event):
		row, col = self.alignment_table.GetDoubleClickedCell()
		selected_experiment = self.project.experiment_name_list[col - 1]
		retention_time = self.project.rt_alignment[selected_experiment][row]
		
		print(
				f"Now the Mass Spectrum needs to be opened for "
				f"'{selected_experiment}' at retention time {retention_time}"
				)
		
		event.Skip()
	
	def on_right_click(self, event):
		row, col = self.alignment_table.GetDoubleClickedCell()
		peak_number = self.project.rt_alignment.index.values[row]
		
		menu = wx.Menu()
		
		item1 = menu.Append(wx.ID_ANY, "View Spectra")
		self.Bind(wx.EVT_MENU, self.on_view_spectra, item1)

		if hasattr(self.parent.Parent, "compounds_tab"):
			if hasattr(self.parent.Parent.compounds_tab, "ident_panel"):
				if self.parent.Parent.compounds_tab.ident_panel:
					if peak_number in self.parent.Parent.compounds_tab.ident_panel.peak_numbers:
						item2 = menu.Append(wx.ID_ANY, "View Identified Compounds")
						self.Bind(wx.EVT_MENU, self.on_view_compounds, item2)
						
						if hasattr(self.parent.Parent.compounds_tab, "ident_panel"):
							item3 = menu.Append(wx.ID_ANY, "View Consolidated Results")
							self.Bind(wx.EVT_MENU, self.on_view_consolidated, item3)
		
		self.PopupMenu(menu)
		menu.Destroy()
		event.Skip()
	
	def on_view_consolidated(self, _):
		row, col = self.alignment_table.GetDoubleClickedCell()
		peak_number = self.project.rt_alignment.index.values[row]
		wx.CallAfter(pub.sendMessage, "view_peak_in_consolidated", peak_number=peak_number)
	
	def on_view_compounds(self, event):
		row, col = self.alignment_table.GetDoubleClickedCell()
		peak_number = self.project.rt_alignment.index.values[row]
		pub.sendMessage("display_compounds_for_peak", peak_number=peak_number)
		event.Skip()
	
	def apply_filter(self):
		self.alignment_table.DeleteAllItems()

		self._populate_table()
		
	def on_filter_peaks(self, _):  # wxGlade: AlignmentDataPanel.<event_handler>
		if self.filter_dialog.IsShownOnScreen():
			wx.CallAfter(self.filter_dialog.SetFocus)
			wx.CallAfter(self.filter_dialog.Raise)
		else:
			self.filter_dialog.Show()
	
	def export_pdf(self, input_filename, output_filename):
		Project.AlignmentPDFExporter(
				self,
				input_filename=input_filename,
				output_filename=output_filename,
				)
	
	def filter_is_default(self):
		return \
			self.filter_min_rt == self.min_rt \
			and self.filter_max_rt == self.max_rt \
			and self.filter_min_experiments == 1
	
# end of class AlignmentDataPanel
