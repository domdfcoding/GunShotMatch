#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  NewExperiment.py
#
"""
Create a New Experiment
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
#


# stdlib
import sys
import locale

# 3rd party
from pyms.IntensityMatrix import build_intensity_matrix_i
from pyms.Noise.Analysis import window_analyzer
from pyms.Noise.SavitzkyGolay import savitzky_golay
from pyms.TopHat import tophat
from pyms.BillerBiemann import BillerBiemann, num_ions_threshold
from pyms.Peak.Function import peak_sum_area
from pyms.Experiment import Experiment

# this package
from GuiV2.GSMatch2_Core.IDs import *
from GuiV2.GSMatch2_Core import Method
from GuiV2.GSMatch2_Core.watchdog import time_now


sys.path.append("..")

__author__ = "Dominic Davis-Foster"
__copyright__ = "Copyright 2017-2019 Dominic Davis-Foster"

__license__ = "GPLv3"
__version__ = "1.0.0 Rework"
__email__ = "dominic@davis-foster.co.uk"

program_name = "GunShotMatch"
copyright = __copyright__

# Setup for reading strings with thousand separators as floats
# From https://stackoverflow.com/a/31074271
locale.setlocale(locale.LC_ALL, "")

verbose = False

# From https://stackoverflow.com/questions/14463277/how-to-disable-python-warnings
# with warnings.catch_warnings():
# 	warnings.simplefilter("ignore")


class NewExperiment:
	"""
	
	:param properties:
	:type properties:
	
	:return:
	:rtype:
	"""
	
	def __init__(self, properties, pbar=None):
		self.properties = properties
		self.pbar = pbar
		self.pbar_count = 0
		
		# Determine the name of the sample from the filename
		self.sample_name = properties["Name"]
		
		self.filetype = properties["Original Filetype"]
		
		self.run()
	
	def update_pbar(self):
		if self.pbar:
			self.pbar_count += 1
			self.pbar.Update(self.pbar_count)
	
	def run(self):
		print("Quantitative Processing in Progress...")
		
		# TODO: Include data etc. in experiment file
		
		self.update_pbar()
		
		if self.filetype == ID_Format_jcamp:
			# Load data using JCAMP_reader
			from pyms.GCMS.IO.JCAMP import JCAMP_reader
			data = JCAMP_reader(self.properties["Original Filename"])
		
		elif self.filetype == ID_Format_mzML:
			# Load data using JCAMP_reader
			from pyms.GCMS.IO.MZML import MZML_reader
			data = MZML_reader(self.properties["Original Filename"])
		
		elif self.filetype == ID_Format_ANDI:
			# Load data using JCAMP_reader
			from pyms.GCMS.IO.ANDI import ANDI_reader
			data = ANDI_reader(self.properties["Original Filename"])
		
		else:
			# Unknown Format
			return
		# TODO: Waters RAW, Thermo RAW, Agilent .d
		
		self.update_pbar()
		
		method = Method.Method(self.properties["Method"])
		
		self.update_pbar()
		
		# list of all retention times, in seconds
		times = data.get_time_list()
		# get Total Ion Chromatogram
		tic = data.get_tic()
		# RT Range, time step, no. scans, min, max, mean and median m/z
		data.info()
		
		# Build "intensity matrix" by binning data with integer bins and a
		# 	window of -0.3 to +0.7, the same as NIST uses
		im = build_intensity_matrix_i(data)
		
		self.update_pbar()
		
		# Show the m/z of the maximum and minimum bins
		print(" Minimum m/z bin: {}".format(im.get_min_mass()))
		print(" Maximum m/z bin: {}".format(im.get_max_mass()))
		
		# Crop masses
		min_mass, max_mass, *_ = method.mass_range
		
		if min_mass < im.get_min_mass():
			min_mass = im.get_min_mass()
		if max_mass > im.get_max_mass():
			max_mass = im.get_max_mass()
		im.crop_mass(min_mass, max_mass)
		
		self.update_pbar()
		
		# Perform Data filtering
		n_scan, n_mz = im.get_size()
		
		# Iterate over each IC in the intensity matrix
		for ii in range(n_mz):
			# print("\rWorking on IC#", ii+1, '  ',end='')
			ic = im.get_ic_at_index(ii)
			
			if method.enable_sav_gol:
				# Perform Savitzky-Golay smoothing.
				# Note that Turbomass does not use smoothing for qualitative method.
				ic = savitzky_golay(ic)
				
			if method.enable_tophat:
				# Perform Tophat baseline correction
				# Top-hat baseline Correction seems to bring down noise,
				#  		retaining shapes, but keeps points on actual peaks
				ic = tophat(ic, struct=method.tophat_struct)
			
			# Set the IC in the intensity matrix to the filtered one
			im.set_ic_at_index(ii, ic)
			
			self.update_pbar()
		
		# Peak Detection based on Biller and Biemann (1974), with a window
		# 	of <points>, and combining <scans> if they apex next to each other
		peak_list = BillerBiemann(im, points=method.bb_points, scans=method.bb_scans)
		
		self.update_pbar()
		
		print(" Number of peaks identified before filtering: {}".format(len(peak_list)))
		
		if method.enable_noise_filter:
			# Filtering peak lists with automatic noise filtering
			noise_level = window_analyzer(tic)
			# should we also do rel_threshold() here?
			# https://pymassspec.readthedocs.io/en/master/pyms/BillerBiemann.html#pyms.BillerBiemann.rel_threshold
			peak_list = num_ions_threshold(peak_list, method.noise_thresh, noise_level)
		
		self.update_pbar()
		
		filtered_peak_list = []
		
		for peak in peak_list:
			# Get mass and intensity lists for the mass spectrum at the apex of the peak
			apex_mass_list = peak.mass_spectrum.mass_list
			apex_mass_spec = peak.mass_spectrum.mass_spec
			
			# Determine the intensity of the base peak in the mass spectrum
			base_peak_intensity = max(apex_mass_spec)
			
			# Determine the index of the base peak in the mass spectrum
			base_peak_index = [
				index for index, intensity in enumerate(apex_mass_spec)
				if intensity == base_peak_intensity][0]
			
			# Finally, determine the mass of the base peak
			base_peak_mass = apex_mass_list[base_peak_index]
			
			# skip the peak if the base peak is at e.g. m/z 73, i.e. septum bleed
			if base_peak_mass in method.base_peak_filter:
				continue
			
			area = peak_sum_area(im, peak)
			peak.set_area(area)
			filtered_peak_list.append(peak)
			
			self.update_pbar()
		
		print(" Number of peaks identified: {}".format(len(filtered_peak_list)))
		
		# Create an experiment
		self.expr = Experiment(self.sample_name, filtered_peak_list)
		self.expr.sele_rt_range(["{}m".format(method.target_range[0]), "{}m".format(method.target_range[1])])
		
		self.update_pbar()
		
		current_time = time_now()
		
		# The date and time the experiment was created
		self.properties["Date Created"] = current_time
		
		# The date and time the experiment was last modified
		self.properties["Date Modified"] = current_time
		
		if self.pbar:
			self.pbar.Update(self.pbar.Range)
		
		self.tic = tic
		self.filtered_peak_list = filtered_peak_list

