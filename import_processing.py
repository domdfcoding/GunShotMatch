#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  import_processing.py
#  
#  Copyright 2019 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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

# Imports
from __future__ import print_function
#try:
#	from itertools import izip as zip
#except ImportError:
#	pass
	
import sys
import os
import itertools
import operator
from utils.helper import rounders
import time
from utils import pynist
import traceback
import numpy
	
sys.path.append("..")

nist_path = "../MSSEARCH"

import pyms
from pyms.GCMS.IO.JCAMP.Function import JCAMP_reader
from pyms.GCMS.Function import build_intensity_matrix, build_intensity_matrix_i
from pyms.Noise.Window import window_smooth, window_smooth_im
from pyms.Noise.SavitzkyGolay import savitzky_golay, savitzky_golay_im
from pyms.Baseline.TopHat import tophat, tophat_im
from pyms.Utils.IO import dump_object
from pyms.Deconvolution.BillerBiemann.Function import BillerBiemann, rel_threshold, num_ions_threshold
from pyms.Noise.Analysis import window_analyzer
from pyms.Peak.Function import peak_sum_area, peak_pt_bounds
from pyms.Peak.IO import store_peaks
from pyms.Experiment.Class import Experiment
from pyms.Experiment.IO import store_expr

def import_processing(jcamp_file, spectrum_csv_file, report_csv_file, combined_csv_file, bb_points = 9, bb_scans = 2, noise_thresh = 2, target_range = (0,120), tophat_struct="1.5m", nistpath = "../MSSEARCH", base_peak_filter = ['73'], ExprDir = "."):		
	global nist_path
	nist_path = nistpath
	
	# Parameters
	base_peak_filter = [int(x) for x in base_peak_filter]
	target_range = tuple(target_range)
	sample_name = os.path.splitext(os.path.basename(jcamp_file))[0]
	number_of_peaks = 80
	
	data = JCAMP_reader(jcamp_file)
	
	# list of all retention times, in seconds
	times = data.get_time_list()
	# get Total Ion Chromatogram
	tic = data.get_tic() 
	# RT Range, time step, no. scans, min, max, mean and median m/z
	data.info()
	
	#data.write("output/data") # save output
	
	# Mass Binning	
	im = build_intensity_matrix_i(data) # covnert to intensity matrix
	#im.get_size() #number of scans, number of bins
	masses = im.get_mass_list() # list of mass bins
	
	print(" Minimum m/z bin: {}".format(im.get_min_mass()))
	print(" Maximum m/z bin: {}".format(im.get_max_mass()))
	
	# Write Binned Mass Spectra to OpenChrom-like CSV file
	ms = im.get_ms_at_index(0) # first mass spectrum
	spectrum_csv = open(spectrum_csv_file, 'w')
	spectrum_csv.write('RT(milliseconds);RT(minutes) - NOT USED BY IMPORT;RI;')
	spectrum_csv.write(';'.join(str(mz) for mz in ms.mass_list))
	spectrum_csv.write("\n")
		
	for scan in range(len(times)):
		spectrum_csv.write("{};{};{};".format(int(times[scan]*1000),rounders((times[scan]/60),"0.0000000000"),0))	
		ms = im.get_ms_at_index(scan)
		spectrum_csv.write(';'.join(str(intensity) for intensity in ms.mass_spec))
		spectrum_csv.write('\n')
	spectrum_csv.close()
	
	## Data filtering

	# Note that Turbomass does not use smoothing for qualitative method.	
	# Top-hat baseline Correction seems to bring down noise,
	#  retaning shapes, but keeps points on actual peaks
	
	#dump_object(im, "output/im.dump") # un-processed output

	n_scan, n_mz = im.get_size()
	for ii in range(n_mz):
		#print("\rWorking on IC#", ii+1, '  ',end='')
		ic = im.get_ic_at_index(ii)
		ic_smooth = savitzky_golay(ic)
		ic_bc = tophat(ic_smooth, struct=tophat_struct)
		im.set_ic_at_index(ii, ic_bc)

	#dump_object(im, "output/im-proc.dump") # processed output
		
	# Peak Detection based on Biller and Biemann, 1974, with a window
	#  of n points, and combining y scans if they apex next to each other
	peak_list = BillerBiemann(im, points=bb_points, scans=bb_scans) 
	
	print(" Number of peaks identified before filtering: {}".format(len(peak_list)))
	
	# Filtering peak lists with automatic noise filtering
	noise_level = window_analyzer(tic)
	peak_list = num_ions_threshold(peak_list, noise_thresh, noise_level)
	# why use 2 for number of ions above threshold?
	print(" Number of peaks identified: {}".format(len(peak_list)))

	# Peak Areas
	peak_area_list = []
	filtered_peak_list = []
	
	for peak in peak_list:
		apex_mass_list = peak.get_mass_spectrum().mass_list
		apex_mass_spec = peak.get_mass_spectrum().mass_spec
		base_peak_intensity = max(apex_mass_spec)
		base_peak_index = [index for index, intensity in enumerate(apex_mass_spec) if intensity == base_peak_intensity][0]
		base_peak_mass = apex_mass_list[base_peak_index]
		#print(base_peak_mass)
		if base_peak_mass in base_peak_filter:
			continue # skip the peak if the base peak is at e.g. m/z 73, i.e. septum bleed
		
		area = peak_sum_area(im, peak)
		peak.set_area(area)
		peak_area_list.append(area)
		filtered_peak_list.append(peak)
	
	# Save the TIC and Peak List
	tic.write(os.path.join(ExprDir,"{}_tic.dat".format(sample_name)),formatting=False)
	store_peaks(filtered_peak_list,os.path.join(ExprDir,"{}_peaks.dat".format(sample_name)))
	
	# from https://stackoverflow.com/questions/16878715/how-to-find-the-index-of-n-largest-elements-in-a-list-or-np-array-python?lq=1
	top_peaks = sorted(range(len(peak_area_list)), key=lambda x: peak_area_list[x])
	
	# Write to turbomass-like CSV file
	report_csv = open(report_csv_file, "w")
	
	# Write to GunShotMatch Combine-like CSV file
	combine_csv = open(combined_csv_file, "w")
	
	combine_csv.write(sample_name)
	combine_csv.write("\n")
		
	report_csv.write("#;RT;Scan;Height;Area\n")
	combine_csv.write("Retention Time;Peak Area;;Lib;Match;R Match;Name;CAS Number;Scan\n")
	
	report_buffer = []
	
	for index in top_peaks:
		# Peak Number (1-80)
		peak_number = top_peaks.index(index)+1 
		# Retention time (minutes, 3dp)
		RT = rounders(filtered_peak_list[index].get_rt()/60,"0.000") 
		
		if not target_range[0] < RT <= target_range[1]:
			continue # skip the peak if it is outside the desired range
		
		# scan number, not that we really nead it as the peak object has the spectrum
		Scan = data.get_index_at_time(filtered_peak_list[index].get_rt())+1 
		# the binned mass spectrum
		filtered_peak_list[index].get_mass_spectrum() 
		# TIC intensity, as proxy for Peak height, which should be from baseline
		Height = '{:,}'.format(rounders(tic.get_intensity_at_index(data.get_index_at_time(filtered_peak_list[index].get_rt())),"0"))
		# Peak area, originally in "intensity seconds", so dividing by 60 to
		#  get "intensity minutes" like turbomass uses
		Area = '{:,}'.format(rounders(filtered_peak_list[index].get_area()/60,"0.0")) 
		
		#report_csv.write("{};{};{};{};{};{}\n".format(peak_number, RT, Scan, Height, Area,bounds))
		report_buffer.append([peak_number, RT, Scan, Height, Area])

	report_buffer = report_buffer[::-1] # Reverse list order

	# List of peaks already added to report
	existing_peaks = []

	filtered_report_buffer = []
	
	for row in report_buffer:
		filtered_report_buffer.append(row)
	
	filtered_report_buffer = filtered_report_buffer[:number_of_peaks]
	
	filtered_report_buffer.sort(key=operator.itemgetter(2))
	
	for row in filtered_report_buffer:
		index = filtered_report_buffer.index(row)
		report_csv.write(";".join([str(i) for i in row]))
		
		ms = im.get_ms_at_index(row[2]-1)
		
		create_msp("{}_{}".format(sample_name,row[1]),ms.mass_list, ms.mass_spec)
		matches_dict = nist_ms_comparison("{}_{}".format(sample_name,row[1]),ms.mass_list, ms.mass_spec)
		
		combine_csv.write("{};{};Page {} of 80;;;;;;{}\n".format(row[1],row[4],index+1,row[2]))
		
		for hit in range(1,6):
			report_csv.write(str(matches_dict["Hit{}".format(hit)]))
			report_csv.write(";")
			combine_csv.write(";;{};{};{};{};{};{};\n".format(hit,
					matches_dict["Hit{}".format(hit)]["Lib"],
					matches_dict["Hit{}".format(hit)]["MF"],
					matches_dict["Hit{}".format(hit)]["RMF"],
					matches_dict["Hit{}".format(hit)]["Name"],
					matches_dict["Hit{}".format(hit)]["CAS"],
					))

		report_csv.write("\n")
		
		time.sleep(2)
		
	report_csv.close()
	combine_csv.close()
	
	# Create an experiment
	expr = Experiment(sample_name, filtered_peak_list)
	expr.sele_rt_range(["{}m".format(target_range[0]),"{}m".format(target_range[1])])
	store_expr(os.path.join(ExprDir,"{}.expr".format(sample_name)), expr)
	
	return 0
	
def create_msp(sample_name, mass_list, mass_spec):
	"""Generate .MSP files for NIST MS Search"""
	
	#if sys.version_info[0] == 2:
		
	
	if not os.path.exists("MSP"):
		os.makedirs("MSP")
	msp_file = open(os.path.join("MSP",sample_name + ".MSP"),"w")
	msp_file.write("Name: {}\n".format(sample_name))
	msp_file.write("Num Peaks: {}\n".format(len(mass_list)))
	for mass, intensity in zip(mass_list, mass_spec):
		msp_file.write("{} {},\n".format(rounders(mass,"0.0"),intensity))
	msp_file.close()

def nist_ms_comparison(sample_name, mass_list, mass_spec):
	data_dict = {}

	try:
		pynist.generate_ini(nist_path, "mainlib", 5)
		
		def remove_chars(input_string):
			return input_string.replace("Hit 1  : ","").replace("Hit 2  : ","")\
				.replace("Hit 3","").replace("Hit 4","")\
				.replace("Hit 5","").replace("MF:","")\
				.replace(":","").replace("<","").replace(">","")\
				.replace(" ","").replace(sample_name,"")
		
		
		raw_output = pynist.nist_db_connector(nist_path,"MSP/{}.MSP".format(sample_name))
		
		# Process output
		for i in range(1,6):
			raw_output = raw_output.replace("Hit {}  : ".format(i),"Hit{};".format(i))
		raw_output = raw_output.replace("<<",'"').replace(">>",'"').split("\n")
		
		#for row in raw_output:
		#	print(row)

		matches_dict = {}
		
		for i in range(1,6):
			row = raw_output[i].split(";")
			matches_dict[row[0]] = {"Name":row[1], "MF":(row[3].replace("MF:",'').replace(" ",'')), "RMF":(row[4].replace("RMF:",'').replace(" ",'')), "CAS":(row[6].replace("CAS:",'').replace(" ",'')),"Lib":(row[8].replace("Lib:",'').replace(" ",''))}
		
		#for match in matches_dict:
		#	print(match)
		#	print(matches_dict[match])
		

	except:
		traceback.print_exc()	#print the error
		pynist.reload_ini(nist_path)
		sys.exit(1)
	
	print("\n")
	pynist.reload_ini(nist_path)
	return matches_dict

if __name__ == '__main__':
	from utils import timing
	import argparse

	#Command line switches
	parser = argparse.ArgumentParser()
	parser.add_argument("-i","--infile",help="JDX file to process.", required=True)
	parser.add_argument("-s","--spectrum",help="File to save spectra in.", required=True)
	parser.add_argument("-r","--report",help="File to save report in.",required=True)
	parser.add_argument("-c","--combined",help="File to save combined output in.",required=True)
	parser.add_argument("--bbpoints",help="",type=int, default=9)
	parser.add_argument("--bbscans",help="",type=int,default=2)
	parser.add_argument("-n","--noise_thresh",help="",type=float,default=2)
	parser.add_argument("-g","--target_range",help="",nargs=2, type=float,default=[0.0,120.0])
	parser.add_argument("-t","--tophat_struct",help="",default="1.5m")
	parser.add_argument("-p","--nist_path",help="",default="../MSSEARCH")
	parser.add_argument("-b","--base_peak_filter",help="",nargs="+", default=[])
	parser.add_argument("-e","--expr_dir",help="",default=".")
	
	args = parser.parse_args()

	sys.exit(import_processing(args.infile, args.spectrum, args.report,
								args.combined, args.bbpoints, args.bbscans, 
								args.noise_thresh, args.target_range, 
								args.tophat_struct, args.nist_path, 
								args.base_peak_filter, args.expr_dir))

