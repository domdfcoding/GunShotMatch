#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  build_rst.py
#
"""
Build .rst source files to HTML
"""
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

# 3rd party
from docutils.core import publish_file


for file in [
	"./GSMatch/lib/CREDITS",
	"./GSMatch/lib/licenses/LICENSE_CC_BY_SA_3.0",
	"./GSMatch/lib/licenses/LICENSE_CC_BY_SA_4.0",
	"./GSMatch/lib/licenses/LICENSE_GPL2",
	"./GSMatch/lib/licenses/LICENSE_GPL3",
	"./GSMatch/lib/licenses/LICENSE_MIT",
	
]:
	
	publish_file(source_path=f"{file}.rst", destination_path=f"{file}.html", writer_name="html")