#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  Comparison.py
"""Class that does nothing and can be removed"""
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2019 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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

import wx

# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade


class Comparison(wx.Frame):
	def __init__(self, *args, **kwds):
		# begin wxGlade: Comparison.__init__
		kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_FRAME_STYLE | wx.MAXIMIZE | wx.MINIMIZE
		wx.Frame.__init__(self, *args, **kwds)
		self.SetSize((900, 900))
		self.settings_panel = wx.Panel(self, wx.ID_ANY)
		self.bb_points_value = wx.SpinCtrl(self.settings_panel, wx.ID_ANY, "0", min=0, max=100, style=0)
		self.bb_scans_value = wx.SpinCtrl(self.settings_panel, wx.ID_ANY, "0", min=0, max=100, style=0)
		self.alignment_Dw_value = wx.TextCtrl(self.settings_panel, wx.ID_ANY, "", style=wx.TE_NO_VSCROLL)
		self.alignment_Gw_value = wx.TextCtrl(self.settings_panel, wx.ID_ANY, "", style=wx.TE_NO_VSCROLL)
		self.alignment_min_peaks_value = wx.TextCtrl(self.settings_panel, wx.ID_ANY, "", style=wx.TE_NO_VSCROLL)
		self.mass_range_value = wx.TextCtrl(self.settings_panel, wx.ID_ANY, "", style=wx.TE_NO_VSCROLL)
		self.base_peak_filter_value = wx.TextCtrl(self.settings_panel, wx.ID_ANY, "", style=wx.TE_NO_VSCROLL)
		self.noise_thresh_value = wx.SpinCtrl(self.settings_panel, wx.ID_ANY, "0", min=0, max=100, style=0)
		self.tophat_struct_value = wx.TextCtrl(self.settings_panel, wx.ID_ANY, "", style=wx.TE_NO_VSCROLL)
		self.tophat_struct_units = wx.Choice(self.settings_panel, wx.ID_ANY, choices=["min", "sec", "ms"])
		self.target_range_min_value = wx.TextCtrl(self.settings_panel, wx.ID_ANY, "", style=wx.TE_NO_VSCROLL)
		self.target_range_max_value = wx.TextCtrl(self.settings_panel, wx.ID_ANY, "", style=wx.TE_NO_VSCROLL)
		self.pretty_name_value = wx.TextCtrl(self.settings_panel, wx.ID_ANY, "")
		self.pretty_name_clear = wx.BitmapButton(self.settings_panel, wx.ID_ANY, wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, wx.ART_MENU))
		self.project_quantitative = wx.CheckBox(self.settings_panel, wx.ID_ANY, "Quantitative")
		self.project_merge = wx.CheckBox(self.settings_panel, wx.ID_ANY, "Merge")
		self.project_qualitative = wx.CheckBox(self.settings_panel, wx.ID_ANY, "Qualitative")
		self.project_counter = wx.CheckBox(self.settings_panel, wx.ID_ANY, "Counter")
		self.project_spectra = wx.CheckBox(self.settings_panel, wx.ID_ANY, "Spectra")
		self.project_charts = wx.CheckBox(self.settings_panel, wx.ID_ANY, "Charts")
		self.import_apply_btn = wx.Button(self.settings_panel, wx.ID_ANY, "Apply")
		self.default = wx.Button(self.settings_panel, wx.ID_ANY, "Default")
		self.reset = wx.Button(self.settings_panel, wx.ID_ANY, "Reset")
		self.queue_btn = wx.Button(self.settings_panel, wx.ID_ANY, "Add to Queue")
		self.run_btn = wx.Button(self.settings_panel, wx.ID_ANY, "Run")
		self.project_log_panel = wx.Panel(self, wx.ID_ANY)
		self.project_log_text_control = wx.TextCtrl(self.project_log_panel, wx.ID_ANY, "", style=wx.TE_CHARWRAP | wx.TE_MULTILINE | wx.TE_READONLY)
		self.project_log_save_btn = wx.Button(self.project_log_panel, wx.ID_ANY, "Save Log")

		self.__set_properties()
		self.__do_layout()

		self.Bind(wx.EVT_BUTTON, self.on_pretty_name_clear, self.pretty_name_clear)
		self.Bind(wx.EVT_BUTTON, self.do_apply, self.import_apply_btn)
		self.Bind(wx.EVT_BUTTON, self.do_default, self.default)
		self.Bind(wx.EVT_BUTTON, self.do_reset, self.reset)
		self.Bind(wx.EVT_BUTTON, self.do_enqueue, self.queue_btn)
		self.Bind(wx.EVT_BUTTON, self.do_new_project, self.run_btn)
		self.Bind(wx.EVT_BUTTON, self.on_project_log_save, self.project_log_save_btn)
		# end wxGlade

	def __set_properties(self):
		# begin wxGlade: Comparison.__set_properties
		self.SetTitle("Run Comparison")
		self.bb_points_value.SetMinSize((120, 29))
		self.bb_scans_value.SetMinSize((120, 29))
		self.alignment_Dw_value.SetMinSize((50, 29))
		self.alignment_Dw_value.SetMaxLength(4)
		self.alignment_Gw_value.SetMinSize((50, 29))
		self.alignment_Gw_value.SetMaxLength(4)
		self.alignment_min_peaks_value.SetMinSize((50, 29))
		self.alignment_min_peaks_value.SetMaxLength(4)
		self.mass_range_value.SetMinSize((300, 29))
		self.base_peak_filter_value.SetMinSize((300, 29))
		self.base_peak_filter_value.SetToolTip("Peaks with these base ions (i.e. the most intense peak in the mass spectrum) will be excluded from the results. This can be useful for excluding compounds related to septum bleed, which usually have a base ion at m/z 73")
		self.noise_thresh_value.SetMinSize((120, 29))
		self.tophat_struct_value.SetMinSize((50, 29))
		self.tophat_struct_value.SetMaxLength(4)
		self.tophat_struct_units.SetSelection(0)
		self.target_range_min_value.SetMinSize((55, 29))
		self.target_range_min_value.SetMaxLength(5)
		self.target_range_max_value.SetMinSize((55, 29))
		self.target_range_max_value.SetMaxLength(5)
		self.pretty_name_value.SetMinSize((260, 29))
		self.pretty_name_clear.SetSize(self.pretty_name_clear.GetBestSize())
		self.project_quantitative.SetValue(1)
		self.project_merge.SetValue(1)
		self.project_qualitative.SetValue(1)
		self.project_counter.SetValue(1)
		self.project_spectra.SetValue(1)
		self.project_charts.SetValue(1)
		# end wxGlade

	def __do_layout(self):
		# begin wxGlade: Comparison.__do_layout
		parent_sizer = wx.BoxSizer(wx.HORIZONTAL)
		project_log_sizer = wx.BoxSizer(wx.VERTICAL)
		settings_v_sizer = wx.BoxSizer(wx.VERTICAL)
		settings_grid_sizer = wx.FlexGridSizer(9, 3, 10, 10)
		new_project_button_sizer = wx.BoxSizer(wx.VERTICAL)
		project_settings_run_sizer = wx.BoxSizer(wx.HORIZONTAL)
		project_settings_button_sizer = wx.BoxSizer(wx.HORIZONTAL)
		new_project_steps_sizer = wx.GridSizer(4, 2, 0, 0)
		pretty_name_sizer = wx.BoxSizer(wx.VERTICAL)
		pretty_name_value_sizer = wx.BoxSizer(wx.HORIZONTAL)
		range_sizer = wx.BoxSizer(wx.VERTICAL)
		target_range_grid_sizer = wx.FlexGridSizer(1, 4, 0, 0)
		tophat_grid_sizer = wx.FlexGridSizer(1, 3, 0, 0)
		noise_thresh_grid_sizer_copy = wx.FlexGridSizer(1, 3, 0, 0)
		filter_sizer = wx.BoxSizer(wx.VERTICAL)
		mass_range_sizer = wx.BoxSizer(wx.VERTICAL)
		alignment_sizer = wx.BoxSizer(wx.VERTICAL)
		alignment_grid_sizer = wx.GridSizer(3, 2, 0, 0)
		alignment_Dw_sizer = wx.BoxSizer(wx.HORIZONTAL)
		bb_sizer = wx.BoxSizer(wx.VERTICAL)
		bb_grid_sizer = wx.GridSizer(2, 2, 0, 0)
		bb_top_text = wx.StaticText(self.settings_panel, wx.ID_ANY, "Settings for Biller and Biemann Peak Detection")
		bb_top_text.SetToolTip("Settings for PyMS implementation of BillerBiemann peak detection")
		bb_sizer.Add(bb_top_text, 0, 0, 0)
		bb_points_label = wx.StaticText(self.settings_panel, wx.ID_ANY, "Number of Points: ")
		bb_points_label.SetToolTip("The window width, in data points, for detecting the local maxima")
		bb_grid_sizer.Add(bb_points_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		bb_grid_sizer.Add(self.bb_points_value, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		bb_scans_label = wx.StaticText(self.settings_panel, wx.ID_ANY, "Number of Scans: ")
		bb_scans_label.SetToolTip("The number of scans across which neighbouring, apexing, ions are combined and considered as belonging to the same peak")
		bb_grid_sizer.Add(bb_scans_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		bb_grid_sizer.Add(self.bb_scans_value, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		bb_sizer.Add(bb_grid_sizer, 1, wx.ALL | wx.EXPAND, 5)
		settings_grid_sizer.Add(bb_sizer, 1, wx.EXPAND, 0)
		new_project_v_line_1 = wx.StaticLine(self.settings_panel, wx.ID_ANY, style=wx.LI_VERTICAL)
		settings_grid_sizer.Add(new_project_v_line_1, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 2)
		alignment_top_text = wx.StaticText(self.settings_panel, wx.ID_ANY, "Settings for Dynamic Peak Alignment")
		alignment_top_text.SetToolTip("Settings for PyMS Dynamic Peak Alignment")
		alignment_sizer.Add(alignment_top_text, 0, 0, 0)
		alignment_Dw_label = wx.StaticText(self.settings_panel, wx.ID_ANY, "RT Modulation: ")
		alignment_grid_sizer.Add(alignment_Dw_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		alignment_Dw_sizer.Add(self.alignment_Dw_value, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		alignment_Dw_label_2 = wx.StaticText(self.settings_panel, wx.ID_ANY, " s", style=wx.ALIGN_LEFT)
		alignment_Dw_sizer.Add(alignment_Dw_label_2, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		alignment_grid_sizer.Add(alignment_Dw_sizer, 1, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 0)
		alignment_Gw_label = wx.StaticText(self.settings_panel, wx.ID_ANY, "Gap Penalty: ")
		alignment_grid_sizer.Add(alignment_Gw_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		alignment_grid_sizer.Add(self.alignment_Gw_value, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		alignment_min_peaks_label = wx.StaticText(self.settings_panel, wx.ID_ANY, "Min Peaks: ")
		alignment_grid_sizer.Add(alignment_min_peaks_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		alignment_grid_sizer.Add(self.alignment_min_peaks_value, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		alignment_sizer.Add(alignment_grid_sizer, 1, wx.ALL | wx.EXPAND, 5)
		settings_grid_sizer.Add(alignment_sizer, 1, wx.EXPAND, 0)
		new_project_h_line_1 = wx.StaticLine(self.settings_panel, wx.ID_ANY)
		settings_grid_sizer.Add(new_project_h_line_1, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 2)
		settings_grid_sizer.Add((0, 0), 0, 0, 0)
		new_project_h_line_3 = wx.StaticLine(self.settings_panel, wx.ID_ANY)
		settings_grid_sizer.Add(new_project_h_line_3, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 2)
		mass_range_top_text = wx.StaticText(self.settings_panel, wx.ID_ANY, "Mass Range:   (min, max)")
		mass_range_sizer.Add(mass_range_top_text, 0, 0, 5)
		mass_range_sizer.Add(self.mass_range_value, 0, wx.BOTTOM | wx.RIGHT | wx.TOP, 6)
		mass_range_text_bottom = wx.StaticText(self.settings_panel, wx.ID_ANY, "This must be small enough to encompass all samples")
		mass_range_sizer.Add(mass_range_text_bottom, 0, wx.BOTTOM | wx.LEFT, 10)
		settings_grid_sizer.Add(mass_range_sizer, 1, wx.EXPAND, 0)
		new_project_v_line_4 = wx.StaticLine(self.settings_panel, wx.ID_ANY, style=wx.LI_VERTICAL)
		settings_grid_sizer.Add(new_project_v_line_4, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 2)
		base_peak_filter_text_1 = wx.StaticText(self.settings_panel, wx.ID_ANY, "Exclude peaks with the following base ion(s):")
		base_peak_filter_text_1.SetToolTip("Peaks with these base ions (i.e. the most intense peak in the mass spectrum) will be excluded from the results. This can be useful for excluding compounds related to septum bleed, which usually have a base ion at m/z 73")
		filter_sizer.Add(base_peak_filter_text_1, 0, 0, 0)
		filter_sizer.Add(self.base_peak_filter_value, 0, wx.BOTTOM | wx.RIGHT | wx.TOP, 6)
		base_peak_filter_text_2 = wx.StaticText(self.settings_panel, wx.ID_ANY, "Seperate multiple values with commas ( , )")
		base_peak_filter_text_2.SetToolTip("Peaks with these base ions (i.e. the most intense peak in the mass spectrum) will be excluded from the results. This can be useful for excluding compounds related to septum bleed, which usually have a base ion at m/z 73")
		filter_sizer.Add(base_peak_filter_text_2, 0, wx.BOTTOM | wx.LEFT, 10)
		settings_grid_sizer.Add(filter_sizer, 1, wx.EXPAND, 0)
		new_project_h_line_4 = wx.StaticLine(self.settings_panel, wx.ID_ANY)
		settings_grid_sizer.Add(new_project_h_line_4, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 2)
		settings_grid_sizer.Add((0, 0), 0, 0, 0)
		new_project_h_line_5 = wx.StaticLine(self.settings_panel, wx.ID_ANY)
		settings_grid_sizer.Add(new_project_h_line_5, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 2)
		noise_thresh_label = wx.StaticText(self.settings_panel, wx.ID_ANY, "Noise Filtering Threshold: ")
		noise_thresh_grid_sizer_copy.Add(noise_thresh_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		noise_thresh_grid_sizer_copy.Add(self.noise_thresh_value, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		noise_thresh_ions = wx.StaticText(self.settings_panel, wx.ID_ANY, "ions")
		noise_thresh_grid_sizer_copy.Add(noise_thresh_ions, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		settings_grid_sizer.Add(noise_thresh_grid_sizer_copy, 1, wx.EXPAND, 5)
		new_project_v_line_6 = wx.StaticLine(self.settings_panel, wx.ID_ANY, style=wx.LI_VERTICAL)
		settings_grid_sizer.Add(new_project_v_line_6, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 2)
		tophat_struct_label = wx.StaticText(self.settings_panel, wx.ID_ANY, "Tophat Structural Element: ")
		tophat_struct_label.SetToolTip("Structural element for PyMS Tophat baseline correction. The structural element needs to be larger than the features one wants to retain in the spectrum after the top-hat transform")
		tophat_grid_sizer.Add(tophat_struct_label, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		tophat_grid_sizer.Add(self.tophat_struct_value, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		tophat_grid_sizer.Add(self.tophat_struct_units, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		settings_grid_sizer.Add(tophat_grid_sizer, 1, wx.EXPAND, 5)
		new_project_h_line_6 = wx.StaticLine(self.settings_panel, wx.ID_ANY)
		settings_grid_sizer.Add(new_project_h_line_6, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 2)
		settings_grid_sizer.Add((0, 0), 0, 0, 0)
		new_project_h_line_7 = wx.StaticLine(self.settings_panel, wx.ID_ANY)
		settings_grid_sizer.Add(new_project_h_line_7, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 2)
		target_range_top_text = wx.StaticText(self.settings_panel, wx.ID_ANY, "Search for peaks between these times:")
		range_sizer.Add(target_range_top_text, 0, 0, 5)
		target_range_grid_sizer.Add(self.target_range_min_value, 0, 0, 0)
		target_mid_text = wx.StaticText(self.settings_panel, wx.ID_ANY, "minutes and ")
		target_range_grid_sizer.Add(target_mid_text, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		target_range_grid_sizer.Add(self.target_range_max_value, 0, 0, 0)
		target_post_text = wx.StaticText(self.settings_panel, wx.ID_ANY, "minutes")
		target_range_grid_sizer.Add(target_post_text, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		range_sizer.Add(target_range_grid_sizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 5)
		settings_grid_sizer.Add(range_sizer, 1, wx.EXPAND, 0)
		new_project_v_line_7 = wx.StaticLine(self.settings_panel, wx.ID_ANY, style=wx.LI_VERTICAL)
		settings_grid_sizer.Add(new_project_v_line_7, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 2)
		pretty_name_label = wx.StaticText(self.settings_panel, wx.ID_ANY, "(Optional) Human-Readable Name:")
		pretty_name_sizer.Add(pretty_name_label, 0, wx.BOTTOM, 5)
		pretty_name_value_sizer.Add(self.pretty_name_value, 0, 0, 0)
		pretty_name_value_sizer.Add(self.pretty_name_clear, 0, 0, 0)
		pretty_name_sizer.Add(pretty_name_value_sizer, 1, wx.EXPAND, 0)
		settings_grid_sizer.Add(pretty_name_sizer, 1, wx.EXPAND, 0)
		new_project_h_line_8 = wx.StaticLine(self.settings_panel, wx.ID_ANY)
		settings_grid_sizer.Add(new_project_h_line_8, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 2)
		settings_grid_sizer.Add((0, 0), 0, 0, 0)
		new_project_h_line_9 = wx.StaticLine(self.settings_panel, wx.ID_ANY)
		settings_grid_sizer.Add(new_project_h_line_9, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 2)
		steps_label = wx.StaticText(self.settings_panel, wx.ID_ANY, "Processing Steps: ")
		new_project_steps_sizer.Add(steps_label, 0, 0, 0)
		new_project_steps_sizer.Add((0, 0), 0, 0, 0)
		new_project_steps_sizer.Add(self.project_quantitative, 0, 0, 0)
		new_project_steps_sizer.Add(self.project_merge, 0, 0, 0)
		new_project_steps_sizer.Add(self.project_qualitative, 0, 0, 0)
		new_project_steps_sizer.Add(self.project_counter, 0, 0, 0)
		new_project_steps_sizer.Add(self.project_spectra, 0, wx.TOP, 5)
		new_project_steps_sizer.Add(self.project_charts, 0, wx.TOP, 7)
		settings_grid_sizer.Add(new_project_steps_sizer, 1, wx.EXPAND, 0)
		new_project_v_line_8 = wx.StaticLine(self.settings_panel, wx.ID_ANY, style=wx.LI_VERTICAL)
		settings_grid_sizer.Add(new_project_v_line_8, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 2)
		project_settings_button_sizer.Add(self.import_apply_btn, 0, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.RIGHT, 9)
		project_settings_button_sizer.Add(self.default, 0, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.RIGHT, 9)
		project_settings_button_sizer.Add(self.reset, 0, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.RIGHT, 9)
		new_project_button_sizer.Add(project_settings_button_sizer, 1, wx.ALIGN_RIGHT, 20)
		project_settings_run_sizer.Add(self.queue_btn, 0, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.RIGHT | wx.TOP, 9)
		project_settings_run_sizer.Add(self.run_btn, 0, wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.RIGHT | wx.TOP, 9)
		new_project_button_sizer.Add(project_settings_run_sizer, 1, wx.ALIGN_RIGHT, 0)
		settings_grid_sizer.Add(new_project_button_sizer, 1, wx.EXPAND, 0)
		settings_v_sizer.Add(settings_grid_sizer, 1, wx.EXPAND, 0)
		new_project_line = wx.StaticLine(self.settings_panel, wx.ID_ANY)
		settings_v_sizer.Add(new_project_line, 0, wx.EXPAND | wx.TOP, 10)
		self.settings_panel.SetSizer(settings_v_sizer)
		parent_sizer.Add(self.settings_panel, 5, wx.ALL | wx.EXPAND, 10)
		project_log_label = wx.StaticText(self.project_log_panel, wx.ID_ANY, "Log:")
		project_log_sizer.Add(project_log_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, 5)
		project_log_sizer.Add(self.project_log_text_control, 4, wx.EXPAND | wx.TOP, 5)
		project_log_sizer.Add(self.project_log_save_btn, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT, 0)
		self.project_log_panel.SetSizer(project_log_sizer)
		parent_sizer.Add(self.project_log_panel, 1, wx.ALL | wx.EXPAND, 10)
		self.SetSizer(parent_sizer)
		self.Layout()
		# end wxGlade

	def on_pretty_name_clear(self, event):  # wxGlade: Comparison.<event_handler>
		print("Event handler 'on_pretty_name_clear' not implemented!")
		event.Skip()

	def do_apply(self, event):  # wxGlade: Comparison.<event_handler>
		print("Event handler 'do_apply' not implemented!")
		event.Skip()

	def do_default(self, event):  # wxGlade: Comparison.<event_handler>
		print("Event handler 'do_default' not implemented!")
		event.Skip()

	def do_reset(self, event):  # wxGlade: Comparison.<event_handler>
		print("Event handler 'do_reset' not implemented!")
		event.Skip()

	def do_enqueue(self, event):  # wxGlade: Comparison.<event_handler>
		print("Event handler 'do_enqueue' not implemented!")
		event.Skip()

	def do_new_project(self, event):  # wxGlade: Comparison.<event_handler>
		print("Event handler 'do_new_project' not implemented!")
		event.Skip()

	def on_project_log_save(self, event):  # wxGlade: Comparison.<event_handler>
		print("Event handler 'on_project_log_save' not implemented!")
		event.Skip()

# end of class Comparison
