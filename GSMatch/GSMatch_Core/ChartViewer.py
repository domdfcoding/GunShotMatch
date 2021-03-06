#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  ChartViewer.py
"""Window for viewing and editing charts"""
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
import os
import traceback

# 3rd party
import wx

import pandas

from domdf_wxpython_tools import get_toolbar_icon
from domdf_wxpython_tools import toggle, collapse_label, coming_soon
from domdf_wxpython_tools import file_dialog, file_dialog_multiple
from domdf_wxpython_tools import StylePickerDialog, ColourPickerDialog

from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import (
	FigureCanvasWxAgg as FigureCanvas,
	NavigationToolbar2WxAgg as NavigationToolbar,
)

from mathematical.data_frames import df_count

# this package
from GSMatch.GSMatch_Core.charts import (
	box_whisker,
	peak_area,
	mean_peak_area,
	radar_chart,
	PrincipalComponentAnalysis,
	bw_default_colours,
	bw_default_styles,
	default_colours,
	default_filetypes
)


# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class ChartViewer(wx.Frame):
	def __init__(self, parent, chart_type, initial_samples=None, *args, **kwds):
		if initial_samples is None:
			initial_samples = []
		
		self.chart_type = chart_type.lower()
		# print(type(args))
		args = (parent,) + args
		self.parent = parent
		# self.chart_data = chart_data
		# self.projects = projects
		# self.sample_lists = sample_lists
		# begin wxGlade: ChartViewer.__init__
		kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE
		wx.Frame.__init__(self, *args, **kwds)
		self.SetSize((900, 900))
		self.ChartViewer_v_splitter = wx.SplitterWindow(self, wx.ID_ANY, style=wx.SP_3D | wx.SP_BORDER | wx.SP_LIVE_UPDATE)
		self.v_splitter_left_panel = wx.Panel(self.ChartViewer_v_splitter, wx.ID_ANY)
		self.ChartViewer_h_splitter = wx.SplitterWindow(self.v_splitter_left_panel, wx.ID_ANY, style=wx.SP_3D | wx.SP_BORDER | wx.SP_LIVE_UPDATE)
		self.ChartViewer_chart_pane = wx.Panel(self.ChartViewer_h_splitter, wx.ID_ANY)
		
		self.chart_figure = Figure()
		
		
		
		
		self.chart_canvas = FigureCanvas(self.ChartViewer_chart_pane, wx.ID_ANY, self.chart_figure)
		self.h_splitter_bottom_panel = wx.Panel(self.ChartViewer_h_splitter, wx.ID_ANY)
		self.v_splitter_right_panel = wx.Panel(self.ChartViewer_v_splitter, wx.ID_ANY)
		self.ChartViewer_Settings_Panel = wx.Panel(self, wx.ID_ANY)
		self.settings_scroller = wx.ScrolledWindow(self.ChartViewer_Settings_Panel, wx.ID_ANY, style=wx.TAB_TRAVERSAL)
		self.samples_header = wx.Button(self.settings_scroller, wx.ID_ANY, "Samples", style=wx.BORDER_NONE | wx.BU_LEFT)
		self.samples_panel = wx.Panel(self.settings_scroller, wx.ID_ANY)
		self.up_btn = wx.BitmapButton(self.samples_panel, wx.ID_ANY, get_toolbar_icon("ART_GO_UP", 16))
		self.down_btn = wx.BitmapButton(self.samples_panel, wx.ID_ANY, get_toolbar_icon("ART_GO_DOWN", 16))
		self.add_btn = wx.BitmapButton(self.samples_panel, wx.ID_ANY, get_toolbar_icon("ART_ADD_BOOKMARK", 16))
		self.remove_btn = wx.BitmapButton(self.samples_panel, wx.ID_ANY, get_toolbar_icon("ART_DELETE", 16))
		self.sample_list_viewer = wx.ListBox(self.samples_panel, wx.ID_ANY, choices=[])
		self.general_header = wx.Button(self.settings_scroller, wx.ID_ANY, "General", style=wx.BORDER_NONE | wx.BU_LEFT)
		self.general_panel = wx.Panel(self.settings_scroller, wx.ID_ANY)
		self.colours_button = wx.Button(self.general_panel, wx.ID_ANY, "Choose")
		self.styles_button = wx.Button(self.general_panel, wx.ID_ANY, "Choose")
		self.width_value = wx.SpinCtrlDouble(self.general_panel, wx.ID_ANY, "", min=0.1, max=10.0)
		self.width_value.SetDigits(1)
		self.percentage_checkbox = wx.CheckBox(self.general_panel, wx.ID_ANY, "")
		self.groups_checkbox = wx.CheckBox(self.general_panel, wx.ID_ANY, "")
		self.data_header = wx.Button(self.settings_scroller, wx.ID_ANY, "Data", style=wx.BORDER_NONE | wx.BU_LEFT)
		self.data_panel = wx.Panel(self.settings_scroller, wx.ID_ANY)
		self.show_raw_data_checkbox = wx.CheckBox(self.data_panel, wx.ID_ANY, "")
		self.show_outliers_checkbox = wx.CheckBox(self.data_panel, wx.ID_ANY, "")
		self.outlier_mode_choice = wx.Choice(self.data_panel, wx.ID_ANY, choices=["2Stdev", "Quartiles", "MAD"])
		self.error_bar_choice = wx.Choice(self.data_panel, wx.ID_ANY, choices=["Range", "Stdev", "None"])
		self.log_header = wx.Button(self.settings_scroller, wx.ID_ANY, "Logarithmic", style=wx.BORDER_NONE | wx.BU_LEFT)
		self.log_panel = wx.Panel(self.settings_scroller, wx.ID_ANY)
		self.use_log_checkbox = wx.CheckBox(self.log_panel, wx.ID_ANY, "")
		self.log_base_value = wx.SpinCtrl(self.log_panel, wx.ID_ANY, "10", min=0, max=100, style=0)
		self.legend_header = wx.Button(self.settings_scroller, wx.ID_ANY, "Legend", style=wx.BORDER_NONE | wx.BU_LEFT)
		self.legend_panel = wx.Panel(self.settings_scroller, wx.ID_ANY)
		self.legend_checkbox = wx.CheckBox(self.legend_panel, wx.ID_ANY, "")
		self.leg_cols_value = wx.SpinCtrl(self.legend_panel, wx.ID_ANY, "1", min=1, max=5, style=0)
		self.leg_x_pos_value = wx.SpinCtrlDouble(self.legend_panel, wx.ID_ANY, "0.5", min=-0.5, max=1.5)
		self.leg_x_pos_value.SetDigits(2)
		self.leg_y_pos_value = wx.SpinCtrlDouble(self.legend_panel, wx.ID_ANY, "0.5", min=-0.5, max=1.5)
		self.leg_y_pos_value.SetDigits(2)
		self.size_header = wx.Button(self.settings_scroller, wx.ID_ANY, "Size", style=wx.BORDER_NONE | wx.BU_LEFT)
		self.size_panel = wx.Panel(self.settings_scroller, wx.ID_ANY)
		self.figure_width_value = wx.SpinCtrlDouble(self.size_panel, wx.ID_ANY, "", min=0.0, max=5000.0)
		self.figure_height_value = wx.SpinCtrlDouble(self.size_panel, wx.ID_ANY, "", min=0.0, max=5000.0)
		self.borders_header = wx.Button(self.settings_scroller, wx.ID_ANY, "Borders", style=wx.BORDER_NONE | wx.BU_LEFT)
		self.borders_panel = wx.Panel(self.settings_scroller, wx.ID_ANY)
		self.top_border_value = wx.SpinCtrlDouble(self.borders_panel, wx.ID_ANY, "0.9", min=0.0, max=2.0)
		self.top_border_value.SetDigits(3)
		self.bottom_border_value = wx.SpinCtrlDouble(self.borders_panel, wx.ID_ANY, "0.1", min=0.0, max=2.0)
		self.bottom_border_value.SetDigits(3)
		self.left_border_value = wx.SpinCtrlDouble(self.borders_panel, wx.ID_ANY, "0.125", min=0.0, max=2.0)
		self.left_border_value.SetDigits(3)
		self.right_border_value = wx.SpinCtrlDouble(self.borders_panel, wx.ID_ANY, "0.9", min=0.0, max=2.0)
		self.right_border_value.SetDigits(3)
		self.tight_layout_button = wx.Button(self.borders_panel, wx.ID_ANY, "&Tight Layout")
		self.ylim_header = wx.Button(self.settings_scroller, wx.ID_ANY, "y-Axis", style=wx.BORDER_NONE | wx.BU_LEFT)
		self.ylim_panel = wx.Panel(self.settings_scroller, wx.ID_ANY)
		self.y_ax_max_value = wx.SpinCtrl(self.ylim_panel, wx.ID_ANY, "0", min=0, max=10000000000)
		self.y_ax_min_value = wx.SpinCtrl(self.ylim_panel, wx.ID_ANY, "0", min=0, max=10000000000)
		self.xlim_header = wx.Button(self.settings_scroller, wx.ID_ANY, "x-Axis", style=wx.BORDER_NONE | wx.BU_LEFT)
		self.xlim_panel = wx.Panel(self.settings_scroller, wx.ID_ANY)
		self.x_ax_max_value = wx.SpinCtrlDouble(self.xlim_panel, wx.ID_ANY, "0.0", min=-100.0, max=100.0)
		self.x_ax_max_value.SetDigits(3)
		self.x_ax_min_value = wx.SpinCtrlDouble(self.xlim_panel, wx.ID_ANY, "0.0", min=-100.0, max=100.0)
		self.x_ax_min_value.SetDigits(3)
		self.filetypes_header = wx.Button(self.settings_scroller, wx.ID_ANY, "Filetypes", style=wx.BORDER_NONE | wx.BU_LEFT)
		self.filetypes_panel = wx.Panel(self.settings_scroller, wx.ID_ANY)
		self.png_checkbox = wx.CheckBox(self.filetypes_panel, wx.ID_ANY, "")
		self.svg_checkbox = wx.CheckBox(self.filetypes_panel, wx.ID_ANY, "")
		self.pdf_checkbox = wx.CheckBox(self.filetypes_panel, wx.ID_ANY, "")
		self.reset_button = wx.Button(self.ChartViewer_Settings_Panel, wx.ID_ANY, "&Reset")
		self.load_button = wx.Button(self.ChartViewer_Settings_Panel, wx.ID_OPEN, "Load")
		self.save_settings_button = wx.Button(self.ChartViewer_Settings_Panel, wx.ID_ANY, "&Save")
		self.save_button = wx.Button(self.ChartViewer_Settings_Panel, wx.ID_ANY, "&Save Chart")
		self.close_btn = wx.Button(self.ChartViewer_Settings_Panel, wx.ID_ANY, "Close")

		self.__set_properties()
		self.__do_layout()

		self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, self.on_splitter_moved, self.ChartViewer_h_splitter)
		self.Bind(wx.EVT_SPLITTER_SASH_POS_CHANGING, self.on_splitter_moved, self.ChartViewer_v_splitter)
		self.Bind(wx.EVT_BUTTON, self.collapse_samples, self.samples_header)
		self.Bind(wx.EVT_BUTTON, self.on_sample_up, self.up_btn)
		self.Bind(wx.EVT_BUTTON, self.on_sample_down, self.down_btn)
		self.Bind(wx.EVT_BUTTON, self.on_sample_add, self.add_btn)
		self.Bind(wx.EVT_BUTTON, self.on_sample_remove, self.remove_btn)
		self.Bind(wx.EVT_BUTTON, self.collapse_general, self.general_header)
		self.Bind(wx.EVT_BUTTON, self.configure_colours, self.colours_button)
		self.Bind(wx.EVT_BUTTON, self.configure_styles, self.styles_button)
		self.Bind(wx.EVT_SPINCTRLDOUBLE, self.replot_chart, self.width_value)
		self.Bind(wx.EVT_TEXT, self.replot_chart, self.width_value)
		self.Bind(wx.EVT_TEXT_ENTER, self.replot_chart, self.width_value)
		self.Bind(wx.EVT_CHECKBOX, self.update_percentage, self.percentage_checkbox)
		self.Bind(wx.EVT_CHECKBOX, self.replot_chart, self.groups_checkbox)
		self.Bind(wx.EVT_BUTTON, self.collapse_data, self.data_header)
		self.Bind(wx.EVT_CHECKBOX, self.replot_chart, self.show_raw_data_checkbox)
		self.Bind(wx.EVT_CHECKBOX, self.toggle_outliers, self.show_outliers_checkbox)
		self.Bind(wx.EVT_CHOICE, self.recalculate_data, self.outlier_mode_choice)
		self.Bind(wx.EVT_CHOICE, self.replot_chart, self.error_bar_choice)
		self.Bind(wx.EVT_BUTTON, self.collapse_log, self.log_header)
		self.Bind(wx.EVT_CHECKBOX, self.update_log, self.use_log_checkbox)
		self.Bind(wx.EVT_SPINCTRL, self.update_log, self.log_base_value)
		self.Bind(wx.EVT_TEXT, self.update_log, self.log_base_value)
		self.Bind(wx.EVT_TEXT_ENTER, self.update_log, self.log_base_value)
		self.Bind(wx.EVT_BUTTON, self.collapse_legend, self.legend_header)
		self.Bind(wx.EVT_CHECKBOX, self.update_legend, self.legend_checkbox)
		self.Bind(wx.EVT_SPINCTRL, self.update_legend, self.leg_cols_value)
		self.Bind(wx.EVT_TEXT, self.update_legend, self.leg_cols_value)
		self.Bind(wx.EVT_TEXT_ENTER, self.update_legend, self.leg_cols_value)
		self.Bind(wx.EVT_SPINCTRLDOUBLE, self.move_legend, self.leg_x_pos_value)
		self.Bind(wx.EVT_TEXT, self.move_legend, self.leg_x_pos_value)
		self.Bind(wx.EVT_TEXT_ENTER, self.move_legend, self.leg_x_pos_value)
		self.Bind(wx.EVT_SPINCTRLDOUBLE, self.move_legend, self.leg_y_pos_value)
		self.Bind(wx.EVT_TEXT, self.move_legend, self.leg_y_pos_value)
		self.Bind(wx.EVT_TEXT_ENTER, self.move_legend, self.leg_y_pos_value)
		self.Bind(wx.EVT_BUTTON, self.collapse_size, self.size_header)
		self.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_splitter_changed, self.figure_width_value)
		self.Bind(wx.EVT_TEXT, self.on_splitter_changed, self.figure_width_value)
		self.Bind(wx.EVT_TEXT_ENTER, self.on_splitter_changed, self.figure_width_value)
		self.Bind(wx.EVT_SPINCTRLDOUBLE, self.on_splitter_changed, self.figure_height_value)
		self.Bind(wx.EVT_TEXT, self.on_splitter_changed, self.figure_height_value)
		self.Bind(wx.EVT_TEXT_ENTER, self.on_splitter_changed, self.figure_height_value)
		self.Bind(wx.EVT_BUTTON, self.collapse_borders, self.borders_header)
		self.Bind(wx.EVT_SPINCTRLDOUBLE, self.update_borders, self.top_border_value)
		self.Bind(wx.EVT_TEXT, self.update_borders, self.top_border_value)
		self.Bind(wx.EVT_TEXT_ENTER, self.update_borders, self.top_border_value)
		self.Bind(wx.EVT_SPINCTRLDOUBLE, self.update_borders, self.bottom_border_value)
		self.Bind(wx.EVT_TEXT, self.update_borders, self.bottom_border_value)
		self.Bind(wx.EVT_TEXT_ENTER, self.update_borders, self.bottom_border_value)
		self.Bind(wx.EVT_SPINCTRLDOUBLE, self.update_borders, self.left_border_value)
		self.Bind(wx.EVT_TEXT, self.update_borders, self.left_border_value)
		self.Bind(wx.EVT_TEXT_ENTER, self.update_borders, self.left_border_value)
		self.Bind(wx.EVT_SPINCTRLDOUBLE, self.update_borders, self.right_border_value)
		self.Bind(wx.EVT_TEXT, self.update_borders, self.right_border_value)
		self.Bind(wx.EVT_TEXT_ENTER, self.update_borders, self.right_border_value)
		self.Bind(wx.EVT_BUTTON, self.apply_tight_layout, self.tight_layout_button)
		self.Bind(wx.EVT_BUTTON, self.collapse_ylim, self.ylim_header)
		self.Bind(wx.EVT_SPINCTRL, self.update_ylim, self.y_ax_max_value)
		self.Bind(wx.EVT_TEXT, self.update_ylim, self.y_ax_max_value)
		self.Bind(wx.EVT_TEXT_ENTER, self.update_ylim, self.y_ax_max_value)
		self.Bind(wx.EVT_SPINCTRL, self.update_ylim, self.y_ax_min_value)
		self.Bind(wx.EVT_TEXT, self.update_ylim, self.y_ax_min_value)
		self.Bind(wx.EVT_TEXT_ENTER, self.update_ylim, self.y_ax_min_value)
		self.Bind(wx.EVT_BUTTON, self.collapse_xlim, self.xlim_header)
		self.Bind(wx.EVT_SPINCTRLDOUBLE, self.update_xlim, self.x_ax_max_value)
		self.Bind(wx.EVT_TEXT, self.update_xlim, self.x_ax_max_value)
		self.Bind(wx.EVT_TEXT_ENTER, self.update_xlim, self.x_ax_max_value)
		self.Bind(wx.EVT_SPINCTRLDOUBLE, self.update_xlim, self.x_ax_min_value)
		self.Bind(wx.EVT_TEXT, self.update_xlim, self.x_ax_min_value)
		self.Bind(wx.EVT_TEXT_ENTER, self.update_xlim, self.x_ax_min_value)
		self.Bind(wx.EVT_BUTTON, self.collapse_filetypes, self.filetypes_header)
		self.Bind(wx.EVT_BUTTON, self.do_reset, self.reset_button)
		self.Bind(wx.EVT_BUTTON, self.do_load, self.load_button)
		self.Bind(wx.EVT_BUTTON, self.do_save_settings, self.save_settings_button)
		self.Bind(wx.EVT_BUTTON, self.do_save, self.save_button)
		self.Bind(wx.EVT_BUTTON, self.close_dialog, self.close_btn)
		# end wxGlade
		self.Bind(wx.EVT_SIZE, self.on_splitter_moved())
		self.Bind(wx.EVT_CLOSE, self.on_close)

		self.styles = bw_default_styles
		self.colours = default_colours

		# Setup Collapse Buttons
		self.general_header.SetLabel(collapse_label("General", False))
		self.legend_header.SetLabel(collapse_label("Legend", False))
		self.size_header.SetLabel(collapse_label("Size", False))
		self.borders_header.SetLabel(collapse_label("Borders", False))
		self.ylim_header.SetLabel(collapse_label("y-Axis", False))
		self.filetypes_header.SetLabel(collapse_label("Filetypes", False))
		self.xlim_header.SetLabel(collapse_label("x-Axis", False))
		self.data_header.SetLabel(collapse_label("Data", False))
		self.log_header.SetLabel(collapse_label("Logarithmic", False))
		self.samples_header.SetLabel(collapse_label("Samples", False))

		# Setup Keyboard Shortcuts
		ctrl_p_id = wx.NewId()
		ctrl_g_id = wx.NewId()
		ctrl_d_id = wx.NewId()
		ctrl_o_id = wx.NewId()
		ctrl_l_id = wx.NewId()
		ctrl_t_id = wx.NewId()
		ctrl_r_id = wx.NewId()
		ctrl_s_id = wx.NewId()
		self.Bind(wx.EVT_MENU, self.toggle_percentage, id=ctrl_p_id)
		self.Bind(wx.EVT_MENU, self.toggle_logarithmic, id=ctrl_g_id)
		self.Bind(wx.EVT_MENU, self.toggle_raw_data_button, id=ctrl_d_id)
		self.Bind(wx.EVT_MENU, self.toggle_outliers_button, id=ctrl_o_id)
		self.Bind(wx.EVT_MENU, self.toggle_legend, id=ctrl_l_id)
		self.Bind(wx.EVT_MENU, self.apply_tight_layout, id=ctrl_t_id)
		self.Bind(wx.EVT_MENU, self.do_reset, id=ctrl_r_id)
		self.Bind(wx.EVT_MENU, self.do_save, id=ctrl_s_id)
		accel_tbl = wx.AcceleratorTable([
			(wx.ACCEL_CTRL, ord('P'), ctrl_p_id),
			(wx.ACCEL_CTRL, ord('G'), ctrl_g_id),
			(wx.ACCEL_CTRL, ord('D'), ctrl_d_id),
			(wx.ACCEL_CTRL, ord('O'), ctrl_o_id),
			(wx.ACCEL_CTRL, ord('L'), ctrl_l_id),
			(wx.ACCEL_CTRL, ord('T'), ctrl_t_id),
			(wx.ACCEL_CTRL, ord('R'), ctrl_r_id),
			(wx.ACCEL_CTRL, ord('S'), ctrl_s_id),
		])
		self.SetAcceleratorTable(accel_tbl)
		
		# Set Initial Width and height values
		# self.on_splitter_moved()
		self.ChartViewer_h_splitter.SetSashPosition(1000, True)
		self.ChartViewer_v_splitter.SetSashPosition(1550, True)
		self.figure_height_value.SetValue(1000)
		self.figure_width_value.SetValue(1550)
		
		self.projects = []
		self.sample_lists = {}
		self.index_files = {}
		self.chart_data = pandas.DataFrame()
		
		# self.sample_list_viewer.Append(self.projects)
		if initial_samples:
			for sample in initial_samples:
				self.add_sample(sample)

			self.compound_order()

		# self.do_update_chart()
		self.prepare_chart()
		self.recalculate_data()
		self.replot_chart()
		
	def __set_properties(self):
		# begin wxGlade: ChartViewer.__set_properties
		self.SetTitle("ChartViewer")
		self.chart_canvas.SetMinSize((600, 800))
		self.h_splitter_bottom_panel.SetMinSize((1, 1))
		self.ChartViewer_h_splitter.SetMinimumPaneSize(20)
		self.ChartViewer_v_splitter.SetMinimumPaneSize(20)
		self.samples_header.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
		self.up_btn.SetMinSize((29, 29))
		self.down_btn.SetMinSize((29, 29))
		self.add_btn.SetMinSize((29, 29))
		self.remove_btn.SetMinSize((29, 29))
		self.sample_list_viewer.SetMinSize((-1, 120))
		self.general_header.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
		self.colours_button.SetMinSize((120, -1))
		self.styles_button.SetMinSize((120, -1))
		self.styles_button.Enable(False)
		self.width_value.SetMinSize((120, -1))
		self.width_value.Enable(False)
		self.width_value.SetIncrement(0.1)
		self.percentage_checkbox.Enable(False)
		self.groups_checkbox.Enable(False)
		self.data_header.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
		self.show_raw_data_checkbox.Enable(False)
		self.show_outliers_checkbox.Enable(False)
		self.show_outliers_checkbox.SetValue(1)
		self.outlier_mode_choice.SetMinSize((120, -1))
		self.outlier_mode_choice.Enable(False)
		self.outlier_mode_choice.SetSelection(0)
		self.error_bar_choice.SetMinSize((120, -1))
		self.error_bar_choice.Enable(False)
		self.error_bar_choice.SetSelection(0)
		self.log_header.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
		self.use_log_checkbox.Enable(False)
		self.log_base_value.SetMinSize((120, -1))
		self.log_base_value.Enable(False)
		self.legend_header.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
		self.leg_cols_value.SetMinSize((120, -1))
		self.leg_cols_value.Enable(False)
		self.leg_x_pos_value.SetMinSize((120, -1))
		self.leg_x_pos_value.Enable(False)
		self.leg_x_pos_value.SetIncrement(0.01)
		self.leg_y_pos_value.SetMinSize((120, -1))
		self.leg_y_pos_value.Enable(False)
		self.leg_y_pos_value.SetIncrement(0.01)
		self.size_header.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
		self.figure_width_value.SetMinSize((120, -1))
		self.figure_height_value.SetMinSize((120, -1))
		self.borders_header.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
		self.top_border_value.SetMinSize((120, -1))
		self.top_border_value.SetIncrement(0.005)
		self.bottom_border_value.SetMinSize((120, -1))
		self.bottom_border_value.SetIncrement(0.005)
		self.left_border_value.SetMinSize((120, -1))
		self.left_border_value.SetIncrement(0.005)
		self.right_border_value.SetMinSize((120, -1))
		self.right_border_value.SetIncrement(0.005)
		self.tight_layout_button.SetMinSize((120, -1))
		self.ylim_header.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
		self.y_ax_max_value.Enable(False)
		self.y_ax_min_value.Enable(False)
		self.xlim_header.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
		self.x_ax_max_value.Enable(False)
		self.x_ax_max_value.SetIncrement(0.005)
		self.x_ax_min_value.Enable(False)
		self.x_ax_min_value.SetIncrement(0.005)
		self.filetypes_header.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
		self.png_checkbox.SetValue(1)
		self.svg_checkbox.SetValue(1)
		self.pdf_checkbox.SetValue(1)
		self.settings_scroller.SetScrollRate(10, 10)
		self.reset_button.SetMinSize((85, -1))
		self.load_button.SetMinSize((85, -1))
		self.load_button.SetBitmap(get_toolbar_icon("ART_FILE_OPEN",16))
		self.save_settings_button.SetMinSize((85, -1))
		self.save_button.SetMinSize((178, -1))
		self.close_btn.SetMinSize((85, -1))
		self.ChartViewer_Settings_Panel.SetMinSize((300, -1))
		# end wxGlade

	def __do_layout(self):
		self.Maximize()
		# begin wxGlade: ChartViewer.__do_layout
		ChartViewer_Sizer = wx.BoxSizer(wx.HORIZONTAL)
		settings_outer_sizer = wx.BoxSizer(wx.VERTICAL)
		save_close_grid = wx.FlexGridSizer(1, 3, 0, 0)
		button_grid = wx.GridSizer(1, 3, 0, 0)
		settings_sizer = wx.BoxSizer(wx.VERTICAL)
		filetypes_grid = wx.GridSizer(2, 3, 2, 5)
		xlim_grid = wx.FlexGridSizer(2, 2, 5, 5)
		ylim_grid = wx.FlexGridSizer(2, 2, 5, 5)
		borders_grid = wx.GridSizer(5, 2, 0, 0)
		size_grid = wx.GridSizer(2, 2, 0, 0)
		legend_grid = wx.GridSizer(4, 2, 0, 0)
		log_grid = wx.GridSizer(2, 2, 0, 0)
		data_grid = wx.GridSizer(4, 2, 0, 0)
		general_grid = wx.GridSizer(5, 2, 0, 0)
		samples_sizer = wx.BoxSizer(wx.HORIZONTAL)
		samples_button_sizer = wx.BoxSizer(wx.VERTICAL)
		v_splitter_right_sizer = wx.BoxSizer(wx.HORIZONTAL)
		v_splitter_left_sizer = wx.BoxSizer(wx.HORIZONTAL)
		h_splitter_bottom_sizer = wx.BoxSizer(wx.VERTICAL)
		ChartViewer_chart_sizer = wx.BoxSizer(wx.HORIZONTAL)
		ChartViewer_chart_sizer.Add(self.chart_canvas, 1, wx.EXPAND, 0)
		self.ChartViewer_chart_pane.SetSizer(ChartViewer_chart_sizer)
		static_line_1 = wx.StaticLine(self.h_splitter_bottom_panel, wx.ID_ANY)
		h_splitter_bottom_sizer.Add(static_line_1, 0, wx.EXPAND, 0)
		self.h_splitter_bottom_panel.SetSizer(h_splitter_bottom_sizer)
		self.ChartViewer_h_splitter.SplitHorizontally(self.ChartViewer_chart_pane, self.h_splitter_bottom_panel)
		v_splitter_left_sizer.Add(self.ChartViewer_h_splitter, 1, wx.EXPAND, 0)
		self.v_splitter_left_panel.SetSizer(v_splitter_left_sizer)
		v_splitter_line = wx.StaticLine(self.v_splitter_right_panel, wx.ID_ANY, style=wx.LI_VERTICAL)
		v_splitter_right_sizer.Add(v_splitter_line, 0, wx.EXPAND, 0)
		self.v_splitter_right_panel.SetSizer(v_splitter_right_sizer)
		self.ChartViewer_v_splitter.SplitVertically(self.v_splitter_left_panel, self.v_splitter_right_panel)
		ChartViewer_Sizer.Add(self.ChartViewer_v_splitter, 1, wx.EXPAND, 0)
		settings_header = wx.StaticText(self.settings_scroller, wx.ID_ANY, "Settings")
		settings_header.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, 0, ""))
		settings_sizer.Add(settings_header, 0, wx.BOTTOM | wx.TOP, 5)
		settings_sizer.Add(self.samples_header, 0, 0, 5)
		samples_button_sizer.Add(self.up_btn, 0, 0, 0)
		samples_button_sizer.Add(self.down_btn, 0, 0, 0)
		samples_button_sizer.Add(self.add_btn, 0, 0, 0)
		samples_button_sizer.Add(self.remove_btn, 0, 0, 0)
		samples_sizer.Add(samples_button_sizer, 0, wx.EXPAND | wx.RIGHT, 5)
		samples_sizer.Add(self.sample_list_viewer, 1, wx.RIGHT, 13)
		self.samples_panel.SetSizer(samples_sizer)
		settings_sizer.Add(self.samples_panel, 0, wx.EXPAND | wx.LEFT, 10)
		samples_line = wx.StaticLine(self.settings_scroller, wx.ID_ANY)
		settings_sizer.Add(samples_line, 0, wx.EXPAND | wx.TOP, 5)
		settings_sizer.Add(self.general_header, 0, 0, 5)
		colours_label = wx.StaticText(self.general_panel, wx.ID_ANY, "Colours: ")
		general_grid.Add(colours_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		general_grid.Add(self.colours_button, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		styles_label = wx.StaticText(self.general_panel, wx.ID_ANY, "Styles: ")
		styles_label.Enable(False)
		general_grid.Add(styles_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		general_grid.Add(self.styles_button, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		width_label = wx.StaticText(self.general_panel, wx.ID_ANY, "Width: ")
		width_label.Enable(False)
		general_grid.Add(width_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		general_grid.Add(self.width_value, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		percentage_label = wx.StaticText(self.general_panel, wx.ID_ANY, "&Percentage: ")
		percentage_label.Enable(False)
		general_grid.Add(percentage_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		general_grid.Add(self.percentage_checkbox, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		groups_label = wx.StaticText(self.general_panel, wx.ID_ANY, "Groups: ")
		groups_label.Enable(False)
		general_grid.Add(groups_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		general_grid.Add(self.groups_checkbox, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		self.general_panel.SetSizer(general_grid)
		settings_sizer.Add(self.general_panel, 0, wx.EXPAND | wx.LEFT, 10)
		general_line = wx.StaticLine(self.settings_scroller, wx.ID_ANY)
		settings_sizer.Add(general_line, 0, wx.EXPAND | wx.TOP, 5)
		settings_sizer.Add(self.data_header, 0, 0, 5)
		show_raw_data_label = wx.StaticText(self.data_panel, wx.ID_ANY, "Show Raw &Data:")
		show_raw_data_label.Enable(False)
		data_grid.Add(show_raw_data_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		data_grid.Add(self.show_raw_data_checkbox, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		show_outliers_label = wx.StaticText(self.data_panel, wx.ID_ANY, "Show &Outliers:")
		show_outliers_label.Enable(False)
		data_grid.Add(show_outliers_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		data_grid.Add(self.show_outliers_checkbox, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		outlier_mode_label = wx.StaticText(self.data_panel, wx.ID_ANY, "Outlier Mode: ")
		outlier_mode_label.Enable(False)
		data_grid.Add(outlier_mode_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		data_grid.Add(self.outlier_mode_choice, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		err_bar_label = wx.StaticText(self.data_panel, wx.ID_ANY, "Error bar Type: ")
		err_bar_label.Enable(False)
		data_grid.Add(err_bar_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		data_grid.Add(self.error_bar_choice, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		self.data_panel.SetSizer(data_grid)
		settings_sizer.Add(self.data_panel, 0, wx.EXPAND | wx.LEFT, 10)
		data_line = wx.StaticLine(self.settings_scroller, wx.ID_ANY)
		settings_sizer.Add(data_line, 0, wx.EXPAND | wx.TOP, 5)
		settings_sizer.Add(self.log_header, 0, 0, 5)
		use_log_label = wx.StaticText(self.log_panel, wx.ID_ANY, "Lo&garithmic:")
		use_log_label.Enable(False)
		log_grid.Add(use_log_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		log_grid.Add(self.use_log_checkbox, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		log_base_label = wx.StaticText(self.log_panel, wx.ID_ANY, "Base: ")
		log_base_label.Enable(False)
		log_grid.Add(log_base_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		log_grid.Add(self.log_base_value, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		self.log_panel.SetSizer(log_grid)
		settings_sizer.Add(self.log_panel, 0, wx.EXPAND | wx.LEFT, 10)
		log_line = wx.StaticLine(self.settings_scroller, wx.ID_ANY)
		settings_sizer.Add(log_line, 0, wx.EXPAND | wx.TOP, 5)
		settings_sizer.Add(self.legend_header, 0, 0, 5)
		legend_label = wx.StaticText(self.legend_panel, wx.ID_ANY, "Show:")
		legend_grid.Add(legend_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		legend_grid.Add(self.legend_checkbox, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		leg_cols_label = wx.StaticText(self.legend_panel, wx.ID_ANY, "Columns: ")
		leg_cols_label.Enable(False)
		legend_grid.Add(leg_cols_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		legend_grid.Add(self.leg_cols_value, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		leg_x_pos_label = wx.StaticText(self.legend_panel, wx.ID_ANY, "X Position: ")
		leg_x_pos_label.Enable(False)
		legend_grid.Add(leg_x_pos_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		legend_grid.Add(self.leg_x_pos_value, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		leg_y_pos_label = wx.StaticText(self.legend_panel, wx.ID_ANY, "Y Position: ")
		leg_y_pos_label.Enable(False)
		legend_grid.Add(leg_y_pos_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		legend_grid.Add(self.leg_y_pos_value, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		self.legend_panel.SetSizer(legend_grid)
		settings_sizer.Add(self.legend_panel, 0, wx.EXPAND | wx.LEFT, 10)
		legend_line = wx.StaticLine(self.settings_scroller, wx.ID_ANY)
		settings_sizer.Add(legend_line, 0, wx.EXPAND | wx.TOP, 5)
		settings_sizer.Add(self.size_header, 0, 0, 5)
		figure_width_label = wx.StaticText(self.size_panel, wx.ID_ANY, "Width: ")
		size_grid.Add(figure_width_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		size_grid.Add(self.figure_width_value, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		figure_height_label = wx.StaticText(self.size_panel, wx.ID_ANY, "Height:")
		size_grid.Add(figure_height_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		size_grid.Add(self.figure_height_value, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		self.size_panel.SetSizer(size_grid)
		settings_sizer.Add(self.size_panel, 0, wx.EXPAND | wx.LEFT, 10)
		size_line = wx.StaticLine(self.settings_scroller, wx.ID_ANY)
		settings_sizer.Add(size_line, 0, wx.EXPAND | wx.TOP, 5)
		settings_sizer.Add(self.borders_header, 0, 0, 5)
		top_border_label = wx.StaticText(self.borders_panel, wx.ID_ANY, "Top: ")
		borders_grid.Add(top_border_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		borders_grid.Add(self.top_border_value, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		bottom_border_label = wx.StaticText(self.borders_panel, wx.ID_ANY, "Bottom: ")
		borders_grid.Add(bottom_border_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		borders_grid.Add(self.bottom_border_value, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		left_border_label = wx.StaticText(self.borders_panel, wx.ID_ANY, "Left: ")
		borders_grid.Add(left_border_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		borders_grid.Add(self.left_border_value, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		right_border_label = wx.StaticText(self.borders_panel, wx.ID_ANY, "Right: ")
		borders_grid.Add(right_border_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		borders_grid.Add(self.right_border_value, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		borders_grid.Add((0, 0), 0, 0, 0)
		borders_grid.Add(self.tight_layout_button, 0, wx.ALIGN_CENTER_VERTICAL, 10)
		self.borders_panel.SetSizer(borders_grid)
		settings_sizer.Add(self.borders_panel, 0, wx.EXPAND | wx.LEFT, 10)
		borders_line = wx.StaticLine(self.settings_scroller, wx.ID_ANY)
		settings_sizer.Add(borders_line, 0, wx.EXPAND | wx.TOP, 5)
		settings_sizer.Add(self.ylim_header, 0, 0, 5)
		y_ax_max_label = wx.StaticText(self.ylim_panel, wx.ID_ANY, "Max: ")
		y_ax_max_label.Enable(False)
		ylim_grid.Add(y_ax_max_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		ylim_grid.Add(self.y_ax_max_value, 0, 0, 0)
		y_ax_min_label = wx.StaticText(self.ylim_panel, wx.ID_ANY, "Min: ")
		y_ax_min_label.Enable(False)
		ylim_grid.Add(y_ax_min_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		ylim_grid.Add(self.y_ax_min_value, 0, 0, 0)
		self.ylim_panel.SetSizer(ylim_grid)
		settings_sizer.Add(self.ylim_panel, 0, wx.EXPAND | wx.LEFT, 10)
		ylim_line = wx.StaticLine(self.settings_scroller, wx.ID_ANY)
		settings_sizer.Add(ylim_line, 0, wx.EXPAND | wx.TOP, 5)
		settings_sizer.Add(self.xlim_header, 0, 0, 5)
		x_ax_max_label = wx.StaticText(self.xlim_panel, wx.ID_ANY, "Right: ")
		x_ax_max_label.Enable(False)
		xlim_grid.Add(x_ax_max_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		xlim_grid.Add(self.x_ax_max_value, 0, 0, 0)
		x_ax_min_label = wx.StaticText(self.xlim_panel, wx.ID_ANY, "Left: ")
		x_ax_min_label.Enable(False)
		xlim_grid.Add(x_ax_min_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		xlim_grid.Add(self.x_ax_min_value, 0, 0, 0)
		self.xlim_panel.SetSizer(xlim_grid)
		settings_sizer.Add(self.xlim_panel, 0, wx.EXPAND | wx.LEFT, 10)
		xlim_line = wx.StaticLine(self.settings_scroller, wx.ID_ANY)
		settings_sizer.Add(xlim_line, 0, wx.EXPAND | wx.TOP, 5)
		settings_sizer.Add(self.filetypes_header, 0, 0, 5)
		png_label = wx.StaticText(self.filetypes_panel, wx.ID_ANY, "PNG")
		filetypes_grid.Add(png_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		svg_label = wx.StaticText(self.filetypes_panel, wx.ID_ANY, "SVG")
		filetypes_grid.Add(svg_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		pdf_label = wx.StaticText(self.filetypes_panel, wx.ID_ANY, "PDF")
		filetypes_grid.Add(pdf_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		filetypes_grid.Add(self.png_checkbox, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		filetypes_grid.Add(self.svg_checkbox, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		filetypes_grid.Add(self.pdf_checkbox, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		self.filetypes_panel.SetSizer(filetypes_grid)
		settings_sizer.Add(self.filetypes_panel, 0, wx.EXPAND | wx.LEFT, 10)
		filetypes_line = wx.StaticLine(self.settings_scroller, wx.ID_ANY)
		settings_sizer.Add(filetypes_line, 0, wx.EXPAND | wx.TOP, 5)
		settings_sizer.Add((0, 0), 0, 0, 0)
		self.settings_scroller.SetSizer(settings_sizer)
		settings_outer_sizer.Add(self.settings_scroller, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
		static_line_8 = wx.StaticLine(self.ChartViewer_Settings_Panel, wx.ID_ANY)
		settings_outer_sizer.Add(static_line_8, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 5)
		button_grid.Add(self.reset_button, 0, wx.ALIGN_CENTER, 10)
		button_grid.Add(self.load_button, 0, wx.ALIGN_CENTER, 10)
		button_grid.Add(self.save_settings_button, 0, wx.ALIGN_CENTER, 10)
		settings_outer_sizer.Add(button_grid, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
		static_line_9 = wx.StaticLine(self.ChartViewer_Settings_Panel, wx.ID_ANY)
		settings_outer_sizer.Add(static_line_9, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 5)
		save_close_grid.Add(self.save_button, 0, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 4)
		save_close_grid.Add(self.close_btn, 0, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 4)
		settings_outer_sizer.Add(save_close_grid, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM | wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
		self.ChartViewer_Settings_Panel.SetSizer(settings_outer_sizer)
		ChartViewer_Sizer.Add(self.ChartViewer_Settings_Panel, 0, wx.EXPAND, 10)
		self.SetSizer(ChartViewer_Sizer)
		self.Layout()
		# end wxGlade
		
		# Enable Applicable Buttons
		print(self.chart_type)
		
		self.leg_cols_label = leg_cols_label
		self.log_base_label = log_base_label
		self.leg_x_pos_label = leg_x_pos_label
		self.leg_y_pos_label = leg_y_pos_label
		self.outlier_mode_label = outlier_mode_label
		self.y_ax_max_label = y_ax_max_label
		self.y_ax_min_label = y_ax_min_label
		self.x_ax_max_label = x_ax_max_label
		self.x_ax_min_label = x_ax_min_label
		
		enable_options = {
			width_label: ["mean_peak_area", "peak_area", "box_whisker"],
			self.width_value: ["mean_peak_area", "peak_area", "box_whisker"],
			percentage_label: ["mean_peak_area", "peak_area"],
			self.percentage_checkbox: ["mean_peak_area", "peak_area"],
			err_bar_label: ["mean_peak_area", "peak_area", "box_whisker"],
			self.error_bar_choice: ["mean_peak_area", "peak_area", "box_whisker"],
			self.y_ax_max_label: ["mean_peak_area", "peak_area", "box_whisker", "pca"],
			self.y_ax_max_value: ["mean_peak_area", "peak_area", "box_whisker", "pca"],
			self.y_ax_min_label: ["mean_peak_area", "peak_area", "box_whisker", "pca"],
			self.y_ax_min_value: ["mean_peak_area", "peak_area", "box_whisker", "pca"],
			self.x_ax_max_label: ["mean_peak_area", "peak_area", "box_whisker", "pca"],
			self.x_ax_max_value: ["mean_peak_area", "peak_area", "box_whisker", "pca"],
			self.x_ax_min_label: ["mean_peak_area", "peak_area", "box_whisker", "pca"],
			self.x_ax_min_value: ["mean_peak_area", "peak_area", "box_whisker", "pca"],
			use_log_label: ["peak_area", "radar"],
			self.use_log_checkbox: ["peak_area", "radar"],
			show_outliers_label: ["box_whisker"],
			self.show_outliers_checkbox: ["box_whisker"],
			show_raw_data_label: ["box_whisker"],
			self.show_raw_data_checkbox: ["box_whisker"],
			self.outlier_mode_label: ["box_whisker"],
			self.outlier_mode_choice: ["box_whisker"],
			styles_label: ["box_whisker"],
			self.styles_button: ["box_whisker"],
			groups_label: ["box_whisker"],
			self.groups_checkbox: ["box_whisker"],
		}
		
		hide_options = {
			self.ylim_header: ["radar"],
			self.ylim_panel: ["radar"],
			ylim_line: ["radar"],
			self.xlim_header: ["radar"],
			self.xlim_panel: ["radar"],
			xlim_line: ["radar"],
			self.data_header: ["radar", "pca", "peak_area"],
			self.data_panel: ["radar", "pca", "peak_area"],
			data_line: ["radar", "pca", "peak_area"],
			self.samples_header: ["peak_area"],
			self.samples_panel: ["peak_area"],
			samples_line: ["peak_area"],
			self.log_header: ["mean_peak_area", "box_whisker", "pca"],
			self.log_panel: ["mean_peak_area", "box_whisker", "pca"],
			log_line: ["mean_peak_area", "box_whisker", "pca"],
		}
		
		# TODO: keep disabled while no samples selected
		for item, charts in enable_options.items():
			if self.chart_type in charts:
				item.Enable(True)
		
		for item, charts in hide_options.items():
			if self.chart_type in charts:
				item.Hide()
		
		if self.chart_type in ["mean_peak_area", "peak_area"]:
			self.error_bar_choice.Clear()
			self.error_bar_choice.AppendItems(["Stdev", "None"])

		if self.chart_type in ["mean_peak_area", "peak_area", "box_whisker"]:
			self.error_bar_choice.SetSelection(0)
			
			width_values = {"mean_peak_area": 2.0, "box_whisker":4.0, "peak_area":0.8}
			self.width_value.SetValue(width_values[self.chart_type])
		
		self.Layout()
		
		self.use_log = False
		
		print(self.save_button.GetSize())
	
	def close_dialog(self, _):  # wxGlade: ChartViewer.<event_handler>
		self.Destroy()
	
	def prepare_chart(self):
		if self.chart_type == "peak_area":
			self.chart = peak_area()
		elif self.chart_type == "mean_peak_area":
			self.chart = mean_peak_area()
		elif self.chart_type == "box_whisker":
			self.chart = box_whisker()
		elif self.chart_type == "pca":
			self.chart = PrincipalComponentAnalysis()
		elif self.chart_type == "radar":
			self.chart = radar_chart()
		
		if self.chart_type in ["mean_peak_area", "peak_area", "box_whisker", "pca"]:
			self.chart_axes = self.chart_figure.add_subplot(111)  # 1x1 grid, first subplot
		elif self.chart_type == "radar":
			self.chart_axes = self.chart_figure.add_subplot(111, polar=True)
		
		self.chart.fig = self.chart_figure
		self.chart.ax = self.chart_axes
	
	def on_close(self, _):
		"""
		Handler for closing the chart viewer
		"""
		# Add in case for chart has been changed but not saved
		
		# you may also do:  event.Skip() since the default event handler does call Destroy(), too
		self.Destroy()
	
	
	"""Check Button Functions"""
	
	def toggle_percentage(self, *_):
		"""
		Toggle the percentage checkbox
		"""
		
		if toggle(self.percentage_checkbox):
			self.replot_chart()
	
	def toggle_logarithmic(self, *_):
		"""
		Toggle the logarithmic checkbox
		"""
		
		if toggle(self.use_log_checkbox):
			self.update_log()
	
	def toggle_raw_data_button(self, *_):
		"""
		Toggle the show_raw_data checkbox
		"""

		if toggle(self.show_raw_data_checkbox):
			self.replot_chart()

	def toggle_outliers_button(self, *_):
		"""
		Toggle the show_outliers checkbox
		"""

		if toggle(self.show_outliers_checkbox):
			self.toggle_outliers()
	
	def toggle_legend(self, *_):
		"""
		Toggle the legend checkbox
		"""

		if toggle(self.legend_checkbox):
			self.update_legend()
	
	"""Update Functions"""
	
	def update_percentage(self, _):  # wxGlade: ChartViewer.<event_handler>
		
		for control in [
			self.y_ax_max_label, self.y_ax_min_label,
			self.y_ax_max_value, self.y_ax_min_value
		]:
			control.Enable(not self.percentage_checkbox.GetValue())
		
		self.replot_chart()
	
	def update_legend(self, *_):  # wxGlade: ChartViewer.<event_handler>
		
		self.leg_x_pos_value.Enable(self.legend_checkbox.GetValue())
		self.leg_y_pos_value.Enable(self.legend_checkbox.GetValue())
		self.leg_x_pos_label.Enable(self.legend_checkbox.GetValue())
		self.leg_y_pos_label.Enable(self.legend_checkbox.GetValue())
		if self.chart_type in ["box_whisker", "pca"]:
			self.leg_cols_label.Enable(self.legend_checkbox.GetValue())
			self.leg_cols_value.Enable(self.legend_checkbox.GetValue())
		
		self.Layout()

		# Remove legend
		try:
			# self.chart.ax.get_legend().remove()
			# self.chart.fig.get_legend().remove()
			self.legend.remove()
			# self.chart_figure.canvas.draw_idle()
		except AttributeError:  # If there is no legend
			# traceback.print_exc()
			pass
		except ValueError:  # If there is no legend
			# traceback.print_exc()
			pass

		if self.legend_checkbox.GetValue():
			
			# Add legend to Chart
			if self.chart_type in ["box_whisker", "pca"]:
				self.legend = self.chart.create_legend(
					(self.leg_x_pos_value.GetValue(), self.leg_y_pos_value.GetValue()),
					leg_cols=self.leg_cols_value.GetValue()
				)
			
			else:
				self.legend = self.chart.create_legend((self.leg_x_pos_value.GetValue(), self.leg_y_pos_value.GetValue()))

		self.chart_figure.canvas.draw_idle()
		
		# if self.legend_checkbox.GetValue():
		#
		# 	self.leg_x_pos_value.Enable(True)
		# 	self.leg_y_pos_value.Enable(True)
		# 	if self.chart_type == "box_whisker":
		# 		self.leg_cols_label.Enable(True)
		# 		self.leg_cols_value.Enable(True)
		# 	self.leg_x_pos_label.Enable(True)
		# 	self.leg_y_pos_label.Enable(True)
		# 	self.Layout()
		#
		# 	# Add legend to Chart
		# 	self.chart.create_legend((self.leg_x_pos_value.GetValue(), self.leg_y_pos_value.GetValue()))
		# 	self.chart_figure.canvas.draw_idle()
		#
		#
		# else:
		# 	self.leg_cols_value.Enable(False)
		# 	self.leg_x_pos_value.Enable(False)
		# 	self.leg_y_pos_value.Enable(False)
		# 	self.leg_cols_label.Enable(False)
		# 	self.leg_x_pos_label.Enable(False)
		# 	self.leg_y_pos_label.Enable(False)
		# 	self.Layout()
		#
		# 	# Remove legend
		# 	try:
		# 		self.chart.ax.get_legend().remove()
		# 		self.chart_figure.canvas.draw_idle()
		# 	except AttributeError:  # If there is no legend
		# 		pass
	
	def update_log(self, *_):  # wxGlade: ChartViewer.<event_handler>
		
		self.log_base_label.Enable(self.use_log_checkbox.GetValue())
		self.log_base_value.Enable(self.use_log_checkbox.GetValue())
		self.Layout()
		
		if self.use_log_checkbox.GetValue():
			self.use_log = self.log_base_value.GetValue()
		else:
			self.use_log = False
		
		self.recalculate_data()
		
		# if self.use_log_checkbox.GetValue():
		# 	self.log_base_label.Enable(True)
		# 	self.log_base_value.Enable(True)
		# 	self.Layout()
		# 	self.use_log = self.log_base_value.GetValue()
		# else:
		# 	self.log_base_label.Enable(False)
		# 	self.log_base_value.Enable(False)
		# 	self.Layout()
		# 	self.use_log = False
		# self.recalculate_data()
	
	def toggle_outliers(self, *_):  # wxGlade: ChartViewer.<event_handler>
		if self.show_outliers_checkbox.IsEnabled():
			self.outlier_mode_choice.Enable(self.show_outliers_checkbox.GetValue())
			self.outlier_mode_label.Enable(self.show_outliers_checkbox.GetValue())
			self.Layout()
			self.replot_chart()
		
		# if self.show_outliers_checkbox.IsEnabled():
		# 	if self.show_outliers_checkbox.GetValue():
		# 		self.outlier_mode_choice.Enable(True)
		# 		self.outlier_mode_label.Enable(True)
		# 	else:
		# 		self.outlier_mode_choice.Enable(False)
		# 		self.outlier_mode_label.Enable(False)
		# 	self.Layout()
		# 	self.replot_chart()
	
	def update_borders(self, *_):  # wxGlade: ChartViewer.<event_handler>
		"""
		Update the chart borders to the settings chosen by the user
		"""
		self.chart_figure.subplots_adjust(
			self.left_border_value.GetValue(),
			self.bottom_border_value.GetValue(),
			self.right_border_value.GetValue(),
			self.top_border_value.GetValue()
		)
		self.chart_figure.canvas.draw_idle()
	
	def apply_tight_layout(self, *_):  # wxGlade: ChartViewer.<event_handler>
		"""
		Apply tight_layout to the figure and update the settings to the new values
		"""
		self.chart.fig.tight_layout()
		self.chart_figure.canvas.draw_idle()
		
		# set SpinCtrls to new values
		self.right_border_value.SetValue(self.chart.fig.subplotpars.right)
		self.left_border_value.SetValue(self.chart.fig.subplotpars.left)
		self.bottom_border_value.SetValue(self.chart.fig.subplotpars.bottom)
		self.top_border_value.SetValue(self.chart.fig.subplotpars.top)
	
	def recalculate_data(self, *_):  # wxGlade: ChartViewer.<event_handler>
		"""
		Recalculate the data for the chart
		"""
		
		self.projects = [self.sample_list_viewer.GetString(item) for item in range(self.sample_list_viewer.GetCount())]
		
		if self.projects == []:
			return
		
		outlier_mode = self.outlier_mode_choice.GetString(self.outlier_mode_choice.GetSelection()).lower()
		
		if self.chart_type == "box_whisker":
			self.chart.setup_data(
				self.chart_data,
				[(name, self.sample_lists[name]) for name in self.projects],
				outlier_mode)
		elif self.chart_type == "pca":
			pca_data = {"target": []}
			targets = []
			features = []
			
			for name in self.projects:
				for i in range(len(self.sample_lists[name])):
					pca_data["target"].append(name)
				targets.append(name)
			
			for compound in self.chart_data.index.values:
				area_list = []
				for name in self.projects:
					for prefix in self.sample_lists[name]:
						area_list.append(self.chart_data.loc[compound, prefix])
				
				pca_data[compound] = area_list
				features.append(compound)
			
			pca_data = pandas.DataFrame(data=pca_data)
			self.pca = self.chart.setup_data(pca_data, features, targets)
			
		elif self.chart_type in ["mean_peak_area", "radar"]:
			self.chart.setup_data(self.chart_data, self.projects)
		elif self.chart_type == "peak_area":
			self.chart.setup_data(
				self.chart_data,
				self.projects[0],
				self.sample_lists[self.projects[0]],
				self.use_log)
		
		# print(outlier_mode)
		self.replot_chart()
	
	def replot_chart(self, *_):  # wxGlade: ChartViewer.<event_handler>
		"""
		Redraw the data points on the chart
		"""
		
		self.projects = [self.sample_list_viewer.GetString(item) for item in range(self.sample_list_viewer.GetCount())]
		
		self.chart_axes.clear()
		self.chart_figure.canvas.draw_idle()
		
		self.toolbar = NavigationToolbar(self.chart_canvas)
		self.toolbar.Hide()
		
		if not self.projects:
			return
		
		# print(self.chart_type)
		
		show_outliers = self.show_outliers_checkbox.GetValue()
		show_raw_data = self.show_raw_data_checkbox.GetValue()
		percentage = self.percentage_checkbox.GetValue()
		err_bar = self.error_bar_choice.GetString(self.error_bar_choice.GetSelection()).lower()
		leg_cols = self.leg_cols_value.GetValue()
		column_width = self.width_value.GetValue()

		groupings = False
		if self.groups_checkbox.GetValue():
			groupings = [x.replace(" Fired",'') for x in self.projects[::2]]

		if self.chart_type == "box_whisker":
			self.chart.setup_datapoints(column_width, self.styles, self.colours)
			self.chart.create_chart(show_outliers, show_raw_data, err_bar, groupings)
		if self.chart_type == "pca":
			self.chart.setup_datapoints(self.colours)
			self.chart.create_chart()
		elif self.chart_type == "mean_peak_area":
			self.chart.create_chart(bar_width=column_width, percentage=percentage, err_bar=err_bar, colours=self.colours)
		elif self.chart_type == "peak_area":
			self.chart.create_chart(column_width, percentage=percentage, colours=self.colours)
		elif self.chart_type == "radar":
			self.chart.create_chart(use_log=self.use_log, colours=self.colours)
		
		# self.chart_figure.subplots_adjust(left=0.1, bottom=0.125, top=0.9, right=0.97)
		self.chart_canvas.draw()
		
		self.update_legend()
		
		# Update y limit values in settings panel
		y_lims = self.chart.ax.get_ylim()
		self.y_ax_min_value.SetValue(y_lims[0])
		self.y_ax_max_value.SetValue(y_lims[1])
		
		# Update x limit values in settings panel
		x_lims = self.chart.ax.get_xlim()
		self.x_ax_min_value.SetValue(x_lims[0])
		self.x_ax_max_value.SetValue(x_lims[1])
	
	def do_update_chart(self, *_):  # wxGlade: ChartViewer.<event_handler>
		print("Update Chart not implemented")
	
	def on_splitter_moved(self, *_):  # wxGlade: ChartViewer.<event_handler>
		"""
		Update the chart width and height settings after the splitter has been changed by the user
		"""

		self.figure_width_value.SetValue(self.ChartViewer_v_splitter.GetSashPosition())
		self.figure_height_value.SetValue(self.ChartViewer_h_splitter.GetSashPosition())
	
	# self.ChartViewer_Settings_Panel.SetSize((275, self.GetSize()[1]-70))
	
	def on_splitter_changed(self, *_):  # wxGlade: ChartViewer.<event_handler>
		"""
		Update the splitter on the chart after it has been changed by the user
		"""

		self.ChartViewer_h_splitter.SetSashPosition(self.figure_height_value.GetValue(), True)
		self.ChartViewer_v_splitter.SetSashPosition(self.figure_width_value.GetValue(), True)
	
	def update_ylim(self, _):  # wxGlade: ChartViewer.<event_handler>
		"""
		Update the ylim on the chart after it has been changed by the user
		"""
		
		self.chart.ax.set_ylim(self.y_ax_min_value.GetValue(), self.y_ax_max_value.GetValue())
		self.chart_figure.canvas.draw_idle()
		# TODO: Respect setting when switching to percentage, log etc.
	
	def update_xlim(self, _):  # wxGlade: ChartViewer.<event_handler>
		"""
		Update the xlim on the chart after it has been changed by the user
		"""
		
		self.chart.ax.set_xlim(self.x_ax_min_value.GetValue(), self.x_ax_max_value.GetValue())
		self.chart_figure.canvas.draw_idle()
		# TODO: Respect setting when switching to percentage, log etc.
	
	"""Save, load and reset"""
	
	def do_reset(self, *_):  # wxGlade: ChartViewer.<event_handler>
		"""
		Reset the chart properties
		"""
		
		self.colours = default_colours
		self.percentage_checkbox.SetValue(False)
		# TODO Width value was set somewhere else
		# self.width_value.SetValue(float(row[1]))
		self.use_log_checkbox.SetValue(False)
		self.log_base_value.SetValue(10)
		self.show_raw_data_checkbox.SetValue(False)
		self.show_outliers_checkbox.SetValue(True)
		self.outlier_mode_choice.SetSelection(0)
		self.error_bar_choice.SetSelection(0)
		self.styles = bw_default_styles
		self.legend_checkbox.SetValue(False)
		self.leg_cols_value.SetValue(1)
		self.leg_x_pos_value.SetValue(0.5)
		self.leg_y_pos_value.SetValue(0.5)
		self.top_border_value.SetValue(0.9)
		self.bottom_border_value.SetValue(0.1)
		self.left_border_value.SetValue(0.125)
		self.right_border_value.SetValue(0.9)
		# ylim max and min should be set based on the data self.ax.set_ylim(y_min, y_max)
		
		self.ChartViewer_h_splitter.SetSashPosition(1000, True)
		self.ChartViewer_v_splitter.SetSashPosition(1550, True)
		self.figure_height_value.SetValue(1000)
		self.figure_width_value.SetValue(1550)
		
		self.update_log()
		self.toggle_outliers()
		self.update_legend()
		self.update_borders()
		self.replot_chart()
		
		self.Layout()
		self.chart_figure.canvas.draw_idle()
	
	def do_save(self, *_):  # wxGlade: ChartViewer.<event_handler>
		"""
		Saves the chart in the location chosen by the user
			with the selected filetypes
		"""
		
		filetypes = []
		if self.png_checkbox.GetValue():
			filetypes.append("png")
		if self.svg_checkbox.GetValue():
			filetypes.append("svg")
		if self.pdf_checkbox.GetValue():
			filetypes.append("pdf")
		
		if len(filetypes) == 0:
			wx.MessageBox("Please choose one or more filetypes", "Error", wx.ICON_ERROR | wx.OK)
			return
		
		pathname = file_dialog(self, "*", "Save Chart", "", defaultDir=self.parent.Config.results_dir)
		
		if pathname is None:
			return
		
		try:
			# Case for the user specifying an extension in the dialog
			if os.path.splitext(pathname)[1] != '':
				self.chart.fig.savefig(f"{pathname}")
				pathname = os.path.splitext(pathname)[0]
			
			# Case for no extension specified (the expected behaviour)
			else:
				pathname = os.path.splitext(pathname)[0]
				for filetype in filetypes:
					# Do any of the files already exist?
					if os.path.isfile(f"{pathname}.{filetype}"):
						alert = wx.MessageDialog(
							self,
							f'A file named "{pathname}.{filetype}" already exists.\nDo you want to replace it?',
							"Overwrite File?",
							wx.ICON_QUESTION | wx.OK | wx.CANCEL
						)
						alert.SetOKLabel("Replace")
						if alert.ShowModal() != wx.ID_OK:
							return
					
					self.chart.fig.savefig(f"{pathname}.{filetype}")
					
					# NotificationMessage("GunShotMatch", message='Chart Saved Successfully',
					# 					parent=None, flags=wx.ICON_INFORMATION).Show()
				
			with open(f"{pathname}.settings", 'w') as file:
				self.save_settings(file)
		
		except:
			wx.LogError("Cannot save file '%s'." % pathname)
			traceback.print_exc()
	
	def save_settings(self, file):
		"""
		Saves the settings to the given file
		
		:param file:
		:type file:
		"""
		
		file.write(f"""colours;{','.join(self.colours)}
percentage;{self.percentage_checkbox.GetValue()}
width;{self.width_value.GetValue()}
use_log;{self.use_log_checkbox.GetValue()}
log_base;{self.log_base_value.GetValue()}
raw_data;{self.show_raw_data_checkbox.GetValue()}
outliers;{self.show_outliers_checkbox.GetValue()}
f"outlier_mode;{self.outlier_mode_choice.GetString(self.outlier_mode_choice.GetSelection()).lower()}
error_bar;{self.error_bar_choice.GetString(self.error_bar_choice.GetSelection()).lower()}
styles;{','.join(self.styles)}
legend;{self.legend_checkbox.GetValue()}
leg_cols;{self.leg_cols_value.GetValue()}
leg_x_pos;{self.leg_x_pos_value.GetValue()}
leg_y_pos;{self.leg_y_pos_value.GetValue()}
fig_width;{self.figure_width_value.GetValue()}
fig_height;{self.figure_height_value.GetValue()}
top_border;{self.top_border_value.GetValue()}
bottom_border;{self.bottom_border_value.GetValue()}
left_border;{self.left_border_value.GetValue()}
right_border;{self.right_border_value.GetValue()}
y_lim_max;{self.y_ax_max_value.GetValue()}
y_lim_min;{self.y_ax_min_value.GetValue()}
x_lim_max;{self.x_ax_max_value.GetValue()}
x_lim_min;{self.x_ax_min_value.GetValue()}
""")
		
		# file.write(f"colours;{','.join(self.colours)}\n")
		# file.write(f"percentage;{self.percentage_checkbox.GetValue()}\n")
		# file.write(f"width;{self.width_value.GetValue()}\n")
		# file.write(f"use_log;{self.use_log_checkbox.GetValue()}\n")
		# file.write(f"log_base;{self.log_base_value.GetValue()}\n")
		# file.write(f"raw_data;{self.show_raw_data_checkbox.GetValue()}\n")
		# file.write(f"outliers;{self.show_outliers_checkbox.GetValue()}\n")
		# file.write(
		# 	f"outlier_mode;{self.outlier_mode_choice.GetString(self.outlier_mode_choice.GetSelection()).lower()}\n")
		# file.write(f"error_bar;{self.error_bar_choice.GetString(self.error_bar_choice.GetSelection()).lower()}\n")
		# file.write(f"styles;{','.join(self.styles)}\n")
		# file.write(f"legend;{self.legend_checkbox.GetValue()}\n")
		# file.write(f"leg_cols;{self.leg_cols_value.GetValue()}\n")
		# file.write(f"leg_x_pos;{self.leg_x_pos_value.GetValue()}\n")
		# file.write(f"leg_y_pos;{self.leg_y_pos_value.GetValue()}\n")
		# file.write(f"fig_width;{self.figure_width_value.GetValue()}\n")
		# file.write(f"fig_height;{self.figure_height_value.GetValue()}\n")
		# file.write(f"top_border;{self.top_border_value.GetValue()}\n")
		# file.write(f"bottom_border;{self.bottom_border_value.GetValue()}\n")
		# file.write(f"left_border;{self.left_border_value.GetValue()}\n")
		# file.write(f"right_border;{self.right_border_value.GetValue()}\n")
		# file.write(f"y_lim_max;{self.y_ax_max_value.GetValue()}\n")
		# file.write(f"y_lim_min;{self.y_ax_min_value.GetValue()}\n")
		# file.write(f"x_lim_max;{self.x_ax_max_value.GetValue()}\n")
		# file.write(f"x_lim_min;{self.x_ax_min_value.GetValue()}\n")
	
	def load_settings(self, file):
		"""
		Loads the settings from the given file
		
		:param file:
		:type file:
		"""
		
		for row in file.readlines():
			row = row.rstrip("\r\n").split(";")

			if row[0] == "colours":
				self.colours = row[1].split(",")
			elif row[0] == "percentage":
				if row[1] == "True":
					self.percentage_checkbox.SetValue(True)
				else:
					self.percentage_checkbox.SetValue(False)
			elif row[0] == "width":
				self.width_value.SetValue(float(row[1]))
			elif row[0] == "use_log":
				if row[1] == "True":
					self.use_log_checkbox.SetValue(True)
				else:
					self.use_log_checkbox.SetValue(False)
			elif row[0] == "log_base":
				self.log_base_value.SetValue(int(row[1]))
			elif row[0] == "raw_data":
				if row[1] == "True":
					self.show_raw_data_checkbox.SetValue(True)
				else:
					self.show_raw_data_checkbox.SetValue(False)
			elif row[0] == "outliers":
				if row[1] == "True":
					self.show_outliers_checkbox.SetValue(True)
				else:
					self.show_outliers_checkbox.SetValue(False)
			elif row[0] == "outlier_mode":
				self.outlier_mode_choice.SetSelection(self.outlier_mode_choice.FindString(row[1]))
			elif row[0] == "error_bar":
				self.error_bar_choice.SetSelection(self.error_bar_choice.FindString(row[1]))
			elif row[0] == "styles":
				self.styles = row[1].split(",")
			elif row[0] == "legend":
				if row[1] == "True":
					self.legend_checkbox.SetValue(True)
				else:
					self.legend_checkbox.SetValue(False)
			elif row[0] == "leg_cols":
				self.leg_cols_value.SetValue(int(row[1]))
			elif row[0] == "leg_x_pos":
				self.leg_x_pos_value.SetValue(float(row[1]))
			elif row[0] == "leg_y_pos":
				self.leg_y_pos_value.SetValue(float(row[1]))
			elif row[0] == "fig_width":
				self.figure_width_value.SetValue(float(row[1]))
			elif row[0] == "fig_height":
				self.figure_height_value.SetValue(float(row[1]))
			elif row[0] == "top_border":
				self.top_border_value.SetValue(float(row[1]))
			elif row[0] == "bottom_border":
				self.bottom_border_value.SetValue(float(row[1]))
			elif row[0] == "left_border":
				self.left_border_value.SetValue(float(row[1]))
			elif row[0] == "right_border":
				self.right_border_value.SetValue(float(row[1]))
			elif row[0] == "y_lim_max":
				self.y_ax_max_value.SetValue(int(row[1]))
			elif row[0] == "y_lim_min":
				self.y_ax_min_value.SetValue(int(row[1]))
			elif row[0] == "x_lim_max":
				self.x_ax_max_value.SetValue(float(row[1]))
			elif row[0] == "x_lim_min":
				self.x_ax_min_value.SetValue(float(row[1]))
	
	def do_load(self, event):  # wxGlade: ChartViewer.<event_handler>
		"""
		Loads the settings from the file selected by the user
		
		:param event:
		:type event:
		"""
		
		pathname = file_dialog(
			self, "settings", "Load Settings", "Settings",
			style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
			defaultDir=self.parent.Config.results_dir
		)
		
		if pathname is None:
			return
		
		with open(pathname, 'r') as file:
			self.load_settings(file)
		
		self.on_splitter_changed()
		self.update_log()
		self.toggle_outliers()
		self.update_legend()
		self.update_borders()
		self.replot_chart()
		
		event.Skip()
	
	"""Configuration Popups"""
	
	def configure_colours(self, *_):  # wxGlade: ChartViewer.<event_handler>
		"""
		Opens the ColourPickerDialog to allow the user to choose the colours for the chart
		"""
		
		dlg = ColourPickerDialog(self, selection_choices=self.colours)
		res = dlg.ShowModal()
		if res == wx.ID_OK:
			self.colours = dlg.colour_list
			dlg.Destroy()
			self.replot_chart()
	
	def configure_styles(self, *_):  # wxGlade: ChartViewer.<event_handler>
		"""
		Opens the StylePickerDialog to allow the user to choose the styles for the chart
		"""
		
		dlg = StylePickerDialog(self, selection_choices=self.styles)
		res = dlg.ShowModal()
		if res == wx.ID_OK:
			self.styles = dlg.style_list
			dlg.Destroy()
			self.replot_chart()
		
	"""Collapse Functions"""
	
	def collapse_general(self, event):  # wxGlade: ChartViewer.<event_handler>
		"""
		Collapse the general section of the options
		
		:param event:
		:type event:
		"""
		
		if not self.general_panel.Hide():
			self.general_panel.Show()
			self.general_header.SetLabel(collapse_label("General", False))
		else:
			self.general_header.SetLabel(collapse_label("General"))
		self.Layout()
		event.Skip()
	
	def collapse_legend(self, event):  # wxGlade: ChartViewer.<event_handler>
		"""
		Collapse the legend section of the options

		:param event:
		:type event:
		"""
		
		if not self.legend_panel.Hide():
			self.legend_panel.Show()
			self.legend_header.SetLabel(collapse_label("Legend", False))
		else:
			self.legend_header.SetLabel(collapse_label("Legend"))
		self.Layout()
		event.Skip()
	
	def collapse_size(self, event):  # wxGlade: ChartViewer.<event_handler>
		"""
		Collapse the size section of the options

		:param event:
		:type event:
		"""
		
		if not self.size_panel.Hide():
			self.size_panel.Show()
			self.size_header.SetLabel(collapse_label("Size", False))
		else:
			self.size_header.SetLabel(collapse_label("Size"))
		self.Layout()
		event.Skip()
	
	def collapse_borders(self, event):  # wxGlade: ChartViewer.<event_handler>
		"""
		Collapse the borders section of the options

		:param event:
		:type event:
		"""
		
		if not self.borders_panel.Hide():
			self.borders_panel.Show()
			self.borders_header.SetLabel(collapse_label("Borders", False))
		else:
			self.borders_header.SetLabel(collapse_label("Borders"))
		self.Layout()
		event.Skip()
	
	def collapse_ylim(self, event):  # wxGlade: ChartViewer.<event_handler>
		"""
		Collapse the ylim section of the options

		:param event:
		:type event:
		"""
		
		if not self.ylim_panel.Hide():
			self.ylim_panel.Show()
			self.ylim_header.SetLabel(collapse_label("y-Axis", False))
		else:
			self.ylim_header.SetLabel(collapse_label("y-Axis"))
		self.Layout()
		event.Skip()
	
	def collapse_filetypes(self, event):  # wxGlade: ChartViewer.<event_handler>
		"""
		Collapse the filetypes section of the options

		:param event:
		:type event:
		"""
		
		if not self.filetypes_panel.Hide():
			self.filetypes_panel.Show()
			self.filetypes_header.SetLabel(collapse_label("Filetypes", False))
		else:
			self.filetypes_header.SetLabel(collapse_label("Filetypes"))
		self.Layout()
		event.Skip()

	def collapse_xlim(self, event):  # wxGlade: ChartViewer.<event_handler>
		"""
		Collapse the xlim section of the options

		:param event:
		:type event:
		"""
		
		if not self.xlim_panel.Hide():
			self.xlim_panel.Show()
			self.xlim_header.SetLabel(collapse_label("x-Axis", False))
		else:
			self.xlim_header.SetLabel(collapse_label("x-Axis"))
		self.Layout()
		event.Skip()
		
	def collapse_data(self, event):  # wxGlade: ChartViewer.<event_handler>
		"""
		Collapse the data section of the options

		:param event:
		:type event:
		"""
		
		if not self.data_panel.Hide():
			self.data_panel.Show()
			self.data_header.SetLabel(collapse_label("Data", False))
		else:
			self.data_header.SetLabel(collapse_label("Data"))
		self.Layout()
		event.Skip()

	def collapse_log(self, event):  # wxGlade: ChartViewer.<event_handler>
		"""
		Collapse the logarithm section of the options

		:param event:
		:type event:
		"""
		
		if not self.log_panel.Hide():
			self.log_panel.Show()
			self.log_header.SetLabel(collapse_label("Logarithmic", False))
		else:
			self.log_header.SetLabel(collapse_label("Logarithmic"))
		self.Layout()
		event.Skip()
	
	def collapse_samples(self, event):  # wxGlade: ChartViewer.<event_handler>
		"""
		Collapse the samples section of the options

		:param event:
		:type event:
		"""
		
		if not self.samples_panel.Hide():
			self.samples_panel.Show()
			self.samples_header.SetLabel(collapse_label("Samples", False))
		else:
			self.samples_header.SetLabel(collapse_label("Samples"))
		self.Layout()
		event.Skip()
	
	"""Sample List Viewer Buttons"""
	
	def on_sample_up(self, event):  # wxGlade: ChartViewer.<event_handler>
		"""
		Move the selected sample up

		:param event:
		:type event:
		"""

		self.sample_move(-1)
		event.Skip()

	def on_sample_down(self, event):  # wxGlade: ChartViewer.<event_handler>
		"""
		Move the selected sample down
		
		:param event:
		:type event:
		"""
		
		self.sample_move(1)
		event.Skip()
		
	def sample_move(self, direction=1):
		"""
		Move the selected sample in the given direction
		
		:param direction: The direction to move the sample, 1 = Down, -1 = Up
		:type direction: int, optional
		"""
		selection = self.sample_list_viewer.GetSelection()
		selection_string = self.sample_list_viewer.GetString(selection)
		if self.sample_list_viewer.GetCount() == selection + direction or selection + direction < 0:
			return
		
		self.sample_list_viewer.Delete(selection)
		self.sample_list_viewer.InsertItems([selection_string], selection + direction)
		self.sample_list_viewer.SetSelection(selection + direction)
		
		self.projects = [self.sample_list_viewer.GetString(item) for item in range(self.sample_list_viewer.GetCount())]
		self.recalculate_data()
		self.replot_chart()

	def on_sample_add(self, _):  # wxGlade: ChartViewer.<event_handler>
		"""
		Adds the sample chosen by the user to the chart
		"""
		
		selected_projects = file_dialog_multiple(
			self, "info", "Choose a Project to Open", "info files",
			style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE,
			defaultDir=self.parent._parent.Config.results_dir
		)
		
		if selected_projects is None:
			return
		
		for project in selected_projects:
			self.add_sample(project)
		self.compound_order()
		
		self.recalculate_data()
		self.replot_chart()
		
	def add_sample(self, selected_project):
		"""
		Adds a sample to the chart
		
		:param selected_project:
		:type selected_project:
		"""
		
		pretty_name = os.path.splitext(os.path.split(selected_project)[-1])[0]
		
		if pretty_name in self.projects or pretty_name is None:
			# Sample is already on the chart or None; ignore
			return
	
		self.sample_list_viewer.Append(pretty_name)
		
		self.load_data(selected_project, pretty_name)
		
	def load_data(self, selected_project, pretty_name):
		"""
		Load Chart Data
		
		:param selected_project:
		:type selected_project:
		:param pretty_name:
		:type pretty_name:
		"""
		
		self.chart_data = pandas.concat([
			self.chart_data,
			pandas.read_csv(
				f"Results/CSV/{pretty_name}_CHART_DATA.csv",
				sep=";",
				index_col=0
				)],
			axis=1,
			sort=False
		)
		
		with open(selected_project, "r") as f:
			self.sample_lists[pretty_name] = [x.rstrip("\r\n") for x in f.readlines()]
		
		self.index_files[pretty_name] = selected_project
		
		self.chart_data.drop("Compound Names", axis=1, inplace=True)
		self.chart_data['Compound Names'] = self.chart_data.index

	def compound_order(self):
		"""
		Determine the order of compounds on graph
		
		:return:
		:rtype:
		"""
		
		for compound in self.chart_data.index.values:
			self.chart_data["Count"] = self.chart_data.apply(df_count, args=(
				[f"{sample} Peak Area" for sample in self.projects],), axis=1)
		
		self.chart_data['Compound Names'] = self.chart_data.index
		self.chart_data = self.chart_data.sort_values(['Count', 'Compound Names'])
		self.chart_data.fillna(0, inplace=True)
		
	def on_sample_remove(self, event):  # wxGlade: ChartViewer.<event_handler>
		"""
		Removes the selected sample from the chart
		
		:param event:
		:type event:
		"""
		selection = self.sample_list_viewer.GetSelection()
		if selection == -1:
			return
		
		selection_string = self.sample_list_viewer.GetString(selection)
		if selection_string == '':
			return
		
		self.sample_list_viewer.Delete(self.sample_list_viewer.GetSelection())
		
		self.projects = [self.sample_list_viewer.GetString(item) for item in range(self.sample_list_viewer.GetCount())]
		
		# Reload Chart Data
		self.chart_data = pandas.DataFrame()
		self.projects = [self.sample_list_viewer.GetString(item) for item in range(self.sample_list_viewer.GetCount())]
		for pretty_name in self.projects:
			self.load_data(self.index_files[pretty_name], pretty_name)
		self.compound_order()
		self.recalculate_data()
		self.replot_chart()
		
		event.Skip()
		
	def do_save_settings(self, event):  # wxGlade: ChartViewer.<event_handler>
		"""
		Saves the chart settings to the file chosen by the user
		
		:param event:
		:type event:
		"""
		pathname = file_dialog(
			self, "settings", "Save Settings", "Settings",
			defaultDir=self.parent.Config.results_dir
		)
		
		if pathname is None:
			return
		
		try:
			with open(pathname, 'w') as file:
				self.save_settings(file)
		except:
			wx.LogError("Cannot save file '%s'." % pathname)
			traceback.print_exc()
		
		event.skip()

	def move_legend(self, _):  # wxGlade: ChartViewer.<event_handler>
		"""
		Handler for moving legend to the previously set x and y positions
		"""
		
		if self.legend_checkbox.GetValue():
			self.legend.set_bbox_to_anchor((self.leg_x_pos_value.GetValue(), self.leg_y_pos_value.GetValue()))
			self.chart_figure.canvas.draw_idle()
		else:
			pass
		
# end of class ChartViewer
