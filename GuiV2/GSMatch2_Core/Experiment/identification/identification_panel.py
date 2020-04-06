#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  identification_panel.py
#
#  This file is part of GunShotMatch
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  CustomTreeListMainWindow and CustomHyperTreeList based on
#  wx.lib.agw.hypertreelist from wxPython.
#  Licenced under the wxWindows Licence
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
from domdf_wxpython_tools import CharValidator
from mathematical.utils import rounders
from wx.lib import buttons
from wx.lib.agw import customtreectrl, hypertreelist
from pubsub import pub
import numpy

# this package
from GuiV2.GSMatch2_Core.Experiment.identification.sort_filter_dialog import (
	SinglePeakSortFilterDialog, SortFilterDialog,
	Sort_Area, Sort_CAS, Sort_Hit, Sort_MF, Sort_Name, Sort_RMF, Sort_RT,
	)
from GuiV2.icons import get_icon
from GuiV2.GSMatch2_Core import Experiment

from wx.lib.agw.hypertreelist import _NO_IMAGE, _LINEATROOT, _MARGIN, _MAX_WIDTH


# Patch in additional methods for HyperTreeList
# See https://github.com/wxWidgets/Phoenix/compare/master...domdfcoding:master

def _ctc_CollapseAll(self):
	"""
	Collapses all :class:`CustomTreeCtrl` items.
	:note: This method suppresses the ``EVT_TREE_ITEM_EXPANDING`` and
	 ``EVT_TREE_ITEM_EXPANDED`` events because expanding many items int the
	 control would be too slow then.
	"""
	
	if self._anchor:
		self.CollapseAllChildren(self._anchor)
	
	self._sendEvent = True
	self._dirty = True


def _ctc_CollapseAllChildren(self, item):
	"""
	Collapses all the items children of the input item.
	:param `item`: an instance of :class:`GenericTreeItem`.
	:note: This method suppresses the ``EVT_TREE_ITEM_EXPANDING`` and
	 ``EVT_TREE_ITEM_EXPANDED`` events because expanding many items int the
	 control would be too slow then.
	"""

	self._sendEvent = False
	if not self.HasAGWFlag(customtreectrl.TR_HIDE_ROOT) or item != self.GetRootItem():
		self.Collapse(item)
		if self.IsExpanded(item):
			self._sendEvent = True
			return

	child, cookie = self.GetFirstChild(item)

	while child:
		self.CollapseAllChildren(child)
		child, cookie = self.GetNextChild(item, cookie)

	self._sendEvent = True
	self._dirty = True


customtreectrl.CustomTreeCtrl.CollapseAllChildren = _ctc_CollapseAllChildren
customtreectrl.CustomTreeCtrl.CollapseAll = _ctc_CollapseAll

for method in ["SetItemData", "GetItemData", "CollapseAllChildren", "CollapseAll"]:
	setattr(
			hypertreelist.HyperTreeList,
			method,
			hypertreelist.create_delegator_for(method)
			)
# End of patch

arrows = ("↑", "↓")


# TODO: Indicate in header row which columns have filters applied. Possible symbol ⧩
class IdentificationPanel(wx.ScrolledWindow):
	def __init__(
			self, parent, peak_list, id=wx.ID_ANY, pos=wx.DefaultPosition,
			size=wx.DefaultSize, style=0, name="IdentificationPanel"):
		"""
		:param parent: The parent window.
		:type parent: wx.Window
		:param peak_list:
		:type peak_list: list of QualifiedPeak objects
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
		
		wx.ScrolledWindow.__init__(self, parent, id=id, pos=pos, size=size, style=style | wx.HSCROLL | wx.VSCROLL, name=name)
		
		self.peak_list = peak_list[:]
		
		self._create_buttons()
		
		# Create HyperTreeList
		self.tree = CustomHyperTreeList(
				self, style=wx.BORDER_NONE,
				agwStyle=hypertreelist.TR_HAS_BUTTONS | hypertreelist.TR_COLUMN_LINES |
						 hypertreelist.TR_FULL_ROW_HIGHLIGHT | hypertreelist.TR_HIDE_ROOT |
						 hypertreelist.TR_LINES_AT_ROOT | hypertreelist.TR_ELLIPSIZE_LONG_ITEMS
				)
		self._setup_image_list()
		
		self._setup_sort_filter_dialog()

		self._create_columns()
		
		# Populate Tree
		self.root = self.tree.AddRoot("")
		self._populate_tree()
		
		self._set_properties()
		self._do_layout()
		self._bind_events()

	def _bind_events(self):
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.tree.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
		self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_activate)
		self.tree.GetHeaderWindow().Bind(wx.EVT_LEFT_DOWN, self.on_header_clicked)
		self.sort_filter_btn.Bind(wx.EVT_BUTTON, self.show_sort_filter)
		self.expand_all_btn.Bind(wx.EVT_BUTTON, self.expand_all)
		self.collapse_all_btn.Bind(wx.EVT_BUTTON, self.collapse_all)
	
	def collapse_all(self, event=None):
		self.tree.CollapseAll()

	def _create_buttons(self):
		self.btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
		
		self.sort_filter_btn = buttons.GenBitmapTextButton(self, -1, None, "Sort & Filter  ")
		self.sort_filter_btn.SetBitmapLabel(get_icon("data-filter", 24))
		self.expand_all_btn = buttons.GenButton(self, label="  Expand All  ")
		self.collapse_all_btn = buttons.GenButton(self, label="  Collapse All  ")
		
		self.btn_sizer.Add(self.sort_filter_btn, 0, wx.EXPAND, 0)
		self.btn_sizer.Add(self.expand_all_btn, 0, wx.EXPAND, 0)
		self.btn_sizer.Add(self.collapse_all_btn, 0, wx.EXPAND, 0)
	
	def _create_columns(self):
		# Create Columns
		self.tree.AddColumn("", width=170)
		self.tree.AddColumn("", width=400)
		self.tree.AddColumn("")
		self.tree.AddColumn("", width=80)
		self.tree.AddColumn("", width=80)
		self.tree.SetMainColumn(0)  # the one with the tree in it...
		
		# Column Alignment
		# TODO: Make multiline text in column header correctly align right
		# self.tree.SetColumnAlignment(2, wx.ALIGN_RIGHT)
		self.tree.SetColumnAlignment(3, wx.ALIGN_RIGHT)
		self.tree.SetColumnAlignment(4, wx.ALIGN_RIGHT)
		
		self.tree.custom_alignments = [
				[],
				[None, None, None, None, None],
				[None, None, wx.ALIGN_CENTER, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT],
				]
		
		self._update_header_labels()
	
	def default_filter_settings(self):
		self.min_rt = numpy.nanmin([peak.rt for peak in self.peak_list])
		self.max_rt = numpy.nanmax([peak.rt for peak in self.peak_list])
		self.min_area = numpy.nanmin([peak.area for peak in self.peak_list])
		self.max_area = numpy.nanmax([peak.area for peak in self.peak_list])
		
		self.peak_sort = Sort_RT
		self.peak_descending = False
		self.hit_descending = False
		self.hit_sort = Sort_Hit
		self.min_mf = 0
		self.min_rmf = 0
		
		self.filter_min_rt = self.min_rt
		self.filter_max_rt = self.max_rt
		self.filter_min_area = self.min_area
		self.filter_max_area = self.max_area
		
		self.n_hits = 0
	
	def _do_layout(self):
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.btn_sizer, 0, 0, 0)
		sizer.Add(self.tree, 1, wx.EXPAND | wx.TOP, 3)
		
		self.SetSizer(sizer)
		# self.Fit()
		self.Layout()
	
	def expand_all(self, event=None):
		self.tree.ExpandAll()
	
	def on_activate(self, evt):
		# TODO: Something like show the spectrum or a comparison between the peak and the reference?
		#  In either case need to add explanatory text to GUI
		
		print(f'on_activate: {self.tree.GetItemText(evt.GetItem())}')
		print(f'on_activate: {self.tree.GetItemData(evt.GetItem())}')
		print(f'on_activate: {self.tree.IsVisible(evt.GetItem())}')
	
	def OnSize(self, evt):
		self.tree.SetSize(self.GetSize())
	
	def on_header_clicked(self, event):
		print(f"Column {self.tree.GetHeaderWindow().XToCol(event.GetPosition().x)} clicked!")
		event.Skip()
	
	def OnRightUp(self, event):
		pos = event.GetPosition()
		item, flags, col = self.tree.HitTest(pos)
		if item:
			print(f'Flags: {flags}, Col:{col}, Text: {self.tree.GetItemText(item, col)}')
			print(item)
			item_data = item.GetData()
			
			def on_view_aligned_peaks(event):
				wx.CallAfter(pub.sendMessage, "display_compounds_for_peak", peak_number=item_data.peak_number)

			def on_view_consolidated(event):
				wx.CallAfter(pub.sendMessage, "view_peak_in_consolidated", peak_number=item_data.peak_number)
			
			menu = wx.Menu()
			
			item1 = menu.Append(wx.ID_ANY, "View Aligned Peaks")
			self.Bind(wx.EVT_MENU, on_view_aligned_peaks, item1)
			
			# TODO: If consolidate performed
			#if hasattr(self.Parent.Parent, "consolidate_panel"):
			#	if self.Parent.Parent.consolidate_panel:
			item2 = menu.Append(wx.ID_ANY, "View Consolidated Results")
			self.Bind(wx.EVT_MENU, on_view_consolidated, item2)
			
			self.PopupMenu(menu)
			menu.Destroy()
		
		event.Skip()
	
	def _sort_peak_list(self):
		# Sort peaks
		if self.peak_sort == Sort_RT:
			self.peak_list.sort(key=lambda peak: peak.rt, reverse=self.peak_descending)
		elif self.peak_sort == Sort_Area:
			self.peak_list.sort(key=lambda peak: peak.area, reverse=self.peak_descending)
	
	def _filter_peak_list(self):
		# Filter peaks
		
		filtered_peak_list = []
		
		for peak in self.peak_list:
			if not rounders(self.filter_min_rt, "0.00") <= rounders(peak.rt, "0.00") <= rounders(self.filter_max_rt,
																								 "0.00"):
				print("RT")
				print(self.filter_min_rt, peak.rt, rounders(peak.rt, "0.00"), self.filter_max_rt)
				continue
			if not rounders(self.filter_min_area, "0.00") <= rounders(peak.area, "0.00") <= rounders(
					self.filter_max_area, "0.00"):
				print("Area")
				print(self.filter_min_area, peak.area, rounders(peak.area, "0.00"), self.filter_max_area)
				continue
			
			filtered_peak_list.append(peak)
		
		return filtered_peak_list
	
	def _truncate_hit_list(self, hit_list):
		# Limit to n_hits
		if self.n_hits:
			hit_list = hit_list[:self.n_hits]
		
		return hit_list
	
	def _sort_hit_list(self, hit_list):
		# Sort hits
		if self.hit_sort == Sort_Hit:
			hit_list.sort(key=lambda hit: hit[0], reverse=self.hit_descending)
		elif self.hit_sort == Sort_Name:
			hit_list.sort(key=lambda hit: hit[1].name, reverse=self.hit_descending)
		elif self.hit_sort == Sort_CAS:
			hit_list.sort(key=lambda hit: hit[1].cas, reverse=self.hit_descending)
		elif self.hit_sort == Sort_MF:
			hit_list.sort(key=lambda hit: hit[1].match_factor, reverse=self.hit_descending)
		elif self.hit_sort == Sort_RMF:
			hit_list.sort(key=lambda hit: hit[1].reverse_match_factor, reverse=self.hit_descending)
		
		return hit_list
	
	def _filter_hit_list(self, hit_list):
		# Filter hits
		
		filtered_hit_list = []
		
		for hit_number, hit in hit_list:
			if not self.min_mf <= hit.match_factor:
				continue
			if not self.min_rmf <= hit.reverse_match_factor:
				continue
			
			filtered_hit_list.append((hit_number, hit))
		
		return filtered_hit_list
	
	def _prepare_hit_list(self, peak):
		hit_list_0 = list(enumerate(peak.hits))
		hit_list_1 = self._truncate_hit_list(hit_list_0)
		hit_list_2 = self._sort_hit_list(hit_list_1)
		hit_list_3 = self._filter_hit_list(hit_list_2)
		
		return hit_list_3
	
	def _add_peak(self, peak):
		peak_item = self.tree.AppendItem(self.root, f"{rounders(peak.rt / 60, '0.000000'):10}")
		self.tree.SetItemText(peak_item, f"{rounders(peak.area, '0.000000'):16,}", 1)
		self.tree.SetItemText(peak_item, str(peak.peak_number), 2)
		self.tree.SetItemImage(peak_item, 0, which=wx.TreeItemIcon_Normal)
		# self.tree.SetItemImage(peak_item, 1, which=wx.TreeItemIcon_Expanded)
		self.tree.SetItemData(peak_item, peak)
		return peak_item
	
	def _add_hit(self, hit, peak_item, hit_number):
		hit_item = self.tree.AppendItem(peak_item, f'{hit_number + 1}')
		self.tree.SetItemText(hit_item, f"    {hit.name}", 1)
		self.tree.SetItemText(hit_item, f"{hit.cas}  ", 2)
		self.tree.SetItemText(hit_item, f"{hit.match_factor}  ", 3)
		self.tree.SetItemText(hit_item, f"{hit.reverse_match_factor}  ", 4)
		self.tree.SetItemImage(hit_item, 2)
		return hit_item
	
	def _populate_tree(self):
		"""
		When sorting, if the column only contains data for hits,
		the hits will be sorted under each peak and not globally
		"""
		
		self.tree.DeleteChildren(self.root)
		self._update_header_labels()
		self._sort_peak_list()
		filtered_peak_list = self._filter_peak_list()
		
		# Populate Tree
		for peak in filtered_peak_list:
			
			peak_item = self._add_peak(peak)
			self.apply_font(peak_item)
			
			hit_list = self._prepare_hit_list(peak)
			
			for hit_number, hit in hit_list:
				hit_item = self._add_hit(hit, peak_item, hit_number)
				self.tree.SetItemData(hit_item, peak)
				self.apply_font(hit_item)
		
		self.tree.ExpandAll()
	
	def _setup_sort_filter_dialog(self):
		# Sort & Filter Dialog
		self.default_filter_settings()
		self.sort_filter_dialog = SortFilterDialog(self)
	
	def _setup_image_list(self):
		# Image List
		isz = (16, 16)
		self.il = wx.ImageList(isz[0], isz[1])
		self.il.Add(get_icon("chromatogram", isz[0]))
		self.il.Add(get_icon("peak", isz[0]))
		self.il.Add(get_icon("Conical_flask_red", isz[0]))
		
		self.tree.SetImageList(self.il)
	
	def _set_properties(self):
		# Make header taller
		self.tree._headerHeight = 40
		self.tree.DoHeaderLayout()

	def show_sort_filter(self, event=None):
		# Sort & Filter clicked
		if self.sort_filter_dialog.IsShownOnScreen():
			wx.CallAfter(self.sort_filter_dialog.SetFocus)
			wx.CallAfter(self.sort_filter_dialog.Raise)
		else:
			self.sort_filter_dialog.Show()
	
	def _update_header_labels(self):
		area_sort_arrow = " "
		rt_sort_arrow = " "
		cas_sort_arrow = " "
		name_sort_arrow = " "
		mf_sort_arrow = " "
		rmf_sort_arrow = " "
		hit_sort_arrow = " "
		
		# Column Headers
		if self.peak_sort == Sort_RT:
			rt_sort_arrow = arrows[self.peak_descending]
		elif self.peak_sort == Sort_Area:
			area_sort_arrow = arrows[self.peak_descending]
		
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
		
		self.tree.SetColumnText(0, f"""Retention Time (mins){rt_sort_arrow}
Hit Number{hit_sort_arrow}""")
		self.tree.SetColumnText(1, f"Peak Area{area_sort_arrow}\nName{name_sort_arrow}")
		self.tree.SetColumnText(2, f"Peak No.\nCAS{cas_sort_arrow}")
		self.tree.SetColumnText(3, f"\nMatch{mf_sort_arrow}")
		self.tree.SetColumnText(4, f"\nR Match{rmf_sort_arrow}")
	
	def apply_font(self, item):
		self.tree.SetItemFont(item, wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas'))
	
	def select_peak(self, peak_number):
		# Get sorted peak list with current settings
		self._sort_peak_list()
		filtered_peak_list = self._filter_peak_list()
		
		# Select the peak
		for index, peak in enumerate(filtered_peak_list):
			if peak.peak_number == peak_number:
				item = self.tree.GetItem(index)
				self.tree.SelectItem(item)
				self.tree.EnsureVisible(item.GetChildren()[-1])
				self.tree.SetFocus()
				break
			

class SinglePeakIdentificationPanel(IdentificationPanel):
	def __init__(
			self, parent, experiment_list, id=wx.ID_ANY, pos=wx.DefaultPosition,
			size=wx.DefaultSize, style=0, name="SinglePeakIdentificationPanel"):
		"""
		:param parent: The parent window.
		:type parent: wx.Window
		:param experiment_list:
		:type experiment_list: list of experiments
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
		
		self.experiment_list = experiment_list[:]
		
		self.peak_numbers = set()
		for experiment in self.experiment_list:
			for peak in experiment.ident_peaks:
				self.peak_numbers.add(peak.peak_number)
		
		self.expr_names = []
		
		IdentificationPanel.__init__(self, parent, [], id=id, pos=pos, size=size, style=style, name=name)
		
		# Convert peak_numbers to a list and sort smallest to largest
		self.peak_numbers = sorted(list(self.peak_numbers))
		for n in self.peak_numbers:
			self.peak_number_combo.Append(str(n))
		self.selected_peak = ''
	
	def _bind_events(self):
		IdentificationPanel._bind_events(self)
		
		# Peak Number Combo Box
		self.Bind(wx.EVT_COMBOBOX, self.on_peak_changed, self.peak_number_combo)
		self.peak_number_combo.Bind(wx.EVT_CHAR, self.on_peak_combo_char)
		
		# Next & previous buttons
		self.Bind(wx.EVT_BUTTON, self.next_peak, self.next_peak_btn)
		self.Bind(wx.EVT_BUTTON, self.previous_peak, self.previous_peak_btn)
	
	def _create_buttons(self):
		# Create Buttons
		# TODO: Tooltips and bindings
		IdentificationPanel._create_buttons(self)
		
		self.peak_number_combo = wx.ComboBox(self, size=(100, -1), validator=CharValidator("int-only"))
		self.previous_peak_btn = buttons.GenBitmapButton(self, bitmap=get_icon(wx.ART_GO_BACK, 24))
		self.previous_peak_btn.SetToolTip("Previous Peak")
		self.next_peak_btn = buttons.GenBitmapButton(self, bitmap=get_icon(wx.ART_GO_FORWARD, 24))
		self.next_peak_btn.SetToolTip("Next Peak")
		
		self.btn_sizer.AddSpacer(20)
		self.btn_sizer.Add(wx.StaticText(self, label="Peak Number: "), 1, wx.ALIGN_CENTER_VERTICAL, 0)
		self.btn_sizer.Add(self.peak_number_combo, 0, wx.EXPAND, 0)
		self.btn_sizer.Add(self.previous_peak_btn, 0, wx.EXPAND, 0)
		self.btn_sizer.Add(self.next_peak_btn, 0, wx.EXPAND, 0)
	
	def default_filter_settings(self):
		self.hit_descending = False
		self.hit_sort = Sort_Hit
		self.min_mf = 0
		self.min_rmf = 0
		
		self.n_hits = 0
	
	def next_peak(self, event):
		self.switch_peak(1)
	
	def _add_peak(self, peak):
		pass
		
	def _populate_tree(self):
		"""
		When sorting, if the column only contains data for hits,
		the hits will be sorted under each peak and not globally
		"""
		
		self.tree.DeleteChildren(self.root)
		self._update_header_labels()
		# No Peak sorting in this subclass
		# Note: No peak filtering support for the subclass
		
		# Populate Tree
		for peak, experiment_name in zip(self.peak_list, self.expr_names):
			
			peak_item = self.tree.AppendItem(self.root, experiment_name)
			self.tree.SetItemText(peak_item, f"{rounders(peak.area, '0.000000'):16,}", 1)
			self.tree.SetItemText(peak_item, f"{rounders(peak.rt / 60, '0.000000'):10}", 2)
			self.tree.SetItemImage(peak_item, 0, which=wx.TreeItemIcon_Normal)
			# self.tree.SetItemImage(peak_item, 1, which=wx.TreeItemIcon_Expanded)
			self.tree.SetItemData(peak_item, (peak, experiment_name))
			
			self.apply_font(peak_item)
			
			hit_list = self._prepare_hit_list(peak)

			for hit_number, hit in hit_list:
				hit_item = self._add_hit(hit, peak_item, hit_number)
				self.tree.SetItemData(hit_item, (peak, experiment_name))
				self.apply_font(hit_item)
		
		self.tree.ExpandAll()

	def previous_peak(self, event):
		self.switch_peak(-1)
	
	def set_peak(self, new_peak):
		if new_peak != '':
			# A peak has been selected
			# If the combobox is cleared this function gets called with an empty string
			
			if int(new_peak) in self.peak_numbers:
				self.selected_peak = str(new_peak)
				self.peak_list = []
				self.expr_names = []
				for experiment in self.experiment_list:
					for peak in experiment.ident_peaks:
						if peak.peak_number == int(self.selected_peak):
							self.peak_list.append(peak)
							self.expr_names.append(experiment.name)
							print(experiment.name)
							print(peak.area)
				self._populate_tree()
			
			else:
				wx.MessageBox("Invalid Peak Number!", "Invalid Peak Number!")
				self.peak_number_combo.SetValue(self.selected_peak)
				self.peak_number_combo.SetInsertionPointEnd()
		
		else:
			# Clear tree
			self.selected_peak = ''
			self.tree.DeleteChildren(self.root)

	def _setup_sort_filter_dialog(self):
		# Sort & Filter Dialog
		self.default_filter_settings()
		self.sort_filter_dialog = SinglePeakSortFilterDialog(self)
	
	def switch_peak(self, direction=1):
		if self.selected_peak == '':
			if direction > 0:
				current_index = -1
			elif direction <= 0:
				current_index = 0
		
		elif int(self.selected_peak) == self.peak_numbers[-1]:
			current_index = -1
		else:
			current_index = self.peak_numbers.index(int(self.selected_peak))
		self.set_peak(self.peak_numbers[current_index + direction])
		self.peak_number_combo.SetValue(self.selected_peak)
		
	def _update_header_labels(self):
		rt_sort_arrow = " "
		cas_sort_arrow = " "
		name_sort_arrow = " "
		mf_sort_arrow = " "
		rmf_sort_arrow = " "
		
		# Column Headers
		if self.hit_sort == Sort_CAS:
			cas_sort_arrow = arrows[self.hit_descending]
		elif self.hit_sort == Sort_Name:
			name_sort_arrow = arrows[self.hit_descending]
		elif self.hit_sort == Sort_MF:
			mf_sort_arrow = arrows[self.hit_descending]
		elif self.hit_sort == Sort_RMF:
			rmf_sort_arrow = arrows[self.hit_descending]
		
		self.tree.SetColumnText(0, f"""Experiment
Hit Number""")
		self.tree.SetColumnText(1, f"Peak Area\nName{name_sort_arrow}")
		self.tree.SetColumnText(2, f"RT (mins){rt_sort_arrow}\nCAS{cas_sort_arrow}")
		self.tree.SetColumnText(3, f"\nMatch{mf_sort_arrow}")
		self.tree.SetColumnText(4, f"\nR Match{rmf_sort_arrow}")
		
	def on_peak_combo_char(self, event):
		keycode = int(event.GetKeyCode())
		if keycode == wx.WXK_RETURN:
			self.on_peak_changed(event)
		else:
			event.Skip()
	
	def on_peak_changed(self, event):
		self.set_peak(self.peak_number_combo.GetValue())
		event.Skip()
		
	def export_pdf(self, input_filename, output_filename):
		Experiment.SinglePeakCompoundsPDFExporter(
				self.selected_peak,
				self.peak_list,
				self.expr_names,
				input_filename=input_filename,
				output_filename=output_filename,
				)
	
	def OnRightUp(self, event):
		pos = event.GetPosition()
		item, flags, col = self.tree.HitTest(pos)
		if item:
			print(f'Flags: {flags}, Col:{col}, Text: {self.tree.GetItemText(item, col)}')

			item_data = self.tree.GetItemData(item)
			
			def on_view_in_expr(event):
				wx.CallAfter(pub.sendMessage, "view_peak_in_expr", peak_number=item_data[0].peak_number, expr_name=item_data[1])
			
			def on_view_consolidated(event):
				wx.CallAfter(pub.sendMessage, "view_peak_in_consolidated", peak_number=item_data[0].peak_number)
			
			def on_view_in_dataviewer(event):
				# TODO:
				print("on_view_in_dataviewer")
			
			menu = wx.Menu()
			
			item1 = menu.Append(wx.ID_ANY, "View in Experiment")
			self.Bind(wx.EVT_MENU, on_view_in_expr, item1)
			
			if hasattr(self.Parent.Parent, "consolidate_panel"):
				if self.Parent.Parent.consolidate_panel:
					item2 = menu.Append(wx.ID_ANY, "View Consolidated Results")
					self.Bind(wx.EVT_MENU, on_view_consolidated, item2)
			
			if hasattr(self.Parent.Parent, "data_panel"):
				if self.Parent.Parent.data_panel:
					item3 = menu.Append(wx.ID_ANY, "View in Data Viewer")
					self.Bind(wx.EVT_MENU, on_view_in_dataviewer, item3)
			
			self.PopupMenu(menu)
			menu.Destroy()
		
		event.Skip()


class CustomTreeListMainWindow(hypertreelist.TreeListMainWindow):
	def __init__(self, *args, **kwargs):
		hypertreelist.TreeListMainWindow.__init__(self, *args, **kwargs)
		self.custom_alignments = []
	
	def PaintItem(self, item, dc, level):
		"""
		Actually draws an item.

		:param item: an instance of :class:`TreeListItem`;
		:param dc: an instance of :class:`wx.DC`.
		"""
		
		def _paintText(text, textrect, alignment):
			"""
			Sub-function to draw multi-lines text label aligned correctly.

			:param `text`: the item text label (possibly multiline);
			:param `textrect`: the label client rectangle;
			:param `alignment`: the alignment for the text label, one of ``wx.ALIGN_LEFT``,
			 ``wx.ALIGN_RIGHT``, ``wx.ALIGN_CENTER``.
			"""
			
			txt = text.splitlines()
			if alignment != wx.ALIGN_LEFT and len(txt):
				yorigin = textrect.Y
				for t in txt:
					w, h = dc.GetTextExtent(t)
					plus = textrect.Width - w
					if alignment == wx.ALIGN_CENTER:
						plus //= 2
					dc.DrawLabel(t, wx.Rect(textrect.X + plus, yorigin, w, yorigin + h))
					yorigin += h
				return
			dc.DrawLabel(text, textrect)
		
		attr = item.GetAttributes()
		
		if attr and attr.HasFont():
			dc.SetFont(attr.GetFont())
		elif item.IsBold():
			dc.SetFont(self._boldFont)
		if item.IsHyperText():
			dc.SetFont(self.GetHyperTextFont())
			if item.GetVisited():
				dc.SetTextForeground(self.GetHyperTextVisitedColour())
			else:
				dc.SetTextForeground(self.GetHyperTextNewColour())
		
		colText = wx.Colour(*dc.GetTextForeground())
		
		if item.IsSelected():
			if (wx.Platform == "__WXMAC__" and self._hasFocus):
				colTextHilight = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT)
			else:
				colTextHilight = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT)
		
		else:
			attr = item.GetAttributes()
			if attr and attr.HasTextColour():
				colText = attr.GetTextColour()
		
		if self._vistaselection:
			colText = colTextHilight = wx.BLACK
		
		total_w = self._owner.GetHeaderWindow().GetWidth()
		total_h = self.GetLineHeight(item)
		off_h = (self.HasAGWFlag(hypertreelist.TR_ROW_LINES) and [1] or [0])[0]
		off_w = (self.HasAGWFlag(hypertreelist.TR_COLUMN_LINES) and [1] or [0])[0]
		##        clipper = wx.DCClipper(dc, 0, item.GetY(), total_w, total_h) # only within line
		
		# text_w, text_h, dummy = dc.GetFullMultiLineTextExtent(item.GetText(self.GetMainColumn()))
		
		drawItemBackground = False
		# determine background and show it
		if attr and attr.HasBackgroundColour():
			colBg = attr.GetBackgroundColour()
			drawItemBackground = True
		else:
			colBg = self._backgroundColour
		
		dc.SetBrush(wx.Brush(colBg))
		if attr and attr.HasBorderColour():
			colBorder = attr.GetBorderColour()
			dc.SetPen(wx.Pen(colBorder, 1))
		else:
			dc.SetPen(wx.TRANSPARENT_PEN)
		
		if self.HasAGWFlag(wx.TR_FULL_ROW_HIGHLIGHT):
			
			# itemrect = wx.Rect(0, item.GetY() + off_h, total_w - 1, total_h - off_h)
			
			if item == self._dragItem:
				dc.SetBrush(self._hilightBrush)
				if wx.Platform == "__WXMAC__":
					dc.SetPen((item == self._dragItem) and [wx.BLACK_PEN] or [wx.TRANSPARENT_PEN])[0]
				
				dc.SetTextForeground(colTextHilight)
			
			elif item.IsSelected():
				
				# wnd = item.GetWindow(self._main_column)
				# wndx = 0
				# if wnd:
				# 	wndx, wndy = item.GetWindowSize(self._main_column)
				
				itemrect = wx.Rect(0, item.GetY() + off_h, total_w - 1, total_h - off_h)
				
				if self._usegradients:
					if self._gradientstyle == 0:  # Horizontal
						self.DrawHorizontalGradient(dc, itemrect, self._hasFocus)
					else:  # Vertical
						self.DrawVerticalGradient(dc, itemrect, self._hasFocus)
				elif self._vistaselection:
					self.DrawVistaRectangle(dc, itemrect, self._hasFocus)
				else:
					if wx.Platform in ["__WXGTK2__", "__WXMAC__"]:
						flags = wx.CONTROL_SELECTED
						if self._hasFocus: flags = flags | wx.CONTROL_FOCUSED
						wx.RendererNative.Get().DrawItemSelectionRect(self._owner, dc, itemrect, flags)
					else:
						dc.SetBrush((self._hasFocus and [self._hilightBrush] or [self._hilightUnfocusedBrush])[0])
						dc.SetPen((self._hasFocus and [self._borderPen] or [wx.TRANSPARENT_PEN])[0])
						dc.DrawRectangle(itemrect)
				
				dc.SetTextForeground(colTextHilight)
			
			# On GTK+ 2, drawing a 'normal' background is wrong for themes that
			# don't allow backgrounds to be customized. Not drawing the background,
			# except for custom item backgrounds, works for both kinds of theme.
			elif drawItemBackground:
				
				pass
			# We have to colour the item background for each column separately
			# So it is better to move this functionality in the subsequent for loop.
			
			else:
				dc.SetTextForeground(colText)
		
		else:
			
			dc.SetTextForeground(colText)
		
		# text_extraH = (total_h > text_h and [(total_h - text_h) // 2] or [0])[0]
		img_extraH = (total_h > self._imgHeight and [(total_h - self._imgHeight) // 2] or [0])[0]
		x_colstart = 0
		
		for i in range(self.GetColumnCount()):
			if not self._owner.GetHeaderWindow().IsColumnShown(i):
				continue
			
			col_w = self._owner.GetHeaderWindow().GetColumnWidth(i)
			dc.SetClippingRegion(x_colstart, item.GetY(), col_w, total_h)  # only within column
			
			image = _NO_IMAGE
			x = image_w = wcheck = hcheck = 0
			
			if i == self.GetMainColumn():
				x = item.GetX() + _MARGIN
				if self.HasButtons():
					x += (self._btnWidth - self._btnWidth2) + _LINEATROOT
				else:
					x -= self._indent // 2
				
				if self._imageListNormal:
					image = item.GetCurrentImage(i)
				
				if item.GetType() != 0 and self._imageListCheck:
					checkimage = item.GetCurrentCheckedImage()
					wcheck, hcheck = self._imageListCheck.GetSize(item.GetType())
				else:
					wcheck, hcheck = 0, 0
			
			else:
				x = x_colstart + _MARGIN
				image = item.GetImage(column=i)
			
			if image != _NO_IMAGE:
				image_w = self._imgWidth + _MARGIN
			
			# honor text alignment
			text = item.GetText(i)
			
			text_w, dummy, dummy = dc.GetFullMultiLineTextExtent(text)
			
			custom_alignment = self.custom_alignments[level][i]
			
			if custom_alignment is None:
				alignment = self._owner.GetHeaderWindow().GetColumn(i).GetAlignment()
			else:
				alignment = custom_alignment
			
			if alignment == wx.ALIGN_RIGHT:
				w = col_w - (image_w + wcheck + text_w + off_w + _MARGIN + 1)
				x += (w > 0 and [w] or [0])[0]
			
			elif alignment == wx.ALIGN_CENTER:
				w = (col_w - (image_w + wcheck + text_w + off_w + _MARGIN)) // 2
				x += (w > 0 and [w] or [0])[0]
			else:
				if image_w == 0 and wcheck:
					x += 2 * _MARGIN
			
			text_x = x + image_w + wcheck + 1
			
			if i == self.GetMainColumn():
				item.SetTextX(text_x)
			
			if not self.HasAGWFlag(wx.TR_FULL_ROW_HIGHLIGHT):
				dc.SetBrush((self._hasFocus and [self._hilightBrush] or [self._hilightUnfocusedBrush])[0])
				dc.SetPen((self._hasFocus and [self._borderPen] or [wx.TRANSPARENT_PEN])[0])
				if i == self.GetMainColumn():
					if item == self._dragItem:
						if wx.Platform == "__WXMAC__":  # don't draw rect outline if we already have the background colour
							dc.SetPen((item == self._dragItem and [wx.BLACK_PEN] or [wx.TRANSPARENT_PEN])[0])
						
						dc.SetTextForeground(colTextHilight)
					
					elif item.IsSelected():
						
						itemrect = wx.Rect(
								text_x - 2,
								item.GetY() + off_h,
								text_w + 2 * _MARGIN,
								total_h - off_h
								)
						
						if self._usegradients:
							if self._gradientstyle == 0:  # Horizontal
								self.DrawHorizontalGradient(dc, itemrect, self._hasFocus)
							else:  # Vertical
								self.DrawVerticalGradient(dc, itemrect, self._hasFocus)
						elif self._vistaselection:
							self.DrawVistaRectangle(dc, itemrect, self._hasFocus)
						else:
							if wx.Platform in ["__WXGTK2__", "__WXMAC__"]:
								flags = wx.CONTROL_SELECTED
								if self._hasFocus:
									flags = flags | wx.CONTROL_FOCUSED
								wx.RendererNative.Get().DrawItemSelectionRect(self._owner, dc, itemrect, flags)
							else:
								dc.DrawRectangle(itemrect)
						
						dc.SetTextForeground(colTextHilight)
					
					elif item == self._current:
						dc.SetPen((self._hasFocus and [wx.BLACK_PEN] or [wx.TRANSPARENT_PEN])[0])
					
					# On GTK+ 2, drawing a 'normal' background is wrong for themes that
					# don't allow backgrounds to be customized. Not drawing the background,
					# except for custom item backgrounds, works for both kinds of theme.
					elif drawItemBackground:
						
						if self.HasAGWFlag(hypertreelist.TR_FILL_WHOLE_COLUMN_BACKGROUND):
							itemrect = wx.Rect(
									text_x - 2,
									item.GetY() + off_h,
									col_w - 2 * _MARGIN,
									total_h - off_h,
									)
						else:
							itemrect = wx.Rect(
									text_x - 2,
									item.GetY() + off_h,
									text_w + 2 * _MARGIN,
									total_h - off_h,
									)
							
						dc.SetBrush(wx.Brush(colBg))
						dc.SetPen(wx.TRANSPARENT_PEN)
						dc.DrawRectangle(itemrect)
					
					else:
						dc.SetTextForeground(colText)
				
				else:
					
					if self.HasAGWFlag(hypertreelist.TR_FILL_WHOLE_COLUMN_BACKGROUND):
						itemrect = wx.Rect(
								text_x - 2,
								item.GetY() + off_h,
								col_w - 2 * _MARGIN,
								total_h - off_h,
								)
					else:
						itemrect = wx.Rect(
								text_x - 2,
								item.GetY() + off_h,
								text_w + 2 * _MARGIN,
								total_h - off_h,
								)
						
					colBgX = item.GetBackgroundColour(i)
					
					if colBgX != None and i != 0:
						dc.SetBrush(wx.Brush(colBgX, wx.SOLID))
						dc.SetPen(wx.TRANSPARENT_PEN)
						dc.DrawRectangle(itemrect)
					
					dc.SetTextForeground(colText)
			
			else:
				
				if not item.IsSelected():
					
					if self.HasAGWFlag(hypertreelist.TR_FILL_WHOLE_COLUMN_BACKGROUND):
						itemrect = wx.Rect(
								text_x - 2,
								item.GetY() + off_h,
								col_w - 2 * _MARGIN,
								total_h - off_h,
								)
					else:
						itemrect = wx.Rect(
								text_x - 2,
								item.GetY() + off_h,
								text_w + 2 * _MARGIN,
								total_h - off_h,
								)
						
					colBgX = item.GetBackgroundColour(i)
					
					if colBgX is not None:
						dc.SetBrush(wx.Brush(colBgX, wx.SOLID))
						dc.SetPen(wx.TRANSPARENT_PEN)
						dc.DrawRectangle(itemrect)
			
			if self.HasAGWFlag(hypertreelist.TR_COLUMN_LINES):  # vertical lines between columns
				pen = wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT), 1, wx.PENSTYLE_SOLID)
				dc.SetPen((self.GetBackgroundColour() == wx.WHITE and [pen] or [wx.WHITE_PEN])[0])
				dc.DrawLine(x_colstart + col_w - 1, item.GetY(), x_colstart + col_w - 1, item.GetY() + total_h)
			
			dc.SetBackgroundMode(wx.TRANSPARENT)
			
			if image != _NO_IMAGE:
				y = item.GetY() + img_extraH
				if wcheck:
					x += wcheck
				
				if item.IsEnabled():
					imglist = self._imageListNormal
				else:
					imglist = self._grayedImageList
				
				imglist.Draw(image, dc, x, y, wx.IMAGELIST_DRAW_TRANSPARENT)
			
			if wcheck:
				if item.IsEnabled():
					imglist = self._imageListCheck
				else:
					imglist = self._grayedCheckList
				
				if self.HasButtons():  # should the item show a button?
					btnWidth = self._btnWidth
				else:
					btnWidth = -self._btnWidth
				
				imglist.Draw(
						checkimage,
						dc,
						item.GetX() + btnWidth + _MARGIN,
						item.GetY() + ((total_h > hcheck) and [(total_h - hcheck) // 2] or [0])[0] + 1,
						wx.IMAGELIST_DRAW_TRANSPARENT,
						)
			
			text_w, text_h, dummy = dc.GetFullMultiLineTextExtent(text)
			text_extraH = (total_h > text_h and [(total_h - text_h) // 2] or [0])[0]
			text_y = item.GetY() + text_extraH
			textrect = wx.Rect(text_x, text_y, text_w, text_h)
			
			if self.HasAGWFlag(hypertreelist.TR_ELLIPSIZE_LONG_ITEMS):
				if i == self.GetMainColumn():
					maxsize = col_w - text_x - _MARGIN
				else:
					maxsize = col_w - (wcheck + image_w + _MARGIN)
				
				text = hypertreelist.ChopText(dc, text, maxsize)
			
			if not item.IsEnabled():
				foreground = dc.GetTextForeground()
				dc.SetTextForeground(self._disabledColour)
				_paintText(text, textrect, alignment)
				dc.SetTextForeground(foreground)
			else:
				if wx.Platform == "__WXMAC__" and item.IsSelected() and self._hasFocus:
					dc.SetTextForeground(wx.WHITE)
				_paintText(text, textrect, alignment)
			
			wnd = item.GetWindow(i)
			if wnd:
				if text_w == 0:
					wndx = text_x
				else:
					wndx = text_x + text_w + 2 * _MARGIN
				xa, ya = self.CalcScrolledPosition(0, item.GetY())
				wndx += xa
				if item.GetHeight() > item.GetWindowSize(i)[1]:
					ya += (item.GetHeight() - item.GetWindowSize(i)[1]) // 2
				
				if wnd.GetPosition() != (wndx, ya):
					wnd.Move(wndx, ya, flags=wx.SIZE_ALLOW_MINUS_ONE)
				# Force window visible after any position changes were made.
				if not wnd.IsShown():
					wnd.Show()
			
			x_colstart += col_w
			dc.DestroyClippingRegion()
		
		# restore normal font
		dc.SetFont(self._normalFont)
	
	# Now y stands for the top of the item, whereas it used to stand for middle !
	def PaintLevel(self, item, dc, level, y, x_maincol):
		"""
		Paint a level in the hierarchy of :class:`TreeListMainWindow`.

		:param item: an instance of :class:`TreeListItem`;
		:type: item: :class:`TreeListItem`
		:param dc: an instance of :class:`wx.DC`;
		:type dc: :class:`wx.DC`
		:param level: the item level in the tree hierarchy;
		:type level:
		:param y: the current vertical position in the :class:`ScrolledWindow`;
		:type y: int
		:param x_maincol: the horizontal position of the main column.
		:type x_maincol: int
		"""
		
		if item.IsHidden():
			return y, x_maincol
		
		# Handle hide root (only level 0)
		if self.HasAGWFlag(wx.TR_HIDE_ROOT) and level == 0:
			for child in item.GetChildren():
				y, x_maincol = self.PaintLevel(child, dc, 1, y, x_maincol)
			
			# end after expanding root
			return y, x_maincol
		
		# calculate position of vertical lines
		x = x_maincol + _MARGIN  # start of column
		
		if self.HasAGWFlag(wx.TR_LINES_AT_ROOT):
			x += _LINEATROOT  # space for lines at root
		
		if self.HasButtons():
			x += (self._btnWidth - self._btnWidth2)  # half button space
		else:
			x += (self._indent - self._indent // 2)
		
		if self.HasAGWFlag(wx.TR_HIDE_ROOT):
			x += self._indent * (level - 1)  # indent but not level 1
		else:
			x += self._indent * level  # indent according to level
		
		# set position of vertical line
		item.SetX(x)
		item.SetY(y)
		
		h = self.GetLineHeight(item)
		y_top = y
		y_mid = y_top + (h // 2)
		y += h
		
		exposed_x = dc.LogicalToDeviceX(0)
		exposed_y = dc.LogicalToDeviceY(y_top)
		
		# horizontal lines between rows?
		draw_row_lines = self.HasAGWFlag(hypertreelist.TR_ROW_LINES)
		
		if self.IsExposed(exposed_x, exposed_y, _MAX_WIDTH, h + int(draw_row_lines)):
			# fill background below twist buttons
			if self.HasAGWFlag(hypertreelist.TR_FILL_WHOLE_COLUMN_BACKGROUND):
				attr = item.GetAttributes()
				
				if attr and attr.HasBackgroundColour():
					width = self._owner.GetEventHandler().GetColumn(self._main_column).GetWidth()
					colBg = attr.GetBackgroundColour()
					itemrect = wx.Rect(x_maincol, y - h - 1, width, h + 1)
					
					dc.SetBrush(wx.Brush(colBg, wx.SOLID))
					dc.SetPen(wx.TRANSPARENT_PEN)
					dc.DrawRectangle(itemrect)
			
			# draw item
			self.PaintItem(item, dc, level)
			
			# restore DC objects
			dc.SetBrush(wx.WHITE_BRUSH)
			dc.SetPen(self._dottedPen)
			
			# clip to the column width
			clip_width = self._owner.GetHeaderWindow().GetColumn(self._main_column).GetWidth()
			# clipper = wx.DCClipper(dc, x_maincol, y_top, clip_width, 10000)
			
			if not self.HasAGWFlag(wx.TR_NO_LINES):  # connection lines
				
				# draw the horizontal line here
				dc.SetPen(self._dottedPen)
				x2 = x - self._indent
				if x2 < (x_maincol + _MARGIN):
					x2 = x_maincol + _MARGIN
				x3 = x + (self._btnWidth - self._btnWidth2)
				if self.HasButtons():
					if item.HasPlus():
						dc.DrawLine(x2, y_mid, x - self._btnWidth2, y_mid)
						dc.DrawLine(x3, y_mid, x3 + _LINEATROOT, y_mid)
					else:
						dc.DrawLine(x2, y_mid, x3 + _LINEATROOT, y_mid)
				else:
					dc.DrawLine(x2, y_mid, x - self._indent // 2, y_mid)
			
			if item.HasPlus() and self.HasButtons():  # should the item show a button?
				
				if self._imageListButtons:
					
					# draw the image button here
					image = wx.TreeItemIcon_Normal
					if item.IsExpanded():
						image = wx.TreeItemIcon_Expanded
					if item.IsSelected():
						image += wx.TreeItemIcon_Selected - wx.TreeItemIcon_Normal
					xx = x - self._btnWidth2 + _MARGIN
					yy = y_mid - self._btnHeight2
					dc.SetClippingRegion(xx, yy, self._btnWidth, self._btnHeight)
					self._imageListButtons.Draw(image, dc, xx, yy, wx.IMAGELIST_DRAW_TRANSPARENT)
					dc.DestroyClippingRegion()
				
				elif self.HasAGWFlag(wx.TR_TWIST_BUTTONS):
					
					# draw the twisty button here
					dc.SetPen(wx.BLACK_PEN)
					dc.SetBrush(self._hilightBrush)
					button = [wx.Point() for j in range(3)]
					if item.IsExpanded():
						button[0].x = x - (self._btnWidth2 + 1)
						button[0].y = y_mid - (self._btnHeight // 3)
						button[1].x = x + (self._btnWidth2 + 1)
						button[1].y = button[0].y
						button[2].x = x
						button[2].y = button[0].y + (self._btnHeight2 + 1)
					else:
						button[0].x = x - (self._btnWidth // 3)
						button[0].y = y_mid - (self._btnHeight2 + 1)
						button[1].x = button[0].x
						button[1].y = y_mid + (self._btnHeight2 + 1)
						button[2].x = button[0].x + (self._btnWidth2 + 1)
						button[2].y = y_mid
					
					dc.SetClippingRegion(x_maincol + _MARGIN, y_top, clip_width, h)
					dc.DrawPolygon(button)
					dc.DestroyClippingRegion()
				
				else:  # if (HasAGWFlag(wxTR_HAS_BUTTONS))
					
					rect = wx.Rect(x - self._btnWidth2, y_mid - self._btnHeight2, self._btnWidth, self._btnHeight)
					flag = (item.IsExpanded() and [wx.CONTROL_EXPANDED] or [0])[0]
					wx.RendererNative.GetDefault().DrawTreeItemButton(self, dc, rect, flag)
			
			if draw_row_lines:
				total_width = self._owner.GetHeaderWindow().GetWidth()
				# if the background colour is white, choose a
				# contrasting colour for the lines
				pen = wx.Pen(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT), 1, wx.PENSTYLE_SOLID)
				dc.SetPen((self.GetBackgroundColour() == wx.WHITE and [pen] or [wx.WHITE_PEN])[0])
				dc.DrawLine(0, y_top, total_width, y_top)
				dc.DrawLine(0, y_top + h, total_width, y_top + h)
		
		# restore DC objects
		dc.SetBrush(wx.WHITE_BRUSH)
		dc.SetPen(self._dottedPen)
		dc.SetTextForeground(wx.BLACK)
		
		if item.IsExpanded():
			
			# process lower levels
			if self._imgWidth > 0:
				oldY = y_mid + self._imgHeight2
			else:
				oldY = y_mid + h // 2
			
			children = item.GetChildren()
			for child in children:
				y, x_maincol = self.PaintLevel(child, dc, level + 1, y, x_maincol)
			
			if not self.HasAGWFlag(wx.TR_NO_LINES) and children:
				last_child = children[-1]
				Y1 = last_child.GetY() + last_child.GetHeight() / 2
				dc.DrawLine(x, oldY, x, Y1)
		
		return y, x_maincol


class CustomHyperTreeList(hypertreelist.HyperTreeList):
	def __init__(
			self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
			style=0, agwStyle=wx.TR_DEFAULT_STYLE, validator=wx.DefaultValidator,
			name="HyperTreeList",
			):
		"""
		Default class constructor.

		:param `parent`: parent window. Must not be ``None``;
		:param `id`: window identifier. A value of -1 indicates a default value;
		:param `pos`: the control position. A value of (-1, -1) indicates a default position, chosen by either the windowing system or wxPython, depending on platform;
		:param `size`: the control size. A value of (-1, -1) indicates a default size, chosen by either the windowing system or wxPython, depending on platform;
		:param `style`: the underlying :class:`wx.Control` style;
		:param `agwStyle`: the AGW-specific :class:`HyperTreeList` window style. This can be a combination of the following bits:

			============================== =========== ==================================================
			Window Styles                  Hex Value   Description
			============================== =========== ==================================================
			``TR_NO_BUTTONS``                      0x0 For convenience to document that no buttons are to be drawn.
			``TR_SINGLE``                          0x0 For convenience to document that only one item may be selected at a time. Selecting another item causes the current selection, if any, to be deselected. This is the default.
			``TR_HAS_BUTTONS``                     0x1 Use this style to show + and - buttons to the left of parent items.
			``TR_NO_LINES``                        0x4 Use this style to hide vertical level connectors.
			``TR_LINES_AT_ROOT``                   0x8 Use this style to show lines between root nodes. Only applicable if ``TR_HIDE_ROOT`` is set and ``TR_NO_LINES`` is not set.
			``TR_DEFAULT_STYLE``                   0x9 The set of flags that are closest to the defaults for the native control for a particular toolkit.
			``TR_TWIST_BUTTONS``                  0x10 Use old Mac-twist style buttons.
			``TR_MULTIPLE``                       0x20 Use this style to allow a range of items to be selected. If a second range is selected, the current range, if any, is deselected.
			``TR_EXTENDED``                       0x40 Use this style to allow disjoint items to be selected. (Only partially implemented; may not work in all cases).
			``TR_HAS_VARIABLE_ROW_HEIGHT``        0x80 Use this style to cause row heights to be just big enough to fit the content. If not set, all rows use the largest row height. The default is that this flag is unset.
			``TR_EDIT_LABELS``                   0x200 Use this style if you wish the user to be able to edit labels in the tree control.
			``TR_ROW_LINES``                     0x400 Use this style to draw a contrasting border between displayed rows.
			``TR_HIDE_ROOT``                     0x800 Use this style to suppress the display of the root node, effectively causing the first-level nodes to appear as a series of root nodes.
			``TR_COLUMN_LINES``                 0x1000 Use this style to draw a contrasting border between displayed columns.
			``TR_FULL_ROW_HIGHLIGHT``           0x2000 Use this style to have the background colour and the selection highlight extend  over the entire horizontal row of the tree control window.
			``TR_AUTO_CHECK_CHILD``             0x4000 Only meaningful for checkbox-type items: when a parent item is checked/unchecked its children are checked/unchecked as well.
			``TR_AUTO_TOGGLE_CHILD``            0x8000 Only meaningful for checkbox-type items: when a parent item is checked/unchecked its children are toggled accordingly.
			``TR_AUTO_CHECK_PARENT``           0x10000 Only meaningful for checkbox-type items: when a child item is checked/unchecked its parent item is checked/unchecked as well.
			``TR_ALIGN_WINDOWS``               0x20000 Flag used to align windows (in items with windows) at the same horizontal position.
			``TR_NO_HEADER``                   0x40000 Use this style to hide the columns header.
			``TR_ELLIPSIZE_LONG_ITEMS``        0x80000 Flag used to ellipsize long items when the horizontal space for :class:`~wx.lib.agw.customtreectrl.CustomTreeCtrl` is low.
			``TR_VIRTUAL``                    0x100000 :class:`HyperTreeList` will have virtual behaviour.
			============================== =========== ==================================================

		:param `validator`: window validator;
		:param `name`: window name.
		"""
		
		wx.Control.__init__(self, parent, id, pos, size, style, validator, name)
		
		self._header_win = None
		self._main_win = None
		self._headerHeight = 0
		self._attr_set = False
		
		main_style = style & ~(
				wx.SIMPLE_BORDER | wx.SUNKEN_BORDER | wx.DOUBLE_BORDER | wx.RAISED_BORDER | wx.STATIC_BORDER
				)
		
		self._agwStyle = agwStyle
		
		self._main_win = CustomTreeListMainWindow(self, -1, wx.Point(0, 0), size, main_style, agwStyle, validator)
		self._main_win._buffered = False
		
		self._header_win = hypertreelist.TreeListHeaderWindow(
				self,
				-1,
				self._main_win,
				wx.Point(0, 0),
				wx.DefaultSize,
				wx.TAB_TRAVERSAL,
				)
		
		self._header_win._buffered = False
		
		self.CalculateAndSetHeaderHeight()
		self.Bind(wx.EVT_SIZE, self.OnSize)
		
		self.SetBuffered(hypertreelist.IsBufferingSupported())
		self._main_win.SetAGWWindowStyleFlag(agwStyle)
	
	@property
	def custom_alignments(self):
		return self._main_win.custom_alignments
	
	@custom_alignments.setter
	def custom_alignments(self, value):
		self._main_win.custom_alignments = value
	
	def OnSize(self, event):
		# print("Size Event")
		# print(self.GetSize())
		# print(self._main_win.GetSize())
		hypertreelist.HyperTreeList.OnSize(self, event)
	
	def GetItem(self, item_idx):
		return self.GetAllItems()[item_idx]
	
	def GetAllItems(self):
		return self.GetMainWindow()._anchor.GetChildren()
