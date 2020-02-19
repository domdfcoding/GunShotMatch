#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  utils.py
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

# stdlib
import base64
from io import BytesIO

# 3rd party
from PIL import Image


def Image2Base64(image):
	if isinstance(image, Image.Image):
		buf = BytesIO()
		image.save(buf, format="JPEG")
		return base64.b64encode(buf.getvalue()).decode("utf-8")


def Base642Image(b64string):
	if isinstance(b64string, str):
		b64string = b64string.encode("utf-8")
	if b64string is not None:
		try:
			return Image.open(BytesIO(base64.b64decode(b64string)))
		except OSError:
			return
