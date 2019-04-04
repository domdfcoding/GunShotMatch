#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Charts.py
#  
#  Copyright 2019 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  mean_peak_area, mean_peak_area_multiple and peak_area adapted from
#  		https://python-graph-gallery.com/13-percent-stacked-barplot/
#		Copyright (C) 2017 The python graph gallery
#
#  radar_chart adapted from
#  		https://python-graph-gallery.com/391-radar-chart-with-several-individuals/
#		Copyright (C) 2017 The python graph gallery
#
#	PlotSpectrum adapted from SpectrumSimilarity.R
# 		Part of OrgMassSpecR
# 		Copyright Nathan Dodder <nathand@sccwrp.org>
#
#	PrincipalCOmponentAnalysis based on
#		https://towardsdatascience.com/pca-using-python-scikit-learn-e653f8989e60
#		Copyright 2017 Michael Galarnyk
#
#	box_whisker based on https://stackoverflow.com/a/48192246/3092681
#		Copyright 2018 DavidG
#		Available under the MIT License
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
# adapted
# https://matplotlib.org/tutorials/intermediate/legend_guide.html
# https://matplotlib.org/devdocs/gallery/text_labels_and_annotations/custom_legends.html
#

# Imports

import matplotlib
from matplotlib import pyplot as plt

default_colours = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
default_filetypes = ["png", "pdf", "svg"]
bw_default_styles = ["D",  # diamond
			  		 "s",  # square
			  		 "X",  # bold cross
			  		 "^",  # triangle
			  		 "d",  # diamond
			  		 "h",  # hexagon
			  		 "o",  # dot
			  		 "v",  # down triangle
			  		 "<",  # left triangle
			  		 ">",  # right triangle
					 ]
bw_default_colours_a = ["DarkRed",
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
						]

bw_default_colours_b = ["PaleVioletRed",
						"DeepSkyBlue",
						"y",
						"Green",
						"OrangeRed",
						"MediumTurquoise",
						"m",
						"Red",
						"Olive",
						"CadetBlue",
						"Sienna",
						"Purple",
						"Blue",
						"DarkRed",
						"DarkSlateBlue",
						"DarkOliveGreen",
						"RoyalBlue",
						"Black",
						"Teal",
						]

bw_default_colours = bw_default_colours_b[:]


class chart():
	def __init__(self):
		pass
	
	def save_chart(self, filepath, filetypes=default_filetypes):
		matplotlib.use("Agg")
		for filetype in filetypes:
			plt.savefig(filepath + ".{}".format(filetype))
		plt.close()
	
	def show_chart(self):
		matplotlib.use("TkAgg")
		plt.show()
		plt.close()


class box_whisker(chart):
	def __init__(self):
		"""\
		err_bar options: range, stdev
		outlier_mode options: mad,2stdev,quartile
		leg_cols: Number of columns for legend
		"""
		
		self.x_tick_positions = []
		self.all_values = []
	
	def setup_data(self, peak_areas, sample_list, outlier_mode="2stdev"):
		from utils.mathematical import df_data_points, df_count, df_mean, df_stdev, df_median, df_outliers, remove_zero
		
		# determine order of compounds on graph
		for compound in peak_areas.index.values:
			# print([sample for sample in sample_list])
			peak_areas["Count"] = peak_areas.apply(df_count,
												   args=([f"{sample[0]} Peak Area" for sample in sample_list],), axis=1)
		
		peak_areas['Compound Names'] = peak_areas.index
		peak_areas = peak_areas.sort_values(['Count', 'Compound Names'])
		# print(peak_areas)
		
		for sample in sample_list:
			# print(sample[0])
			# print(sample[1])
			# print("\n")
			
			# Put all data points in one list
			peak_areas[f"{sample[0]} Data Points"] = peak_areas.apply(df_data_points,
																	  args=(sample[1],),
																	  axis=1)
			
			# Calculate y-axis limits
			data_points = ([item for sublist in peak_areas[f"{sample[0]} Data Points"] for item in sublist])
			self.all_values.append(max(data_points))
			self.all_values.append(min(remove_zero(data_points)))
			
			# Determine Outliers
			# Based on https://stackoverflow.com/a/52564783/3092681
			outlier_data = peak_areas.apply(lambda row: df_outliers(row[f"{sample[0]} Data Points"], outlier_mode),axis=1)
			peak_areas[f"{sample[0]} Outliers"] = outlier_data[0]
			peak_areas[f"{sample[0]} Data Excluding Outliers"] = outlier_data[1]

			# Calculate Mean, Median and Standard Deviation from Data Excluding Outliers
			peak_areas[f"{sample[0]} Mean Excluding Outliers"] = peak_areas.apply(df_mean,
																				  args=(f"{sample[0]} Data Excluding Outliers",),
																				  axis=1)
			peak_areas[f"{sample[0]} Median Excluding Outliers"] = peak_areas.apply(df_median,
																					args=(f"{sample[0]} Data Excluding Outliers",),
																					axis=1)
			peak_areas[f"{sample[0]} Stdev Excluding Outliers"] = peak_areas.apply(df_stdev,
																				   args=(f"{sample[0]} Data Excluding Outliers",),axis=1)
		
		self.peak_areas = peak_areas
		self.sample_list = sample_list
		self.outlier_mode = outlier_mode
	
	def setup_subplots(self, figsize=None):
		if figsize == None:
			figsize = (1 + (3 * len(self.sample_list)), 9)
		
		self.fig, self.ax = plt.subplots(figsize=figsize)
	
	def setup_datapoints(self, column_width=4, styles=bw_default_styles, colours=bw_default_colours):
		import numpy as np
		print(f"######{column_width}#####")
		self.datapoint_spacing = column_width / (len(self.peak_areas) + 1)
		
		self.datapoint_offset = list(np.arange((0 - (column_width / 2)) + self.datapoint_spacing,
											   (0 + (column_width / 2)),
											   self.datapoint_spacing
											   ))
		
		if len(colours) % len(styles) == 0:
			colours = colours[:-1]
		
		self.colours = colours
		self.column_width = column_width
		self.styles = styles
	
	def create_chart(self, show_outliers=True, show_raw_data=False, err_bar="range", groupings=None):
		import numpy as np
		from copy import deepcopy
		from itertools import cycle
		import matplotlib.ticker as ticker
		import matplotlib.transforms as transforms
		from utils.mathematical import magnitude
		
		self.ax.set_yscale('log')  # logarithmic scale on y-axis
		y_max = max(self.all_values) + (10 ** magnitude(max(self.all_values)))
		y_min = min(self.all_values) - (10 ** magnitude(min(self.all_values)))
		
		self.ax.set_ylim(y_min, y_max)
		
		x_pos = deepcopy(self.column_width)
		
		# Plot points on graph
		for sample in self.sample_list:
			colour_cycle = cycle(self.colours)
			style_cycle = cycle(self.styles)
			offset_cycle = cycle(self.datapoint_offset)
			
			compounds_added = []  # Fix for multiple peaks for same compound
			
			for compound in self.peak_areas.index.values:
				if compound in compounds_added:
					pass
				else:
					compounds_added.append(compound)
					
					offset_x_pos = x_pos + next(offset_cycle)
					colour = next(colour_cycle)
					marker = next(style_cycle)
					
					if show_outliers:
						mean = self.peak_areas.loc[compound, f"{sample[0]} Mean Excluding Outliers"]
						stdev = self.peak_areas.loc[compound, f"{sample[0]} Stdev Excluding Outliers"]
						outliers = self.peak_areas.loc[compound, f"{sample[0]} Outliers"]
						min_value = mean - min(self.peak_areas.loc[compound, f"{sample[0]} Data Excluding Outliers"])
						max_value = max(self.peak_areas.loc[compound, f"{sample[0]} Data Excluding Outliers"]) - mean
						range_values = np.array([[min_value], [max_value]])
						
						# Mean
						self.ax.scatter(offset_x_pos, mean, color=colour, marker=marker, label=compound)
						
						if err_bar == "stdev":
							self.ax.errorbar(offset_x_pos, mean, yerr=stdev, linestyle="None", color=colour, capsize=3)
						elif err_bar == "range":
							self.ax.errorbar(offset_x_pos, mean, yerr=range_values, linestyle="None", color=colour,
											 capsize=3)
						
						# plot outliers
						for outlier in outliers:
							self.ax.scatter(offset_x_pos, outlier, color="k", marker="x", label='')
						
						# plot raw data
						if show_raw_data:
							for area in self.peak_areas.loc[compound, f"{sample[0]} Mean Excluding Outliers"]:
								self.ax.scatter(offset_x_pos, area, color="grey", marker="x", label='', alpha=0.3)
					
					else:
						mean = self.peak_areas.loc[compound, f"{sample[0]} Peak Area"]
						stdev = self.peak_areas.loc[compound, f"{sample[0]} Standard Deviation"]
						min_value = mean - min(self.peak_areas.loc[compound, f"{sample[0]} Peak Area"])
						max_value = max(self.peak_areas.loc[compound, f"{sample[0]} Peak Area"]) - mean
						range_values = np.array([[min_value], [max_value]])
						
						# Mean
						self.ax.scatter(offset_x_pos, mean, color=colour, marker=marker, label=compound)
						
						if err_bar == "stdev":
							self.ax.errorbar(offset_x_pos, mean, yerr=stdev, linestyle="None", color=colour, capsize=3)
						elif err_bar == "range":
							self.ax.errorbar(offset_x_pos, mean, yerr=range_values, linestyle="None", color=colour,
											 capsize=3)
						
						# plot raw data
						if show_raw_data:
							for area in self.peak_areas.loc[compound, f"{sample[0]} Peak Area"]:
								self.ax.scatter(offset_x_pos, area, color="grey", marker="x", label='', alpha=0.3)
			
			x_pos += self.column_width
		
		IDs = [x[0] for x in self.sample_list]
		
		# gridlines and labels
		self.ax.grid(b=True, axis="y", which='major', color='b', linestyle='-')
		self.ax.grid(b=True, axis="y", which='minor', color='r', alpha=0.3, linestyle='--')
		self.ax.grid(axis="x", which='major', linestyle='-')
		
		x_vals = list(
			np.arange(self.column_width, (self.column_width * (len(self.sample_list) + 1)), self.column_width))
		x_vals = np.array(x_vals)
		
		# Thin Vertical Lines Between Samples
		minor_x_vals = []
		for x in x_vals:
			minor_x_vals.append(x - (self.column_width / 2))
		minor_x_vals.append(max(minor_x_vals) + (self.column_width) - (0.025 if groupings else 0.03))
		minor_x_vals = np.array([minor_x_vals[0] + 0.05] + minor_x_vals[1:])
		
		self.ax.set_xticks(minor_x_vals)
		self.ax.set_xticklabels(IDs)  # , size='small')  # ,ha='left')
		self.ax.xaxis.set_major_formatter(ticker.NullFormatter())
		
		# Sample Labels
		self.ax.xaxis.set_minor_locator(ticker.FixedLocator(x_vals))
		
		if groupings:
			self.ax.xaxis.set_minor_formatter(
				ticker.FixedFormatter(["Unfired\nPropellant", "Fired\nCartridge Case"] * (len(self.sample_list) // 2)))
			
			# Labels at Top for Groupings
			print(x_vals)
			# top_vals = numpy.array([x-0.005 for x in x_vals[::2]])
			top_vals = np.array(x_vals[::2])
			print(top_vals)
			min_top_vals = np.array(x_vals[1::2])
			print(min_top_vals)
			
			# Thick Vertical Lines Between Groups
			print(minor_x_vals)
			print(minor_x_vals[::2])
			
			for minor_x_val in minor_x_vals[::2]:
				self.ax.axvline(x=minor_x_val, ymax=1.02, color="black", clip_on=False)
			
			print(groupings)
			for group, minor_x_val in zip(groupings, minor_x_vals[1::2]):
				print(group, minor_x_val)
				# print(ax.transAxes.inverted().transform((0,1)))
				# plt.text(minor_x_val, 1.01, group, horizontalalignment="center",transform=transforms.blended_transform_factory(ax.transData, ax.transAxes))
				self.ax.text(minor_x_val, 1.01, group, horizontalalignment="center",
							 transform=transforms.blended_transform_factory(self.ax.transData, self.ax.transAxes))
			
			# plt.title("Ammunition", fontsize=12, y=1.03)
			self.fig.title("Ammunition", fontsize=12, y=1.03)
		
		else:
			self.ax.xaxis.set_minor_formatter(ticker.FixedFormatter(IDs))
			self.ax.set_xlabel('Ammunition', fontsize=12, labelpad=10)
		
		self.ax.set_ylabel('Peak Area', fontsize=12)
		
		# x-axis limits
		self.ax.set_xlim(left=(self.column_width / 2), right=(x_vals[-1] + (self.column_width / 2)))
		self.ax.set_axisbelow(True)
		
		self.show_outliers = show_outliers
		self.show_raw_data = show_raw_data
		self.err_bar = err_bar
	
	def create_legend(self, leg_cols=1):
		from itertools import cycle
		from matplotlib.lines import Line2D
		
		legend_elements = []
		
		colour_cycle = cycle(self.colours)
		style_cycle = cycle(self.styles)
		for compound in self.peak_areas.index.values:
			colour = next(colour_cycle)
			marker = next(style_cycle)
			legend_elements.append(Line2D([0], [0], marker=marker, color='w', label=compound,
										  markerfacecolor=colour, markersize=10, linestyle="None"))
		
		if self.show_outliers:
			legend_elements.append(Line2D([0], [0], marker="x", color="k", label="Outlier",
										  markerfacecolor="k", markersize=10, linestyle="None"))
		if self.show_raw_data:
			legend_elements.append(Line2D([0], [0], marker="x", color="k", label="Raw Data",
										  markerfacecolor="grey", alpha=0.3, markersize=10, linestyle="None"))
		if self.err_bar == "stdev":
			legend_elements.append(Line2D([0], [0], marker=None, color=None, label="Error Bars Indicate ± σ",
										  markerfacecolor=None, alpha=0, markersize=0, linestyle="None"))
		elif self.err_bar == "range":
			legend_elements.append(Line2D([0], [0], marker=None, color=None, label="Error Bars Indicate Range",
										  markerfacecolor=None, alpha=0, markersize=0, linestyle="None"))
		
		fig, ax = plt.subplots(figsize=(4 * leg_cols, 1 + (0.5 * len(self.peak_areas))))
		plt.clf()
		plt.axis('off')
		# fig.set_size_inches(4, 4)
		plt.legend(handles=legend_elements, loc="center", scatterpoints=1, ncol=leg_cols, title="Legend")
		fig.tight_layout()
	
	def save_chart(self, filepath, filetypes=default_filetypes):
		matplotlib.use("Agg")
		plt.tight_layout()
		for filetype in filetypes:
			plt.savefig(f"{filepath}_CHART.{filetype}")
		plt.close()
	
	def save_legend(self, filepath, filetypes=default_filetypes):
		matplotlib.use("Agg")
		for filetype in filetypes:
			plt.savefig(f"{filepath}_LEGEND.{filetype}")
		plt.close()
	


class mean_peak_area(chart):
	def setup_data(self, peak_areas, sample_list):
		from utils.mathematical import df_percentage
		
		
		# From raw value to percentage
		for sample_idx, sample in enumerate(sample_list):
			peak_areas["{} Percentage Peak Area".format(sample)] = peak_areas.apply(df_percentage,
				args=((peak_areas["{} Peak Area".format(sample)].sum()), "{} Peak Area".format(sample)),axis=1)
			peak_areas["{} Percentage Standard Deviation".format(sample)] = peak_areas.apply(
				df_percentage,args=((peak_areas["{} Standard Deviation".format(sample)].sum()), "{} Standard Deviation".format(sample)),axis=1)
			
				
		self.peak_areas = peak_areas
		self.sample_list = sample_list
		
	def setup_subplots(self, figsize=None):
		if figsize == None:
			figsize = (1 + (3 * len(self.sample_list)), 9)
		self.fig, self.ax = plt.subplots(figsize=figsize)

	def create_chart(self, barWidth=2, percentage=False, colours=default_colours, legend=True):
		import numpy as np
		import pandas as pd
		from itertools import cycle
		from matplotlib.patches import Patch
		
		# plot settings
		err_bar_spacing = barWidth / (len(self.peak_areas) + 1)
		print(err_bar_spacing)
		
		self.ax.grid(axis="y", linestyle='--', zorder=0)
		
		x_tick_positions = []
		
		bar_position = 0
		error_bar_offset = list(np.arange((bar_position - (barWidth / 2)) + err_bar_spacing,
										  (bar_position + (barWidth / 2)),
										  err_bar_spacing
										  ))[:len(self.peak_areas)]
		
		for sample_idx, sample in enumerate(self.sample_list):
			colour_cycle = cycle(colours)
			
			self.peak_areas["{} Error Bar Offset".format(sample)] = pd.Series([x + bar_position for x in error_bar_offset],
																		 index=self.peak_areas.index)
			bottom = 0
			for row_idx, row in self.peak_areas.iterrows():
				peak_area = row["{} {}Peak Area".format(sample, "Percentage " if percentage else '')]
				standard_deviation = row["{} {}Standard Deviation".format(sample, "Percentage " if percentage else '')]
				
				plt.bar(bar_position, peak_area, bottom=bottom, color=next(colour_cycle),
						width=barWidth, label=row["Compound Names"], zorder=3)
				
				plt.plot((row["{} Error Bar Offset".format(sample)], row["{} Error Bar Offset".format(sample)]),
						 ((bottom + peak_area) - standard_deviation,
						  (bottom + peak_area) + standard_deviation),
						 "black", zorder=3)
				
				bottom += peak_area
			
			x_tick_positions.append(bar_position)
			bar_position += barWidth + 0.1
		
		# Custom x axis
		self.ax.set_xticks(x_tick_positions)
		self.ax.set_xticklabels(self.sample_list)
		self.ax.set_xlabel("Sample Name")
		
	#	if percentage:
	#		vals = self.ax.get_yticks()
		# ax.set_yticklabels(['{:.0%}'.format(y/100) for y in vals])
		
		self.ax.set_ylabel("Peak Area{}".format(" (%)" if percentage else '', ))
		
		if legend:  # Add a legend
			legend_elements = []
			colour_cycle = cycle(colours)
			
			for row_idx, row in self.peak_areas.iterrows():
				legend_colour = next(colour_cycle)
				legend_elements.append(
					Patch(facecolor=legend_colour, edgecolor=legend_colour, label=row["Compound Names"]))
			
			self.ax.legend(handles=legend_elements[::-1], loc=9, bbox_to_anchor=(0.5, -0.06), ncol=1)
		

		


class peak_area(chart):
	def setup_data(self, peak_areas, lot_name, prefixList, use_log=False):

		from utils.mathematical import df_percentage, df_log
		
		if not prefixList:
			prefixList = list(peak_areas.columns.values)[1:]
		
		for prefix in prefixList:
			peak_areas["Percentage {}".format(prefix)] = peak_areas.apply(df_percentage,
																		  args=((peak_areas[prefix].sum()), prefix),
																		  axis=1)
			if use_log:
				peak_areas["Log {}".format(prefix)] = peak_areas.apply(df_log, args=(use_log, prefix), axis=1)
				peak_areas["Log Percentage {}".format(prefix)] = peak_areas.apply(df_percentage, args=(
					(peak_areas["Log {}".format(prefix)].sum()), "Log {}".format(prefix)), axis=1)
		
		self.peak_areas = peak_areas
		self.prefixList = prefixList
		self.use_log=use_log
		self.lot_name = lot_name
	
	def setup_subplots(self, figsize=(12,6)):
		self.fig, self.ax = plt.subplots(figsize=figsize)
	
	def create_chart(self, barWidth=2, percentage=False, colours=default_colours, legend=(0.5, -0.15)):
		from operator import add
		from itertools import cycle
		from matplotlib.patches import Patch
		
		colour_cycle = cycle(colours)
		x_vals = [x for x in range(len(self.prefixList))]
		bottom = [0] * len(self.prefixList)
		
		self.ax.grid(axis="y", linestyle='--', zorder=0)
		
		for index, row in self.peak_areas.iterrows():
			peak_area = []
			for prefix in self.prefixList:
				peak_area.append(
					row["{}{}{}".format("Log " if self.use_log else '', "Percentage " if percentage else '', prefix)])
			
			self.ax.bar(x_vals, peak_area, bottom=bottom, color=next(colour_cycle),
					width=barWidth, label=row["Compound Names"], zorder=3)
			
			bottom = list(map(add, bottom, peak_area))
		
		# Custom x axis
		self.ax.set_xticks(x_vals)
		self.ax.set_xticklabels(self.prefixList)
		self.ax.set_xlabel("Sample", labelpad=10)
		self.ax.set_title(self.lot_name, y=1.03)
		
		if percentage:
			self.ax.set_ylim(0, 100)
	#		vals = self.ax.get_yticks()
		# ax.set_yticklabels(['{:.0%}'.format(y/100) for y in vals])
		
		self.ax.set_ylabel(r"{}{}".format(log_string("Peak Area", self.use_log)," (%)" if percentage else ''))
		
		if legend:  # Add a legend
			legend_elements = []
			colour_cycle = cycle(colours)
			
			for row_idx, row in self.peak_areas.iterrows():
				legend_colour = next(colour_cycle)
				legend_elements.append(
					Patch(facecolor=legend_colour, edgecolor=legend_colour, label=row["Compound Names"]))
			print(legend)
			self.ax.legend(handles=legend_elements[::-1], bbox_to_anchor=legend, ncol=1)
			
			

		
		# plt.legend(loc='upper left', bbox_to_anchor=(1,1), ncol=1)
		

	

class radar_chart(chart):
	def setup_data(self, peak_areas, sample_list):
		self.sample_list = sample_list
		self.peak_areas = peak_areas
	
	def setup_subplots(self, figsize=(10, 10)):
		# Initialise the spider plot
		self.fig = plt.figure(figsize=figsize)
		self.ax = self.fig.add_subplot(111, polar=True)
	
	def create_chart(self, use_log=False, legend=True, colours=default_colours):
		from itertools import cycle
		from math import pi, log
		
		colour_cycle = cycle(colours)
		
		# If you want the first axis to be on top:
		self.ax.set_theta_offset(pi / 2)
		self.ax.set_theta_direction(-1)
		
		# number of variables
		compounds = self.peak_areas["Compound Names"]
		N_compounds = len(compounds)
		
		# What will be the angle of each axis in the plot? (we divide the plot / number of variable)
		angles = [n / float(N_compounds) * 2 * pi for n in range(N_compounds)]
		angles += angles[:1]
		
		# Draw one axe per variable + add labels labels yet
		self.ax.set_xticks(angles[:-1])
		#self.ax.set_xticklabels(compounds)
		
		# Axis Label Alignment
		ticklabels = self.ax.get_xticklabels()
		for tick, angle in zip(ticklabels, angles[:-1]):
			# angle in radians
			if angle == 0.0:
				tick.set_ha("center")
			elif angle > pi:
				tick.set_ha("right")
			elif angle < pi:
				tick.set_ha("left")
			elif angle == pi:
				tick.set_ha("center")
		
		# Draw ylabels
		self.ax.set_rlabel_position(0)
		# plt.yticks([10,20,30], ["10","20","30"], color="grey", size=7)
		
		datapoints = []
		
		# Plot each individual = each line of the data
		for sample in self.sample_list:
			if use_log:
				values = [log(area, use_log) if area > 0.0 else 0 for area in
						  self.peak_areas["{} Peak Area".format(sample)]]
			else:
				values = [area for area in self.peak_areas["{} Peak Area".format(sample)]]
			values += values[:1]
			colour = next(colour_cycle)
			self.ax.plot(angles, values, linewidth=1, color=colour, linestyle='solid', label=sample)
			self.ax.fill(angles, values, color=colour, alpha=0.1)
			datapoints.append(values)
		
		# plt.ylim(min([item for sublist in datapoints for item in sublist]),max([item for sublist in datapoints for item in sublist]))
		
		if legend:
			# Add legend
			self.fig.legend(loc='upper right', bbox_to_anchor=(0.15, 0.07))
		
		self.ax.set_title(r"{}".format(log_string("Peak Area", use_log)), y=1.06)


	


def PlotSpectrum(spec, label=None, xlim=(50, 1200), mode="display", color="red", filetypes=default_filetypes):
	"""
	Parameters:
	top (numpy.array): Array containing the experimental spectrum's peak list with the m/z values in the first column and corresponding intensities in the second
	label (str): string to label the spectrum.
	xlim (tuple of ints): tuple of length 2, defining the beginning and ending values of the x-axis.
	mode (str): "display" to show the spectrum; otherwise the directory to save the spectrum in
	filetypes (list of strings): Filetypes to save spectrum as
	"""
	
	import os
	from utils.SpectrumSimilarity import normalize
	import pandas as pd
	
	if mode.lower() == "display":
		matplotlib.use("TkAgg")
	else:
		matplotlib.use("Agg")

	## format spectra and normalize intensitites
	tmp = pd.DataFrame(data = spec, columns = ["mz", "intensity"])
	tmp["normalized"] = tmp.apply(normalize, args=(max(tmp["intensity"]),),axis=1)
	tmp = tmp[tmp["mz"].between(xlim[0],xlim[1])]
	plot = tmp[["mz", "normalized"]].copy() # data frame for plotting spectrum
	plot.columns = ["mz", "intensity"]
	
	## generate plot
	fig, ax = plt.subplots(figsize=(8,4))
	ax.vlines(plot["mz"], 0, plot["intensity"], color=color)
	ax.set_ylim(0,110)
	ax.set_xlim(xlim[0], xlim[1])
	ax.set_ylabel("Intensity (%)")
	ax.set_xlabel("m/z", style="italic", family="serif")
	h_centre = xlim[0]+(xlim[1]-xlim[0])//2
	fig.tight_layout()

	plt.text(0.98, 0.92, label, horizontalalignment = "right", verticalalignment = "bottom", transform = ax.transAxes)
	if mode.lower() == "display":
		plt.show()
	else:
		for filetype in filetypes:
			plt.savefig(os.path.join(mode,"{}.{}".format(label, filetype)))
	
	return plt.close()


def peak_area_wrapper(peak_areas, lot_name, prefixList, percentage=True,
					  colours=default_colours, figsize=(12, 6), barWidth=0.85,
					  legend=(1,1), mode="display", filetypes=default_filetypes, use_log=False):
	chart = peak_area()
	chart.setup_data(peak_areas, lot_name, prefixList, use_log)
	chart.setup_subplots(figsize)
	chart.create_chart(barWidth, percentage, colours, legend)
	chart.fig.tight_layout()
	if mode.lower() == "display":
		chart.show_chart()
	else:
		chart.save_chart(mode, filetypes)


def mean_peak_area_wrapper(peak_areas, sample_list, percentage=False,
						   colours=default_colours, figsize=None, barWidth=2,
						   legend=True, mode="display", filetypes=default_filetypes):
	chart = mean_peak_area()
	chart.setup_data(peak_areas, sample_list)
	chart.setup_subplots(figsize)
	chart.create_chart(barWidth, percentage, colours, legend)
	chart.fig.tight_layout()
	if mode.lower() == "display":
		chart.show_chart()
	else:
		chart.save_chart(mode, filetypes)

def radar_chart_wrapper(peak_areas, sample_list,
				colours = default_colours, figsize=(10,10),
				legend=True, mode = "display",
				filetypes = default_filetypes, use_log = False):
	
	chart = radar_chart()
	chart.setup_data(peak_areas, sample_list)
	chart.setup_subplots(figsize)
	chart.create_chart(use_log, legend, colours)
	chart.fig.tight_layout()
	if mode == "display":
		chart.show_chart()
	else:
		chart.save_chart(mode, filetypes)

def log_string(inner_text, base):
	from math import e
	if base == e:
		return "log({})".format(inner_text)
	elif base:
		return "log$_{" + str(base) + "}$(" + str(inner_text) + ")"
	else:
		return inner_text

def box_whisker_wrapper(peak_areas, sample_list,
				show_outliers=True, show_raw_data=False,
				err_bar="range", outlier_mode="2stdev",
				leg_cols=1, mode="display",
				figsize=None, column_width=4,
				styles=bw_default_styles,
				colours=bw_default_colours,
				filetypes=default_filetypes,
				groupings=None, legend=True,
				):
	
	chart = box_whisker()
	chart.setup_data(peak_areas, sample_list, outlier_mode)
	chart.setup_subplots(figsize)
	chart.setup_datapoints(column_width, styles, colours)
	chart.create_chart(show_outliers, show_raw_data, err_bar, groupings)
	
	if mode == "display":
		chart.show_chart()
		if legend:
			chart.create_legend(leg_cols)
			chart.show_chart()
	else:
		chart.save_chart(mode, filetypes)
		if legend:
			chart.create_legend(leg_cols)
			chart.save_legend(mode, filetypes)
	


def PrincipalComponentAnalysis(data, features, targets, colours=default_colours, mode="display",
							   filetypes=default_filetypes, figsize=(8, 8)):
	
	import pandas as pd
	from itertools import cycle
	from sklearn.decomposition import PCA
	from sklearn.preprocessing import StandardScaler
	#from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
	
	
	colour_cycle = cycle(colours)
	
	if mode.lower() == "display":
		matplotlib.use("TkAgg")
	else:
		matplotlib.use("Agg")
	
	# Separating out the features
	x = data.loc[:, features].values
	# Separating out the target
	y = data.loc[:, ['target']].values
	# Standardizing the features
	x = StandardScaler().fit_transform(x)
	
	pca = PCA(n_components=2)
	principalComponents = pca.fit_transform(x)
	# principalComponents = pca.fit(x).transform(x) # how is this different?
	
	# Percentage of variance explained for each components
	print(f'\nExplained variance ratio (first two components): {pca.explained_variance_ratio_}')
	print("This is the percentage of variance explained by each of the two principal components.")
	
	principalDf = pd.DataFrame(data=principalComponents, columns=['principal component 1', 'principal component 2'])
	finalDf = pd.concat([principalDf, data[['target']]], axis=1)
	
	fig = plt.figure(figsize=figsize)
	ax = fig.add_subplot(1, 1, 1)
	ax.set_xlabel('Principal Component 1', fontsize=15)
	ax.set_ylabel('Principal Component 2', fontsize=15)
	ax.set_title('2 component PCA', fontsize=20)
	
	for target in targets:
		indicesToKeep = finalDf['target'] == target
		ax.scatter(finalDf.loc[indicesToKeep, 'principal component 1'],
				   finalDf.loc[indicesToKeep, 'principal component 2'],
				   c=next(colour_cycle), s=50, alpha=0.8, lw=2)
	
	ax.legend(targets, loc='best', shadow=False)
	ax.grid()
	ax.set_axisbelow(True)
	
	if mode.lower() == "display":
		plt.show()
	else:
		for filetype in filetypes:
			plt.savefig(mode + ".{}".format(filetype))
	
	plt.close()
	
	return pca.explained_variance_ratio_


if __name__ == "__main__":
	import pandas as pd
	
	chart_data = pd.read_csv("../Results/CSV/ELEY_SUBTRACT_CHART_DATA.csv", sep=";", index_col=0)
	
	samples_to_compare = [
		("Eley Contact", ["ELEY_1_SUBTRACT", "ELEY_2_SUBTRACT", "ELEY_3_SUBTRACT", "ELEY_4_SUBTRACT",
										  "ELEY_5_SUBTRACT"]),
		#	("ELEY_CASE_SUBTRACT","Eley Case"),
		#	("WINCHESTER_SUBTRACT","Winchester Pistol"),
		#	("WINCHESTER_CASE_SUBTRACT","Winchester Case"),
		#	("GECO_SUBTRACT","Geco"),
		#	("GECO_CASE_SUBTRACT","Geco Case"),
		#	("ELEY_SHOTGUN_SUBTRACT", "Eley Hawk"),
	]  # must be in order you want them on the graph
	
	box_whisker_wrapper(chart_data, samples_to_compare)
	
	
	
	exit()
	
	

	data = pd.DataFrame({"Compound":["Diphenylamine", "Ethyl Centralite", "1,2-benzenedicarbonitrile", "Quinoline", "Naphthalene"],
								"ELEY_SUBTRACT Peak Area": [260511.3, 41310.2,39843.5,143740.0,1145116.7,],"ELEY_SUBTRACT Standard Deviation": [185532.9, 27770.7,22458.0,81281.1,437638.9,],
								"MAGTECH_SUBTRACT Peak Area": [260511.3, 41310.2,39843.5,143740.0,1145116.7,],"MAGTECH_SUBTRACT Standard Deviation": [185532.9, 27770.7,22458.0,81281.1,437638.9,],
								"CBC_SUBTRACT Peak Area": [143740.0,1145116.7,260511.3, 41310.2,39843.5],"CBC_SUBTRACT Standard Deviation": [185532.9, 27770.7,22458.0,81281.1,437638.9,]})
	
	radar_chart(data, ["ELEY_SUBTRACT","CBC_SUBTRACT"], use_log = 10)
	mean_peak_area_multiple(data, ["ELEY_SUBTRACT"])
	mean_peak_area_multiple(data, ["ELEY_SUBTRACT","MAGTECH_SUBTRACT","CBC_SUBTRACT"])
	
	peak_area(pd.DataFrame({"Compound":["Diphenylamine", "Ethyl Centralite", "1,2-benzenedicarbonitrile", "Quinoline", "Naphthalene"],
								"ELEY_1_SUBTRACT": [260511.3, 41310.2,49843.5,143740.0,1045116.7,],
								"ELEY_2_SUBTRACT": [280511.3, 31310.2,39843.5,143740.0,1145116.7,],
								"ELEY_3_SUBTRACT": [300511.3, 51310.2,30843.5,143740.0,1245116.7,],
								"ELEY_4_SUBTRACT": [200511.3, 45310.2,59843.5,143740.0,1345116.7,],
								"ELEY_5_SUBTRACT": [220511.3, 40310.2,32003.5,143740.0,1445116.7,]}),
			   percentage = False)
