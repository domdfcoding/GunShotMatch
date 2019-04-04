#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  GSMatch_Comparison.py
#
#  Copyright 2017-2019 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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

"""GunShotMatch Project Comparison"""

program_name = "GunShotMatch Project Comparison"
__version__ = "0.1"
copyright = "2017-2019"

# Imports
import coverage

COV = coverage.coverage(branch=True, include="./*")
COV.start()

import os
import sys
import time
sys.path.append("..")

from gsm_core import GSMConfig
from utils.terminal import clear, br
from utils.charts import default_colours, default_filetypes, bw_default_colours, bw_default_styles

def comparison(left_sample, right_sample, show_outliers=True, show_raw_data=False, err_bar="range",
			   outlier_mode="2stdev", leg_cols=1, column_width=4, a_value = 0.01, radar_use_log=10,
			   styles=bw_default_styles, bw_colours=bw_default_colours, colours=default_colours,
			   filetypes=default_filetypes, radar_figsize=(4,9), pca_figsize=(8,8), bw_figsize=None,
			   display = False):
	
	import json
	import numpy
	import pandas
	import operator
	
	from utils.paths import maybe_make
	from utils.spreadsheet import append_to_xlsx
	from utils.mathematical import df_count, df_mean, rounders
	from utils.charts import radar_chart_wrapper, box_whisker_wrapper, PrincipalComponentAnalysis
	
	from gsm_core import get_ms_alignment, get_peak_alignment
	
	from pyms.Experiment.IO import store_expr, load_expr
	from pyms.Peak.List.DPA.Class import PairwiseAlignment
	from pyms.Peak.List.DPA.Function import align_with_tree, exprl2alignment, align
	
	comparison_name = "{} v {}".format(left_sample, right_sample)
	
	if display:
		radar_mode = "display"
		box_whisker_mode = "display"
		pca_mode = "display"
	else:
		radar_mode = os.path.join(CHARTS_DIRECTORY, "Comparison", f"{comparison_name}_RADAR")
		box_whisker_mode = os.path.join(CHARTS_DIRECTORY, "Comparison", f"{comparison_name}_BOX_WHISKER")
		pca_mode = os.path.join(CHARTS_DIRECTORY, "Comparison", f"{comparison_name}_PCA")
		
	
	"""Chart Data"""
	chart_data = pandas.concat([pandas.read_csv(os.path.join(CSV_DIRECTORY, "{}_CHART_DATA.csv".format(left_sample)),
												sep=";", index_col=0),
								pandas.read_csv(os.path.join(CSV_DIRECTORY, "{}_CHART_DATA.csv".format(right_sample)),
												sep=";", index_col=0)
								], axis=1, sort=False)
	
	chart_data.drop("Compound Names", axis=1, inplace=True)
	chart_data['Compound Names'] = chart_data.index
	
	# determine order of compounds on graph
	for compound in chart_data.index.values:
		chart_data["Count"] = chart_data.apply(df_count, args=(
		[f"{sample} Peak Area" for sample in [left_sample, right_sample]],),
											   axis=1)
	
	chart_data['Compound Names'] = chart_data.index
	chart_data = chart_data.sort_values(['Count', 'Compound Names'])
	chart_data.fillna(0, inplace=True)
	
	maybe_make(os.path.join(CHARTS_DIRECTORY, "Comparison"))
	
	radar_chart_wrapper(chart_data, [left_sample, right_sample], use_log=radar_use_log, colours=colours, figsize=radar_figsize,
				mode=radar_mode, filetypes=default_filetypes)
	
	with open(os.path.join(RESULTS_DIRECTORY, f"{left_sample}.info"), "r") as info_file:
		left_prefixList = [x.rstrip("\r\n") for x in info_file.readlines()]
	
	with open(os.path.join(RESULTS_DIRECTORY, f"{right_sample}.info"), "r") as info_file:
		right_prefixList = [x.rstrip("\r\n") for x in info_file.readlines()]
	
	print(left_sample, left_prefixList)
	print(right_sample,right_prefixList)

	box_whisker_wrapper(chart_data, [(left_sample, left_prefixList), (right_sample, right_prefixList)],
				show_outliers=show_outliers, show_raw_data=show_raw_data,
				err_bar=err_bar, outlier_mode=outlier_mode, leg_cols=leg_cols, mode=box_whisker_mode,
				figsize=bw_figsize, column_width=column_width, styles=styles, colours=bw_colours, filetypes=filetypes)
	
	
	
	"""Principal Component Analysis"""
	pca_data = {"target":[left_sample]*len(left_prefixList) + [right_sample]*len(right_prefixList)}
	features = []
	targets = [left_sample, right_sample]
	
	for compound in chart_data.index.values:
		area_list = []
		for prefix in left_prefixList + right_prefixList:
			area_list.append(chart_data.loc[compound,prefix])
		pca_data[compound] = area_list
		features.append(compound)
	
	pca_data = pandas.DataFrame(data=pca_data)
	pca = PrincipalComponentAnalysis(pca_data, features, targets,mode=pca_mode, figsize=pca_figsize, colours=colours)
	
	"""Open the output file"""
	output_filename = os.path.join(RESULTS_DIRECTORY, f"{comparison_name}_COMPARISON")
	
	while True:
		try:
			outputCSV = open(output_filename + ".CSV", "w")
			outputCSV.write(f"Explained Variance Ratio: {rounders(pca[0],'0.0000')}, {rounders(pca[1],'0.0000')};;;;{left_sample};;;;;;;;{right_sample};;;;;;;;t-tests;;;;;;;;\n")
			outputCSV.write(
				f"t-test Threshold α={a_value};;;;Retention Time;;;;Peak Area;;;;Retention Time;;;;Peak Area;;;;Retention Time;;;;Peak Area;;;;Welch's t-test Peak Area;;;;MS Comparison\n")
			outputCSV.write(
				"Name;CAS Number;;;Mean;STDEV;%RSD;;Mean;STDEV;%RSD;;Mean;STDEV;%RSD;;Mean;STDEV;%RSD;;t-statistic;p-value;Result;;t-statistic;p-value;Result;;t-statistic;p-value;Result;;Mean;STDEV;%RSD\n")
			
			break
		except IOError:
			print(
				"The file \"" + output_filename + "\" is locked for editing in another program. Press any key to try again.")
			input(">")


	"""Peak Data"""
	left_peak_data = []
	with open(os.path.join(CSV_DIRECTORY, "{}_peak_data.json".format(left_sample)), "r") as jsonfile:
		for peak in jsonfile.readlines():
			left_peak_data.append(json.loads(peak))
			
	right_peak_data = []
	with open(os.path.join(CSV_DIRECTORY, "{}_peak_data.json".format(right_sample)), "r") as jsonfile:
		for peak in jsonfile.readlines():
			right_peak_data.append(json.loads(peak))
			
			
	"""Alignment Data"""
	# define the input experiments list
	left_expr_list = []
	for prefix in left_prefixList:
		file_name = os.path.join(EXPERIMENTS_DIRECTORY, prefix + ".expr")
		left_expr_list.append(load_expr(file_name))
	
	right_expr_list = []
	for prefix in right_prefixList:
		file_name = os.path.join(EXPERIMENTS_DIRECTORY, prefix + ".expr")
		right_expr_list.append(load_expr(file_name))
	
	print("\nAligning\n")
	left_F1 = exprl2alignment(left_expr_list)
	left_T1 = PairwiseAlignment(left_F1, Dw, Gw)
	left_A1 = align_with_tree(left_T1, min_peaks=min_peaks)
	
	right_F2 = exprl2alignment(right_expr_list)
	right_T2 = PairwiseAlignment(right_F2, Dw, Gw)
	right_A2 = align_with_tree(right_T2, min_peaks=min_peaks)
	
	both_alignment = align(left_A1, right_A2, Dw, Gw)
	
#	print(score_matrix(left_A1, right_A2, Dw))

	rt_alignment = get_peak_alignment(both_alignment)
	
	rt_alignment[left_sample] = rt_alignment.apply(df_mean,
												   args=([prefix for prefix in left_prefixList],),
												   axis=1)
	rt_alignment[right_sample] = rt_alignment.apply(df_mean,
												   args=([prefix for prefix in right_prefixList],),
												   axis=1)
	
	ms_alignment = get_ms_alignment(both_alignment)
	
	left_aligned_peaks = []
	right_aligned_peaks = []
	
	#print(f"{left_sample} Peaks")
	for index, aligned_peak in enumerate(rt_alignment[left_sample]):
		found_peak = False
		for peak in left_peak_data:
			#print(aligned_peak, peak["average_rt"])
			if peak["average_rt"] == aligned_peak:
				#print(peak)
				#for key in peak:
				#	print(f"{key}: {peak[key]}")
				peak["ms_list"] = [ms_alignment.iloc[index][prefix] for prefix in left_prefixList]
				left_aligned_peaks.append(peak)
				found_peak = True
				break
		if not found_peak:
			left_aligned_peaks.append(None)
	
	#print(f"{right_sample} Peaks")
	for index, aligned_peak in enumerate(rt_alignment[right_sample]):
		found_peak = False
		for peak in right_peak_data:
			if peak["average_rt"] == aligned_peak:
				#print(peak)
				#for key in peak:
				#	print(f"{key}: {peak[key]}")
				peak["ms_list"] = [ms_alignment.iloc[index][prefix] for prefix in right_prefixList]
				right_aligned_peaks.append(peak)
				found_peak = True
				break
		if not found_peak:
			right_aligned_peaks.append(None)
	
	for left_peak, right_peak in zip(left_aligned_peaks, right_aligned_peaks):
		if not any([left_peak is None, right_peak is None]):
		#	print(f"{left_peak['average_rt']}		{right_peak['average_rt']}")
			if (f"{left_peak['hits'][0]['CAS']}" == f"{right_peak['hits'][0]['CAS']}"):
				# The top hit for each project is the same
				#print(f"{left_peak['hits'][0]['Name']}		{right_peak['hits'][0]['Name']}")
				left_hit_number, right_hit_number = 0, 0
			else: # Check if there is a match in the other four hits
				left_hit_dict = {}
				right_hit_dict = {}
				for hit_num in range(0,5):
					left_hit_dict[f"{left_peak['hits'][hit_num]['CAS']}"] = hit_num
					right_hit_dict[f"{right_peak['hits'][hit_num]['CAS']}"] = hit_num
				left_hit_set = set(left_hit_dict)
				right_hit_set = set(right_hit_dict)
				
				results_list = []
				for CAS in left_hit_set.intersection(right_hit_set):
					# CAS Number and Hit Numbers of hits in common
					left_hit_num = left_hit_dict[CAS]
					right_hit_num = right_hit_dict[CAS]
					left_hit_mf = left_peak["hits"][left_hit_num]["average_MF"]
					right_hit_mf = right_peak["hits"][right_hit_num]["average_MF"]
					
					results_list.append([CAS, left_hit_num, right_hit_num,
										numpy.mean([left_hit_num, right_hit_num]),
										numpy.mean([left_hit_mf, right_hit_mf])
										])
				results_list = sorted(results_list, key=operator.itemgetter(3,4))
				#print(results_list[0])
				left_hit_number, right_hit_number = results_list[0][1:3]
			
			#print(f"{left_peak['hits'][left_hit_number]['Name']}		{right_peak['hits'][right_hit_number]['Name']}")
			
			# Write output data
			name = left_peak['hits'][left_hit_number]['Name']
			CAS = left_peak['hits'][left_hit_number]['CAS']
			
			left_rt_mean = left_peak['average_rt']
			left_rt_stdev = numpy.nanstd(left_peak['rt_data'])
			left_rt_n = len(left_peak['rt_data'])
			
			left_area_mean = left_peak['average_peak_area']
			left_area_stdev = numpy.nanstd(left_peak['area_data'])
			left_area_n = len(left_peak['rt_data'])
			
			right_rt_mean = right_peak['average_rt']
			right_rt_stdev = numpy.nanstd(right_peak['rt_data'])
			right_rt_n = len(right_peak['rt_data'])
			
			right_area_mean = right_peak['average_peak_area']
			right_area_stdev = numpy.nanstd(right_peak['area_data'])
			right_area_n = len(left_peak['rt_data'])
			

			outputCSV.write(f"{name};{CAS};;;")	# Name;CAS Number;;;
			
			outputCSV.write(f"{left_rt_mean};{left_rt_stdev};{left_rt_stdev / left_rt_mean};;") # Mean RT left;STDEV RT left;%RSD RT left;;
			outputCSV.write(f"{left_area_mean};{left_area_stdev};{left_area_stdev / left_area_mean};;") # Mean Area left;STDEV Area left;%RSD Area left;;
			
			outputCSV.write(f"{right_rt_mean};{right_rt_stdev};{right_rt_stdev / right_rt_mean};;") # Mean RT right;STDEV RT right;%RSD RT right;;
			outputCSV.write(f"{right_area_mean};{right_area_stdev};{right_area_stdev / right_area_mean};;") # Mean Area right;STDEV Area right;%RSD Area right;;
			
			"""Retention Time t-statistics"""
			# Independent 2 Samples t-test
			rt_t_stat, rt_p_val, rt_result = t_test(left_rt_mean, left_rt_n, left_rt_stdev,right_rt_mean, right_rt_n, right_rt_stdev, a_value)
			outputCSV.write(f"{rt_t_stat}; {rt_p_val}; {rt_result};;")
			
			"""Peak Area t-statistics"""
			# Independent 2 Samples t-test
			area_t_stat, area_p_val, area_result = t_test(left_area_mean, left_area_n, left_area_stdev,right_area_mean, right_area_n, right_area_stdev, a_value)
			outputCSV.write(f"{area_t_stat};{area_p_val};{area_result};;")
			
			# Welch's t-test
			area_t_stat, area_p_val, area_result = t_test(left_area_mean, left_area_n, left_area_stdev,right_area_mean, right_area_n, right_area_stdev, a_value, True)
			outputCSV.write(f"{area_t_stat};{area_p_val};{area_result};;")
			
			"""MS Comparison"""
			#print(left_peak["ms_list"])
			#print(right_peak["ms_list"])
			mf_mean, mf_stdev = ms_comparisons(left_peak["ms_list"], right_peak["ms_list"])
			outputCSV.write(f"{mf_mean};{mf_stdev};{mf_stdev/mf_mean};;")

			outputCSV.write("\n")
			
	outputCSV.close()

	time.sleep(3)

	append_to_xlsx(output_filename + ".CSV", output_filename + ".xlsx", "Comparison", overwrite=True, seperator=";", toFloats=True)
	
	comparisonFormat(output_filename + ".xlsx", a_value)

	make_archive(comparison_name, left_sample, left_prefixList, right_sample, right_prefixList)
	
	return

def comparisonFormat(inputFile, a_value=0.05):  # Formatting for Final Output
	from openpyxl import load_workbook
	from openpyxl.utils import get_column_letter
	from utils.spreadsheet import format_header, format_sheet, make_column_property_list
	
	print('\nGenerating XLSX Output...')

	"""From http://openpyxl.readthedocs.io/en/default/"""
	wb = load_workbook(inputFile)
	
	# grab the active worksheet
	ws = wb["Comparison"]
	
	#ws.cell(column=1, row=1).value = u"Threshold α={}".format(a_value)
	
	number_format_list = {'E': '0.000', 'F': '0.000000', 'G': '0.00%', 'I': '0.00', 'J':'0.00', 'K':'0.00%', # left Sample
						  'M': '0.000', 'N': '0.000000', 'O': '0.00%', 'Q': '0.00', 'R':'0.00', 'S':'0.00%', # right sample
						  'U': '0.000000', 'V': '0.000000',			# RT t-test
						  'Y': '0.000000', 'Z': '0.000000',			# Area t-test
						  'AC': '0.000000', 'AD': '0.000000',		# Area Welch's t-test
						  'AG': '0.0', 'AH': '0.0000', 'AI': '0.00%',# MS Comparison
						  }
	spacer_width = 1
	
	width_list = {'B': 12, 'C': spacer_width, 'D': 0, # Name and CAS
				  'E': 8, 'F': 11, 'G': 7, 'H': spacer_width, 'I': 15, 'J': 12, 'K': 8, 'L': spacer_width*2, # left Sample
				  'M': 8, 'N': 11, 'O': 7, 'P': spacer_width, 'Q': 15, 'R': 12, 'S': 8, 'T': spacer_width*2, # right Sample
				  'U': 11, 'V': 10, 'W': 7, 'X': spacer_width,		# RT t-test
				  'Y': 11, 'Z': 10, 'AA': 7, 'AB': spacer_width,	# Area t-test
				  'AC': 11, 'AD': 10, 'AE': 7, 'AF': spacer_width,	# Area Welch's t-test
				  'AG': 8, 'AH': 10, 'AI': 8,						# MS Comparison
				  }
	
	alignment_list = make_column_property_list({'5':'right'}, {'B':'center'}, repeat=32, length=1)
	
	for column in ['W', 'AA', 'AE']:
		alignment_list[column] = 'center'
	
	format_sheet(ws, number_format_list, width_list, alignment_list)
	
	
	"""Header"""
	# Row 1
	ws.merge_cells("E1:K1")
	ws.merge_cells("M1:S1")
	ws.merge_cells('U1:AE1')
	
	# Row 2
	for offset in range(7):
		merge_string = get_column_letter(5 + (4 * offset)) + '2:' + get_column_letter(7 + (4 * offset)) + '2'
		# print(merge_string)
		ws.merge_cells(merge_string)
	
	# MS Comparisons
	ws.cell(column=33, row=1).value = "MS Comparisons"
	ws.merge_cells('AG1:AI2')
	
	# Centering text
	format_header(ws, make_column_property_list(
		{"2": "center"}, repeat=35,
		length=1), 1, 2)
	
	
	# Save the file
	wb.save(inputFile)
	return

def ms_comparisons(left_ms_data, right_ms_data):
	import numpy
	from itertools import product
	from utils.SpectrumSimilarity import SpectrumSimilarity
	
	
	perms = []
	for perm in product(left_ms_data, right_ms_data):
		top_spec = numpy.column_stack((perm[0].mass_list, perm[0].mass_spec))
		bottom_spec = numpy.column_stack((perm[1].mass_list, perm[1].mass_spec))
		perms.append(SpectrumSimilarity(top_spec, bottom_spec, t=0.25, b=1, xlim=(45, 500), x_threshold=0, print_graphic=False)[0] * 1000)
	
	#print(numpy.nanmean(perms))
	#print(numpy.nanstd(perms))
	return numpy.nanmean(perms), numpy.nanstd(perms)

def t_test(left_mean, left_n, left_stdev, right_mean, right_n, right_stdev, a_value=0.01, welch=False):
	from scipy import stats
	
	if not any(x == 0.0 for x in [left_mean, left_n, right_mean, right_n]):
		t_stat, p_val = stats.ttest_ind_from_stats(left_mean, left_stdev, left_n, right_mean,
												   right_stdev, right_n, not welch)
		
		if str(t_stat) == "inf":
			t_stat = "#"
		
		result = "Diff" if p_val <= a_value else "Same"
	
	else:
		t_stat = ''
		p_val = ''
		result = "Diff"
	
	return t_stat, p_val, result

def multiple_project_charts(projectList, show_outliers=True, show_raw_data=False, err_bar="range",
			   outlier_mode="2stdev", leg_cols=1, column_width=4, filetypes=default_filetypes,
			   styles=[	"D",  # diamond
			  			"s",  # square
			  			"X",  # bold cross
			  			"^",  # triangle
			  			"d",  # diamond
			  			"h",  # hexagon
			  			"o",  # dot
			  			"v",  # down triangle
			  			"<",  # left triangle
			  			">"], # right triangle
			   bw_colours=[	"DarkRed",
							"DeepSkyBlue",
							"Green",
							"Purple",
							"Black",
							"Sienna",
							"MediumTurquoise",
							"DarkOliveGreen",
							"m",
							"DarkSlateBlue",
							"OrangeRed",
							"CadetBlue",
							"Olive",
							"Red",
							"Blue",
							"PaleVioletRed",
							"Teal",
							"y",
							"RoyalBlue",
							],
			   radar_colours=default_colours, radar_figsize=(4,9), bw_figsize=None, mode = "display",
			   radar_use_log = False):
	
	"""All Samples Comparison (Charts Only)"""
	# TODO File names for charts
	
	import pandas
	from utils.mathematical import df_count
	from utils.charts import radar_chart, box_whisker
	
	"""Chart Data"""
	chart_data = pandas.concat(
		[pandas.read_csv(os.path.join(CSV_DIRECTORY, "{}_CHART_DATA.csv".format(sample)),
						 sep=";", index_col=0) for sample in projectList
		 ], axis=1, sort=False)
	
	chart_data.drop("Compound Names", axis=1, inplace=True)
	
	# determine order of compounds on graph
	for compound in chart_data.index.values:
		chart_data["Count"] = chart_data.apply(df_count, args=(
			[f"{sample} Peak Area" for sample in projectList],),
											   axis=1)
	
	chart_data['Compound Names'] = chart_data.index
	chart_data = chart_data.sort_values(['Count', 'Compound Names'])
	chart_data.fillna(0, inplace=True)
	
	radar_chart(chart_data, projectList, use_log=10)
	
	sample_list = []
	
	for project in projectList:
		with open(os.path.join(RESULTS_DIRECTORY, f"{project}.info"), "r") as info_file:
			sample_list.append((project, [x.rstrip("\r\n") for x in info_file.readlines()]))
	print(sample_list)
	
	box_whisker(chart_data, sample_list,
				groupings=(groupings))

def make_archive(comparison_name, left_sample, left_prefixList, right_sample, right_prefixList):
	"""Make Single Tarball Containing All Files"""
	import tarfile
	import datetime
	
	tar = tarfile.open(os.path.join(RESULTS_DIRECTORY, (
			comparison_name + "_COMPARISON_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S") + '.tar.gz')), mode='w:gz')
	
	for sample in [left_sample, right_sample]:
		tar.add(os.path.join(RESULTS_DIRECTORY, sample + "_FINAL.xlsx"), arcname=(sample + ".xlsx"))
		tar.add(os.path.join(CHARTS_DIRECTORY, sample), arcname=f'Charts/{sample}')
		tar.add(os.path.join(SPECTRA_DIRECTORY, sample), arcname=f'Spectra/{sample}')
	
		tar.add(os.path.join(CSV_DIRECTORY, sample + "_MERGED.csv"), arcname=sample+'_Merged.CSV')
		tar.add(os.path.join(CSV_DIRECTORY, sample + "_MATCHES.csv"), arcname=sample+'_Matches.CSV')
		tar.add(os.path.join(CSV_DIRECTORY, "{}_STATISTICS_FULL.csv".format(sample)),
				arcname=f'Statistics/{sample}_Statistics_Full.CSV')
		tar.add(os.path.join(CSV_DIRECTORY, "{}_STATISTICS.csv".format(sample)), arcname=f'Statistics/{sample}_Statistics.CSV')
		tar.add(os.path.join(CSV_DIRECTORY, "{}_STATISTICS_LIT.csv".format(sample)),
				arcname=f'Statistics/{sample}_Statistics_Lit.CSV')
		tar.add(os.path.join(CSV_DIRECTORY, "{}_peak_data.json".format(sample)), arcname=f"{sample}_Peak_Data.json")
		tar.add(os.path.join(RESULTS_DIRECTORY, f"{sample}.info"), arcname=f"{sample}.info")
	
	for prefix in left_prefixList+right_prefixList:
		tar.add(os.path.join(EXPERIMENTS_DIRECTORY, "{}_tic.dat".format(prefix)),
				arcname="Experiments/{}_tic.dat".format(prefix))
		tar.add(os.path.join(EXPERIMENTS_DIRECTORY, "{}_peaks.dat".format(prefix)),
				arcname="Experiments/{}_peaks.dat".format(prefix))
		tar.add(os.path.join(EXPERIMENTS_DIRECTORY, "{}.expr".format(prefix)),
				arcname="Experiments/{}_expr.dat".format(prefix))
		
		tar.add(os.path.join(CSV_DIRECTORY, "{}_COMBINED.csv".format(prefix)),
				arcname="Combined/{}.CSV".format(prefix))
	
	tar.add(os.path.join(RESULTS_DIRECTORY, f"{comparison_name}_COMPARISON.CSV"), arcname="Comparison.CSV")
	tar.add(os.path.join(RESULTS_DIRECTORY, f"{comparison_name}_COMPARISON.xlsx"), arcname="Comparison.xlsx")
	tar.add(os.path.join(CHARTS_DIRECTORY, "Comparison"), arcname='Charts/Comparison')
	
	print(f"\nSaved as: {os.path.join(RESULTS_DIRECTORY, comparison_name + '_COMPARISON.xlsx')}")

def arguments():
	# Command line switches
	import argparse
	parser = argparse.ArgumentParser()
	
	parser.add_argument("-p", "--projects", help="List of projects to compare.", nargs='+', required=True)
	parser.add_argument("-g", "--groups", help="List of groups for comparison chart.", nargs='+')
	parser.add_argument("--info", help="Show program info.", action='store_true')
	
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		print("No options supplied.")
		print('')
		parser.print_help(sys.stderr)
		sys.exit(1)
	
	return args

if __name__ == '__main__':

	import platform
	from utils import timing
	from utils.paths import maybe_make

	
	clear()  # clear the display
	startup_string = f"\n\n{program_name} Version {__version__} running on {platform.system()}.\nCopyright {copyright} Dominic Davis-Foster."
	print(startup_string)
	
	# Load Configuration
	config = GSMConfig("config.ini")
	msp_directory = config.MSP_DIRECTORY
	MSP_DIRECTORY = config.MSP_DIRECTORY
	EXPERIMENTS_DIRECTORY = config.EXPERIMENTS_DIRECTORY
	RESULTS_DIRECTORY = config.RESULTS_DIRECTORY
	CSV_DIRECTORY = config.CSV_DIRECTORY
	SPECTRA_DIRECTORY = config.SPECTRA_DIRECTORY
	CHARTS_DIRECTORY = config.CHARTS_DIRECTORY
	
	# within replicates alignment parameters
	Dw = config.rt_modulation  # [s]
	Gw = config.gap_penalty
	min_peaks = config.min_peaks
	
	#args = arguments()
	
	#projectList = args.projects
	projectList = ["Eley Contact", "Geco Rifle"]
	#projectList = ["Eley Contact", "Eley Contact Fired", "Geco Rifle", "Geco Rifle Fired"]
	
	#if args.groups:
	#	groupings = args.groups
	#else:
	groupings = projectList[::2]
	
	br()
	
	if len(projectList) < 2:
		print("Error: Require Two or More Projects to Compare")
		sys.exit(1)
	
	elif len(projectList) == 2:
		"""Two Samples Comparison"""
		comparison(*projectList)
	
	else:
		"""All Samples Comparison (Charts Only)"""
		multiple_project_charts(projectList)

	"""Charts"""
	"""print("\nGenerating Charts")
	maybe_make(os.path.join(CHARTS_DIRECTORY, "+".join(projectList)+"COMPARISON"))
	

	
	radar_chart(chart_data, [lot_name], use_log=10,
				mode=os.path.join(CHARTS_DIRECTORY, lot_name, "radar_log10_peak_area"))
	radar_chart(chart_data, [lot_name], use_log=False,
				mode=os.path.join(CHARTS_DIRECTORY, lot_name, "radar_peak_area"))
	mean_peak_area_multiple(chart_data, [lot_name],
							mode=os.path.join(CHARTS_DIRECTORY, lot_name, "mean_peak_area"))
	peak_area(chart_data, prefixList, use_log=10,
			  mode=os.path.join(CHARTS_DIRECTORY, lot_name, "log10_peak_area_percentage"))
	
	with open(os.path.join(RESULTS_DIRECTORY, f"{lot_name}.info"), "w") as info_file:
		for prefix in prefixList:
			info_file.write(f"{prefix}\n")"""
	
	
	print("\nComplete.")
	
	COV.stop()
	COV.save()
	print("\nCoverage Summary:")
	COV.report()
	basedir = os.path.join(os.path.dirname(__file__))
	covdir = os.path.join(basedir, "coverage")
	COV.html_report(directory=covdir)
	print("HTML version: file://%s/index.html" % covdir)
	COV.erase()




