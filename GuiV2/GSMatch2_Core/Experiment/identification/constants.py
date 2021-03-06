#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  constants.py
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

import wx


Sort_RT = ID_Sort_RT = wx.NewIdRef()
Sort_Area = ID_Sort_Area = wx.NewIdRef()
Sort_Similarity = ID_Sort_Similarity = wx.NewIdRef()
Sort_Experiments = ID_Sort_Experiments = wx.NewIdRef()
Sort_Hit = ID_Sort_Hit = wx.NewIdRef()
Sort_Name = ID_Sort_Name = wx.NewIdRef()
Sort_MF = ID_Sort_MF = wx.NewIdRef()
Sort_RMF = ID_Sort_RMF = wx.NewIdRef()
Sort_CAS = ID_Sort_CAS = wx.NewIdRef()

# cleanup
del wx
