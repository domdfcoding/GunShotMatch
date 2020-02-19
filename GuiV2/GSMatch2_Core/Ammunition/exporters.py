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
import datetime
import statistics

# 3rd party
from mathematical.utils import rounders
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, Spacer, Table, TableStyle

# This package
from GuiV2.GSMatch2_Core.exporters import inner_width, PDFExporterBase, styles
from GuiV2.GSMatch2_Core.InfoProperties import Measurement

font_size = 9


class PDFExporter(PDFExporterBase):
	no_input_filename_str = "&lt;Unsaved Ammunition Details File&gt;"
	no_input_full_filename_str = "an unsaved ammunition details file"

	def __init__(self, ammo_details, input_filename, output_filename, title):
		PDFExporterBase.__init__(self, ammo_details, input_filename, output_filename, title)
		
		self.ammo_details = ammo_details
		
		self.make_ammo_details_inner()
		
		self.build()
	
	def make_ammo_details_table(self, properties, title, starter=None):
		col_widths = [inner_width * (2.5 / 7), inner_width * (4.5 / 7)]
		
		if starter:
			table = starter
		else:
			table = []
			
		for prop in properties:
			if isinstance(prop.type, Measurement):
				val = get_measurement_statistics(prop.value)
			elif prop.type == datetime:
				val = prop.format_time()
			else:
				val = prop.value
			table.append([prop.label, val])
		self.elements.append(
				self.make_parameter_table(title, table, False, col_widths))
		
		self.elements.append(Spacer(1, cm))
	
	def make_ammo_details_inner(self):
		self.make_ammo_details_table(
				self.ammo_details.ammunition_properties,
				"Ammunition Information",
				[["Name", self.ammo_details.name]]
				)
		
		self.make_ammo_details_table(self.ammo_details.projectile.all_properties, "Projectile Information")
		self.make_ammo_details_table(self.ammo_details.propellant_granules.all_properties, "Propellant Information")
		self.make_ammo_details_table(self.ammo_details.file_properties, "File Information")
		
		self.elements.append(self.make_ammo_images_table())
		
		other_images = self.ammo_details.other_images * 3
		chunks = list(divide_chunks(other_images, 5))
		
		for chunk in chunks:
			self.elements.append(self.make_other_images_table(chunk, row_length=5))
		
		self.elements.append(Spacer(1, cm))
	
	def make_ammo_images_table(self):
		
		category_style = TableStyle([
				('ALIGN', (0, 0), (0, 0), 'LEFT'),
				('ALIGN', (0, 1), (-1, -1), 'CENTER'),
				('VALIGN', (0, 0), (-1, -1), 'TOP'),
				("LINEBELOW", (0, 0), (3, 1), 1, colors.black),
				])
		
		top_row = [Paragraph(f"<font size='11'><b>Images</b></font>", styles["Normal"])]
		header_row = [
				Paragraph(f"<font size='{font_size}'>Propellant</font>", styles["Center"]),
				Paragraph(f"<font size='{font_size}'>Headstamp</font>", styles["Center"]),
				]
		
		images_row = []
		
		for image in [self.ammo_details.propellant_image, self.ammo_details.headstamp_image]:
			if image:
				images_row.append(Image(*convert_image(image, inner_width / 2.1)))
			else:
				images_row.append(Paragraph('', styles["Normal"]))

		col_widths = [inner_width / 2, inner_width / 2]
		
		return Table(
				[top_row, header_row, images_row],
				colWidths=col_widths,
				rowHeights=[0.8 * cm, None, None],
				style=category_style,
				hAlign="LEFT",
				repeatRows=2
				)
	
	@staticmethod
	def make_other_images_table(image_list, row_length=5):
		
		category_style = TableStyle([
				('ALIGN', (0, 0), (-1, -1), 'CENTER'),
				('VALIGN', (0, 0), (-1, -1), 'TOP'),
				("LINEBELOW", (0, 0), (3, 0), 1, colors.black),
				("LINEABOVE", (0, 0), (3, 0), 1, colors.black),
				])
		
		col_widths = [inner_width / row_length]*row_length
	
		captions_row = []
		images_row = []
		
		for caption, image in image_list:
			captions_row.append(Paragraph(f"<font size='{font_size}'>{caption}</font>", styles["Center"]))
			images_row.append(Image(*convert_image(image, col_widths[0])))

		while len(captions_row) % row_length != 0:
			captions_row.append(Paragraph('', styles["Normal"]))
			images_row.append(Paragraph('', styles["Normal"]))
		
		return Table(
				[captions_row, images_row],
				colWidths=col_widths,
				rowHeights=[None, None],
				style=category_style,
				hAlign="LEFT",
				repeatRows=2
				)


def convert_image(original_image, max_width, max_height=None):
	if max_height is None:
		max_height = max_width
	import io
	
	img_bytes = io.BytesIO()
	original_image.save(img_bytes, format='png')
	img_bytes.seek(0)
	
	img_width, img_height = original_image.size
	
	# Scale image so height is no height or width is no more than maximum values specified
	if img_width > img_height:
		img_height = img_height / (img_width / max_width)
		img_width = max_width

	else:
		img_width = img_width / (img_height / max_height)
		img_height = max_height

	return img_bytes, img_width, img_height


def get_measurement_statistics(values):
	"""
	Calculate Mean, Stdev, Range and n
	"""
	if not isinstance(values, (list, tuple, set)):
		values = [values]
	
	n = len(values)
	
	if n == 0:
		mean = 0
		stdev = 0
	elif n == 1:
		mean = values[0]
		stdev = values[0]
	else:
		mean = statistics.mean(values)
		stdev = statistics.stdev(values)

	# TODO: range
	
	from reportlab.pdfbase import pdfmetrics
	from reportlab.pdfbase.ttfonts import TTFont
	
	custom_font = "/home/domdf/GunShotMatch/GunShotMatch/GuiV2/GSMatch2_Core/Arvo_modified.ttf"
	pdfmetrics.registerFont(TTFont("Arvo_modified", custom_font))
	# TODO: modify glyph to taste using BirdFont
	
	return f"<font name='Arvo_modified'>𝝬</font> = {rounders(mean, '0.000')}, σ = {rounders(stdev, '0.00000')}, n = {n}"


# Yield successive n-sized chunks from l.
# https://www.geeksforgeeks.org/break-list-chunks-size-n-python/
def divide_chunks(l, n):
	# looping till length l
	for i in range(0, len(l), n):
		yield l[i:i + n]
