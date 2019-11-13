#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  browse_tab.py
"""Tab for browsing data"""
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2017-2019 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import csv
import json
import types
import traceback

# 3rd party
import numpy

import wx
import wx.html2

import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar

from domdf_wxpython_tools import list_dialog
from domdf_wxpython_tools.icons import get_toolbar_icon
from domdf_wxpython_tools.utils import coming_soon
from domdf_wxpython_tools.dialogs import file_dialog

from mathematical.utils import rounders

from pyms.Display import Display
from pyms.Peak.List.IO import load_peaks
from pyms.GCMS.Class import IonChromatogram

# this package
from GSMatch.GSMatch_Core import border_config, ChartViewer, threads
from GSMatch.GSMatch_Core.My_Axes import My_Axes
#from GSMatch.GSMatch_Core.ChromatogramDisplay import Display


# begin wxGlade: dependencies
# end wxGlade

# begin wxGlade: extracode
# end wxGlade

matplotlib.projections.register_projection(My_Axes)


class browse_tab(wx.Panel):
	def __init__(self, parent, *args, **kwds):
		self._parent = parent
		# begin wxGlade: browse_tab.__init__
		kwds["style"] = kwds.get("style", 0) | wx.TAB_TRAVERSAL
		wx.Panel.__init__(self, *args, **kwds)
		self.browse_toolbar = wx.Panel(self, wx.ID_ANY, style=wx.BORDER_SUNKEN)
		self.browse_toolbar.SetMaxSize((-1,40))
		self.focus_thief = wx.Button(self.browse_toolbar, wx.ID_ANY, "")
		self.CloseProject = wx.BitmapButton(self.browse_toolbar, wx.ID_ANY, wx.Bitmap("./lib/icons/close_24.png", wx.BITMAP_TYPE_ANY), style=wx.BORDER_NONE | wx.BU_AUTODRAW | wx.BU_EXACTFIT | wx.BU_NOTEXT)
		self.OpenSample = wx.BitmapButton(self.browse_toolbar, wx.ID_ANY, wx.Bitmap("./lib/icons/open_24.png", wx.BITMAP_TYPE_ANY), style=wx.BORDER_NONE | wx.BU_AUTODRAW | wx.BU_EXACTFIT | wx.BU_NOTEXT)
		self.ViewPeakList = wx.BitmapButton(self.browse_toolbar, wx.ID_ANY, wx.Bitmap("./lib/icons/list_view_24.png", wx.BITMAP_TYPE_ANY), style=wx.BORDER_NONE | wx.BU_AUTODRAW | wx.BU_EXACTFIT | wx.BU_NOTEXT)
		self.PreviousSample = wx.BitmapButton(self.browse_toolbar, wx.ID_ANY, get_toolbar_icon("ART_GO_BACK"), style=wx.BORDER_NONE | wx.BU_AUTODRAW | wx.BU_EXACTFIT | wx.BU_NOTEXT)
		self.NextSample = wx.BitmapButton(self.browse_toolbar, wx.ID_ANY, get_toolbar_icon("ART_GO_FORWARD"), style=wx.BORDER_NONE | wx.BU_AUTODRAW | wx.BU_EXACTFIT | wx.BU_NOTEXT)
		self.ResetView = wx.BitmapButton(self.browse_toolbar, wx.ID_ANY, get_toolbar_icon("ART_GO_HOME"), style=wx.BORDER_NONE | wx.BU_AUTODRAW | wx.BU_EXACTFIT | wx.BU_NOTEXT)
		self.PreviousView = wx.BitmapButton(self.browse_toolbar, wx.ID_ANY, get_toolbar_icon("ART_GO_TO_PARENT"), style=wx.BORDER_NONE | wx.BU_AUTODRAW | wx.BU_EXACTFIT | wx.BU_NOTEXT)
		self.Zoom_Btn = wx.BitmapButton(self.browse_toolbar, wx.ID_ANY, wx.Bitmap("./lib/icons/zoom_24.png", wx.BITMAP_TYPE_ANY), style=wx.BORDER_NONE | wx.BU_AUTODRAW | wx.BU_EXACTFIT | wx.BU_NOTEXT)
		self.Pan_Btn = wx.BitmapButton(self.browse_toolbar, wx.ID_ANY, wx.Bitmap("./lib/icons/gimp-tool-move.png", wx.BITMAP_TYPE_ANY), style=wx.BORDER_NONE | wx.BU_AUTODRAW | wx.BU_EXACTFIT | wx.BU_NOTEXT)
		self.ViewSpectrum_Btn = wx.BitmapButton(self.browse_toolbar, wx.ID_ANY, wx.Bitmap("./lib/icons/Mass_Spectrum_by_Fredrik_Edfors_from_the_Noun_Project.24.png", wx.BITMAP_TYPE_ANY), style=wx.BORDER_NONE | wx.BU_AUTODRAW | wx.BU_EXACTFIT | wx.BU_NOTEXT)
		self.config_borders_button = wx.Button(self.browse_toolbar, wx.ID_ANY, "Configure Borders")
		self.png_button = wx.ToggleButton(self.browse_toolbar, wx.ID_ANY, "PNG")
		self.svg_button = wx.ToggleButton(self.browse_toolbar, wx.ID_ANY, "SVG")
		self.pdf_button = wx.ToggleButton(self.browse_toolbar, wx.ID_ANY, "PDF")
		self.save_btn = wx.BitmapButton(self.browse_toolbar, wx.ID_SAVE, get_toolbar_icon("ART_FLOPPY"), style=wx.BORDER_NONE | wx.BU_AUTODRAW | wx.BU_EXACTFIT | wx.BU_NOTEXT)
		self.browse_project_notebook = wx.Notebook(self, wx.ID_ANY, style=wx.NB_BOTTOM)
		self.browse_project_charts = wx.Panel(self.browse_project_notebook, wx.ID_ANY)
		self.open_project_body_panel = wx.Panel(self.browse_project_charts, wx.ID_ANY, style=wx.BORDER_SUNKEN)
		self.radar_chart_button = wx.BitmapButton(self.open_project_body_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/radar_chart_192.png", wx.BITMAP_TYPE_ANY))
		self.mean_peak_area_button = wx.BitmapButton(self.open_project_body_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/mean_peak_area_192.png", wx.BITMAP_TYPE_ANY))
		self.open_project_header_browser = wx.html2.WebView.New(self.open_project_body_panel, wx.ID_ANY)
		self.open_project_header_browser.SetMaxSize((200,200))
		self.box_whisker_button = wx.BitmapButton(self.open_project_body_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/box_whisker_192.png", wx.BITMAP_TYPE_ANY))
		self.peak_area_button = wx.BitmapButton(self.open_project_body_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/peak_area_192.png", wx.BITMAP_TYPE_ANY))
		self.chromatogram_button = wx.BitmapButton(self.open_project_body_panel, wx.ID_ANY, wx.Bitmap("./lib/icons/HPLC_Chromatogram_by_Fredrik_Edfors_from_the_Noun_Project_192.png", wx.BITMAP_TYPE_ANY))
		self.browse_project_chromatogram = wx.Panel(self.browse_project_notebook, wx.ID_ANY)
		self.chromatogram_parent_panel = wx.Panel(self.browse_project_chromatogram, wx.ID_ANY, style=wx.BORDER_SUNKEN)
		
		# create the figure with a single plot and create a canvas with the figure
		self.chromatogram_figure = Figure()
		self.chromatogram_axes = self.chromatogram_figure.add_subplot(111, projection="My_Axes")  # 1x1 grid, first subplot
		
		self.chromatogram_canvas = FigureCanvas(self.chromatogram_parent_panel, wx.ID_ANY, self.chromatogram_figure)
		self.browse_project_comparison = wx.Panel(self.browse_project_notebook, wx.ID_ANY)
		self.browse_project_data = wx.Panel(self.browse_project_notebook, wx.ID_ANY)
		self.dv_main_panel = wx.Panel(self.browse_project_data, wx.ID_ANY, style=wx.BORDER_SUNKEN)
		self.data_viewer_v_splitter = wx.SplitterWindow(self.dv_main_panel, wx.ID_ANY, style=wx.SP_3D | wx.SP_BORDER | wx.SP_LIVE_UPDATE)
		self.dv_list_panel = wx.Panel(self.data_viewer_v_splitter, wx.ID_ANY)
		self.data_viewer_list = wx.ListCtrl(self.dv_list_panel, wx.ID_ANY, style=wx.LC_HRULES | wx.LC_REPORT | wx.LC_VRULES)
		self.dv_data_panel = wx.Panel(self.data_viewer_v_splitter, wx.ID_ANY)
		self.data_viewer_h_splitter = wx.SplitterWindow(self.dv_data_panel, wx.ID_ANY, style=wx.SP_3D | wx.SP_BORDER | wx.SP_LIVE_UPDATE)
		self.dv_spec_panel = wx.Panel(self.data_viewer_h_splitter, wx.ID_ANY)
		self.data_viewer_notebook = wx.Notebook(self.dv_spec_panel, wx.ID_ANY, style=wx.NB_BOTTOM)
		self.data_viewer_reference = wx.Panel(self.data_viewer_notebook, wx.ID_ANY)
		self.dv_reference_panel = wx.Panel(self.data_viewer_reference, wx.ID_ANY, style=wx.BORDER_SUNKEN)
		
		# create the figure with a single plot and create a canvas with the figure
		self.dv_reference_spec_figure = Figure()
		self.dv_reference_spec_axes = self.dv_reference_spec_figure.add_subplot(111, projection="My_Axes")  # 1x1 grid, first subplot
		
		self.dv_reference_spec_canvas = FigureCanvas(self.dv_reference_panel, wx.ID_ANY, self.dv_reference_spec_figure)
		self.dv_reference_toolbar = wx.Panel(self.data_viewer_reference, wx.ID_ANY, style=wx.BORDER_SUNKEN)
		self.dv_reference_toolbar.SetMaxSize((-1,40))
		self.dv_reference_focus_thief = wx.Button(self.dv_reference_toolbar, wx.ID_ANY, "")
		self.dv_reference_previous_btn = wx.BitmapButton(self.dv_reference_toolbar, wx.ID_ANY, wx.Bitmap("./lib/icons/go_back_24.png", wx.BITMAP_TYPE_ANY), style=wx.BORDER_NONE | wx.BU_AUTODRAW | wx.BU_EXACTFIT | wx.BU_NOTEXT)
		self.dv_reference_next_btn = wx.BitmapButton(self.dv_reference_toolbar, wx.ID_ANY, wx.Bitmap("./lib/icons/go_forward_24.png", wx.BITMAP_TYPE_ANY), style=wx.BORDER_NONE | wx.BU_AUTODRAW | wx.BU_EXACTFIT | wx.BU_NOTEXT)
		self.dv_reference_png_button = wx.ToggleButton(self.dv_reference_toolbar, wx.ID_ANY, "PNG")
		self.dv_reference_svg_button = wx.ToggleButton(self.dv_reference_toolbar, wx.ID_ANY, "SVG")
		self.dv_reference_pdf_button = wx.ToggleButton(self.dv_reference_toolbar, wx.ID_ANY, "PDF")
		self.dv_reference_save_btn = wx.BitmapButton(self.dv_reference_toolbar, wx.ID_ANY, wx.Bitmap("./lib/icons/save_24.png", wx.BITMAP_TYPE_ANY), style=wx.BORDER_NONE | wx.BU_AUTODRAW | wx.BU_EXACTFIT | wx.BU_NOTEXT)
		self.data_viewer_samples = wx.Panel(self.data_viewer_notebook, wx.ID_ANY)
		self.dv_samples_panel = wx.Panel(self.data_viewer_samples, wx.ID_ANY, style=wx.BORDER_SUNKEN)
		
		# create the figure with a single plot and create a canvas with the figure
		self.dv_samples_spec_figure = Figure()
		self.dv_samples_spec_axes = self.dv_samples_spec_figure.add_subplot(111, projection="My_Axes")  # 1x1 grid, first subplot
		
		self.dv_samples_spec_canvas = FigureCanvas(self.dv_samples_panel, wx.ID_ANY, self.dv_samples_spec_figure)
		self.dv_samples_toolbar = wx.Panel(self.data_viewer_samples, wx.ID_ANY, style=wx.BORDER_SUNKEN)
		self.dv_samples_toolbar.SetMaxSize((-1,40))
		self.dv_samples_focus_thief = wx.Button(self.dv_samples_toolbar, wx.ID_ANY, "")
		self.dv_samples_previous_btn = wx.BitmapButton(self.dv_samples_toolbar, wx.ID_ANY, wx.Bitmap("./lib/icons/go_back_24.png", wx.BITMAP_TYPE_ANY), style=wx.BORDER_NONE | wx.BU_AUTODRAW | wx.BU_EXACTFIT | wx.BU_NOTEXT)
		self.dv_samples_next_btn = wx.BitmapButton(self.dv_samples_toolbar, wx.ID_ANY, wx.Bitmap("./lib/icons/go_forward_24.png", wx.BITMAP_TYPE_ANY), style=wx.BORDER_NONE | wx.BU_AUTODRAW | wx.BU_EXACTFIT | wx.BU_NOTEXT)
		self.dv_samples_png_button = wx.ToggleButton(self.dv_samples_toolbar, wx.ID_ANY, "PNG")
		self.dv_samples_svg_button = wx.ToggleButton(self.dv_samples_toolbar, wx.ID_ANY, "SVG")
		self.dv_samples_pdf_button = wx.ToggleButton(self.dv_samples_toolbar, wx.ID_ANY, "PDF")
		self.dv_samples_save_btn = wx.BitmapButton(self.dv_samples_toolbar, wx.ID_ANY, wx.Bitmap("./lib/icons/save_24.png", wx.BITMAP_TYPE_ANY), style=wx.BORDER_NONE | wx.BU_AUTODRAW | wx.BU_EXACTFIT | wx.BU_NOTEXT)
		self.data_viewer_head2tail = wx.Panel(self.data_viewer_notebook, wx.ID_ANY)
		self.dv_head2tail_panel = wx.Panel(self.data_viewer_head2tail, wx.ID_ANY, style=wx.BORDER_SUNKEN)
		
		# create the figure with a single plot and create a canvas with the figure
		self.dv_head2tail_spec_figure = Figure()
		self.dv_head2tail_spec_axes = self.dv_head2tail_spec_figure.add_subplot(111, projection="My_Axes")  # 1x1 grid, first subplot
		
		self.dv_head2tail_spec_canvas = FigureCanvas(self.dv_head2tail_panel, wx.ID_ANY, self.dv_head2tail_spec_figure)
		self.dv_head2tail_toolbar = wx.Panel(self.data_viewer_head2tail, wx.ID_ANY, style=wx.BORDER_SUNKEN)
		self.dv_head2tail_toolbar.SetMaxSize((-1,40))
		self.dv_head2tail_focus_thief = wx.Button(self.dv_head2tail_toolbar, wx.ID_ANY, "")
		self.dv_head2tail_previous_btn = wx.BitmapButton(self.dv_head2tail_toolbar, wx.ID_ANY, wx.Bitmap("./lib/icons/go_back_24.png", wx.BITMAP_TYPE_ANY), style=wx.BORDER_NONE | wx.BU_AUTODRAW | wx.BU_EXACTFIT | wx.BU_NOTEXT)
		self.dv_head2tail_next_btn = wx.BitmapButton(self.dv_head2tail_toolbar, wx.ID_ANY, wx.Bitmap("./lib/icons/go_forward_24.png", wx.BITMAP_TYPE_ANY), style=wx.BORDER_NONE | wx.BU_AUTODRAW | wx.BU_EXACTFIT | wx.BU_NOTEXT)
		self.dv_head2tail_png_button = wx.ToggleButton(self.dv_head2tail_toolbar, wx.ID_ANY, "PNG")
		self.dv_head2tail_svg_button = wx.ToggleButton(self.dv_head2tail_toolbar, wx.ID_ANY, "SVG")
		self.dv_head2tail_pdf_button = wx.ToggleButton(self.dv_head2tail_toolbar, wx.ID_ANY, "PDF")
		self.dv_head2tail_save_btn = wx.BitmapButton(self.dv_head2tail_toolbar, wx.ID_ANY, wx.Bitmap("./lib/icons/save_24.png", wx.BITMAP_TYPE_ANY), style=wx.BORDER_NONE | wx.BU_AUTODRAW | wx.BU_EXACTFIT | wx.BU_NOTEXT)
		self.dv_html_panel = wx.Panel(self.data_viewer_h_splitter, wx.ID_ANY)
		self.dv_html = wx.html2.WebView.New(self.dv_html_panel, wx.ID_ANY)
		self.dv_html_home = "http://domdfcoding.github.com/GunShotMatch"
		self.dv_html.LoadURL(self.dv_html_home)

		self.__set_properties()
		self.__do_layout()

		self.Bind(wx.EVT_BUTTON, self.on_close_project, self.CloseProject)
		self.Bind(wx.EVT_BUTTON, self.on_open_sample, self.OpenSample)
		self.Bind(wx.EVT_BUTTON, self.on_view_peak_list, self.ViewPeakList)
		self.Bind(wx.EVT_BUTTON, self.on_previous_sample, self.PreviousSample)
		self.Bind(wx.EVT_BUTTON, self.on_next_sample, self.NextSample)
		self.Bind(wx.EVT_BUTTON, self.on_chromatogram_reset_view, self.ResetView)
		self.Bind(wx.EVT_BUTTON, self.on_chromatogram_previous_view, self.PreviousView)
		self.Bind(wx.EVT_BUTTON, self.on_chromatogram_zoom, self.Zoom_Btn)
		self.Bind(wx.EVT_BUTTON, self.on_chromatogram_pan, self.Pan_Btn)
		self.Bind(wx.EVT_BUTTON, self.on_view_spectrum, self.ViewSpectrum_Btn)
		self.Bind(wx.EVT_BUTTON, self.do_configure_borders, self.config_borders_button)
		self.Bind(wx.EVT_BUTTON, self.do_save_chrom, self.save_btn)
		self.Bind(wx.EVT_BUTTON, self.show_radar_chart, self.radar_chart_button)
		self.Bind(wx.EVT_BUTTON, self.show_mean_peak_area_chart, self.mean_peak_area_button)
		self.Bind(wx.EVT_BUTTON, self.show_box_whisker_chart, self.box_whisker_button)
		self.Bind(wx.EVT_BUTTON, self.show_peak_area_chart, self.peak_area_button)
		self.Bind(wx.EVT_BUTTON, self.show_chromatogram, self.chromatogram_button)
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.do_select_peak, self.data_viewer_list)
		self.Bind(wx.EVT_BUTTON, self.dv_do_save_reference, self.dv_reference_save_btn)
		self.Bind(wx.EVT_BUTTON, self.dv_on_samples_previous, self.dv_samples_previous_btn)
		self.Bind(wx.EVT_BUTTON, self.dv_on_samples_next, self.dv_samples_next_btn)
		self.Bind(wx.EVT_BUTTON, self.dv_do_save_samples, self.dv_samples_save_btn)
		self.Bind(wx.EVT_BUTTON, self.dv_on_head2tail_previous, self.dv_head2tail_previous_btn)
		self.Bind(wx.EVT_BUTTON, self.dv_on_head2tail_next, self.dv_head2tail_next_btn)
		self.Bind(wx.EVT_BUTTON, self.dv_do_save_head2tail, self.dv_head2tail_save_btn)
		self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_browse_tab_change, self.browse_project_notebook)
		# end wxGlade
		
		threads.myEVT_DATA_VIEWER2.set_receiver(self)
		threads.myEVT_DATA_VIEWER2.Bind(self.Data_Viewer_Ready)
		#self.Bind(threads.EVT_DATA_VIEWER, self.Data_Viewer_Ready)
	
		self.display_chromatogram()
	
		self.pdf_button.SetValue(True)
		self.png_button.SetValue(True)
		self.svg_button.SetValue(True)
		
		self.browser_peak_data = []
		
		self.current_project = None
		self.current_project_name = None

	def __set_properties(self):
		# begin wxGlade: browse_tab.__set_properties
		self.focus_thief.SetMinSize((1, 1))
		self.CloseProject.SetMinSize((38, 38))
		self.CloseProject.SetToolTip("Close Project")
		self.OpenSample.SetMinSize((38, 38))
		self.OpenSample.SetToolTip("Open Sample Chromatogram")
		self.OpenSample.Enable(False)
		self.ViewPeakList.SetMinSize((38, 38))
		self.ViewPeakList.SetToolTip("View Peak List")
		self.PreviousSample.SetMinSize((38, 38))
		self.PreviousSample.SetToolTip("Previous Sample")
		self.PreviousSample.Enable(False)
		self.NextSample.SetMinSize((38, 38))
		self.NextSample.SetToolTip("Next Sample")
		self.NextSample.Enable(False)
		self.ResetView.SetMinSize((38, 38))
		self.ResetView.SetToolTip("Reset View")
		self.ResetView.Enable(False)
		self.PreviousView.SetMinSize((38, 38))
		self.PreviousView.SetToolTip("Previous View")
		self.PreviousView.Enable(False)
		self.Zoom_Btn.SetMinSize((38, 38))
		self.Zoom_Btn.SetToolTip("Pan")
		self.Zoom_Btn.Enable(False)
		self.Pan_Btn.SetMinSize((38, 38))
		self.Pan_Btn.SetToolTip("Pan")
		self.Pan_Btn.Enable(False)
		self.ViewSpectrum_Btn.SetMinSize((38, 38))
		self.ViewSpectrum_Btn.SetToolTip("View Mass Spectrum")
		self.ViewSpectrum_Btn.Enable(False)
		self.config_borders_button.Enable(False)
		self.png_button.SetMinSize((45, -1))
		self.svg_button.SetMinSize((45, -1))
		self.pdf_button.SetMinSize((45, -1))
		self.save_btn.Enable(False)
		self.save_btn.SetSize(self.save_btn.GetBestSize())
		self.browse_toolbar.SetMinSize((-1, 32))
		self.radar_chart_button.SetMinSize((200, 200))
		self.mean_peak_area_button.SetMinSize((200, 200))
		self.open_project_header_browser.SetMinSize((200, 200))
		self.box_whisker_button.SetMinSize((200, 200))
		self.peak_area_button.SetMinSize((200, 200))
		self.chromatogram_button.SetMinSize((200, 200))
		self.chromatogram_canvas.SetMinSize((1, 1))
		self.data_viewer_list.AppendColumn("Time", format=wx.LIST_FORMAT_LEFT, width=80)
		self.data_viewer_list.AppendColumn("Name", format=wx.LIST_FORMAT_LEFT, width=400)
		self.data_viewer_list.AppendColumn("CAS", format=wx.LIST_FORMAT_LEFT, width=80)
		self.dv_reference_focus_thief.SetMinSize((1, 1))
		self.dv_reference_previous_btn.SetMinSize((38, 38))
		self.dv_reference_previous_btn.SetToolTip("Go back")
		self.dv_reference_previous_btn.Enable(False)
		self.dv_reference_next_btn.SetMinSize((38, 38))
		self.dv_reference_next_btn.SetToolTip("Go forward")
		self.dv_reference_next_btn.Enable(False)
		self.dv_reference_png_button.SetMinSize((45, -1))
		self.dv_reference_svg_button.SetMinSize((45, -1))
		self.dv_reference_pdf_button.SetMinSize((45, -1))
		self.dv_reference_save_btn.SetMinSize((38, 38))
		self.dv_reference_toolbar.SetMaxSize((10000000,40))
		self.dv_samples_focus_thief.SetMinSize((1, 1))
		self.dv_samples_previous_btn.SetMinSize((38, 38))
		self.dv_samples_previous_btn.SetToolTip("Go back")
		self.dv_samples_next_btn.SetMinSize((38, 38))
		self.dv_samples_next_btn.SetToolTip("Go forward")
		self.dv_samples_png_button.SetMinSize((45, -1))
		self.dv_samples_svg_button.SetMinSize((45, -1))
		self.dv_samples_pdf_button.SetMinSize((45, -1))
		self.dv_samples_save_btn.SetMinSize((38, 38))
		self.dv_samples_toolbar.SetMaxSize((10000000,40))
		self.dv_head2tail_focus_thief.SetMinSize((1, 1))
		self.dv_head2tail_previous_btn.SetMinSize((38, 38))
		self.dv_head2tail_previous_btn.SetToolTip("Go back")
		self.dv_head2tail_next_btn.SetMinSize((38, 38))
		self.dv_head2tail_next_btn.SetToolTip("Go forward")
		self.dv_head2tail_png_button.SetMinSize((45, -1))
		self.dv_head2tail_svg_button.SetMinSize((45, -1))
		self.dv_head2tail_pdf_button.SetMinSize((45, -1))
		self.dv_head2tail_save_btn.SetMinSize((38, 38))
		self.dv_head2tail_toolbar.SetMaxSize((10000000,40))
		self.data_viewer_h_splitter.SetMinimumPaneSize(40)
		self.data_viewer_v_splitter.SetMinimumPaneSize(20)
		# end wxGlade

	def __do_layout(self):
		# begin wxGlade: browse_tab.__do_layout
		browse_project_tab_sizer = wx.BoxSizer(wx.VERTICAL)
		data_viewer_sizer = wx.BoxSizer(wx.VERTICAL)
		dv_main_sizer = wx.BoxSizer(wx.HORIZONTAL)
		dv_data_sizer = wx.BoxSizer(wx.HORIZONTAL)
		dv_html_sizer = wx.BoxSizer(wx.HORIZONTAL)
		dv_spec_sizer = wx.BoxSizer(wx.VERTICAL)
		dv_head2tail_main_sizer = wx.BoxSizer(wx.VERTICAL)
		dv_head2tail_toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
		dv_head2tail_sizer = wx.BoxSizer(wx.VERTICAL)
		dv_sample_main_sizer = wx.BoxSizer(wx.VERTICAL)
		dv_samples_toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
		dv_samples_sizer = wx.BoxSizer(wx.VERTICAL)
		dv_reference_main_sizer = wx.BoxSizer(wx.VERTICAL)
		dv_reference_toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
		dv_reference_sizer = wx.BoxSizer(wx.VERTICAL)
		dv_list_sizer = wx.BoxSizer(wx.HORIZONTAL)
		browse_project_chromatogram_sizer = wx.BoxSizer(wx.VERTICAL)
		chromatogram_main_sizer = wx.BoxSizer(wx.VERTICAL)
		browse_project_charts_sizer = wx.BoxSizer(wx.VERTICAL)
		open_project_body_sizer = wx.GridSizer(2, 3, 5, 5)
		chromatogram_sizer = wx.BoxSizer(wx.VERTICAL)
		peak_area_sizer = wx.BoxSizer(wx.VERTICAL)
		box_whisker_sizer = wx.BoxSizer(wx.VERTICAL)
		open_project_header_sizer = wx.BoxSizer(wx.VERTICAL)
		mean_peak_area_sizer = wx.BoxSizer(wx.VERTICAL)
		radar_chart_sizer = wx.BoxSizer(wx.VERTICAL)
		browse_toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
		browse_toolbar_sizer.Add(self.focus_thief, 0, 0, 0)
		browse_toolbar_sizer.Add(self.CloseProject, 0, 0, 0)
		browse_toolbar_sizer.Add(self.OpenSample, 0, 0, 0)
		browse_toolbar_spacer_1 = wx.StaticLine(self.browse_toolbar, wx.ID_ANY, style=wx.LI_VERTICAL)
		browse_toolbar_sizer.Add(browse_toolbar_spacer_1, 0, wx.EXPAND, 0)
		browse_toolbar_sizer.Add(self.ViewPeakList, 0, 0, 0)
		browse_toolbar_sizer.Add(self.PreviousSample, 0, 0, 0)
		browse_toolbar_sizer.Add(self.NextSample, 0, 0, 0)
		browse_toolbar_spacer_2 = wx.StaticLine(self.browse_toolbar, wx.ID_ANY, style=wx.LI_VERTICAL)
		browse_toolbar_sizer.Add(browse_toolbar_spacer_2, 0, wx.EXPAND, 0)
		browse_toolbar_sizer.Add(self.ResetView, 0, 0, 0)
		browse_toolbar_sizer.Add(self.PreviousView, 0, 0, 0)
		browse_toolbar_sizer.Add(self.Zoom_Btn, 0, 0, 0)
		browse_toolbar_sizer.Add(self.Pan_Btn, 0, 0, 0)
		browse_toolbar_sizer.Add(self.ViewSpectrum_Btn, 0, 0, 0)
		browse_toolbar_spacer_4 = wx.StaticLine(self.browse_toolbar, wx.ID_ANY, style=wx.LI_VERTICAL)
		browse_toolbar_sizer.Add(browse_toolbar_spacer_4, 0, wx.EXPAND, 0)
		browse_toolbar_sizer.Add(self.config_borders_button, 0, wx.ALIGN_CENTER | wx.LEFT | wx.RIGHT, 5)
		browse_toolbar_spacer_5 = wx.StaticLine(self.browse_toolbar, wx.ID_ANY, style=wx.LI_VERTICAL)
		browse_toolbar_sizer.Add(browse_toolbar_spacer_5, 0, wx.EXPAND, 0)
		save_label = wx.StaticText(self.browse_toolbar, wx.ID_ANY, "Save: ")
		browse_toolbar_sizer.Add(save_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
		browse_toolbar_sizer.Add(self.png_button, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		browse_toolbar_sizer.Add(self.svg_button, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		browse_toolbar_sizer.Add(self.pdf_button, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		browse_toolbar_sizer.Add(self.save_btn, 0, 0, 0)
		browse_toolbar_sizer.Add((0, 0), 0, 0, 0)
		browse_toolbar_sizer.Add((0, 0), 0, 0, 0)
		browse_toolbar_sizer.Add((0, 0), 0, 0, 0)
		self.browse_toolbar.SetSizer(browse_toolbar_sizer)
		browse_project_tab_sizer.Add(self.browse_toolbar, 1, wx.EXPAND, 0)
		browse_project_charts_sizer.Add((0, 0), 0, 0, 0)
		radar_chart_label = wx.StaticText(self.open_project_body_panel, wx.ID_ANY, "Radar Chart", style=wx.ALIGN_CENTER)
		radar_chart_sizer.Add(radar_chart_label, 0, wx.ALIGN_CENTER_HORIZONTAL, 25)
		radar_chart_sizer.Add(self.radar_chart_button, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
		open_project_body_sizer.Add(radar_chart_sizer, 1, wx.EXPAND | wx.TOP, 10)
		mean_peak_area_label = wx.StaticText(self.open_project_body_panel, wx.ID_ANY, "Mean Peak Area")
		mean_peak_area_sizer.Add(mean_peak_area_label, 0, wx.ALIGN_CENTER_HORIZONTAL, 25)
		mean_peak_area_sizer.Add(self.mean_peak_area_button, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
		open_project_body_sizer.Add(mean_peak_area_sizer, 1, wx.EXPAND | wx.TOP, 10)
		open_project_header_info_label = wx.StaticText(self.open_project_body_panel, wx.ID_ANY, "Samples in this Project:", style=wx.ALIGN_LEFT)
		open_project_header_sizer.Add(open_project_header_info_label, 0, wx.ALIGN_CENTER_HORIZONTAL, 25)
		open_project_header_sizer.Add(self.open_project_header_browser, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 5)
		open_project_body_sizer.Add(open_project_header_sizer, 1, wx.EXPAND | wx.TOP, 10)
		box_whisker_label = wx.StaticText(self.open_project_body_panel, wx.ID_ANY, "Box & Whisker Plot", style=wx.ALIGN_CENTER)
		box_whisker_sizer.Add(box_whisker_label, 0, wx.ALIGN_CENTER_HORIZONTAL, 25)
		box_whisker_sizer.Add(self.box_whisker_button, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
		open_project_body_sizer.Add(box_whisker_sizer, 1, wx.EXPAND, 0)
		peak_area_label = wx.StaticText(self.open_project_body_panel, wx.ID_ANY, "Peak Area", style=wx.ALIGN_CENTER)
		peak_area_sizer.Add(peak_area_label, 0, wx.ALIGN_CENTER_HORIZONTAL, 25)
		peak_area_sizer.Add(self.peak_area_button, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
		open_project_body_sizer.Add(peak_area_sizer, 1, wx.EXPAND, 0)
		chromatogram_label = wx.StaticText(self.open_project_body_panel, wx.ID_ANY, "Chromatogram")
		chromatogram_sizer.Add(chromatogram_label, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
		chromatogram_sizer.Add(self.chromatogram_button, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
		open_project_body_sizer.Add(chromatogram_sizer, 1, wx.EXPAND, 0)
		self.open_project_body_panel.SetSizer(open_project_body_sizer)
		browse_project_charts_sizer.Add(self.open_project_body_panel, 7, wx.EXPAND, 10)
		self.browse_project_charts.SetSizer(browse_project_charts_sizer)
		browse_project_chromatogram_sizer.Add((0, 0), 0, 0, 0)
		chromatogram_main_sizer.Add(self.chromatogram_canvas, 1, wx.EXPAND, 0)
		self.chromatogram_parent_panel.SetSizer(chromatogram_main_sizer)
		browse_project_chromatogram_sizer.Add(self.chromatogram_parent_panel, 1, wx.EXPAND, 10)
		self.browse_project_chromatogram.SetSizer(browse_project_chromatogram_sizer)
		data_viewer_sizer.Add((0, 0), 0, 0, 0)
		dv_list_sizer.Add(self.data_viewer_list, 1, wx.EXPAND | wx.LEFT | wx.TOP, 5)
		dv_list_line = wx.StaticLine(self.dv_list_panel, wx.ID_ANY, style=wx.LI_VERTICAL)
		dv_list_sizer.Add(dv_list_line, 0, wx.EXPAND, 0)
		self.dv_list_panel.SetSizer(dv_list_sizer)
		dv_reference_sizer.Add(self.dv_reference_spec_canvas, 1, wx.EXPAND, 0)
		self.dv_reference_panel.SetSizer(dv_reference_sizer)
		dv_reference_main_sizer.Add(self.dv_reference_panel, 1, wx.EXPAND, 10)
		dv_reference_toolbar_sizer.Add(self.dv_reference_focus_thief, 0, 0, 0)
		dv_reference_toolbar_sizer.Add(self.dv_reference_previous_btn, 0, 0, 0)
		dv_reference_toolbar_sizer.Add(self.dv_reference_next_btn, 0, 0, 0)
		dv_reference_toolbar_spacer_1 = wx.StaticLine(self.dv_reference_toolbar, wx.ID_ANY, style=wx.LI_VERTICAL)
		dv_reference_toolbar_sizer.Add(dv_reference_toolbar_spacer_1, 0, wx.EXPAND, 0)
		dv_reference_save_label = wx.StaticText(self.dv_reference_toolbar, wx.ID_ANY, "Save: ")
		dv_reference_toolbar_sizer.Add(dv_reference_save_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
		dv_reference_toolbar_sizer.Add(self.dv_reference_png_button, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		dv_reference_toolbar_sizer.Add(self.dv_reference_svg_button, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		dv_reference_toolbar_sizer.Add(self.dv_reference_pdf_button, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		dv_reference_toolbar_sizer.Add(self.dv_reference_save_btn, 0, 0, 0)
		dv_reference_toolbar_spacer_2 = wx.StaticLine(self.dv_reference_toolbar, wx.ID_ANY, style=wx.LI_VERTICAL)
		dv_reference_toolbar_sizer.Add(dv_reference_toolbar_spacer_2, 0, wx.EXPAND, 0)
		self.dv_reference_toolbar.SetSizer(dv_reference_toolbar_sizer)
		dv_reference_main_sizer.Add(self.dv_reference_toolbar, 0, wx.EXPAND, 0)
		self.data_viewer_reference.SetSizer(dv_reference_main_sizer)
		dv_samples_sizer.Add(self.dv_samples_spec_canvas, 1, wx.EXPAND, 0)
		self.dv_samples_panel.SetSizer(dv_samples_sizer)
		dv_sample_main_sizer.Add(self.dv_samples_panel, 1, wx.EXPAND, 10)
		dv_samples_toolbar_sizer.Add(self.dv_samples_focus_thief, 0, 0, 0)
		dv_samples_toolbar_sizer.Add(self.dv_samples_previous_btn, 0, 0, 0)
		dv_samples_toolbar_sizer.Add(self.dv_samples_next_btn, 0, 0, 0)
		dv_samples_toolbar_spacer_1 = wx.StaticLine(self.dv_samples_toolbar, wx.ID_ANY, style=wx.LI_VERTICAL)
		dv_samples_toolbar_sizer.Add(dv_samples_toolbar_spacer_1, 0, wx.EXPAND, 0)
		dv_samples_save_label = wx.StaticText(self.dv_samples_toolbar, wx.ID_ANY, "Save: ")
		dv_samples_toolbar_sizer.Add(dv_samples_save_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
		dv_samples_toolbar_sizer.Add(self.dv_samples_png_button, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		dv_samples_toolbar_sizer.Add(self.dv_samples_svg_button, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		dv_samples_toolbar_sizer.Add(self.dv_samples_pdf_button, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		dv_samples_toolbar_sizer.Add(self.dv_samples_save_btn, 0, 0, 0)
		dv_samples_toolbar_spacer_2 = wx.StaticLine(self.dv_samples_toolbar, wx.ID_ANY, style=wx.LI_VERTICAL)
		dv_samples_toolbar_sizer.Add(dv_samples_toolbar_spacer_2, 0, wx.EXPAND, 0)
		self.dv_samples_toolbar.SetSizer(dv_samples_toolbar_sizer)
		dv_sample_main_sizer.Add(self.dv_samples_toolbar, 0, wx.EXPAND, 0)
		self.data_viewer_samples.SetSizer(dv_sample_main_sizer)
		dv_head2tail_sizer.Add(self.dv_head2tail_spec_canvas, 1, wx.EXPAND, 0)
		self.dv_head2tail_panel.SetSizer(dv_head2tail_sizer)
		dv_head2tail_main_sizer.Add(self.dv_head2tail_panel, 1, wx.EXPAND, 10)
		dv_head2tail_toolbar_sizer.Add(self.dv_head2tail_focus_thief, 0, 0, 0)
		dv_head2tail_toolbar_sizer.Add(self.dv_head2tail_previous_btn, 0, 0, 0)
		dv_head2tail_toolbar_sizer.Add(self.dv_head2tail_next_btn, 0, 0, 0)
		dv_head2tail_toolbar_spacer_1 = wx.StaticLine(self.dv_head2tail_toolbar, wx.ID_ANY, style=wx.LI_VERTICAL)
		dv_head2tail_toolbar_sizer.Add(dv_head2tail_toolbar_spacer_1, 0, wx.EXPAND, 0)
		dv_head2tail_save_label = wx.StaticText(self.dv_head2tail_toolbar, wx.ID_ANY, "Save: ")
		dv_head2tail_toolbar_sizer.Add(dv_head2tail_save_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 5)
		dv_head2tail_toolbar_sizer.Add(self.dv_head2tail_png_button, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		dv_head2tail_toolbar_sizer.Add(self.dv_head2tail_svg_button, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		dv_head2tail_toolbar_sizer.Add(self.dv_head2tail_pdf_button, 0, wx.ALIGN_CENTER_VERTICAL, 0)
		dv_head2tail_toolbar_sizer.Add(self.dv_head2tail_save_btn, 0, 0, 0)
		dv_head2tail_toolbar_spacer_2 = wx.StaticLine(self.dv_head2tail_toolbar, wx.ID_ANY, style=wx.LI_VERTICAL)
		dv_head2tail_toolbar_sizer.Add(dv_head2tail_toolbar_spacer_2, 0, wx.EXPAND, 0)
		self.dv_head2tail_toolbar.SetSizer(dv_head2tail_toolbar_sizer)
		dv_head2tail_main_sizer.Add(self.dv_head2tail_toolbar, 0, wx.EXPAND, 0)
		self.data_viewer_head2tail.SetSizer(dv_head2tail_main_sizer)
		self.data_viewer_notebook.AddPage(self.data_viewer_reference, "Reference")
		self.data_viewer_notebook.AddPage(self.data_viewer_samples, "Samples")
		self.data_viewer_notebook.AddPage(self.data_viewer_head2tail, "Head to Tail")
		dv_spec_sizer.Add(self.data_viewer_notebook, 1, wx.EXPAND, 0)
		dv_data_line = wx.StaticLine(self.dv_spec_panel, wx.ID_ANY)
		dv_spec_sizer.Add(dv_data_line, 0, wx.EXPAND, 0)
		self.dv_spec_panel.SetSizer(dv_spec_sizer)
		dv_html_sizer.Add(self.dv_html, 1, wx.EXPAND, 0)
		self.dv_html_panel.SetSizer(dv_html_sizer)
		self.data_viewer_h_splitter.SplitHorizontally(self.dv_spec_panel, self.dv_html_panel)
		dv_data_sizer.Add(self.data_viewer_h_splitter, 1, wx.EXPAND, 0)
		self.dv_data_panel.SetSizer(dv_data_sizer)
		self.data_viewer_v_splitter.SplitVertically(self.dv_list_panel, self.dv_data_panel)
		dv_main_sizer.Add(self.data_viewer_v_splitter, 1, wx.EXPAND, 0)
		self.dv_main_panel.SetSizer(dv_main_sizer)
		data_viewer_sizer.Add(self.dv_main_panel, 7, wx.EXPAND, 10)
		self.browse_project_data.SetSizer(data_viewer_sizer)
		self.browse_project_notebook.AddPage(self.browse_project_charts, "Charts")
		self.browse_project_notebook.AddPage(self.browse_project_chromatogram, "Chromatogram")
		self.browse_project_notebook.AddPage(self.browse_project_comparison, "Compare")
		self.browse_project_notebook.AddPage(self.browse_project_data, "Data")
		browse_project_tab_sizer.Add(self.browse_project_notebook, 1, wx.EXPAND, 0)
		self.SetSizer(browse_project_tab_sizer)
		browse_project_tab_sizer.Fit(self)
		self.Layout()
		# end wxGlade
	
	"""Browse Project Tab"""
	
	def on_close_project(self, event):  # wxGlade: browse_tab.<event_handler>
		self.current_project_name = None
		self._parent.notebook_1.ChangeSelection(0)
		
		self.focus_thief.SetFocus()
		self._parent.size_change(event)
		
		self.browser_sample_list = []
		self.browser_sample_idx = 0
		
		self._parent.notebook_1.SetPageText(3, "Browse Project")
		
		self.open_project_header_browser.LoadURL("about:blank")
		
		# Load Chart Data
		# self.comparison_chart_data = None
		
		# self.comparison_prefixList = []
		
		self.browser_peak_data = []
		
		event.Skip()
	
	"""Browse Project > Charts Tab Buttons"""
	
	def show_radar_chart(self, event):  # wxGlade: browse_tab.<event_handler>
		self.ChartViewer = ChartViewer.ChartViewer(self,
												   chart_type="radar",
												   initial_samples=[self.current_project],
												   # chart_data=self.chart_data,
												   # pretty_names = [self.current_project_name],
												   # sample_lists={self.current_project_name: self.current_prefixList}
												   )
		self.ChartViewer.Show()
		self.ChartViewer.Raise()
		event.Skip()
	
	def show_mean_peak_area_chart(self, event):  # wxGlade: browse_tab.<event_handler>
		self.ChartViewer = ChartViewer.ChartViewer(self,
												   chart_type="mean_peak_area",
												   initial_samples=[self.current_project],
												   # chart_data=self.chart_data,
												   # pretty_names = [self.current_project_name],
												   # sample_lists={self.current_project_name: self.current_prefixList}
												   )
		self.ChartViewer.Show()
		self.ChartViewer.Raise()
		event.Skip()
	
	def show_box_whisker_chart(self, event):  # wxGlade: browse_tab.<event_handler>
		self.ChartViewer = ChartViewer.ChartViewer(self, chart_type="box_whisker",
												   # chart_data=self.chart_data,
												   initial_samples=[self.current_project],
												   # pretty_names = [self.current_project_name],
												   # sample_lists={self.current_project_name: self.current_prefixList}
												   )
		self.ChartViewer.Show()
		self.ChartViewer.Raise()
		event.Skip()
	
	def show_peak_area_chart(self, event):  # wxGlade: browse_tab.<event_handler>
		self.ChartViewer = ChartViewer.ChartViewer(self, chart_type="peak_area",
												   initial_samples=[self.current_project],
												   # chart_data=self.chart_data,
												   # pretty_names = [self.current_project_name],
												   # sample_lists={self.current_project_name: self.current_prefixList}
												   )
		self.ChartViewer.Show()
		self.ChartViewer.Raise()
		event.Skip()
	
	def show_chromatogram(self, event):  # wxGlade: browse_tab.<event_handler>
		self.browse_project_notebook.SetSelection(1)
		event.Skip()
	
	def dv_do_save_reference(self, event):  # wxGlade: browse_tab.<event_handler>
		print("Event handler 'dv_do_save_reference' not implemented!")
		event.Skip()

	def dv_on_samples_previous(self, event):  # wxGlade: browse_tab.<event_handler>
		print("Event handler 'dv_on_samples_previous' not implemented!")
		event.Skip()

	def dv_on_samples_next(self, event):  # wxGlade: browse_tab.<event_handler>
		print("Event handler 'dv_on_samples_next' not implemented!")
		event.Skip()

	def dv_do_save_samples(self, event):  # wxGlade: browse_tab.<event_handler>
		print("Event handler 'dv_do_save_samples' not implemented!")
		event.Skip()

	def dv_on_head2tail_previous(self, event):  # wxGlade: browse_tab.<event_handler>
		print("Event handler 'dv_on_head2tail_previous' not implemented!")
		event.Skip()

	def dv_on_head2tail_next(self, event):  # wxGlade: browse_tab.<event_handler>
		print("Event handler 'dv_on_head2tail_next' not implemented!")
		event.Skip()

	def dv_do_save_head2tail(self, event):  # wxGlade: browse_tab.<event_handler>
		print("Event handler 'dv_do_save_head2tail' not implemented!")
		event.Skip()

	def browse_get_tab(self):
		return self.browse_project_notebook.GetSelection()
	
	# Toolbar Buttons
	def on_open_sample(self, event):  # wxGlade: browse_tab.<event_handler>
		# print(event.GetEventObject() == self.OpenSample) # to handle multiple buttons calling same event
		self.focus_thief.SetFocus()
		
		dlg = list_dialog.list_dialog(self, title="Choose Sample", label="Choose a sample: ",
									  choices=self.browser_sample_list)
		res = dlg.ShowModal()
		if res == wx.ID_OK:
			if self.browse_get_tab() == 1:
				# print(dlg.list_box.GetSelection())
				# print(dlg.list_box.GetString(dlg.list_box.GetSelection()))
				self.display_chromatogram(dlg.list_box.GetString(dlg.list_box.GetSelection()))
			elif self.browse_get_tab() == 2:
				coming_soon()
		
		dlg.Destroy()
		event.Skip()
	
	def on_view_peak_list(self, event):  # wxGlade: browse_tab.<event_handler>
		coming_soon()
		self.focus_thief.SetFocus()
		event.Skip()
	
	def on_previous_sample(self, event):  # wxGlade: browse_tab.<event_handler>
		self.focus_thief.SetFocus()
		
		if self.browse_get_tab() == 1:
			self.browser_sample_idx -= 1
			if self.browser_sample_idx < 0:
				self.browser_sample_idx = len(self.browser_sample_list) - 1
			
			self.display_chromatogram(self.browser_sample_list[self.browser_sample_idx])
		elif self.browse_get_tab() == 2:
			coming_soon()
		
		event.Skip()
	
	def on_next_sample(self, event):  # wxGlade: browse_tab.<event_handler>
		self.focus_thief.SetFocus()
		
		if self.browse_get_tab() == 1:
			self.browser_sample_idx += 1
			if self.browser_sample_idx > len(self.browser_sample_list) - 1:
				self.browser_sample_idx = 0
			
			self.display_chromatogram(self.browser_sample_list[self.browser_sample_idx])
		elif self.browse_get_tab() == 2:
			coming_soon()
		
		event.Skip()
	
	def on_chromatogram_reset_view(self, event):  # wxGlade: browse_tab.<event_handler>
		self.focus_thief.SetFocus()
		
		if self.browse_get_tab() == 1:
			self.chromatogram_canvas.toolbar.home()
		elif self.browse_get_tab() == 2:
			coming_soon()
		event.Skip()
	
	def on_chromatogram_previous_view(self, event):  # wxGlade: browse_tab.<event_handler>
		self.focus_thief.SetFocus()
		
		if self.browse_get_tab() == 1:
			self.chromatogram_canvas.toolbar.back()
		elif self.browse_get_tab() == 1:
			coming_soon()
		
		event.Skip()
	
	def on_chromatogram_zoom(self, event):  # wxGlade: browse_tab.<event_handler>
		self.focus_thief.SetFocus()
		
		if self.browse_get_tab() == 1:
			self.Pan_Btn.Enable()
			self.ViewSpectrum_Btn.Enable()
			self.chromatogram_canvas.toolbar.zoom()
			self.Zoom_Btn.Disable()
		if self.browse_get_tab() == 2:
			coming_soon()
		event.Skip()
	
	def on_chromatogram_pan(self, event):  # wxGlade: browse_tab.<event_handler>
		self.focus_thief.SetFocus()
		
		if self.browse_get_tab() == 1:
			self.Zoom_Btn.Enable()
			self.ViewSpectrum_Btn.Enable()
			self.chromatogram_canvas.toolbar.pan()
			self.Pan_Btn.Disable()
		elif self.browse_get_tab() == 2:
			coming_soon()
		
		event.Skip()
	
	def on_view_spectrum(self, event):  # wxGlade: browse_tab.<event_handler>
		self.focus_thief.SetFocus()
		self.Pan_Btn.Enable()
		self.Zoom_Btn.Enable()
		coming_soon()
		self.ViewSpectrum_Btn.Disable()
		event.Skip()
	
	def do_configure_borders(self, event):  # wxGlade: browse_tab.<event_handler>
		self.border_config = border_config.border_config(self, self.chromatogram_figure)
		self.border_config.Show()
	
	def do_save_chrom(self, event):  # wxGlade: browse_tab.<event_handler>
		
		self.focus_thief.SetFocus()
		
		filetypes = []
		if self.png_button.GetValue():
			filetypes.append("png")
		if self.svg_button.GetValue():
			filetypes.append("svg")
		if self.pdf_button.GetValue():
			filetypes.append("pdf")
		
		if len(filetypes) == 0:
			wx.MessageBox("Please choose one or more filetypes", "Error", wx.ICON_ERROR | wx.OK)
			return
		
		pathname = os.path.splitext(file_dialog(
			self, "*", "Save Chart", "",
			# defaultDir=self.Config.get("main", "resultspath")))[0]
			defaultDir=self._parent.Config.RESULTS_DIRECTORY))[0]
		
		# Do any of the files already exist?
		try:
			for filetype in filetypes:
				if os.path.isfile(f"{pathname}.{filetype}"):
					alert = wx.MessageDialog(
						self,
						f'A file named "{pathname}.{filetype}" already exists.\nDo you want to replace it?',
						"Overwrite File?",
						wx.ICON_QUESTION | wx.OK | wx.CANCEL
					)
					
					alert.SetOKLabel("Replace")
					if alert.ShowModal() != wx.YES:
						return
				
				self.chromatogram_figure.savefig(f"{pathname}.{filetype}")
		
		except:
			wx.LogError("Cannot save file '%s'." % pathname)
			traceback.print_exc()
	
	# Display Function
	def display_chromatogram(self, sample_name=None):
		"""
			Chromatogram Diaplay

		:param sample_name:
		:type sample_name:

		:return:
		:rtype:
		"""
		
		print(sample_name)
		
		self.Bind(wx.EVT_SIZE, self.size_change)
		self.Bind(wx.EVT_MAXIMIZE, self.size_change)
		
		self.toolbar = NavigationToolbar(self.chromatogram_canvas)
		self.toolbar.Hide()
		
		self.browse_zoom = True
		self.browse_pan = False
		self.browse_spec = False
		
		# Constrain zoom to x axis only
		# From https://stackoverflow.com/questions/16705452/matplotlib-forcing-pan-zoom-to-constrain-to-x-axes
		def press_zoom(self, event):
			event.key = 'x'
			NavigationToolbar.press_zoom(self, event)
		
		self.chromatogram_figure.canvas.toolbar.press_zoom = types.MethodType(
			press_zoom,
			self.chromatogram_figure.canvas.toolbar
		)
		
		time_list = []
		intensity_list = []
		
		display = Display(self.chromatogram_figure, self.chromatogram_axes)
		print(display.ax)
		
		if sample_name:
			self.chromatogram_axes.clear()
			# ExprDir = self.Config.get("main", "exprdir")
			ExprDir = self._parent.Config.EXPERIMENTS_DIRECTORY
			
			with open(os.path.join(ExprDir, "{}_tic.dat".format(sample_name))) as tic_file:
				ticreader = csv.reader(tic_file, delimiter=" ")
				for row in ticreader:
					row = list(filter(None, row))
					intensity_array = intensity_list.append(float(row[1]))
					time_list.append(float(row[0]))
			
			intensity_array = numpy.array(intensity_list)
			tic = IonChromatogram(intensity_array, time_list)
			
			peak_list = load_peaks(os.path.join(ExprDir, "{}_peaks.dat".format(sample_name)))
			
			display.plot_tic(tic, label=sample_name, minutes=True)
			# display.plot_peaks(filtered_peak_list, "Peaks")
			# display.do_plotting('TIC and PyMS Detected Peaks')
			# display.do_plotting(f'{sample_name} TIC')
			display.do_plotting('')
			
			y = tic.get_intensity_array()
			x = [time / 60 for time in tic.get_time_list()]
			
			self.chromatogram_axes.set_xlim(left=0, right=max(x))
		
		else:
			self.chromatogram_axes.text(
				0.5,
				0.5,
				"Please select a Project",
				horizontalalignment="center",
				fontsize='32',
				transform=self.chromatogram_axes.transAxes
			)
		
		self.chromatogram_axes.set_ylim(bottom=0)
		self.chromatogram_axes.set_xlabel("Retention Time")
		self.chromatogram_axes.set_ylabel("Intensity")
		
		self.chromatogram_figure.subplots_adjust(left=0.1, bottom=0.125, top=0.9, right=0.97)
		# figure.tight_layout()
		self.chromatogram_canvas.draw()
		
		# def on_xlims_change(ax):
		def update_ylim(*args):
				# print(*args)
				# print(str(*args).startswith("MPL MouseEvent")) # Pan
			if (str(*args).startswith("My_AxesSubplot") and not self.Zoom_Btn.IsEnabled()) or (
					str(*args).startswith("MPL MouseEvent") and not self.Pan_Btn.IsEnabled()):  # Zoom, Pan
					# print("updated xlims: ", axes.get_xlim())
				min_x_index = (numpy.abs(x - self.chromatogram_axes.get_xlim()[0])).argmin()
				max_x_index = (numpy.abs(x - self.chromatogram_axes.get_xlim()[1])).argmin()
					# print(min_x_index, max_x_index)
				
				y_vals_for_range = numpy.take(y, [idx for idx in range(min_x_index, max_x_index)])
					# print(max(y_vals_for_range))
				self.chromatogram_axes.set_ylim(bottom=0, top=max(y_vals_for_range) * 1.1)
				self.chromatogram_figure.canvas.draw()
					# print("x-val: {}, y-val:{}
				self.size_change(0)
		
		self.chromatogram_axes.callbacks.connect('xlim_changed', update_ylim)
		self.chromatogram_figure.canvas.callbacks.connect("button_release_event", update_ylim)
	
	# Other Toolbar Options
	# Save chromatogram as image: save_figure(self, *args)
	# set_cursor(self, cursor)
	# Set the current cursor to one of the :class:`Cursors` enums values.
	
	# If required by the backend, this method should trigger an update in
	# the backend event loop after the cursor is set, as this method may be
	# called e.g. before a long-running task during which the GUI is not
	# updated.
	# set_history_buttons(self)
	# Enable or disable the back/forward button.
	# forward(self, *args)
	# move forward in the view lim stack.
	# print(axes.get_ylim())
	
	
	"""Data Viewer"""
	
	def populate_data_viewer(self):
		self.data_viewer_list.DeleteAllItems()
		
		for peak in self.browser_peak_data:
			print(list(peak))
			print(list(peak["hits"][0]))
			self.data_viewer_list.Append(
				[rounders(peak["average_rt"], "0.000"), peak["hits"][0]["Name"], peak["hits"][0]["CAS"]])
	
	def do_select_peak(self, event):  # wxGlade: browse_tab.<event_handler>
		dv_selection = self.data_viewer_list.GetFocusedItem()
		self.dv_selection_data = self.browser_peak_data[dv_selection]
		
		CAS = self.dv_selection_data["hits"][0]["CAS"]
		
		data_path = os.path.join(
				self._parent.Config.CSV_DIRECTORY,
				"{}_peak_data.json".format(
					self.current_project_name)
			).replace("&", "%26")
		
		samples = "/".join(self.browser_sample_list)
		self.dv_url = f"http://localhost:5000/{samples}?filename={data_path}&index={dv_selection}"
		
		if os.path.isfile(os.path.join("cache", CAS)):
			self.Data_Viewer_Ready()
		else:
			data_getter = threads.FlaskThread(self, self.dv_url)
			data_getter.start()
			# self.dv_html.LoadURL("http://webkit.org/blog-files/bounce.html")
			# self.dv_html.LoadURL(f"http://localhost:5000/loader?url={self.dv_url}")
			self.dv_html.LoadURL(f"file://{os.path.join(os.getcwd(), 'lib', 'loading.html')}")
		return
	
	def Data_Viewer_Ready(self, *args):
		if self.dv_html.GetCurrentURL() != self.dv_url:
			self.dv_html.LoadURL(self.dv_url)
		
	def on_browse_tab_change(self, event):  # wxGlade: browse_tab.<event_handler>
		print(event.GetSelection())
		controls = [self.OpenSample, self.PreviousSample, self.NextSample, self.ResetView, self.PreviousView,
					self.Zoom_Btn, self.Pan_Btn, self.config_borders_button, self.save_btn]
		if event.GetSelection() in [1, 2]:
			for control in controls:
				control.Enable()
			if event.GetSelection() == 1:
				self.ViewSpectrum_Btn.Enable()
		else:
			for control in controls + [self.ViewSpectrum_Btn]:
				control.Enable(False)
		
		event.Skip()
	
	def size_change(self, event):
		# code to run whenever window resized
		self.chromatogram_canvas.draw()
		self.chromatogram_canvas.Refresh()
		if type(event) == wx._core.SizeEvent:
			event.Skip()
	
	def setup_browser(self, selected_project):
		self.current_project = selected_project
		self.current_project_name = os.path.splitext(os.path.split(selected_project)[-1])[0]
		
		self._parent.notebook_1.SetPageText(3, self.current_project_name)
		
		self.open_project_header_browser.LoadURL("file://{}".format(selected_project))
		
		with open(selected_project, "r") as f:
			self.current_prefixList = [x.rstrip("\r\n") for x in f.readlines()]
		# print(self.current_prefixList)
		
		self.browser_sample_list = self.current_prefixList
		
		self.browser_sample_idx = 0
		# print(self.browser_sample_list)
		# print(self.browser_sample_list[self.browser_sample_idx])
		
		# Show chromatogram for first sample
		self.display_chromatogram(self.browser_sample_list[self.browser_sample_idx])
		
		with open(os.path.join(
					self._parent.Config.CSV_DIRECTORY,
					"{}_peak_data.json".format(
						self.current_project_name)
				), "r") as jsonfile:
			for peak in jsonfile.readlines():
				self.browser_peak_data.append(json.loads(peak))
		
		self.populate_data_viewer()
	
	def setup_project_browser(self,*args, **kwargs):
		self.setup_browser(*args, **kwargs)


# end of class browse_tab
