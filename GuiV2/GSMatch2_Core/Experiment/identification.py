#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  identification.py
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2020  Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
from pyms.Peak import Peak


class QualifiedPeak(Peak):
	"""
	A Peak that has been identified using NIST MS Search and contains a list of possible identities
	"""
	def __init__(self, rt=0.0, ms=None, minutes=False, outlier=False, hits=None, peak_number=None):
		Peak.__init__(self, rt, ms, minutes, outlier)
		
		if hits is not None:
			if not isinstance(hits, list) or not isinstance(hits[0], SearchResult):
				raise TypeError("'hits' must be a list of SearchResult objects")
		
		if hits is None:
			self.hits = []
		else:
			self.hits = hits
		
		self.peak_number = peak_number  # Optional number of the peak in e.g. Alignment
	
	@classmethod
	def from_peak(cls, peak):
		if not isinstance(peak, Peak):
			raise TypeError("'peak' must be a Peak object")
		
		if peak.ic_mass:
			new_peak = cls(peak.rt, peak.ic_mass, False, peak.is_outlier)
		else:
			new_peak = cls(peak.rt, peak.mass_spectrum, False, peak.is_outlier)
		new_peak.area = peak.area
		new_peak.bounds = peak.bounds
		new_peak._UID = peak.UID
		
		return new_peak
	
	def to_csv(self):
		area = '{:,}'.format(self.area / 60)
		csv = [[str(self.rt / 60), area, '', '', '', '', '', '', '']]
		for hit in self.hits:
			csv.append(
					['', '', '', hit.library, str(hit.match_factor), str(hit.reverse_match_factor), hit.name, hit.cas]
					)
		return csv
	
	@Peak.rt.setter
	def rt(self, value):
		self._Peak__rt = value
	
	def __repr__(self):
		return f"Qualified Peak: {self.rt}"
	
	def __str__(self):
		return self.__repr__()
		
		
class SearchResult:
	def __init__(self, name='', cas='', library='', match_factor=0, reverse_match_factor=0):
		self._name = name
		
		if cas == "0-00-0":
			cas = "---"
		self._cas = cas
		
		self._library = library
		self._match_factor = int(match_factor)
		self._reverse_match_factor = int(reverse_match_factor)
	
	@property
	def name(self):
		return self._name
	
	@property
	def cas(self):
		return self._cas
	
	@property
	def library(self):
		return self._library
	
	@property
	def match_factor(self):
		return int(self._match_factor)
	
	@property
	def reverse_match_factor(self):
		return int(self._reverse_match_factor)
	
	@classmethod
	def from_pynist(cls, pynist_dict):
		return cls(
				library=pynist_dict["Lib"],
				match_factor=pynist_dict["MF"],
				reverse_match_factor=pynist_dict["RMF"],
				cas=pynist_dict["CAS"],
				name=pynist_dict["Name"].replace(";", ":"),
				)
	
	def __repr__(self):
		return f"Search Result: {self.name} \t({self.match_factor})"
	
	def __str__(self):
		return self.__repr__()
