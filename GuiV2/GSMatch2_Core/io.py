#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  io.py
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
import json
import pathlib
import tarfile
from io import BytesIO

# this package
from GuiV2.GSMatch2_Core.InfoProperties import Property


def load_info_json(filename):
	"""
	Load the info.json file from the given experiment or Project

	Based on https://stackoverflow.com/a/23308087

	:param filename:
	:type filename:

	:return: parsed info.json
	:rtype: dict
	"""
	
	if isinstance(filename, (str, pathlib.Path)):
		filename = tarfile.open(str(filename), "r")
	elif isinstance(filename, BytesIO):
		filename = tarfile.open(fileobj=filename, mode="r")
	elif isinstance(filename, Property):
		filename = tarfile.open(filename.value, mode="r")
	elif not isinstance(filename, tarfile.TarFile):
		raise TypeError(
				f"'filename' must be a string, GuiV2.GSMatch2_Core.InfoProperties.Property, pathlib.Path, "
				f"io.BytesIO or tarfile.TarFile object, not {type(filename)}."
				)
	
	info_json = json.load(get_file_from_archive(filename, "info.json"))
	filename.close()
	return info_json


def get_file_from_archive(archive, filename):
	"""
	Returns the given file from the given archive

	Based on https://stackoverflow.com/a/23308087

	:param archive:
	:type archive:
	:param filename:
	:type filename:

	:return:
	:rtype:
	"""
	
	if isinstance(archive, (str, pathlib.Path)):
		archive = tarfile.open(str(archive), "r")
	elif isinstance(archive, BytesIO):
		archive.seek(0)
		archive = tarfile.open(fileobj=archive, mode="r")
	elif not isinstance(archive, tarfile.TarFile):
		raise TypeError(
				f"'archive' must be a string, pathlib.Path, io.BytesIO or tarfile.TarFile object, not {type(archive)}.")
	
	extracted_file = archive.extractfile(dict(zip(
			archive.getnames(),
			archive.getmembers()
			))[filename])
	
	return extracted_file
