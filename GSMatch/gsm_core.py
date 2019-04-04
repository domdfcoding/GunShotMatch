#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  gsm_core.py
"""Core Functions For GunShotMatch"""
#
#  Copyright 2017-2019 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
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
import wx
import os
from utils.paths import maybe_make, relpath

def infer_samples(csvpath):
	import os
	
	inferred_samples = []
	directory_listing = os.listdir(csvpath)
	for filename in directory_listing:
		# if filename.lower().endswith(".csv"):
		if filename.endswith("GC_80.CSV"):
			# print filename[:-9]+'MS_80.CSV'
			if os.path.isfile(os.path.join(csvpath, filename[:-9] + 'MS_80.CSV')):
				inferred_samples.append(filename[:-10])
	
	inferred_samples.sort()
	return (inferred_samples)


class GSMConfig(object):
	def __init__(self, configfile):
		self.configfile = configfile
		print("\nUsing configuration file {}".format(configfile))
		self.get_config(self.configfile)
	
	def get_config(self, configfile=None, parent=None):
		# Returns configuration to parent if set, if not to self
		
		if parent is None:
			parent = self
		if configfile is None:
			configfile = self.configfile
		
		import platform
		import sys
		
		import configparser as ConfigParser
		from itertools import chain, permutations
		
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
		parent.tophat_struct = "{}{}".format(Config.get("import", "tophat"), Config.get("import", "tophat_unit"))
		from utils.helper import str2tuple
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
	
	def save_config(self, configfile=None, parent=None):
		# Gets configuration from parent if set, if not from self
		
		if parent is None:
			parent = self
		if configfile is None:
			configfile = self.configfile
		
		import platform
		import sys
		
		import configparser as ConfigParser
		from itertools import chain, permutations
		
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
		
		Config.set("samples", "samples", relpath(parent.prefixList))
		
		"""TODO"""
		#	parent.bb_points = int(Config.get("import","bb_points"))
		#	parent.bb_scans = int(Config.get("import", "bb_scans"))
		#	parent.noise_thresh = int(Config.get("import", "noise_thresh"))
		#	min_range, max_range = tuple(Config.get("import", "target_range").split(","))
		#	parent.target_range = (float(min_range),float(max_range))
		#	parent.base_peak_filter = [int(x) for x in Config.get("import", "exclude_ions").split(",")]
		#	parent.tophat_struct = "{}{}".format(Config.get("import", "tophat"),Config.get("import", "tophat_unit"))
		
		#	parent.rt_modulation = float(Config.get("alignment", "rt_modulation"))
		#	parent.gap_penalty = float(Config.get("alignment", "rt_gap_penalty"))
		#	parent.min_peaks = int(Config.get("alignment", "min_peaks"))
		#		parent.mass_range = Config.get("import", "mass_range")

		
		Config.set("analysis", "do_quantitative", parent.do_quantitative)
		Config.set("analysis", "do_qualitative", parent.do_qualitative)
		Config.set("analysis", "do_merge", parent.do_merge)
		Config.set("analysis", "do_counter", parent.do_counter)
		Config.set("analysis", "do_spectra", parent.do_spectra)
		Config.set("analysis", "do_charts", parent.do_charts)


def read_peaks_json(jsonfile):
	import json
	return [json.loads(x) for x in open(jsonfile, "r").readlines()]


# GUI Thread Boilerplates
class EventBoilerplate(wx.PyCommandEvent):
	"""Event to signal that a the conversion is complete"""
	
	def __init__(self, etype, eid):
		"""Creates the event object"""
		wx.PyCommandEvent.__init__(self, etype, eid)


class LogEventBoilerplate(wx.PyCommandEvent):
	"""Event to signal that a the conversion is complete"""
	
	def __init__(self, etype, eid, log_text):
		"""Creates the event object"""
		wx.PyCommandEvent.__init__(self, etype, eid)
		self.log_text = log_text
	
	def GetValue(self):
		"""Returns the value from the event.
		@return: the value of this event

		"""
		return self.log_text


"""Peak Alignment"""


def get_peak_alignment(A, minutes=True):
	"""
	Based on code from PyMS
	@summary: Get dictionary of aligned retention times

	@param A: Alignment object to extract data from
	@param minutes: An optional indicator whether to return retention times
		in minutes. If False, retention time will be returned in seconds
	@type minutes: BooleanType

	@author: Woon Wai Keen
	@author: Andrew Isaac
	@author: Vladimir Likic
	@author: Dominic Davis-Foster
	"""
	
	import pandas
	
	# create header
	# print(A.expr_code)
	
	rt_table = []
	
	# for each alignment position write alignment's RT
	for peak_idx in range(len(A.peakpos[0])):
		
		rts = []
		countrt = 0
		
		for align_idx in range(len(A.peakpos)):
			
			peak = A.peakpos[align_idx][peak_idx]
			
			if peak is not None:
				
				if minutes:
					rt = peak.get_rt() / 60.0
				else:
					rt = peak.get_rt()
				
				rts.append(rt)
				
				countrt = countrt + 1
			else:
				rts.append(None)
		
		if countrt == len(A.expr_code):
			rt_table.append(rts)
	
	rt_alignment = pandas.DataFrame(rt_table, columns=A.expr_code)
	rt_alignment = rt_alignment.reindex(sorted(rt_alignment.columns), axis=1)
	
	return rt_alignment


def get_ms_alignment(A):
	"""
	Based on code from PyMS
	@summary: Get dictionary of mass spectra for the aligned peaks

	@param A: Alignment object to extract data from

	@author: Woon Wai Keen
	@author: Andrew Isaac
	@author: Vladimir Likic
	@author: Dominic Davis-Foster
	"""
	
	import pandas
	
	ms_table = []
	
	# for each alignment position write alignment's ms
	for peak_idx in range(len(A.peakpos[0])):
		
		specs = []
		countms = 0
		
		for align_idx in range(len(A.peakpos)):
			
			peak = A.peakpos[align_idx][peak_idx]
			
			if peak is not None:
				
				ms = peak.get_mass_spectrum()
				specs.append(ms)
				countms = countms + 1
			else:
				specs.append(None)
		
		if countms == len(A.expr_code):
			ms_table.append(specs)
	
	ms_alignment = pandas.DataFrame(ms_table, columns=A.expr_code)
	ms_alignment = ms_alignment.reindex(sorted(ms_alignment.columns), axis=1)
	
	return ms_alignment


def infer_samples(csvpath):
	import os
	
	inferred_samples = []
	directory_listing = os.listdir(csvpath)
	for filename in directory_listing:
		# if filename.lower().endswith(".csv"):
		if filename.endswith("GC_80.CSV"):
			# print filename[:-9]+'MS_80.CSV'
			if os.path.isfile(csvpath + filename[:-9] + 'MS_80.CSV'):
				inferred_samples.append(filename[:-10])
	
	inferred_samples.sort()
	return (inferred_samples)


if __name__ == '__main__':
	print(infer_samples("./Results/CSV/"))