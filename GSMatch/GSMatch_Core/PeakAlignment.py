#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  PeakAlignment.py
"""Ancillary functions for PyMS peak alignment"""
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2019 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#  Based on Code from PyMS
#  Copyright (C) 2005-2012 Vladimir Likic
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


import pandas


def get_peak_alignment(A, minutes=True):
	"""
	Get dictionary of aligned retention times

	:param A: Alignment object to extract data from
	:param minutes: An optional indicator whether to return retention times
		in minutes. If False, retention time will be returned in seconds
	:type minutes: BooleanType

	:author: Woon Wai Keen
	:author: Andrew Isaac
	:author: Vladimir Likic
	:author: Dominic Davis-Foster
	"""
	
	rt_table = []
	
	# for each alignment position write alignment's RT
	for peak_idx in range(len(A.peakpos[0])):
		
		rts = []
		countrt = 0
		
		for align_idx in range(len(A.peakpos)):
			
			peak = A.peakpos[align_idx][peak_idx]
			
			if peak is not None:
				
				if minutes:
					rt = peak.get_rt() / 60.0
				else:
					rt = peak.get_rt()
				
				rts.append(rt)
				
				countrt = countrt + 1
			else:
				rts.append(None)
		
		if countrt == len(A.expr_code):
			rt_table.append(rts)
	
	rt_alignment = pandas.DataFrame(rt_table, columns=A.expr_code)
	rt_alignment = rt_alignment.reindex(sorted(rt_alignment.columns), axis=1)
	
	return rt_alignment


def get_ms_alignment(A):
	"""
	Get dictionary of mass spectra for the aligned peaks

	:param A: Alignment object to extract data from

	:author: Woon Wai Keen
	:author: Andrew Isaac
	:author: Vladimir Likic
	:author: Dominic Davis-Foster
	"""
	
	ms_table = []
	
	# for each alignment position write alignment's ms
	for peak_idx in range(len(A.peakpos[0])):
		
		specs = []
		countms = 0
		
		for align_idx in range(len(A.peakpos)):
			
			peak = A.peakpos[align_idx][peak_idx]
			
			if peak is not None:
				
				ms = peak.get_mass_spectrum()
				specs.append(ms)
				countms = countms + 1
			else:
				specs.append(None)
		
		if countms == len(A.expr_code):
			ms_table.append(specs)
	
	ms_alignment = pandas.DataFrame(ms_table, columns=A.expr_code)
	ms_alignment = ms_alignment.reindex(sorted(ms_alignment.columns), axis=1)
	
	return ms_alignment

