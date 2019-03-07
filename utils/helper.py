#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  helper.py	A collection of helpful Python functions
#  
#  Copyright 2018 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
#  check_dependencies based on code by TehTechGuy <https://stackoverflow.com/users/1117216/tehtechguy>. Copyright 2015
#  RepresentsInt by Triptych <https://stackoverflow.com/users/43089/triptych>. Copyright 2009

import os, sys#, msvcrt, time
from decimal import Decimal, ROUND_HALF_UP
import numpy

pyversion = int(sys.version[0])		# Python Version

def clear():								# clear the display
	os.system('cls' if os.name == 'nt' else 'clear')
	# works for Windows and UNIX, but does not clear Python Shell
	
def br():									# Line Break
	print("")
	
def isint(num):	# Only works with floating point numbers
	if num == int(num):
		return True
	else:
		return False

def entry(text_to_print):
	if pyversion == 3:
		return input(text_to_print)
	elif pyversion == 2:
		return raw_input(text_to_print)

def check_dependencies(dependencies, prt=True):
	"""Based on https://stackoverflow.com/questions/22213997/programmatically-check-if-python-dependencies-are-satisfied"""
	from pkgutil import iter_modules
	modules = set(x[1] for x in iter_modules())
	
	missing_modules = []
	for requirement in dependencies:
		if not requirement in modules:
			missing_modules.append(requirement)
	
	if prt:
		if len(missing_modules)==0:
			print("All modules installed")
		else:
			print("""\rThe following modules are missing.
	Please check the documentation.""")
			print(missing_modules)
		print("")
	
	else:
		return missing_modules

def parent_path(path):
	return os.path.abspath(os.path.join(path,os.pardir))

def RepresentsInt(s):
	"""From https://stackoverflow.com/questions/1265665/python-check-if-a-string-represents-an-int-without-using-try-except"""
	try: 
		int(s)
		return True
	except (ValueError, TypeError) as e:
		return False

def rounders(val_to_round, round_format):
	from decimal import Decimal, ROUND_HALF_UP
	return Decimal(Decimal(val_to_round).quantize(Decimal(str(round_format)), rounding=ROUND_HALF_UP))

def convert_to_xlsx(csv_input_file, xlsx_output_file, sheet_title, seperator=","):
	"""From http://coderscrowd.com/app/public/codes/view/201"""
	import xlsxwriter
	import csv
	
	wb = xlsxwriter.Workbook(xlsx_output_file)
	ws = wb.add_worksheet(sheet_title[:29]) 
	with open("./" + csv_input_file,'r') as csvfile:
		table = csv.reader(csvfile, delimiter=seperator)
		i = 0
		# write each row from the csv file as text into the excel file
		# this may be adjusted to use 'excel types' explicitly (see xlsxwriter doc)
		wrap_format = wb.add_format()
		wrap_format.set_text_wrap(True)
		
		for row in table:
			ws.write_row(i, 0, row)#,wrap_format)
			i += 1
	wb.close()
	

def mean_none(values_to_mean):
#	print(values_to_mean)
	for i in range(2):
		for val in values_to_mean:
			if val in  ['', None, 0.0,0] or val is None:
				values_to_mean.remove(val)
#	print(values_to_mean)
	if len(values_to_mean) == 0:
		return 0
#		return float('nan')
	elif values_to_mean == [None]:
		return 0
#		return float('nan')
	else:
		return numpy.mean(values_to_mean)	


def std_none(values_to_std):
	for i in range(2):
		for val in values_to_std:
			if val in  ['', None, 0.0,0]:
				values_to_std.remove(val)
	if len(values_to_std) == 0:
		return 0
#		return float('nan')
		
	elif values_to_std == [None]:
		return 0
#		return float('nan')
	else:
		return numpy.std(values_to_std, ddof=1)	
		
def median_none(values_to_median):
	for i in range(2):
		for val in values_to_median:
			if val in  ['', None, 0.0,0]:
				values_to_median.remove(val)
	if len(values_to_std) == 0:
		return 0
#		return float('nan')
	elif values_to_std == [None]:
		return 0
#		return float('nan')
	else:
		return numpy.median(values_to_median)
		
def verbosePrint(text):	#print only if the --verbose flag is set
	if verbose:
		print(str(text))
		
def copytree(src, dst, symlinks=False, ignore=None):
	import os
	import shutil
	"""from https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth
		because shutil.copytree is borked"""
	for item in os.listdir(src):
		s = os.path.join(src, item)
		d = os.path.join(dst, item)
		if os.path.isdir(s):
			shutil.copytree(s, d, symlinks, ignore)
		else:
			shutil.copy2(s, d)



