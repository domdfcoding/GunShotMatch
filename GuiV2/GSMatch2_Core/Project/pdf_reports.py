#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  pdf_reports.py
#
#  This file is part of GunShotMatch
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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

# 3rd party
from reportlab.lib.units import cm
from reportlab.platypus import NextPageTemplate, PageBreak, Spacer

# this package
from GuiV2.GSMatch2_Core.Ammunition import AmmoPDFExporter
from GuiV2.GSMatch2_Core.exporters import PDFExporterBase
from GuiV2.GSMatch2_Core.Method import MethodPDFExporter
from GuiV2.GSMatch2_Core.Project import AlignmentPDFExporter, ConsolidatePDFExporter, InfoPDFExporter


class ProjectReportPDFExporter(InfoPDFExporter, MethodPDFExporter, AmmoPDFExporter, AlignmentPDFExporter, ConsolidatePDFExporter):
	def __init__(self, project_panel, output_filename, title="Project Report"):
		
		self.overall_title = title
		
		self.project = project_panel.project
		
		PDFExporterBase.__init__(self, self.project.filename.value, output_filename, title)
		
		# TODO: Contents page
		self.elements.append(PageBreak())

		self.elements.append(self.make_report_header("Project Information", self.filename))
		self.elements.append(Spacer(1, cm))
		self.make_project_info_inner()
		
		self.elements.append(self.make_report_header("Method Report", self.project.method.value))
		self.elements.append(Spacer(1, cm))
		self.method = self.project.method_data
		self.make_method_inner()
		self.elements.append(PageBreak())
		
		self.elements.append(self.make_report_header("Ammunition Details Report", self.project.ammo_details.value))
		self.elements.append(Spacer(1, cm))
		self.ammo_details = self.project.ammo_data
		self.make_ammo_details_inner()
		self.elements.append(PageBreak())
		
		# for experiment in self.project.experiment_objects:
		# TODO: Experiment Report for each experiment
		
		if self.project.alignment_performed:
			self.elements.append(self.make_report_header("Alignment Report", self.filename))
			self.elements.append(Spacer(1, cm))
			self.alignment_panel = project_panel.alignment_page
			self.make_alignment_inner()
			self.elements.append(PageBreak())

		if self.project.consolidate_performed:
			# TODO: Wrong width
			self.elements.append(self.make_report_header("Consolidated Peaks", self.filename))
			self.consolidate_panel = project_panel.compounds_tab.consolidate_panel
			self.elements.append(NextPageTemplate("landscape"))
			self.elements.append(PageBreak())
			self.elements.append(NextPageTemplate("landscape"))
			self.make_consolidate_inner()
		
		self.build()


if __name__ == '__main__':
	print(ProjectReportPDFExporter.no_input_full_filename_str)
