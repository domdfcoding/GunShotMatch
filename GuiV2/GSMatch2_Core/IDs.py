#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  IDs.py
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
from string import ascii_lowercase

# 3rd party
import wx


def id_from_string(id_string):
	int_id = ['1']
	for character in id_string.lower():
		char_num = str(ascii_lowercase.index(character))
		if len(char_num) == 1:
			char_num = f"0{char_num}"
		int_id.append(char_num)
	return int("".join(int_id))


tb_icon_size = (24, 24)


ID_Settings = wx.NewIdRef()
ID_About = wx.NewIdRef()
ID_RECENT_0 = wx.NewIdRef()
ID_RECENT_1 = wx.NewIdRef()
ID_RECENT_2 = wx.NewIdRef()
ID_RECENT_3 = wx.NewIdRef()
ID_RECENT_4 = wx.NewIdRef()
ID_RECENT_5 = wx.NewIdRef()
ID_RECENT_6 = wx.NewIdRef()
ID_RECENT_7 = wx.NewIdRef()
ID_RECENT_8 = wx.NewIdRef()
ID_RECENT_9 = wx.NewIdRef()

recent_project_ids = [ID_RECENT_0, ID_RECENT_1, ID_RECENT_2, ID_RECENT_3, ID_RECENT_4, ID_RECENT_5, ID_RECENT_6, ID_RECENT_7, ID_RECENT_8, ID_RECENT_9]

ID_New_Experiment = wx.NewIdRef()
ID_New_Experiment_Single = wx.NewIdRef()
ID_New_Experiment_Multiple = wx.NewIdRef()

ID_Save_All = wx.NewIdRef()
ID_Close_Project = wx.NewIdRef()

ID_Next_Experiment = wx.NewIdRef()
ID_Previous_Experiment = wx.NewIdRef()

ID_Config_Colours = wx.NewIdRef()
ID_Config_Markers = wx.NewIdRef()
ID_Config_Borders = wx.NewIdRef()

ID_View_Reset = wx.NewIdRef()
ID_View_Previous = wx.NewIdRef()
ID_View_Rescale_y = wx.NewIdRef()
ID_View_Rescale_x = wx.NewIdRef()
ID_View_Default = wx.NewIdRef()
ID_View_Zoom = wx.NewIdRef()
ID_View_Pan = wx.NewIdRef()
ID_View_Spectrum = wx.NewIdRef()
ID_View_Spectrum_by_rt = wx.NewIdRef()
ID_View_Spectrum_by_num = wx.NewIdRef()
ID_View_Toolbar = wx.NewIdRef()
ID_View_Legend = wx.NewIdRef()
ID_View_Proj_Nav = wx.NewIdRef()
ID_View_Workflow = wx.NewIdRef()

ID_Format_MassHunter = 4808
ID_Format_WatersRAW = 8218
ID_Format_jcamp = 10544
ID_Format_ThermoRAW = 13336
ID_Format_mzML = 25588
ID_Format_ANDI = 12878

ID_Method_Menu = wx.NewIdRef()
ID_Method_Menu_New = wx.NewIdRef()
ID_Method_Menu_Open = wx.NewIdRef()
ID_Method_Menu_Save = wx.NewIdRef()
ID_Method_Menu_Save_As = wx.NewIdRef()
ID_Method_Menu_Close = wx.NewIdRef()

ID_Method_Menu_Help = wx.NewIdRef()
ID_Method_Menu_Help_Help = wx.NewIdRef()

ID_Spec_Viewer_Previous_Experiment = wx.NewIdRef()
ID_Spec_Viewer_Next_Experiment = wx.NewIdRef()
ID_Spec_Viewer_View_Reset = wx.NewIdRef()
ID_Spec_Viewer_View_Previous = wx.NewIdRef()
ID_Spec_Viewer_View_Default = wx.NewIdRef()
ID_Spec_Viewer_View_Zoom = wx.NewIdRef()
ID_Spec_Viewer_View_Pan = wx.NewIdRef()
ID_Spec_Viewer_by_num = wx.NewIdRef()
ID_Spec_Viewer_by_rt = wx.NewIdRef()
ID_Spec_Viewer_Save = wx.NewIdRef()
ID_Spec_Viewer_Copy_Image = wx.NewIdRef()
ID_Spec_Viewer_Copy_Data = wx.NewIdRef()

ID_RemoveAlignmentData = wx.NewIdRef()
ID_RemoveIdentData = wx.NewIdRef()
ID_RemoveConsolidateData = wx.NewIdRef()

ID_Tools_MethodEditor = wx.NewIdRef()
ID_Tools_AmmunitionEditor = wx.NewIdRef()

ID_Export = wx.NewIdRef()
ID_Export_PDF = wx.NewIdRef()


# cleanup
del ascii_lowercase
del wx
