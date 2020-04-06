#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  encoder.py
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
import numpy
from pyms_nist_search.json import PyNISTEncoder

# this package
from .peak import ConsolidatedPeak
from .search_result import ConsolidatedSearchResult


class ConsolidateEncoder(PyNISTEncoder):
	"""
	Custom JSON Encoder to support Consolidate
	"""
	
	def default(self, obj):
		if isinstance(obj, (ConsolidatedSearchResult, ConsolidatedPeak)):
			return obj.__dict__(recursive=True)
		elif isinstance(obj, numpy.integer):
			return int(obj)
		elif isinstance(obj, numpy.floating):
			return float(obj)
		elif isinstance(obj, numpy.ndarray):
			return obj.tolist()
		else:
			super().default(obj)

