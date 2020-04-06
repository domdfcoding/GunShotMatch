#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  experiment.py
#
#  This file is part of GunShotMatch
#
#  Copyright © 2017-2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import csv
import json
import operator
import os
import pickle
import sys
import tarfile
import tempfile
import time
import traceback
from decimal import Decimal
from io import BytesIO
from statistics import mean, median

# 3rd party
import numpy
import pyms.Experiment
import pyms_nist_search
from domdf_python_tools.doctools import is_documented_by
from mathematical.utils import rounders
from pyms.BillerBiemann import BillerBiemann, num_ions_threshold
from pyms.Experiment import store_expr
from pyms.GCMS.Class import IonChromatogram
from pyms.IntensityMatrix import build_intensity_matrix_i
from pyms.Noise.Analysis import window_analyzer
from pyms.Noise.SavitzkyGolay import savitzky_golay
from pyms.Peak.Function import peak_sum_area
from pyms.Peak.List.IO import store_peaks
from pyms.TopHat import tophat

# this package
from GSMatch.utils import pynist
from GuiV2.GSMatch2_Core import Base, Method
from GuiV2.GSMatch2_Core.Config import internal_config
from GuiV2.GSMatch2_Core.Experiment.identification import QualifiedPeak
from GuiV2.GSMatch2_Core.Experiment.identification.functions import create_msp
from GuiV2.GSMatch2_Core.IDs import *
from GuiV2.GSMatch2_Core.InfoProperties import massrange, Property, rtrange
from GuiV2.GSMatch2_Core.io import get_file_from_archive, load_info_json
from GuiV2.GSMatch2_Core.utils import filename_only
from GuiV2.GSMatch2_Core.watchdog import AuditRecord, time_now

conversion_thread_running = False


class Experiment(Base.GSMBase):
	"""
	GunShotMatch Experiment Class
	"""
	
	type_string = "Experiment"
	
	def __init__(
			self, name, method, user, device, date_created, date_modified,
			version, original_filename=None, original_filetype=0,
			description='', filename=None, identification_performed=False,
			ident_audit_record=None
			):
		"""
		:param name: The name of the Experiment
		:type name: str
		:param method: The name of the file containing the Method used to create the Experiment
		:type method:
		:param user: The user who created the Experiment
		:type user: str
		:param device: The device that created the Experiment
		:type device: str
		:param date_created: The date and time the Experiment was created
		:type date_created:
		:param date_modified: The date and time the Experiment was last modified
		:type date_modified:
		:param version: File format version in semver format
		:type version: str
		:param original_filename: The filename of the file the Experiment was created from
		:type original_filename: str
		:param original_filetype: The filetype of the file the Experiment was created from
		:type original_filetype:int
		:param description: A description of the Experiment
		:type description: str
		:param filename:
		:type filename:
		:param identification_performed: Whether Identify Compounds was performed
		:type identification_performed: bool
		:param ident_audit_record: If Identify Compounds was performed, when and by whom
		:type ident_audit_record: AuditRecord
		"""
		
		Base.GSMBase.__init__(self, name, method, user, device, date_created, date_modified, version, description, filename)
		
		# self._method_files = {method}  # Not needed, experiment stores method internally
		
		self.original_filename = Property(
				f"{name}_original_filename", original_filename, dir,
				help="The name of the datafile the Experiment was created from", label="Original Filename"
				)
		
		self.original_filetype = Property(
				f"{name}_original_filetype", int(original_filetype), format,
				help="The type of datafile the Experiment was created from", label="Original Filetype"
				)
		
		self.description.editable = True
		
		# for experiment in experiments:
		# 	if experiment["Method"] not in self._method_files:
		# 		self._method_files.add(experiment["Method"])
		
		self.expr = None
		self.tic = None
		self.intensity_matrix = None
		self.gcms_data = None
		self.peak_list = None
		self.ident_peaks = None
		
		self.time_step = Property(
				f"{name}_time_step", None, float,
				help="The average time step of the data, in seconds", label="Time Step (seconds)"
				)
		self.time_step_stdev = Property(
				f"{name}_time_step_stdev", None, float,
				help="The standard deviation of the time step of the data, in seconds", label="Time Step σ (seconds)"
				)
		self.n_scans = Property(
				f"{name}_n_scans", None, int,
				help="The number of MS scans in the data", label="Number of Scans"
				)
		self.data_mz_range = Property(
				f"{name}_data_mz_range", (None, None), massrange,
				help="The range of m/z values in the data", label="m/z Range"
				)
		self.data_n_mz_mean = Property(
				f"{name}_data_n_mz_mean", None, Decimal, decimal_format="0.0",
				help="Mean number of m/z values per scan", label="Mean number of m/z values per scan"
				)
		self.data_n_mz_median = Property(
				f"{name}_data_n_mz_median", None, float,
				help="Median number of m/z values per scan", label="Median number of m/z values per scan"
				)
		self.data_rt_range = Property(
				f"{name}_data_rt_range", (None, None), rtrange,
				help="The retention time range of the data, in minutes", label="Data Time Range (minutes)"
				)
		
		self.method_unsaved = False
		self.ammo_details_unsaved = False
		self._unsaved_changes = False
		
		# Compound Identification
		self.identification_performed = identification_performed
		if self.identification_performed:
			self.ident_audit_record = AuditRecord(record_dict=ident_audit_record)
		else:
			self.ident_audit_record = None
	
		# TODO: load compound identities
	
	def get_info_from_gcms_data(self):
		"""
		Method to get information from the :class:`pyms.GCMS.Class.GCMS_data` object contained within experiment
		"""
		
		# TODO: within pyms make read only properties for these private attributes
		
		self.data_rt_range.value = (self.gcms_data._min_rt / 60, self.gcms_data._max_rt / 60)
		self.time_step.value = self.gcms_data._time_step
		self.time_step_stdev.value = self.gcms_data._time_step_std
		self.n_scans.value = len(self.gcms_data.scan_list)
		self.data_mz_range.value = (self.gcms_data._min_mass, self.gcms_data._max_mass)
		
		# calculate median number of m/z values measured per scan
		n_list = []
		scan_list = self.gcms_data.scan_list
		for ii in range(len(scan_list)):
			scan = scan_list[ii]
			n = len(scan)
			n_list.append(n)
		self.data_n_mz_mean.value = mean(n_list)
		self.data_n_mz_median.value = median(n_list)
		
	@classmethod
	def load(cls, filename):
		"""
		Load an Experiment from file
	
		:param filename:
		:type filename:
		"""
		
		experiment_data = load_info_json(filename)
		
		expr = cls(**experiment_data, filename=filename)
		expr.gcms_data = pickle.load(get_file_from_archive(expr.filename.Path, "gcms_data.dat"))
		expr.expr = pickle.load(get_file_from_archive(expr.filename.Path, "experiment.expr"))
		expr.peak_list = pickle.load(get_file_from_archive(expr.filename.Path, "peaks.dat"))
		expr.intensity_matrix = pickle.load(get_file_from_archive(expr.filename.Path, "intensity_matrix.dat"))
		
		if expr.identification_performed:
			expr.ident_peaks = pickle.load(get_file_from_archive(expr.filename.Path, "ident_peaks.dat"))
		
		expr.tic = expr.tic_data[1]

		expr.get_info_from_gcms_data()
		
		return expr
	
	def store(self, filename=None):
		"""
		Save the Project to a file

		:param filename:
		:type filename:

		:return:
		:rtype:
		"""
		
		if filename:
			self.filename.value = filename
		
		self.date_modified.value = time_now()
		
		if any((
				self.expr is None,
				self.tic is None,
				self.peak_list is None,
				self.intensity_matrix is None,
				self.gcms_data is None
				)):
			raise ValueError("Must call 'Experiment.run()' before 'store()'")
		
		# Write experiment, tic and peak list to temporary directory
		with tempfile.TemporaryDirectory() as tmp:
			self.gcms_data.dump(os.path.join(tmp, "gcms_data.dat"))
			self.intensity_matrix.dump(os.path.join(tmp, "intensity_matrix.dat"))
			self.tic.write(os.path.join(tmp, "tic.dat"), formatting=False)
			store_peaks(self.peak_list, os.path.join(tmp, "peaks.dat"), 3)
			store_expr(os.path.join(tmp, "experiment.expr"), self.expr)
			
			with tarfile.open(self.filename.value, mode="w") as experiment_file:
				# # Add the method files
				# for method in self._method_files:
				# 	experiment_file.add(method)
				
				experiment_data = {
					"name": str(self.name),
					"user": str(self.user),
					"device": str(self.device),
					"date_created": float(self.date_created),
					"date_modified": float(self.date_modified),
					"description": str(self.description),
					"version": "1.0.0",
					"method": str(self.method),
					"original_filename": str(self.original_filename),
					"original_filetype": int(self.original_filetype),
					"identification_performed": self.identification_performed,
					"ident_audit_record": None,
					}
				
				if self.identification_performed:
					experiment_data["ident_audit_record"] = dict(self.ident_audit_record)
					store_peaks(self.ident_peaks, os.path.join(tmp, "ident_peaks.dat"), 3)
					experiment_file.add(os.path.join(tmp, "ident_peaks.dat"), arcname="ident_peaks.dat")
				
				# Add the info file to the archive
				info_json = json.dumps(experiment_data, indent=4).encode("utf-8")
				tarinfo = tarfile.TarInfo('info.json')
				tarinfo.size = len(info_json)
				experiment_file.addfile(tarinfo=tarinfo, fileobj=BytesIO(info_json))
				
				# Add the method to the archive
				experiment_file.add(self.method.value, arcname=filename_only(self.method.value))
				
				# Add the experiment, tic, intrnsity_matrix, gcms_data and peak list
				experiment_file.add(os.path.join(tmp, "experiment.expr"), arcname="experiment.expr")
				experiment_file.add(os.path.join(tmp, "tic.dat"), arcname="tic.dat")
				experiment_file.add(os.path.join(tmp, "peaks.dat"), arcname="peaks.dat")
				experiment_file.add(os.path.join(tmp, "gcms_data.dat"), arcname="gcms_data.dat")
				experiment_file.add(os.path.join(tmp, "intensity_matrix.dat"), arcname="intensity_matrix.dat")
		
		return self.filename
	
	def run(self, original_filename, original_filetype):
		"""
		Load the original data from the given datafile and perform quantitative analysis
		
		:param original_filename:
		:type original_filename:
		:param original_filetype:
		:type original_filetype:
		"""
		
		self.original_filename = str(original_filename)
		self.original_filetype = int(original_filetype)
		
		print("Quantitative Processing in Progress...")
		
		# TODO: Include data etc. in experiment file
		
		if self.original_filetype == ID_Format_jcamp:
			# Load data using JCAMP_reader
			from pyms.GCMS.IO.JCAMP import JCAMP_reader
			self.gcms_data = JCAMP_reader(self.original_filename)
		
		elif self.original_filetype == ID_Format_mzML:
			# Load data using JCAMP_reader
			from pyms.GCMS.IO.MZML import mzML_reader
			self.gcms_data = mzML_reader(self.original_filename)
		
		elif self.original_filetype == ID_Format_ANDI:
			# Load data using JCAMP_reader
			from pyms.GCMS.IO.ANDI import ANDI_reader
			self.gcms_data = ANDI_reader(self.original_filename)
		
		else:
			# Unknown Format
			return
		# TODO: Waters RAW, Thermo RAW, Agilent .d
		
		method = Method.Method(self.method.value)
		
		# list of all retention times, in seconds
		# times = self.gcms_data.get_time_list()
		# get Total Ion Chromatogram
		self.tic = self.gcms_data.get_tic()
		# RT Range, time step, no. scans, min, max, mean and median m/z
		self.gcms_data.info()
		
		self.get_info_from_gcms_data()
		
		# Build "intensity matrix" by binning data with integer bins and a
		# 	window of -0.3 to +0.7, the same as NIST uses
		self.intensity_matrix = build_intensity_matrix_i(self.gcms_data)
		
		# Show the m/z of the maximum and minimum bins
		print(" Minimum m/z bin: {}".format(self.intensity_matrix.get_min_mass()))
		print(" Maximum m/z bin: {}".format(self.intensity_matrix.get_max_mass()))
		
		# Crop masses
		min_mass, max_mass, *_ = method.mass_range
		
		if min_mass < self.intensity_matrix.get_min_mass():
			min_mass = self.intensity_matrix.get_min_mass()
		if max_mass > self.intensity_matrix.get_max_mass():
			max_mass = self.intensity_matrix.get_max_mass()
		self.intensity_matrix.crop_mass(min_mass, max_mass)
		
		# Perform Data filtering
		n_scan, n_mz = self.intensity_matrix.get_size()
		
		# Iterate over each IC in the intensity matrix
		for ii in range(n_mz):
			# print("\rWorking on IC#", ii+1, '  ',end='')
			ic = self.intensity_matrix.get_ic_at_index(ii)
			
			if method.expr_creation_enable_sav_gol:
				# Perform Savitzky-Golay smoothing.
				# Note that Turbomass does not use smoothing for qualitative method.
				ic = savitzky_golay(ic)
			
			if method.expr_creation_enable_tophat:
				# Perform Tophat baseline correction
				# Top-hat baseline Correction seems to bring down noise,
				#  		retaining shapes, but keeps points on actual peaks
				ic = tophat(ic, struct=method.tophat_struct)
			
			# Set the IC in the intensity matrix to the filtered one
			self.intensity_matrix.set_ic_at_index(ii, ic)
			
		# Peak Detection based on Biller and Biemann (1974), with a window
		# 	of <points>, and combining <scans> if they apex next to each other
		peak_list = BillerBiemann(
				self.intensity_matrix,
				points=method.expr_creation_bb_points,
				scans=method.expr_creation_bb_scans,
				)
		
		print(" Number of peaks identified before filtering: {}".format(len(peak_list)))
		
		if method.expr_creation_enable_noise_filter:
			# Filtering peak lists with automatic noise filtering
			noise_level = window_analyzer(self.tic)
			# should we also do rel_threshold() here?
			# https://pymassspec.readthedocs.io/en/master/pyms/BillerBiemann.html#pyms.BillerBiemann.rel_threshold
			peak_list = num_ions_threshold(peak_list, method.expr_creation_noise_thresh, noise_level)
		
		self.peak_list = []
		
		for peak_idx, peak in enumerate(peak_list):
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
			
			area = peak_sum_area(self.intensity_matrix, peak)
			peak.set_area(area)
			self.peak_list.append(peak)
			
		print(" Number of peaks identified: {}".format(len(self.peak_list)))
		
		# Create an experiment
		self.expr = pyms.Experiment.Experiment(self.name, self.peak_list)
		self.expr.sele_rt_range(["{}m".format(method.target_range[0]), "{}m".format(method.target_range[1])])
		
	def identify_compounds(self, rt_alignment, n_hits=10):
		"""
		Identify the compounds that produced each of the peaks in the Chromatogram
		
		:param rt_alignment:
		:type rt_alignment:
		:param n_hits: The number of hits to return from NIST MS Search
		:type n_hits: int
		"""
		
		print(f"Identifying Compounds for {self.name}")
		
		rt_list = rt_alignment[self.name]
		# tic = self.tic
		n_peaks = 80
		
		print(rt_list)
		
		# Obtain area for each peak
		peak_area_list = []
		for peak in self.peak_list:
			area = peak.get_area()
			peak_area_list.append(area)
		
		# Write output to CSV file
		combined_csv_file = os.path.join("/home/domdf/.config/GunShotMatch", "{}_COMBINED.csv".format(self.name))
		with open(combined_csv_file, "w") as combine_csv:
			
			# Sample name and header row
			combine_csv.write(f"{self.name}\n{csv_header_row}\n")
			
			report_buffer = []
			# Filter to those peaks present in all samples, by UID
			for peak in self.peak_list:
				
				# if str(rounders(peak.get_rt()/60,"0.000")) in rt_list:
				# print(peak.get_rt()/60.0)
				# TODO: there is a simpler way to do this as part of the DPA functions
				# 	DDF 20/11/19
				# limit to 10 decimal places as that's what Pandas writes JSON data as; no need for greater precision
				print(rounders(peak.get_rt()/60, "0.0000000000"))
				
				if rounders(peak.get_rt() / 60, "0.0000000000") in rt_list:
					print(internal_config.nist_path)
					report_buffer.append([
							'',
							# rounders(peak.get_rt()/60,"0.000"),
							(peak.get_rt() / 60),
							'',
							peak.get_mass_spectrum(),
							# '{:,}'.format(rounders(peak.get_area()/60,"0.0"))
							'{:,}'.format(peak.get_area() / 60),
							peak
							])
			
			# TODO: I thought this was supposed to filter to show the 80 largest peaks,
			# 	but I'm not sure it actually does that
			# 	DDF 20/11/19
			
			# Reverse list order
			report_buffer = report_buffer[::-1]
			# Get last 80 peaks
			report_buffer = report_buffer[:n_peaks]
			# Sort by retention time
			report_buffer.sort(key=operator.itemgetter(1))
			
			# Iterate over peaks
			for row_idx, row in enumerate(report_buffer):
				# TODO: some tidying up here; is writing to disk the most efficient?
				# 	DDF 20/11/19
				
				# Get mass spectrum
				ms = row[3]
				
				qualified_peak = QualifiedPeak.from_peak(row[5])
				
				# Create MSP file for the peak
				create_msp("{}_{}".format(self.name, row[1]), ms.mass_list, ms.mass_spec)
				
				matches_dict = self.nist_ms_comparison(
						"{}_{}".format(self.name, row[1]),
						# ms.mass_list, ms.mass_spec,
						n_hits
						)
				
				combine_csv.write("{};{};Page {} of 80;;;;;;{}\n".format(row[1], row[4], row_idx + 1, row[2]))
				
				for hit in range(1, n_hits + 1):
					search_result = pyms_nist_search.SearchResult.from_pynist(matches_dict["Hit{}".format(hit)])
					
					combine_csv.write(';;{};{};{};{};{};{};\n'.format(
								hit,
								'',  # search_result.library,
								search_result.match_factor,
								search_result.reverse_match_factor,
								search_result.name,
								search_result.cas,
								))
					
					qualified_peak.hits.append(search_result)
					
				time.sleep(2)
		
		return 0
		
	def identify_compounds2(self, target_times, n_hits=10):
		"""
		Identify the compounds that produced each of the peaks in the Chromatogram
		
		:param target_times:
		:type target_times:
		:param n_hits: The number of hits to return from NIST MS Search
		:type n_hits: int
		"""
		
		print(f"Identifying Compounds for {self.name}")
		
		# # Obtain area for each peak
		# peak_area_list = get_area_list(self.peak_list)
		
		# Convert float retention times to Decimal
		# rt_list = [rounders(rt, "0.0000000000") for rt in target_times]
		target_times = target_times.apply(round_rt)
		# Remove NaN values
		rt_list = [rt for rt in target_times if not rt.is_nan()]
		# Sort smallest to largest
		rt_list.sort()
		
		# Write output to CSV file
		combined_csv_file = os.path.join("/home/domdf/.config/GunShotMatch", "{}_COMBINED.csv".format(self.name))
		with open(combined_csv_file, "w") as combine_csv:
			
			# Sample name and header row
			combine_csv.write(f"{self.name}\n{csv_header_row}\n")
			peaks = []
			
			# Filter to those peaks present in all samples, by UID
			for peak in self.peak_list:
				
				rt = (peak.rt / 60)
				rounded_rt = round_rt(rt)
				
				if rounded_rt in rt_list:
					qualified_peak = QualifiedPeak.from_peak(peak)
					qualified_peak.peak_number = target_times[target_times == rounded_rt].index[0]
					
					ms = qualified_peak.mass_spectrum

					# Create MSP file for the peak
					create_msp(
							"{}_{}".format(self.name, rt),
							ms.mass_list,
							ms.mass_spec)
					
					# Actual Search
					matches_dict = self.nist_ms_comparison(
							"{}_{}".format(self.name, rt),
							n_hits
							)
					
					# Add search results to peak
					for hit in range(1, n_hits + 1):
						search_result = pyms_nist_search.SearchResult.from_pynist(matches_dict["Hit{}".format(hit)])
						qualified_peak.hits.append(search_result)
					
					# Write to file
					for row in qualified_peak.to_csv():
						combine_csv.write(f'{";".join(row)}\n')
						
					peaks.append(qualified_peak)
					
					time.sleep(2)
		
		# Add peaks to experiment and save
		self.ident_peaks = peaks
		self.identification_performed = True
		self.ident_audit_record = AuditRecord()
		
		return peaks
		
	def identify_compounds3(self, target_times, n_hits=10):
		"""
		Identify the compounds that produced each of the peaks in the Chromatogram
		
		:param target_times:
		:type target_times:
		:param n_hits: The number of hits to return from NIST MS Search
		:type n_hits: int
		"""
		
		print(f"Identifying Compounds for {self.name}")
		
		peaks = []
		
		# Initialise search engine.
		# TODO: Ideally this can be done once and shared between all experiments
		#  but it breaks when loading the Method editor
		search = pyms_nist_search.Engine(
				Base.FULL_PATH_TO_MAIN_LIBRARY,
				pyms_nist_search.NISTMS_MAIN_LIB,
				Base.FULL_PATH_TO_WORK_DIR,
				debug=True,
				)
		
		# Wrap search in try/except so that the search engine will be uninitialised in the event of an error
		try:
			# Convert float retention times to Decimal
			# rt_list = [rounders(rt, "0.0000000000") for rt in target_times]
			target_times = target_times.apply(round_rt)
			# Remove NaN values
			rt_list = [rt for rt in target_times if not rt.is_nan()]
			# Sort smallest to largest
			rt_list.sort()
			
			# # Obtain area for each peak
			# peak_area_list = get_area_list(self.peak_list)
			
			# Write output to CSV file
			combined_csv_file = os.path.join("/home/domdf/.config/GunShotMatch", "{}_COMBINED.csv".format(self.name))
			with open(combined_csv_file, "w") as combine_csv:
				
				# Sample name and header row
				combine_csv.write(f"{self.name}\n{csv_header_row}\n")
				
				# Filter to those peaks present in all samples, by UID
				for peak in self.peak_list:
					
					rounded_rt = round_rt(peak.rt / 60)
					
					if rounded_rt in rt_list:
						qualified_peak = QualifiedPeak.from_peak(peak)
						qualified_peak.peak_number = target_times[target_times == rounded_rt].index[0]
						
						ms = qualified_peak.mass_spectrum
	
						print(f"Identifying peak at rt {rounded_rt} minutes...")
						
						hit_list = search.full_spectrum_search(ms, n_hits)
						
						# Add search results to peak
						for hit in hit_list:
							qualified_peak.hits.append(hit)
						
						# Write to file
						for row in qualified_peak.to_csv():
							combine_csv.write(f'{";".join(row)}\n')
							
						peaks.append(qualified_peak)
			
			# Add peaks to experiment and save
			self.ident_peaks = peaks
			self.identification_performed = True
			self.ident_audit_record = AuditRecord()
			
		except Exception:
			search.uninit()
			raise
		
		search.uninit()
		return peaks
		
	def nist_ms_comparison(self, sample_name, n_hits=5):
		"""
		
		:param sample_name:
		:type sample_name:
		:param n_hits:
		:type n_hits:

		:return:
		:rtype:
		"""
		
		# data_dict = {}
		
		try:
			pynist.generate_ini(internal_config.nist_path, "mainlib", n_hits)
			
			# def remove_chars(input_string):
			# 	for i in range(n_hits + 1):
			# 		input_string = input_string.replace("Hit {}  : ", "")
			#
			# 	return input_string.replace("MF:", "") \
			# 		.replace(":", "").replace("<", "").replace(">", "") \
			# 		.replace(" ", "").replace(self.name, "")
					
			raw_output = pynist.nist_db_connector(
					internal_config.nist_path,
					os.path.join(internal_config.msp_dir, "{}.MSP".format(sample_name))
					)
			
			# Process output
			for i in range(n_hits + 1):
				raw_output = raw_output.replace("Hit {}  : ".format(i), "Hit{};".format(i)) \
					.replace("Hit {} : ".format(i), "Hit{};".format(i)) \
					.replace("Hit {}: ".format(i), "Hit{};".format(i))
			
			raw_output = raw_output.replace("<<", '"').replace(">>", '"').split("\n")
			
			matches_dict = {}
			
			for i in range(1, n_hits + 1):
				row = list(csv.reader([raw_output[i]], delimiter=";", quotechar='"'))[0]
				
				matches_dict[row[0]] = {
						"Name": row[1], "MF": (row[3].replace("MF:", '').replace(" ", '')),
						"RMF": (row[4].replace("RMF:", '').replace(" ", '')),
						"CAS": (row[6].replace("CAS:", '').replace(" ", '')),
						# "Lib": (row[8].replace("Lib:", '').replace(" ", ''))
						}
		
		except:
			traceback.print_exc()  # print the error
			pynist.reload_ini(internal_config.nist_path)
			sys.exit(1)
		
		print("\r\033[KSearch Complete")  # , end='')
		pynist.reload_ini(internal_config.nist_path)
		return matches_dict
	
	@property
	def experiment_data(self):
		"""
		Returns the PyMassSpec experiment object stored in the experiment.expr file

		:return:
		:rtype:
		"""
		
		# return pickle.load(get_file_from_archive(self.filename.Path, "experiment.expr"))
		return self.expr
	
	@property
	def peak_list_data(self):
		"""
		Returns the PyMassSpec peak list stored in the peaks.dat file
	
		:return:
		:rtype:
		"""

		# peak_list = pickle.load(get_file_from_archive(self.filename.Path, "peaks.dat"))
		#
		# if not isinstance(peak_list, (list, tuple)):
		# 	raise IOError("The selected file is not a List")
		# if not len(peak_list) > 0 or not isinstance(peak_list[0], Peak):
		# 	raise IOError("The selected file is not a list of Peak objects")
		#
		# return peak_list
		return self.peak_list
		
	@property
	def tic_data(self):
		"""
		Returns the TIC stored in the tic.dat file
	
		:return:
		:rtype:
		"""
		
		intensity_list = []
		time_list = []
		
		for row in get_file_from_archive(self.filename.Path, "tic.dat").read().decode("utf-8").split("\n"):
			row = list(filter(None, row.split(" ")))
			if len(row) == 0:
				break
			intensity_list.append(float(row[1]))
			time_list.append(float(row[0]))
		
		intensity_array = numpy.array(intensity_list)
		tic = IonChromatogram(intensity_array, time_list)

		return intensity_array, tic
	
	def _get_all_properties(self):
		"""
		Returns a list containing all of the properties, in the order they should be displayed

		:return:
		:rtype: list
		"""
		
		all_props = Base.GSMBase._get_all_properties(self)
		all_props = all_props[:-2] + [
				self.data_rt_range,
				self.time_step,
				self.time_step_stdev,
				self.n_scans,
				self.data_mz_range,
				self.data_n_mz_mean,
				self.data_n_mz_median,
				# self.filename,
				self.original_filename,
				self.original_filetype,
				self.version,
				]
		return all_props

# Code for running in parallel with old method
#
# # Number of workers for performing Quantitative Processing in parallel
# # If 0 processing will be performed sequentially
# n_quant_workers = self.PL_len
#
# if n_quant_workers:
# 	# Perform Quantitative Processing in parallel
# 	with Pool(n_quant_workers) as p:
# 		p.map(
# 			self.quantitative_processing, [os.path.join(
# 				self.config.raw_dir,
# 				"{}.JDX".format(prefix)
# 			) for prefix in self.config.prefixList])
#
# for prefix in self.config.prefixList:
# 	if not n_quant_workers:
# 		# Perform Quantitative Processing sequentially
# 		self.quantitative_processing(os.path.join(self.config.raw_dir, "{}.JDX".format(prefix)), False)
#
# 	# Read the log file and print the contents
# 	with open(os.path.join(self.config.log_dir, prefix + ".log"), "r") as f:
# 		print(f.read())


@is_documented_by(Experiment.new)
def new(*args, **kwargs):
	return Experiment.new(*args, **kwargs)


@is_documented_by(Experiment.new_empty)
def new_empty():
	return Experiment.new_empty()


@is_documented_by(Experiment.load)
def load(*args, **kwargs):
	return Experiment.load(*args, **kwargs)


def round_rt(rt):
	"""
	Limit to 10 decimal places as that's what Pandas writes JSON data as; no need for greater precision
	
	:param rt:
	:type rt:
	
	:return:
	:rtype:
	"""
	
	return rounders(rt, "0.0000000000")


def get_area_list(peak_list):
	"""
	Obtain area for each peak
	
	:param peak_list:
	:type peak_list:
	
	:return:
	:rtype: list of float
	"""
	
	peak_area_list = []
	for peak in peak_list:
		area = peak.get_area()
		peak_area_list.append(area)
	
	return peak_area_list


csv_header_row = "Retention Time;Peak Area;;Lib;Match;R Match;Name;CAS Number;Notes"
