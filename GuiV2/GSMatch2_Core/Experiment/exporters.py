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
import math

# 3rd party
from mathematical.utils import rounders
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, Spacer, Table, TableStyle

# This package
from GuiV2.GSMatch2_Core.exporters import inner_width, PDFExporterBase, styles

font_size = 9


class PeakListPDFExporter(PDFExporterBase):
	def __init__(self, experiment, input_filename, output_filename):
		PDFExporterBase.__init__(self, experiment, input_filename, output_filename, f"Peak List - {experiment.name}")
		
		self.experiment = experiment
		self.make_expr_peak_list_inner()
		self.build()
	
	def make_expr_peak_list_inner(self):
		self.elements[-1] = Spacer(1, cm/2)
		self.elements.append(Paragraph("<font size=9>Note: retention times are given in minutes.</font>", styles["Normal"]))
		self.elements.append(Spacer(1, cm / 3))
		
		first_page_peaks = 30
		subsequent_page_peaks = first_page_peaks + 7
		
		category_style = TableStyle([
				('FONTSIZE', (0, 0), (-1, -1), font_size),
				('ALIGN', (0, 0), (0, -1), 'LEFT'),
				('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
				('VALIGN', (0, 0), (-1, -1), 'TOP'),
				("LINEBELOW", (0, 1), (-1, -1), 0.5, colors.lightgrey),
				("LINEBELOW", (0, 0), (-1, 0), 1, colors.black),
				("LINEAFTER", (2, 0), (2, -1), 1, colors.black),
				# ("LINEAFTER", (0, 0), (-2, -1), 1, colors.black),
				])
		
		header_row = [
						Paragraph("UID", styles["Normal"]),
						Paragraph("RT", styles["Right"]),
						Paragraph("Area", styles["Right"]),
						] * 2
		# TODO: Option to respect filter options?
		chunks = [self.experiment.peak_list_data[:first_page_peaks * 2]]
		chunks += list(divide_chunks(self.experiment.peak_list_data[first_page_peaks * 2:], subsequent_page_peaks * 2))
		
		col_widths = [inner_width * (4.25 / 20), inner_width * (1.8 / 20), inner_width * (3.95 / 20)] * 2
		
		for chunk in chunks:
			rows = [header_row]
			chunk_size = math.ceil(len(chunk) / 2)
			for i in range(chunk_size):
				peak_a = chunk[i]
				cols = parse_peak(peak_a)
				
				if i + chunk_size < len(chunk):
					peak_b = chunk[i + chunk_size]
					cols += parse_peak(peak_b)
				
				rows.append(cols)
			
			self.elements.append(Table(
					rows,
					colWidths=col_widths,
					rowHeights=[None] * len(rows),
					style=category_style,
					hAlign="LEFT",
					repeatRows=1
					))
			
			self.elements.append(PageBreak())


def parse_peak(peak):
	return [
			Paragraph(peak.UID, styles["Normal"]),
			Paragraph(f"{rounders(peak.rt / 60, '0.000')}", styles["Right"]),
			Paragraph(f"{rounders(peak.area, '0.000'):,}", styles["Right"]),
			]


# Yield successive n-sized chunks from l.
# https://www.geeksforgeeks.org/break-list-chunks-size-n-python/
def divide_chunks(l, n):
	# looping till length l
	for i in range(0, len(l), n):
		yield l[i:i + n]


class CompoundsPDFExporter(PDFExporterBase):
	def __init__(self, experiment, input_filename, output_filename):
		PDFExporterBase.__init__(self, experiment, input_filename, output_filename, f"Identified Compounds - {experiment.name}")
		
		self.experiment = experiment
		self.make_expr_compounds_inner()
		self.build()
	
	def make_expr_compounds_inner(self):
		
		for peak in self.experiment.ident_peaks:
			# TODO: Option to respect filter options?
			#  Perhaps a dialog after choosing the filename? Or before?
			#  With options for all peaks, use current display, or custom, which has options from filter dialog?
			self.add_peak_compound(peak)

	def add_peak_compound(self, peak, show_peak_number=True):
		col_widths = [
				inner_width * (2.2 / 20),
				inner_width * (10.6 / 20),
				inner_width * (3 / 20),
				inner_width * (2 / 20),
				inner_width * (2.2 / 20),
				]
		
		hits_style = TableStyle([
				('FONTSIZE', (0, 0), (-1, -1), font_size),
				('ALIGN', (0, 0), (0, -1), 'LEFT'),
				('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
				('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
				("LINEAFTER", (0, 0), (-2, -1), 0.5, colors.lightgrey),
				("LINEBELOW", (0, 0), (-1, 1), 1, colors.black),
				("LINEABOVE", (0, 0), (-1, 0), 1, colors.black),
				("LINEBELOW", (0, 2), (-1, -1), 0.5, colors.lightgrey),
				("SPAN", (0, 0), (1, 0)),
				("SPAN", (2, 0), (4, 0)),
				])
		
		rt_string = str(rounders(peak.rt / 60, '0.000000')).rjust(15).replace(' ', '&nbsp;')
		area_string = f"{rounders(peak.area, '0.000000'):,}".rjust(25).replace(' ', '&nbsp;')
		peak_no_string = str(peak.peak_number).rjust(4).replace(' ', '&nbsp;')
		
		if show_peak_number:
			rt_paragraph = Paragraph(f"Retention Time: {rt_string} minutes{'&nbsp;'*8}Peak Number: {peak_no_string}", styles["Normal"])
		else:
			rt_paragraph = Paragraph(f"Retention Time: {rt_string} minutes", styles["Normal"])
		
		rows = [
				[
						rt_paragraph, '',
						Paragraph(f"Peak Area: {area_string}", styles["Normal"]),
						'', '',
						],
				[
						Paragraph("Hit Num.", styles["Normal"]),
						Paragraph("Name", styles["Normal"]),
						Paragraph("CAS", styles["Right"]),
						Paragraph("Match", styles["Right"]),
						Paragraph("R Match", styles["Right"]),
						]
				]
		
		hit_list = list(enumerate(peak.hits))
		
		for hit_number, hit in hit_list:
			rows.append([
					Paragraph(f'{hit_number + 1}', styles["Right"]),
					Paragraph(f"{hit.name}", styles["Normal"]),
					Paragraph(f"{hit.cas}", styles["Right"]),
					Paragraph(f"{hit.match_factor}", styles["Right"]),
					Paragraph(f"{hit.reverse_match_factor}", styles["Right"]),
					])
		
		self.elements.append(Table(
				rows,
				colWidths=col_widths,
				rowHeights=[None] * len(rows),
				style=hits_style,
				hAlign="LEFT",
				repeatRows=2
				))
		
		self.elements.append(Spacer(1, cm/2))


class SinglePeakCompoundsPDFExporter(CompoundsPDFExporter):
	def __init__(self, peak_number, peak_list, expr_names, input_filename, output_filename):
		PDFExporterBase.__init__(self, 0, input_filename, output_filename, f"Identified Compounds - Peak Number {peak_number}")
		
		self.peak_number = peak_number
		self.peak_list = peak_list
		self.expr_names = expr_names
		self.make_expr_compounds_inner()
		self.build()
	
	def make_expr_compounds_inner(self):
		
		for peak, experiment_name in zip(self.peak_list, self.expr_names):
			# TODO: Option to respect filter options?
			#  Perhaps a dialog after choosing the filename? Or before?
			#  With options for all peaks, use current display, or custom, which has options from filter dialog?
			self.elements.append(Paragraph(f"<font size=9>{experiment_name}</font>", styles["Normal"]))
			self.add_peak_compound(peak, False)
