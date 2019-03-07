#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  dummy.py
#  
#  Copyright 2019 dom13 <dom13@DOM-XPS>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
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

#import wx
import time
import uibar as progressbar

def dummy(main_window):
	bar = progressbar.ProgressBar("Analysis in progress", 100, main_window)
	for i in range(100):
		time.sleep(2)
		bar.update(i+1)
	bar.finish()
