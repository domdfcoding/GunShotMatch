#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  project.py
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2017-2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import datetime
import json
import os
import pathlib
import shutil
import tarfile
import tempfile
from collections import Counter
from io import BytesIO
from multiprocessing import Pool

# 3rd party
import numpy
import pandas
from chemistry_tools import SpectrumSimilarity
from domdf_python_tools.doctools import is_documented_by

# this package
from GuiV2.GSMatch2_Core import Ammunition, Experiment, Base
from GuiV2.GSMatch2_Core.Config import internal_config
from GuiV2.GSMatch2_Core.InfoProperties import longstr, Property
from GuiV2.GSMatch2_Core.io import get_file_from_archive, load_info_json
from GuiV2.GSMatch2_Core.Project.consolidate import ConsolidatedPeak, ConsolidatedSearchResult, ConsolidateEncoder
from GuiV2.GSMatch2_Core.Project.exporters import MatchesCSVExporter
from GuiV2.GSMatch2_Core.utils import filename_only
from GuiV2.GSMatch2_Core import watchdog


class Project(Base.GSMBase):

	type_string = "Project"

	def __init__(
			self, name, method, user, device, date_created, date_modified,
			version, description='', experiments=None, filename=None, ammo_details=None,
			alignment_performed=False, alignment_audit_record=None,
			consolidate_performed=False, consolidate_audit_record=None, **_
		):
		
		Base.GSMBase.__init__(self, name, method, user, device, date_created, date_modified, version, description, filename)
		
		if experiments:
			self._experiments = experiments #sorted(experiments, key=lambda experiment: experiment.name)
		else:
			self._experiments = []
		
		
		self.ammo_details = Property(
				"Ammunition Details", ammo_details, dir,
				help="The Ammunition Details file for this Project"
				)

		self._experiment_objects = None
		
		# Setup Variables
		self.rt_alignment = None
		self.ms_alignment = None
		self.area_alignment = None
		self.consolidated_peaks = None

		self.alignment_performed = alignment_performed
		if self.alignment_performed:
			self.alignment_audit_record = watchdog.AuditRecord(record_dict=alignment_audit_record)
		else:
			self.alignment_audit_record = None
			
		self.consolidate_performed = consolidate_performed
		if self.consolidate_performed:
			self.consolidate_audit_record = watchdog.AuditRecord(record_dict=consolidate_audit_record)
		else:
			self.consolidate_audit_record = None

		# Load Data
		self.load_alignment_data()
		self.load_consolidate_results()
		
		if self.ammo_details.filename:
			self.ammo_data = Ammunition.load(self.ammo_tarfile)
		
		# TODO: Adding and removing experiments
		
		self.method_unsaved = False
		self.ammo_details_unsaved = False
		self._unsaved_changes = False
		
	def store_new(self, filename=None):
		"""
		Save the Project to a file
		
		:param filename:
		:type filename:
		
		:return:
		:rtype:
		"""
		
		if filename:
			self.filename.value = filename
		
		self.date_modified.value = datetime.datetime.now().timestamp()
		
		with tarfile.open(filename, mode="w") as project_file:
			
			# Sort the experiments
			self._experiments.sort(key=lambda experiment: experiment.name)
			
			# Add the Experiment files
			for experiment in self._experiments:
				project_file.add(experiment["filename"], filename_only(experiment["filename"]))
			
			# Add the info file to the archive
			info_json = json.dumps(self.project_info_dict, indent=4).encode("utf-8")
			tarinfo = tarfile.TarInfo('info.json')
			tarinfo.size = len(info_json)
			project_file.addfile(tarinfo=tarinfo, fileobj=BytesIO(info_json))
			
			# Add the Method and Ammo Details to the archive
			project_file.add(self.method.value, filename_only(self.method.value))
			project_file.add(self.ammo_details.value, filename_only(self.ammo_details.value))
		
		return self.filename.value
	
	@property
	def project_info_dict(self):
		project_info = {
			# The name of the Project
			"name": str(self.name),
			
			# The user who created the Project
			"user": str(self.user),
			
			# The device that created the Project
			"device": str(self.device),
			
			# The date and time the Project was created
			"date_created": float(self.date_created),
			
			# The date and time the Project was last modified
			"date_modified": float(self.date_modified),
			
			# A description of the Project
			"description": str(self.description),
			
			# File format version in semver format
			"version": "1.0.0",
			
			# The name of the file containing the Method used to create the Project
			"method": str(self.method),
			
			# The name of the file containing the Ammunition Details for the Project
			"ammo_details": str(self.ammo_details),
			
			# List of dictionaries containing the experiments
			"experiments": self._experiments,
			
			# Whether alignment was performed
			"alignment_performed": self.alignment_performed,
			
			# If alignment was performed, when and by whom
			"alignment_audit_record": None,
			
			# Whether consolidate was performed
			"consolidate_performed": self.consolidate_performed,
			
			# If consolidate was performed, when and by whom
			"consolidate_audit_record": None,
			}
		
		if self.alignment_performed:
			project_info["alignment_audit_record"] = dict(self.alignment_audit_record)
			
		if self.consolidate_performed:
			project_info["consolidate_audit_record"] = dict(self.consolidate_audit_record)
			
		return project_info

	def store(self, filename=None, remove_alignment=False, resave_experiments=False, remove_consolidate=False):
		"""
		Save the project
		
		:param filename:
		:type filename:
		:param remove_alignment: Whether to remove the alignment data from the file
		:type remove_alignment: bool
		
		:return:
		:rtype:
		"""
		
		# 1. Extract the project tarfile to a temporary directory
		# 2. Move any files that were changed to a timestamped folder
		# 3. In that folder, create a file called "user" containing the username of the user who made the change
		# 4. In the same folder, create a file called "device" containing the hostname of the device
		# 5. Save the changed files to the temporary directory
		# 6. Tar the contents of the temporary directory over the project file
		# 7. Get rid of the temporary directory
		
		if filename:
			self.filename.value = filename
		
		if remove_alignment:
			print(f"Removing Alignment data from {self.filename}")
			self.alignment_performed = False
		elif remove_consolidate:
			print(f"Removing Consolidate data from {self.filename}")
			self.consolidate_performed = False
		else:
			print(f"Saving changes as {self.filename}")
		
		# Set date modified value
		self.date_modified.value = datetime.datetime.now().timestamp()
		
		# One of the files has been changed
		with tempfile.TemporaryDirectory() as tempdir:
			tarfile.open(self.filename.value, mode="r").extractall(tempdir)
			
			tempdir_p = pathlib.Path(tempdir)
			
			if not (tempdir_p / "changes").is_dir():
				(tempdir_p / "changes").mkdir()
			
			timestamp_dir = tempdir_p / "changes" / datetime.datetime.fromtimestamp(
				self.date_modified.value).strftime(
					"%Y%m%d %H%M%S")
			
			timestamp_dir.mkdir()
			
			# The user and device who made the changes
			user, device = watchdog.user_info()
			(timestamp_dir / "user").write_text(user)
			(timestamp_dir / "device").write_text(user)
			
			if resave_experiments:
				# Move old experiment objects to timestamp_dir
				for expr_obj, expr_filename in zip(self.experiment_objects, self.experiment_file_list):
					expr_filename = filename_only(expr_filename)
					shutil.move(tempdir_p / expr_filename, timestamp_dir / expr_filename)
					expr_obj.store(tempdir_p / expr_filename)
			
			if self.method_unsaved:
				shutil.copy2(
						tempdir_p / filename_only(self.method.value),
						timestamp_dir / filename_only(self.method.value))
			
			# TODO: Add the new method file and change copy2 above to move
			print(self.ammo_details_unsaved)

			if self.ammo_details_unsaved:
				shutil.move(tempdir_p / filename_only(self.ammo_details.value),
							timestamp_dir / filename_only(self.ammo_details.value))

				self.ammo_data.store(tempdir_p / filename_only(self.ammo_details.value))
			
			shutil.move(tempdir_p / "info.json", timestamp_dir / "info.json")
			
			if remove_alignment:
				# Move the alignment files to the timestamp_dir
				for fname in {
						"alignment_area.csv", "alignment_rt.csv",
						"alignment_ms.json", "alignment_rt.json",  "alignment_area.json"
						}:
					try:
						shutil.move(tempdir_p / fname, timestamp_dir / fname)
					except FileNotFoundError:
						pass
			elif remove_consolidate:
				# Move the consolidate files to the timestamp_dir
				try:
					shutil.move(tempdir_p / "consolidate.json", timestamp_dir / "consolidate.json")
				except FileNotFoundError:
					pass
			
			# Add the info file to the archive
			info_json = json.dumps(self.project_info_dict, indent=4)
			(tempdir_p / "info.json").write_text(info_json)
			
			if self.consolidate_performed:
				# Add the consolidate data file to the archive
				consolidate_json = json.dumps(self.consolidated_peaks, indent=4, cls=ConsolidateEncoder)
				(tempdir_p / "consolidate.json").write_text(consolidate_json)
			
			# Tar the contents of the temporary directory over the project file
			with tarfile.open(self.filename.value, mode="w") as project_file:
				project_file.add(tempdir_p, arcname="")
		
		# Mark as saved
		self.mark_all_saved()
		
		return self.filename.value
	
	def mark_all_saved(self):
		self._unsaved_changes = False
		self.ammo_details_unsaved = False
		self.method_unsaved = False
	
	def remove_alignment(self):
		"""
		Remove the alignment data from the project

		:return:
		:rtype:
		"""
		
		self.store(remove_alignment=True)
		
	def remove_consolidate(self):
		"""
		Remove the consolidate data from the project

		:return:
		:rtype:
		"""
		
		self.store(remove_consolidate=True)
	
	def add_to_archive(self, filename, arcname=None):
		# Check if the file already exists in the archive:
		archive = tarfile.open(self.filename.value, mode="r")

		if (arcname and arcname in archive.getnames()) or (filename in archive.getnames()):
			# File is already in archive
			return False
		
		with tarfile.open(self.filename.value, mode="a") as project_file:
			project_file.add(filename, arcname)
		
		return True
	
	# Experiments
	
	def add_experiment(self, filename):
		experiment_info = load_info_json(filename)
		if filename in self.experiment_file_list:
			raise ValueError(f"The experiment '{filename}' is already in the project")
		
		experiment_info["filename"] = filename
		
		self._experiments.append(experiment_info)
	
	@property
	def experiments(self):
		return self._experiments
	
	@property
	def experiment_file_list(self):
		return [experiment["filename"] for experiment in self.experiments]
	
	@property
	def experiment_name_list(self):
		return [experiment["name"] for experiment in self.experiments]
	
	def remove_experiment(self, filename):
		self._experiments = [experiment for experiment in self._experiments if experiment["filename"] != filename]
	
	def _load_experiments(self):
		"""
		Load the experiments from file
		"""
		
		for filename in self.experiment_file_list:
			#self._experiment_objects.append(Experiment.load(filename))
			
			# Get Experiment tarfile from the Project tarfile and convert to BytesIO
			expr_tarfile = BytesIO(get_file_from_archive(str(self.filename.value), filename_only(filename)).read())
		
			# Load the Experiment
			expr = Experiment.Experiment.load(expr_tarfile)
			
			# Add the Experiment to the list of Experiment objects
			self._experiment_objects.append(expr)
	
	@property
	def experiment_objects(self):
		"""
		
		:return:
		:rtype:
		"""
		
		if self._experiment_objects:
			return self._experiment_objects
		else:
			self._experiment_objects = []
			self._load_experiments()
			return self._experiment_objects
	
	# Analysis
	
	def align(self):
		"""
		Perform Peak Alignment on the selected experiments
		"""
		print(self.alignment_performed)
		print(self.alignment_audit_record)
		
		if self.alignment_performed:
			raise ValueError(f"Alignment has already been performed.\n{self.alignment_audit_record}")
		
		# Imports
		from pyms.DPA.Alignment import exprl2alignment
		from pyms.DPA.PairwiseAlignment import align_with_tree, PairwiseAlignment
		from pyms.json import PyMassSpecEncoder
		
		# Perform dynamic peak alignment
		print("\nAligning\n")
		
		# Read the experiment.expr file from each experiment into a list

		pyms_expr_list = []
	
		for experiment in self.experiment_objects:
			pyms_expr_list.append(experiment.experiment_data)
		
		print(pyms_expr_list)
		
		F1 = exprl2alignment(pyms_expr_list)
		print(F1)
		
		T1 = PairwiseAlignment(F1, self.method_data.rt_modulation, self.method_data.gap_penalty)
		A1 = align_with_tree(T1, min_peaks=self.method_data.min_peaks)
		
		# Save alignment to file and then add to tarfile
		with tempfile.TemporaryDirectory() as tmp:
			
			A1.write_csv(
				os.path.join(tmp, 'alignment_rt.csv'),
				os.path.join(tmp, 'alignment_area.csv'))
			self.add_to_archive(os.path.join(tmp, 'alignment_rt.csv'), arcname="alignment_rt.csv")
			self.add_to_archive(os.path.join(tmp, 'alignment_area.csv'), arcname="alignment_area.csv")
		
			self.rt_alignment = A1.get_peak_alignment(require_all_expr=False)
			self.rt_alignment.to_json(os.path.join(tmp, 'alignment_rt.json'))
			self.add_to_archive(os.path.join(tmp, 'alignment_rt.json'), arcname="alignment_rt.json")

			self.ms_alignment = A1.get_ms_alignment(require_all_expr=False)
			# self.ms_alignment.to_json(os.path.join(tmp, 'alignment_ms.json'))
			with open(os.path.join(tmp, 'alignment_ms.json'), "w") as fp:
				json.dump(self.ms_alignment.to_dict(), fp, cls=PyMassSpecEncoder)
			self.add_to_archive(os.path.join(tmp, 'alignment_ms.json'), arcname="alignment_ms.json")
		
			self.area_alignment = A1.get_area_alignment(require_all_expr=False)
			self.area_alignment.to_json(os.path.join(tmp, 'alignment_area.json'))
			self.add_to_archive(os.path.join(tmp, 'alignment_area.json'), arcname="alignment_area.json")
		
		self.alignment_performed = True
		self.alignment_audit_record = watchdog.AuditRecord()
		self.date_modified.value = datetime.datetime.now().timestamp()
		self.store()
		
	def load_alignment_data(self):
		
		if self.alignment_performed:
			from pyms.Spectrum import MassSpectrum
			
			self.rt_alignment = pandas.read_json(get_file_from_archive(self.filename.Path, 'alignment_rt.json'))
			
			# To make sure that columns of dataframe are in the same order as the experiment name list
			if self.rt_alignment.columns.tolist() != self.experiment_name_list:
				self.rt_alignment = self.rt_alignment[self.experiment_name_list]
				
			self.area_alignment = pandas.read_json(get_file_from_archive(self.filename.Path, 'alignment_area.json'))
			
			# To make sure that columns of dataframe are in the same order as the experiment name list
			if self.area_alignment.columns.tolist() != self.experiment_name_list:
				self.area_alignment = self.area_alignment[self.experiment_name_list]
				
			raw_ms_alignment = json.load(get_file_from_archive(self.filename.Path, 'alignment_ms.json'))
			
			ordered_ms_alignment = {}
			
			for expr, peaks in raw_ms_alignment.items():
				ordered_ms_alignment[expr] = []

				for peak_idx in range(1, len(peaks)):
					peak_idx = str(peak_idx)
					if peaks[peak_idx]:
						peaks[peak_idx] = MassSpectrum.from_dict(peaks[peak_idx])
					ordered_ms_alignment[expr].append(peaks[peak_idx])
			
			self.ms_alignment = pandas.DataFrame(data=ordered_ms_alignment)
			
	def load_consolidate_results(self):

		if self.consolidate_performed:
			archive = tarfile.open(self.filename.value, mode="r")
			raw_consolidated_peaks = json.load(get_file_from_archive(archive, "consolidate.json"))
			archive.close()
			
			self.consolidated_peaks = []
			
			for peak in raw_consolidated_peaks:
				for hit_idx, hit in enumerate(peak["hits"]):
					peak["hits"][hit_idx] = ConsolidatedSearchResult(**hit)
				
				self.consolidated_peaks.append(ConsolidatedPeak(**peak))
		
		
			for peak in self.consolidated_peaks:
				print(peak)
				print(peak.peak_number)
				for hit in peak.hits:
					print(hit)
			
	# Identify Compounds
	
	def identify_compounds(self):
		"""
		Perform Compound Identification on the selected experiments
		"""
		
		if not self.alignment_performed:
			raise ValueError("Peak Alignment must be performed first")
		
		# Check which, if any, experiments have had identification performed already
		identify_performed = []
		
		for experiment in self.experiment_objects:
			if experiment.identification_performed:
				identify_performed.append(experiment)
		
		print(identify_performed)
		
		if identify_performed:
			error_string = "Compound Identification has already been performed for the following experiments"

			for experiment in identify_performed:
				error_string += f"\n{experiment.name}: {experiment.ident_audit_record}"

			raise ValueError(error_string)
		
		# Perform compound identification for each experiment
		
		# Based on the identification settings, determine which peaks to identify
		
		peak_areas = []

		# print(self.area_alignment)
		# print(self.rt_alignment)
		# Can use pandas._libs.json.dumps to get "dict" like output for a class.
		# Probably one way as it might not include all internal variables
		
		# Calculate average peak area for each of the aligned peaks
		for index, areas in self.area_alignment.iterrows():
			# peak_areas.append(statistics.mean([area for area in areas if not numpy.isnan(area)]))
			peak_areas.append(float(numpy.nanmean(areas)))
		
		peak_areas = pandas.DataFrame(peak_areas, columns=["Peak Area"])
		
		# Filter to only aligned peaks that appear in more samples than `ident_min_aligned_peaks`
		peaks_to_identify = self.rt_alignment.dropna(
				thresh=4)
				# thresh=self.method_data.ident_min_aligned_peaks)
		
		# Remove peaks from peak_areas if they are not in peaks_to_identify,
		# i.e. they appear in more samples than `ident_min_aligned_peaks`
		peak_areas = peak_areas.filter(peaks_to_identify.index, axis=0)
		
		# Sort peak_areas from largest (top) to smallest
		peak_areas = peak_areas.sort_values(by="Peak Area")
		
		# Get indices of top n peaks based on `ident_top_peaks`
		top_peaks_indices = []
		
		for top_peak_idx, row in enumerate(peak_areas.iterrows()):
			if top_peak_idx < 20:  # ident_top_peaks
				# print(row_idx)
				top_peaks_indices.append(row[0])
		
		# Remove peaks from peaks_to_identify if they are not in
		# top_peaks_indices, i.e. they are one of the top n largest peaks
		peaks_to_identify = peaks_to_identify.filter(top_peaks_indices, axis=0)
		
		for experiment in self.experiment_objects:
			# print(peaks_to_identify[experiment.name])
			ident_peaks = experiment.identify_compounds2(peaks_to_identify[experiment.name])
			
		# Resave the project, including the experiment files
		self.store(resave_experiments=True)
		
		# TODO: Here's what to do:
		#  Make Experiment file mutable ONLY to remove compound identification data
		#  Add following settings to method:
		#	 Identication Min Match Factor
		#	 Identification Min Aligned peaks
		#		 - defaults to 0 if being run on standalone experiment regardless of method setting
		#	 Identification Top Peaks Num
		#		 - If running on a standalone experiment, the largest n peaks in the experiment
		#		 - If running on project, n largest aligned peaks, sorted by average peak area
		#			 (where the average ignores experiments that don;t have the peak)
		# DDF 27/Jan/2020
		
		return
		
	# Properties
	
	@property
	def all_properties(self):
		"""
		Returns a list containing all of the properties, in the order they should be displayed
		
		:return:
		:rtype: list
		"""
		
		return [
				self.description,
				self.user,
				self.device,
				self.date_created,
				self.date_modified,
				self.method,
				self.ammo_details,
				self.filename,
				self.version,
				]
	
	@property
	def ammo_tarfile(self):
		"""
		
		
		:return:
		:rtype:
		"""

		# Get Ammunition Details tarfile from the Project tarfile and convert to BytesIO
		return BytesIO(get_file_from_archive(self.filename.value, filename_only(self.ammo_details.value)).read())
	
	def __repr__(self):
		return f"Project({self.name})"
	
	@property
	def unsaved_changes(self):
		
		return any([self.ammo_details_unsaved, self.method_unsaved, self._unsaved_changes])
	
	@unsaved_changes.setter
	def unsaved_changes(self, value):
		self._unsaved_changes = bool(value)
	
	def export_method(self, output_filename):
		with open(output_filename, 'w') as f:
			f.write(get_file_from_archive(self.filename.Path, self.method.filename).read().decode("utf-8"))
	
	def export_ammo_details(self, output_filename):
		self.ammo_tarfile.seek(0)
		with open(output_filename, 'wb') as f:
			shutil.copyfileobj(self.ammo_tarfile, f, length=131072)
	
	def match_counter(self, ms_comp_list):
		"""
		Counter
		Also generates final output

		:param ms_comp_list:
		:type ms_comp_list:
		:param separator:
		:type separator: str
		"""
		
		peak_numbers = set()
		for experiment in self.experiment_objects:
			for peak in experiment.ident_peaks:
				peak_numbers.add(peak.peak_number)
				
		# Convert peak_numbers to a list and sort smallest to largest
		peak_numbers = sorted(list(peak_numbers))
		
		aligned_peaks = []
		self.consolidated_peaks = []
		
		n_hits = 5
		
		for n in peak_numbers:
			row = []
			for experiment in self.experiment_objects:
				print(experiment.name)
				for peak in experiment.ident_peaks:
					if peak.peak_number == n:
						row.append(peak)
						break
				else:
					row.append(None)
			
			aligned_peaks.append(row)
			
			rt_data = []
			area_data = []
			ms_data = []
			hits = []
			names = []
			
			print(n)
			
			for peak in row:
				if peak:
					rt_data.append(peak.rt)
					area_data.append(peak.area)
					ms_data.append(peak.mass_spectrum)
					
					for hit in peak.hits:
						hits.append(hit)
						names.append(hit.name)
					
				else:
					rt_data.append(numpy.nan)
					area_data.append(numpy.nan)
					ms_data.append(None)
			
			names.sort()
			names_count = Counter(names)
			print(names)
			import pprint
			print(pprint.pprint(names_count))
			
			consolidated_peak = ConsolidatedPeak(rt_data, area_data, ms_data, peak_number=n)
			
			hits_data = []
			
			print(rt_data)
			print(area_data)
			
			for compound, count in names_count.items():
				mf_data = []
				rmf_data = []
				hit_num_data = []
				
				for peak in row:
					if peak is None:
						mf_data.append(numpy.nan)
						rmf_data.append(numpy.nan)
						hit_num_data.append(numpy.nan)
					
					else:
						for hit_idx, hit in enumerate(peak.hits):
							if hit.name == compound:
								mf_data.append(hit.match_factor)
								rmf_data.append(hit.reverse_match_factor)
								hit_num_data.append(hit_idx+1)
								CAS = hit.cas
								break
						else:
							mf_data.append(numpy.nan)
							rmf_data.append(numpy.nan)
							hit_num_data.append(numpy.nan)
				
				hits_data.append(ConsolidatedSearchResult(compound, CAS, mf_data, rmf_data, hit_num_data))
			
			# Sort consolidated hit list
			hits_data = sorted(hits_data, key=lambda k: (len(k), k.match_factor, k.average_hit_number), reverse=True)
			consolidated_peak.hits = hits_data[:n_hits]
			
			pprint.pprint(hits_data)
			
			self.consolidated_peaks.append(consolidated_peak)
		
		print(len(self.consolidated_peaks))
		
		# Matches Sheet
		MatchesCSVExporter(self, os.path.join(internal_config.csv_dir, self.name + "_MATCHES.csv"), minutes=True,
						   n_hits=n_hits)
		
		return
		"""Get list of CAS Numbers for compounds reported in literature"""
		with open("./lib/CAS.txt", "r") as f:
			CAS_list = f.readlines()
		for index, CAS in enumerate(CAS_list):
			CAS_list[index] = CAS.rstrip("\r\n")
		
		# Statistics Sheet
		statistics_full_output = open(os.path.join(
				self.config.csv_dir,
				"{}_STATISTICS_FULL.csv".format(self.lot_name)
				), "w")
		
		statistics_output = open(os.path.join(
				self.config.csv_dir,
				"{}_STATISTICS.csv".format(self.lot_name)
				), "w")
		
		statistics_lit_output = open(os.path.join(
				self.config.csv_dir,
				"{}_STATISTICS_LIT.csv".format(self.lot_name)
				), "w")
		
		statistics_header = ";".join([
											 self.lot_name, '', '', '',
											 "Retention Time", '', '', '',
											 "Peak Area", '', '', '',
											 "Match Factor", '', '', '',
											 "Reverse Match Factor", '', '', '',
											 "Hit Number", '', '', '',
											 "MS Comparison", '', '', '',
											 "\nName", "CAS Number", '', ''
											 ] + ["Mean", "STDEV", "%RSD", ''] * 6) + "\n"
		
		statistics_full_output.write(statistics_header)
		statistics_output.write(statistics_header)
		statistics_lit_output.write(statistics_header)
		
		# Initialise dictionary for chart data
		chart_data = {
				"Compound": [],
				"{} Peak Area".format(self.lot_name): [],
				"{} Standard Deviation".format(self.lot_name): []
				}
		
		for prefix in self.config.prefixList:
			chart_data[prefix] = []
		
		for peak, ms in zip(peak_data, ms_comp_list):
			peak["ms_comparison"] = ms
			
			write_peak(statistics_full_output, peak, ms)
			if peak["hits"][0]["Count"] > (len(self.experiment_name_list) / 2):  # Write to Statistics; TODO: also need similarity > 800
				write_peak(statistics_output, peak, ms)
				if peak["hits"][0]["CAS"].replace("-", "") in CAS_list:  # Write to Statistics_Lit
					write_peak(statistics_lit_output, peak, ms)
					# Create Chart Data
					chart_data["Compound"].append(peak["hits"][0]["Name"])
					for prefix, area in zip(self.config.prefixList, peak["area_data"]):
						chart_data[prefix].append(area)
					chart_data["{} Peak Area".format(self.lot_name)].append(numpy.mean(peak["area_data"]))
					chart_data["{} Standard Deviation".format(self.lot_name)].append(numpy.mean(peak["area_data"]))
		
		statistics_full_output.close()
		statistics_output.close()
		statistics_lit_output.close()
		
		with open(os.path.join(self.config.csv_dir, "{}_peak_data.json".format(self.lot_name)), "w") as jsonfile:
			for dictionary in peak_data:
				jsonfile.write(json.dumps(dictionary))
				jsonfile.write("\n")
		
		time.sleep(2)
		
		"""Convert to XLSX and format"""
		# GC-MS
		append_to_xlsx(
				os.path.join(self.config.csv_dir, "{}_MERGED.csv".format(self.lot_name)),
				os.path.join(self.config.results_dir, self.lot_name + "_FINAL.xlsx"),
				"GC-MS", overwrite=True, separator=";",
				toFloats=True
				)
		# Counter
		append_to_xlsx(
				os.path.join(self.config.csv_dir, "{}_MATCHES.csv".format(self.lot_name)),
				os.path.join(self.config.results_dir, self.lot_name + "_FINAL.xlsx"),
				"Matches",
				separator=";",
				toFloats=True
				)
		# Statistics_Full
		append_to_xlsx(
				os.path.join(self.config.csv_dir, "{}_STATISTICS_FULL.csv".format(self.lot_name)),
				os.path.join(self.config.results_dir, self.lot_name + "_FINAL.xlsx"),
				"Statistics_Full",
				separator=";",
				toFloats=True
				)
		# Statistics
		append_to_xlsx(
				os.path.join(self.config.csv_dir, "{}_STATISTICS.csv".format(self.lot_name)),
				os.path.join(self.config.results_dir, self.lot_name + "_FINAL.xlsx"),
				"Statistics",
				separator=";",
				toFloats=True
				)
		# Statistics_Lit
		append_to_xlsx(
				os.path.join(self.config.csv_dir, "{}_STATISTICS_LIT.csv".format(self.lot_name)),
				os.path.join(self.config.results_dir, self.lot_name + "_FINAL.xlsx"),
				"Statistics - Lit Only",
				separator=";",
				toFloats=True
				)
		
		self.format_xlsx(os.path.join(self.config.results_dir, self.lot_name + "_FINAL.xlsx"))
		
		"""Charts"""
		chart_data = pandas.DataFrame(chart_data)
		print(chart_data)
		return chart_data
	
	def ms_comparisons(self, ms_data):
		"""
		Between Samples Spectra Comparison

		:param ms_data:
		:type ms_data:

		:return:
		:rtype:
		"""
		
		from itertools import permutations
		
		perms = []
		
		for i in permutations(self.experiment_name_list, 2):
			# from https://stackoverflow.com/questions/10201977/how-to-reverse-tuples-in-python
			if i[::-1] not in perms:
				perms.append(i)

		ms_comparison = []

		rows_list = []

		for row_idx in range(len(ms_data)):
			similarity_list = []
			rows_list.append((ms_data.iloc[row_idx], perms))
		
		with Pool(len(ms_data.columns)) as p:
			ms_comparison = p.map(single_ms_comparison, rows_list)

		# TODO: linear mode

		# for row_idx in range(len(ms_data)):
		# similarity_list = []
		# row = ms_data.iloc[row_idx]
		# for perm in perms:

		# top_spec = numpy.column_stack((row.loc[perm[0]].mass_list, row.loc[perm[0]].mass_spec))
		# bottom_spec = numpy.column_stack((row.loc[perm[1]].mass_list, row.loc[perm[1]].mass_spec))
		# similarity_list.append(SpectrumSimilarity.SpectrumSimilarity(top_spec, bottom_spec, t = 0.25, b = 1,
		# xlim = (45, 500), x_threshold = 0, print_graphic = False)[0]*1000)

		# #ms_comparison.append(rounders((numpy.mean(similarity_list)*100),"0"))
		# ms_comparison.append(similarity_list)
		print(perms)
		return ms_comparison

	def consolidate(self):
		"""
		Consolidate the compound identification from the experiments into a single dataset
		"""
		ms_comparisons = self.ms_comparisons(self.ms_alignment)
		print(ms_comparisons)
		chart_data = self.match_counter(ms_comparisons)
		
		self.consolidate_performed = True
		self.consolidate_audit_record = watchdog.AuditRecord()
		self.date_modified.value = datetime.datetime.now().timestamp()
		self.store()
		
		
	# 	chart_data = chart_data.set_index("Compound", drop=True)
	#
	# 	# remove duplicate compounds:
	# 	# chart_data_count = Counter(chart_data["Compound"])
	# 	chart_data_count = Counter(chart_data.index)
	# 	replacement_data = {
	# 			"Compound": [], f"{self.lot_name} Peak Area": [],
	# 			f"{self.lot_name} Standard Deviation": []
	# 			}
	#
	# 	for prefix in self.config.prefixList:
	# 		replacement_data[prefix] = []
	#
	# 	for compound in chart_data_count:
	# 		if chart_data_count[compound] > 1:
	# 			replacement_data["Compound"].append(compound)
	# 			replacement_data[f"{self.lot_name} Peak Area"].append(
	# 					sum(chart_data.loc[compound, f"{self.lot_name} Peak Area"]))
	#
	# 			peak_data = []
	# 			for prefix in self.config.prefixList:
	# 				replacement_data[prefix].append(sum(chart_data.loc[compound, prefix]))
	# 				peak_data.append(sum(chart_data.loc[compound, prefix]))
	#
	# 			replacement_data[f"{self.lot_name} Standard Deviation"].append(numpy.std(peak_data))
	#
	# 			chart_data = chart_data.drop(compound, axis=0)
	#
	# 	replacement_data = pandas.DataFrame(replacement_data)
	# 	replacement_data = replacement_data.set_index("Compound", drop=False)
	# 	chart_data = chart_data.append(replacement_data, sort=False)
	# 	chart_data.sort_index(inplace=True)
	# 	chart_data = chart_data.drop("Compound", axis=1)
	# 	chart_data['Compound Names'] = chart_data.index
	#
	# 	chart_data.to_csv(os.path.join(self.config.csv_dir, "{}_CHART_DATA.csv".format(self.lot_name)), sep=";")
	#
	#
@is_documented_by(Project.new)
def new(*args, **kwargs):
	return Project.new(*args, **kwargs)


@is_documented_by(Project.new_empty)
def new_empty():
	return Project.new_empty()


@is_documented_by(Project.load)
def load(*args, **kwargs):
	return Project.load(*args, **kwargs)


def single_ms_comparison(arguments):
	"""
	Performs a single Mass Spectrum similarity calculation for the same peak in
		two different samples.

	:param arguments: tuple containing mass spectrum data and the samples to
		which these spectra belong
	:type arguments: tuple
	:return:
	:rtype:
	"""
	
	ms_data, perms = arguments
	
	similarity_list = []
	
	for perm in perms:
		top_ms = ms_data.loc[perm[0]]
		bottom_ms = ms_data.loc[perm[1]]
		
		if top_ms is None or bottom_ms is None:
			similarity_list.append(None)
		else:
			top_spec = numpy.column_stack((ms_data.loc[perm[0]].mass_list, ms_data.loc[perm[0]].mass_spec))
			bottom_spec = numpy.column_stack((ms_data.loc[perm[1]].mass_list, ms_data.loc[perm[1]].mass_spec))
			similarity_list.append(SpectrumSimilarity.SpectrumSimilarity(
					top_spec, bottom_spec, t=0.25, b=1, xlim=(45, 500),
					x_threshold=0, print_graphic=False
					)[0] * 1000)
		
	return similarity_list


def align_in_separate_process(project):
	project.align()


def identify_in_separate_process(project):
	project.identify_compounds()
	
	
def consolidate_in_separate_process(project):
	project.consolidate()
