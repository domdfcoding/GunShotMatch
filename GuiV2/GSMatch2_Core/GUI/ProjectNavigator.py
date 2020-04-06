#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  ProjectNavigator.py
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
from pubsub import pub

# this package
from GuiV2.GSMatch2_Core.GUI.events import (
	EVT_REMOVE_PROJECT, EVT_SWITCH_COMPOUNDS_CONTENT_REQ,
	EVT_SWITCH_EXPR_CONTENT_REQ, EVT_SWITCH_PROJ_CONTENT_REQ, EVT_SWITCH_PROJ_REQ,
	)
from GuiV2.icons import get_icon


class ProjectNavigator(wx.TreeCtrl):
	def __init__(
			self, parent, id, pos=wx.Point(0, 0), size=wx.Size(160, 250),
			style=wx.TR_DEFAULT_STYLE | wx.NO_BORDER | wx.TR_HIDE_ROOT,
			validator=wx.DefaultValidator, name="Project Navigator TreeCtrl",
			):
		
		self.parent = parent
		self.id = id
		wx.TreeCtrl.__init__(self, parent, id, pos, size, style, validator, name)
		
		# Setup Icons
		self.setup_image_list()
		
		self.project_navigator_data = {"__root": self.AddRoot('')}
		
		self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_selection_changed)
		self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_selection_changed)
		pub.subscribe(self.remove_alignment, "remove_alignment")
		pub.subscribe(self.remove_identify, "remove_identify")
		pub.subscribe(self.on_ident_performed, "on_ident_performed")
		pub.subscribe(self.remove_consolidate, "remove_consolidate")
		pub.subscribe(self.on_consolidate_performed, "on_consolidate_performed")
		pub.subscribe(self.on_alignment_performed, "on_alignment_performed")
		
		EVT_REMOVE_PROJECT.set_receiver(self)
		EVT_REMOVE_PROJECT.Bind(self.remove_project)
	
	def setup_image_list(self):
		self.imglist = wx.ImageList(16, 16, True, 2)
		
		self.proj_collapsed_icon = self.imglist.Add(get_icon(wx.ART_FOLDER, 16))  # 0
		self.proj_expanded_icon = self.imglist.Add(get_icon(wx.ART_FILE_OPEN, 16))  # 1
		self.info_icon = self.imglist.Add(get_icon(wx.ART_INFORMATION, 16))  # 2
		self.method_icon = self.imglist.Add(get_icon("method", 16))  # 3 - don't move
		self.peak_list_icon = self.imglist.Add(get_icon(wx.ART_LIST_VIEW, 16))  # 4
		self.data_icon = self.imglist.Add(get_icon(wx.ART_EXECUTABLE_FILE, 16))  # 5
		self.tic_icon = self.imglist.Add(get_icon("chromatogram", 16))  # 6
		self.ammo_icon = self.imglist.Add(get_icon("ammo-details", 16))  # 7 - don't move
		self.alignment_icon = self.imglist.Add(get_icon(wx.ART_LIST_VIEW, 16))  # 8
		self.compounds_icon = self.imglist.Add(get_icon("Conical_flask_red", 16))  # 9
		self.expr_icon = self.imglist.Add(get_icon(wx.ART_REPORT_VIEW, 16))  # 10
		self.consolidate_icon = self.imglist.Add(get_icon("Merge-arrows-3", 16))  # 11
		
		self.AssignImageList(self.imglist)
	
	def on_selection_changed(self, _):
		focused_item = self.GetFocusedItem()
		selection = self.GetItemText(focused_item)
		
		if selection in self.project_navigator_data:
			# project selected, show it on the screen
			EVT_SWITCH_PROJ_REQ.value = selection
			EVT_SWITCH_PROJ_REQ.trigger()
		
		else:
			
			for project, project_data in self.project_navigator_data.items():
				if project == "__root":
					continue
				
				if focused_item in {
						project_data["info"],
						project_data["ammo_details"],
						project_data["alignment_data"],
						project_data["compounds"],
						}:
					# Project info selected
					# Switch notebook to that project and switch the next notebook to the info tab
					EVT_SWITCH_PROJ_CONTENT_REQ.value = (project, selection)
					EVT_SWITCH_PROJ_CONTENT_REQ.trigger()
					# print(f"Switching to {focused_item}")
					break
				
				elif focused_item == project_data["method"]:
					# Project info selected
					# Switch notebook to that project and switch the next notebook to the info tab
					EVT_SWITCH_PROJ_CONTENT_REQ.value = (project, "Method")
					EVT_SWITCH_PROJ_CONTENT_REQ.trigger()
					break
				
				elif focused_item in {
						project_data["single_peak"],
						project_data["consolidated"],
						}:
					EVT_SWITCH_COMPOUNDS_CONTENT_REQ.trigger((project, selection))
				
				else:
					for experiment, experiment_data in project_data["experiments"].items():
						
						if focused_item == experiment:
							EVT_SWITCH_PROJ_CONTENT_REQ.trigger((project, experiment_data["expr_name"]))
							break
						else:
							if focused_item == experiment_data["data"]:
								# load the experiment data
								pass
							elif focused_item in {
									experiment_data["tic"],
									experiment_data["peaks"],
									experiment_data["method"],
									experiment_data["compounds"],
									# TODO: EICs
									}:
								EVT_SWITCH_EXPR_CONTENT_REQ.trigger((project, experiment_data["expr_name"], selection))
								
	def add_project(self, project):
		tree_root = self.project_navigator_data["__root"]
		
		# Add Project name to top level
		tree_project = self.AppendItem(tree_root, project.name)
		self.SetItemImage(tree_project, self.proj_collapsed_icon, which=wx.TreeItemIcon_Normal)
		self.SetItemImage(tree_project, self.proj_expanded_icon, which=wx.TreeItemIcon_Expanded)
		self.project_navigator_data[project.name] = {}
		self.project_navigator_data[project.name]["project"] = project
		self.project_navigator_data[project.name]["alignment_data"] = None
		self.project_navigator_data[project.name]["consolidated"] = None
		self.project_navigator_data[project.name]["single_peak"] = None
		self.project_navigator_data[project.name]["tree_project"] = tree_project
		
		# Add project info below Project Name
		tree_project_info = self.AppendItem(tree_project, "Project Info", self.info_icon)
		self.project_navigator_data[project.name]["info"] = tree_project_info
		
		# Add project method below Project Name
		tree_project_info = self.AppendItem(tree_project, *project.method.tree_item)
		self.project_navigator_data[project.name]["method"] = tree_project_info
		
		# Add project Ammunition Details below Project Name
		tree_project_info = self.AppendItem(tree_project, *project.ammo_details.tree_item)
		self.project_navigator_data[project.name]["ammo_details"] = tree_project_info
		
		# Add experiments below Project name
		self.project_navigator_data[project.name]["experiments"] = {}
		
		for experiment in project.experiment_objects:
			name = self.AppendItem(tree_project, experiment.name, self.expr_icon)
			expr = self.AppendItem(name, "Data", self.data_icon)
			tic = self.AppendItem(name, "TIC", self.tic_icon)
			peaks = self.AppendItem(name, "Peak List", self.peak_list_icon)
			# info = self.project_navigator.AppendItem(name, "Experiment Info", self.info_icon)
			method = self.AppendItem(name, "Method", self.method_icon)
			
			self.project_navigator_data[project.name]["experiments"][name] = {
					"expr_name": experiment.name,
					"data": expr,
					"tic": tic,
					"peaks": peaks,
					"method": method,
					"compounds": None
					}
		
		if project.alignment_performed:
			self.add_alignment(project)
		
		# Add Compounds below Alignment Data
		self.project_navigator_data[project.name]["compounds"] = {}
		compounds_category = self.AppendItem(tree_project, "Compounds", self.compounds_icon)
		
		self.project_navigator_data[project.name]["compounds"] = compounds_category
		
		for experiment in project.experiment_objects:
			if experiment.identification_performed:
				self.add_experiment_identify(project, experiment)
		
		if any(experiment.identification_performed for experiment in project.experiment_objects):
			self.add_project_identify(project)
		
		if project.consolidate_performed:
			self.add_consolidate(project)
		
		self.Expand(tree_project)
		
	def remove_project(self, event):
		self.Delete(self.project_navigator_data[event.GetValue()]["tree_project"])
		event.Skip()
	
	def on_alignment_performed(self, project):
		self.add_alignment(project)
		
	def add_alignment(self, project):
		if not project.alignment_performed:
			raise ValueError("Alignment must be performed first")
		
		tree_project = self.project_navigator_data[project.name]["tree_project"]
		
		# Add project Alignment Data below Project Name
		tree_project_info = self.AppendItem(tree_project, "Alignment Data", self.alignment_icon)
		self.project_navigator_data[project.name]["alignment_data"] = tree_project_info
	
	def remove_alignment(self, project):
		"""
		Remove alignment entry for the project that triggered the event
		"""
		
		self.Delete(self.project_navigator_data[project]["alignment_data"])
		
	def on_ident_performed(self, project):
		for experiment in project.experiment_objects:
			self.add_experiment_identify(project, experiment)
		self.add_project_identify(project)
	
	def add_experiment_identify(self, project, experiment):
		if not experiment.identification_performed:
			raise ValueError("Compound Identification must be performed first")
		
		for tree_expr, data in self.project_navigator_data[project.name]["experiments"].items():
			if data["expr_name"] == experiment.name:
				data["compounds"] = self.AppendItem(tree_expr, "Compounds", self.compounds_icon)
	
	def add_project_identify(self, project):
		if not any(experiment.identification_performed for experiment in project.experiment_objects):
			raise ValueError("Compound Identification must be performed first")
		
		compounds_category = self.project_navigator_data[project.name]["compounds"]
		
		single_peak = self.AppendItem(compounds_category, "Single Peak", self.tic_icon)
		self.project_navigator_data[project.name]["single_peak"] = single_peak
		
	def remove_identify(self, project):
		"""
		Remove compound identification entry for the project that triggered the event
		
		:param project: The name of the project to remove the compound identification data from
		:type project:
		
		:return:
		:rtype:
		"""
		
		for experiment, data in self.project_navigator_data[project]["experiments"].items():
			self.Delete(data["compounds"])
		self.Delete(self.project_navigator_data[project]["single_peak"])
	
	def on_consolidate_performed(self, project):
		self.add_consolidate(project)
		
	def add_consolidate(self, project):
		if not project.alignment_performed:
			raise ValueError("Alignment must be performed first")
		
		if not any(experiment.identification_performed for experiment in project.experiment_objects):
			raise ValueError("Compound Identification must be performed first")
		
		compounds_category = self.project_navigator_data[project.name]["compounds"]
		
		consolidated = self.AppendItem(compounds_category, "Consolidated", self.consolidate_icon)
		self.project_navigator_data[project.name]["consolidated"] = consolidated
		
		data = self.AppendItem(compounds_category, "Data", self.data_icon)
		self.project_navigator_data[project.name]["data"] = data
		
	def remove_consolidate(self, project):
		"""
		Remove consolidate entry for the project that triggered the event
		
		:param project: The name of the project to remove the consolidate data from
		:type project:
		
		:return:
		:rtype:
		"""
		
		self.Delete(self.project_navigator_data[project]["consolidated"])
		self.Delete(self.project_navigator_data[project]["data"])
