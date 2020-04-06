#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  toolbars.py
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
from collections import namedtuple

# 3rd party
import wx
# import wx.lib.agw.aui as aui
from pubsub import pub
from wx import aui

# this package
from GuiV2.GSMatch2_Core.IDs import *
from GuiV2.icons import get_icon


# TODO: replace self.name with wxpython Name in __init__ and elsewhere


class ToolData(namedtuple('__BaseTool', "name, icon, id, handler")):
	__slots__ = []
	
	# make constructor's "handler" argument optional
	def __new__(cls, name, icon, id, handler=None):
		return super(ToolData, cls).__new__(cls, name, icon, id, handler)


class ToolBarBase(wx.ToolBar):
	"""
	Base Class for custom ToolBars
	"""
	
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize):
		self.parent = parent
		self.id = id
		wx.ToolBar.__init__(
				self, parent, id, pos, size,
				style=wx.TB_FLAT | wx.TB_NODIVIDER, name="tb_base"
				)
		self.SetToolBitmapSize(wx.Size(*tb_icon_size))
		self._populate_toolbar()
		self.Realize()
		self.name = "tb_base"
		self.caption = "ToolBar Base"
		self.position = 0
	
	def _populate_toolbar(self):
		pass
	
	def add_tool(self, tool, kind=wx.ITEM_NORMAL):
		added_tool = self.AddTool(tool.id, tool.name, tool.icon, tool.name, kind)
		if tool.handler:
			self.Bind(wx.EVT_TOOL, tool.handler, added_tool, tool.id)
		return added_tool
	
	def add_radio_tool(self, tool):
		added_tool = self.AddRadioTool(tool.id, tool.name, tool.icon, shortHelp=tool.name)
		if tool.handler:
			self.Bind(wx.EVT_TOOL, tool.handler, added_tool, tool.id)
		return added_tool
	
	def add_to_manager(self, manager):
		manager.AddPane(
				self,
				aui.AuiPaneInfo().ToolbarPane().Top().LeftDockable(False).
					RightDockable(False).Name(self.name).Caption(self.caption).
					Position(self.position)
				)


class ProjectToolBar(ToolBarBase):
	"""
	ToolBar for Projects
	"""
	
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize):
		self.parent = parent
		self.id = id
		wx.ToolBar.__init__(
				self, parent, id, pos, size,
				style=wx.TB_FLAT | wx.TB_NODIVIDER, name="tb_project"
				)
		self.SetToolBitmapSize(wx.Size(*tb_icon_size))
		self._populate_toolbar()
		self.Realize()
		self.name = "tb_project"
		self.caption = "Project"
		self.position = 0
	
	def _populate_toolbar(self):
		self.add_tool(ToolData(
				name="New Project (Ctrl+N)",
				icon=get_icon(wx.ART_NEW, tb_icon_size[0]),
				id=wx.ID_NEW,
				handler=self.parent.on_new_project,
				))
		
		self.add_tool(ToolData(
				name="Open Project (Ctrl+O)",
				icon=get_icon(wx.ART_FILE_OPEN, tb_icon_size[0]),
				id=wx.ID_OPEN,
				handler=self.parent.on_open_project,
				),
				wx.ITEM_DROPDOWN
				)
		
		recent_menu = wx.Menu()
		
		for ID in recent_project_ids:
			recent_menu.Append(ID, "item", "")
		
		self.SetDropdownMenu(wx.ID_OPEN, recent_menu)
		
		self.add_tool(ToolData(
				name="Save Project (Ctrl+S)",
				icon=get_icon(wx.ART_FILE_SAVE, tb_icon_size[0]),
				id=wx.ID_SAVE,
				handler=self.parent.on_save_project,
				))
		
		self.add_tool(ToolData(
				name="Save All",
				icon=get_icon("geany-save-all", 24),
				id=ID_Save_All,
				handler=self.parent.on_save_all,
				))
		
		self.add_tool(ToolData(
				name="Close Project",
				icon=get_icon("close", tb_icon_size[0]),
				id=ID_Close_Project,
				handler=self.parent.on_close_project,
				))
		

class ExperimentToolBar(ToolBarBase):
	"""
	ToolBar for Experiments
	"""
	
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize):
		self.parent = parent
		self.id = id
		wx.ToolBar.__init__(
				self, parent, id, pos, size,
				style=wx.TB_FLAT | wx.TB_NODIVIDER, name="tb_experiment"
				)
		self.SetToolBitmapSize(wx.Size(*tb_icon_size))
		self._populate_toolbar()
		self.Realize()
		self.name = "tb_experiment"
		self.caption = "Experiment"
		self.position = 1
		
		# # Bind events for enabling and disabling controls
		pub.subscribe(self.toggle_experiment_tools, "toggle_expr_tools")

	def _populate_toolbar(self):
		self.add_tool(ToolData(
				name="New Experiment (Ctrl+E)",
				icon=get_icon("new-experiment", 24),
				id=ID_New_Experiment,
				handler=self.parent.on_new_experiment,
				),
				wx.ITEM_DROPDOWN
				)
		
		new_experiment_menu = wx.Menu()
		
		new_experiment_menu.Append(ID_New_Experiment_Single, "Create New Experiment", "")
		new_experiment_menu.Append(ID_New_Experiment_Multiple, "Create Multiple Experiments", "")
		
		self.SetDropdownMenu(ID_New_Experiment, new_experiment_menu)
		
		self.add_tool(ToolData(
				name="Previous Experiment (Ctrl+<)",
				icon=get_icon(wx.ART_GO_BACK, tb_icon_size[0]),
				id=ID_Previous_Experiment
				))
		
		self.add_tool(ToolData(
				name="Next Experiment (Ctrl+>)",
				icon=get_icon(wx.ART_GO_FORWARD, tb_icon_size[0]),
				id=ID_Next_Experiment
				))
	
	def on_expr_tools_toggle(self, event):
		self.toggle_experiment_tools(event.GetValue())
	
	def toggle_experiment_tools(self, enable=True):
		self.EnableTool(ID_Next_Experiment, enable)
		self.EnableTool(ID_Previous_Experiment, enable)


class ChartToolBar(ToolBarBase):
	"""
	ToolBar for controlling Chromatogram and Spectrum displays
	"""
	
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize):
		self.parent = parent
		self.id = id
		wx.ToolBar.__init__(
				self, parent, id, pos, size,
				style=wx.TB_FLAT | wx.TB_NODIVIDER | wx.TB_HORZ_TEXT,
				name="tb_charts"
				)
		self.SetToolBitmapSize(wx.Size(*tb_icon_size))
		self._populate_toolbar()
		self.Realize()
		self.name = "tb_charts"
		self.caption = "Charts"
		self.position = 2

	def _populate_toolbar(self):
		self.add_tool(ToolData("Configure Colours", get_icon("configure-colours", 24), ID_Config_Colours))
		self.add_tool(ToolData("Configure Markers", get_icon("configure-markers", 24), ID_Config_Markers))
		self.add_tool(ToolData("Configure Borders", get_icon("configure-borders", 24), ID_Config_Borders))


class ViewToolBar(ToolBarBase):
	"""
	ToolBar for controlling Chromatogram and Spectrum displays
	"""
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize):
		self.parent = parent
		self.id = id
		wx.ToolBar.__init__(
				self, parent, id, pos, size,
				style=wx.TB_FLAT | wx.TB_NODIVIDER, name="tb_view"
				)
		self.SetToolBitmapSize(wx.Size(*tb_icon_size))
		self._populate_toolbar()
		self.Realize()
		self.name = "tb_view"
		self.caption = "View"
		self.position = 3
		
		# Bind events for enabling and disabling controls
		pub.subscribe(self.toggle_view_tools, "toggle_view_tools")
		pub.subscribe(self.toggle_experiment_tools, "toggle_expr_tools")
	
	def _populate_toolbar(self):
		self.add_tool(ToolData(
				name="Reset View",
				icon=get_icon(wx.ART_GO_HOME, tb_icon_size[0]),
				id=ID_View_Reset,
				))
		
		self.add_tool(ToolData(
				name="Previous View",
				icon=get_icon(wx.ART_GO_TO_PARENT, tb_icon_size[0]),
				id=ID_View_Previous,
				))
		
		self.add_tool(ToolData(
				name="Rescale y-axis",
				icon=get_icon("rescale_y", tb_icon_size[0]),
				id=ID_View_Rescale_y,
				))

		self.add_tool(ToolData(
				name="Rescale x-axis",
				icon=get_icon("rescale_x", tb_icon_size[0]),
				id=ID_View_Rescale_x,
				))
		
		self.AddSeparator()
		
		self.add_radio_tool(ToolData(
				name="Select",
				icon=get_icon("default-cursor", 24),
				id=ID_View_Default,
				))
		
		self.add_radio_tool(ToolData(
				name="Zoom (Ctrl+Shift+Z)",
				icon=get_icon("zoom", 24),
				id=ID_View_Zoom,
				))
		
		self.add_radio_tool(ToolData(
				name="Pan (Ctrl+Shift+P)",
				icon=get_icon("gimp-tool-move", 24),
				id=ID_View_Pan,
				))
		
		self.add_radio_tool(
			ToolData("View Spectrum On Click (Ctrl+Shift+S)", get_icon("mass-spectrum", 24), ID_View_Spectrum))
		# TODO: Dropdown with options for Click to view, enter scan No, enter RT
		
		self.add_tool(ToolData(
				name="View Spectrum By Scan No.",
				icon=get_icon("mass-spectrum-123", tb_icon_size[0]),
				id=ID_View_Spectrum_by_num,
				))
		
		self.add_tool(ToolData(
				name="View Spectrum By RT",
				icon=get_icon("mass-spectrum-rt", tb_icon_size[0]),
				id=ID_View_Spectrum_by_rt,
				))
	
	def on_view_tools_toggle(self, event):
		self.toggle_view_tools(event.GetValue())
		
	def on_expr_tools_toggle(self, event):
		self.toggle_experiment_tools(event.GetValue())
	
	def toggle_view_tools(self, enable=True):
		self.EnableTool(ID_View_Default, enable)
		self.EnableTool(ID_View_Pan, enable)
		self.EnableTool(ID_View_Zoom, enable)
		self.EnableTool(ID_View_Spectrum, enable)
		self.EnableTool(ID_View_Previous, enable)
		self.EnableTool(ID_View_Rescale_x, enable)
		self.EnableTool(ID_View_Rescale_y, enable)
		self.EnableTool(ID_View_Reset, enable)
	
	def toggle_experiment_tools(self, enable=True):
		self.EnableTool(ID_View_Spectrum_by_num, enable)
		self.EnableTool(ID_View_Spectrum_by_rt, enable)


class ExportToolBar(ToolBarBase):
	"""
	ToolBar for exporting and printing current view
	"""
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize):
		self.parent = parent
		self.id = id
		wx.ToolBar.__init__(
				self, parent, id, pos, size,
				style=wx.TB_FLAT | wx.TB_NODIVIDER, name="tb_export"
				)
		self.SetToolBitmapSize(wx.Size(*tb_icon_size))
		self._populate_toolbar()
		self.Realize()
		self.name = "tb_export"
		self.caption = "Export"
		self.position = 4

	def _populate_toolbar(self):
		self.add_tool(ToolData(
				name="Export as PDF",
				icon=get_icon("export-pdf", tb_icon_size[0]),
				id=ID_Export_PDF,
				handler=self.parent.on_export_pdf,
				))
		
		self.add_tool(ToolData(
				name="Print (Ctrl+P)",
				icon=get_icon("Document-print", tb_icon_size[0]),
				id=wx.ID_PRINT,
				handler=self.parent.on_print,
				))
		
		self.add_tool(ToolData(
				name="Print Preview",
				icon=get_icon("Document-print-preview", tb_icon_size[0]),
				id=wx.ID_PREVIEW_PRINT,
				handler=self.parent.on_print_preview,
				))


class SpectrumViewerToolBar(ToolBarBase):
	"""
	ToolBar for Spectrum Viewer
	
	TODO: copy and copy data
	"""
	
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize):
		self.parent = parent
		self.id = id
		wx.ToolBar.__init__(
				self, parent, id, pos, size,
				style=wx.TB_FLAT | wx.TB_NODIVIDER, name="tb_spectrum"
				)
		self.SetToolBitmapSize(wx.Size(*tb_icon_size))
		self._populate_toolbar()
		self.Realize()
		self.name = "tb_spectrum"
		self.caption = "Spectrum"
		self.position = 1
	
	def _populate_toolbar(self):
		self.add_tool(ToolData(
				"Previous Experiment (Ctrl+<)",
				get_icon(wx.ART_GO_BACK, tb_icon_size[0]),
				ID_Spec_Viewer_Previous_Experiment,
				self.parent.previous_experiment
				))
		
		self.add_tool(ToolData(
				"Next Experiment (Ctrl+>)",
				get_icon(wx.ART_GO_FORWARD, tb_icon_size[0]),
				ID_Spec_Viewer_Next_Experiment,
				self.parent.next_experiment
				))
		
		self.AddSeparator()
		
		self.add_tool(ToolData(
				"Reset View",
				get_icon(wx.ART_GO_HOME, tb_icon_size[0]),
				ID_Spec_Viewer_View_Reset,
				self.parent.reset_view
				))
		
		self.add_tool(ToolData(
				"Previous View",
				get_icon(wx.ART_GO_TO_PARENT, tb_icon_size[0]),
				ID_Spec_Viewer_View_Previous,
				self.parent.previous_view
				))
		
		self.add_radio_tool(ToolData(
				"Select",
				get_icon("default-cursor", 24),
				ID_Spec_Viewer_View_Default,
				self.parent.tool_select
				))
		
		self.add_radio_tool(ToolData(
				"Zoom (Ctrl+Shift+Z)",
				get_icon("zoom", 24),
				ID_Spec_Viewer_View_Zoom,
				self.parent.tool_zoom
				))
		
		self.add_radio_tool(ToolData(
				"Pan (Ctrl+Shift+P)",
				get_icon("gimp-tool-move", 24),
				ID_Spec_Viewer_View_Pan,
				self.parent.tool_pan
				))
		
		self.AddSeparator()
		
		self.add_tool(ToolData(
				"View Spectrum By Scan No.",
				get_icon("mass-spectrum-123", tb_icon_size[0]),
				ID_Spec_Viewer_by_num,
				self.parent.spectrum_by_number
				))
		
		self.add_tool(ToolData(
				"View Spectrum By RT",
				get_icon("mass-spectrum-rt", tb_icon_size[0]),
				ID_Spec_Viewer_by_rt,
				self.parent.spectrum_by_rt
				))
