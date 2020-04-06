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

# stdlib
import copy
import json
import urllib.parse
import warnings
from itertools import groupby
from numbers import Number

# 3rd party
import numpy
import pandas
from pyms.Base import pymsBaseClass
from pyms.Spectrum import MassSpectrum

# This package
from . import encoder
from .search_result import ConsolidatedSearchResult


class ConsolidatedPeak(pymsBaseClass):
	"""
	A Peak that has been produced by consolidating the properties and search results of several qualified peaks

	Models a signal peak

	:param rt_list: Retention time list
	:type rt_list: list of int or float
	:param ms_list: List of Mass Spectra
	:type ms_list: list of class`pyms.Spectrum.MassSpectrum`
	:param minutes: Retention time units flag. If True, retention time
		is in minutes; if False retention time is in seconds
	:type minutes: bool, optional
	# TODO: Finish docstring

	:author: Vladimir Likic
	:author: Andrew Isaac
	:author: Dominic Davis-Foster (type assertions and properties)
	"""
	
	def __init__(self, rt_list, area_list, ms_list, minutes=False, hits=None, peak_number=None, ms_comparison=None, hidden=False):
		
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
		self.ms_list = ms_list
		self.hidden = hidden
		
		if ms_comparison is None:
			self.ms_comparison = pandas.Series()
		elif isinstance(ms_comparison, pandas.Series):
			self.ms_comparison = ms_comparison
		elif isinstance(ms_comparison, dict):
			self.ms_comparison = pandas.Series(ms_comparison)
		else:
			raise TypeError("'ms_comparison' must be a dict or a pandas.Series")
		
		# print(self.ms_comparison)
		
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
		
		# return numpy.nanmean(self.rt_list)
		return self._average_rt
	
	@property
	def rt_stdev(self):
		"""
		Return the standard deviation of the retention time

		:return: Retention time
		:rtype: float
		"""
		
		# return numpy.nanstd(self.rt_list)
		return self._rt_stdev
	
	@property
	def rt_list(self):
		return self._rt_list[:]
	
	@rt_list.setter
	def rt_list(self, value):
		type_err_msg = f"""

'rt_list' must be a list, tuple or class:`pandas.Series` of int or float objects.
"""
		if not isinstance(value, (list, tuple, pandas.Series)) or not all(
				isinstance(rt, Number) or rt is None for rt in value):
			raise TypeError(f"Invalid Type: {type(value)} of {type(value[0])}!{type_err_msg}")
		
		self._rt_list = value
		
		self._calculate_rt_stats()
	
	def _calculate_rt_stats(self):
		self._average_rt = numpy.nanmean(self.rt_list)
		self._rt_stdev = numpy.nanstd(self.rt_list)
	
	@property
	def area(self):
		"""
		Gets the average area under the peak

		:return: The peak area
		:rtype: float
		"""
		
		return self._average_area
	
	@property
	def area_stdev(self):
		"""
		Return the standard deviation of the peak area
		"""
		
		return self._area_stdev
	
	@property
	def area_list(self):
		return self._area_list[:]
	
	@area_list.setter
	def area_list(self, value):
		if not isinstance(value, (list, tuple, pandas.Series)) or not all(
				isinstance(area, Number) or area is None for area in value):
			raise TypeError(f"""Invalid Type: {type(value)} of {type(value[0])}!

'area_list' must be a list, tuple or class:`pandas.Series` of int or float objects.""")
		
		self._area_list = value
		
		self._calculate_area_stats()
	
	def _calculate_area_stats(self):
		self._average_area = numpy.nanmean(self.area_list)
		self._area_stdev = numpy.nanstd(self.area_list)
	
	@property
	def average_ms_comparison(self):
		# return numpy.nanmean(self.ms_comparison)
		return self._average_ms_comparison
	
	@property
	def ms_comparison_stdev(self):
		# return numpy.nanstd(self.ms_comparison)
		return self._ms_comparison_stdev
	
	@property
	def ms_comparison(self):
		return self._ms_comparison[:]
	
	@ms_comparison.setter
	def ms_comparison(self, value):
		if not isinstance(value, (list, tuple, pandas.Series)) or not all(
				isinstance(area, Number) or area is None for area in value):
			raise TypeError(f"""Invalid Type: {type(value)} of {type(value[0])}!

'ms_comparison' must be a list, tuple or class:`pandas.Series` of int or float objects.""")
		
		self._ms_comparison = value
		
		self._calculate_similarity_stats()
	
	def _calculate_similarity_stats(self):
		if self.ms_comparison.empty:
			self._average_ms_comparison = 0
			self._ms_comparison_stdev = 0
		else:
			self._average_ms_comparison = numpy.nanmean(self.ms_comparison)
			self._ms_comparison_stdev = numpy.nanstd(self.ms_comparison)
	
	@property
	def ms_list(self):
		return self._ms_list[:]
	
	@ms_list.setter
	def ms_list(self, value):
		type_err_msg = f"""

	'ms_list' must be a list, tuple or class:`pandas.Series` of class`pyms.Spectrum.MassSpectrum` objects.
	Alternatively, the sequence may consist of dictionary objects that can be converted to MassSpectrum objects.
	"""
		if not isinstance(value, (list, tuple, pandas.Series)) or not all(
				isinstance(ms, (MassSpectrum, dict)) or ms is None for ms in value):
			raise TypeError(f"Invalid Type: {type(value)} of {type(value[0])}!{type_err_msg}")
		
		ms_list = []
		
		for ms in value:
			
			if isinstance(ms, MassSpectrum):
				ms_list.append(ms)
			elif isinstance(ms, dict):
				if "intensity_list" in ms and "mass_list" in ms:
					ms_list.append(MassSpectrum(**ms))
			elif ms is None:
				ms_list.append(None)
			else:
				raise TypeError(f"Unrecognised Type: {type(value)} of {type(ms)}!{type_err_msg}")
		
		self._ms_list = ms_list
		
		self._calculate_spectra()
	
	def _calculate_spectra(self):
		"""
		Calculate Combined and Averaged spectra
		"""
		
		mass_lists = []
		intensity_lists = []
		
		for spec in self._ms_list:
			
			if spec:
				# print(spec.mass_list)
				mass_lists.append(spec.mass_list)
				intensity_lists.append(spec.intensity_list)
			else:
				# print()
				pass
		
		if all_equal(mass_lists):
			mass_list = mass_lists[0]
			# print(intensity_lists)
			combined_intensity_list = list(sum(map(numpy.array, intensity_lists)))
			self._combined_mass_spectrum = MassSpectrum(
					mass_list=mass_list,
					intensity_list=combined_intensity_list
					)
			
			# averaged_intensity_list = [intensity / len(mass_lists) for intensity in combined_intensity_list]
			
			averaged_intensity_list = []
			avg_intensity_array = numpy.array(intensity_lists)
			for column in avg_intensity_array.T:
				if sum(column) == 0 or numpy.count_nonzero(column) == 0:
					averaged_intensity_list.append(0)
				else:
					averaged_intensity_list.append(sum(column) / numpy.count_nonzero(column))
			
			self._averaged_mass_spectrum = MassSpectrum(
					mass_list=mass_list,
					intensity_list=averaged_intensity_list
					)
		
		else:
			warnings.warn("Mass Ranges Differ. Unable to process")
			self._combined_mass_spectrum = None
			self._averaged_mass_spectrum = None
	
	@property
	def combined_mass_spectrum(self):
		return self._combined_mass_spectrum
	
	@property
	def averaged_mass_spectrum(self):
		return self._averaged_mass_spectrum

	@property
	def hidden(self):
		"""
		Returns whether the peak should be hidden
		
		:rtype: bool
		"""
		
		return self._hidden
	
	@hidden.setter
	def hidden(self, value):
		"""
		Sets whether the peak should be hidden
		
		:type value: bool
		"""

		self._hidden = bool(value)
	
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
	
	def __dict__(self, recursive=False):
		class_dict = dict(
				rt_list=self.rt_list,
				area_list=self.area_list,
				hits=self.hits,
				peak_number=self.peak_number,
				hidden=self.hidden,
				)
		
		if recursive:
			class_dict["hits"] = [hit.__dict__(recursive=True) for hit in self.hits]
			class_dict["ms_list"] = [dict(ms) if ms else None for ms in self.ms_list]
			class_dict["ms_comparison"] = self.ms_comparison.to_dict()
		else:
			class_dict["hits"] = self.hits
			class_dict["ms_list"] = self.ms_list
			class_dict["ms_comparison"] = self.ms_comparison
		
		return class_dict
	
	def __iter__(self):
		for key, value in self.__dict__().items():
			yield key, value
	
	def __getstate__(self):
		return self.__dict__()
	
	def __setstate__(self, state):
		self.__init__(**state)
	
	def __len__(self):
		return numpy.count_nonzero(~numpy.isnan(self.rt_list))
	
	@classmethod
	def from_json(cls, json_data):
		peak_dict = json.load(json_data)
		
		return cls.from_dict(peak_dict)

	@classmethod
	def from_dict(cls, dictionary):
		dictionary = copy.deepcopy(dictionary)
		
		for hit_idx, hit in enumerate(dictionary["hits"]):
			# print(hit["reference_data"])
			dictionary["hits"][hit_idx] = ConsolidatedSearchResult(**hit)
		
		return cls(**dictionary)
	
	def to_json(self):
		return json.dumps(self, cls=encoder.ConsolidateEncoder)
	
	def quoted_string(self):
		return urllib.parse.quote(self.to_json())
	
	@classmethod
	def from_quoted_string(cls, string):
		json_peak = urllib.parse.unquote(string)
		peak_dict = json.loads(json_peak)
		
		return cls.from_dict(peak_dict)
	

#
# def to_csv(self):
# 	area = '{:,}'.format(self.get_area() / 60)
# 	csv = [[str(self.get_rt() / 60), area, '', '', '', '', '', '', '']]
# 	for hit in self.hits:
# 		csv.append(
# 				['', '', '', hit.library, str(hit.match_factor), str(hit.reverse_match_factor), hit.name, hit.cas]
# 				)
# 	return csv


def all_equal(iterable):
	"""
	Returns True if all the elements are equal to each other

	From https://docs.python.org/3/library/itertools.html#recipes

	:param iterable:
	:type iterable:
	:return:
	:rtype:
	"""
	
	g = groupby(iterable)
	return next(g, True) and not next(g, False)
