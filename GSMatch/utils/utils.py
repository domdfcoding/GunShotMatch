#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  utils.py
#
#  Copyright 2018 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  convert_to_xlsx from http://coderscrowd.com/app/public/codes/view/201
#		Copyright 2014 Tim Kacprowski
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
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

__author__ = "Dominic Davis-Foster"
__copyright__ = "Copyright 2018 Dominic Davis-Foster"

__license__ = "GPLv3"
__version__ = "0.1.0"
__email__ = "dominic@davis-foster.co.uk"

def convert_to_xlsx(csv_input_file, xlsx_output_file, sheet_title, seperator=","):
	import xlsxwriter
	import csv
	
	wb = xlsxwriter.Workbook(xlsx_output_file)
	ws = wb.add_worksheet(sheet_title[:29])
	with open("./" + csv_input_file, 'r') as csvfile:
		table = csv.reader(csvfile, delimiter=seperator)
		i = 0
		# write each row from the csv file as text into the excel file
		# this may be adjusted to use 'excel types' explicitly (see xlsxwriter doc)
		wrap_format = wb.add_format()
		wrap_format.set_text_wrap(True)
		
		for row in table:
			ws.write_row(i, 0, row)  # ,wrap_format)
			i += 1
	wb.close()
