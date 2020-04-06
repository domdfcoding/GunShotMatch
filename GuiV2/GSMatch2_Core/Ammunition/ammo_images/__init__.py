#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  __init__.py
#
#  This file is part of GunShotMatch
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
from domdf_wxpython_tools.imagepanel import EVT_IMAGE_PANEL_CHANGED
from wx.lib.agw.thumbnailctrl import (
	THUMB_OUTLINE_FULL,
	THUMB_OUTLINE_IMAGE,
	THUMB_OUTLINE_NONE,
	THUMB_OUTLINE_RECT,
	)

# this package
from GuiV2.GSMatch2_Core.Ammunition.ammo_images.constants import *
from GuiV2.GSMatch2_Core.Ammunition.ammo_images.image_panel import AmmoImagePanel
from GuiV2.GSMatch2_Core.Ammunition.ammo_images.other_image_ctrl import (
	EVT_IMAGE_ADDED, EVT_IMAGE_DELETED, EVT_IMAGE_RENAMED, OtherImagesCtrl,
	)
from GuiV2.GSMatch2_Core.Ammunition.ammo_images.utils import Base642Image, Image2Base64

__all__ = [
		"AmmoImagePanel",
		"Image2Base64",
		"Base642Image",
		"OtherImagesCtrl",
		"THUMB_OUTLINE_FULL",
		"THUMB_OUTLINE_IMAGE",
		"THUMB_OUTLINE_NONE",
		"THUMB_OUTLINE_RECT",
		"ID_Select_All",
		"ID_Add_Image",
		"ID_Paste_Image",
		"ID_View_Image",
		"ID_Copy_Image",
		"ID_Save_Image",
		"ID_Delete_Image",
		"ID_Send2_Other",
		"ID_Exchange_Submenu",
		"ID_Exchange_Propellant",
		"ID_Exchange_Headstamp",
		"ID_Rename_Image",
		"images_wildcard",
		"EVT_IMAGE_ADDED",
		"EVT_IMAGE_DELETED",
		"EVT_IMAGE_RENAMED",
		"EVT_IMAGE_PANEL_CHANGED",
		]

