#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  outliers.py
"""Outlier Detection"""
#  
#  Copyright 2018 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  mad_outliers based on https://eurekastatistics.com/using-the-median-absolute-deviation-to-find-outliers/
#		Copyright 2013 Peter Rosenmai
#
#  quartile_outliers based on http://www.itl.nist.gov/div898/handbook/prc/section1/prc16.htm
#		Copyright 2012 NIST
#
#  spss_outliers based on http://www.unige.ch/ses/sococ/cl/spss/concepts/outliers.html
#		Copyright 2018 Eugene Horber, U. of Geneva
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
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

import numpy

def mad_outliers(dataset, cutoff = 3):
	"""Using the Median Absolute Deviation to Find Outliers"""

	if len(dataset) < 2:
		raise ValueError("Dataset too small")

	
	for i in range(2):
		dataset = [x for x in dataset if x is not None]
		for val in dataset:
			if val in ['', 0.0,0]:
				dataset.remove(val)
	if len(dataset) == 0:
		return float('nan')
	elif dataset == [None]:
		return float('nan')
	
	
	
	data_median = numpy.median(dataset)
	abs_deviation = abs(dataset-data_median)
#	print(data_median)
#	print(abs_deviation)
	mad = numpy.median(abs_deviation)
#	print(mad)
	
	abs_mad = abs_deviation / mad
#	print(abs_mad)
	
	outliers = []
	data_exc_outliers = []
	
	for mad_value, value in zip(abs_mad, dataset):
		#print(value)
		tmp = abs_mad[:]
		if mad_value > cutoff or -cutoff > mad_value:
			#dataset.remove(value)
			outliers.append(value)
		else:
			data_exc_outliers.append(value)
	
	#return outliers, dataset
	return outliers, data_exc_outliers
	
def two_stdev(dataset):
	"""Outliers are greater than 2x stdev from mean"""
	if len(dataset) < 2:
		raise ValueError("Dataset too small")

	
	for i in range(2):
		dataset = [x for x in dataset if x is not None]
		for val in dataset:
			if val in ['', 0.0,0]:
				dataset.remove(val)
	if len(dataset) == 0:
		return float('nan')
	elif dataset == [None]:
		return float('nan')
	
		
	data_mean = numpy.mean(dataset)
	data_stdev = numpy.std(dataset, ddof=1)
	
	outliers = []
	data_exc_outliers = []
	
	for value in dataset:
		#print(value)
		if value > (data_mean + (2*data_stdev)) or -(data_mean + (2*data_stdev)) > value:
			#dataset.remove(value)
			outliers.append(value)
		else:
			data_exc_outliers.append(value)
	
	#return outliers, dataset
	return outliers, data_exc_outliers

def stdev_outlier(dataset, rng = int(2)):
	"""Outliers are greater than rng*stdev from mean"""
	if len(dataset) < 2:
		raise ValueError("Dataset too small")

	
	for i in range(2):
		dataset = [x for x in dataset if x is not None]
		for val in dataset:
			if val in ['', 0.0,0]:
				dataset.remove(val)
	if len(dataset) == 0:
		return float('nan')
	elif dataset == [None]:
		return float('nan')
	
	data_mean = numpy.mean(dataset)
	data_stdev = numpy.std(dataset, ddof=1)
	
	outliers = []
	data_exc_outliers = []
	
	for value in dataset:
		#print(value)
		if value > (data_mean + (rng*data_stdev)) or -(data_mean + (rng*data_stdev)) > value:
			#dataset.remove(value)
			outliers.append(value)
		else:
			data_exc_outliers.append(value)
	
	#return outliers, dataset
	return outliers, data_exc_outliers

def quartile_outliers(dataset): 
	"""outliers are more than 3x inter-quartile range from upper or lower quartile"""

	for i in range(2):
		dataset = [x for x in dataset if x is not None]
		for val in dataset:
			if val in ['', 0.0,0]:
				dataset.remove(val)
	if len(dataset) == 0:
		return float('nan')
	elif dataset == [None]:
		return float('nan')
	
	q1 = numpy.percentile(dataset,25)
	q3 = numpy.percentile(dataset,75)
	iq = q3-q1
	upper_outer_fence = q3 + (3*iq)
	lower_outer_fence = q3 - (3*iq)
	
	outliers = []
	data_exc_outliers = []
	
	for value in dataset:
		#print(value)
		if not lower_outer_fence < value < (upper_outer_fence):
			#dataset.remove(value)
			outliers.append(value)
		else:
			data_exc_outliers.append(value)
	
	#return outliers, dataset
	return outliers, data_exc_outliers

def median_none(values_to_median):

	for i in range(2):
		values_to_median = [x for x in values_to_median if x is not None]
		for val in values_to_median:
			if val in ['', 0.0,0]:
				values_to_median.remove(val)
	if len(values_to_median) == 0:
		return 0
	elif values_to_median == [None]:
		return 0
	else:
		return numpy.median(values_to_median)
		
def iqr_none(dataset):
	if len(dataset) < 2:
		raise ValueError("Dataset too small")
	
	for i in range(2):
		dataset = [x for x in dataset if x is not None]
#		for val in dataset:
#			if val in ['', 0.0,0]:
#				dataset.remove(val)
	if len(dataset) == 0:
		return float('nan')
	elif dataset == [None]:
		return float('nan')
		
	q1 = numpy.percentile(dataset,25)
	q3 = numpy.percentile(dataset,75)
	iq = q3-q1
	
	return iq
	
def percentile_none(dataset,percentage):
	if len(dataset) < 2:
		raise ValueError("Dataset too small")
	
	for i in range(2):
		dataset = [x for x in dataset if x is not None]
#		for val in dataset:
#			if val in ['', 0.0,0]:
#				dataset.remove(val)
	if len(dataset) == 0:
		return float('nan')
	elif dataset == [None]:
		return float('nan')
		
	return numpy.percentile(dataset,percentage)

def spss_outliers(dataset, mode="all"):
	"""Based on IBM SPSS method for detecting outliers
	Outliers more than 1.5*IQR from Q1 or Q3
	"Extreme values" more than 3*IQR from Q1 or Q3"""
	
	if len(dataset) < 2:
		raise ValueError("Dataset too small")

	
	for i in range(2):
		dataset = [x for x in dataset if x is not None]
		for val in dataset:
			if val in ['', 0.0,0]:
				dataset.remove(val)
	if len(dataset) == 0:
		return float('nan')
	elif dataset == [None]:
		return float('nan')
		
	q1 = numpy.percentile(dataset,25)
#	print(q1)
	q3 = numpy.percentile(dataset,75)
#	print(q3)
	iq = q3-q1
#	print(iq)
	
	upper_outlier_fence = q3 + (1.5*iq)
	lower_outlier_fence = q3 - (1.5*iq)
	
	upper_extreme_fence = q3 + (3*iq)
	lower_extreme_fence = q3 - (3*iq)
	
	outliers = []
	extremes = []
	data_exc_outliers = []
	
	for value in dataset:
		if not lower_extreme_fence < value < (upper_extreme_fence):
			extremes.append(value)
		elif not lower_outlier_fence < value < (upper_outlier_fence):
			outliers.append(value)
		else:
			data_exc_outliers.append(value)
	
	return extremes, outliers, data_exc_outliers	
		
def main(args):
	#my_data = [70,72,74,76,80,114]
	my_data = [1, 2, 3, 3, 4, 4, 4, 5, 5.5, 6, 6, 6.5, 7, 7, 7.5, 8, 9, 12, 52, 90]
#	print("two stdev")
#	print(two_stdev(my_data))
#	print(numpy.mean(two_stdev(my_data)[1]))
#	print(numpy.median(two_stdev(my_data)[1]))
#	print("mad")
#	print(mad_outliers(my_data))
#	print(numpy.mean(mad_outliers(my_data)[1]))
#	print(numpy.median(mad_outliers(my_data)[1]))
#	print("quartile")
#	print(quartile_outliers(my_data))
#	print(numpy.mean(quartile_outliers(my_data)[1]))
#	print(numpy.median(quartile_outliers(my_data)[1]))

	print(spss_outliers(my_data))

	
	return 0
	

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
