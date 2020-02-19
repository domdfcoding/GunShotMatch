#!/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  filename.py
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Based on the wxPython Demo by Robin Dunn
#  Copyright (c) 1999-2018 by Total Control Software
#  Licenced under the wxWindows Licence
#
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
#

import os
import re


# ---------------------------------------------------------------------------

def replace_capitals(string):
	"""
	Replaces the capital letter in a string with an underscore plus the
	corresponding lowercase character.

	:param string: the string to be analyzed
	:type string: str
	:return:
	:rtype:
	"""
	
	newString = ""
	for char in string:
		if char.isupper():
			newString += f"_{char.lower()}"
		else:
			newString += char
	
	return newString


def remove_HTML_tags(data):
	"""
	Removes all the HTML tags from a string.

	:param data: the string to be analyzed.
	:type data:
	:return:
	:rtype:
	"""
	
	p = re.compile(r'<[^<]*?>')
	return p.sub('', data)


def convert_path_sep(path):
	"""Convert paths to the platform-specific separator"""
	split_path = os.path.join(*tuple(path.split('/')))
	# HACK: on Linux, a leading / gets lost...
	if path.startswith('/'):
		split_path = '/' + split_path
	return split_path