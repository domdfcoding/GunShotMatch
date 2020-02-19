#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  Base.py
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

# stdlib
import getpass
import socket
from io import StringIO
import datetime

# this package
from GuiV2.GSMatch2_Core import Method
from GuiV2.GSMatch2_Core.io import get_file_from_archive, load_info_json
from GuiV2.GSMatch2_Core.watchdog import time_now
from GuiV2.GSMatch2_Core.InfoProperties import longstr, massrange, Property, rtrange


class GSMBase:
	"""
	Base Class for Experiment and Project
	"""
	
	type_string = "GSMBase"
	
	def __init__(
			self, name, method, user, device, date_created, date_modified,
			version, description='', filename=None
			):
		
		self.name = name
		
		self.description = Property(
				f"{name}_description", description, longstr,
				help=f"A description of the {self.type_string}", label="Description"
				)
		
		self.method = Property(
				f"{name}_method", method, dir, editable=False,
				help="The Method file to use"
				)
		
		self.user = Property(
				f"{name}_user", user, str,
				help=f"The user who created the {self.type_string}",
				editable=False, label="User"
				)
		self.device = Property(
				f"{name}_device", device, str,
				help=f"The device that created the {self.type_string}",
				editable=False, label="Device"
				)
		self.date_created = Property(
				f"{name}_date_created", date_created, datetime,
				help=f"The date the {self.type_string} was created",
				editable=False, immutable=True, label="Date Created"
				)
		self.date_modified = Property(
				f"{name}_date_modified", date_modified, datetime,
				help=f"The date the {self.type_string} was last modified",
				editable=False, label="Date Modified"
				)
		self.version = Property(
				f"{name}_version", version, str,
				help=f"The {self.type_string} file format version number",
				editable=False, label="Version"
				)
		self.filename = Property(
				f"{name}_filename", filename, dir,
				help=f"The name of the {self.type_string} file", label="Filename"
				)
		
	@classmethod
	def new_empty(cls):
		"""
		Create a new empty object

		:return:
		:rtype:
		"""
		
		return cls(
				None, None, getpass.getuser(), socket.gethostname(),
				time_now(),
				time_now(),
				"1.0.0"
				)
	
	@classmethod
	def new(cls, name, method, description=None):
		"""
		Create a new object

		:param name:
		:type name:
		:param method:
		:type method:
		:param description:
		:type description:

		:return:
		:rtype:
		"""
		
		return cls(
				name, method, getpass.getuser(), socket.gethostname(),
				date_created=time_now(),
				date_modified=time_now(),
				version="1.0.0", description=description
				)
	
	@property
	def method_data(self):
		"""
		Returns the contents of the method file

		:return:
		:rtype:
		"""
		
		method_text = get_file_from_archive(self.filename.Path, self.method.filename).read().decode("utf-8")
		
		# From https://stackoverflow.com/a/21766494/3092681
		buf = StringIO(method_text)

		method_data = Method.Method(buf)
		buf.close()
		return method_data
	
	@property
	def info_data(self):
		"""
		Returns the contents of the info file

		:return:
		:rtype:
		"""
		
		return load_info_json(self.filename)
	
	def __str__(self):
		return self.__repr__()
	
	def __eq__(self, other):
		if other.__class__ == self.__class__:
			return self.name == other.name and \
				   self.date_created == other.date_created and \
				   self.date_modified == other.date_modified
		else:
			return NotImplemented
	
	@classmethod
	def load(cls, filename):
		"""
		Load from a file

		:param filename:
		:type filename:
		"""
		
		return cls(**load_info_json(filename), filename=filename)



