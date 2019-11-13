#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  Config.py
"""GunShotMatch configuration Class"""
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2018-2019 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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

import os

import platform
import sys
from domdf_python_tools import str2tuple

import configparser as ConfigParser

from domdf_python_tools.paths import maybe_make, relpath2


# TODO: pathlib support


class GSMConfig(object):
	def __init__(self, configfile):
		self.configfile = configfile
		print("\nUsing configuration file {}".format(self.configfile))
		
		"""Configuration -----"""
		Config = ConfigParser.ConfigParser()
		Config.read(configfile)
		
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
		
		# PerkinElmer or Waters .RAW Files
		self._RAW_DIRECTORY = os.path.abspath(Config.get("main", "rawpath"))
		
		# CSV Reports
		self._CSV_DIRECTORY = os.path.abspath(Config.get("main", "CSVPath"))  # Gets created if not present
		maybe_make(self._CSV_DIRECTORY)
		
		# Mass Spectra Images
		self._SPECTRA_DIRECTORY = os.path.abspath(Config.get("main", "SpectraPath"))  # Gets created if not present
		maybe_make(self._SPECTRA_DIRECTORY)
		
		# Charts
		self._CHARTS_DIRECTORY = os.path.abspath(Config.get("main", "ChartsPath"))  # Gets created if not present
		maybe_make(self._CHARTS_DIRECTORY)
		
		# MSP Files for NIST MS Search
		self._MSP_DIRECTORY = os.path.abspath(Config.get("main", "MSPPath"))  # Gets created if not present
		maybe_make(self._MSP_DIRECTORY)
		
		# Final Results
		self._RESULTS_DIRECTORY = os.path.abspath(Config.get("main", "ResultsPath"))  # Gets created if not present
		maybe_make(self._RESULTS_DIRECTORY)
		
		# Experiments
		self._EXPERIMENTS_DIRECTORY = os.path.abspath(Config.get("main", "exprdir"))  # Gets created if not present
		maybe_make(self._EXPERIMENTS_DIRECTORY)
		
		"""Sample Lists"""
		self.prefixList = Config.get("samples", "samples")
		
		"""Import Settings"""
		self.bb_points = Config.get("import", "bb_points")
		self.bb_scans = Config.get("import", "bb_scans")
		self.noise_thresh = Config.get("import", "noise_thresh")
		min_range, max_range = tuple(Config.get("import", "target_range").split(","))
		self._target_range = (float(min_range), float(max_range))
		self._base_peak_filter = [int(x) for x in Config.get("import", "exclude_ions").split(",")]
		self._tophat = Config.get("import", "tophat")
		self._tophat_unit = Config.get("import", "tophat_unit")
		#self._tophat_struct = "{}{}".format(self.tophat, self.tophat_unit)
		self._mass_range = str2tuple(Config.get("import", "mass_range"))
		
		"""Peak Alignment Settings"""
		self.rt_modulation = Config.get("alignment", "rt_modulation")
		self.gap_penalty = Config.get("alignment", "gap_penalty")
		self.min_peaks = Config.get("alignment", "min_peaks")
		
		"""Analysis Settings"""
		self._do_quantitative = Config.getboolean("analysis", "do_quantitative")
		self._do_qualitative = Config.getboolean("analysis", "do_qualitative")
		self._do_merge = Config.getboolean("analysis", "do_merge")
		self._do_counter = Config.getboolean("analysis", "do_counter")
		self._do_spectra = Config.getboolean("analysis", "do_spectra")
		self._do_charts = Config.getboolean("analysis", "do_charts")
		
		"""Comparison"""
		self.comparison_a = Config.get("comparison", "a")
		self.comparison_rt_modulation = Config.get("comparison", "rt_modulation")
		self.comparison_gap_penalty = Config.get("comparison", "gap_penalty")
		self.comparison_min_peaks = Config.get("comparison", "min_peaks")
	
	@property
	def nist_path(self):
		return self._nist_path
	
	@nist_path.setter
	def nist_path(self, value):
		self._nist_path = value
	
	@property
	def RAW_DIRECTORY(self):
		return self._RAW_DIRECTORY
	
	@RAW_DIRECTORY.setter
	def RAW_DIRECTORY(self, value):
		self._RAW_DIRECTORY = str(relpath2(value))
	
	@property
	def CSV_DIRECTORY(self):
		return self._CSV_DIRECTORY
	
	@CSV_DIRECTORY.setter
	def CSV_DIRECTORY(self, value):
		self._CSV_DIRECTORY = str(relpath2(value))
	
	@property
	def SPECTRA_DIRECTORY(self):
		return self._SPECTRA_DIRECTORY
	
	@SPECTRA_DIRECTORY.setter
	def SPECTRA_DIRECTORY(self, value):
		self._SPECTRA_DIRECTORY = str(relpath2(value))
	
	@property
	def CHARTS_DIRECTORY(self):
		return self._CHARTS_DIRECTORY
	
	@CHARTS_DIRECTORY.setter
	def CHARTS_DIRECTORY(self, value):
		self._CHARTS_DIRECTORY = str(relpath2(value))
	
	@property
	def MSP_DIRECTORY(self):
		return self._MSP_DIRECTORY
	
	@MSP_DIRECTORY.setter
	def MSP_DIRECTORY(self, value):
		self._MSP_DIRECTORY = str(relpath2(value))
	
	@property
	def RESULTS_DIRECTORY(self):
		return self._RESULTS_DIRECTORY
	
	@RESULTS_DIRECTORY.setter
	def RESULTS_DIRECTORY(self, value):
		self._RESULTS_DIRECTORY = str(relpath2(value))
	
	@property
	def EXPERIMENTS_DIRECTORY(self):
		return self._EXPERIMENTS_DIRECTORY
	
	@EXPERIMENTS_DIRECTORY.setter
	def EXPERIMENTS_DIRECTORY(self, value):
		self._EXPERIMENTS_DIRECTORY = str(relpath2(value))
	
	@property
	def prefixList(self):
		return self._prefixList
	
	@prefixList.setter
	def prefixList(self, value):
		if isinstance(value, str):
			value = value.replace(";", ",").replace("\t", ",").replace(" ", "").split(",")
			self._prefixList = value
		elif isinstance(value, list):
			self._prefixList = value
		elif isinstance(value, tuple):
			self._prefixList = list(value)
		
		else:
			raise TypeError("'prefixList' must be a list, tuple or comma-seperated string")

	@property
	def bb_points(self):
		return self._bb_points
	
	@bb_points.setter
	def bb_points(self, value):
		self._bb_points = int(value)
	
	@property
	def bb_scans(self):
		return self._bb_scans
	
	@bb_scans.setter
	def bb_scans(self, value):
		self._bb_scans = int(value)
	
	@property
	def noise_thresh(self):
		return self._noise_thresh
	
	@noise_thresh.setter
	def noise_thresh(self, value):
		self._noise_thresh = int(value)
	
	@property
	def target_range(self):
		return self._target_range
	
	@target_range.setter
	def target_range(self, value):
		if isinstance(value, str):
			min_range, max_range, *_ = tuple(value.split(","))
			self._target_range = (float(min_range), float(max_range))
		elif isinstance(value, tuple):
			self._target_range = value
		elif isinstance(value, list):
			self._target_range = tuple(value)
		else:
			raise TypeError("'target_range' must be a list, tuple or comma-seperated string")
	
	@property
	def base_peak_filter(self):
		return self._base_peak_filter
	
	@base_peak_filter.setter
	def base_peak_filter(self, value):
		if isinstance(value, str):
			self._base_peak_filter = [int(x) for x in value.split(",")]
		elif isinstance(value, list):
			self._base_peak_filter = value
		elif isinstance(value, tuple):
			self._base_peak_filter = list(value)
		else:
			raise TypeError("'base_peak_filter' must be a list, tuple or comma-seperated string")
	
	@property
	def tophat(self):
		return self._tophat
	
	@tophat.setter
	def tophat(self, value):
		self._tophat = value
	
	@property
	def tophat_unit(self):
		return self._tophat_unit
	
	@tophat_unit.setter
	def tophat_unit(self, value):
		self._tophat_unit = value
	
	@property
	def tophat_struct(self):
		return "{}{}".format(self.tophat, self.tophat_unit)
	
	@tophat_struct.setter
	def tophat_struct(self, value):
		self._tophat_struct = value
	
	@property
	def mass_range(self):
		return self._mass_range
	
	@mass_range.setter
	def mass_range(self, value):
		if isinstance(value, str):
			self._base_peak_filter = str2tuple(value)
		elif isinstance(value, list):
			self._base_peak_filter = tuple(value)
		elif isinstance(value, tuple):
			self._base_peak_filter = value
		else:
			raise TypeError("'mass_range' must be a list, tuple or comma-seperated string")
	
	@property
	def rt_modulation(self):
		return self._rt_modulation
	
	@rt_modulation.setter
	def rt_modulation(self, value):
		self._rt_modulation = float(value)
	
	@property
	def gap_penalty(self):
		return self._gap_penalty
	
	@gap_penalty.setter
	def gap_penalty(self, value):
		self._gap_penalty = float(value)
	
	@property
	def min_peaks(self):
		return self._min_peaks
	
	@min_peaks.setter
	def min_peaks(self, value):
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
		return self._comparison_a
	
	@comparison_a.setter
	def comparison_a(self, value):
		self._comparison_a = float(value)
		
	@property
	def comparison_rt_modulation(self):
		return self._comparison_rt_modulation
	
	@comparison_rt_modulation.setter
	def comparison_rt_modulation(self, value):
		self._comparison_rt_modulation = float(value)
		
	@property
	def comparison_gap_penalty(self):
		return self._comparison_gap_penalty
	
	@comparison_gap_penalty.setter
	def comparison_gap_penalty(self, value):
		self._comparison_gap_penalty = float(value)
		
	@property
	def comparison_min_peaks(self):
		return self._comparison_min_peaks
	
	@comparison_min_peaks.setter
	def comparison_min_peaks(self, value):
		self._comparison_min_peaks = int(value)
	

	def save_config(self, configfile=None,):
		# Gets configuration from self if set, if not from self
		
		if configfile is None:
			configfile = self.configfile
		
		import platform
		import configparser as ConfigParser
		from domdf_python_tools import list2str
		
		"""Configuration -----"""
		Config = ConfigParser.ConfigParser()
		Config.read(configfile)
		
		if platform.system() == "Linux":
			Config.set("main", "LinuxNistPath", self.nist_path)
		else:
			Config.set("main", "NistPath", self.nist_path.replace("\\", "/"))
		
		Config.set("main", "rawpath", str(relpath2(self.RAW_DIRECTORY)).replace("\\", "/"))
		Config.set("main", "CSVpath", str(relpath2(self.CSV_DIRECTORY)).replace("\\", "/"))
		Config.set("main", "SPECTRApath", str(relpath2(self.SPECTRA_DIRECTORY)).replace("\\", "/"))
		Config.set("main", "CHARTSpath", str(relpath2(self.CHARTS_DIRECTORY)).replace("\\", "/"))
		Config.set("main", "MSPpath", str(relpath2(self.MSP_DIRECTORY)).replace("\\", "/"))
		Config.set("main", "RESULTSpath", str(relpath2(self.RESULTS_DIRECTORY)).replace("\\", "/"))
		Config.set("main", "MSPpath", str(relpath2(self.MSP_DIRECTORY)).replace("\\", "/"))
		Config.set("main", "exprdir", str(relpath2(self.EXPERIMENTS_DIRECTORY)).replace("\\", "/"))
		
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
