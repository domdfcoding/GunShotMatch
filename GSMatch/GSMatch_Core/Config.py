#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  Config.py
"""GunShotMatch configuration Class"""
#
#  This file is part of GunShotMatch
#
#  Copyright © 2018-2019 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import os
import re
import platform
import configparser

# 3rd party
from domdf_python_tools.utils import list2str, str2tuple
from domdf_python_tools.paths import maybe_make, relpath2

# TODO: pathlib support


class GSMConfig:
	"""
	GunShotMatch configuration Class

	:param configfile: .ini configuration file to load
	:type configfile: str
	"""
	
	def __init__(self, configfile):
		"""
		Initialise GunShotMatch configuration
		
		:param configfile: .ini configuration file to load
		:type configfile: str
		"""
		
		self._configfile = configfile
		print("\nUsing configuration file {}".format(self.configfile))
		
		# Configuration
		Config = configparser.ConfigParser()
		Config.read(self.configfile)
		
		if platform.system() == "Linux":
			self._nist_path = Config.get("main", "LinuxNistPath")
			if len(self._nist_path) == 0:
				print("Error: NIST MS Search path not found in configuration file.")
				sys.exit(1)
		else:
			self._nist_path = Config.get("main", "NistPath")
			if len(self._nist_path) == 0:
				print("Error: NIST MS Search path not found in configuration file.")
				sys.exit(1)
		
		# Directories
		self.raw_dir = os.path.abspath(Config.get("main", "rawpath"))
		self.csv_dir = os.path.abspath(Config.get("main", "CSVPath"))
		self.spectra_dir = os.path.abspath(Config.get("main", "SpectraPath"))
		self.charts_dir = os.path.abspath(Config.get("main", "ChartsPath"))
		self.msp_dir = os.path.abspath(Config.get("main", "MSPPath"))
		self.results_dir = os.path.abspath(Config.get("main", "ResultsPath"))
		self.expr_dir = os.path.abspath(Config.get("main", "exprdir"))
		self.log_dir = os.path.abspath(Config.get("main", "logdir"))
		
		# Sample Lists
		self.prefixList = Config.get("samples", "samples")
		
		# Import Settings
		self.bb_points = Config.get("import", "bb_points")
		self.bb_scans = Config.get("import", "bb_scans")
		self.noise_thresh = Config.get("import", "noise_thresh")
		self.target_range = Config.get("import", "target_range")
		self.base_peak_filter = Config.get("import", "exclude_ions")
		self.tophat = Config.get("import", "tophat")
		self.tophat_unit = Config.get("import", "tophat_unit")
		# self._tophat_struct = "{}{}".format(self.tophat, self.tophat_unit)
		self.mass_range = Config.get("import", "mass_range")
		
		# Peak Alignment Settings
		self.rt_modulation = Config.get("alignment", "rt_modulation")
		self.gap_penalty = Config.get("alignment", "gap_penalty")
		self.min_peaks = Config.get("alignment", "min_peaks")
		
		# Analysis Settings
		self.do_quantitative = Config.getboolean("analysis", "do_quantitative")
		self.do_qualitative = Config.getboolean("analysis", "do_qualitative")
		self.do_merge = Config.getboolean("analysis", "do_merge")
		self.do_counter = Config.getboolean("analysis", "do_counter")
		self.do_spectra = Config.getboolean("analysis", "do_spectra")
		self.do_charts = Config.getboolean("analysis", "do_charts")
		
		# Comparison
		self.comparison_a = Config.get("comparison", "a")
		self.comparison_rt_modulation = Config.get("comparison", "rt_modulation")
		self.comparison_gap_penalty = Config.get("comparison", "gap_penalty")
		self.comparison_min_peaks = Config.get("comparison", "min_peaks")
	
	@property
	def configfile(self):
		"""
		Returns the path of the .ini file from which the configuration was loaded
		
		:return: Configuration file path
		:rtype: str
		"""
		
		return self._configfile
	
	@property
	def nist_path(self):
		"""
		Returns the path of the NIST MS Search program
		
		:return:
		:rtype: str
		"""
		return self._nist_path
	
	@nist_path.setter
	def nist_path(self, value):
		"""
		Sets the path to the NIST MS Search program
		
		:param value:
		:type value: str
		
		"""
		self._nist_path = value
	
	@property
	def raw_dir(self):
		"""
		Returns the directory where PerkinElmer or Waters .RAW Files are stored
		
		:return:
		:rtype: str
		"""
		
		return self._raw_dir
	
	@raw_dir.setter
	def raw_dir(self, value):
		"""
		Sets the directory where PerkinElmer or Waters .RAW Files are stored

		:param value:
		:type value: str or :class:`pathlib.Path`
		"""
		
		self._raw_dir = str(relpath2(value))
	
	@property
	def csv_dir(self):
		"""
		Returns the directory where CSV reports will be stored

		:return:
		:rtype: str
		"""
		
		return self._csv_dir
	
	@csv_dir.setter
	def csv_dir(self, value):
		"""
		Sets the directory where CSV reports will be stored.
		The directory will be created if it does not already exist.

		:param value:
		:type value: str or :class:`pathlib.Path`
		"""
		
		self._csv_dir = str(relpath2(value))
		maybe_make(self._csv_dir)

	@property
	def spectra_dir(self):
		"""
		Returns the directory where Mass Spectra images will be stored

		:return:
		:rtype: str
		"""
		
		return self._spectra_dir
	
	@spectra_dir.setter
	def spectra_dir(self, value):
		"""
		Sets the directory where Mass Spectra images will be stored.
		The directory will be created if it does not already exist.

		:param value:
		:type value: str or :class:`pathlib.Path`
		"""
		
		self._spectra_dir = str(relpath2(value))
		maybe_make(self._spectra_dir)
	
	@property
	def charts_dir(self):
		"""
		Returns the directory where Charts will be stored

		:return:
		:rtype: str
		"""
		
		return self._charts_dir
	
	@charts_dir.setter
	def charts_dir(self, value):
		"""
		Sets the directory where Charts will be stored.
		The directory will be created if it does not already exist.

		:param value:
		:type value: str or :class:`pathlib.Path`
		"""
		
		self._charts_dir = str(relpath2(value))
		maybe_make(self._charts_dir)
	
	@property
	def msp_dir(self):
		"""
		Returns the directory where MSP files for NIST MS Search will be stored

		:return:
		:rtype: str
		"""
		
		return self._msp_dir
	
	@msp_dir.setter
	def msp_dir(self, value):
		"""
		Sets the directory where MSP files for NIST MS Search will be stored.
		The directory will be created if it does not already exist.

		:param value:
		:type value: str or :class:`pathlib.Path`
		"""
		
		self._msp_dir = str(relpath2(value))
		maybe_make(self._msp_dir)
	
	@property
	def results_dir(self):
		"""
		Returns the directory where Results will be stored

		:return:
		:rtype: str
		"""
		
		return self._results_dir
	
	@results_dir.setter
	def results_dir(self, value):
		"""
		Sets the directory where Results will be stored.
		The directory will be created if it does not already exist.

		:param value:
		:type value: str or :class:`pathlib.Path`
		"""
		
		self._results_dir = str(relpath2(value))
		maybe_make(self._results_dir)
	
	@property
	def expr_dir(self):
		"""
		Returns the directory where Experiment files will be stored

		:return:
		:rtype: str
		"""
		
		return self._expr_dir
	
	@expr_dir.setter
	def expr_dir(self, value):
		"""
		Sets the directory where Experiment files will be stored.
		The directory will be created if it does not already exist.

		:param value:
		:type value: str or :class:`pathlib.Path`
		"""
		
		self._expr_dir = str(relpath2(value))
		maybe_make(self._expr_dir)
		
	@property
	def log_dir(self):
		"""
		Returns the directory where log files will be stored

		:return:
		:rtype: str
		"""
		
		return self._log_dir
	
	@log_dir.setter
	def log_dir(self, value):
		"""
		Sets the directory where log files will be stored.
		The directory will be created if it does not already exist.

		:param value:
		:type value: str or :class:`pathlib.Path`
		"""
		
		self._log_dir = str(relpath2(value))
		maybe_make(self._log_dir)
	
	@property
	def prefixList(self):
		"""
		Returns the list of samples to process
		
		:return: Samples to process
		:rtype: list
		"""
		
		return self._prefixList
	
	@prefixList.setter
	def prefixList(self, value):
		"""
		Sets the list of samples to process
		
		:param value: Samples to process
		:type value: list, tuple or comma-separated str
		"""
		
		if isinstance(value, str):
			value = value.replace(";", ",").replace("\t", ",").replace(" ", "").split(",")
			self._prefixList = value
		elif isinstance(value, list):
			self._prefixList = value
		elif isinstance(value, tuple):
			self._prefixList = list(value)
		else:
			raise TypeError("'prefixList' must be a list, tuple or comma-separated string")

	@property
	def bb_points(self):
		"""
		Returns the value for the window width, in data points, for detecting
			local maxima during Biller and Biemann Peak Detection
		
		:return: Number of Points
		:rtype: int
		"""
		
		return self._bb_points
	
	@bb_points.setter
	def bb_points(self, value):
		"""
		Sets the value for the window width, in data points, for detecting
			local maxima during Biller and Biemann Peak Detection
		
		:param value: Number of Points
		:type value: int or other value that can be converted into an int
		"""
		
		self._bb_points = int(value)
	
	@property
	def bb_scans(self):
		"""
		Returns the value for the number of scans across which neighbouring,
			apexing ions and combined and considered as belonging
			to the same peak
		
		:return: Number of Scans
		:rtype: int
		"""
		
		return self._bb_scans
	
	@bb_scans.setter
	def bb_scans(self, value):
		"""
		Sets the value for the number of scans across which neighbouring,
			apexing ions and combined and considered as belonging
			to the same peak
		
		:param value: Number of Scans
		:type value: int or other value that can be converted into an int
		"""
		
		self._bb_scans = int(value)
	
	@property
	def noise_thresh(self):
		"""
		Returns the value for
		
		:return:
		:rtype:
		"""
		
		return self._noise_thresh
	
	@noise_thresh.setter
	def noise_thresh(self, value):
		"""
		Sets the value for
		
		:param value:
		:type value:
		"""
		
		self._noise_thresh = int(value)
	
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
	
	@property
	def tophat(self):
		"""
		Returns the value for the Tophat baseline correction structural element
		
		The structural element needs to be larger than the features one wants
			to retain in the spectrum after the top-hat transform
		
		:return:
		:rtype:
		"""
		
		return self._tophat
	
	@tophat.setter
	def tophat(self, value):
		"""
		Sets the value for the Tophat baseline correction structural element
		
		The structural element needs to be larger than the features one wants
			to retain in the spectrum after the top-hat transform
		
		:param value:
		:type value:
		"""
		
		self._tophat = value
	
	@property
	def tophat_unit(self):
		"""
		Returns the unit for the Tophat baseline correction structural element
		
		The structural element needs to be larger than the features one wants
			to retain in the spectrum after the top-hat transform
		
		:return:
		:rtype:
		"""
		
		return self._tophat_unit
	
	@tophat_unit.setter
	def tophat_unit(self, value):
		"""
		Sets the unit for the Tophat baseline correction structural element
		
		The structural element needs to be larger than the features one wants
			to retain in the spectrum after the top-hat transform
		
		:param value:
		:type value:
		"""
		
		self._tophat_unit = value
	
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
		
		_, self._tophat, self._tophat_unit = re.split('([^a-z]+)', value)
	
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
	def rt_modulation(self):
		"""
		Returns the value for the Peak Alignment RT Modulation
		
		:return:
		:rtype:
		"""
		
		return self._rt_modulation
	
	@rt_modulation.setter
	def rt_modulation(self, value):
		"""
		Sets the value for the Peak Alignment RT Modulation
		
		:param value:
		:type value:
		"""
		
		self._rt_modulation = float(value)
	
	@property
	def gap_penalty(self):
		"""
		Returns the value for the Peak Alignment Gap Penalty
		
		:return:
		:rtype:
		"""
		
		return self._gap_penalty
	
	@gap_penalty.setter
	def gap_penalty(self, value):
		"""
		Sets the value for the Peak Alignment Gap Penalty
		
		:param value:
		:type value:
		"""
		
		self._gap_penalty = float(value)
	
	@property
	def min_peaks(self):
		"""
		Returns the value for the Peak Alignment Min Peaks
		
		:return:
		:rtype:
		"""
		
		return self._min_peaks
	
	@min_peaks.setter
	def min_peaks(self, value):
		"""
		Sets the value for the Peak Alignment Min Peaks
		
		:param value:
		:type value:
		"""
		
		self._min_peaks = int(value)
	
	@property
	def do_quantitative(self):
		return self._do_quantitative
	
	@do_quantitative.setter
	def do_quantitative(self, value):
		if isinstance(value, str):
			if value == "True":
				self._do_quantitative = True
			if value == "False":
				self._do_quantitative = False
		else:
			self._do_quantitative = bool(value)
	
	@property
	def do_qualitative(self):
		return self._do_qualitative
	
	@do_qualitative.setter
	def do_qualitative(self, value):
		if isinstance(value, str):
			if value == "True":
				self._do_qualitative = True
			if value == "False":
				self._do_qualitative = False
		else:
			self._do_qualitative = bool(value)
		
	@property
	def do_merge(self):
		return self._do_merge
	
	@do_merge.setter
	def do_merge(self, value):
		if isinstance(value, str):
			if value == "True":
				self._do_merge = True
			if value == "False":
				self._do_merge = False
		else:
			self._do_merge = bool(value)
	
	@property
	def do_counter(self):
		return self._do_counter
	
	@do_counter.setter
	def do_counter(self, value):
		if isinstance(value, str):
			if value == "True":
				self._do_counter = True
			if value == "False":
				self._do_counter = False
		else:
			self._do_counter = bool(value)
		
	@property
	def do_spectra(self):
		return self._do_spectra
	
	@do_spectra.setter
	def do_spectra(self, value):
		if isinstance(value, str):
			if value == "True":
				self._do_spectra = True
			if value == "False":
				self._do_spectra = False
		else:
			self._do_spectra = bool(value)
	
	@property
	def do_charts(self):
		return self._do_charts
	
	@do_charts.setter
	def do_charts(self, value):
		if isinstance(value, str):
			if value == "True":
				self._do_charts = True
			if value == "False":
				self._do_charts = False
		else:
			self._do_charts = bool(value)
	
	@property
	def comparison_a(self):
		"""
		Returns the value for
		
		:return:
		:rtype:
		"""
		
		return self._comparison_a
	
	@comparison_a.setter
	def comparison_a(self, value):
		"""
		Sets the value for
		
		:param value:
		:type value:
		"""
		
		self._comparison_a = float(value)
		
	@property
	def comparison_rt_modulation(self):
		"""
		Returns the value for
		
		:return:
		:rtype:
		"""
		
		return self._comparison_rt_modulation
	
	@comparison_rt_modulation.setter
	def comparison_rt_modulation(self, value):
		"""
		Sets the value for
		
		:param value:
		:type value:
		"""
		
		self._comparison_rt_modulation = float(value)
		
	@property
	def comparison_gap_penalty(self):
		"""
		Returns the value for
		
		:return:
		:rtype:
		"""
		
		return self._comparison_gap_penalty
	
	@comparison_gap_penalty.setter
	def comparison_gap_penalty(self, value):
		"""
		Sets the value for
		
		:param value:
		:type value:
		"""
		
		self._comparison_gap_penalty = float(value)
		
	@property
	def comparison_min_peaks(self):
		"""
		Returns the value for
		
		:return:
		:rtype:
		"""
		
		return self._comparison_min_peaks
	
	@comparison_min_peaks.setter
	def comparison_min_peaks(self, value):
		"""
		Sets the value for
		
		:param value:
		:type value:
		"""
		
		self._comparison_min_peaks = int(value)
	
	def save_config(self, configfile=None):
		"""
		Saves the configuration to the given filename, or to self.configfile if no filename is given
		
		:param configfile: Filename to save the configuration to
		:type configfile: str, optional
		"""
		
		if configfile is None:
			configfile = self.configfile
		
		# Configuration
		Config = configparser.ConfigParser()
		Config.read(configfile)
		
		if platform.system() == "Linux":
			Config.set("main", "LinuxNistPath", self.nist_path)
		else:
			Config.set("main", "NistPath", self.nist_path.replace("\\", "/"))
		
		Config.set("main", "rawpath", str(relpath2(self.raw_dir)).replace("\\", "/"))
		Config.set("main", "CSVpath", str(relpath2(self.csv_dir)).replace("\\", "/"))
		Config.set("main", "SPECTRApath", str(relpath2(self.spectra_dir)).replace("\\", "/"))
		Config.set("main", "CHARTSpath", str(relpath2(self.charts_dir)).replace("\\", "/"))
		Config.set("main", "MSPpath", str(relpath2(self.msp_dir)).replace("\\", "/"))
		Config.set("main", "RESULTSpath", str(relpath2(self.results_dir)).replace("\\", "/"))
		Config.set("main", "MSPpath", str(relpath2(self.msp_dir)).replace("\\", "/"))
		Config.set("main", "exprdir", str(relpath2(self.expr_dir)).replace("\\", "/"))
		
		Config.set("samples", "samples", ",".join(self.prefixList))
		
		Config.set("import", "bb_points", str(self.bb_points))
		Config.set("import", "bb_scans", str(self.bb_scans))
		Config.set("import", "noise_thresh", str(self.noise_thresh))
		Config.set("import", "target_range", "{},{}".format(*self.target_range))
		Config.set("import", "exclude_ions", list2str(self.base_peak_filter))
		Config.set("import", "tophat", str(self.tophat))
		Config.set("import", "tophat_unit", self.tophat_unit)
		Config.set("import", "mass_range", "{},{}".format(*self.mass_range))
		
		Config.set("alignment", "rt_modulation", str(self.rt_modulation))
		Config.set("alignment", "gap_penalty", str(self.gap_penalty))
		Config.set("alignment", "min_peaks", str(self.min_peaks))
		
		Config.set("analysis", "do_quantitative", str(self.do_quantitative))
		Config.set("analysis", "do_qualitative", str(self.do_qualitative))
		Config.set("analysis", "do_merge", str(self.do_merge))
		Config.set("analysis", "do_counter", str(self.do_counter))
		Config.set("analysis", "do_spectra", str(self.do_spectra))
		Config.set("analysis", "do_charts", str(self.do_charts))
		
		Config.set("comparison", "a", str(self.comparison_a))
		Config.set("comparison", "rt_modulation", str(self.comparison_rt_modulation))
		Config.set("comparison", "gap_penalty", str(self.comparison_gap_penalty))
		Config.set("comparison", "min_peaks", str(self.comparison_min_peaks))
		
		with open(configfile, "w") as f:
			Config.write(f)
		

# End of Class GSMConfig


if __name__ == "__main__":
	import sys
	sys.exit(1)
