#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  consolidate.py
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
from json import JSONEncoder

# 3rd party
import numpy
from pyms.Base import pymsBaseClass
from pyms.Spectrum import MassSpectrum, Scan


class ConsolidateEncoder(JSONEncoder):
	"""
	Custom JSON Encoder to support Consolidate
	"""
	
	def default(self, obj):
		if isinstance(obj, (Scan, MassSpectrum, ConsolidatedSearchResult, ConsolidatedPeak)):
			return dict(obj)
		elif isinstance(obj, numpy.integer):
			return int(obj)
		elif isinstance(obj, numpy.floating):
			return float(obj)
		elif isinstance(obj, numpy.ndarray):
			return obj.tolist()
		else:
			JSONEncoder.default(self, obj)


class ConsolidatedPeak(pymsBaseClass):
	"""
	A Peak that has been produced by consolidating the properties and search results of several qualified peaks

	Models a signal peak

	:param rt_list: Retention time list
	:type rt_list: list of int or float
	:param ms: Either an ion mass, a mass spectrum or None
	:type ms: int or float or class`pyms.Spectrum.MassSpectrum`, optional
	:param minutes: Retention time units flag. If True, retention time
		is in minutes; if False retention time is in seconds
	:type minutes: bool, optional
	# TODO: Finish docstring

	:author: Vladimir Likic
	:author: Andrew Isaac
	:author: Dominic Davis-Foster (type assertions and properties)
	"""
	
	def __init__(self, rt_list, area_list, ms_list, minutes=False, hits=None, peak_number=None):
		
		# TODO: Type check rt_list and ms_list
		# 		if not isinstance(rt, (int, float)):
		# 			raise TypeError("'rt' must be a number")
		#
		# 			if ms and not isinstance(ms, MassSpectrum) and not isinstance(ms, (int, float)):
		# 				raise TypeError("'ms' must be a number or a MassSpectrum object")
		#
		
		if minutes:
			rt_list = [rt * 60.0 for rt in rt_list]
		
		self.rt_list = rt_list
		self.area_list = area_list
		self._ms_list = ms_list
		
		if hits is None:
			self.hits = []
		elif not isinstance(hits, list) or not isinstance(hits[0], ConsolidatedSearchResult):
			raise TypeError("'hits' must be a list of ConsolidatedSearchResult objects")
		else:
			self.hits = hits
		
		self.peak_number = peak_number  # Optional number of the peak in e.g. Alignment
	
	@property
	def rt(self):
		"""
		Return the average retention time

		:return: Retention time
		:rtype: float
		"""
		
		return numpy.nanmean(self.rt_list)
	
	@property
	def rt_stdev(self):
		"""
		Return the standard deviation of the retention time

		:return: Retention time
		:rtype: float
		"""
		
		return numpy.nanstd(self.rt_list)
	
	@property
	def area(self):
		"""
		Gets the average area under the peak

		:return: The peak area
		:rtype: float
		"""
		
		return numpy.nanmean(self.area_list)
	
	@property
	def area_stdev(self):
		"""
		Return the standard deviation of the peak area
		"""
		
		return numpy.nanstd(self.area_list)
	
	def __repr__(self):
		return f"Consolidated Peak: {self.rt}"
	
	def __str__(self):
		return self.__repr__()
	
	def __eq__(self, other):
		"""
		Return whether this ConsolidatedPeak object is equal to another object

		:param other: The other object to test equality with
		:type other: object

		:rtype: bool
		"""
		
		if isinstance(other, self.__class__):
			if self.rt_list == other.rt_list and self.area_list == other.area_list:
				return self._ms_list == other._ms_list
			return False
		else:
			return NotImplemented
	
	def __dict__(self):
		return dict(
				rt_list=self.rt_list,
				area_list=self.area_list,
				ms_list=self._ms_list,
				hits=self.hits,
				peak_number=self.peak_number,
				)
	
	def __iter__(self):
		for key, value in self.__dict__().items():
			yield key, value
	
	def __getstate__(self):
		return self.__dict__()
	
	def __setstate__(self, state):
		self.__init__(**state)

#
# def to_csv(self):
# 	area = '{:,}'.format(self.get_area() / 60)
# 	csv = [[str(self.get_rt() / 60), area, '', '', '', '', '', '', '']]
# 	for hit in self.hits:
# 		csv.append(
# 				['', '', '', hit.library, str(hit.match_factor), str(hit.reverse_match_factor), hit.name, hit.cas]
# 				)
# 	return csv


# @property
# def mass_spectrum(self):
# 	"""
# 	Gets the mass spectrum at the apex of the peak
#
# 	:return: The mass spectrum at the apex of the peak
# 	:rtype: pyms.Spectrum.MassSpectrum
# 	"""
#
# 	# TODO: Combine the mass spectra


class ConsolidatedSearchResult:
	def __init__(self, name='', cas='', mf_list=None, rmf_list=None, hit_numbers=None):
		
		self._name = name
		self.mf_list = mf_list
		self.rmf_list = rmf_list
		self.hit_numbers = hit_numbers
		
		if cas == "0-00-0":
			cas = "---"
		self._cas = cas
	
	@property
	def name(self):
		return self._name
	
	@property
	def cas(self):
		return self._cas
	
	@property
	def match_factor(self):
		return numpy.nanmean(self.mf_list)
	
	@property
	def match_factor_stdev(self):
		return numpy.nanstd(self.mf_list)
	
	@property
	def reverse_match_factor(self):
		return numpy.nanmean(self.rmf_list)
	
	@property
	def reverse_match_factor_stdev(self):
		return numpy.nanstd(self.rmf_list)
	
	@property
	def average_hit_number(self):
		return numpy.nanmean(self.hit_numbers)
	
	@property
	def hit_number_stdev(self):
		return numpy.nanstd(self.hit_numbers)
	
	def __len__(self):
		return numpy.count_nonzero(~numpy.isnan(self.hit_numbers))
	
	def __repr__(self):
		return f"Consolidated Search Result: {self.name} \tmf={self.match_factor}\tn={len(self)}"
	
	def __str__(self):
		return self.__repr__()
	
	def __dict__(self):
		return dict(
				name=self._name,
				mf_list=self.mf_list,
				rmf_list=self.rmf_list,
				hit_numbers=self.hit_numbers,
				cas=self._cas,
				)
	
	def __iter__(self):
		for key, value in self.__dict__().items():
			yield key, value
	
	def __getstate__(self):
		return self.__dict__()
	
	def __setstate__(self, state):
		self.__init__(**state)

