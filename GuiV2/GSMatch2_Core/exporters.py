#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  exporters.py
"""
Classes and functions for generating and exporting reports
"""
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
import datetime
import getpass
import socket
import textwrap
import pathlib

# 3rd party
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, _baseFontName
from reportlab.lib.units import cm, inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from importlib_resources import path

# This package
import GuiV2.icons._256

# Constants across all reports
width, height = A4

rightMargin = 62
leftMargin = 50
topMargin = 50
bottomMargin = 90

inner_width = width - leftMargin - rightMargin
inner_height = height - topMargin - bottomMargin

# Setup styles
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
styles.add(ParagraphStyle(name="Center", alignment=TA_CENTER))
styles.add(ParagraphStyle(name="Right", alignment=TA_RIGHT))
styles.add(ParagraphStyle(name="NoWrap", wordWrap=None))


def make_report_header(title, filename):
	"""
	Create report header, containing the title of the report,

	:param title: The title of the report
	:type title: str
	:param filename: The name of the file the report was generated from, without the directory structure
	:type filename: str

	:return:
	:rtype:
	"""
	
	header = Paragraph(
			f"<font size='16'>{title}</font>",
			style=styles["Normal"]
			)
	
	header_text_style = TableStyle([
			('ALIGN', (0, 0), (-1, -1), 'LEFT'),
			('VALIGN', (0, 0), (-1, -1), 'CENTER'),
			])
	
	header_style = TableStyle([
			('ALIGN', (0, 0), (0, 0), 'LEFT'),
			('ALIGN', (-1, -1), (-1, -1), 'RIGHT'),
			('VALIGN', (0, 0), (-1, -1), 'CENTER'),
			("LINEBELOW", (0, 0), (-1, -1), 1, colors.black),
			("LINEABOVE", (0, 0), (-1, -1), 1, colors.black),
			])
	
	l_text_table = Table([
			[header],
			[Paragraph(
					f"<font size='12'>{filename}</font>",
					style=styles["Normal"]
					)],
			],
			colWidths=[inner_width - inch],
			rowHeights=[cm, cm],
			style=header_text_style,
			hAlign="LEFT",
			)
	
	with path(GuiV2.icons._256, "logo-v2.png") as logo_path:
		im = Image(str(logo_path), inch, inch)
	
	return Table(
			[[l_text_table, im], ],
			colWidths=[inner_width - inch, inch],
			rowHeights=[3 * cm],
			style=header_style,
			hAlign="LEFT",
			)


class FooterCanvas(canvas.Canvas):
	
	def __init__(self, *args, **kwargs):
		canvas.Canvas.__init__(self, *args, **kwargs)
		self.pages = []
		self.footer_height = 50
	
	def showPage(self):
		self.pages.append(dict(self.__dict__))
		self._startPage()
	
	def save(self):
		page_count = len(self.pages)
		for page in self.pages:
			self.__dict__.update(page)
			self.draw_canvas(page_count)
			canvas.Canvas.showPage(self)
		canvas.Canvas.save(self)
	
	def draw_canvas(self, page_count):
		self.saveState()
		
		# self.setStrokeColorRGB(0, 0, 0)
		# self.setLineWidth(0.5)
		self.setFont('Times-Roman', 10)
		
		self.drawString(A4[0] - 128, self.footer_height, f"Page {self._pageNumber} of {page_count}")
		
		self.restoreState()


class PDFExporterBase:
	no_input_filename_str = "&lt;Unsaved File&gt;"
	no_input_full_filename_str = "an unsaved file"
	
	def __init__(self, _, input_filename, output_filename, title):
		self.doc = SimpleDocTemplate(
				output_filename,
				pagesize=A4,
				rightMargin=rightMargin,
				leftMargin=leftMargin,
				topMargin=topMargin,
				bottomMargin=bottomMargin
				)
		
		self.elements = []
		
		# Table for image and text at the top
		if input_filename is None:
			self.filename = self.no_input_filename_str
			self.full_filename = "an unsaved method file"
		else:
			self.filename = pathlib.Path(input_filename).name
			self.full_filename = input_filename
		
		self.title = title
		
		self.elements.append(make_report_header(title, self.filename))
		
		self.elements.append(Spacer(1, cm))

	def build(self):
		self.doc.multiBuild(
				self.elements,
				canvasmaker=FooterCanvas,
				onFirstPage=self.onFirstPage,
				onLaterPages=self.onLaterPages
				)
	
	def make_parameter_table(self, label, data, show_unit=True, col_widths=None):
		"""

		:param label:
		:type label:
		:param data:
		:type data:
		:return:
		:rtype:
		"""
		
		font_size = 9
		row_height = font_size * 2
		
		category_style = TableStyle([
				('ALIGN', (0, 0), (-1, -1), 'LEFT'),
				('VALIGN', (0, 0), (-1, -1), 'TOP'),
				("LINEBELOW", (0, 0), (3, 1), 1, colors.black),
				])
		
		top_row = [Paragraph(f"<font size='11'><b>{label}</b></font>", styles["Normal"])]
		header_row = [
				Paragraph(f"<font size='{font_size}'>Parameter</font>", styles["Normal"]),
				Paragraph(f"<font size='{font_size}'>Value</font>", styles["Normal"]),
				]
		if show_unit:
			header_row.append(
					Paragraph(
							f"<font size='{font_size}'>Unit </font><font size='9'>(if applicable)</font>",
							styles["Normal"]
							))
		
		rows = [top_row, header_row]
		for param in data:
			rows.append([
					Paragraph(f"<font size='{font_size}'>{convert_newlines(param[0])}</font>", styles["Normal"]),
					Paragraph(f"<font size='{font_size}'>{convert_newlines(param[1])}</font>", styles["Normal"]),
					])
			
			if show_unit:
				rows[-1].append(Paragraph(f"<font size='{font_size}'>{convert_newlines(param[2])}</font>", styles["Normal"]))
		
		if show_unit:
			if col_widths:
				col_widths = col_widths[:3]
			else:
				col_widths = [inner_width * (3.5 / 7), inner_width * (1.5 / 7), inner_width * (2 / 7)]
		else:
			if col_widths:
				col_widths = col_widths[:2]
			else:
				col_widths = [inner_width * (3 / 7), inner_width * (4 / 7)]
		
		return Table(
				rows,
				colWidths=col_widths,
				# rowHeights=[0.8 * cm] + ([row_height] * (len(rows) - 1)),
				rowHeights=[0.8 * cm] + ([None] * (len(rows) - 1)),
				style=category_style,
				hAlign="LEFT",
				repeatRows=2
				)
	
	def draw_footer(self, canvas, doc):
		
		canvas.setStrokeColorRGB(0, 0, 0)
		canvas.setLineWidth(0.5)
		canvas.setFont('Times-Roman', 10)
		
		username = getpass.getuser()
		device = socket.gethostname()
		creation_time = datetime.datetime.now().strftime("%H:%M:%S %d/%m/%Y")
		
		footer_string = f"Generated from {self.full_filename} by {username}@{device} on {creation_time}"
		split_len = 100
		
		generated_by_height = canvas.footer_height + (cm * 0.5)
		
		if len(footer_string) > split_len:
			wrap_text = textwrap.wrap(footer_string, width=split_len)[::-1]
			for idx, line in enumerate(wrap_text):
				canvas.drawString(leftMargin, generated_by_height + (idx * 0.5 * cm), line)
			canvas.line(
					x1=leftMargin,
					y1=generated_by_height + (len(wrap_text) * 0.5 * cm),
					x2=A4[0] - 50,
					y2=generated_by_height + (len(wrap_text) * 0.5 * cm)
					)
		
		else:
			canvas.drawString(leftMargin, generated_by_height, footer_string)
	
	def onFirstPage(self, canvas, doc):
		
		canvas.saveState()
		
		self.draw_footer(canvas, doc)
		
		canvas.restoreState()
	
	def draw_later_header(self, canvas, doc):
		header_string = f"{self.title} - {self.filename}".replace("&lt;", "<").replace("&gt;", ">")
		
		canvas.setStrokeColorRGB(0, 0, 0)
		canvas.setLineWidth(0.5)
		canvas.setFont(_baseFontName, 10)
		
		canvas.drawString(leftMargin + 5, bottomMargin + inner_height + 5, header_string)
	
	def onLaterPages(self, canvas, doc):
		
		canvas.saveState()
		
		self.draw_footer(canvas, doc)
		self.draw_later_header(canvas, doc)
		
		canvas.restoreState()


def convert_newlines(line):
	return str(line).replace("\\n", "<br/>")
