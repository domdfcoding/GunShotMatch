#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  peak_filter.py
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
from importlib_resources import path

# this package
import GSMatch.lib


class ConsolidatePeakFilter:
	min_similarity = 0  # Average match factor between samples
	min_match_factor = 0
	min_reverse_match_factor = 0
	
	min_samples = 0  # Number of samples peak must be present in
	
	filter_by_cas = False
	cas_numbers = set()
	
	def __init__(self):
		self.load_default_cas()
	
	def load_default_cas(self):
		"""Get list of CAS Numbers for compounds reported in literature"""
		with path(GSMatch.lib, "CAS.txt") as cas_list_file:
			with open(str(cas_list_file)) as f:
				raw_cas_numbers = f.readlines()
		for index, CAS in enumerate(raw_cas_numbers):
			CAS = CAS.rstrip("\r\n")
			if CAS:
				self.cas_numbers.add(int(CAS))
	
	def check_cas_number(self, cas):
		if self.filter_by_cas:
			return int(cas.replace("-", "")) in self.cas_numbers
		else:
			return True
	
	filter_by_rt = False
	min_rt = 0
	max_rt = -1
	
	def check_rt(self, rt):
		"""

		:param rt:
		:type rt:

		:return: True if the retention time is within the defined range
		:rtype:
		"""
		
		if self.filter_by_rt:
			if self.max_rt == -1:
				return rt >= self.min_rt
			else:
				return self.min_rt <= rt <= self.max_rt
		else:
			return True
	
	filter_by_area = False
	min_area = 0
	max_area = -1
	
	def check_area(self, area):
		"""

		:param area:
		:type area:

		:return: True if the peak area is within the defined range
		:rtype:
		"""
		
		if self.filter_by_area:
			if self.max_area == -1:
				return area >= self.min_area
			else:
				return self.min_area <= area <= self.max_area
		else:
			return True
