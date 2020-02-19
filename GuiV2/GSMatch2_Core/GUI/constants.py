#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  constants.py
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

# stdlib

# 3rd party
import wx
from importlib_resources import path

# this package
import GSMatch.lib.icons
from GuiV2.GSMatch2_Core.IDs import *
from GuiV2.icons import get_icon


windows_only_formats = [ID_Format_MassHunter]
file_formats = {ID_Format_mzML, ID_Format_ANDI, ID_Format_jcamp}
folder_formats = {ID_Format_MassHunter, ID_Format_WatersRAW, ID_Format_ThermoRAW}

# Help strings
project_user_help = "The user who created the Project"
project_name_help = "The name of the Project"
project_device_help = "The device that created the Project"
project_date_created_help = "The date and time the Project was created"
project_date_modified_help = "The date and time the Project was modified"
project_description_help = "A description of the Project"
project_version_help = "File format version in semver format"
project_method_help = "The name of the file containing the Method used to create the Project"

experiment_user_help = "The user who created the Experiment"
experiment_name_help = "The name of the Experiment"
experiment_device_help = "The device that created the Experiment"
experiment_date_created_help = "The date and time the Experiment was created"
experiment_date_modified_help = "The date and time the Experiment was modified"
experiment_description_help = "A description of the Experiment"
experiment_version_help = "File format version in semver format"
experiment_method_help = "The name of the file containing the Method used to create the Experiment"
experiment_filename_help = "The name of the Experiment file"
experiment_original_filename_help = "The filename of the file the Experiment was created from"
experiment_original_filetype_help = "The filetype of the file the Experiment was created from"

