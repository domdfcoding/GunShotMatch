#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  filename.py
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2020  Dominic Davis-Foster <dominic@davis-foster.co.uk>
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

# 3rd party
from reportlab.lib.units import cm
from reportlab.platypus import Spacer

# This package
from GuiV2.GSMatch2_Core.exporters import PDFExporterBase


class PDFExporter(PDFExporterBase):
	no_input_filename_str = "&lt;Unsaved Method File&gt;"
	no_input_full_filename_str = "an unsaved method file"

	def __init__(self, method, input_filename, output_filename, title):
		PDFExporterBase.__init__(self, method, input_filename, output_filename, title)
		
		self.method = method
		self.make_method_inner()
		self.build()
	
	def make_method_inner(self):
		# Extract parameters from the method
		
		if self.method.tophat_unit == "m":
			tophat_unit = "minutes"
		elif self.method.tophat_unit == "s":
			tophat_unit = "seconds"
		elif self.method.tophat_unit == "ms":
			tophat_unit = "milliseconds"
		
		expr_creation_data = [
				["Mass Range", f"{self.method.mass_range}", "<i>m/z</i>"],
				["Perform Savitsky-Golay smoothing", self.method.enable_sav_gol, ""],
				["Perform Tophat baseline correction", self.method.enable_tophat, ""],
				["Tophat structural element", self.method.tophat, tophat_unit],
				["<b>Biller-Biemann Peak Detection</b>", "", ""],
				["&nbsp;&nbsp;Number of Points", self.method.bb_points, ''],
				["&nbsp;&nbsp;Number of Scans", self.method.bb_scans, ''],
				["&nbsp;&nbsp;Time Range", self.method.target_range, "minutes"],
				["Perform Noise Filtering", self.method.enable_noise_filter, ""],
				["Noise Filtering Threshold", self.method.noise_thresh, "ions"],
				["Exclude peaks with theee base ions", self.method.base_peak_filter, "<i>m/z</i>"],
				]
		
		peak_alignment_data = [
				["Retention Time Modulation", self.method.rt_modulation, "seconds"],
				["Gap Penalty", self.method.gap_penalty, ""],
				["Minimum Peaks", self.method.min_peaks, ""],
				]
		
		ident_data = [
				["Minimum Aligned Peaks", self.method.ident_min_aligned_peaks, ""],
				["Top Peaks", self.method.ident_top_peaks, ""],
				["Number of `Hits`", self.method.ident_nist_n_hits, ""],
				["Minimum Peak Area", self.method.ident_min_peak_area, ""],
				["Minimum Match Factor", self.method.ident_min_match_factor, ""],
				]
		
		project_comprison_data = [
				["<b>Peak Alignment</b>", "", ""],
				["&nbsp;&nbsp;Retention Time Modulation", self.method.comparison_rt_modulation, "seconds"],
				["&nbsp;&nbsp;Gap Penalty", self.method.comparison_gap_penalty, ""],
				["&nbsp;&nbsp;Minimum Peaks", self.method.comparison_min_peaks, ""],
				["Significance Level", self.method.comparison_a, ""],
				]
		
		self.elements.append(self.make_parameter_table("Experiment Creation", expr_creation_data))
		self.elements.append(Spacer(1, cm))
		self.elements.append(self.make_parameter_table("Peak Alignment", peak_alignment_data))
		self.elements.append(Spacer(1, cm))
		self.elements.append(self.make_parameter_table("Compound Identification", ident_data))
		self.elements.append(Spacer(1, cm))
		self.elements.append(self.make_parameter_table("Project Comparison", project_comprison_data))
		self.elements.append(Spacer(1, cm))
