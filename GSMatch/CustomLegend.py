#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  CustomLegend.py
"""Custom Legend for Box and Whisker Plot"""
#
#  Copyright 2018, 2019 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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

__author__ = "Dominic Davis-Foster"
__copyright__ = "Copyright 2018, 2019 Dominic Davis-Foster"

__license__ = "GPL"
__version__ = "0.5.0"
__email__ = "dominic@davis-foster.co.uk"

from utils.charts import bw_default_colours, bw_default_styles

def bw_custom_legend(legend_entries, styles=bw_default_styles, colours=bw_default_colours,
					 show_outliers=True, show_raw_data=False, leg_cols=1):
	
	import matplotlib
	matplotlib.use("TkAgg")
	import matplotlib.pyplot as plt
	from matplotlib.lines import Line2D
	from itertools import cycle
	
	if len(colours) % len(styles) == 0:
		colours = colours[:-1]
	
	legend_elements = []
	colour_cycle = cycle(colours)
	style_cycle = cycle(styles)
		
	for label in legend_entries:
		legend_elements.append(Line2D([0], [0], marker=next(style_cycle), color='w', label=label,
						  markerfacecolor=next(colour_cycle), markersize=10,linestyle="None"))
	if show_outliers:
		legend_elements.append(Line2D([0], [0], marker="x", color="k", label="Outlier\n>2σ from the mean",
						  markerfacecolor="k", markersize=10,linestyle="None"))
	if show_raw_data:
		legend_elements.append(Line2D([0], [0], marker="x", color="k", label="Raw Data",
						  markerfacecolor="grey", alpha=0.3, markersize=10,linestyle="None"))
	
	fig, ax = plt.subplots()
	plt.clf()
	plt.axis('off')
	plt.legend(handles=legend_elements, loc="center", scatterpoints=1,ncol=leg_cols,title="Legend")
	fig.tight_layout()
	plt.show()
			
if __name__ == '__main__':
	legend_entries = [
		"""Diphenylamine (DPA)""",
		"""Ethyl Centralite (EC)""",
		"""Naphthalene""",
		"""4-nitro-diphenylamine (4NDPA)""",
		"""N,N-diphenyl-Formamide""",
		"""Dibutyl phthalate (DBP)""",
		"""2-nitro-diphenylamine (2NDPA)""",
		"""1,2-Ethanediol, dinitrate
(possibly nitroglycerine)""",
		"""1,2-Benzenedicarbonitrile""",
		"""Quinoline""",
		"""2,4-Dinitrotoluene (DNT)""",
		"""2,6-Dinitrotoluene (2,6-DNT)""",
		"""Styrene""",
		"""2-methyl-Naphthalene""",
		"""1,3,5-trimethyl-Benzene""",
		"""p-Xylene""",
		]  # must be in order you want them on the legend
		
	bw_custom_legend(legend_entries, show_outliers=True, show_raw_data=False, leg_cols=2)
	# Number of columns for legend:
	# 2 for Landscape poster
	# 4 for Portrait poster
	
	# Note: Outlier has fixed text. Change this if using something other than 2stdev
