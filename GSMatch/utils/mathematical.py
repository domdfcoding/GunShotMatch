#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  mathematical.py
"""Mathematical Functions"""
#
#  Copyright 2014-2019 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  df_mean, df_stdev, df_percentage and df_log based on
#		http://jonathansoma.com/lede/foundations/classes/pandas%20columns%20and%20functions/apply-a-function-to-every-row-in-a-pandas-dataframe/
#		Copyright 2016 Jonathan Soma
#
#  RepresentsInt from https://stackoverflow.com/questions/1265665/python-check-if-a-string-represents-an-int-without-using-try-except
#  		Copyright 2009 Triptych
#		Licensed Under CC-BY-SA
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


def df_mean(row, col_string):
	from numpy import nanmean
	return nanmean(row[col_string])

def df_median(row, col_string):
	from numpy import nanmedian
	return nanmedian(row[col_string])

def df_stdev(row, col_string):
	from numpy import nanstd
	return nanstd(row[col_string])
	
def df_log_stdev(row, col_string):
	from numpy import nanstd, nan
	from math import log10
	return nanstd([log10(x) if x > 0.0 else nan for x in row[col_string]])

def df_percentage(row, total, col_string):
	return (row[col_string]/float(total))*100.0

def df_log(row, base, col_string):
	from math import log
	if row[col_string] > 0.0:
		return log(row[col_string], base)
	else:
		return 0

def df_data_points(row, prefixList):
	return [row[prefix] for prefix in prefixList]


def df_outliers(data, outlier_mode):
	"""detect outliers"""
	import pandas as pd
	from utils import outliers

	if outlier_mode == "mad":
		x = outliers.mad_outliers(data)
	elif outlier_mode == "quartiles":
		x = outliers.quartile_outliers(data)
	elif outlier_mode == "2stdev":
		x = outliers.stdev_outlier(data, 2)  # outlier classed as more than 2 stdev away from mean
	else:
		return (None)
	
	return pd.Series(list(x))


def df_count(row, col_string_list):
	import numpy
	count = 0
	for col_string in col_string_list:
		if row[col_string] and not numpy.isnan(row[col_string]):
			count += 1
	return count

def magnitude(x):
	from math import log10
	if x>0.0:
		return int(log10(x))
	else:
		return 0

def remove_zero(inputlist):
	import numpy as np
	inputlist = np.array(inputlist)
	outputlist = inputlist[np.nonzero(inputlist)]
	return list(outputlist)


def isint(num):	# Only works with floating point numbers
	if num == int(num):
		return True
	else:
		return False
	
def RepresentsInt(s):
	try:
		int(s)
		return True
	except (ValueError, TypeError) as e:
		return False

def rounders(val_to_round, round_format):
	from decimal import Decimal, ROUND_HALF_UP
	return Decimal(Decimal(val_to_round).quantize(Decimal(str(round_format)), rounding=ROUND_HALF_UP))


def mean_none(values_to_mean):
	import numpy
	#	print(values_to_mean)
	for i in range(2):
		for val in values_to_mean:
			if val in ['', None, 0.0, 0] or val is None:
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
	import numpy
	for i in range(2):
		for val in values_to_std:
			if val in ['', None, 0.0, 0]:
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
	import numpy
	for i in range(2):
		for val in values_to_median:
			if val in ['', None, 0.0, 0]:
				values_to_median.remove(val)
	if len(values_to_median) == 0:
		return 0
	#		return float('nan')
	elif values_to_median == [None]:
		return 0
	#		return float('nan')
	else:
		return numpy.median(values_to_median)

def within1min(value1, value2):
	if value1 not in [0, None, ''] and value2 not in [0, None, '']:
		return (float(value1) - 1) < (float(value2)) < (float(value1) + 1)
	else:
		return False