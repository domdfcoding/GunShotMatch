#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  SampleInferer.py
#  
#  Copyright 2019 Dominic Davis-Foster <domdf@ryzen>
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

def infer_samples(csvpath):

	import os
	
	inferred_samples = []
	directory_listing = os.listdir(csvpath)
	for filename in directory_listing:
		#if filename.lower().endswith(".csv"):
		if filename.endswith("GC_80.CSV"):
			#print filename[:-9]+'MS_80.CSV'
			if os.path.isfile(csvpath + filename[:-9]+'MS_80.CSV'):
				inferred_samples.append(filename[:-10])

	inferred_samples.sort()
	return(inferred_samples)

if __name__ == '__main__':
    print(infer_samples("./Results/CSV/"))
