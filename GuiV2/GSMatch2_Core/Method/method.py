#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  method.py
"""
GunShotMatch Method Class
"""
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
import configparser
import io
import re
import datetime
import pathlib

# 3rd party
from domdf_python_tools.utils import list2str, str2tuple

# this package
from GuiV2.GSMatch2_Core.InfoProperties import Property


# TODO: pathlib support

class MethodProperty:
	def __init__(self, category, name, default_value='', type=str):
		"""

		:param category: The category of the property in the Method file
		:type category: str
		:param name: The name of the Property in the method file.
		:type name: str
		:param default_value: The default value for the property if it is not defined in the method file
		:type default_value: any
		:param type: The type of the property
		:type type: object

		The name of the functions object has the following structure:
			_{self.category}_{self.name}
		"""
		
		self.name = str(name)
		self.type = type
		self.value = default_value
		self.category = str(category)
		self.default_value = default_value
	
	def load_property(self, config):
		if self.type == bool:
			self.value = config.getboolean(self.category, self.name, fallback=self.default_value)
		else:
			self.value = config.get(self.category, self.name, fallback=self.default_value)
	
	def save_property(self, config):
		if self.type == tuple:
			config.set(self.category, f"{self.category}_{self.name}", list2str(self.value))
		else:
			config.set(self.category, f"{self.category}_{self.name}", str(self.value))
	
	@property
	def value(self):
		return self._value
	
	@value.setter
	def value(self, value):
		if self.type in {int, float, bool, str}:
			self._value = self.type(value)
		
		# Special case for datetime
		elif self.type == datetime:
			if isinstance(value, datetime.datetime):
				self._value = value.timestamp()
			elif isinstance(value, str):
				self._value = datetime.datetime.strptime(value, "%d/%m/%Y %H:%M:%S").timestamp()
			elif isinstance(value, (int, float)):
				self._value = value
		
		# Special case for directories
		elif self.type == dir:
			if isinstance(value, str):
				self._value = pathlib.Path(value)
			else:
				self._value = value
		
		elif self.type == tuple:
			if isinstance(value, str):
				self._value = str2tuple(value)
			elif isinstance(value, list):
				self._value = tuple(value)
			elif isinstance(value, tuple):
				self._value = value
			else:
				raise TypeError(f"'{self.name}' must be a list, tuple or comma-separated string")
	
	def __get__(self, ins, type):
		return self.value
	
	def __set__(self, ins, value=None):
		if value is None:
			self.value = self.default_value
		elif isinstance(value, configparser.ConfigParser):
			self.load_property(value)
		else:
			self.value = value
		
		setattr(ins, f"_{self.category}_{self.name}", self)


class Method:
	"""
	GunShotMatch Method Class

	:param method_file: .method file to load
	:type method_file: str
	"""
	
	# Experiment Creation Settings
	enable_sav_gol = MethodProperty("expr_creation", "enable_sav_gol", True, bool)
	enable_tophat = MethodProperty("expr_creation", "enable_tophat", True, bool)
	tophat = MethodProperty("expr_creation", "tophat", 1.5, float)
	tophat_unit = MethodProperty("expr_creation", "tophat_unit", "m", str)
	bb_points = MethodProperty("expr_creation", "bb_points", 9, int)
	bb_scans = MethodProperty("expr_creation", "bb_scans", 2, int)
	enable_noise_filter = MethodProperty("expr_creation", "enable_noise_filter", True, bool)
	noise_thresh = MethodProperty("expr_creation", "noise_thresh", 2, int)
	# mass_range = MethodProperty("expr_creation", "mass_range", "50,400", tuple)
	# target_range = MethodProperty("expr_creation", "target_range", "3.0,38.0", tuple)
	# base_peak_filter = MethodProperty("expr_creation", "base_peak_filter", "73,147", tuple)
	
	# Peak Alignment Settings
	rt_modulation = MethodProperty("alignment", "rt_modulation", 2.5, float)
	gap_penalty = MethodProperty("alignment", "gap_penalty", 0.3, float)
	min_peaks = MethodProperty("alignment", "min_peaks", 2, int)
	
	# Project Comparison Settings
	comparison_a = MethodProperty("comparison", "a", 0.05, float)
	comparison_rt_modulation = MethodProperty("comparison", "rt_modulation", 2.5, float)
	comparison_gap_penalty = MethodProperty("comparison", "gap_penalty", 0.3, float)
	comparison_min_peaks = MethodProperty("comparison", "min_peaks", 2, int)
	
	# Compound Identification Settings
	ident_min_match_factor = MethodProperty("ident", "min_match_factor", 300, int)
	ident_min_aligned_peaks = MethodProperty("ident", "min_aligned_peaks", 0, int)
	ident_top_peaks = MethodProperty("ident", "top_peaks", 80, int)
	ident_nist_n_hits = MethodProperty("ident", "nist_n_hits", 10, int)
	ident_min_peak_area = MethodProperty("ident", "min_peak_area", 0, int)
	
	def __init__(self, method_file):
		"""
		Initialise Method class
		
		:param method_file: .ini configuration file to load
		:type method_file: str or io.StringIO
		"""
		
		self.Config = configparser.ConfigParser()
		
		if isinstance(method_file, io.StringIO):
			self._method_file = None
			print(f"Reading method from {method_file}")
			self.Config.read_file(method_file)
		
		elif isinstance(method_file, str):
			self._method_file = method_file
			print(f"Using Method File {self.method_file}")
			self.Config.read(self.method_file)
		
		elif isinstance(method_file, Property):
			self._method_file = method_file.value
			print(f"Using Method File {self.method_file}")
			self.Config.read(self.method_file)
		
		else:
			raise TypeError(
					"'method_file' must be a string, an io.StringIO object, or a "
					":class:`GuiV2.GSMatch2_Core.InfoProperties.Property object"
					)
		
		# Create sections if not present
		if "expr_creation" not in self.Config:
			self.Config["expr_creation"] = {}
		if "alignment" not in self.Config:
			self.Config["alignment"] = {}
		if "comparison" not in self.Config:
			self.Config["comparison"] = {}
		if "ident" not in self.Config:
			self.Config["ident"] = {}
			
		# Experiment Creation Settings
		self.mass_range = self.Config.get("expr_creation", "mass_range")
		# self.enable_sav_gol = self.Config.getboolean("expr_creation", "enable_sav_gol")
		# self.enable_tophat = self.Config.getboolean("expr_creation", "enable_tophat")
		# self.tophat = self.Config.get("expr_creation", "tophat")
		# self.tophat_unit = self.Config.get("expr_creation", "tophat_unit")
		# self._tophat_struct = "{}{}".format(self.tophat, self.tophat_unit)
		# self.enable_noise_filter = self.Config.getboolean("expr_creation", "enable_noise_filter")
		# self.noise_thresh = self.Config.get("expr_creation", "noise_thresh")
		# self.bb_points = self.Config.get("expr_creation", "bb_points")
		# self.bb_scans = self.Config.get("expr_creation", "bb_scans")
		self.target_range = self.Config.get("expr_creation", "target_range")
		self.base_peak_filter = self.Config.get("expr_creation", "exclude_ions")
		# self.mass_range = self.Config
		self.enable_sav_gol = self.Config
		self.enable_tophat = self.Config
		self.tophat = self.Config
		# The value for the Tophat baseline correction structural element
		#
		# The structural element needs to be larger than the features one wants
		# to retain in the spectrum after the top-hat transform
		
		self.tophat_unit = self.Config
		# The unit for the Tophat baseline correction structural element
		
		self.bb_points = self.Config
		# Returns the value for the window width, in data points, for detecting
		# local maxima during Biller and Biemann Peak Detection
		
		self.bb_scans = self.Config
		# Returns the value for the number of scans across which neighbouring,
		# apexing ions and combined and considered as belonging to the same peak
		
		self.enable_noise_filter = self.Config
		self.noise_thresh = self.Config
		# self.target_range = self.Config
		# self.base_peak_filter = self.Config
		
		# Peak Alignment Settings
		# self.rt_modulation = self.Config.get("alignment", "rt_modulation")
		# self.gap_penalty = self.Config.get("alignment", "gap_penalty")
		# self.min_peaks = self.Config.get("alignment", "min_peaks")
		self.rt_modulation = self.Config
		self.gap_penalty = self.Config
		self.min_peaks = self.Config
		
		# Project Comparison Settings
		# self.comparison_a = self.Config.get("comparison", "a")
		# self.comparison_rt_modulation = self.Config.get("comparison", "rt_modulation")
		# self.comparison_gap_penalty = self.Config.get("comparison", "gap_penalty")
		# self.comparison_min_peaks = self.Config.get("comparison", "min_peaks")
		self.comparison_a = self.Config
		self.comparison_rt_modulation = self.Config
		self.comparison_gap_penalty = self.Config
		self.comparison_min_peaks = self.Config
		
		# Compound Identification Settings
		self.ident_min_match_factor = self.Config
		# Any hits with both the Match Factor and the Reverse Match Factor below this value will be ignored
		
		self.ident_min_aligned_peaks = self.Config
		# defaults to 0 if being run on standalone experiment regardless of method setting

		self.ident_top_peaks = self.Config
		# - If running on a standalone experiment, the largest n peaks in the experiment
		# - If running on project, n largest aligned peaks, sorted by average peak area
		#	(where the average ignores experiments that don't have the peak)
		
		self.ident_nist_n_hits = self.Config
		# The number of `hits` to return from NIST MS Search
		
		self.ident_min_peak_area = self.Config
		# Do not identify any peaks with an average area less than this value

	@property
	def method_file(self):
		"""
		Returns the path of the file from which the method was loaded

		:return: Method file path
		:rtype: str
		"""
		
		return self._method_file

	@property
	def mass_range(self):
		"""
		Returns the value for the mass range

		This must be small enough to encompass all samples

		:return: Mass Range (min, max)
		:rtype: tuple of ints
		"""

		return self._mass_range

	@mass_range.setter
	def mass_range(self, value):
		"""
		Sets the value for the mass range

		This must be small enough to encompass all samples

		:param value: Mass Range
		:type value: list, tuple or comma-separated string
		"""

		if isinstance(value, str):
			self._mass_range = str2tuple(value)
		elif isinstance(value, list):
			self._mass_range = tuple(value)
		elif isinstance(value, tuple):
			self._mass_range = value
		else:
			raise TypeError("'mass_range' must be a list, tuple or comma-separated string")
	
	@property
	def tophat_struct(self):
		"""
		Returns the Tophat baseline correction structural element
		
		The structural element needs to be larger than the features one wants
			to retain in the spectrum after the top-hat transform
		
		:return:
		:rtype:
		"""
		
		return "{}{}".format(self.tophat, self.tophat_unit)
	
	@tophat_struct.setter
	def tophat_struct(self, value):
		"""
		Sets the the Tophat baseline correction structural element
		
		The structural element needs to be larger than the features one wants
			to retain in the spectrum after the top-hat transform
		
		:param value:
		:type value:
		"""
		
		_, self.tophat, self.tophat_unit = re.split('([^a-z]+)', value)
	
	@property
	def target_range(self):
		"""
		Returns the value for the range of retention times in which to search for peaks

		:return: Retention time range
		:rtype: tuple of floats
		"""

		return self._target_range

	@target_range.setter
	def target_range(self, value):
		"""
		Sets the value for the range of retention times in which to search for peaks

		:param value: Retention time range
		:type value: list, tuple or comma-separated string
		"""

		if isinstance(value, str):
			min_range, max_range, *_ = tuple(value.split(","))
			self._target_range = (float(min_range), float(max_range))
		elif isinstance(value, tuple):
			self._target_range = value
		elif isinstance(value, list):
			self._target_range = tuple(value)
		else:
			raise TypeError("'target_range' must be a list, tuple or comma-separated string")

	@property
	def base_peak_filter(self):
		"""
		Peaks with these base ions (i.e. the most intense peak in the mass
			spectrum) will be excluded from the results.

		This can be useful for excluding compounds related to septum bleed,
			which usually have a base ion at m/z 73

		:return: Base peak filter
		:rtype: tuple of ints
		"""

		return self._base_peak_filter
	
	@property
	def base_peak_filter_str(self):
		"""
		Peaks with these base ions (i.e. the most intense peak in the mass
			spectrum) will be excluded from the results.

		This can be useful for excluding compounds related to septum bleed,
			which usually have a base ion at m/z 73

		:return: Base peak filter
		:rtype: tuple of ints
		"""
		
		return ",".join([str(x) for x in self.base_peak_filter])
	
	@base_peak_filter.setter
	def base_peak_filter(self, value):
		"""
		Peaks with these base ions (i.e. the most intense peak in the mass
			spectrum) will be excluded from the results.

		This can be useful for excluding compounds related to septum bleed,
			which usually have a base ion at m/z 73


		:param value: Base peak filter
		:type value: list, tuple or comma-separated string
		"""

		if isinstance(value, str):
			self._base_peak_filter = [int(x) for x in value.split(",")]
		elif isinstance(value, list):
			self._base_peak_filter = value
		elif isinstance(value, tuple):
			self._base_peak_filter = list(value)
		else:
			raise TypeError("'base_peak_filter' must be a list, tuple or comma-separated string")
	
	def save_method(self, method_file=None):
		"""
		Saves the method to the given filename, or to self.method_file if no filename is given
		
		:param method_file: Filename to save the method to
		:type method_file: str, optional
		"""
		
		if method_file is None:
			method_file = self.method_file
		
		if method_file is None:
			raise ValueError("Please provide a filename to save the method as")
		
		# Configuration
		Config = configparser.ConfigParser()
		Config.read(method_file)
		
		for section in ["expr_creation", "alignment", "comparison"]:
			if section not in Config:
				Config.add_section(section)
		
		# Experiment Creation Settings
		Config.set("expr_creation", "mass_range", "{},{}".format(*self.mass_range))
		
		self._expr_creation_enable_sav_gol.save_property(self.Config)
		# Config.set("expr_creation", "enable_sav_gol", str(self.enable_sav_gol))
		
		Config.set("expr_creation", "enable_tophat", str(self.enable_tophat))
		Config.set("expr_creation", "tophat", str(self.tophat))
		Config.set("expr_creation", "tophat_unit", self.tophat_unit)
		
		Config.set("expr_creation", "bb_points", str(self.bb_points))
		Config.set("expr_creation", "bb_scans", str(self.bb_scans))
		Config.set("expr_creation", "target_range", "{},{}".format(*self.target_range))
		
		Config.set("expr_creation", "enable_noise_filter", str(self.enable_noise_filter))
		Config.set("expr_creation", "noise_thresh", str(self.noise_thresh))
		
		Config.set("expr_creation", "exclude_ions", list2str(self.base_peak_filter))
		
		# Peak Alignment Settings
		Config.set("alignment", "rt_modulation", str(self.rt_modulation))
		Config.set("alignment", "gap_penalty", str(self.gap_penalty))
		Config.set("alignment", "min_peaks", str(self.min_peaks))
		
		# Project Comparison Settings
		Config.set("comparison", "a", str(self.comparison_a))
		Config.set("comparison", "rt_modulation", str(self.comparison_rt_modulation))
		Config.set("comparison", "gap_penalty", str(self.comparison_gap_penalty))
		Config.set("comparison", "min_peaks", str(self.comparison_min_peaks))
		
		# Compound Identification Settings
		self._ident_min_match_factor.save_property(self.Config)
		self._ident_min_aligned_peaks.save_property(self.Config)
		self._ident_top_peaks.save_property(self.Config)

		with open(method_file, "w") as f:
			Config.write(f)
		
# End of Class Method


if __name__ == "__main__":
	class TestClass:
		test_property = MethodProperty("main", "test_property", 0, int)

		def __init__(self):
			# Setup Property
			self.test_property = None
			
			# Print Default Value
			print(self.test_property)
			
			# Load value from file
			print(self._test_property.load_property(0))
			
			# Print Loaded Value
			print(self.test_property)
	
	TestClass()


descriptions = {
		"enable_sav_gol": "Whether Savitzky-Golay smoothing should be performed.",
		"enable_tophat": "Whether Tophat baseline correction should be performed.",
		"enable_noise_filter": "Whether noise filtering should be performed.",
		"noise_thresh": "The threshold for noise filtering, in ions.",
		"tophat": "The size of the structural element for Tophat baseline correction. "
				  "The structural element needs to be larger than the features one wants "
				  "to retain in the spectrum after the top-hat transform.",
		"tophat_struct": "The size of the structural element for Tophat baseline correction. "
						 "The structural element needs to be larger than the features one "
						 "wants to retain in the spectrum after the top-hat transform.",
		"tophat_unit": "The unit of the structural element for Tophat baseline correction.",
		"bb_points": "",
		"bb_scans": "",
		"rt_modulation": "",
		"gap_penalty": "",
		"min_peaks": "Only aligned peaks that appear in more samples than this value will be "
					 "included in the results.",
		"comparison_rt_modulation": "",
		"comparison_gap_penalty": "",
		"comparison_min_peaks": "Only aligned peaks that appear in more samples than this value "
								"will be included in the results.",
		"comparison_a": "The significance value to use for statistical tests when comparing two "
						"projects.",
		"ident_min_match_factor": "When identifying compounds any hits where BOTH the Match "
								  "Factor and the Reverse Match Factor are less this value "
								  "will be ignored.",
		"ident_min_aligned_peaks": "When identifying compounds only aligned peaks that appear "
								   "in more samples than this value will be included in the results.",
		"ident_top_peaks": "When identifying compounds only this many peaks will be identified, "
						   "in descending peak area.",
		"ident_nist_n_hits": "The number of `hits` to return from NIST MS Search when identifying "
							 "compounds.",
		"ident_min_peak_area": "When identifying compounds only aligned peaks with an average peak "
							   "area larger than this value will be included in the results.",
		"target_range": "The time range in which to perform Biller & Biemann peak detection",
		"base_peak_filter": "Any peaks where the base peak is in this list will be excluded from "
							"the results.",
		"mass_range": "The range of m/z / mass values to use for the analysis.",
		
		}
