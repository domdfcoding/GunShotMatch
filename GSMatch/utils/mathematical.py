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

__author__ = "Dominic Davis-Foster"
__copyright__ = "Copyright 2014-2019 Dominic Davis-Foster"

__license__ = "GPL"
__version__ = "0.1.0"
__email__ = "dominic@davis-foster.co.uk"

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
		#print(row[col_string])
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


# The following ased on:
#   https://www.psychometrica.de/effect_size.html#transform
#   https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/hedgeg.htm
# and Cohen, J. (1988). Statistical power analysis for the behavioral sciences (2nd Edition). Hillsdale, NJ: Lawrence Erlbaum Associates

def pooled_sd(sample1, sample2, weighted=False):
	"""weighted=True for weighted pooled SD
	Formula from https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/hedgeg.htm"""
	import numpy as np
	
	sd1 = np.std(sample1)
	sd2 = np.std(sample2)
	n1 = len(sample1)
	n2 = len(sample2)
	if weighted:
		return np.sqrt((((n1 - 1) * (sd1 ** 2)) + ((n2 - 1) * (sd2 ** 2))) / (n1 + n2 - 2))
	else:
		return np.sqrt(((sd1 ** 2) + (sd2 ** 2)) / 2)


def d_cohen(sample1, sample2, sd=1, tail=1, pooled=False):
	import numpy as np
	
	mean1 = np.mean(sample1)
	mean2 = np.mean(sample2)
	
	if sd == 1:
		sd = np.std(sample1)
	else:
		sd = np.std(sample2)
	
	if pooled:
		sd = pooled_sd(sample1, sample2)
	
	if tail == 2:
		return np.abs(mean1 - mean2) / sd
	
	return (mean1 - mean2) / sd


def g_hedge(sample1, sample2):
	import numpy as np
	
	mean1 = np.mean(sample1)
	mean2 = np.mean(sample2)
	return (mean1 - mean2) / pooled_sd(sample1, sample2, True)


def g_durlak_bias(g, n):
	"""Application of Durlak's bias correction to the Hedge's g statistic.
	Formula from https://www.itl.nist.gov/div898/software/dataplot/refman2/auxillar/hedgeg.htm
	
	n = n1+n2"""
	
	import numpy as np
	
	Durlak = ((n - 3) / (n - 2.25)) * np.sqrt((n - 2) / n)
	return g * Durlak


def interpret_d(d_or_g):
	"""Interpret Cohen's d or Hedge's g values using Table 1
	from https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3444174/"""
	import numpy as np
	
	if d_or_g < 0:
		return f"{interpret_d(np.abs(d_or_g)).split(' ')[0]} Adverse Effect"
	elif 0.0 <= d_or_g < 0.2:
		return "No Effect"
	elif 0.2 <= d_or_g < 0.5:
		return "Small Effect"
	elif 0.5 <= d_or_g < 0.8:
		return "Intermediate Effect"
	elif 0.8 <= d_or_g:
		return "Large Effect"
