#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  CalibreSearchPanel.py
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

# 3rd party
import wx
from sqlalchemy.orm import sessionmaker
from wx.lib.mixins.treemixin import ExpansionState

# this package
from GuiV2 import CalibreSearch
from GuiV2.CalibreSearch.calibre_db import engine
from GuiV2.CalibreSearch.calibre_db.model import CalibreModel

# TODO: Advanced search window


# SQLAlchemy database session
Session = sessionmaker(bind=engine)
session = Session()


class CalibreTree(wx.TreeCtrl, ExpansionState):
	def __init__(self, parent):
		wx.TreeCtrl.__init__(
				self, parent,
				style=wx.TR_DEFAULT_STYLE | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_HIDE_ROOT
				)
		
		self.SetInitialSize((200, 80))
	
	def GetItemIdentity(self, item):
		return self.GetItemData(item)


class CalibreSearchPanel(wx.Panel):
	def __init__(
			self, parent, id=wx.ID_ANY,
			pos=wx.DefaultPosition,
			style=0, name="CalibreSearchPanel", dialog=False
			):
		"""
		:param parent: The parent window.
		:type parent: wx.Window
		:param id: An identifier for the panel. wx.ID_ANY is taken to mean a default.
		:type id: wx.WindowID, optional
		:param pos: The panel position. The value wx.DefaultPosition indicates a default position,
		chosen by either the windowing system or wxWidgets, depending on platform.
		:type pos: wx.Point, optional
		:param style: The window style. See wx.Panel.
		:type style: int, optional
		:param name: Window name.
		:type name: str, optional
		:param dialog:
		:type dialog:
		"""
		
		self.parent = parent
		
		wx.Panel.__init__(
				self, parent, id=id, pos=pos,
				style=style | wx.TAB_TRAVERSAL, name=name
				)
		
		# Left panel with TreeCtrl and SearchCtrl
		self.leftPanel = wx.Panel(self, style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN)

		self.treeMap = {}
		self.searchItems = {}
		self.tree = CalibreTree(self.leftPanel)
		self.root = self.tree.AddRoot("")

		self.filter = wx.SearchCtrl(self.leftPanel, style=wx.TE_PROCESS_ENTER)
		searchMenu = wx.Menu()
		item = searchMenu.AppendRadioItem(-1, "Calibre Name")
		self.Bind(wx.EVT_MENU, self.on_search_menu, item)
		item = searchMenu.AppendRadioItem(-1, "Calibre Properties")
		self.Bind(wx.EVT_MENU, self.on_search_menu, item)
		self.filter.SetMenu(searchMenu)
		self._filter_menu_opts = searchMenu.GetMenuItems()
		
		# Right panel with CalibreInfoPanel and New Calibre button
		self.rightPanel = wx.Panel(self, style=wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN)
		self.info_panel = CalibreSearch.InfoPanel(self.rightPanel, wx.ID_ANY, style=wx.CLIP_CHILDREN)
		
		if dialog:
			size = (650, 620)
			self.buttons = CalibreSearch.ButtonPanel(self.rightPanel)
		else:
			size = (660, 575)
			self.buttons = CalibreSearch.NewCalibreButtonPanel(self.rightPanel)
		
		self.SetSize(size)
		self.SetMinSize(size)
		self.SetMaxSize(size)
		
		self.filter.ShowCancelButton(True)
		self.info_panel.SetEditable(False)
		
		self._do_layout()
		self._bind_events()
		self._compile_calibre_list()
		
		self.tree.ExpandAll()
		self.recreate_tree()
	
	def _bind_events(self):
		self.filter.Bind(wx.EVT_TEXT, self.recreate_tree)
		self.filter.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.on_filter_clear)
		self.filter.Bind(wx.EVT_TEXT_ENTER, self.recreate_tree)
		self.filter.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.recreate_tree)
		
		self.tree.Bind(wx.EVT_TREE_ITEM_EXPANDED, self.on_item_expanded)
		self.tree.Bind(wx.EVT_TREE_ITEM_COLLAPSED, self.on_item_collapsed)
		self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_sel_changed)
		# self.tree.Bind(wx.EVT_LEFT_DOWN, self.on_tree_left_down)
		
		self.Bind(wx.EVT_ACTIVATE, self.on_activate)
		self.Bind(wx.EVT_CLOSE, self.on_close)
		
		self.Bind(wx.EVT_BUTTON, self.on_new_calibre, id=CalibreSearch.ID_NEW_CALIBRE)
		
	def _do_layout(self):
		if 'gtk3' in wx.PlatformInfo:
			# Something is wrong with the bestsize of the SearchCtrl, so for now
			# let's set it based on the size of a TextCtrl.
			txt = wx.TextCtrl(self.leftPanel)
			bs = txt.GetBestSize()
			txt.DestroyLater()
			self.filter.SetMinSize((-1, bs.height + 4))
	
		# Left sizer
		leftBox = wx.BoxSizer(wx.VERTICAL)
		leftBox.Add(self.tree, 1, wx.EXPAND | wx.RIGHT, 10)
		leftBox.Add(wx.StaticText(self.leftPanel, label="Filter Calibres:"), 0, wx.TOP | wx.LEFT, 5)
		leftBox.Add(self.filter, 0, wx.ALL | wx.EXPAND, 10)
		if 'wxMac' in wx.PlatformInfo:
			leftBox.Add((5, 5))  # Make sure there is room for the focus ring
		self.leftPanel.SetSizer(leftBox)
		
		# Right sizer
		self.rightBox = wx.BoxSizer(wx.VERTICAL)
		self.rightBox.Add(self.info_panel, 1, wx.RIGHT | wx.ALIGN_RIGHT, 10)
		
		bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
		bottom_sizer.AddStretchSpacer(6)
		bottom_sizer.Add(self.buttons, 0, wx.ALL | wx.ALIGN_BOTTOM, 10)
		self.rightBox.Add(bottom_sizer, 1, wx.EXPAND, 0)
	
		self.rightPanel.SetSizerAndFit(self.rightBox)
		
		main_sizer = wx.BoxSizer(wx.HORIZONTAL)
		main_sizer.Add(self.leftPanel, 3, wx.EXPAND, 0)
		main_sizer.Add(self.rightPanel, 5, wx.EXPAND, 0)
		self.SetSizerAndFit(main_sizer)
	
	def _compile_calibre_list(self):
		"""
		Put together dictionary containing names of calibres and the corresponding database IDs
		"""
		
		self.calibre_list = []
		self.calibre_dict = {}
		
		records = session.query(CalibreModel).all()
		
		for record in records:
			
			if record.type not in {x[0] for x in self.calibre_list}:
				self.calibre_list.append((record.type, []))
			
			for category in self.calibre_list:
				if category[0] == record.type:
					category[1].append(record.name)
					
					self.calibre_dict[record.name] = record
					
					for name in record.other_names:
						self.calibre_dict[name] = record
						category[1].append(name)
					
					break
		
		for category in self.calibre_list:
			category[1].sort()
			
	def on_new_calibre(self, _):
		with CalibreSearch.NewCalibreDialog(self) as dlg:
			print(dlg.ShowModal())
			print(dlg.GetData().__dict__)
			# TODO: Add data to UserDatabase
	
	def on_filter_clear(self, event):
		self.filter.Clear()
		event.Skip()
	
	def recreate_tree(self, event=None):
		# Catch the search type (name or content)
		fullSearch = self._filter_menu_opts[1].IsChecked()
		
		# if evt and fullSearch:
		# 	# Do not scan all the demo files for every char
		# 	# the user input, use wx.EVT_TEXT_ENTER instead
		# 	return
		
		expansionState = self.tree.GetExpansionState()
		
		current = None
		item = self.tree.GetSelection()
		if item:
			parent = self.tree.GetItemParent(item)
			if parent:
				current = (
						self.tree.GetItemText(item),
						self.tree.GetItemText(parent)
						)
		
		self.tree.Freeze()
		self.tree.DeleteAllItems()
		self.root = self.tree.AddRoot("Calibre Search")
		
		treeFont = self.tree.GetFont()
		catFont = self.tree.GetFont()
		
		# The native treectrl on MSW has a bug where it doesn't draw
		# all of the text for an item if the font is larger than the
		# default.  It seems to be clipping the item's label as if it
		# was the size of the same label in the default font.
		if 'wxMSW' not in wx.PlatformInfo:
			treeFont.SetPointSize(treeFont.GetPointSize() + 2)
		
		treeFont.SetWeight(wx.FONTWEIGHT_BOLD)
		catFont.SetWeight(wx.FONTWEIGHT_BOLD)
		# self.tree.SetItemFont(self.root, treeFont)
		
		firstChild = None
		selectItem = None
		filter = self.filter.GetValue()
		count = 0
		
		for category, items in self.calibre_list:
			count += 1
			if filter:
				if fullSearch:
					items = []
				# TODO: Search database for value
				else:
					new_items = []
					for calibre in items:
						if filter.lower() in calibre.lower():
							new_items.append(calibre)
						
						# Special case for Smith & Wesson / S&W
						if "smith" in calibre.lower() and "wesson" in calibre.lower() and "s&w" in filter.lower():
							new_items.append(calibre)
							
						# Special case for Special / Spl
						if "special" in calibre.lower() and "spl" in filter.lower():
							new_items.append(calibre)
							
					items = new_items
			if items:
				child = self.tree.AppendItem(self.root, category)
				self.tree.SetItemFont(child, catFont)
				self.tree.SetItemData(child, count)
				if not firstChild:
					firstChild = child
				for childItem in items:
					theDemo = self.tree.AppendItem(child, childItem)
					self.tree.SetItemData(theDemo, count)
					self.treeMap[childItem] = theDemo
					if current and (childItem, category) == current:
						selectItem = theDemo
		
		if firstChild:
			self.tree.Expand(firstChild)
		if filter:
			self.tree.ExpandAll()
		elif expansionState:
			self.tree.SetExpansionState(expansionState)
		if selectItem:
			self.tree.SelectItem(selectItem)
		
		self.tree.Thaw()
		self.searchItems = {}
	
	def on_search_menu(self, _):
		
		# Catch the search type (name or content)
		fullSearch = self._filter_menu_opts[1].IsChecked()
		
		if fullSearch:
			# TODO
			pass
		else:
			self.recreate_tree()
	
	def on_item_expanded(self, event):
		item = event.GetItem()
		print(f"on_item_expanded: {self.tree.GetItemText(item)}")
		event.Skip()
	
	def on_item_collapsed(self, event):
		item = event.GetItem()
		print(f"on_item_collapsed: {self.tree.GetItemText(item)}")
		event.Skip()
	
	# def on_tree_left_down(self, event):
	# 	print(event.GetEventObject().GetSelection())
	# 	# reset the overview text if the tree item is clicked on again
	# 	pt = event.GetPosition()
	# 	item, flags = self.tree.HitTest(pt)
	# 	if item == self.tree.GetSelection():
	# 		print(self.tree.GetSelection())
	# 	event.Skip()
	#
	
	def on_sel_changed(self, event):
		print("Tree Selection Changed")
		try:
			tree_item_id = event.GetEventObject().GetSelection()
			calibre = event.GetEventObject().GetItemText(tree_item_id)
			self.info_panel.LoadData(self.calibre_dict[calibre])
		except KeyError:
			pass
	
	def on_activate(self, evt):
		print("on_activate: %s" % evt.GetActive())
		evt.Skip()
	
	def on_close(self, event):
		event.Skip()

	def GetSelection(self):
		return self.info_panel.name_value.GetValue()


