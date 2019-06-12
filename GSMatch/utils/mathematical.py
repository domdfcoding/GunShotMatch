#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  mathematical.py
"""Mathematical Functions"""
#
#  Copyright 2014-2019 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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

from mathematical.utils import strip_none_bool_string
import numpy

def mean_none(values_to_mean):
	"""
	Calculate the mean, excluding NaN, strings, boolean values, and zeros
	
	:param values_to_mean: list to calculate mean from
	:type values_to_mean: list
	
	:return: mean
	:return float
	"""
	
	values_to_mean = strip_none_bool_string(values_to_mean)

	
	#	print(values_to_mean)
	for i in range(2):
		for val in values_to_mean:
			if val in ['', None, 0.0, 0] or val is None:
				values_to_mean.remove(val)
	#	print(values_to_mean)
	
	if len(values_to_mean) == 0:
		return 0
	elif values_to_mean == [None]:
		return 0
	else:
		return numpy.nanmean(values_to_mean)


def std_none(values_to_std):
	"""
	Calculate the standard deviation, excluding NaN, strings, boolean values, and zeros

	:param values_to_std: list to calculate mean from
	:type values_to_std: list

	:return: standard deviation
	:return float
	"""
	
	values_to_std = strip_none_bool_string(values_to_std)
	
	for i in range(2):
		for val in values_to_std:
			if val in ['', None, 0.0, 0]:
				values_to_std.remove(val)
	
	if len(values_to_std) == 0:
		return 0
	elif values_to_std == [None]:
		return 0
	else:
		return numpy.nanstd(values_to_std, ddof=1)


def median_none(values_to_median):
	"""
	Calculate the median, excluding NaN, strings, boolean values, and zeros

	:param values_to_median: list to calculate mean from
	:type values_to_median: list

	:return: standard deviation
	:return float
	"""
	
	values_to_median = strip_none_bool_string(values_to_median)

	for i in range(2):
		for val in values_to_median:
			if val in ['', None, 0.0, 0]:
				values_to_median.remove(val)
	
	if len(values_to_median) == 0:
		return 0
	elif values_to_median == [None]:
		return 0
	else:
		return numpy.nanmedian(values_to_median)