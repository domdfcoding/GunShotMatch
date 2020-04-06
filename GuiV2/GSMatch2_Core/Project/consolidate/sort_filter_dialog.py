#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  sort_filter_dialog.py
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

# 3rd party
import wx

# this package
from GuiV2.GSMatch2_Core.Experiment.identification import (
	ID_Sort_Experiments, ID_Sort_Similarity, Sort_Experiments, Sort_Similarity, SortFilterDialog,
	)

ID_Sort_Freq = Sort_Freq = wx.NewIdRef()
ID_Sort_AvgHit = Sort_AvgHit = wx.NewIdRef()


class ConsolidatedSortFilterDialog(SortFilterDialog):
	def __init__(
			self, parent, id=wx.ID_ANY, title="Sort & Filter",
			pos=wx.DefaultPosition, size=(600, 480), style=0,
			name="ConsolidatedSortFilterDialog"
			):
		
		SortFilterDialog.__init__(
				self, parent, id=id, title=title, pos=pos, size=size,
				style=style,# | wx.RESIZE_BORDER,
				name=name)
	
	def create_main_panel(self):
		self.main_panel = wx.Panel(self, wx.ID_ANY)
		
		grid_sizer_1 = wx.FlexGridSizer(5, 2, 5, 10)
		
		grid_sizer_1.Add(self.create_sort_peaks_sizer(), 1, wx.EXPAND | wx.TOP, 3)
		grid_sizer_1.Add(self.create_sort_hits_sizer(), 1, wx.EXPAND | wx.TOP, 3)
		grid_sizer_1.Add(self.create_filter_rt_sizer(), 1, wx.EXPAND, 0)
		grid_sizer_1.Add(self.create_min_hits_sizer(), 1, wx.EXPAND, 0)
		grid_sizer_1.Add(self.create_filter_area_sizer(), 1, wx.EXPAND, 0)
		grid_sizer_1.Add(self.create_min_mf_sizer(), 1, wx.EXPAND, 0)
		grid_sizer_1.Add(self.create_min_experiments_sizer(), 1, wx.EXPAND, 0)
		grid_sizer_1.Add(self.create_min_freq_sizer(), 1, wx.EXPAND, 0)
		grid_sizer_1.Add(self.create_min_similarity_sizer(), 1, wx.EXPAND, 0)
		grid_sizer_1.Add(self.create_show_rsd_sizer(), 1, wx.EXPAND, 0)
		
		self.main_panel.SetSizer(grid_sizer_1)
		
		return self.main_panel
	
	# Sort Peaks
	def create_sort_peaks_sizer(self):
		# Use the original method to create the buttons but then create a new sizer below
		SortFilterDialog.create_sort_peaks_sizer(self)
		
		peaks_sort_by_sizer = wx.StaticBoxSizer(
				wx.StaticBox(self.main_panel, wx.ID_ANY, "Sort Peaks By: "),
				wx.VERTICAL)
		peaks_sort_by_grid = wx.FlexGridSizer(2, 2, 0, 2)
		
		peaks_sort_by_grid.Add(self.sort_rt, 0, wx.LEFT, 2)
		
		self.sort_similarity = wx.RadioButton(self.main_panel, ID_Sort_Similarity, "Similarity")
		peaks_sort_by_grid.Add(self.sort_similarity, 0, wx.RIGHT, 2)
		
		peaks_sort_by_grid.Add(self.sort_area, 0, wx.LEFT, 2)
		
		self.sort_n_experiments = wx.RadioButton(self.main_panel, ID_Sort_Experiments, "No. Experiments")
		peaks_sort_by_grid.Add(self.sort_n_experiments, 0, wx.RIGHT, 2)
		
		peaks_sort_by_sizer.Add(peaks_sort_by_grid, 1, wx.EXPAND, 0)
		
		peaks_sort_by_sizer.Add(self.peak_descending_check, 0, wx.BOTTOM | wx.LEFT, 2)
		
		return peaks_sort_by_sizer
	
	def set_peak_sort(self, by, descending=False):
		"""

		:param by: The criteria to sort the peaks by
		:type by:
		:param descending: Whether the peaks should be sorted in descending order
		:type descending: bool
		"""
		
		try:
			SortFilterDialog.set_peak_sort(self, by, descending)
		except ValueError:
			if by == Sort_Similarity:
				self.sort_similarity.SetValue(1)
			elif by == Sort_Experiments:
				self.sort_n_experiments.SetValue(1)
			else:
				raise ValueError("Unknown criteria")
	
	def get_peak_sort(self):
		
		sort_by, descending = SortFilterDialog.get_peak_sort(self)
		
		if sort_by is None:
			if self.sort_n_experiments.GetValue():
				return Sort_Experiments, descending
			elif self.sort_similarity.GetValue():
				return Sort_Similarity, descending
		
		return sort_by, descending
	
	# Sort Hits
	def create_sort_hits_sizer(self):
		# Use the original method to create the buttons but then create a new sizer below
		SortFilterDialog.create_sort_hits_sizer(self)
		
		sort_hits_box = wx.StaticBoxSizer(wx.StaticBox(self.main_panel, wx.ID_ANY, "Sort Hits By: "), wx.VERTICAL)
		hits_sort_by_grid = wx.FlexGridSizer(4, 2, 0, 2)
		
		hits_sort_by_grid.Add(self.sort_num, 0, wx.LEFT, 2)
		hits_sort_by_grid.Add(self.sort_name, 0, wx.RIGHT, 2)
		hits_sort_by_grid.Add(self.sort_cas, 0, wx.LEFT, 2)
		
		self.sort_freq = wx.RadioButton(self.main_panel, ID_Sort_Freq, "Frequency")
		self.sort_freq.SetToolTip("Sort the hits by the frequency the compound occurred")
		hits_sort_by_grid.Add(self.sort_freq, 0, wx.RIGHT, 2)
		
		hits_sort_by_grid.Add(self.sort_mf, 0, wx.LEFT, 2)
		hits_sort_by_grid.Add(self.sort_rmf, 0, wx.RIGHT, 2)
		hits_sort_by_grid.Add(self.hit_descending_check, 0, wx.BOTTOM | wx.LEFT, 2)
		
		self.sort_avg_hit = wx.RadioButton(self.main_panel, ID_Sort_AvgHit, "Average Hit Number")
		self.sort_avg_hit.SetToolTip("Sort the average hit number")
		hits_sort_by_grid.Add(self.sort_avg_hit, 0, wx.RIGHT, 2)
		
		sort_hits_box.Add(hits_sort_by_grid, 1, wx.EXPAND, 0)
		
		return sort_hits_box
	
	def set_hit_sort(self, by, descending=False):
		"""

		:param by: The criteria to sort the hits by
		:type by:
		:param descending: Whether the hits should be sorted in descending order
		:type descending: bool
		"""
		
		try:
			SortFilterDialog.set_hit_sort(self, by, descending)
		except ValueError:
			if by == Sort_Freq:
				self.sort_freq.SetValue(1)
			elif by == Sort_AvgHit:
				self.sort_avg_hit.SetValue(1)
			else:
				raise ValueError("Unknown criteria")
	
	def get_hit_sort(self):
		sort_by, descending = SortFilterDialog.get_hit_sort(self)
		
		if sort_by is None:
			if self.sort_freq.GetValue():
				return Sort_Freq, descending
			elif self.sort_avg_hit.GetValue():
				return Sort_AvgHit, descending
		
		return sort_by, descending
		
	# Min Experiments
	def create_min_experiments_sizer(self):
		peaks_experiments_box = wx.StaticBoxSizer(
				wx.StaticBox(
						self.main_panel,
						wx.ID_ANY,
						"Minimum Experiments: "),
				wx.VERTICAL)
		
		self.min_experiments_value = wx.SpinCtrl(self.main_panel, wx.ID_ANY, "0", min=0, max=100)
		self.min_experiments_value.SetMinSize((-1, 29))
		self.min_experiments_value.SetToolTip("Show only peaks that appear in more experiments than this value")
		
		peaks_experiments_box.Add(self.min_experiments_value, 0, wx.ALL, 2)
		
		return peaks_experiments_box
	
	def _load_n_experiments_settings(self):
		self.min_experiments_value.SetValue(self.Parent.min_experiments)

	def _reset_n_experiments_settings(self):
		self.min_experiments_value.SetValue(0)

	def _apply_n_experiments_settings(self):
		self.Parent.min_experiments = self.min_experiments_value.GetValue()

	# Min Freq
	def create_min_freq_sizer(self):
		hits_freq_box = wx.StaticBoxSizer(
				wx.StaticBox(
						self.main_panel,
						wx.ID_ANY,
						"Minimum Frequency: "),
				wx.VERTICAL)
		
		self.min_freq_value = wx.SpinCtrl(self.main_panel, wx.ID_ANY, "0", min=0, max=100)
		self.min_freq_value.SetMinSize((-1, 29))
		self.min_freq_value.SetToolTip("Show only hits that appeared in more freq than this value")
		
		hits_freq_box.Add(self.min_freq_value, 0, wx.ALL, 2)
		
		return hits_freq_box
	
	def _load_freq_settings(self):
		self.min_freq_value.SetValue(self.Parent.min_freq)

	def _reset_freq_settings(self):
		self.min_freq_value.SetValue(0)

	def _apply_freq_settings(self):
		self.Parent.min_freq = self.min_freq_value.GetValue()

	# Show RSD
	def create_show_rsd_sizer(self):
		
		show_rsd_box = wx.StaticBoxSizer(
				wx.StaticBox(
						self.main_panel,
						wx.ID_ANY,
						),
				wx.HORIZONTAL)
		
		self.show_rsd_check = wx.CheckBox(self.main_panel, label="Show  `± %RSD`")
		# self.show_rsd_check.SetToolTip("Show only hits that appeared in more freq than this value")
		
		# show_rsd_box.AddSpacer(10)
		show_rsd_box.Add(self.show_rsd_check, 0, wx.EXPAND | wx.ALL, 2)
		
		return show_rsd_box
	
	def _load_show_rsd_settings(self):
		self.show_rsd_check.SetValue(self.Parent.show_rsd)

	def _reset_show_rsd_settings(self):
		self.show_rsd_check.SetValue(1)

	def _apply_show_rsd_settings(self):
		self.Parent.show_rsd = self.show_rsd_check.GetValue()

	# Min Similarity
	def create_min_similarity_sizer(self):
		peaks_similarity_box = wx.StaticBoxSizer(
				wx.StaticBox(
						self.main_panel,
						wx.ID_ANY,
						"Minimum Similarity: "),
				wx.VERTICAL)
		
		self.min_similarity_value = wx.SpinCtrlDouble(self.main_panel, wx.ID_ANY, "0.0", min=0.0, max=1000.0)
		self.min_similarity_value.SetMinSize((-1, 29))
		self.min_similarity_value.SetToolTip("Show only peaks with a similarity higher than this value")
		self.min_similarity_value.SetDigits(0)
		self.min_similarity_value.SetIncrement(10.0)
		
		peaks_similarity_box.Add(self.min_similarity_value, 0, wx.ALL, 2)
		
		return peaks_similarity_box
	
	def _load_similarity_settings(self):
		self.min_similarity_value.SetValue(self.Parent.min_similarity)

	def _reset_similarity_settings(self):
		self.min_similarity_value.SetValue(0)

	def _apply_similarity_settings(self):
		self.Parent.min_similarity = self.min_similarity_value.GetValue()
	
	# All Settings
	def load_settings(self):
		SortFilterDialog.load_settings(self)
		self._load_similarity_settings()
		self._load_freq_settings()
		self._load_n_experiments_settings()
		self._load_show_rsd_settings()
	
	def apply_settings(self):
		SortFilterDialog.apply_settings(self)
		self._apply_show_rsd_settings()
		self._apply_n_experiments_settings()
		self._apply_freq_settings()
		self._apply_similarity_settings()
		
	# Buttons
	def on_reset(self, event):
		SortFilterDialog.on_reset(self, event)
		self._reset_similarity_settings()
		self._reset_freq_settings()
		self._reset_n_experiments_settings()
		self._reset_show_rsd_settings()
