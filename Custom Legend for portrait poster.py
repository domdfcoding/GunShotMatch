#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  GSM_plot.py
program_name ="GunShotMatch Comparison Plot"
_version = '0.2'
copyright = 2018

#  Copyright 2018 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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

# adapted from https://stackoverflow.com/questions/48191792/scatter-plot-with-multiple-y-values-with-line-for-each-category-x-label
# https://matplotlib.org/tutorials/intermediate/legend_guide.html
# https://matplotlib.org/devdocs/gallery/text_labels_and_annotations/custom_legends.html

legend_entries = [
	"Diphenylamine (DPA)",
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
	] #must be in order you want them on the legend

show_outliers = True
show_raw_data = False
leg_cols = 4 # Number of columns for legend

from utils import timing # Times the program
import sys, os

from utils.helper import clear, check_dependencies
clear()		#clear the display

missing_modules = check_dependencies(["progressbar", "matplotlib"], prt=False)
if len(missing_modules) > 0:
	for mod in missing_modules:
		print("{} is not installed. Please install it and try again".format(mod))
		sys.exit(1)
		
import progressbar

print("""\r{0} Version {1} is loading. Please wait...
Copyright {2} Dominic Davis-Foster""".format(program_name,_version,copyright,))

"""Imports"""
if "-h" not in str(sys.argv):
	bar = progressbar.ProgressBar(max_value=10) #progressbar for imports

	import time ; time.sleep(0.1); bar.update(1)
	import warnings	; time.sleep(0.1); bar.update(2)
	import datetime	; time.sleep(0.1); bar.update(3)
	
	from utils.helper import entry, mean_none, std_none, copytree
	time.sleep(0.1); bar.update(4)
	from utils import load_config, within1min, outliers
	
	import matplotlib; matplotlib.use("TkAgg")
	time.sleep(0.1); bar.update(5)
	
	import matplotlib.pyplot as plt	; time.sleep(0.1); bar.update(6)
	import matplotlib.ticker as ticker; time.sleep(0.1); bar.update(7)
	
	from matplotlib.lines import Line2D; time.sleep(0.1); bar.update(8)
else:
	import warnings


"""From https://stackoverflow.com/questions/21129020/how-to-fix-unicodedecodeerror-ascii-codec-cant-decode-byte
Big shout out to fisherman https://stackoverflow.com/users/2309581/fisherman"""
reload(sys)  
sys.setdefaultencoding('utf8')
time.sleep(0.1); bar.update(9)


def comparison():
	
	styles = ["D", #diamond
	"s", #square
	"X", #bold cross
	"^", #triangle
	"d", #diamond
	"h", #hexagon
	"o", #dot
	"v", #down triangle
	"<", #left triangle
	">"] #right triangle
		
	#colours = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
	colours = [
		"PaleVioletRed",
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

	legend_elements = []
	
	while len(colours) < len(legend_entries):
		colours += colours
	while len(styles) < len(legend_entries):
		styles += styles

	colours = colours[:len(legend_entries)]
	styles = styles[:len(legend_entries)]
		
	for label, mark, colour in zip(legend_entries,styles, colours):

		legend_elements.append(Line2D([0], [0], marker=mark, color='w', label=label,
						  markerfacecolor=colour, markersize=10,linestyle="None"))
						  
	if show_outliers:
		#legend_elements.append(Line2D([0], [0], marker="x", color="k", label="Outlier",
		legend_elements.append(Line2D([0], [0], marker="x", color="k", label="Outlier\n>2σ from the mean",
						  markerfacecolor="k", markersize=10,linestyle="None"))
	if show_raw_data:
		legend_elements.append(Line2D([0], [0], marker="x", color="k", label="Raw Data",
						  markerfacecolor="grey", alpha=0.3, markersize=10,linestyle="None"))
	
	fig, ax = plt.subplots()
		
	plt.clf()
	plt.axis('off')	
	fig.set_size_inches(4,4)	
	plt.legend(handles=legend_elements, loc="center", scatterpoints=1,ncol=leg_cols,title="Legend")
	fig.tight_layout()    
	
#	plt.show()
	
	#save legend
	for file_format in ["pdf","png"]:
#	for file_format in ["pdf"]:
		plt.savefig("./charts/custom_legend_{}.{}".format(str(datetime.datetime.now())[:19].replace(":",""),file_format), format = file_format, dpi = 1200,bbox_inches="tight",transparent=True)

			
if __name__ == '__main__':
	"""from https://stackoverflow.com/questions/14463277/how-to-disable-python-warnings"""
	with warnings.catch_warnings():
		warnings.simplefilter("ignore")
		
		print("\nReady")
		comparison()	# Actual Comparison
		print("\nComplete.")
