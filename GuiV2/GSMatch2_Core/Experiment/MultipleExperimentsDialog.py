#!/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  MultipleExperimentsDialog.py
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2019  Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
# generated by wxGlade 0.9.3 on Tue Dec  3 15:33:36 2019
#

# TODO: Load name and description from file, if present

# stdlib
import getpass
import pathlib
import socket
import threading

# 3rd party
import wx
from domdf_wxpython_tools.picker import file_picker

# this package
from GuiV2.GSMatch2_Core import Experiment, Method, SorterPanels
from GuiV2.GSMatch2_Core.Config import internal_config
from GuiV2.GSMatch2_Core.Experiment.DatafilePanel import DatafilePanel
from GuiV2.GSMatch2_Core.Experiment.PropertiesPanel import PropertiesPanel
from GuiV2.GSMatch2_Core.GUI.prog_dialog_indeterminate import ProgDialogThread
from GuiV2.GSMatch2_Core.GUI.validators import ExperimentMethodValidator
from GuiV2.GSMatch2_Core.IDs import *
from GuiV2.GSMatch2_Core.utils import lookup_filetype

# 3rd party

'''
# begin wxGlade: dependencies
from MultipleExperimentSorterPanel import MultipleExperimentSorterPanel
# end wxGlade
'''

# begin wxGlade: extracode
# end wxGlade


# TODO: Import and export of csv file containing experiments and properties to process
class MultipleExperimentsDialog(wx.Dialog, Method.MethodPickerMixin):
	"""
	Dialog for creating multiple Experiments in bulk using similar settings
	"""

	def __init__(self, *args, **kwds):
		"""
		:param parent: The parent window.
		:type parent: wx.Window
		:param id: An identifier for the dialog. wx.ID_ANY is taken to mean a default.
		:type id: wx.WindowID, optional
		:param pos: The dialog position. The value ::wxDefaultPosition indicates a default position,
		:type pos: wx.Point, optional
			chosen by either the windowing system or wxWidgets, depending on platform.
		:param size: The dialog size. The value ::wxDefaultSize indicates a default size, chosen by
		:type size: wx.Size, optional
			either the windowing system or wxWidgets, depending on platform.
		:param style: The window style. See wxPanel.
		:type style: int, optional
		:param name: Window name.
		:type name: str, optional
		"""
		
		# begin wxGlade: MultipleExperimentsDialog.__init__
		kwds["style"] = kwds.get("style", 0) | wx.DEFAULT_DIALOG_STYLE
		wx.Dialog.__init__(self, *args, **kwds)
		self.SetSize((1000, 800))
		self.main_panel = wx.Panel(self, wx.ID_ANY)
		self.properties = PropertiesPanel(self.main_panel, wx.ID_ANY)
		self.datafile = DatafilePanel(self.main_panel, wx.ID_ANY)
		self.meth_picker = file_picker(self.main_panel, wx.ID_ANY, style=wx.TAB_TRAVERSAL|wx.FD_OPEN, title="Choose a Method", filetypestring="Method Files", extension="method")
		self.new_meth_button = wx.Button(self.main_panel, wx.ID_ANY, "New")
		self.edit_meth_button = wx.Button(self.main_panel, wx.ID_ANY, "Edit")
		self.add_expr_button = wx.Button(self.main_panel, wx.ID_ANY, "&Add Experiment")
		self.edit_expr_button = wx.Button(self.main_panel, wx.ID_ANY, "&Edit Experiment")
		self.remove_expr_button = wx.Button(self.main_panel, wx.ID_ANY, "&Remove Experiment")
		self.remove_expr_button_copy = wx.Button(self.main_panel, wx.ID_ANY, "Clear")
		self.expr_list_panel = SorterPanels.MultipleExperimentSorterPanel(self.main_panel, wx.ID_ANY)

		self.__set_properties()
		self.__do_layout()

		self.Bind(wx.EVT_BUTTON, self.on_add_experiment, self.add_expr_button)
		self.Bind(wx.EVT_BUTTON, self.on_edit_experiment, self.edit_expr_button)
		self.Bind(wx.EVT_BUTTON, self.on_remove_experiment, self.remove_expr_button)
		self.Bind(wx.EVT_BUTTON, self.on_clear_experiments, self.remove_expr_button_copy)
		# end wxGlade
		
		self.properties.ShowFilename()
		
		Method.MethodPickerMixin.__init__(self)
		
		self.properties.user.SetValue(getpass.getuser())
		self.properties.device.SetValue(socket.gethostname())
		
		self.Bind(wx.EVT_BUTTON, self.on_create, id=self.ok_button)
		self.SetExtraStyle(wx.WS_EX_VALIDATE_RECURSIVELY)
		
		self.experiments = []

	def __set_properties(self):
		# begin wxGlade: MultipleExperimentsDialog.__set_properties
		self.SetTitle("Create Multiple Experiments")
		self.SetSize((1000, 800))
		self.meth_picker.SetMinSize((-1, 30))
		self.meth_picker.SetMaxSize((-1, 30))
		self.meth_picker.SetValidator(ExperimentMethodValidator())
		self.new_meth_button.SetMinSize((-1, 29))
		self.edit_meth_button.SetMinSize((-1, 29))
		# end wxGlade
		
		self.meth_picker.SetValue(str(internal_config.last_method))
		self.Bind(wx.EVT_TEXT, self.on_method_change, self.meth_picker.dir_value)
		
		self.meth_picker.dialog_title = "Select Method File"

	def __do_layout(self):
		# begin wxGlade: MultipleExperimentsDialog.__do_layout
		outer_sizer = wx.BoxSizer(wx.VERTICAL)
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		expr_sizer = wx.StaticBoxSizer(wx.StaticBox(self.main_panel, wx.ID_ANY, "Experiments: "), wx.VERTICAL)
		expr_button_sizer = wx.BoxSizer(wx.HORIZONTAL)
		meth_picker_box = wx.StaticBoxSizer(wx.StaticBox(self.main_panel, wx.ID_ANY, "Method: "), wx.VERTICAL)
		meth_picker_sizer = wx.BoxSizer(wx.HORIZONTAL)
		intro_label = wx.StaticText(self.main_panel, wx.ID_ANY, "Create Multiple Experiments")
		intro_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 0, ""))
		main_sizer.Add(intro_label, 0, 0, 5)
		static_line_1 = wx.StaticLine(self.main_panel, wx.ID_ANY)
		main_sizer.Add(static_line_1, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 6)
		main_sizer.Add(self.properties, 1, wx.EXPAND, 0)
		static_line_2 = wx.StaticLine(self.main_panel, wx.ID_ANY)
		main_sizer.Add(static_line_2, 0, wx.BOTTOM | wx.EXPAND | wx.TOP, 6)
		main_sizer.Add(self.datafile, 1, wx.EXPAND, 0)
		meth_picker_sizer.Add(self.meth_picker, 1, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 2)
		meth_picker_sizer.Add(self.new_meth_button, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
		meth_picker_sizer.Add(self.edit_meth_button, 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 5)
		meth_picker_box.Add(meth_picker_sizer, 0, wx.EXPAND, 0)
		main_sizer.Add(meth_picker_box, 0, wx.EXPAND | wx.TOP, 10)
		expr_button_sizer.Add(self.add_expr_button, 0, wx.LEFT | wx.RIGHT, 5)
		expr_button_sizer.Add(self.edit_expr_button, 0, wx.RIGHT, 5)
		expr_button_sizer.Add(self.remove_expr_button, 0, wx.RIGHT, 5)
		expr_button_sizer.Add(self.remove_expr_button_copy, 0, wx.RIGHT, 5)
		expr_sizer.Add(expr_button_sizer, 1, wx.EXPAND | wx.TOP, 5)
		expr_sizer.Add(self.expr_list_panel, 7, wx.ALIGN_CENTER_VERTICAL | wx.BOTTOM | wx.EXPAND | wx.RIGHT, 2)
		main_sizer.Add(expr_sizer, 1, wx.EXPAND | wx.TOP, 10)
		self.main_panel.SetSizer(main_sizer)
		outer_sizer.Add(self.main_panel, 1, wx.ALL | wx.EXPAND, 10)
		self.SetSizer(outer_sizer)
		self.Layout()
		# end wxGlade
		
		btnsizer = self.CreateSeparatedButtonSizer(wx.OK | wx.CANCEL)
		
		self.ok_button = self.GetAffirmativeId()
		self.FindWindow(self.ok_button).SetLabel("Create")
		
		outer_sizer.Add(btnsizer, 0, wx.ALIGN_RIGHT | wx.EXPAND | wx.BOTTOM, 5)
	
	def update_expr_list(self):
		"""
		Function to update the list of Experiments in the GUI from the list of
		Experiments in the back end. Called whenever an Experiment is added, removed etc.
		"""

		self.expr_list_panel.expr_list.DeleteAllItems()
		if self.experiments:
			
			itemDataMap = {}
			
			for row_idx, experiment in enumerate(self.experiments):
				expr_data = (
						experiment.name, experiment.filename, experiment.description,
						experiment.method, experiment.original_filename, lookup_filetype(experiment.original_filetype)
						)
				
				self.expr_list_panel.expr_list.Append(expr_data)
				itemDataMap[row_idx] = expr_data
				self.expr_list_panel.expr_list.SetItemData(row_idx, row_idx)
			
			self.expr_list_panel.itemDataMap = itemDataMap
	
	def on_edit_experiment(self, event=None):  # wxGlade: MultipleExperimentsDialog.<event_handler>
		"""
		Event handler for an Experiment being edited
		"""
		
		selected_experiment = self.expr_list_panel.expr_list.GetFirstSelected()
		if selected_experiment != -1:
			
			self.properties.name.SetValue(
					self.expr_list_panel.expr_list.GetItemText(selected_experiment, 0)
					)
			self.properties.filename.SetValue(
					self.expr_list_panel.expr_list.GetItemText(selected_experiment, 1)
					)
			self.properties.description.SetValue(
					self.expr_list_panel.expr_list.GetItemText(selected_experiment, 2)
					)
			self.meth_picker.SetValue(
					self.expr_list_panel.expr_list.GetItemText(selected_experiment, 3)
					)
			self.datafile.expr_picker.SetValue(
					self.expr_list_panel.expr_list.GetItemText(selected_experiment, 4)
					)
			
			# Determine filetype
			for ID, button in self.datafile.format_radio_btns.items():
				if ID == self.expr_list_panel.expr_list.GetItemText(selected_experiment, 5):
					button.SetValue(1)
				else:
					button.SetValue(0)
			
		if event:
			event.Skip()
	
	def on_remove_experiment(self, event=None):  # wxGlade: MultipleExperimentsDialog.<event_handler>
		"""
		Event handler for an Experiment being removed
		"""
		
		selected_experiment = self.expr_list_panel.expr_list.GetItemText(
				self.expr_list_panel.expr_list.GetFirstSelected(),
				1,
				)
		
		self.experiments = [experiment for experiment in self.experiments if experiment.filename != selected_experiment]
		
		self.update_expr_list()
		
		if event:
			event.Skip()
	
	def on_clear_experiments(self, _):  # wxGlade: MultipleExperimentsDialog.<event_handler>
		self.experiments = []
		self.update_expr_list()
	
	def on_add_experiment(self, event):  # wxGlade: MultipleExperimentsDialog.<event_handler>
		
		if self.Validate() and self.datafile.validate_datafile():
			
			for experiment in self.experiments:
				if experiment.filename.value == self.properties.filename.GetValue():
					# Update existing entry
					with wx.MessageDialog(
							self, caption="Overwrite settings?", style=wx.YES_NO,
							message=f"Overwrite existing settings for file {experiment.filename}?",
							) as dlg:
						if dlg.ShowModal() != wx.ID_YES:
							# Abort
							return
						else:

							experiment.name = self.properties.name.GetValue()
							experiment.method = self.meth_picker.GetValue()
							experiment.description = self.properties.description.GetValue()
							
							self._set_experiment_properties(experiment)
							
							break
						
			else:
				experiment = Experiment.Experiment.new(
						self.properties.name.GetValue(),
						self.meth_picker.GetValue(),
						self.properties.description.GetValue()
						)
				
				self._set_experiment_properties(experiment)
				
				self.experiments.append(experiment)
				
			self.update_expr_list()
		
		else:
			print("Validation Error")
	
	def _set_experiment_properties(self, experiment):
		
		filename = self.properties.filename.GetValue()
		if not filename.lower().endswith(".expr"):
			filename = f"{filename}.expr"
		experiment.filename.value = filename
		
		experiment.original_filename = self.datafile.expr_picker.GetValue()
		
		# Determine filetype
		for ID, button in self.datafile.format_radio_btns.items():
			if button.GetValue():
				experiment.original_filetype = ID
				return
	
	def on_create(self, event=None):
		"""
		Event handler for 'Create' button being pressed.
		
		Creates the Experiments
		"""
		
		internal_config.last_datafile = self.datafile.expr_picker.GetValue()
		internal_config.last_method = self.meth_picker.GetValue()
		
		# TODO: need some validation here
		
		# Ask the user where to save the experiment
		with wx.DirDialog(
			self, "Save Experiments", defaultPath=str(internal_config.last_experiment),
			) as dlg:
			
			if dlg.ShowModal() == wx.ID_OK:
				save_path = pathlib.Path(dlg.GetPath())
			else:
				return
		
		experiments_to_process = []
		yes_to_all = False
		for experiment in self.experiments:
			
			# Check if the file exists already:
			filename = pathlib.Path(save_path) / pathlib.Path(experiment.filename.value)
			if filename.exists() and not yes_to_all:
				with OverwritePrompt(
						self,
						message=f"""The file '{experiment.filename}' already exists.
Do you want to replace it?""",
						) as dlg:
					res = dlg.ShowModal()
					if res == wx.ID_CANCEL:
						return
					elif res == wx.ID_NO:
						# Skip this experiment file
						continue
					elif res == wx.ID_YESTOALL:
						yes_to_all = True
					
			
			# If file doesn't exist or if it does exist and user wants to replace it:
			internal_config.last_experiment = filename
			experiment.filename.value = filename
			experiments_to_process.append(experiment)
		
		MultipleExperimentsProgressDialog(self, experiments_to_process)
					
# end of class MultipleExperimentsDialog


class OverwritePrompt(wx.Dialog):
	def __init__(self, parent, id=wx.ID_ANY, message="Do you want to overwrite the existing file?", title='Overwrite File?', pos=wx.DefaultPosition, size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE, name=wx.DialogNameStr):
		wx.Dialog.__init__(self, parent, id=id, title=title, pos=pos, size=size, style=style, name=name)
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(wx.StaticText(self, label=str(message)), 0, wx.ALL, 10)
		
		self.cancel_btn = wx.Button(self, label="Cancel")
		self.no_btn = wx.Button(self, label="&No")
		self.yes_btn = wx.Button(self, label="&Yes")
		self.yes_to_all_btn = wx.Button(self, label="Yes to All")
		
		btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
		btn_sizer.AddSpacer(10)
		btn_sizer.Add(self.cancel_btn)
		btn_sizer.Add(self.no_btn)
		btn_sizer.Add(self.yes_btn)
		btn_sizer.Add(self.yes_to_all_btn)
		
		sizer.Add(btn_sizer, 1, wx.EXPAND | wx.ALIGN_RIGHT | wx.ALL, 10)
		self.SetSizerAndFit(sizer)
		
		self.Bind(wx.EVT_BUTTON, self.on_yes, self.yes_btn)
		self.Bind(wx.EVT_BUTTON, self.on_yes_to_all, self.yes_to_all_btn)
		self.Bind(wx.EVT_BUTTON, self.on_no, self.no_btn)
		self.Bind(wx.EVT_BUTTON, self.on_cancel, self.cancel_btn)
		
		self.no_btn.SetFocus()
		
	
	def Show(self, *args, **kwargs):
		return self.ShowModal()
	
	def on_yes(self, event):
		self.EndModal(wx.ID_YES)
		
	def on_yes_to_all(self, event):
		self.EndModal(wx.ID_YESTOALL)
		
	def on_no(self, event):
		self.EndModal(wx.ID_NO)
		
	def on_cancel(self, event):
		self.EndModal(wx.ID_CANCEL)
		

class MultipleExperimentsThread(threading.Thread):
	"""
	Thread for creating multiple Experiments
	"""
	
	def __init__(self, experiment_list):
		threading.Thread.__init__(self)
		
		self.experiment_list = experiment_list
	
	def run(self):
		"""
		Starts the Thread. Don't call this directly; use ``Thread.start()`` instead.
		"""
		print("Experiment Creation in Progress...")
		
		for experiment in self.experiment_list:
			# TODO: perform creation in parallel
			experiment.run(experiment.original_filename, experiment.original_filetype)


class MultipleExperimentsProgressDialog(ProgDialogThread):
	def __init__(self, parent, experiment_list):
		"""
		:param parent:
		:type parent:
		:param experiment_list: A list of :class:`Experiment` object to process
		:type experiment_list:
		
		.. note: Unlike with :class:`ExperimentProgressDialog`,
		the original_filetype and original_filename attributes must have already
		been set for the Experiment
		"""
		
		self.parent = parent
		self.experiment_list = experiment_list
		thread = MultipleExperimentsThread(self.experiment_list)
		
		ProgDialogThread.__init__(self, thread, "Experiment", "Experiment Creation In Progress...", 100, parent)
	
	def updateProgress(self, msg):
		"""
		Event handler for updating the progress bar
		"""
		
		self.Pulse()
		
		if msg == "Dead":
			# Thread is dead because Experiment has been created
			
			for experiment in self.experiment_list:
				experiment.store()
				
			print("Experiments Created")
			with wx.MessageDialog(
					self,
					"Experiments Created Successfully.",
					"Experiments Created") as dlg:
				dlg.ShowModal()
				
			if self.parent.IsModal():
				self.parent.EndModal(wx.ID_OK)
			else:
				self.parent.Destroy()
		
			self.Destroy()


if __name__ == '__main__':
	app = wx.App()
	with OverwritePrompt(None) as dlg:
		res = dlg.ShowModal()
		if res == wx.ID_YES:
			print("YES")
		elif res == wx.ID_YESTOALL:
			print("YESTOALL")
		elif res == wx.ID_NO:
			print("NO")
		elif res == wx.ID_CANCEL:
			print("CANCEL")
