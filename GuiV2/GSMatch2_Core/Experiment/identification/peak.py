#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  peak.py
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
from pyms.Peak import Peak
from pyms_nist_search import SearchResult


class QualifiedPeak(Peak):
	"""
	A Peak that has been identified using NIST MS Search and contains a list of possible identities
	"""
	
	def __init__(self, rt=0.0, ms=None, minutes=False, outlier=False, hits=None, peak_number=None):
		"""
		:param rt: Retention time
		:type rt: int or float
		:param ms: Either an ion mass, a mass spectrum or None
		:type ms: int or float or class`pyms.Spectrum.MassSpectrum`, optional
		:param minutes: Retention time units flag. If True, retention time
			is in minutes; if False retention time is in seconds
		:type minutes: bool, optional
		:param outlier: Whether the peak is an outlier
		:type outlier: bool, optional
		"""
		
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
					['', '', '', '', str(hit.match_factor), str(hit.reverse_match_factor), hit.name, hit.cas]
					)
		return csv
	
	@Peak.rt.setter
	def rt(self, value):
		self._rt = value
	
	def __repr__(self):
		return f"Qualified Peak: {self.rt}"
	
	def __str__(self):
		return self.__repr__()
