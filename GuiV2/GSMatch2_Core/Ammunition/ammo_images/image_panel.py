#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  ammunition_image_panel.py
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
import wx
from domdf_wxpython_tools import imagepanel

# this package
from GuiV2.GSMatch2_Core.Ammunition import ammo_images


class AmmoImagePanel(imagepanel.ImagePanel):
	def __init__(
			self, parent, image=None, id=wx.ID_ANY, pos=wx.DefaultPosition,
			size=wx.DefaultSize, style=0, name="AmmoImagePanel"):
		"""
		:param parent: The parent window.
		:type parent: wx.Window
		:param image:
		:type image:
		:param id: An identifier for the panel. wx.ID_ANY is taken to mean a default.
		:type id: wx.WindowID, optional
		:param pos: The panel position. The value wx.DefaultPosition indicates a default position,
		chosen by either the windowing system or wxWidgets, depending on platform.
		:type pos: wx.Point, optional
		:param size: The panel size. The value wx.DefaultSize indicates a default size, chosen by
		either the windowing system or wxWidgets, depending on platform.
		:type size: wx.Size, optional
		:param style: The window style. See wx.Panel.
		:type style: int, optional
		:param name: Window name.
		:type name: str, optional
		"""
		
		imagepanel.ImagePanel.__init__(self, parent, image, id, pos, size, style, name)
		
		self.exchange_submenu = wx.Menu()
		
		self.exchange_submenu.Append(ammo_images.ID_Exchange_Headstamp, "Headstamp")
		self.exchange_submenu.Append(ammo_images.ID_Exchange_Propellant, "Propellant")
		
		self.context_menu.Insert(
				6,
				ammo_images.ID_Exchange_Propellant,
				"Exchange with 'Propellant'")
		self.context_menu.Insert(
				6,
				ammo_images.ID_Exchange_Headstamp,
				"Exchange with 'Headstamp'")
		self.context_menu.Insert(
				6,
				ammo_images.ID_Send2_Other,
				"Send to 'Other Images'")

	def remove_headstamp_option(self):
		self.context_menu.Delete(ammo_images.ID_Exchange_Headstamp)
		
	def remove_propellant_option(self):
		self.context_menu.Delete(ammo_images.ID_Exchange_Propellant)
