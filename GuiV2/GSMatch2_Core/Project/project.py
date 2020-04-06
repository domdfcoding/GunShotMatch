#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  project.py
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
from chemistry_tools import spectrum_similarity
from domdf_python_tools.doctools import is_documented_by
from domdf_python_tools.paths import maybe_make
from mathematical.utils import rounders
import pyms_nist_search


# this package
from GuiV2.GSMatch2_Core import Ammunition, Base, Experiment, watchdog
from GuiV2.GSMatch2_Core.Config import internal_config
from GuiV2.GSMatch2_Core.InfoProperties import Property
from GuiV2.GSMatch2_Core.io import get_file_from_archive, load_info_json
from GuiV2.GSMatch2_Core.Project.consolidate import (
	ConsolidatedPeak, ConsolidatedSearchResult, ConsolidateEncoder,
	ConsolidatePeakFilter,
	)
from GuiV2.GSMatch2_Core.Project.exporters import MatchesCSVExporter, StatisticsXLSXExporter
from GuiV2.GSMatch2_Core.utils import filename_only


class Project(Base.GSMBase):

	type_string = "Project"

	def __init__(
			self, name, method, user, device, date_created, date_modified,
			version, description='', experiments=None, filename=None, ammo_details=None,
			alignment_performed=False, alignment_audit_record=None,
			consolidate_performed=False, consolidate_audit_record=None, **_
		):
		"""
		
		:param name: The name of the Project
		:type name: str
		:param method:
		:type method:
		:param user: The user who created the Project
		:type user: str
		:param device: The device that created the Project
		:type device: str
		:param date_created: The date and time the Project was created
		:type date_created: datetime.datetime
		:param date_modified: The date and time the Project was last modified
		:type date_modified: datetime.datetime
		:param version: File format version in semver format
		:type version:
		:param description: A description of the Project
		:type description: str
		:param experiments:
		:type experiments:
		:param filename:
		:type filename:
		:param ammo_details:
		:type ammo_details:
		:param alignment_performed: Whether alignment was performed
		:type alignment_performed: bool
		:param alignment_audit_record: If alignment was performed, when and by whom
		:type alignment_audit_record: watchdog.AuditRecord
		:param consolidate_performed: Whether consolidate was performed
		:type consolidate_performed: bool
		:param consolidate_audit_record: If consolidate was performed, when and by whom
		:type consolidate_audit_record: watchdog.AuditRecord
		"""
		
		Base.GSMBase.__init__(self, name, method, user, device, date_created, date_modified, version, description, filename)
		
		if experiments:
			self._experiments = experiments  # sorted(experiments, key=lambda experiment: experiment.name)
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
			self.ammo_data = Ammunition.load(self.ammo_file)
		
		# TODO: Adding and removing experiments
		
		self.method_unsaved = False
		self.ammo_details_unsaved = False
		self._unsaved_changes = False
		
	def store_new(self, filename=None):
		"""
		Save the Project to a file
		
		:param filename: The filename to save the Project as
		:type filename: str
		
		:return: The filename the Project was saved as
		:rtype: str
		"""
		
		if filename:
			self.filename.value = filename
		
		self.date_modified.value = datetime.datetime.now().timestamp()
		
		with tarfile.open(filename, mode="w") as project_file:
			
			# Sort the experiments
			self._experiments.sort(key=lambda expr: expr.name)
			
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
		"""
		Returns the dictionary that makes up the `info.json` file.

		:rtype: dict
		"""
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
		
		:param filename: The filename to save the Project as
		:type filename: str, optional
		:param remove_alignment: Whether to remove the alignment data from the file. Default False
		:type remove_alignment: bool, optional
		:param resave_experiments: Whether the experiments should be resaved. Default False
		:type resave_experiments: bool, optional
		:param remove_consolidate: Whether to remove the Consolidate data. Default False
		:type remove_consolidate: bool, optional
		
		:return: The filename of the saved project
		:rtype: str
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
			(timestamp_dir / "device").write_text(device)
			
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
				print("Saving new Method")
				self.method_data.save_method(tempdir_p / filename_only(self.method.value))
				
			# TODO: Add the new method file and change copy2 above to move
			print(self.ammo_details_unsaved)

			if self.ammo_details_unsaved:
				shutil.move(
						tempdir_p / filename_only(self.ammo_details.value),
						timestamp_dir / filename_only(self.ammo_details.value)
						)

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
				# for peak in self.consolidated_peaks:
				# 	for hit in peak.hits:
				# 		print(hit.reference_data)
				# 		print(hit.reference_data.mass_spec)
				# 		print(hit.reference_data.__dict__(recursive=True)["mass_spec"])
				# 		print("^^^^^")
				# TODO: flag to show consolidated_peaks has been changed
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
			# self._experiment_objects.append(Experiment.load(filename))
			
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
		
		F1 = exprl2alignment(pyms_expr_list)
		
		T1 = PairwiseAlignment(F1, self.method_data.alignment_rt_modulation, self.method_data.alignment_gap_penalty)
		A1 = align_with_tree(T1, min_peaks=self.method_data.alignment_min_peaks)
		
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

				for peak_idx in range(len(peaks)):
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
				self.consolidated_peaks.append(ConsolidatedPeak.from_dict(peak))
				
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
				
		if identify_performed:
			error_string = "Compound Identification has already been performed for the following experiments"

			for experiment in identify_performed:
				error_string += f"\n{experiment.name}: {experiment.ident_audit_record}"

			raise ValueError(error_string)
		
		# Perform compound identification for each experiment
		
		# Based on the identification settings, determine which peaks to identify
		
		peak_areas = []

		# Can use pandas._libs.json.dumps to get "dict" like output for a class.
		# Probably one way as it might not include all internal variables
		
		pandas.set_option("display.max_rows", None, "display.max_columns", None)
		
		# Calculate average peak area for each of the aligned peaks
		for index, areas in self.area_alignment.iterrows():
			# peak_areas.append(statistics.mean([area for area in areas if not numpy.isnan(area)]))
			peak_areas.append(float(numpy.nanmean(areas)))
		
		peak_areas = pandas.DataFrame(peak_areas, columns=["Peak Area"])
		
		print(peak_areas)
		
		# Filter to only aligned peaks that appear in more samples than `ident_min_aligned_peaks`
		print(f"Filtering to only those peaks in more than {self.method_data.ident_min_aligned_peaks} experiments")
		peaks_to_identify = self.rt_alignment.dropna(
				# thresh=4)
				thresh=self.method_data.ident_min_aligned_peaks)
		print(peaks_to_identify)

		# TODO: Filter peaks by min_match_factor
		
		# Remove peaks from peak_areas if they are not in peaks_to_identify,
		# i.e. they appear in more samples than `ident_min_aligned_peaks`
		peak_areas = peak_areas.filter(peaks_to_identify.index, axis=0)
		print(peak_areas)
		# Sort peak_areas from largest (top) to smallest
		peak_areas = peak_areas.sort_values(by="Peak Area")
		
		# Get indices of top n peaks based on `ident_top_peaks`
		top_peaks_indices = []
		
		method_data = self.method_data
		
		print("########")
		print(peak_areas.tail(self.method_data.ident_top_peaks))
		
		# Limit to the largest `ident_top_peaks` peaks
		for peak_no, areas in peak_areas.tail(self.method_data.ident_top_peaks).iterrows():
			# If average peak area is less then min_peak_area, skip
			if numpy.mean(areas) >= self.method_data.ident_min_peak_area:
				top_peaks_indices.append(peak_no)
		
		print(top_peaks_indices)
		
		#
		# # Limit to the largest `ident_top_peaks` peaks
		# for top_peak_idx, row in enumerate(peak_areas.iterrows()):
		# 	if top_peak_idx < self.method_data.ident_top_peaks:
		# 		# If average peak area is less then min_peak_area, skip
		# 		if numpy.mean(row[1:]) >= self.method_data.ident_min_peak_area:
		# 			top_peaks_indices.append(row[0])
				
		# Remove peaks from peaks_to_identify if they are not in
		# top_peaks_indices, i.e. they are one of the top n largest peaks
		peaks_to_identify = peaks_to_identify.filter(top_peaks_indices, axis=0)
		
		for experiment in self.experiment_objects:
			# experiment.identify_compounds2(peaks_to_identify[experiment.name])
			experiment.identify_compounds3(
					peaks_to_identify[experiment.name],
					n_hits=method_data.ident_nist_n_hits,
					)
			
		# Resave the project, including the experiment files
		self.store(resave_experiments=True)
		
		# TODO: Here's what to do:
		#  Make Experiment file mutable ONLY to remove compound identification data
		#  Add following settings to method:
		#    Identication Min Match Factor
		#    Identification Min Aligned peaks
		#         - defaults to 0 if being run on standalone experiment regardless of method setting
		#     Identification Top Peaks Num
		#         - If running on a standalone experiment, the largest n peaks in the experiment
		#         - If running on project, n largest aligned peaks, sorted by average peak area
		#            (where the average ignores experiments that don't have the peak)
		# DDF 27/Jan/2020
		
		return
		
	# Properties
	
	def _get_all_properties(self):
		"""
		Returns a list containing all of the properties, in the order they should be displayed

		:return:
		:rtype: list
		"""
		
		all_props = Base.GSMBase._get_all_properties(self)
		all_props.insert(-2, self.ammo_details)
		return all_props
	
	@property
	def ammo_file(self):
		"""
		Gets Ammunition Details from the Project tarfile and convert to BytesIO
		"""
		return BytesIO(get_file_from_archive(self.filename.value, filename_only(self.ammo_details.value)).read())
	
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
		self.ammo_file.seek(0)
		with open(output_filename, 'wb') as f:
			shutil.copyfileobj(self.ammo_file, f, length=131072)
	
	def match_counter(self, ms_comp_data):
		"""
		Counter
		Also generates final output

		:param ms_comp_data:
		:type ms_comp_data:
		"""
		
		# Initialise search engine.
		search = pyms_nist_search.Engine(
				Base.FULL_PATH_TO_MAIN_LIBRARY,
				pyms_nist_search.NISTMS_MAIN_LIB,
				Base.FULL_PATH_TO_WORK_DIR,
				# debug=True,
				)
		
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
			
			consolidated_peak = ConsolidatedPeak(rt_data, area_data, ms_data, peak_number=n)
			
			hits_data = []
			
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
								spec_loc = hit.spec_loc
								
								break
						else:
							mf_data.append(numpy.nan)
							rmf_data.append(numpy.nan)
							hit_num_data.append(numpy.nan)
				
				print(f"Obtaining reference data for {compound} (CAS {CAS})")
				ref_data = search.get_reference_data(spec_loc)
				# print(ref_data)
				hits_data.append(ConsolidatedSearchResult(
						name=compound, cas=CAS, mf_list=mf_data, rmf_list=rmf_data,
						hit_numbers=hit_num_data, reference_data=ref_data,
						))
			
			# Sort consolidated hit list
			hits_data = sorted(hits_data, key=lambda k: (len(k), k.match_factor, k.average_hit_number), reverse=True)
			consolidated_peak.hits = hits_data  # [:n_hits]
			
			consolidated_peak.ms_comparison = ms_comp_data.loc[n]
			
			self.consolidated_peaks.append(consolidated_peak)
		
		# print(len(self.consolidated_peaks))
		
		# Matches Sheet
		MatchesCSVExporter(
				self,
				os.path.join(internal_config.csv_dir, self.name + "_MATCHES.csv"),
				minutes=True,
				n_hits=n_hits,
				)
		# webbrowser.open(os.path.join(internal_config.csv_dir, self.name + "_MATCHES.csv"))
		
		literature_peak_filter = ConsolidatePeakFilter()
		literature_peak_filter.filter_by_cas = True
		
		mf500_peak_filter = ConsolidatePeakFilter()
		mf500_peak_filter.min_match_factor = 500
		
		StatisticsXLSXExporter(
				self,
				os.path.join(internal_config.csv_dir, self.name + "_STATISTICS.xlsx"),
				minutes=True,
				)

		# webbrowser.open(os.path.join(internal_config.csv_dir, self.name + "_STATISTICS.xlsx"))
		
		# with open(os.path.join(internal_config.csv_dir, "{self.name}_peak_data.json"), "w") as jsonfile:
		# 	for dictionary in peak_data:
		# 		jsonfile.write(json.dumps(dictionary))
		# 		jsonfile.write("\n")
		
		search.uninit()

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

		rows_list = []
		
		for peak_number, spectra in ms_data.iterrows():
			rows_list.append((peak_number, spectra, perms))
		
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
		
		# Convert list of (peak_number, comparisons) pairs to data frame
		column_labels = ["{} & {}".format(*perm) for perm in perms]
		comparison_dict = {}
		
		for peak_number, comparison in ms_comparison:
			comparison_dict[peak_number] = comparison
		
		comparison_df = pandas.DataFrame.from_dict(data=comparison_dict, columns=column_labels, orient="index")
		
		return comparison_df

	def consolidate(self):
		"""
		Consolidate the compound identification from the experiments into a single dataset
		"""
		ms_comparisons = self.ms_comparisons(self.ms_alignment)
		self.match_counter(ms_comparisons)
		
		chart_data = make_chart_data(self)
		
		self.consolidate_performed = True
		self.consolidate_audit_record = watchdog.AuditRecord()
		self.date_modified.value = datetime.datetime.now().timestamp()
		self.store()
	
	def spectrum_image_wrapper(self, arguments):
		return self.generate_spectrum_image(*arguments)
	
	def generate_spectrum_image(self, sample, rt_data, ms_data, path):
		"""

		:param sample:
		:type sample:
		:param rt_data:
		:type rt_data:
		:param ms_data:
		:type ms_data:
		:param path:
		:type path:

		:return:
		:rtype:
		"""
		
		# return sample
		from GSMatch.GSMatch_Core.charts import PlotSpectrum
		
		for row_idx in range(len(rt_data)):
			rt = rt_data.iloc[row_idx].loc[sample]
			ms = ms_data.iloc[row_idx].loc[sample]
			
			# TODO: Use mass range given in settings
			
			PlotSpectrum(
					numpy.column_stack((ms.mass_list, ms.mass_spec)),
					label="{} {}".format(sample, rounders(rt, "0.000")),
					xlim=(45, 500),
					mode=path
					)
	
	def generate_spectra_from_alignment(self, rt_data, ms_data):
		"""
		Mass Spectra Images

		:param rt_data:
		:type rt_data:
		:param ms_data:
		:type ms_data:

		:return:
		:rtype:
		"""
		
		path = os.path.join(internal_config.spectra_dir, self.name)
		maybe_make(path)
		
		print("\nGenerating mass spectra images. Please wait.")
		
		# Delete Existing Files
		for filename in os.listdir(path):
			os.unlink(os.path.join(path, filename))
		
		if len(rt_data) > 20:
			arguments = [(sample, rt_data, ms_data, path) for sample in rt_data.columns.values]
			with Pool(len(arguments)) as p:
				
				p.map(self.spectrum_image_wrapper, arguments)
		else:
			for sample in rt_data.columns.values:
				self.generate_spectrum_image(sample, rt_data, ms_data, path)
	
	def generate_spectra(self):
		self.generate_spectra_from_alignment(self.rt_alignment, self.ms_alignment)
		
		def generate_spectra_csv(rt_data, ms_data, name):
			# Write Mass Spectra to OpenChrom-like CSV files
			
			ms = ms_data[0]  # first mass spectrum
			
			spectrum_csv_file = os.path.join(internal_config.spectra_dir, self.name, f"{name}_data.csv")
			spectrum_csv = open(spectrum_csv_file, 'w')
			spectrum_csv.write('RT(milliseconds);RT(minutes) - NOT USED BY IMPORT;RI;')
			spectrum_csv.write(';'.join(str(mz) for mz in ms.mass_list))
			spectrum_csv.write("\n")
			
			for rt, ms in zip(rt_data, ms_data):
				spectrum_csv.write(f"{int(rt * 60000)};{rounders(rt, '0.0000000000')};0;")
				spectrum_csv.write(';'.join(str(intensity) for intensity in ms.mass_spec))
				spectrum_csv.write('\n')
			spectrum_csv.close()
		
		for prefix in internal_config.prefixList:
			print(prefix)
			# print(rt_alignment[prefix])
			# print(ms_alignment[prefix])
			generate_spectra_csv(self.rt_alignment[prefix], self.ms_alignment[prefix], prefix)


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
	
	peak_number, ms_data, perms = arguments
	
	similarity_list = []
	
	for perm in perms:
		top_ms = ms_data.loc[perm[0]]
		bottom_ms = ms_data.loc[perm[1]]
		
		if top_ms is None or bottom_ms is None:
			similarity_list.append(None)
		else:
			top_spec = numpy.column_stack((ms_data.loc[perm[0]].mass_list, ms_data.loc[perm[0]].mass_spec))
			bottom_spec = numpy.column_stack((ms_data.loc[perm[1]].mass_list, ms_data.loc[perm[1]].mass_spec))
			similarity_list.append(spectrum_similarity.SpectrumSimilarity(
					top_spec, bottom_spec, t=0.25, b=1, xlim=(45, 500),
					x_threshold=0, print_graphic=False
					)[0] * 1000)
		
	return peak_number, similarity_list


def align_in_separate_process(project):
	project.align()


def identify_in_separate_process(project):
	project.identify_compounds()
	
	
def consolidate_in_separate_process(project):
	project.consolidate()


def make_chart_data(project, peak_filter=None):
	# Initialise dictionary for chart data
	chart_data = {
			"Compound": [],
			f"{project.name} Peak Area": [],
			f"{project.name} Standard Deviation": []
			}
	
	for experiment_name in project.experiment_name_list:
		chart_data[experiment_name] = []
	
	for peak in project.consolidated_peaks:
		hit = peak.hits[0]
		
		if peak_filter:
			if len(hit) < peak_filter.min_samples or not peak_filter.check_cas_number(hit.cas):
				# Skip peak
				continue
				
		chart_data["Compound"].append(hit.name)
		for prefix, area in zip(project.experiment_name_list, peak.area_list):
			chart_data[prefix].append(area)
		chart_data[f"{project.name} Peak Area"].append(peak.area)
		chart_data[f"{project.name} Standard Deviation"].append(peak.area_stdev)
	
	chart_data = pandas.DataFrame(chart_data)
	print(chart_data)
	
	chart_data = chart_data.set_index("Compound", drop=True)

	# remove duplicate compounds:
	# chart_data_count = Counter(chart_data["Compound"])
	chart_data_count = Counter(chart_data.index)
	replacement_data = {
			"Compound": [], f"{project.name} Peak Area": [],
			f"{project.name} Standard Deviation": []
			}

	for expr_name in project.experiment_name_list:
		replacement_data[expr_name] = []

	for compound in chart_data_count:
		if chart_data_count[compound] > 1:
			replacement_data["Compound"].append(compound)
			replacement_data[f"{project.name} Peak Area"].append(
					sum(chart_data.loc[compound, f"{project.name} Peak Area"]))

			peak_data = []
			for expr_name in project.experiment_name_list:
				replacement_data[expr_name].append(sum(chart_data.loc[compound, expr_name]))
				peak_data.append(sum(chart_data.loc[compound, expr_name]))

			replacement_data[f"{project.name} Standard Deviation"].append(numpy.std(peak_data))

			chart_data = chart_data.drop(compound, axis=0)

	replacement_data = pandas.DataFrame(replacement_data)
	replacement_data = replacement_data.set_index("Compound", drop=False)
	chart_data = chart_data.append(replacement_data, sort=False)
	chart_data.sort_index(inplace=True)
	chart_data = chart_data.drop("Compound", axis=1)
	chart_data['Compound Names'] = chart_data.index

	save_chart_data(chart_data, os.path.join(internal_config.csv_dir, "{}_CHART_DATA.csv".format(project.name)))
	
	return chart_data


def save_chart_data(chart_data, filename):
	chart_data.to_csv(filename, sep=";")
	
	
def load_chart_data(filename):
	return pandas.read_csv(filename, sep=";", index_col=0)
