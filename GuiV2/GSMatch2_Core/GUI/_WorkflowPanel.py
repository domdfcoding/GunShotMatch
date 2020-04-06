#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  _WorkflowPanel.py
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
# generated by wxGlade 0.9.3 on Tue Nov 26 10:17:30 2019
#


# 3rd party
import wx
import wx.grid
import wx.html

from domdf_wxpython_tools import collapse_label

# this package


# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class _WorkflowPanel(wx.Panel):
	def __init__(self, *args, **kwds):
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
		
		# begin wxGlade: _WorkflowPanel.__init__
		kwds["style"] = kwds.get("style", 0) | wx.TAB_TRAVERSAL
		wx.Panel.__init__(self, *args, **kwds)
		self.workflow_main_panel = wx.Panel(self, wx.ID_ANY)
		self.workflow_scroller = wx.ScrolledWindow(self.workflow_main_panel, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
		self.grid_main_options_panel = wx.Panel(self.workflow_scroller, wx.ID_ANY)
		self.quick_start_guide_btn = wx.Button(self.grid_main_options_panel, wx.ID_ANY, "Quick Start Guide", style=wx.BORDER_NONE)
		self.main_options_line = wx.StaticLine(self.grid_main_options_panel, wx.ID_ANY)
		self.grid_project_panel = wx.Panel(self.workflow_scroller, wx.ID_ANY)
		self.project_header = wx.Button(self.grid_project_panel, wx.ID_ANY, "Project", style=wx.BORDER_NONE | wx.BU_LEFT)
		self.project_panel = wx.Panel(self.grid_project_panel, wx.ID_ANY)
		self.project_line = wx.StaticLine(self.grid_project_panel, wx.ID_ANY)
		self.grid_analysis_panel = wx.Panel(self.workflow_scroller, wx.ID_ANY)
		self.analysis_header = wx.Button(self.grid_analysis_panel, wx.ID_ANY, "Analysis", style=wx.BORDER_NONE | wx.BU_LEFT)
		self.analysis_panel = wx.Panel(self.grid_analysis_panel, wx.ID_ANY)
		self.analysis_panel_a = wx.Panel(self.analysis_panel, wx.ID_ANY)
		self.alignment_checkbox = wx.CheckBox(self.analysis_panel_a, wx.ID_ANY, "")
		self.alignment_btn = wx.Button(self.analysis_panel_a, wx.ID_ANY, "Run Peak Alignment", style=wx.BORDER_NONE)
		self.identify_checkbox = wx.CheckBox(self.analysis_panel_a, wx.ID_ANY, "")
		self.identify_btn = wx.Button(self.analysis_panel_a, wx.ID_ANY, "Identify Compounds", style=wx.BORDER_NONE)
		self.consolidate_checkbox = wx.CheckBox(self.analysis_panel_a, wx.ID_ANY, "")
		self.consolidate_btn = wx.Button(self.analysis_panel_a, wx.ID_ANY, "Run Consolidate", style=wx.BORDER_NONE)
		self.analysis_panel_b = wx.Panel(self.analysis_panel, wx.ID_ANY)
		self.spectra_checkbox = wx.CheckBox(self.analysis_panel_b, wx.ID_ANY, "")
		self.spectra_btn = wx.Button(self.analysis_panel_b, wx.ID_ANY, "Generate Spectra", style=wx.BORDER_NONE)
		self.charts_checkbox = wx.CheckBox(self.analysis_panel_b, wx.ID_ANY, "")
		self.charts_btn = wx.Button(self.analysis_panel_b, wx.ID_ANY, "Generate Charts", style=wx.BORDER_NONE)
		self.run_analysis_btn = wx.Button(self.analysis_panel_b, wx.ID_ANY, "Run Selected Steps")
		self.grid_charts_panel = wx.Panel(self.workflow_scroller, wx.ID_ANY)
		self.charts_header = wx.Button(self.grid_charts_panel, wx.ID_ANY, "Charts", style=wx.BORDER_NONE | wx.BU_LEFT)
		self.charts_panel = wx.Panel(self.grid_charts_panel, wx.ID_ANY)
		self.radar_chart_btn = wx.Button(self.charts_panel, wx.ID_ANY, "Create Radar Chart", style=wx.BORDER_NONE)
		self.bar_chart_btn = wx.Button(self.charts_panel, wx.ID_ANY, "Create Bar Chart", style=wx.BORDER_NONE)
		self.bw_chart_btn = wx.Button(self.charts_panel, wx.ID_ANY, "Create Box & Whisker Plot", style=wx.BORDER_NONE)
		self.pca_chart_btn = wx.Button(self.charts_panel, wx.ID_ANY, "Create PCA Plot", style=wx.BORDER_NONE)
		self.charts_line = wx.StaticLine(self.grid_charts_panel, wx.ID_ANY)

		self.__set_properties()
		self.__do_layout()

		self.Bind(wx.EVT_BUTTON, self.collapse_project, self.project_header)
		self.Bind(wx.EVT_BUTTON, self.collapse_analysis, self.analysis_header)
		self.Bind(wx.EVT_BUTTON, self.collapse_charts, self.charts_header)
		# end wxGlade
		
		# Setup Collapse Buttons
		self.project_header.SetLabel(collapse_label("Project", False))
		self.charts_header.SetLabel(collapse_label("Charts", False))
		self.analysis_header.SetLabel(collapse_label("Analysis", False))
		
		self.current_layout = 0

	def __set_properties(self):
		# begin wxGlade: _WorkflowPanel.__set_properties
		self.project_header.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
		self.project_header.Hide()
		self.project_panel.Hide()
		self.project_line.Hide()
		self.analysis_header.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
		self.charts_header.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
		self.workflow_scroller.SetScrollRate(10, 10)
		# end wxGlade

	def __do_layout(self):
		# begin wxGlade: _WorkflowPanel.__do_layout
		workflow_sizer = wx.GridSizer(1, 1, 0, 0)
		workflow_outer_sizer = wx.BoxSizer(wx.VERTICAL)
		self.workflow_grid_sizer = wx.FlexGridSizer(4, 1, 0, 0)
		grid_charts_sizer = wx.BoxSizer(wx.VERTICAL)
		charts_sizer = wx.BoxSizer(wx.VERTICAL)
		grid_analysis_sizer = wx.BoxSizer(wx.VERTICAL)
		self.analysis_grid = wx.FlexGridSizer(2, 1, 0, 0)
		analysis_sizer_b = wx.FlexGridSizer(4, 2, 0, 0)
		analysis_sizer_a = wx.FlexGridSizer(3, 2, 0, 0)
		grid_project_sizer = wx.BoxSizer(wx.VERTICAL)
		project_sizer = wx.BoxSizer(wx.VERTICAL)
		grid_main_options_sizer = wx.BoxSizer(wx.VERTICAL)
		grid_main_options_sizer.Add(self.quick_start_guide_btn, 0, 0, 0)
		grid_main_options_sizer.Add((0, 0), 0, 0, 0)
		grid_main_options_sizer.Add(self.main_options_line, 0, wx.EXPAND | wx.TOP, 5)
		self.grid_main_options_panel.SetSizer(grid_main_options_sizer)
		self.workflow_grid_sizer.Add(self.grid_main_options_panel, 1, wx.EXPAND, 0)
		grid_project_sizer.Add(self.project_header, 0, 0, 5)
		project_sizer.Add((0, 0), 0, 0, 0)
		self.project_panel.SetSizer(project_sizer)
		grid_project_sizer.Add(self.project_panel, 0, wx.EXPAND | wx.LEFT, 20)
		grid_project_sizer.Add(self.project_line, 0, wx.EXPAND | wx.TOP, 5)
		self.grid_project_panel.SetSizer(grid_project_sizer)
		self.workflow_grid_sizer.Add(self.grid_project_panel, 1, wx.EXPAND, 0)
		grid_analysis_sizer.Add(self.analysis_header, 0, 0, 5)
		analysis_sizer_a.Add(self.alignment_checkbox, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		analysis_sizer_a.Add(self.alignment_btn, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		analysis_sizer_a.Add(self.identify_checkbox, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		analysis_sizer_a.Add(self.identify_btn, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		analysis_sizer_a.Add(self.consolidate_checkbox, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		analysis_sizer_a.Add(self.consolidate_btn, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		self.analysis_panel_a.SetSizer(analysis_sizer_a)
		self.analysis_grid.Add(self.analysis_panel_a, 1, wx.EXPAND, 0)
		analysis_sizer_b.Add(self.spectra_checkbox, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		analysis_sizer_b.Add(self.spectra_btn, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		analysis_sizer_b.Add(self.charts_checkbox, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		analysis_sizer_b.Add(self.charts_btn, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		static_line_5 = wx.StaticLine(self.analysis_panel_b, wx.ID_ANY)
		analysis_sizer_b.Add(static_line_5, 0, 0, 0)
		static_line_6 = wx.StaticLine(self.analysis_panel_b, wx.ID_ANY)
		analysis_sizer_b.Add(static_line_6, 0, 0, 0)
		analysis_sizer_b.Add((0, 0), 0, 0, 0)
		analysis_sizer_b.Add(self.run_analysis_btn, 0, 0, 0)
		self.analysis_panel_b.SetSizer(analysis_sizer_b)
		self.analysis_grid.Add(self.analysis_panel_b, 1, wx.EXPAND, 0)
		self.analysis_panel.SetSizer(self.analysis_grid)
		grid_analysis_sizer.Add(self.analysis_panel, 0, wx.EXPAND | wx.LEFT, 20)
		analysis_line = wx.StaticLine(self.grid_analysis_panel, wx.ID_ANY)
		grid_analysis_sizer.Add(analysis_line, 0, wx.EXPAND | wx.TOP, 5)
		self.grid_analysis_panel.SetSizer(grid_analysis_sizer)
		self.workflow_grid_sizer.Add(self.grid_analysis_panel, 1, wx.EXPAND, 0)
		grid_charts_sizer.Add(self.charts_header, 0, 0, 5)
		charts_sizer.Add(self.radar_chart_btn, 0, 0, 0)
		charts_sizer.Add(self.bar_chart_btn, 0, 0, 0)
		charts_sizer.Add(self.bw_chart_btn, 0, 0, 0)
		charts_sizer.Add(self.pca_chart_btn, 0, 0, 0)
		self.charts_panel.SetSizer(charts_sizer)
		grid_charts_sizer.Add(self.charts_panel, 0, wx.EXPAND | wx.LEFT, 20)
		grid_charts_sizer.Add(self.charts_line, 0, wx.EXPAND | wx.TOP, 5)
		self.grid_charts_panel.SetSizer(grid_charts_sizer)
		self.workflow_grid_sizer.Add(self.grid_charts_panel, 1, wx.EXPAND, 0)
		self.workflow_scroller.SetSizer(self.workflow_grid_sizer)
		workflow_outer_sizer.Add(self.workflow_scroller, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
		self.workflow_main_panel.SetSizer(workflow_outer_sizer)
		workflow_sizer.Add(self.workflow_main_panel, 1, wx.EXPAND, 0)
		self.SetSizer(workflow_sizer)
		workflow_sizer.Fit(self)
		self.Layout()
		# end wxGlade
		
		self.Bind(wx.EVT_SIZE, self.on_size)
	
		# self.on_size(0)
		
	def on_size(self, event):
		if not self.IsFrozen():
			self.Freeze()
		
		if self.GetSize().x >= 560 and self.current_layout != 3:
			self.Thaw()
			self.layout_3()
			self.Freeze()
		elif 400 < self.GetSize().x < 560 and self.current_layout != 2:
			self.Thaw()
			self.layout_2()
			self.Freeze()
		elif self.GetSize().x <= 400 and self.current_layout != 1:
			self.Thaw()
			self.layout_1()
			self.Freeze()
		
		event.Skip()
		self.Thaw()
	
	def collapse_project(self, event):  # wxGlade: _WorkflowPanel.<event_handler>
		"""
		Collapse the project section of the workflow

		:param event:
		:type event:
		"""
		
		if not self.project_panel.Hide():
			self.project_panel.Show()
			self.project_header.SetLabel(collapse_label("Project", False))
		else:
			self.project_header.SetLabel(collapse_label("Project"))
		self.Layout()
		event.Skip()
		
	def collapse_charts(self, event):  # wxGlade: _WorkflowPanel.<event_handler>
		if not self.charts_panel.Hide():
			self.charts_panel.Show()
			self.charts_header.SetLabel(collapse_label("Charts", False))
		else:
			self.charts_header.SetLabel(collapse_label("Charts"))
		self.Layout()
		event.Skip()
	
	def collapse_analysis(self, event):  # wxGlade: _WorkflowPanel.<event_handler>
		if not self.analysis_panel.Hide():
			self.analysis_panel.Show()
			self.analysis_header.SetLabel(collapse_label("Analysis", False))
		else:
			self.analysis_header.SetLabel(collapse_label("Analysis"))
		self.Layout()
		event.Skip()
	
	def layout_1(self):
		# One column
		self.workflow_grid_sizer.SetCols(1)
		self.analysis_grid.SetCols(1)
		self.current_layout = 1
		self.Layout()
		self.Refresh()
		
	def layout_2(self):
		# Two column
		self.workflow_grid_sizer.SetCols(2)
		self.analysis_grid.SetCols(1)
		self.current_layout = 2
		self.Layout()
		self.Refresh()
		
	def layout_3(self):
		# Two columns and two columns in the analysis section
		self.workflow_grid_sizer.SetCols(2)
		self.analysis_grid.SetCols(2)
		self.current_layout = 3
		self.Layout()
		self.Refresh()
	
# end of class _WorkflowPanel
