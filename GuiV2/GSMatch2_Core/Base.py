#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  Base.py
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

# stdlib
import datetime
import getpass
import socket
import sys
from io import StringIO

# 3rd party
import wx
from wx.aui import AuiNotebook

# this package
from GuiV2.GSMatch2_Core import Method
from GuiV2.GSMatch2_Core.InfoProperties import longstr, Property
# from GuiV2.GSMatch2_Core.SpectrumFrame import SpectrumFrame
from GuiV2.GSMatch2_Core.io import get_file_from_archive, load_info_json
from GuiV2.GSMatch2_Core.watchdog import time_now

# Paths for NIST Search Engine
if sys.platform == "win32":
	FULL_PATH_TO_MAIN_LIBRARY = "C:\\Users\\dom13\\Python\\mainlib"
	FULL_PATH_TO_WORK_DIR = "C:\\Users\\dom13\\Python\\00 Projects\\pynist"
else:
	FULL_PATH_TO_MAIN_LIBRARY = "/home/domdf/Python/mainlib"
	FULL_PATH_TO_WORK_DIR = "/home/domdf/Python/00 Projects/pynist"


class GSMBase:
	"""
	Base Class for Experiment and Project
	"""
	
	type_string = "GSMBase"
	
	def __init__(
			self, name, method, user, device, date_created, date_modified,
			version, description='', filename=None
			):
		
		self.name = name
		
		self.description = Property(
				f"{name}_description", description, longstr,
				help=f"A description of the {self.type_string}", label="Description"
				)
		
		self.method = Property(
				f"{name}_method", method, dir, editable=False,
				help="The Method file to use"
				)
		
		self.user = Property(
				f"{name}_user", user, str,
				help=f"The user who created the {self.type_string}",
				editable=False, label="User"
				)
		self.device = Property(
				f"{name}_device", device, str,
				help=f"The device that created the {self.type_string}",
				editable=False, label="Device"
				)
		self.date_created = Property(
				f"{name}_date_created", date_created, datetime,
				help=f"The date the {self.type_string} was created",
				editable=False, immutable=True, label="Date Created"
				)
		self.date_modified = Property(
				f"{name}_date_modified", date_modified, datetime,
				help=f"The date the {self.type_string} was last modified",
				editable=False, label="Date Modified"
				)
		self.version = Property(
				f"{name}_version", version, str,
				help=f"The {self.type_string} file format version number",
				editable=False, label="Version"
				)
		self.filename = Property(
				f"{name}_filename", filename, dir,
				help=f"The name of the {self.type_string} file", label="Filename"
				)
		
		self._method_data = None
	
	@classmethod
	def new_empty(cls):
		"""
		Create a new empty object

		:return:
		:rtype:
		"""
		
		return cls(
				None, None, getpass.getuser(), socket.gethostname(),
				time_now(),
				time_now(),
				"1.0.0"
				)
	
	@classmethod
	def new(cls, name, method, description=None):
		"""
		Create a new object

		:param name:
		:type name:
		:param method:
		:type method:
		:param description:
		:type description:

		:return:
		:rtype:
		"""
		
		return cls(
				name, method, getpass.getuser(), socket.gethostname(),
				date_created=time_now(),
				date_modified=time_now(),
				version="1.0.0", description=description
				)
	
	@property
	def info_data(self):
		"""
		Returns the contents of the info file

		:return:
		:rtype:
		"""
		
		return load_info_json(self.filename)
	
	def __str__(self):
		return self.__repr__()
	
	def __eq__(self, other):
		if other.__class__ == self.__class__:
			return \
				self.name == other.name and \
				self.date_created == other.date_created and \
				self.date_modified == other.date_modified
		else:
			return NotImplemented
	
	def __repr__(self):
		return f"{self.type_string}({self.name})"
	
	@classmethod
	def load(cls, filename):
		"""
		Load from a file

		:param filename:
		:type filename:
		"""
		
		return cls(**load_info_json(filename), filename=filename)
	
	def _get_all_properties(self):
		"""
		Returns a list containing all of the properties, in the order they should be displayed

		:return:
		:rtype: list
		"""
		
		return [
				self.description,
				self.user,
				self.device,
				self.date_created,
				self.date_modified,
				self.method,
				self.filename,
				self.version,
				]
	
	@property
	def all_properties(self):
		"""
		Returns a list containing all of the properties, in the order they should be displayed

		:return:
		:rtype: list
		"""
		
		return self._get_all_properties()
	
	@property
	def method_data(self):
		"""
		Returns the contents of the method file

		:return:
		:rtype:
		"""
		
		# Load method data if it hasn't been before
		if not self._method_data:
			# hasattr(self, "_method_data"):
			self._load_method_data()
		return self._method_data
	
	def _load_method_data(self):
		"""
		Loads the contents of the method file
		"""
		
		method_text = get_file_from_archive(self.filename.Path, self.method.filename).read().decode("utf-8")
		
		# From https://stackoverflow.com/a/21766494/3092681
		buf = StringIO(method_text)
		
		self._method_data = Method.Method(buf)
		# self._method_data = None
		buf.close()


class NotebookToolsMixin:
	
	def get_page_by_index(self, index):
		"""
		Returns the page with the given index

		:param index: The index of the tab to return the page for
		:type index: int

		:rtype: wx.Panel
		"""
		
		return self.notebook.GetPage(index)
	
	def get_selected_page(self):
		"""
		Returns the currently selected page, or None if no page is selected.

		:rtype: wx.Panel
		"""
		
		sel = self.notebook.GetSelection()
		
		if sel != -1:
			return self.notebook.GetPage(sel)
	
	def get_selected_page_text(self):
		"""
		Returns the page title for the currently selected page.

		:rtype: str
		"""
		
		sel = self.notebook.GetSelection()
		
		if sel != -1:
			return self.notebook.GetPageText(sel)


class NotebookPanelBase(wx.Panel, NotebookToolsMixin):
	def __init__(
			self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
			size=wx.DefaultSize, style=0, name="ExperimentDataPanel"
			):
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
		
		wx.Panel.__init__(self, parent, id=id, pos=pos, size=size, style=style | wx.TAB_TRAVERSAL, name=name)
		self.notebook = AuiNotebook(
				self, wx.ID_ANY,
				style=wx.aui.AUI_NB_TOP | wx.aui.AUI_NB_TAB_SPLIT |
					  wx.aui.AUI_NB_TAB_MOVE | wx.aui.AUI_NB_SCROLL_BUTTONS |
					  wx.aui.AUI_NB_CLOSE_ON_ACTIVE_TAB | wx.aui.AUI_NB_MIDDLE_CLICK_CLOSE
				)

		self._do_layout()
		
		self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.on_page_close, self.notebook)
		self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.on_nb_sel_changed)

	def on_nb_sel_changed(self, event):
		wx.CallAfter(self.freeze_hidden_tabs)
		event.Skip()
	
	def freeze_hidden_tabs(self):
		# print(self.get_selected_page_text())
		for page_idx in range(self.notebook.GetPageCount()):
			# print(self.notebook.GetPageText(page_idx))
			if self.notebook.GetPage(page_idx).IsShownOnScreen():
				if self.notebook.GetPage(page_idx).IsFrozen():
					self.notebook.GetPage(page_idx).Thaw()
			else:
				if not self.notebook.GetPage(page_idx).IsFrozen():
					self.notebook.GetPage(page_idx).Freeze()

	def _do_layout(self):
		outer_sizer = wx.BoxSizer(wx.VERTICAL)
		outer_sizer.Add(self.notebook, 1, wx.EXPAND, 0)
		self.SetSizer(outer_sizer)
		outer_sizer.Fit(self)
		self.Layout()
	
	def on_page_close(self, event):
		"""
		Event Handler for a page being closed
		"""
		
		closed_tab_idx = event.GetOldSelection()
		closed_tab = self.notebook.GetPage(closed_tab_idx)
		event.Veto()
		self.notebook.RemovePage(closed_tab_idx)
		
		# TODO: do something about closing the last page;
		#  perhaps open a special page that tells the user what they can open?
		closed_tab.Hide()
	
	def switch_to_content(self, page_title):
		"""
		Switch to the page with the given title. if the tab is not open it is opened

		:param page_title: The name of the page to switch to
		:type page_title: str

		:return: The index of the tab that was switched to
		:rtype: int
		"""
		
		for tab_idx in range(self.notebook.PageCount):
			if self.notebook.GetPageText(tab_idx) == page_title:
				self.notebook.SetSelection(tab_idx)
				return tab_idx
		
		# Tab not open, so open it
		self.add_tab(page_title)
		return self.notebook.GetPageCount() - 1
	
	def add_tab(self, tab_name):
		pass
	
	
class ProjExprPanelBase(NotebookPanelBase):
	def __init__(
			self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
			size=wx.DefaultSize, style=0, name="ExperimentDataPanel"):
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
		
		NotebookPanelBase.__init__(self, parent, id=id, pos=pos, size=size, style=style | wx.TAB_TRAVERSAL, name=name)
	
	def add_method_tab(self):
		"""
		Add the tab for the Method if it is not already open
		"""
		
		for tab_idx in range(self.notebook.GetPageCount()):
			if self.notebook.GetPageText(tab_idx) == "Method":
				# tab is already open
				return
		
		# Tab is not open
		self.notebook.AddPage(self.method_tab, "Method", select=True)
	
	def remove_ident_tab(self):
		for tab_idx in range(self.notebook.GetPageCount()):
			if self.notebook.GetPage(tab_idx) == self.ident_panel:
				self.notebook.RemovePage(tab_idx)
				self.ident_panel.Destroy()
				self.ident_panel = None
				return
	
	def do_make_method_tab(self, method, editable=True):
		self.method_tab = Method.MethodPGPanel(self.notebook, method=method, editable=editable)
		self.notebook.AddPage(self.method_tab, "Method", select=True)

