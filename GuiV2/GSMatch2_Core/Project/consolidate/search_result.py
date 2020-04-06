#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  search_result.py
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
import json
import urllib.parse

# 3rd party
import numpy
from pyms_nist_search import ReferenceData

# This package
from . import encoder


class ConsolidatedSearchResult:
	def __init__(self, name='', cas='', mf_list=None, rmf_list=None, hit_numbers=None, reference_data=None):
		"""
		Not currently copying hit_prob from SearchResult
		
		:param name:
		:type name:
		:param cas:
		:type cas:
		:param mf_list:
		:type mf_list:
		:param rmf_list:
		:type rmf_list:
		:param hit_numbers:
		:type hit_numbers:
		"""
		self._name = name
		
		self.mf_list = mf_list if mf_list else []
		self.rmf_list = rmf_list if rmf_list else []
		self.hit_numbers = hit_numbers if hit_numbers else []
		
		if cas == "0-00-0":
			cas = "---"
		self._cas = cas
		
		if reference_data:
			if isinstance(reference_data, dict):
				if set(reference_data.keys()) != {"name", "cas", "formula", "contributor", "nist_no", "id", "mw", "mass_spec", "synonyms"}:
					print(set(reference_data.keys()))
					raise TypeError(
							"'reference_data' must be a `pyms_nist_search.ReferenceData` object, "
							"a dictionary representing a `ReferenceData` object, "
							"or `None`"
							)
				else:
					reference_data = ReferenceData(**reference_data)
			if not isinstance(reference_data, ReferenceData):
				raise TypeError(
						"'reference_data' must be a `pyms_nist_search.ReferenceData` object, "
						"a dictionary representing a `ReferenceData` object, "
						"or `None`"
						)
		
		self._reference_data = reference_data
	
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
	
	@property
	def reference_data(self):
		return self._reference_data
		
	def __len__(self):
		return numpy.count_nonzero(~numpy.isnan(self.hit_numbers))
	
	def __repr__(self):
		return f"Consolidated Search Result: {self.name} \tmf={self.match_factor}\tn={len(self)}"
	
	def __str__(self):
		return self.__repr__()
	
	def __dict__(self, recursive=False):
		class_dict = dict(
				name=self._name,
				cas=self._cas,
				mf_list=self.mf_list,
				rmf_list=self.rmf_list,
				hit_numbers=self.hit_numbers,
				)
		if recursive:
			class_dict["reference_data"] = self.reference_data.__dict__(recursive=True)
		else:
			class_dict["reference_data"] = self.reference_data
			
		return class_dict
	
	def __iter__(self):
		for key, value in self.__dict__().items():
			yield key, value
	
	def __getstate__(self):
		return self.__dict__()
	
	def __setstate__(self, state):
		self.__init__(**state)
	
	@classmethod
	def from_json(cls, json_data):
		peak_dict = json.load(json_data)
		
		return cls.from_dict(peak_dict)
	
	@classmethod
	def from_dict(cls, dictionary):
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
