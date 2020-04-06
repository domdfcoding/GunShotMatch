#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  notebook.py
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
import wx.aui
import wx.html2
from pubsub import pub

# this package
from GuiV2.GSMatch2_Core import Experiment, Project
from GuiV2.GSMatch2_Core.GUI.events import (
	EVT_REMOVE_PROJECT, EVT_SWITCH_COMPOUNDS_CONTENT_REQ, EVT_SWITCH_EXPR_CONTENT_REQ, EVT_SWITCH_PROJ_CONTENT_REQ,
	EVT_SWITCH_PROJ_REQ,
	)
from GuiV2.GSMatch2_Core.GUI.welcome_page import render_welcome_page

#
# use_cefpython = False
#
# if "gtk2" in wx.version():
# 	use_cefpython = False
#
# if use_cefpython:
# 	from GuiV2.GSMatch2_Core.GUI.CefBrowser import init_cefpython, BrowserPanel
#
# 	cef = init_cefpython


class Notebook(wx.aui.AuiNotebook):
	def __init__(
			self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
			style=wx.aui.AUI_NB_TOP | wx.aui.AUI_NB_TAB_SPLIT | wx.aui.AUI_NB_TAB_MOVE |
				  wx.aui.AUI_NB_SCROLL_BUTTONS | wx.aui.AUI_NB_CLOSE_ON_ACTIVE_TAB | wx.aui.AUI_NB_MIDDLE_CLICK_CLOSE
			):
		self.parent = parent
		self.id = id
		wx.aui.AuiNotebook.__init__(self, parent, id, pos, size, style)
		
		self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.on_close_tab)
		# self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSED, self.on_close_tab)
		self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.on_nb_sel_changed)
		
		EVT_SWITCH_PROJ_REQ.set_receiver(self)
		EVT_SWITCH_PROJ_REQ.Bind(self.on_request_switch_project)
	
		EVT_SWITCH_PROJ_CONTENT_REQ.set_receiver(self)
		EVT_SWITCH_PROJ_CONTENT_REQ.Bind(self.on_request_switch_content)
		
		EVT_SWITCH_EXPR_CONTENT_REQ.set_receiver(self)
		EVT_SWITCH_EXPR_CONTENT_REQ.Bind(self.on_request_switch_experiment)
		
		EVT_SWITCH_COMPOUNDS_CONTENT_REQ.set_receiver(self)
		EVT_SWITCH_COMPOUNDS_CONTENT_REQ.Bind(self.on_request_switch_compounds)

		# Welcome Page
		# if use_cefpython:
		# 	page = BrowserPanel(f"file://{render_welcome_page()}", self, style=wx.WANTS_CHARS)
		# 	wx.CallLater(100, page.embed_browser)
		# else:
		page = wx.html2.WebView.New(self, wx.ID_ANY, size=(400, 300))
		page.LoadURL(f"file://{render_welcome_page()}")
		
		self.AddPage(page, "Welcome")
		
		wx.CallAfter(self.SendSizeEvent)
	
	def on_request_switch_project(self, event):
		self.switch_to_project(event.GetValue())
		
	def on_request_switch_content(self, event):
		self.switch_to_project_content(*event.GetValue())
		
	def on_request_switch_experiment(self, event):
		self.switch_to_experiment_content(*event.GetValue())
		
	def on_request_switch_compounds(self, event):
		self.switch_to_compounds_content(*event.GetValue())
	
	def add_project(self, project):
		# TODO?: Check if project already in notebook
		page = Project.ProjectDataPanel(self, project)
		# self.notebook.AddPage(page, "Eley Contact Propellant")
		self.AddPage(page, project.name)
		self.select_last_page()
		return page
	
	def on_close_tab(self, event):
		# Close button on tab clicked or tab middle clicked
		event.Veto()
		closed_tab_idx = event.GetOldSelection()
		project_panel = self.GetPage(closed_tab_idx)
		self.remove_project(project_panel, closed_tab_idx)
	
	def remove_project(self, project_panel=None, closed_tab_idx=None):
		if not project_panel:
			closed_tab_idx = self.GetSelection()
			project_panel = self.GetPage(closed_tab_idx)
		
		project_name = project_panel.name
		
		if project_name != "Welcome":
			
			if project_panel.save_changes():
				self.DeletePage(closed_tab_idx)
				EVT_REMOVE_PROJECT.value = project_name
				EVT_REMOVE_PROJECT.trigger()
				del self.parent.opened_projects[project_name]
	
	def select_last_page(self):
		self.SetSelection(self.PageCount-1)
	
	def get_selected_page(self):
		sel = self.GetSelection()
		
		if sel != -1:
			return self.GetPage(sel)
	
	def get_selected_page_text(self):
		sel = self.GetSelection()
		
		if sel != -1:
			return self.GetPageText(sel)
	
	def get_selected_project(self):
		sel = self.GetSelection()
		
		if sel != -1:
			return self.get_project_by_index(sel)
	
	def get_selected_project_panel(self):
		sel = self.GetSelection()
		
		if sel != -1:
			return self.get_project_panel_by_index(sel)
	
	def get_page_by_index(self, index):
		return self.GetPage(index)
	
	def get_project_panel_by_index(self, index):
		if isinstance(self.GetPage(index), Project.ProjectDataPanel):
			return self.GetPage(index)
	
	def get_project_by_index(self, index):
		if isinstance(self.GetPage(index), Project.ProjectDataPanel):
			return self.GetPage(index).project
	
	def iter_project_panels(self):
		for tab_idx in range(self.GetPageCount()):
			page = self.get_page_by_index(tab_idx)
			if isinstance(page, Project.ProjectDataPanel):
				yield page
	
	def switch_to_project(self, project_name):
		"""
		Switch the notebook focus to the desired project

		:param project_name:
		:type project_name:

		:return: The index of the tab representing the desired project
		:rtype: int
		"""
		
		print(project_name)
		for tab_idx in range(self.PageCount):
			if self.GetPageText(tab_idx) != "Welcome":
				if self.GetPage(tab_idx).name == project_name:
					self.SetSelection(tab_idx)
					return tab_idx
	
	def on_nb_sel_changed(self, _):
		# print("Notebook Sel Changed")
		# print(self.get_selected_page())
		
		if isinstance(self.get_selected_page(), Project.ProjectDataPanel):
			# print(self.get_selected_page().get_selected_page())
			
			if isinstance(self.get_selected_page().get_selected_page(), Experiment.ExperimentDataPanel):
				# print(self.get_selected_page().get_selected_page().get_selected_page())
				
				pub.sendMessage("toggle_expr_tools", enable=True)
				
				if self.get_selected_page().get_selected_page().get_selected_page_text() == "TIC":
					pub.sendMessage("toggle_view_tools", enable=True)
				else:
					pub.sendMessage("toggle_view_tools", enable=False)
					
			elif isinstance(self.get_selected_page().get_selected_page(), Project.CompoundsDataPanel) \
				and isinstance(self.get_selected_page().get_selected_page().get_selected_page(), Project.DataViewer):
				
				pub.sendMessage("toggle_expr_tools", enable=True)
				pub.sendMessage("toggle_view_tools", enable=True)
				
			else:
				pub.sendMessage("toggle_view_tools", enable=False)
				pub.sendMessage("toggle_expr_tools", enable=False)
		else:
			# # Welcome Page
			# if use_cefpython:
			# 	page = self.get_selected_page()
			# 	if isinstance(page, BrowserPanel):
			# 		if self.GetHandle():
			# 			page.embed_browser(self)
			
			pub.sendMessage("toggle_view_tools", enable=False)
			pub.sendMessage("toggle_expr_tools", enable=False)
		
		pub.sendMessage("refresh_menus")
		
		wx.CallAfter(self.freeze_hidden_tabs)
		
		# Ask GunShotMatch to check whether project has alignment, ident, consolidate etc data and disable menu options
		
	def freeze_hidden_tabs(self):
		# print(self.get_selected_page_text())
		for page_idx in range(self.GetPageCount()):
			# print(self.GetPageText(page_idx))
			if self.GetPage(page_idx).IsShownOnScreen():
				if self.GetPage(page_idx).IsFrozen():
					self.GetPage(page_idx).Thaw()
			else:
				if not self.GetPage(page_idx).IsFrozen():
					self.GetPage(page_idx).Freeze()
	
	def update_titles(self, event=None):
		current_project_idx = self.GetSelection()
		current_project_panel = self.GetPage(current_project_idx)
		if current_project_panel.project.unsaved_changes:
			self.SetPageText(current_project_idx, f"{current_project_panel.project.name}*")
		else:
			self.SetPageText(current_project_idx, current_project_panel.project.name)
		
		current_project_panel.refresh_date_modified_value()
	
	def switch_to_project_content(self, project, page_title):
		# Switch notebook to that project and switch the next notebook to the info tab
		tab_idx = self.switch_to_project(project)
		project_panel = self.GetPage(tab_idx)
		p_tab_idx = project_panel.switch_to_content(page_title)
		return tab_idx, p_tab_idx
	
	def switch_to_experiment_content(self, project, expr_name, page_title):
		# Switch notebook to the specified project, experiment and page
		tab_idx = self.switch_to_project(project)
		project_panel = self.GetPage(tab_idx)
		p_tab_idx, e_tab_idx = project_panel.switch_to_experiment_content(expr_name, page_title)
		return tab_idx, p_tab_idx, e_tab_idx
	
	def switch_to_compounds_content(self, project, page_title):
		# Switch notebook to the specified project, then the Comppunds tab, and finally the specified page
		tab_idx = self.switch_to_project(project)
		project_panel = self.GetPage(tab_idx)
		p_tab_idx, c_tab_idx = project_panel.switch_to_compounds_content(page_title)
		return tab_idx, p_tab_idx, c_tab_idx
	
	def _pass_through_view_event(self, method):
		selected_page = self.get_selected_project_panel().get_selected_page()
		
		if isinstance(selected_page, Experiment.ExperimentDataPanel):
			attr = getattr(selected_page.experiment_tic, method)
			attr()
		
		elif isinstance(selected_page, Project.CompoundsDataPanel):
			if isinstance(selected_page.get_selected_page(), Project.DataViewer):
				attr = getattr(selected_page.get_selected_page(), method)
				attr()
		
		else:
			return
			
	def on_reset_view(self, event):  # wxGlade: GunShotMatch.<event_handler>
		self._pass_through_view_event("reset_view")
		event.Skip()
	
	def on_previous_view(self, event):  # wxGlade: GunShotMatch.<event_handler>
		self._pass_through_view_event("previous_view")
		event.Skip()
		
	def on_rescale_y(self, event):
		self._pass_through_view_event("rescale_y")
		event.Skip()
		
	def on_rescale_x(self, event):
		self._pass_through_view_event("rescale_x")
		event.Skip()
	
	def on_spectrum_scan(self, _):  # wxGlade: GunShotMatch.<event_handler>
		if not isinstance(self.get_selected_page(), Project.ProjectDataPanel):
			# Project not currently selected
			return
		
		self.get_selected_page().view_spectrum_by_scan()
	
	def on_spectrum_rt(self, _):  # wxGlade: GunShotMatch.<event_handler>
		if not isinstance(self.get_selected_page(), Project.ProjectDataPanel):
			# Project not currently selected
			return
		
		self.get_selected_page().view_spectrum_by_rt()
