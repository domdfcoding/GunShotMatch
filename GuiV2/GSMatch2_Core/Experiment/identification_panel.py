#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  identification_panel.py
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#  Based on the TreeListCtrl demo from wxPython.
#  Licenced under the wxWindows licence
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

# this package
from GuiV2.GSMatch2_Core.Experiment.SortFilterDialog import (
	SinglePeakSortFilterDialog, SortFilterDialog,
	Sort_Area, Sort_CAS, Sort_Hit, Sort_MF, Sort_Name, Sort_RMF, Sort_RT,
	)
from GuiV2.icons import get_icon
from GuiV2.GSMatch2_Core import Experiment


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
class IdentificationPanel(wx.Panel):
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
		
		wx.Panel.__init__(self, parent, id=id, pos=pos, size=size, style=style, name=name)
		
		self.peak_list = peak_list[:]
		
		self._create_buttons()
		
		# Create HyperTreeCtrl
		self.tree = hypertreelist.HyperTreeList(
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
		self.tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnActivate)
		self.tree.GetHeaderWindow().Bind(wx.EVT_LEFT_DOWN, self.OnHeaderClicked)
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
		self.tree.AddColumn("", width=70)
		self.tree.AddColumn("", width=70)
		self.tree.SetMainColumn(0)  # the one with the tree in it...
		
		# Column Alignment
		# TODO: Make multiline text in column header correctly align right
		# self.tree.SetColumnAlignment(2, wx.ALIGN_RIGHT)
		self.tree.SetColumnAlignment(3, wx.ALIGN_RIGHT)
		self.tree.SetColumnAlignment(4, wx.ALIGN_RIGHT)
		
		self._update_header_labels()
	
	def default_filter_settings(self):
		self.min_rt = min([peak.rt for peak in self.peak_list])
		self.max_rt = max([peak.rt for peak in self.peak_list])
		self.min_area = min([peak.area for peak in self.peak_list])
		self.max_area = max([peak.area for peak in self.peak_list])
		
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
		sizer.Add(self.btn_sizer, 0, wx.EXPAND, 0)
		sizer.Add(self.tree, 0, wx.EXPAND | wx.TOP, 3)
		
		self.SetSizer(sizer)
		self.Fit()
		self.Layout()
	
	def expand_all(self, event=None):
		self.tree.ExpandAll()
	
	def OnActivate(self, evt):
		# TODO: Something like show the spectrum or a comparison between the peak and the reference?
		#  In either case need to add explanatory text to GUI
		
		print(f'OnActivate: {self.tree.GetItemText(evt.GetItem())}')
		print(f'OnActivate: {self.tree.GetItemData(evt.GetItem())}')
		print(f'OnActivate: {self.tree.IsVisible(evt.GetItem())}')
	
	def OnSize(self, evt):
		self.tree.SetSize(self.GetSize())
	
	def OnHeaderClicked(self, event):
		print(f"Column {self.tree.GetHeaderWindow().XToCol(event.GetPosition().x)} clicked!")
		event.Skip()
	
	def OnRightUp(self, event):
		pos = event.GetPosition()
		item, flags, col = self.tree.HitTest(pos)
		if item:
			print(f'Flags: {flags}, Col:{col}, Text: {self.tree.GetItemText(item, col)}')
		self.tree.CollapseAllChildren(item)
		
		if not item:
			event.Skip()
			return
	
	def _populate_tree(self):
		"""
		When sorting, if the column only contains data for hits,
		the hits will be sorted under each peak and not globally
		"""
		
		# Clear the tree
		self.tree.DeleteChildren(self.root)
		
		self._update_header_labels()
		
		# Sort peaks
		if self.peak_sort == Sort_RT:
			self.peak_list.sort(key=lambda peak: peak.rt, reverse=self.peak_descending)
		elif self.peak_sort == Sort_Area:
			self.peak_list.sort(key=lambda peak: peak.area, reverse=self.peak_descending)
		
		# Populate Tree
		for peak in self.peak_list:
			# Filter peaks
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
			
			peak_item = self.tree.AppendItem(self.root, str(rounders(peak.rt / 60, "0.000000")))
			self.tree.SetItemText(peak_item, f"{rounders(peak.area, '0.000000'):,}", 1)
			self.tree.SetItemText(peak_item, str(peak.peak_number), 2)
			self.tree.SetItemImage(peak_item, 0, which=wx.TreeItemIcon_Normal)
			# self.tree.SetItemImage(peak_item, 1, which=wx.TreeItemIcon_Expanded)
			self.tree.SetItemData(peak_item, peak)
			
			hit_list = list(enumerate(peak.hits))
			
			# Limit to n_hits
			if self.n_hits:
				hit_list = hit_list[:self.n_hits]
			
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
			
			for hit_number, hit in hit_list:
				
				# Filter hits
				if not self.min_mf <= hit.match_factor:
					continue
				if not self.min_rmf <= hit.reverse_match_factor:
					continue
				
				hit_item = self.tree.AppendItem(peak_item, f'{hit_number + 1}')
				self.tree.SetItemText(hit_item, f"\t{hit.name}", 1)
				self.tree.SetItemText(hit_item, f"{hit.cas}  ", 2)
				self.tree.SetItemText(hit_item, f"{hit.match_factor}  ", 3)
				self.tree.SetItemText(hit_item, f"{hit.reverse_match_factor}  ", 4)
				self.tree.SetItemData(hit_item, hit)
				self.tree.SetItemImage(hit_item, 2)
		
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


class SinglePeakIdentificationPanel(IdentificationPanel):
	def __init__(
			self, parent, experiment_list, id=wx.ID_ANY, pos=wx.DefaultPosition,
			size=wx.DefaultSize, style=0, name="IdentificationPanel"):
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
	
	def _populate_tree(self):
		"""
		When sorting, if the column only contains data for hits,
		the hits will be sorted under each peak and not globally
		"""
		
		# Clear the tree
		self.tree.DeleteChildren(self.root)
		
		self._update_header_labels()
		
		# Sort peaks
		# No sorting in this subclass
		
		# Populate Tree
		for peak, experiment_name in zip(self.peak_list, self.expr_names):
			# Note: No peak filtering support for the subclass
			
			peak_item = self.tree.AppendItem(self.root, experiment_name)
			self.tree.SetItemText(peak_item, f"{rounders(peak.area, '0.000000'):,}", 1)
			self.tree.SetItemText(peak_item, f"{rounders(peak.rt / 60, '0.000000')}", 2)
			self.tree.SetItemImage(peak_item, 0, which=wx.TreeItemIcon_Normal)
			# self.tree.SetItemImage(peak_item, 1, which=wx.TreeItemIcon_Expanded)
			self.tree.SetItemData(peak_item, peak)
			
			hit_list = list(enumerate(peak.hits))
			
			# Limit to n_hits
			if self.n_hits:
				hit_list = hit_list[:self.n_hits]
			
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
			
			for hit_number, hit in hit_list:
				
				# Filter hits
				if not self.min_mf <= hit.match_factor:
					continue
				if not self.min_rmf <= hit.reverse_match_factor:
					continue
				
				hit_item = self.tree.AppendItem(peak_item, f'{hit_number + 1}')
				self.tree.SetItemText(hit_item, f"\t{hit.name}", 1)
				self.tree.SetItemText(hit_item, f"{hit.cas}  ", 2)
				self.tree.SetItemText(hit_item, f"{hit.match_factor}  ", 3)
				self.tree.SetItemText(hit_item, f"{hit.reverse_match_factor}  ", 4)
				self.tree.SetItemData(hit_item, hit)
				self.tree.SetItemImage(hit_item, 2)
		
		self.tree.ExpandAll()

	def previous_peak(self, event):
		self.switch_peak(-1)
	
	def set_peak(self, new_peak):
		if new_peak:
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
		area_sort_arrow = " "
		rt_sort_arrow = " "
		cas_sort_arrow = " "
		name_sort_arrow = " "
		mf_sort_arrow = " "
		rmf_sort_arrow = " "
		hit_sort_arrow = " "
		
		# Column Headers
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

