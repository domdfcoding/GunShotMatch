#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  exporters.py
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import datetime
from collections import Counter
from numbers import Number

# 3rd party
from mathematical.utils import rounders
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, Spacer, Table, TableStyle

# This package
from GuiV2.GSMatch2_Core.exporters import inner_width, PDFExporterBase, styles

font_size = 9


class InfoPDFExporter(PDFExporterBase):
	no_input_filename_str = "&lt;Unsaved Project&gt;"
	no_input_full_filename_str = "an unsaved Project"

	def __init__(self, project, input_filename, output_filename, title):
		PDFExporterBase.__init__(self, project, input_filename, output_filename, title)
		
		self.project = project
		self.make_project_inner()
		self.build()
	
	def make_project_inner(self):
		project_info_col_widths = [inner_width * (2.5 / 7), inner_width * (4.5 / 7)]
		
		project_info = [["Name", self.project.name]]
		for prop in self.project.all_properties:
			if prop.type == datetime:
				value = prop.format_time()
			else:
				value = prop.value
			
			project_info.append([prop.label, value])
		
		self.elements.append(
			self.make_parameter_table("Project Information", project_info, False, project_info_col_widths))
		self.elements.append(PageBreak())
		
		# Experiments
		for experiment in self.project.experiment_objects:
			expr_info = []
			
			for prop in experiment.all_properties:
				expr_info.append([prop.label, prop.value])
			self.elements.append(
					self.make_parameter_table(f"Experiment: {experiment.name}", expr_info, False))
			self.elements.append(PageBreak())


class AlignmentPDFExporter(PDFExporterBase):
	def __init__(self, parent, input_filename, output_filename):
		# Parent: class:AlignmentDataPanel
		PDFExporterBase.__init__(self, parent, input_filename, output_filename, "Alignment Report")
		
		self.parent = parent
		self.make_alignment_inner()
		self.build()
	
	def make_alignment_inner(self):
		self.elements.append(self.make_alignment_filter_table())
		self.elements.append(Spacer(1, cm/2))
		self.elements.append(self.make_alignment_table())
		
		
	def make_alignment_table(self):
		
		alignment_table_style = TableStyle([
				('FONTSIZE', (0, 0), (-1, -1), font_size),
				("SPAN", (1, 0), (-1, 0)),
				('ALIGN', (1, 0), (-1, 0), 'CENTER'),
				('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
				('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
				("LINEBELOW", (0, 0), (-1, 1), 1, colors.black),
				("LINEBELOW", (0, 2), (-1, -1), 0.5, colors.lightgrey),
				])
		
		top_row = ['', Paragraph("Retention Time (minutes)", styles["Center"])]
		header_row = [Paragraph("Peak No.", styles["Normal"])]
		rows = [top_row, header_row]
		
		for experiment in self.parent.project.experiment_name_list:
			header_row.append(Paragraph(experiment, styles["Right"]))
		
		for peak in self.parent.project.rt_alignment.itertuples():
			row_data = []
			
			for experiment in peak:
				rt = rounders(experiment, "0.00000")
				if rt.is_nan():
					rt = "-"
				row_data.append(rt)
			
			row_data[0] = peak.Index
			if self.parent.n_experiments - Counter(row_data)["-"] >= self.parent.filter_min_experiments:
				for experiment in row_data[1:]:
					if experiment != "-":
						if self.parent.filter_min_rt <= experiment <= self.parent.filter_max_rt:
							rows.append([Paragraph(str(x), styles["Right"]) for x in row_data])
							break  # As long as one of the peaks is in range, add the peak
		
		peak_no_prop = 1.5
		expr_prop = 2
		base_total = peak_no_prop + expr_prop*len(self.parent.project.experiment_name_list)
		peak_no_width = inner_width * (peak_no_prop / base_total)
		expr_width = inner_width * (expr_prop / base_total)
		
		col_widths = [peak_no_width] + [expr_width]*len(self.parent.project.experiment_name_list)
		
		return Table(
				rows,
				colWidths=col_widths,
				rowHeights=[None] * len(rows),
				style=alignment_table_style,
				hAlign="LEFT",
				repeatRows=2
				)
				
	def make_alignment_filter_table(self):
		if self.parent.filter_is_default():
			return Paragraph("<font size=12>This report was produced with all peaks shown.</font>", styles["Normal"])
		
		else:
			filter_table_style = TableStyle([
					('FONTSIZE', (0, 0), (-1, 0), 12),
					('FONTSIZE', (0, 1), (-1, -1), font_size),
					("SPAN", (0, 0), (-1, 0)),
					('ALIGN', (1, 0), (-1, 0), 'CENTER'),
					('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
					('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
					("LINEBELOW", (0, 0), (-1, 0), 1, colors.black),
					("LINEBELOW", (0, 1), (-1, -1), 0.5, colors.lightgrey),
					])
			
			return Table(
					[
							[
									Paragraph(
										"This report was produced with the following settings applied:",
										styles["Normal"]),
									'',
									],
							[
									Paragraph("Minimum Experiments:", styles["Normal"]),
									Paragraph(f"{self.parent.filter_min_experiments}", styles["Normal"]),
									],
							[
									Paragraph("Retention Time Range:", styles["Normal"]),
									Paragraph(
											f"{self.parent.filter_min_rt} - {self.parent.filter_max_rt} minutes",
											styles["Normal"]),
									],
							],
					colWidths=[5 * cm, 7 * cm],
					rowHeights=[None, None, None],
					style=filter_table_style,
					hAlign="LEFT",
					)


class MatchesCSVExporter:
	def __init__(self, project, output_filename, minutes=True, n_hits=5):
		"""
		
		:param project:
		:type project:
		:param output_filename:
		:type output_filename:
		:param minutes: Whether the retention times should be given in minutes. Default True
		:type minutes: bool, optional
		:param n_hits: The number of hits to report for each peak. Default 5
		:type n_hits: int, optional
		"""
		
		self.minutes = minutes
		
		# Matches Sheet
		with open(output_filename, "w") as matches_csv_output:
			# Write the names of the project and the experiments
			matches_csv_output.write(f"{project.name};;;")
			
			for experiment_name in project.experiment_name_list:
				matches_csv_output.write(f"{experiment_name};;;")
			matches_csv_output.write("\n")
			
			# Number of experiments
			n_expr = len(project.experiment_name_list)
			
			# Write the column headers
			matches_csv_output.write(
					"Retention Time;Peak Area;;" +
					"Page;RT;Area;" * n_expr +
					";Match Factor;;;;Reverse Match Factor;;;;Hit Number;;;;Retention Time;;;;Peak Area;;\n")
			matches_csv_output.write(
					"Name;CAS Number;Freq.;" +
					"Hit No.;Match;R Match;" * n_expr +
					";Mean;STDEV;%RSD;;Mean;STDEV;%RSD;;Mean;STDEV;%RSD;;Mean;STDEV;%RSD;;Mean;STDEV;%RSD\n")
			
			for peak in project.consolidated_peaks:
				matches_csv_output.write(f"{self.convert_rt(peak.rt)};{peak.area};;")
				matches_csv_output.write(";".join(
								[str(val) for pair in zip(
										[''] * n_expr, self.convert_rt(peak.rt_list), peak.area_list
										) for val in pair]))
				matches_csv_output.write(";"*14)
				matches_csv_output.write(f"{self.convert_rt(peak.rt)};{self.convert_rt(peak.rt_stdev)};{peak.rt_stdev / peak.rt};;")
				matches_csv_output.write(f"{peak.area};{peak.area_stdev};{peak.area_stdev / peak.area};;\n")

				for hit in peak.hits[:n_hits]:
					matches_csv_output.write(f"{hit.name};{hit.cas};{len(hit)};")
					matches_csv_output.write(";".join(
									[str(val) for pair in zip(
											hit.hit_numbers, hit.mf_list, hit.rmf_list
											) for val in pair]))
					matches_csv_output.write(f";;{hit.match_factor};{hit.match_factor_stdev};")
					matches_csv_output.write(f"{hit.match_factor_stdev / hit.match_factor};")
					matches_csv_output.write(f";;{hit.reverse_match_factor};{hit.reverse_match_factor_stdev};")
					matches_csv_output.write(f"{hit.reverse_match_factor_stdev / hit.reverse_match_factor};")
					matches_csv_output.write(f";{hit.average_hit_number};{hit.hit_number_stdev};")
					matches_csv_output.write(f"{hit.hit_number_stdev / hit.average_hit_number};\n")
	
	def convert_rt(self, rt):
		"""
		Converts the retention time to minutes if applicable
		
		:param rt:
		:type rt:
		"""
		
		if not self.minutes:
			if isinstance(rt, (list, tuple)):
				return [seconds / 60 for seconds in rt]
			elif isinstance(rt, Number):
				return rt / 60
		else:
			return rt

class StatisticsCSVExporter:
	def __init__(self, project, output_basename, minutes=True, n_hits=5):
		"""Get list of CAS Numbers for compounds reported in literature"""
		with open("./lib/CAS.txt", "r") as f:
			CAS_list = f.readlines()
		for index, CAS in enumerate(CAS_list):
			CAS_list[index] = CAS.rstrip("\r\n")
		
		# Statistics Sheet
		statistics_full_output = open(f"{output_basename} FULL.csv", "w")
		statistics_output = open(f"{output_basename}.csv", "w")
		statistics_lit_output = open(f"{output_basename} LIT.csv", "w")
		
		statistics_header = ";".join([
											project.name, '', '', '',
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
				"{} Peak Area".format(project.name): [],
				"{} Standard Deviation".format(project.name): []
				}
		
		for experiment_name in project.experiment_name_list:
			chart_data[experiment_name] = []
		
		for peak, ms in zip(peak_data, ms_comp_list):
			peak["ms_comparison"] = ms
			
			write_peak(statistics_full_output, peak, ms)
			if peak["hits"][0]["Count"] > (
					len(self.experiment_name_list) / 2):  # Write to Statistics; TODO: also need similarity > 800
				write_peak(statistics_output, peak, ms)
				if peak["hits"][0]["CAS"].replace("-", "") in CAS_list:  # Write to Statistics_Lit
					write_peak(statistics_lit_output, peak, ms)
					# Create Chart Data
					chart_data["Compound"].append(peak["hits"][0]["Name"])
					for prefix, area in zip(self.config.prefixList, peak["area_data"]):
						chart_data[prefix].append(area)
					chart_data["{} Peak Area".format(project.name)].append(numpy.mean(peak["area_data"]))
					chart_data["{} Standard Deviation".format(project.name)].append(numpy.mean(peak["area_data"]))
		
		statistics_full_output.close()
		statistics_output.close()
		statistics_lit_output.close()
