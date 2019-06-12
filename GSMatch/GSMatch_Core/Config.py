# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2017-2019 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

import os

from domdf_python_tools.paths import maybe_make, relpath


class GSMConfig(object):
	def __init__(self, configfile):
		self.load_config(configfile)
	
	def load_config(self, configfile):
		self.configfile = configfile
		print("\nUsing configuration file {}".format(self.configfile))
		self.get_config(self.configfile)
	
	def get_config(self, configfile=None, parent=None):
		# Returns configuration to parent if set, if not to self
		
		if parent is None:
			parent = self
		if configfile is None:
			configfile = self.configfile
		
		import platform
		import sys
		from domdf_python_tools import str2tuple
		
		import configparser as ConfigParser
		
		"""Configuration -----"""
		Config = ConfigParser.ConfigParser()
		Config.read(configfile)
		
		if platform.system() == "Linux":
			parent.nist_path = Config.get("main", "LinuxNistPath")
			if len(parent.nist_path) == 0:
				print("Error: NIST MS Search path not found in configuration file.")
				sys.exit(1)
		else:
			parent.nist_path = Config.get("main", "NistPath")
			if len(parent.nist_path) == 0:
				print("Error: NIST MS Search path not found in configuration file.")
				sys.exit(1)
		
		# PerkinElmer or Waters .RAW Files
		parent.RAW_DIRECTORY = os.path.abspath(Config.get("main", "rawpath"))
		
		# CSV Reports
		parent.CSV_DIRECTORY = os.path.abspath(Config.get("main", "CSVPath"))  # Gets created if not present
		maybe_make(parent.CSV_DIRECTORY)
		
		# Mass Spectra Images
		parent.SPECTRA_DIRECTORY = os.path.abspath(Config.get("main", "SpectraPath"))  # Gets created if not present
		maybe_make(parent.SPECTRA_DIRECTORY)
		
		# Charts
		parent.CHARTS_DIRECTORY = os.path.abspath(Config.get("main", "ChartsPath"))  # Gets created if not present
		maybe_make(parent.CHARTS_DIRECTORY)
		
		# MSP Files for NIST MS Search
		parent.MSP_DIRECTORY = os.path.abspath(Config.get("main", "MSPPath"))  # Gets created if not present
		maybe_make(parent.MSP_DIRECTORY)
		
		# Final Results
		parent.RESULTS_DIRECTORY = os.path.abspath(Config.get("main", "ResultsPath"))  # Gets created if not present
		maybe_make(parent.RESULTS_DIRECTORY)
		
		# Experiments
		parent.EXPERIMENTS_DIRECTORY = os.path.abspath(Config.get("main", "exprdir"))  # Gets created if not present
		maybe_make(parent.EXPERIMENTS_DIRECTORY)
		
		"""Sample Lists"""
		parent.prefixList = Config.get("samples", "samples").replace(";", ",").replace("\t", ",").replace(" ",
																										  "").split(",")
		
		"""Import Settings"""
		parent.bb_points = int(Config.get("import", "bb_points"))
		parent.bb_scans = int(Config.get("import", "bb_scans"))
		parent.noise_thresh = int(Config.get("import", "noise_thresh"))
		min_range, max_range = tuple(Config.get("import", "target_range").split(","))
		parent.target_range = (float(min_range), float(max_range))
		parent.base_peak_filter = [int(x) for x in Config.get("import", "exclude_ions").split(",")]
		parent.tophat = Config.get("import", "tophat")
		parent.tophat_unit = Config.get("import", "tophat_unit")
		parent.tophat_struct = "{}{}".format(parent.tophat, parent.tophat_unit)
		parent.mass_range = str2tuple(Config.get("import", "mass_range"))
		
		"""Peak Alignment Settings"""
		parent.rt_modulation = float(Config.get("alignment", "rt_modulation"))
		parent.gap_penalty = float(Config.get("alignment", "gap_penalty"))
		parent.min_peaks = int(Config.get("alignment", "min_peaks"))
		
		"""Analysis Settings"""
		parent.do_quantitative = Config.getboolean("analysis", "do_quantitative")
		parent.do_qualitative = Config.getboolean("analysis", "do_qualitative")
		parent.do_merge = Config.getboolean("analysis", "do_merge")
		parent.do_counter = Config.getboolean("analysis", "do_counter")
		parent.do_spectra = Config.getboolean("analysis", "do_spectra")
		parent.do_charts = Config.getboolean("analysis", "do_charts")
		
		"""Comparison"""
		parent.comparison_a = float(Config.get("comparison", "a"))
		parent.comparison_rt_modulation = float(Config.get("comparison", "rt_modulation"))
		parent.comparison_gap_penalty = float(Config.get("comparison", "gap_penalty"))
		parent.comparison_min_peaks = int(Config.get("comparison", "min_peaks"))
	
	def save_config(self, configfile=None, parent=None):
		# Gets configuration from parent if set, if not from self
		
		if parent is None:
			parent = self
		if configfile is None:
			configfile = self.configfile
		
		import platform
		import configparser as ConfigParser
		from domdf_python_tools import list2str
		
		"""Configuration -----"""
		Config = ConfigParser.ConfigParser()
		Config.read(configfile)
		
		if platform.system() == "Linux":
			Config.set("main", "LinuxNistPath", parent.nist_path)
		else:
			Config.set("main", "NistPath", parent.nist_path)
		
		Config.set("main", "rawpath", relpath(parent.RAW_DIRECTORY))
		Config.set("main", "CSVpath", relpath(parent.CSV_DIRECTORY))
		Config.set("main", "SPECTRApath", relpath(parent.SPECTRA_DIRECTORY))
		Config.set("main", "CHARTSpath", relpath(parent.CHARTS_DIRECTORY))
		Config.set("main", "MSPpath", relpath(parent.MSP_DIRECTORY))
		Config.set("main", "RESULTSpath", relpath(parent.RESULTS_DIRECTORY))
		Config.set("main", "MSPpath", relpath(parent.MSP_DIRECTORY))
		Config.set("main", "exprdir", relpath(parent.EXPERIMENTS_DIRECTORY))
		
		Config.set("samples", "samples", ",".join(parent.prefixList))
		
		Config.set("import", "bb_points", str(parent.bb_points))
		Config.set("import", "bb_scans", str(parent.bb_scans))
		Config.set("import", "noise_thresh", str(parent.noise_thresh))
		Config.set("import", "target_range", "{},{}".format(*parent.target_range))
		Config.set("import", "exclude_ions", list2str(parent.base_peak_filter))
		Config.set("import", "tophat", str(parent.tophat))
		Config.set("import", "tophat_unit", parent.tophat_unit)
		Config.set("import", "mass_range", "{},{}".format(*parent.mass_range))
		
		Config.set("alignment", "rt_modulation", str(parent.rt_modulation))
		Config.set("alignment", "gap_penalty", str(parent.gap_penalty))
		Config.set("alignment", "min_peaks", str(parent.min_peaks))
		
		Config.set("analysis", "do_quantitative", str(parent.do_quantitative))
		Config.set("analysis", "do_qualitative", str(parent.do_qualitative))
		Config.set("analysis", "do_merge", str(parent.do_merge))
		Config.set("analysis", "do_counter", str(parent.do_counter))
		Config.set("analysis", "do_spectra", str(parent.do_spectra))
		Config.set("analysis", "do_charts", str(parent.do_charts))
		
		Config.set("comparison", "a", str(parent.comparison_a))
		Config.set("comparison", "rt_modulation", str(parent.comparison_rt_modulation))
		Config.set("comparison", "gap_penalty", str(parent.comparison_gap_penalty))
		Config.set("comparison", "min_peaks", str(parent.comparison_min_peaks))
		
		with open(configfile, "w") as f:
			Config.write(f)
		

# End of Class GSMConfig


if __name__ == "__main__":
	import sys
	sys.exit(1)
