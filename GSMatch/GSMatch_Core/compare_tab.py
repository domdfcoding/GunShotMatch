#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  compare_tab.py
"""Tab for comparing two sets of samples"""
#
#  This file is part of GunShotMatch
#
#  Copyright © 2019 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import configparser

# 3rd party
import wx
import wx.html2

from domdf_wxpython_tools import file_dialog
from domdf_wxpython_tools import get_toolbar_icon
from domdf_wxpython_tools import LogCtrl as Log

# this package
from GSMatch.GSMatch_Core import ChartViewer, pretty_name_from_info
from GSMatch.GSMatch_Core.threads import ComparisonThread, EVT_COMPARISON_LOG


# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class compare_tab(wx.Panel):
	def __init__(self, parent, *args, **kwds):
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
		
		self._parent = parent
		# begin wxGlade: compare_tab.__init__
		kwds["style"] = kwds.get("style", 0) | wx.TAB_TRAVERSAL
		wx.Panel.__init__(self, *args, **kwds)
		self.comparison_panel = wx.Panel(self, wx.ID_ANY)
		self.comparison_left_picker = wx.TextCtrl(self.comparison_panel, wx.ID_ANY, "", style=wx.TE_READONLY)
		self.comparison_left_browse_btn = wx.BitmapButton(self.comparison_panel, wx.ID_ANY, get_toolbar_icon("ART_FILE_OPEN", 16))
		self.comparison_left_header = wx.html2.WebView.New(self.comparison_panel, wx.ID_ANY)
		self.comparison_right_picker = wx.TextCtrl(self.comparison_panel, wx.ID_ANY, "", style=wx.TE_READONLY)
		self.comparison_right_browse_btn = wx.BitmapButton(self.comparison_panel, wx.ID_ANY, get_toolbar_icon("ART_FILE_OPEN", 16))
		self.comparison_right_header = wx.html2.WebView.New(self.comparison_panel, wx.ID_ANY)
		self.comparison_alignment_Dw_value = wx.SpinCtrlDouble(self.comparison_panel, wx.ID_ANY, "0.0", min=0.0, max=99.0)
		self.comparison_alignment_Dw_value.SetDigits(2)
		self.comparison_alignment_Gw_value = wx.SpinCtrlDouble(self.comparison_panel, wx.ID_ANY, "0.0", min=0.0, max=99.0)
		self.comparison_alignment_Gw_value.SetDigits(2)
		self.comparison_alignment_min_peaks_value = wx.SpinCtrlDouble(self.comparison_panel, wx.ID_ANY, "0.0", min=0.0, max=99.0)
		self.significance_level_value = wx.SpinCtrlDouble(self.comparison_panel, wx.ID_ANY, "0.05", min=0.0, max=1.0)
		self.significance_level_value.SetDigits(3)
		self.comparison_apply_btn = wx.Button(self.comparison_panel, wx.ID_ANY, "Apply")
		self.comparison_default_btn = wx.Button(self.comparison_panel, wx.ID_ANY, "Default")
		self.comparison_reset_btn = wx.Button(self.comparison_panel, wx.ID_ANY, "Reset")
		self.run_comparison_button = wx.Button(self.comparison_panel, wx.ID_ANY, u"▶ Run Comparison")
		self.comparison_radar_button = wx.Button(self.comparison_panel, wx.ID_ANY, "Radar Chart")
		self.comparison_mean_pa_button = wx.Button(self.comparison_panel, wx.ID_ANY, "Mean Peak Area")
		self.comparison_box_whisker_btn = wx.Button(self.comparison_panel, wx.ID_ANY, "Box Whisker Plot")
		self.comparison_pca_btn = wx.Button(self.comparison_panel, wx.ID_ANY, "")
		self.comparison_log_text_control = Log(self.comparison_panel, wx.ID_ANY)

		self.__set_properties()
		self.__do_layout()

		self.Bind(wx.EVT_BUTTON, self.on_left_comparison_browse, self.comparison_left_browse_btn)
		self.Bind(wx.EVT_BUTTON, self.on_right_comparison_browse, self.comparison_right_browse_btn)
		self.Bind(wx.EVT_BUTTON, self.comparison_run, self.run_comparison_button)
		# end wxGlade
	
		self.Bind(wx.EVT_BUTTON, self.do_comparison_apply, self.comparison_apply_btn)
		self.Bind(wx.EVT_BUTTON, self.do_comparison_default, self.comparison_default_btn)
		self.Bind(wx.EVT_BUTTON, self.do_comparison_reset, self.comparison_reset_btn)
		self.Bind(wx.EVT_BUTTON, self.comparison_show_radar, self.comparison_radar_button)
		self.Bind(wx.EVT_BUTTON, self.comparison_show_box_whisker, self.comparison_box_whisker_btn)
		self.Bind(wx.EVT_BUTTON, self.comparison_show_mean_peak_area, self.comparison_mean_pa_button)
		self.Bind(wx.EVT_BUTTON, self.comparison_show_pca, self.comparison_pca_btn)
		
		self.Bind(EVT_COMPARISON_LOG, self.on_comparison_log)
		#self.comparison_log_text_control.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)

		self.comparison_right_project = None
		self.comparison_right_project_name = None
		self.comparison_left_project = None
		self.comparison_left_project_name = None
		
		#log_font = wx.Font(12, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, "FreeMono")
		#self.comparison_log_text_control.SetFont(log_font)
		
		self.do_comparison_reset()

	def onKeyPress(self, event):
		pass

	def __set_properties(self):
		# begin wxGlade: compare_tab.__set_properties
		self.comparison_left_picker.SetMinSize((171, -1))
		self.comparison_left_browse_btn.SetMinSize((29, 29))
		self.comparison_left_header.SetMinSize((200, 160))
		self.comparison_right_picker.SetMinSize((171, -1))
		self.comparison_right_browse_btn.SetMinSize((29, 29))
		self.comparison_right_header.SetMinSize((200, 160))
		self.comparison_alignment_Dw_value.SetMinSize((120, 29))
		self.comparison_alignment_Dw_value.SetIncrement(0.01)
		self.comparison_alignment_Gw_value.SetMinSize((120, 29))
		self.comparison_alignment_Gw_value.SetIncrement(0.01)
		self.comparison_alignment_min_peaks_value.SetMinSize((120, 29))
		self.significance_level_value.SetIncrement(0.001)
		self.run_comparison_button.Enable(False)
		self.comparison_radar_button.Enable(False)
		self.comparison_mean_pa_button.Enable(False)
		self.comparison_box_whisker_btn.Enable(False)
		self.comparison_pca_btn.Enable(False)
		self.comparison_pca_btn.SetLabel("Principal\nComponent\nAnalysis")
		# end wxGlade

	def __do_layout(self):
		# begin wxGlade: compare_tab.__do_layout
		comparison_parent_sizer = wx.BoxSizer(wx.VERTICAL)
		comparison_sizer = wx.BoxSizer(wx.HORIZONTAL)
		comparison_log_sizer = wx.BoxSizer(wx.VERTICAL)
		comparison_option_sizer = wx.BoxSizer(wx.VERTICAL)
		comparison_settings_grid = wx.FlexGridSizer(1, 3, 10, 10)
		comparison_button_sizer = wx.BoxSizer(wx.VERTICAL)
		comparison_settings_sizer = wx.BoxSizer(wx.VERTICAL)
		comparison_settings_button_sizer = wx.BoxSizer(wx.HORIZONTAL)
		comparison_alignment_grid = wx.FlexGridSizer(3, 2, 0, 0)
		comparison_alignment_Dw_sizer = wx.BoxSizer(wx.HORIZONTAL)
		comparison_pickers_grid = wx.FlexGridSizer(1, 3, 10, 10)
		comparison_right = wx.BoxSizer(wx.VERTICAL)
		comparison_right_picker_sizer = wx.BoxSizer(wx.HORIZONTAL)
		comparison_left = wx.BoxSizer(wx.VERTICAL)
		comparison_left_picker_sizer = wx.BoxSizer(wx.HORIZONTAL)
		comparison_left_label = wx.StaticText(self.comparison_panel, wx.ID_ANY, "Compare these Samples...", style=wx.ALIGN_LEFT)
		comparison_left.Add(comparison_left_label, 0, 0, 25)
		comparison_left_picker_sizer.Add(self.comparison_left_picker, 0, 0, 0)
		comparison_left_picker_sizer.Add(self.comparison_left_browse_btn, 0, 0, 0)
		comparison_left.Add(comparison_left_picker_sizer, 0, wx.BOTTOM | wx.TOP, 5)
		comparison_left.Add(self.comparison_left_header, 0, wx.EXPAND, 5)
		comparison_pickers_grid.Add(comparison_left, 1, wx.EXPAND, 0)
		comparison_picker_v_line = wx.StaticLine(self.comparison_panel, wx.ID_ANY, style=wx.LI_VERTICAL)
		comparison_pickers_grid.Add(comparison_picker_v_line, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		comparison_right_label = wx.StaticText(self.comparison_panel, wx.ID_ANY, "... To These Samples", style=wx.ALIGN_LEFT)
		comparison_right.Add(comparison_right_label, 0, 0, 25)
		comparison_right_picker_sizer.Add(self.comparison_right_picker, 0, 0, 0)
		comparison_right_picker_sizer.Add(self.comparison_right_browse_btn, 0, 0, 0)
		comparison_right.Add(comparison_right_picker_sizer, 0, wx.BOTTOM | wx.TOP, 5)
		comparison_right.Add(self.comparison_right_header, 0, wx.EXPAND, 5)
		comparison_pickers_grid.Add(comparison_right, 1, wx.EXPAND, 0)
		comparison_option_sizer.Add(comparison_pickers_grid, 1, wx.EXPAND, 10)
		static_line_3 = wx.StaticLine(self.comparison_panel, wx.ID_ANY)
		comparison_option_sizer.Add(static_line_3, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 10)
		comparison_settings_label = wx.StaticText(self.comparison_panel, wx.ID_ANY, "Settings")
		comparison_settings_label.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
		comparison_settings_sizer.Add(comparison_settings_label, 0, 0, 0)
		comparison_alignment_top_text = wx.StaticText(self.comparison_panel, wx.ID_ANY, "Dynamic Peak Alignment")
		comparison_alignment_top_text.SetToolTip("Settings for PyMS Dynamic Peak Alignment")
		comparison_settings_sizer.Add(comparison_alignment_top_text, 0, wx.TOP, 5)
		comparison_alignment_Dw_label = wx.StaticText(self.comparison_panel, wx.ID_ANY, "RT Modulation: ")
		comparison_alignment_grid.Add(comparison_alignment_Dw_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		comparison_alignment_Dw_sizer.Add(self.comparison_alignment_Dw_value, 0, 0, 0)
		comparison_alignment_Dw_label_2 = wx.StaticText(self.comparison_panel, wx.ID_ANY, " s", style=wx.ALIGN_LEFT)
		comparison_alignment_Dw_sizer.Add(comparison_alignment_Dw_label_2, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		comparison_alignment_grid.Add(comparison_alignment_Dw_sizer, 1, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)
		comparison_alignment_Gw_label = wx.StaticText(self.comparison_panel, wx.ID_ANY, "Gap Penalty: ")
		comparison_alignment_grid.Add(comparison_alignment_Gw_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		comparison_alignment_grid.Add(self.comparison_alignment_Gw_value, 0, 0, 0)
		comparison_alignment_min_peaks_label = wx.StaticText(self.comparison_panel, wx.ID_ANY, "Min Peaks: ")
		comparison_alignment_grid.Add(comparison_alignment_min_peaks_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		comparison_alignment_grid.Add(self.comparison_alignment_min_peaks_value, 0, 0, 0)
		comparison_settings_sizer.Add(comparison_alignment_grid, 1, wx.ALL | wx.EXPAND, 5)
		significance_level_label = wx.StaticText(self.comparison_panel, wx.ID_ANY, u"Significance Level (α): ")
		comparison_settings_sizer.Add(significance_level_label, 0, wx.BOTTOM | wx.TOP, 5)
		comparison_settings_sizer.Add(self.significance_level_value, 0, 0, 0)
		comparison_line_4 = wx.StaticLine(self.comparison_panel, wx.ID_ANY)
		comparison_settings_sizer.Add(comparison_line_4, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 10)
		comparison_settings_button_sizer.Add(self.comparison_apply_btn, 0, wx.ALIGN_BOTTOM | wx.RIGHT, 9)
		comparison_settings_button_sizer.Add(self.comparison_default_btn, 0, wx.ALIGN_BOTTOM | wx.RIGHT, 9)
		comparison_settings_button_sizer.Add(self.comparison_reset_btn, 0, wx.ALIGN_BOTTOM | wx.RIGHT, 9)
		comparison_settings_sizer.Add(comparison_settings_button_sizer, 1, wx.ALIGN_RIGHT, 20)
		comparison_settings_grid.Add(comparison_settings_sizer, 1, wx.EXPAND, 0)
		static_line_8 = wx.StaticLine(self.comparison_panel, wx.ID_ANY, style=wx.LI_VERTICAL)
		comparison_settings_grid.Add(static_line_8, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		comparison_button_sizer.Add(self.run_comparison_button, 0, 0, 0)
		static_line_2 = wx.StaticLine(self.comparison_panel, wx.ID_ANY)
		comparison_button_sizer.Add(static_line_2, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 10)
		comparison_charts_label = wx.StaticText(self.comparison_panel, wx.ID_ANY, "Charts")
		comparison_charts_label.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
		comparison_button_sizer.Add(comparison_charts_label, 0, wx.BOTTOM, 5)
		comparison_button_sizer.Add(self.comparison_radar_button, 0, wx.BOTTOM | wx.LEFT, 3)
		comparison_button_sizer.Add(self.comparison_mean_pa_button, 0, wx.BOTTOM | wx.LEFT, 3)
		comparison_button_sizer.Add(self.comparison_box_whisker_btn, 0, wx.BOTTOM | wx.LEFT, 3)
		comparison_button_sizer.Add(self.comparison_pca_btn, 0, wx.BOTTOM | wx.LEFT, 3)
		comparison_settings_grid.Add(comparison_button_sizer, 1, wx.EXPAND, 0)
		comparison_option_sizer.Add(comparison_settings_grid, 2, wx.EXPAND | wx.LEFT, 10)
		comparison_sizer.Add(comparison_option_sizer, 1, wx.EXPAND | wx.RIGHT, 10)
		comparison_log_line = wx.StaticLine(self.comparison_panel, wx.ID_ANY, style=wx.LI_VERTICAL)
		comparison_sizer.Add(comparison_log_line, 0, wx.EXPAND, 0)
		comparison_log_label = wx.StaticText(self.comparison_panel, wx.ID_ANY, "Log:")
		comparison_log_sizer.Add(comparison_log_label, 0, wx.BOTTOM, 5)
		comparison_log_sizer.Add(self.comparison_log_text_control, 4, wx.EXPAND | wx.RIGHT, 10)
		comparison_sizer.Add(comparison_log_sizer, 3, wx.ALL | wx.EXPAND, 10)
		self.comparison_panel.SetSizer(comparison_sizer)
		comparison_parent_sizer.Add(self.comparison_panel, 7, wx.ALL | wx.EXPAND, 10)
		self.SetSizer(comparison_parent_sizer)
		comparison_parent_sizer.Fit(self)
		self.Layout()
		# end wxGlade

	def comparison_browse_dialog(self):
		selected_project = file_dialog(
			self, "info", "Choose a Project to Open", "info files",
			style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
			# defaultDir=self.Config.get("main", "resultspath"))
			defaultDir=self._parent.Config.results_dir
		)
		
		return selected_project

	def on_left_comparison_browse(self, _):  # wxGlade: compare_tab.<event_handler>
		selected_project = self.comparison_browse_dialog
		
		if selected_project is None:
			return
		
		if pretty_name_from_info(selected_project) == self.comparison_right_project_name:
			wx.MessageBox(
				"""You cannot compare a project to itself!
Please choose a different project.""",
				"Error",
				wx.ICON_ERROR | wx.OK
			)
			return
		
		self.comparison_left_project = selected_project
		self.comparison_left_project_name = pretty_name_from_info(self.comparison_left_project)
		
		self.comparison_left_picker.SetValue(self.comparison_left_project_name)
		self.comparison_left_header.LoadURL("file://{}".format(self.comparison_left_project))
		
		self.comparison_check_enable()
	
	def on_right_comparison_browse(self, _):  # wxGlade: compare_tab.<event_handler>
		selected_project = self.comparison_browse_dialog
		
		if selected_project is None:
			return
		
		if pretty_name_from_info(selected_project) == self.comparison_left_project_name:
			wx.MessageBox(
				"""You cannot compare a project to itself!
Please choose a different project.""",
				"Error",
				wx.ICON_ERROR | wx.OK
			)
			return
		
		self.comparison_right_project = selected_project
		self.comparison_right_project_name = pretty_name_from_info(self.comparison_right_project)
		
		self.comparison_right_picker.SetValue(self.comparison_right_project_name)
		self.comparison_right_header.LoadURL("file://{}".format(self.comparison_right_project))
		
		self.comparison_check_enable()
	
	def comparison_check_enable(self):
		if self.comparison_right_project and self.comparison_left_project:
			self.run_comparison_button.Enable()
			self.comparison_box_whisker_btn.Enable()
			self.comparison_pca_btn.Enable()
			self.comparison_mean_pa_button.Enable()
			self.comparison_radar_button.Enable()
	
	def comparison_run(self, _):  # wxGlade: compare_tab.<event_handler>
		self.comparison_log_text_control.ClearAll()
		
		a_value = self.significance_level_value.GetValue()
		
		self.comparison = ComparisonThread(
			self,
			self.comparison_left_project,
			self.comparison_right_project,
			self._parent.Config,
			a_value
		)
		self.comparison.start()
	
	def do_comparison_apply(self, event):  # wxGlade: Launcher.<event_handler>
		# Save the settings
		self._parent.Config.comparison_a = self.significance_level_value.GetValue()
		self._parent.Config.comparison_rt_modulation = self.comparison_alignment_Dw_value.GetValue()
		self._parent.Config.comparison_gap_penalty = self.comparison_alignment_Gw_value.GetValue()
		self._parent.Config.comparison_min_peaks = int(self.comparison_alignment_min_peaks_value.GetValue())
		
		event.Skip()
	
	def do_comparison_default(self, event):  # wxGlade: Launcher.<event_handler>
		# Read settings
		self.significance_level_value.SetValue(str(self._parent.Config.comparison_a))
		self.comparison_alignment_Dw_value.SetValue(str(self._parent.Config.comparison_rt_modulation))
		self.comparison_alignment_Gw_value.SetValue(str(self._parent.Config.comparison_gap_penalty))
		self.comparison_alignment_min_peaks_value.SetValue(str(self._parent.Config.comparison_min_peaks))
		
		event.Skip()
	
	def do_comparison_reset(self, *_):  # wxGlade: Launcher.<event_handler>
		"""
		Reset the comparison settings to default
		"""
		
		Config = configparser.ConfigParser()
		Config.read("lib/default.ini")
		
		self.significance_level_value.SetValue(Config.get("comparison", "a"))
		self.comparison_alignment_Dw_value.SetValue(Config.get("comparison", "rt_modulation"))
		self.comparison_alignment_Gw_value.SetValue(Config.get("comparison", "gap_penalty"))
		self.comparison_alignment_min_peaks_value.SetValue(Config.get("comparison", "min_peaks"))
	
	def comparison_show_chart(self, chart_type):
		"""
		Show a chart of the given type for the samples being compared
		"""
		
		self.ChartViewer = ChartViewer.ChartViewer(
			self,
			chart_type=chart_type,
			initial_samples=[
				self.comparison_left_project,
				self.comparison_right_project],
		)
		self.ChartViewer.Show()
		self.ChartViewer.Raise()
	
	def comparison_show_box_whisker(self, event):
		"""
		Show a box-whisker chart for the samples being compared
		"""
		
		self.comparison_show_chart(chart_type="box_whisker")
		event.Skip()
	
	def comparison_show_pca(self, event):
		"""
		Show a pca plot for the samples being compared
		"""

		self.comparison_show_chart(chart_type="pca")
		event.Skip()
	
	def comparison_show_radar(self, event):  # wxGlade: Launcher.<event_handler>
		"""
		Show a radar chart for the samples being compared
		"""

		self.comparison_show_chart(chart_type="radar")
		event.Skip()
	
	def comparison_show_mean_peak_area(self, event):  # wxGlade: Launcher.<event_handler>
		"""
		Show a mean peak area chart for the samples being compared
		"""

		self.comparison_show_chart(chart_type="mean_peak_area")
		event.Skip()
	
	def on_comparison_log(self, event):
		"""
		Handler for comparison log events
		"""
		self.comparison_log_text_control.AppendText(event.log_text)

# end of class compare_tab
