#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  menus.py
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

# this package
from GuiV2.GSMatch2_Core.IDs import *


class SpectrumViewerMenu(wx.MenuBar):
	"""
	MenuBar for Spectrum Viewer
	"""
	
	def __init__(self, parent, style=0):
		self.parent = parent
		wx.MenuBar.__init__(self, style)
		self.__populate_menubar()
	
	def __populate_menubar(self):
		file_menu = wx.Menu()
		file_menu.Append(ID_Spec_Viewer_Save, "&Save As Image\tCtrl+S", "")
		self.Bind(wx.EVT_MENU, self.parent.on_save, id=ID_Spec_Viewer_Save)
		file_menu.Append(wx.ID_EXIT, "&Quit", "")
		self.Bind(wx.EVT_MENU, self.parent.OnExit, id=wx.ID_EXIT)
		self.Append(file_menu, "&File")
		
		edit_menu = wx.Menu()
		edit_menu.Append(ID_Spec_Viewer_Copy_Image, "&Copy Image\tCtrl+C", "")
		self.Bind(wx.EVT_MENU, self.parent.on_copy, id=ID_Spec_Viewer_Copy_Image)
		edit_menu.Append(ID_Spec_Viewer_Copy_Data, "Copy &Data\tCtrl+Shift+C", "")
		self.Bind(wx.EVT_MENU, self.parent.on_copy_data, id=ID_Spec_Viewer_Copy_Data)
		self.Append(edit_menu, "&Edit")
		
		view_menu = wx.Menu()
		view_menu.Append(ID_Spec_Viewer_View_Reset, "&Reset View\tCtrl+Shift+R", "")
		self.Bind(wx.EVT_MENU, self.parent.reset_view, id=ID_Spec_Viewer_View_Reset)
		view_menu.Append(ID_Spec_Viewer_View_Previous, "&Previous View", "")
		self.Bind(wx.EVT_MENU, self.parent.previous_view, id=ID_Spec_Viewer_View_Previous)
		view_menu.Append(ID_Spec_Viewer_View_Default, "&Select", "")
		self.Bind(wx.EVT_MENU, self.parent.tool_select, id=ID_Spec_Viewer_View_Default)
		view_menu.Append(ID_Spec_Viewer_View_Zoom, "&Zoom\tCtrl+Shift+Z", "")
		self.Bind(wx.EVT_MENU, self.parent.tool_zoom, id=ID_Spec_Viewer_View_Zoom)
		view_menu.Append(ID_Spec_Viewer_View_Pan, "&Pan\tCtrl+Shift+P", "")
		self.Bind(wx.EVT_MENU, self.parent.tool_pan, id=ID_Spec_Viewer_View_Pan)
		self.Append(view_menu, "&View")
		
		menu_spectrum = wx.Menu()
		menu_spectrum.Append(ID_Spec_Viewer_by_num, "View Spectrum by Scan &Number", "")
		self.Bind(wx.EVT_MENU, self.parent.spectrum_by_number, id=ID_Spec_Viewer_by_num)
		menu_spectrum.Append(ID_Spec_Viewer_by_rt, "View Spectrum by Retention &Time", "")
		self.Bind(wx.EVT_MENU, self.parent.spectrum_by_rt, id=ID_Spec_Viewer_by_rt)
		self.Append(menu_spectrum, "&Spectrum")
		
		menu_experiment = wx.Menu()
		menu_experiment.Append(ID_Spec_Viewer_Previous_Experiment, "&Previous Experiment\tCtrl+<", "")
		self.Bind(wx.EVT_MENU, self.parent.previous_experiment, id=ID_Spec_Viewer_Previous_Experiment)
		menu_experiment.Append(ID_Spec_Viewer_Next_Experiment, "&Next Experiment\tCtrl+>", "")
		self.Bind(wx.EVT_MENU, self.parent.next_experiment, id=ID_Spec_Viewer_Next_Experiment)
		self.Append(menu_experiment, "E&xperiment")


class MenuBase(wx.Menu):
	"""
	Base class for Menus
	"""
	def __init__(self, parent, style=0):
		self.parent = parent
		wx.Menu.__init__(self, style)
		self._populate_menu()
		self._bind_events()
	
	def _populate_menu(self):
		pass
	
	def _bind_events(self):
		pass


class GSMFileMenu(MenuBase):
	"""
	File Menu for main window
	
	Options:
	
		Export
		Export as PDF
		---
		Print Preview
		Print
		Printer Settings
		---
		Quit
	"""
	
	def _populate_menu(self):
		self.Append(ID_Export, "Export", "")
		self.Append(ID_Export_PDF, "Export as PDF", "")
		self.AppendSeparator()
		self.Append(wx.ID_PREVIEW_PRINT, "Print Preview", "")
		self.Append(wx.ID_PRINT, "Print", "")
		self.Append(wx.ID_PRINT_SETUP, "Printer Settings", "")
		self.AppendSeparator()
		self.Append(wx.ID_EXIT, "Quit GunShotMatch", "")
	
	def _bind_events(self):
		self.Bind(wx.EVT_MENU, self.parent.on_export, id=ID_Export)
		self.Bind(wx.EVT_MENU, self.parent.on_export_pdf, id=ID_Export_PDF)
		self.Bind(wx.EVT_MENU, self.parent.on_print_preview, id=wx.ID_PREVIEW_PRINT)
		self.Bind(wx.EVT_MENU, self.parent.on_print, id=wx.ID_PRINT)
		self.Bind(wx.EVT_MENU, self.parent.on_printer_settings, id=wx.ID_PRINT_SETUP)
		self.Bind(wx.EVT_MENU, self.parent.OnExit, id=wx.ID_EXIT)


class GSMProjectMenu(MenuBase):
	"""
	Project Menu for main window
	
	Options:
		New Project
		---
		Open Project
		Recent Project -> Submenu
		---
		Save Project
		Save All
		---
		Close Project
	"""
	
	def _populate_menu(self):
		self.new_item = self.Append(wx.ID_NEW, "New Project", "")
		self.AppendSeparator()
		self.open_item = self.Append(wx.ID_OPEN, "Open Project", "")
		
		recent_menu = wx.Menu()
		recent_menu.Append(ID_RECENT_0, "item", "")
		recent_menu.Append(ID_RECENT_1, "item", "")
		recent_menu.Append(ID_RECENT_2, "item", "")
		recent_menu.Append(ID_RECENT_3, "item", "")
		recent_menu.Append(ID_RECENT_4, "item", "")
		recent_menu.Append(ID_RECENT_5, "item", "")
		recent_menu.Append(ID_RECENT_6, "item", "")
		recent_menu.Append(ID_RECENT_7, "item", "")
		recent_menu.Append(ID_RECENT_8, "item", "")
		recent_menu.Append(ID_RECENT_9, "item", "")
		self.AppendMenu(wx.ID_ANY, "Recent Project", recent_menu, "")
		
		self.AppendSeparator()
		self.Append(wx.ID_SAVE, "Save Project", "")
		
		self.save_all_item = self.Append(wx.ID_ANY, "Save All", "")
		
		self.AppendSeparator()
		self.Append(ID_Close_Project, "Close Project", "")
	
	def _bind_events(self):
		self.Bind(wx.EVT_MENU, self.parent.on_new_project, id=wx.ID_NEW)
		self.Bind(wx.EVT_MENU, self.parent.on_open_project, id=wx.ID_OPEN)
		self.Bind(wx.EVT_MENU, self.parent.on_recent_project, id=ID_RECENT_0)
		self.Bind(wx.EVT_MENU, self.parent.on_recent_project, id=ID_RECENT_1)
		self.Bind(wx.EVT_MENU, self.parent.on_recent_project, id=ID_RECENT_2)
		self.Bind(wx.EVT_MENU, self.parent.on_recent_project, id=ID_RECENT_3)
		self.Bind(wx.EVT_MENU, self.parent.on_recent_project, id=ID_RECENT_4)
		self.Bind(wx.EVT_MENU, self.parent.on_recent_project, id=ID_RECENT_5)
		self.Bind(wx.EVT_MENU, self.parent.on_recent_project, id=ID_RECENT_6)
		self.Bind(wx.EVT_MENU, self.parent.on_recent_project, id=ID_RECENT_7)
		self.Bind(wx.EVT_MENU, self.parent.on_recent_project, id=ID_RECENT_8)
		self.Bind(wx.EVT_MENU, self.parent.on_recent_project, id=ID_RECENT_9)
		self.Bind(wx.EVT_MENU, self.parent.on_save_project, id=wx.ID_SAVE)
		self.Bind(wx.EVT_MENU, self.parent.on_save_all, id=self.save_all_item.GetId())
		self.Bind(wx.EVT_MENU, self.parent.on_close_project, id=ID_Close_Project)


class GSMExprMenu(MenuBase):
	"""
	Experiment Menu for main window
	
	Options:
		New
		Create Multiple
		---
		Previous - switch between experiments in project depending on context e.g. when viewing TIC or spectra
		Next
	"""
	
	def _populate_menu(self):
		self.Append(ID_New_Experiment, "New\tCtrl+E", "")
		self.Append(ID_New_Experiment_Multiple, "Create Multiple", "")
		self.AppendSeparator()
		self.Append(ID_Previous_Experiment, "Previous\tCtrl+<", "")
		self.Append(ID_Next_Experiment, "Next\tCtrl+>", "")
	
	def _bind_events(self):
		self.Bind(wx.EVT_MENU, self.parent.on_new_experiment, id=ID_New_Experiment)
		self.Bind(wx.EVT_MENU, self.parent.on_new_experiment_multiple, id=ID_New_Experiment_Multiple)
		self.parent.Bind(wx.EVT_MENU, self.parent.on_previous_experiment, id=ID_Previous_Experiment)
		self.parent.Bind(wx.EVT_MENU, self.parent.on_next_experiment, id=ID_Next_Experiment)


class GSMChartsMenu(MenuBase):
	"""
	Charts Menu for main window
	
	Options:
		Create Radar Chart
		Create Bar Chart
		Create Box Whisker Plot
		Create PCA Plot
		---
		Configure Colours
		Configure Markers
		Configure Borders
		---
		Save As -> Brings up dialog with options for PNG, SVG, PDF
	"""
	
	def _populate_menu(self):
		self.Append(wx.ID_ANY, "Create Radar Chart", "")
		self.Append(wx.ID_ANY, "Create Bar Chart", "")
		self.Append(wx.ID_ANY, "Create Box Whisker Plot", "")
		self.Append(wx.ID_ANY, "Create PCA Plot", "")
		self.AppendSeparator()
		self.Append(ID_Config_Colours, "Configure Colours", "")
		self.Append(ID_Config_Markers, "Configure Markers", "")
		self.Append(ID_Config_Borders, "Configure Borders", "")
		self.AppendSeparator()
		self.__save_as_item = self.Append(wx.ID_ANY, "Save As", "")
	
	def _bind_events(self):
		self.parent.Bind(wx.EVT_MENU, self.parent.on_config_colours, id=ID_Config_Colours)
		self.parent.Bind(wx.EVT_MENU, self.parent.on_config_markers, id=ID_Config_Markers)
		self.parent.Bind(wx.EVT_MENU, self.parent.on_config_borders, id=ID_Config_Borders)
		self.Bind(wx.EVT_MENU, self.parent.on_chart_save, id=self.__save_as_item.GetId())


class GSMViewMenu(MenuBase):
	"""
	View Menu for main window
	
	Options:
		Reset Perspective
		---
		View Workflow Panel - reopen the panel if closed
		View Project Navigator
		View Legend
		---
		Reset View - Chromatogram / Spectrum
		Previous View
		Rescale y-axis
		Rescale x-axis
		---
		Select - default tool
		Zoom - Chromatogram / Spectrum
		Pan
		---
		Click to view Spectrum
		View Spectrum by Scan No. -> Opens dialog
		View Spectrum by RT -> Opens dialog
	"""
	
	def _populate_menu(self):
		self.__reset_perspective_item = self.Append(wx.ID_ANY, "Reset Perspective", "")
		self.Append(ID_View_Workflow, "View Workflow Panel", "", wx.ITEM_CHECK)
		self.Append(ID_View_Proj_Nav, "View Project Navigator", "", wx.ITEM_CHECK)
		self.Append(ID_View_Legend, "View Legend", "", wx.ITEM_CHECK)
		self.AppendSeparator()
		self.Append(ID_View_Reset, "Reset View\tCtrl+Shift+R", "")
		self.Append(ID_View_Previous, "Previous View", "")
		self.Append(ID_View_Rescale_y, "Rescale y-axis", "")
		self.Append(ID_View_Rescale_x, "Rescale x-axis", "")
		self.AppendSeparator()
		self.Append(ID_View_Default, "Select", "")
		self.Append(ID_View_Zoom, "Zoom\tCtrl+Shift+Z", "")
		self.Append(ID_View_Pan, "Pan\tCtrl+Shift+P", "")
		self.AppendSeparator()
		self.Append(ID_View_Spectrum, "Click to view Spectrum\tCtrl+Shift+S", "")
		self.Append(ID_View_Spectrum_by_num, "View Spectrum by Scan No.", "")
		self.Append(ID_View_Spectrum_by_rt, "View Spectrum by RT", "")
	
	def _bind_events(self):
		self.Bind(wx.EVT_MENU, self.parent.on_menu_view_restore, id=self.__reset_perspective_item.GetId())
		self.Bind(wx.EVT_MENU, self.parent.on_toggle_workflow, id=ID_View_Workflow)
		self.Bind(wx.EVT_MENU, self.parent.on_toggle_project_navigator, id=ID_View_Proj_Nav)
		self.Bind(wx.EVT_MENU, self.parent.on_toggle_legend, id=ID_View_Legend)
		self.parent.Bind(wx.EVT_MENU, self.parent.on_reset_view, id=ID_View_Reset)
		self.parent.Bind(wx.EVT_MENU, self.parent.on_previous_view, id=ID_View_Previous)
		self.parent.Bind(wx.EVT_MENU, self.parent.on_rescale_y, id=ID_View_Rescale_y)
		self.parent.Bind(wx.EVT_MENU, self.parent.on_rescale_x, id=ID_View_Rescale_x)
		self.parent.Bind(wx.EVT_MENU, self.parent.on_view_select, id=ID_View_Default)
		self.parent.Bind(wx.EVT_MENU, self.parent.on_zoom, id=ID_View_Zoom)
		self.parent.Bind(wx.EVT_MENU, self.parent.on_pan, id=ID_View_Pan)
		self.parent.Bind(wx.EVT_MENU, self.parent.on_spectrum_click, id=ID_View_Spectrum)
		self.parent.Bind(wx.EVT_MENU, self.parent.on_spectrum_scan, id=ID_View_Spectrum_by_num)
		self.parent.Bind(wx.EVT_MENU, self.parent.on_spectrum_rt, id=ID_View_Spectrum_by_rt)


class GSMSearchMenu(MenuBase):
	"""
	Search Menu for main window
	"""


class GSMToolsMenu(MenuBase):
	"""
	Tools Menu for main window
	
	"""
	
	def _populate_menu(self):
		self.Append(ID_RemoveAlignmentData, "Remove Alignment Data", "")
		self.Append(ID_RemoveIdentData, "Remove Compound Identification Data", "")
		self.Append(ID_RemoveConsolidateData, "Remove Consolidate Data", "")
		self.AppendSeparator()
		self.Append(
				ID_Tools_MethodEditor, "Method Editor",
				"Open the Method Editor to create or edit a Method",
				)
		self.Append(
				ID_Tools_AmmunitionEditor, "Ammunition Details Editor",
				"Open the Ammunition Details Editor to create or edit an Ammunition Details file",
				)
		self.AppendSeparator()
		self.Append(ID_Settings, "Settings", "")
	
	def _bind_events(self):
		self.Bind(wx.EVT_MENU, self.parent.on_menu_remove_alignment, id=ID_RemoveAlignmentData)
		self.Bind(wx.EVT_MENU, self.parent.on_menu_remove_ident, id=ID_RemoveIdentData)
		self.Bind(wx.EVT_MENU, self.parent.on_menu_remove_consolidate, id=ID_RemoveConsolidateData)
		self.Bind(wx.EVT_MENU, self.parent.on_method_editor, id=ID_Tools_MethodEditor)
		self.Bind(wx.EVT_MENU, self.parent.on_ammo_editor, id=ID_Tools_AmmunitionEditor)
		self.Bind(wx.EVT_MENU, self.parent.on_menu_tools_settings, id=ID_Settings)


class GSMHelpMenu(MenuBase):
	"""
	Help Menu for main window
	"""
	
	def _populate_menu(self):
		self.Append(wx.ID_HELP, "Help", "")
		self.Append(ID_About, "About", "")
	
	def _bind_events(self):
		self.Bind(wx.EVT_MENU, self.parent.on_menu_help, id=wx.ID_HELP)
		self.Bind(wx.EVT_MENU, self.parent.on_menu_help_about, id=ID_About)
