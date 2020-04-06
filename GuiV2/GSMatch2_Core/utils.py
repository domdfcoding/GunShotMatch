#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  utils.py
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
import pathlib
import subprocess

# 3rd party
import wx
from domdf_wxpython_tools import file_dialog_multiple
from importlib_resources import path

# this package
import GuiV2
from GuiV2.GSMatch2_Core.Config import internal_config
from GuiV2.GSMatch2_Core.IDs import *


def method_editor(filename=None):
	with path(GuiV2, "MethodEditor_GUI.py") as me_path:
		args = ["python3", str(me_path)]
		if filename:
			args.append(filename)
		subprocess.Popen(args)


def ammo_editor(filename=None):
	with path(GuiV2, "AmmoDetailsEditor_GUI.py") as me_path:
		args = ["python3", str(me_path)]
		if filename:
			args.append(filename)
		subprocess.Popen(args)


def open_project_dialog(parent, start_directory=None):
	if not start_directory:
		start_directory = str(internal_config.last_project)
	
	return file_dialog_multiple(
			parent, "proj", "Open Project", "Project files",
			style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE,
			defaultDir=start_directory
			)


def lookup_filetype(filetype):
	if filetype == ID_Format_jcamp:
		return "JCAMP-DX"
	elif filetype == ID_Format_mzML:
		return "HUPO-PSI mzML"
	elif filetype == ID_Format_ANDI:
		return "ANDI-MS / netCDF"
	elif filetype == ID_Format_MassHunter:
		return "Agilent MassHunter"
	elif filetype == ID_Format_WatersRAW:
		return "Waters MassLynx / PerkinElmer TurboMass"
	elif filetype == ID_Format_ThermoRAW:
		return "ThermoFisher RAW"


def filename_only(fullpath):
	"""
	Returns just the filename when given a full path

	:param fullpath:
	:type fullpath:

	:return:
	:rtype: str
	"""
	#
	# if isinstance(fullpath, Property) and fullpath.type == dir:
	# 	fullpath = fullpath.value
	
	if fullpath is None:
		return
	else:
		return pathlib.Path(fullpath).name


# Yield successive n-sized chunks from l.
# https://www.geeksforgeeks.org/break-list-chunks-size-n-python/
def divide_chunks(original_list, n):
	# looping till len(original_list)
	for i in range(0, len(original_list), n):
		yield original_list[i:i + n]


def create_button(
		parent, id=wx.ID_ANY, label='', pos=wx.DefaultPosition, size=wx.DefaultSize,
		style=0, validator=wx.DefaultValidator, name=wx.ButtonNameStr, sizer=None,
		handler=None, sizer_proportion=0, sizer_flags=0, sizer_border=0):
	"""
	Constructs a button.
	Optionally binds a handler to wx.EVT_BUTTON.
	Optionally adds the button to a sizer.

	:param parent: Parent window. Must not be None.
	:type parent: wx.Window
	:param id: Checkbox identifier. The value wx.ID_ANY indicates a default value.
	:type id: wx.WindowID, optional
	:param label: Text to be displayed on the button.
	:type label: str
	:param pos: Checkbox position. If wx.DefaultPosition is specified then a default position is chosen.
	:type pos: wx.Point, optional
	:param size: Checkbox size. If wx.DefaultSize is specified then a default size is chosen.
	:type size: wx.Size, optional
	:param style: Window style. See wx.CheckBox.
	:type style: int, optional
	:param validator: Window validator.
	:type validator: wx.Validator, optional
	:param name: Window name.
	:type name: str, optional
	:param sizer: The sizer to add the control to. If None the control will not be added to any sizer.
	:type sizer: wx.Sizer or None, optional.
	:param handler: Event handler to bind to wx.EVT_BUTTON. If None no handler will be bound to the event
	:type handler: callable or None, optional.
	:param sizer_proportion: Passed through to the sizer if sizer is not None. Used to indicate if a child
		of a sizer can change its size in the main orientation of the wx.BoxSizer - where 0 stands for
		not changeable and a value of more than zero is interpreted relative to the value of other
		children of the same wx.BoxSizer. For example, you might have a horizontal wx.BoxSizer with three
		children, two of which are supposed to change their size with the sizer. Then the two stretchable
		windows would get a value of 1 each to make them grow and shrink equally with the sizer’s
		horizontal dimension.
	:type sizer_proportion: int, optional
	:param sizer_flags: Passed through to the sizer if sizer is not None. OR-combination of flags
		affecting the sizer’s behaviour. See wx.Sizer for a list of flags.
	:type sizer_flags: int, optional
	:param sizer_border: Passed through to the sizer if sizer is not None. Determines the border width,
		if the sizer_flags parameter is set to include any border flag.
	:type sizer_border: int, optional

	:return:
	:rtype: wx.Button
	"""
	
	btn = wx.Button(parent, id, label, pos, size, style, validator, name)
	
	if sizer:
		sizer.Add(btn, sizer_proportion, sizer_flags, sizer_border)
	
	if handler:
		parent.Bind(wx.EVT_BUTTON, handler, btn)
