#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  constants.py
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
from domdf_wxpython_tools import Wildcards

ID_Select_All = wx.NewIdRef()
ID_Add_Image = wx.NewIdRef()
ID_Paste_Image = wx.NewIdRef()
ID_View_Image = wx.NewIdRef()
ID_Copy_Image = wx.NewIdRef()
ID_Save_Image = wx.NewIdRef()
ID_Delete_Image = wx.NewIdRef()
ID_Exchange_Submenu = wx.NewIdRef()
ID_Exchange_Propellant = wx.NewIdRef()
ID_Exchange_Headstamp = wx.NewIdRef()
ID_Rename_Image = wx.NewIdRef()
ID_Send2_Other = wx.NewIdRef()

images_wildcard = Wildcards()
images_wildcard.add_image_wildcard()
images_wildcard.add_common_filetype("jpeg")
images_wildcard.add_common_filetype("png")
images_wildcard.add_common_filetype("bmp")
images_wildcard.add_common_filetype("tiff")
images_wildcard.add_common_filetype("gif")
images_wildcard.add_all_files_wildcard()

# Tidy up
del wx
del Wildcards