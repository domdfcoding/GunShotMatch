#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  utils.py
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2019-2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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

