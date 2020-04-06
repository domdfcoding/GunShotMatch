#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  results_panel.py
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
from mathematical.utils import rounders
from pubsub import pub

# this package
from GuiV2.GSMatch2_Core.Experiment.identification.identification_panel import arrows, IdentificationPanel
from GuiV2.GSMatch2_Core.Experiment.identification.sort_filter_dialog import (
	Sort_Area, Sort_CAS, Sort_Experiments, Sort_Hit, Sort_MF, Sort_Name, Sort_RMF, Sort_RT, Sort_Similarity,
	)
from GuiV2.GSMatch2_Core.Project.exporters import ConsolidatePDFExporter
from .sort_filter_dialog import ConsolidatedSortFilterDialog, Sort_AvgHit, Sort_Freq


class ConsolidatedResultsPanel(IdentificationPanel):
	def __init__(
			self, parent, peak_list, id=wx.ID_ANY, pos=wx.DefaultPosition,
			size=wx.DefaultSize, style=0, name="ConsolidatedResultsPanel"):
		"""
		TODO: Standard deviation for hit numbers
		
		:param parent: The parent window.
		:type parent: wx.Window
		:param peak_list:
		:type peak_list: list of ConsolidatedPeak objects
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
		
		IdentificationPanel.__init__(self, parent, peak_list, id=id, pos=pos, size=size, style=style, name=name)

	def _create_columns(self):
		# Create Columns
		self.tree.AddColumn("", width=200) 	# RT x̄ / Hit
		self.tree.AddColumn("", width=400) 	# Peak Area x̄ / Name
		self.tree.AddColumn("")				# Peak No. / CAS
		self.tree.AddColumn("", width=140) 	# Similarity x̄ / Match x̄
		self.tree.AddColumn("", width=140) 	# No. Experiments / R Match x̄
		self.tree.AddColumn("", width=60) 	# Frequency
		self.tree.AddColumn("", width=110) 	# Hit No. x̄
		
		self.tree.SetMainColumn(0)  # the one with the tree in it...
		
		# Column Alignment
		# TODO: Make multiline text in column header correctly align right
		# self.tree.SetColumnAlignment(2, wx.ALIGN_RIGHT)
		# self.tree.SetColumnAlignment(3, wx.ALIGN_RIGHT)
		# self.tree.SetColumnAlignment(4, wx.ALIGN_RIGHT)
		# self.tree.SetColumnAlignment(5, wx.ALIGN_RIGHT)
		# self.tree.SetColumnAlignment(6, wx.ALIGN_RIGHT)
		# self.tree.SetColumnAlignment(7, wx.ALIGN_RIGHT)
		
		self.tree.custom_alignments = [
				[],
				[None, None, None, 			  wx.ALIGN_LEFT,  wx.ALIGN_LEFT,  wx.ALIGN_LEFT,  wx.ALIGN_LEFT,  wx.ALIGN_LEFT,  wx.ALIGN_RIGHT, wx.ALIGN_RIGHT],
				[None, None, wx.ALIGN_CENTER, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT],
				]
		
		self._update_header_labels()
	
	# TODO: default_filter_settings for new columns
	
	def _sort_peak_list(self):
		IdentificationPanel._sort_peak_list(self)
		
		if self.peak_sort == Sort_Experiments:
			self.peak_list.sort(key=lambda peak: len(peak), reverse=self.peak_descending)
		if self.peak_sort == Sort_Similarity:
			self.peak_list.sort(key=lambda peak: peak.average_ms_comparison, reverse=self.peak_descending)
	
	def _filter_peak_list(self):
		first_filtered_peak_list = IdentificationPanel._filter_peak_list(self)
		
		second_filtered_peak_list = []
		
		for peak in first_filtered_peak_list:
			if not len(peak) >= self.min_experiments:
				print("Samples")
				continue
			
			if not int(peak.average_ms_comparison) >= int(self.min_similarity):
				print("Similarity")
				continue
			
			second_filtered_peak_list.append(peak)
		
		return second_filtered_peak_list
	
	def _sort_hit_list(self, hit_list):
		hit_list = IdentificationPanel._sort_hit_list(self, hit_list)
		
		if self.hit_sort == Sort_Freq:
			hit_list.sort(key=lambda hit: len(hit[1]), reverse=self.hit_descending)
		elif self.hit_sort == Sort_AvgHit:
			hit_list.sort(key=lambda hit: hit[1].average_hit_number, reverse=self.hit_descending)
		
		return hit_list
	
	def _filter_hit_list(self, hit_list):
		first_filtered_hit_list = IdentificationPanel._filter_hit_list(self, hit_list)
		
		second_filtered_hit_list = []
		
		for hit_number, hit in first_filtered_hit_list:
			if not self.min_freq <= len(hit):
				continue
				
			second_filtered_hit_list.append((hit_number, hit))
		
		return second_filtered_hit_list
	
	def _add_peak(self, peak):
		if self.show_rsd:
			rt_stdev = f" ±{peak.rt_stdev / peak.rt:8.2%}"
			area_stdev = f" ±{peak.area_stdev / peak.area:8.2%}"
			similarity_stdev = f" ±{peak.ms_comparison_stdev / peak.average_ms_comparison:8.2%}"
		else:
			rt_stdev = area_stdev = similarity_stdev = ''
		
		peak_item = self.tree.AppendItem(self.root, f"{rounders(peak.rt / 60, '0.000000'):10}{rt_stdev}")
		self.tree.SetItemText(peak_item, f" {rounders(peak.area, '0.000000'):16,}{area_stdev}", 1)
		self.tree.SetItemText(peak_item, f" {peak.peak_number}", 2)
		self.tree.SetItemText(peak_item, f" {peak.average_ms_comparison:5.1f}{similarity_stdev}", 3)
		self.tree.SetItemText(peak_item, f" {len(peak)}", 4)
		self.tree.SetItemImage(peak_item, 0, which=wx.TreeItemIcon_Normal)
		# self.tree.SetItemImage(peak_item, 1, which=wx.TreeItemIcon_Expanded)
		self.tree.SetItemData(peak_item, peak)
		return peak_item
	
	def _add_hit(self, hit, peak_item, hit_number):
		if self.show_rsd:
			mf_stdev = f" ±{hit.match_factor_stdev / hit.match_factor:8.2%}"
			rmf_stdev = f" ±{hit.reverse_match_factor_stdev / hit.reverse_match_factor:8.2%}"
			hit_stdev = f" ±{hit.hit_number_stdev / hit.average_hit_number:8.2%}"
		else:
			mf_stdev = rmf_stdev = hit_stdev = ''
		
		hit_item = self.tree.AppendItem(peak_item, f'{hit_number + 1}')
		self.tree.SetItemText(hit_item, f"    {hit.name}", 1)
		self.tree.SetItemText(hit_item, f"{hit.cas}  ", 2)
		self.tree.SetItemText(hit_item, f"{hit.match_factor:.1f}{mf_stdev} ", 3)
		self.tree.SetItemText(hit_item, f"{hit.reverse_match_factor:.1f}{rmf_stdev} ", 4)
		self.tree.SetItemText(hit_item, f"{len(hit)}  ", 5)
		self.tree.SetItemText(hit_item, f"{hit.average_hit_number:.1f}{hit_stdev} ", 6)
		
		self.tree.SetItemImage(hit_item, 2)
		return hit_item
		
	def _update_header_labels(self):
		area_sort_arrow = " "
		rt_sort_arrow = " "
		cas_sort_arrow = " "
		name_sort_arrow = " "
		mf_sort_arrow = " "
		rmf_sort_arrow = " "
		hit_sort_arrow = " "
		freq_sort_arrow = " "
		avg_hit_sort_arrow = " "
		similarity_sort_arrow = " "
		n_experiments_sort_arrow = " "
		
		# Column Headers
		if self.peak_sort == Sort_RT:
			rt_sort_arrow = arrows[self.peak_descending]
		elif self.peak_sort == Sort_Area:
			area_sort_arrow = arrows[self.peak_descending]
		elif self.peak_sort == Sort_Experiments:
			n_experiments_sort_arrow = arrows[self.peak_descending]
		elif self.peak_sort == Sort_Similarity:
			similarity_sort_arrow = arrows[self.peak_descending]
		
		if self.hit_sort == Sort_Hit:
			hit_sort_arrow = arrows[self.hit_descending]
		elif self.hit_sort == Sort_CAS:
			cas_sort_arrow = arrows[self.hit_descending]
		elif self.hit_sort == Sort_Name:
			name_sort_arrow = arrows[self.hit_descending]
		elif self.hit_sort == Sort_MF:
			mf_sort_arrow = arrows[self.hit_descending]
		elif self.hit_sort == Sort_RMF:
			rmf_sort_arrow = arrows[self.hit_descending]
		elif self.hit_sort == Sort_Freq:
			freq_sort_arrow = arrows[self.hit_descending]
		elif self.hit_sort == Sort_AvgHit:
			avg_hit_sort_arrow = arrows[self.hit_descending]
		
		self.tree.SetColumnText(0, f"Average RT (mins){rt_sort_arrow}\nHit Number{hit_sort_arrow}")
		self.tree.SetColumnText(1, f"Average Peak Area{area_sort_arrow}\nName{name_sort_arrow}")
		self.tree.SetColumnText(2, f"Peak No.\nCAS{cas_sort_arrow}")
		self.tree.SetColumnText(3, f"MS Similarity x̄{similarity_sort_arrow}\nMatch x̄{mf_sort_arrow}")
		self.tree.SetColumnText(4, f"No. Experiments{n_experiments_sort_arrow}\nR Match x̄{rmf_sort_arrow}")
		self.tree.SetColumnText(5, f"\nFreq.{freq_sort_arrow}")
		self.tree.SetColumnText(6, f"\nHit No. x̄{avg_hit_sort_arrow}")
	
	def _setup_sort_filter_dialog(self):
		# Sort & Filter Dialog
		self.default_filter_settings()
		self.sort_filter_dialog = ConsolidatedSortFilterDialog(self)
	
	def default_filter_settings(self):
		IdentificationPanel.default_filter_settings(self)
		
		self.min_experiments = 0
		self.min_freq = 0
		self.min_similarity = 0
		self.show_rsd = 1
		
		self.n_hits = 5
	
	def export_pdf(self, input_filename, output_filename):
		ConsolidatePDFExporter(
				self,
				input_filename=input_filename,
				output_filename=output_filename,
				)
	
	def OnRightUp(self, event):
		pos = event.GetPosition()
		item, flags, col = self.tree.HitTest(pos)
		if item:
			print(f'Flags: {flags}, Col:{col}, Text: {self.tree.GetItemText(item, col)}')
			print(item)
			data = item.GetData()
			
			def on_view_indiv_peaks(_):
				wx.CallAfter(pub.sendMessage, "display_compounds_for_peak", peak_number=data.peak_number)
			
			def on_view_in_dataviewer(_):
				wx.CallAfter(pub.sendMessage, "view_in_dataviewer", peak_number=data.peak_number)
			
			menu = wx.Menu()
			
			if hasattr(self.Parent.Parent, "ident_panel"):
				if self.Parent.Parent.ident_panel:
					item1 = menu.Append(wx.ID_ANY, "View Individual Peaks")
					self.Bind(wx.EVT_MENU, on_view_indiv_peaks, item1)
					
			if hasattr(self.Parent.Parent, "data_panel"):
				if self.Parent.Parent.data_panel:
					item3 = menu.Append(wx.ID_ANY, "View in Data Viewer")
					self.Bind(wx.EVT_MENU, on_view_in_dataviewer, item3)
			
			self.PopupMenu(menu)
			menu.Destroy()
		
		event.Skip()
