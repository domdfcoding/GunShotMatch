#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  types.py
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
import decimal
import json

# 3rd party
import sqlalchemy.types as types


class DecimalType(types.TypeDecorator):
	"""
	Converts Decimal objects to strings on the way in and back to Decimal objects on the way out
	"""
	
	impl = types.String
	
	def process_bind_param(self, value, dialect):
		if value is None:
			return None
		return str(value)
	
	def process_result_value(self, value, dialect):
		if value is None:
			return None
		return decimal.Decimal(value)
	
	def copy(self, **kw):
		return self.__class__(self.impl.length)


class ListType(types.TypeDecorator):
	"""
	Converts lists to strings using json.dumps() on the way in and back to lists on the way out
	"""
	
	impl = types.String
	
	def process_bind_param(self, value, dialect):
		return json.dumps(value)
	
	def process_result_value(self, value, dialect):
		return json.loads(value)
	
	def copy(self, **kw):
		return self.__class__(self.impl.length)

#