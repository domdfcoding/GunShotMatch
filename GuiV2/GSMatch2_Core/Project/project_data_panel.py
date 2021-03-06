#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  project_data_panel.py
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
#
# generated by wxGlade 0.9.3 on Wed Dec  4 09:44:16 2019
#

# stdlib
import datetime
import multiprocessing
import threading
import warnings

# 3rd party
import wx
import wx.propgrid
from domdf_wxpython_tools import FloatEntryDialog, IntEntryDialog
from pubsub import pub

# this package
from GuiV2.GSMatch2_Core import Ammunition, Experiment, Project
from GuiV2.GSMatch2_Core.Ammunition import ammo_images
from GuiV2.GSMatch2_Core.Base import ProjExprPanelBase
from GuiV2.GSMatch2_Core.GUI.events import EVT_PROJECT_CHANGE
from GuiV2.GSMatch2_Core.GUI.prog_dialog_indeterminate import AnimatedProgDialog


class ProjectDataPanel(ProjExprPanelBase):
	"""
	Notebook tab to contain all of the information for a project
	"""
	
	def __init__(
			self, parent, project, id=wx.ID_ANY,
			pos=wx.DefaultPosition, size=wx.DefaultSize,
			style=0, name="ProjectDataPanel"):
		"""
		:param parent: The parent window.
		:type parent: wx.Window
		:param project:
		:type project:
		:param id: An identifier for the panel. wx.ID_ANY is taken to mean a default.
		:type id: wx.WindowID, optional
		:param pos: The panel position. The value wx.DefaultPosition indicates a default position, chosen by either the windowing system or wxWidgets, depending on platform.
		:type pos: wx.Point, optional
		:param size: The panel size. The value wx.DefaultSize indicates a default size, chosen by either the windowing system or wxWidgets, depending on platform.
		:type size: wx.Size, optional
		:param style: The window style. See wxPanel.
		:type style: int, optional
		:param name: Window name.
		:type name: str, optional
		"""
		
		self.project = project
		
		ProjExprPanelBase.__init__(self, parent, id=id, pos=pos, size=size, style=style | wx.TAB_TRAVERSAL, name=name)
		
		self.project_info = Project.ProjectInfoPanel(self, self.project, self.notebook, wx.ID_ANY)
		self.notebook.AddPage(self.project_info, "Project Info")
		
		# Make tabs
		self.method_tab = None
		self.make_method_tab()
		
		self.project_ammo = None
		self.make_ammo_tab()
		
		self.experiment_pages = {}
		
		# Add Experiments
		for experiment in self.project.experiment_objects:
			experiment_page = Experiment.ExperimentDataPanel(experiment, self.notebook, wx.ID_ANY)
			self.notebook.AddPage(experiment_page, experiment.name)
			self.experiment_pages[experiment.name] = experiment_page
		
		self.alignment_page = None
		if self.project.alignment_performed:
			self.create_alignment_page()
		
		# self.ident_panel = None
		# if any(experiment.identification_performed for experiment in self.project.experiment_objects):
		# 	self.add_ident_tab()
		
		self.compounds_tab = Project.CompoundsDataPanel(self)
		self.notebook.AddPage(self.compounds_tab, "Compounds")
		
		# self.consolidate_panel = None
		# if self.project.consolidate_performed:
		# 	self.add_consolidate_tab()
		
		for page_idx in range(self.notebook.PageCount):
			if self.notebook.GetPageText(page_idx) == "Project Info":
				self.notebook.SetSelection(page_idx)
				break
		else:
			self.notebook.SetSelection(0)
		
		self._bind_events()
		
		self.project._unsaved_changes = False
		self.project.ammo_details_unsaved = False
		self.project.method_unsaved = False

	def _bind_events(self):
		self.Bind(wx.propgrid.EVT_PG_CHANGED, self.on_method_changed, self.method_tab.property_grid_1)
		self.Bind(wx.propgrid.EVT_PG_CHANGED, self.on_ammo_details_changed, self.project_ammo.ammo_details_grid)
		self.Bind(ammo_images.EVT_IMAGE_PANEL_CHANGED, self.on_ammo_details_changed, self.project_ammo.propellant_image)
		self.Bind(ammo_images.EVT_IMAGE_PANEL_CHANGED, self.on_ammo_details_changed, self.project_ammo.headstamp_image)
		self.Bind(ammo_images.EVT_IMAGE_ADDED, self.on_ammo_details_changed, self.project_ammo.other_images)
		self.Bind(ammo_images.EVT_IMAGE_RENAMED, self.on_ammo_details_changed, self.project_ammo.other_images)
		self.Bind(ammo_images.EVT_IMAGE_DELETED, self.on_ammo_details_changed, self.project_ammo.other_images)
		self.Bind(wx.propgrid.EVT_PG_CHANGED, self.on_project_info_changed, self.project_info.property_grid)
		pub.subscribe(self.display_compounds_for_peak, "display_compounds_for_peak")
		pub.subscribe(self.view_in_dataviewer, "view_in_dataviewer")
		pub.subscribe(self.view_peak_in_expr, "view_peak_in_expr")
		pub.subscribe(self.view_peak_in_consolidated, "view_peak_in_consolidated")
		
	def display_compounds_for_peak(self, peak_number):
		if not hasattr(self, "compounds_tab") or not hasattr(self.compounds_tab, "ident_panel"):
			wx.MessageBox("`Compound Identification` must be performed first!", "Error!", style=wx.OK | wx.ICON_ERROR)
			return
		
		if peak_number not in self.compounds_tab.ident_panel.peak_numbers:
			wx.MessageBox(
					"The selected peak has not had `Compound Identification` performed for it.",
					"Warning",
					style=wx.OK | wx.ICON_WARNING,
					)
			return
		
		self.switch_to_content("Compounds 2")
		self.compounds_tab.show_single_peak(peak_number)
		
	def view_in_dataviewer(self, peak_number):
		if not hasattr(self, "compounds_tab") or not hasattr(self.compounds_tab, "ident_panel"):
			wx.MessageBox("`Compound Identification` must be performed first!", "Error!", style=wx.OK | wx.ICON_ERROR)
			return
		
		if peak_number not in self.compounds_tab.ident_panel.peak_numbers:
			wx.MessageBox(
					"The selected peak has not had `Compound Identification` performed for it.",
					"Warning",
					style=wx.OK | wx.ICON_WARNING,
					)
			return
		
		self.switch_to_content("Compounds 2")
		self.compounds_tab.view_in_dataviewer(peak_number)
		
	def view_peak_in_expr(self, peak_number, expr_name):
		print("view_peak_in_expr")
		print(expr_name)
		tab_idx, e_tab_idx = self.switch_to_experiment_content(expr_name, "Compounds")
		self.get_page_by_index(tab_idx).get_page_by_index(e_tab_idx).select_peak(peak_number)
		
	def view_peak_in_consolidated(self, peak_number):
		print("view_peak_in_consolidated")
		tab_idx, c_tab_idx = self.switch_to_compounds_content("Consolidated")
		self.get_page_by_index(tab_idx).get_page_by_index(c_tab_idx).select_peak(peak_number)
		
	def create_alignment_page(self):
		"""
		Create the page for the Alignment data
		"""

		if not self.project.alignment_performed:
			raise ValueError("Alignment must be performed first")
			
		self.alignment_page = Project.AlignmentDataPanel(self.notebook, self.project)
		self.notebook.AddPage(self.alignment_page, "Alignment Data", select=True)
	
	def create_ident_pages(self):
		for expr_name, expr_page in self.experiment_pages.items():
			expr_page.add_ident_tab()
		self.compounds_tab.add_ident_tab()
	
	# def add_ident_tab(self):
	# 	if self.notebook.GetPageIndex(self.ident_panel) != wx.NOT_FOUND:
	# 		# Tab already exists
	# 		return
	#
	# 	self.ident_panel = Experiment.SinglePeakIdentificationPanel(self, self.project.experiment_objects)
	# 	self.notebook.AddPage(self.ident_panel, "Compounds", select=True)
		
	# def add_consolidate_tab(self):
	# 	if self.notebook.GetPageIndex(self.consolidate_panel) != wx.NOT_FOUND:
	# 		# Tab already exists
	# 		return
	#
	# 	self.consolidate_panel = ConsolidatedResultsPanel(self, self.project.consolidated_peaks)
	# 	self.notebook.AddPage(self.consolidate_panel, "Consolidated")

	def on_method_changed(self, event):
		"""
		Event Handler for a property in the Method tab being changed
		"""
		print("on_method_changed")
		print(self.project.method_data.ident_min_aligned_peaks)
		self.project.method_unsaved = True
		event.Skip()
		EVT_PROJECT_CHANGE.trigger()
		
	def on_ammo_details_changed(self, event):
		"""
		Event Handler for a property in the Ammunition Details tab being changed
		"""
		
		self.project.ammo_details_unsaved = True
		event.Skip()
		EVT_PROJECT_CHANGE.trigger()
	
	def on_project_info_changed(self, event):
		"""
		Event Handler for a property in the Project Info propgrid being changed
		"""
		
		self.project.unsaved_changes = True
		event.Skip()
		EVT_PROJECT_CHANGE.trigger()
	
	def add_tab(self, tab_name):
		"""
		Add the tab with the given name if it is not already open

		:param tab_name: The name of the tab to open
		:type tab_name: str
		"""
		
		if tab_name == "Project Info":
			self.add_info_tab()
		elif tab_name == "Method":
			self.add_method_tab()
		elif tab_name == "Ammunition Details":
			self.add_ammo_tab()
		elif tab_name == "Alignment Data":
			self.add_alignment_tab()
		elif tab_name in self.experiment_pages:
			self.add_experiment_tab(tab_name)
	
	def add_experiment_tab(self, tab_name):
		"""
		Add the tab for the Experiment with the given name if it is not already open

		:param tab_name: The name of the Experiment to open the tab for
		:type tab_name: str
		"""
		
		for tab_idx in range(self.notebook.GetPageCount()):
			if self.notebook.GetPageText(tab_idx) == tab_name:
				# tab is already open
				return
		
		# Tab is not open
		self.notebook.AddPage(self.experiment_pages[tab_name], tab_name, select=True)
	
	def add_info_tab(self):
		"""
		Add the tab for the Project Info
		"""

		for tab_idx in range(self.notebook.GetPageCount()):
			if self.notebook.GetPageText(tab_idx) == "Project Info":
				# tab is already open
				return
		
		# Tab is not open
		self.notebook.AddPage(self.project_info, "Project Info", select=True)
		
	def add_ammo_tab(self):
		"""
		
		:return:
		:rtype:
		"""
		
		for tab_idx in range(self.notebook.GetPageCount()):
			if self.notebook.GetPageText(tab_idx) == "Ammunition Details":
				# tab is already open
				return
		
		# Tab is not open
		self.notebook.AddPage(self.project_ammo, "Ammunition Details", select=True)
		
	def add_alignment_tab(self):
		"""
		
		:return:
		:rtype:
		"""
		
		for tab_idx in range(self.notebook.GetPageCount()):
			if self.notebook.GetPageText(tab_idx) == "Alignment Data":
				# tab is already open
				return
		
		# Tab is not open
		self.notebook.AddPage(self.alignment_page, "Alignment Data", select=True)
	
	def save(self, filename=None):
		"""
		Save the project, either to the filename of the project or, if given, the `filename` argument
		
		:param filename:
		:type filename:
		
		:return: True if the operation completed successfully, False otherwise.
		:rtype: bool
		"""
		
		# 1. Extract the project tarfile to a temporary directory
		# 2. Move any files that were changed to a timestamped folder
		# 3. In that folder, create a file called "user" containing the username of the user who made the change
		# 4. In the same folder, create a file called "device" containing the hostname of the device
		# 5. Save the changed files to the temporary directory
		# 6. Tar the contents of the temporary directory over the project file
		# 7. Get rid of the temporary directory
	
		if filename:
			self.project.filename.value = filename
		
		# TODO: Check if the project needs to be saved
		
		print(f"Saving changes as {self.project.filename}")
		
		# One of the files has been changed
		
		self.project.date_modified.value = datetime.datetime.now().timestamp()
		
		self.project.store()
		
		self.project_ammo.fileNotSaved = False
		self.method_tab.fileNotSaved = False
		
		EVT_PROJECT_CHANGE.trigger()
		return True
	
	def save_changes(self):
		"""
		Ask the user whether to save changes to the project, act on their decision.
		
		:return: False if the user cancelled or closed the dialog, and therefore the operation should be aborted;
		True otherwise.
		:rtype: bool
		"""
		
		if self.project.unsaved_changes:
			while True:
				with wx.MessageDialog(
						self,
						f"Do you want to save the changes to {self.project.filename}?",
						"Save Changes?",
						wx.ICON_QUESTION | wx.YES_NO | wx.CANCEL
						) as dlg:
					res = dlg.ShowModal()
					
					if res == wx.ID_YES:
						if self.save():
							break
					elif res == wx.ID_NO:
						print(f"{self.project.name}: Changes discarded")
						break
					else:
						return False
		
		return True
	
	def refresh_date_modified_value(self):
		"""
		Set the 'Date Modified' value in the Property Grid to the value from the Project object
		:return:
		:rtype:
		"""
		self.project_info.property_grid.ChangePropertyValue(
				wx.propgrid.PGPropArgCls(f"{self.project.name}_date_modified"),
				datetime.datetime.fromtimestamp(self.project.date_modified).strftime("%d/%m/%Y %H:%M:%S")
				)
	
	def remove_alignment_data(self):
		"""
		Removes the alignment data from the project file,
		closes the alignment data tab (if open) and removes it from the tree
		"""
		
		self.project.remove_alignment()
		self.project_ammo.fileNotSaved = False
		self.method_tab.fileNotSaved = False
		EVT_PROJECT_CHANGE.trigger()
		
		# Find index of alignment page
		for tab_idx in range(self.notebook.GetPageCount()):
			if self.notebook.GetPageText(tab_idx) == "Alignment Data":
				self.notebook.RemovePage(tab_idx)
				break
		
		self.alignment_page.Destroy()
		self.alignment_page = None
		
		# Tell ProjectNavigator to remove Alignment for this Project
		pub.sendMessage("remove_alignment", project=self.name)
	
	def remove_consolidate_data(self):
		"""
		Removes the consolidate data from the project file,
		closes the consolidate data tab (if open) and removes it from the tree
		"""
		
		self.project.remove_consolidate()
		self.project_ammo.fileNotSaved = False
		self.method_tab.fileNotSaved = False
		EVT_PROJECT_CHANGE.trigger()
		
		self.compounds_tab.remove_consolidate_and_data_tabs()

		# Tell ProjectNavigator to remove Consolidate for this Project
		pub.sendMessage("remove_consolidate", project=self.project.name)
	
	def remove_identification_data(self):
		"""
		Removes the compound identification data from the project file,
		closes the appropriate tab (if open) and removes it from the tree
		"""
		
		for experiment in self.project.experiment_objects:
			experiment.identification_performed = False
			expr_tab = self.experiment_pages[experiment.name]
			expr_tab.remove_ident_tab()
		self.compounds_tab.remove_ident_tab()
		
		self.project.store(resave_experiments=True)
		self.project_ammo.fileNotSaved = False
		self.method_tab.fileNotSaved = False
		EVT_PROJECT_CHANGE.trigger()
		
		pub.sendMessage("remove_identify", project=self.project.name)

	def remove_consolidate_tab(self):
		self.compounds_tab.remove_consolidate_tab()
		# for tab_idx in range(self.notebook.GetPageCount()):
		# 	if self.notebook.GetPage(tab_idx) == self.consolidate_panel:
		# 		self.notebook.RemovePage(tab_idx)
		# 		self.consolidate_panel.Destroy()
		# 		self.consolidate_panel = None
		# 		return

	def align(self):
		"""
		Perform PyMassSpec 'Peak Alignment'
		
		:return: True if the operation completed successfully.
		:rtype: bool
		"""
		
		if self.project.alignment_performed:
			with wx.MessageDialog(
					self,
					f"""Alignment has already been performed.
{self.project.alignment_audit_record}
Do you want to remove the existing Alignment data and continue?""",
					caption="Alignment already performed",
					style=wx.OK | wx.CANCEL | wx.CANCEL_DEFAULT | wx.CENTRE | wx.ICON_ERROR) as dlg:
				dlg.SetOKLabel("Remove && Continue")
				res = dlg.ShowModal()
				
				if res == wx.ID_OK:
					self.remove_alignment_data()
				else:
					return
		
		# Create progressbar and align
		thread = WorkerThread(self, Project.align_in_separate_process)
		thread.start()
		self.prog_dialog = AnimatedProgDialog("Alignment In Progress...", self)
		
		# pub.subscribe(self.on_dialog_cancelled, "AnimatedProgDialogCancel")
		
		self.prog_dialog.ShowModal()
		
		# pub.unsubscribe(self.on_dialog_cancelled, "AnimatedProgDialogCancel")
		
		# del self.align_prog_dialog
		# del self.align_thread
		
		self.reload_project()
	
		pub.sendMessage("on_alignment_performed", project=self.project)
		
		wx.CallAfter(self.create_alignment_page)
		# self.destroy_prog_dialog()
	#
	# def on_dialog_cancelled(self, dialog):
	# 	if hasattr(self, "align_prog_dialog"):
	# 		if dialog == self.align_prog_dialog:
	# 			self.align_thread.cancel()
	#
	
	def identify(self):
		"""
		Identify compounds in each experiments
		
		:return: True if the operation completed successfully.
		:rtype: bool
		"""
		
		if not self.project.alignment_performed:
			wx.MessageDialog(
					self, "Peak Alignment must be performed first!",
					caption="Error", style=wx.OK | wx.CENTRE | wx.ICON_ERROR
					).ShowModal()
			return
		
		# Check which, if any, experiments have had identification performed already
		identify_performed = []
		
		for experiment in self.project.experiment_objects:
			if experiment.identification_performed:
				identify_performed.append(experiment)
		
		print(identify_performed)
		
		if identify_performed:
			error_string = "Compound Identification has already been performed for the following experiments"

			for experiment in identify_performed:
				error_string += f"\n{experiment.name}: {experiment.ident_audit_record}"

			with wx.MessageDialog(
					self,
					f"{error_string}\n\nDo you want to remove the existing data and continue?",
					caption="Identify Compounds already performed",
					style=wx.OK | wx.CANCEL | wx.CANCEL_DEFAULT | wx.CENTRE | wx.ICON_ERROR) as dlg:
				dlg.SetOKLabel("Remove && Continue")
				res = dlg.ShowModal()

				if res == wx.ID_OK:
					self.remove_identification_data()
				else:
					return
		
		# Create progressbar
		thread = WorkerThread(self, Project.identify_in_separate_process)
		thread.start()
		self.prog_dialog = AnimatedProgDialog("Compound Identification In Progress...", self)
		self.prog_dialog.ShowModal()
		
		self.reload_project()
		
		wx.CallAfter(pub.sendMessage, "on_ident_performed", project=self.project)
		wx.CallAfter(self.create_ident_pages)
		# self.destroy_prog_dialog()

	def consolidate(self):
		if not self.project.alignment_performed:
			wx.MessageDialog(
					self, "Peak Alignment must be performed first!",
					caption="Error", style=wx.OK | wx.CENTRE | wx.ICON_ERROR
					).ShowModal()
			return
		
		for experiment in self.project.experiment_objects:
			if not experiment.identification_performed:
				wx.MessageDialog(
						self, "Compound Identification must be performed first!",
						caption="Error", style=wx.OK | wx.CENTRE | wx.ICON_ERROR
						).ShowModal()
				return
		
		if self.project.consolidate_performed:
			with wx.MessageDialog(
					self,
					f"""Consolidate has already been performed.
{self.project.consolidate_audit_record}
Do you want to remove the existing Consolidate data and continue?""",
					caption="Consolidate already performed",
					style=wx.OK | wx.CANCEL | wx.CANCEL_DEFAULT | wx.CENTRE | wx.ICON_ERROR) as dlg:
				dlg.SetOKLabel("Remove && Continue")
				res = dlg.ShowModal()
				
				if res == wx.ID_OK:
					self.remove_consolidate_data()
				else:
					return
	
		# Create progressbar
		thread = WorkerThread(self, Project.consolidate_in_separate_process)
		thread.start()
		self.prog_dialog = AnimatedProgDialog("Consolidation In Progress...", self)
		self.prog_dialog.ShowModal()
		
		self.reload_project()
		
		print("Sending trigger to Project Navigator")
		wx.CallAfter(pub.sendMessage, "on_consolidate_performed", project=self.project)
		print("Sending request to add Consolidate and Data tabs")
		wx.CallAfter(self.compounds_tab.add_consolidate_and_data_tabs)
	
	def destroy_prog_dialog(self):
		if hasattr(self, "prog_dialog"):
			wx.CallAfter(self.prog_dialog.Destroy)
			del self.prog_dialog
	
	def reload_project(self):
		self.project = Project.Project.load(self.project.filename.value)
		
		for experiment in self.project.experiment_objects:
			self.experiment_pages[experiment.name].experiment = experiment
		
		# self.compounds_tab.project = self.project
		
		EVT_PROJECT_CHANGE.trigger()
		
	@property
	def name(self):
		"""
		Returns the name of the Project
		"""

		return self.project.name
	
	def get_selected_experiment(self):
		"""
		Returns the Experiment object for the currently selected page,
		or None if the page is not an ExperimentDataPanel

		:rtype: Experiment
		"""
		
		return self.get_experiment_by_index(self.notebook.GetSelection())
	
	def get_selected_experiment_panel(self):
		"""
		Returns the ExperimentDataPanel for the currently selected page,
		or None if the page is not an ExperimentDataPanel

		:rtype: ExperimentDataPanel
		"""
		
		return self.get_experiment_panel_by_index(self.notebook.GetSelection())
	
	def get_experiment_by_index(self, index):
		"""
		Returns the Experiment object for the page with the given index,
		or None if the page is not an ExperimentDataPanel

		:param index: The index of the tab to return the Experiment object for
		:type index: int

		:rtype: Experiment
		"""
		
		expr_panel = self.get_experiment_panel_by_index(index)
		
		if expr_panel:
			return expr_panel.experiment
		
	def get_experiment_panel_by_index(self, index):
		"""
		Returns the ExperimentDataPanel for the page with the given index,
		or None if the page is not an ExperimentDataPanel
		
		:param index: The index of the tab to return the ExperimentDataPanel for
		:type index: int
		
		:rtype: ExperimentDataPanel
		"""
		
		if isinstance(self.notebook.GetPage(index), Experiment.ExperimentDataPanel):
			return self.notebook.GetPage(index)
	
	def iter_experiment_panels(self):
		"""
		Returns an iterable for the pages in the notebook, in the order they appear
		
		:rtype:
		"""
		
		for tab_idx in range(self.notebook.GetPageCount()):
			page = self.get_experiment_panel_by_index(tab_idx)
			if page:
				yield page
		
	def switch_to_experiment_content(self, expr_name, page_title):
		"""
		Switch to the given Experiment, and then to the selected page within that Experiment
		
		:param expr_name: The name of the Experiment to switch to
		:type expr_name: str
		:param page_title: The name of the page to switch to
		:type page_title: str
		:return: A tuple containing the index of the Experiment's tab, and the index of the page's tab
		:rtype: (int, int)
		"""
		
		tab_idx = self.switch_to_content(expr_name)
		expr_panel = self.notebook.GetPage(tab_idx)
		e_tab_idx = expr_panel.switch_to_content(page_title)
		return tab_idx, e_tab_idx
	
	def switch_to_compounds_content(self, page_title):
		"""
		Switch to the Compounds tab, and then to the selected page
		
		:param page_title: The name of the page to switch to
		:type page_title: str
		:return: A tuple containing the index of the Compounds tab, and the index of the page's tab
		:rtype: (int, int)
		"""
		
		tab_idx = self.switch_to_content("Compounds")
		compounds_panel = self.notebook.GetPage(tab_idx)
		c_tab_idx = compounds_panel.switch_to_content(page_title)
		return tab_idx, c_tab_idx
	
	def next_experiment(self):
		"""
		Change to the next (right) experiment.
		"""
		
		self.change_experiment(1)
		
	def previous_experiment(self):
		"""
		Change to the previous (left) experiment.
		"""
		
		self.change_experiment(-1)
	
	def change_experiment(self, direction=1):
		"""
		Change experiment, either to the right (+) or the left (-).
		
		:param direction: The direction to move, either + (right) or the - (left), and how fare to move
		:type direction: int
		"""
		
		# if direction not in {1, -1}:
		if not isinstance(direction, int):
			warnings.warn("Unknown direction, reverting to 1 (Next)")
			direction = 1
		
		if direction == 0:
			warnings.warn("Direction = 0, not moving")
			return
		
		current_selected_page = self.notebook.GetPage(self.notebook.GetSelection())
		expr_list = self.project.experiments
		
		print(isinstance(current_selected_page.get_selected_page(), Project.DataViewer))
		
		if isinstance(current_selected_page, Experiment.ExperimentDataPanel):
			for expr_idx, experiment in enumerate(expr_list):
				if current_selected_page.name == experiment["name"]:
					current_expr_index = expr_idx
			
					# if (current_expr_index + direction) == len(expr_list):
					# 	if direction > 0:
					# 		current_expr_index = -1
					# 	elif direction < 0:
					# 		current_expr_index = len(expr_list)
					
					current_expr_index = (current_expr_index + direction) % len(expr_list)
						
					next_expr_name = expr_list[current_expr_index + direction]["name"]
					
					current_expr_content = current_selected_page.notebook.GetPageText(
							current_selected_page.notebook.GetSelection()
							)
					
					self.switch_to_experiment_content(next_expr_name, current_expr_content)
					
					return
		
		elif isinstance(current_selected_page, Project.CompoundsDataPanel) \
			and isinstance(current_selected_page.get_selected_page(), Project.DataViewer):
			current_selected_page.get_selected_page().change_experiment(direction)
			
		
	def view_spectrum_on_click(self):
		"""
		Enables viewing the spectrum by clicking the chromatogram. Currently does nothing.
		
		:return:
		:rtype:
		"""
		return NotImplemented
	
	def view_spectrum_by_scan(self):
		"""
		Shows the user a dialog to choose the scan number they went to see the spectrum for,
		then displays the spectrum in that scan in the currently selected experiment in a separate window.
		"""
		
		if not isinstance(self.get_selected_page(), Experiment.ExperimentDataPanel):
			# No experiment currently selected
			return
		
		with IntEntryDialog(
				parent=self, message='View Mass Spectrum with the following Scan Number:',
				caption='View Mass Spectrum by Scan No.') as dlg:
			if dlg.ShowModal() == wx.ID_OK:
				self.get_selected_experiment_panel().view_spectrum(num=dlg.GetValue())
		
	def view_spectrum_by_rt(self):
		"""
		Shows the user a dialog to choose the retention time they went to see the spectrum for,
		then displays the spectrum at that time in the currently selected experiment in a separate window.
		"""
		
		if not isinstance(self.get_selected_page(), Experiment.ExperimentDataPanel):
			# No experiment currently selected
			return
		
		with FloatEntryDialog(
				parent=self, message='View Mass Spectrum at the following Retention Time:',
				caption='View Mass Spectrum by RT') as dlg:
			if dlg.ShowModal() == wx.ID_OK:
				self.get_selected_experiment_panel().view_spectrum(rt=dlg.GetValue())
	
	def export_method(self, output_filename):
		self.project.export_method(output_filename)
	
	def export_ammo_details(self, output_filename):
		self.project.export_ammo_details(output_filename)
	
	def export_project_report(self, output_filename):
		Project.ProjectReportPDFExporter(self, output_filename)
	
	def make_method_tab(self):
		self.do_make_method_tab(self.project.method_data)
		self.method_tab.filename_value.SetValue(self.project.filename.value)
	
	def make_ammo_tab(self):
		self.project_ammo = Ammunition.DetailsPanel(self.project.ammo_data, self.notebook, wx.ID_ANY)
		self.project_ammo.filename_value.SetValue(self.project.ammo_details.value)
		self.notebook.AddPage(self.project_ammo, "Ammunition Details")


# def view_spectrum(self, *, rt=None, num=None):
	# 	"""
	# 	View the spectrum selected for the currently selected project
	#
	# 	:param rt: Retention Time in minutes
	# 	:type rt: float
	# 	:param num: Scan Number
	# 	:type num: int
	#
	# 	:return:
	# 	:rtype:
	# 	"""
	#
	# 	if not rt and not num:
	# 		raise ValueError("Either 'rt' or 'num' is required!")
	#
	# 	if rt and num:
	# 		raise ValueError("Only specify one of 'rt' or 'num'!")
	#
	# 	if rt:
	# 		if not isinstance(rt, float):
	# 			raise TypeError("'rt' must be a float")
	# 		print(f"Loading Spectrum at retention time: {rt} minutes")
	#
	# 	if num:
	# 		if not isinstance(num, int):
	# 			raise TypeError("'num' must be an int")
	# 		print(f"Loading Spectrum with scan number: {num}")
		

# end of class ProjectDataPanel

# TODO: Allow cancelling of operations

class WorkerThread(threading.Thread):
	"""
	Thread for performing processing in a separate process
	"""
	
	def __init__(self, parent, target):
		threading.Thread.__init__(self)
		self.target = target
		self.parent = parent
	
	def run(self):
		self.process = multiprocessing.Process(target=self.target, args=(self.parent.project,))
		self.process.start()
		self.process.join()
		self.parent.destroy_prog_dialog()
	#
	# def cancel(self):
	# 	self.process.terminate()
	# 	print("Operation Cancelled")
