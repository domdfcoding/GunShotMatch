#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright 2019 Dominic Davis-Foster
#
# Adapted from SpectrumSimilarity.R
# Part of OrgMassSpecR
# Copyright Nathan Dodder <nathand@sccwrp.org>

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import timing

def SpectrumSimilarity(spec_top, spec_bottom, t = 0.25, b = 10, top_label = None, 
                               bottom_label = None, xlim = (50, 1200), x_threshold = 0, print_alignment = False,
                               print_graphic = True, output_list = False):
	"""
	Parameters:
	spec_top (numpy.array): Array containing the experimental spectrum's peak list with the m/z values in the first column and corresponding intensities in the second
	spec_bottom	(numpy.array): Array containing the reference spectrum's peak list with the m/z values in the first column and corresponding intensities in the second
	t (float): numeric value specifying the tolerance used to align the m/z values of the two spectra.
	b (float): numeric value specifying the baseline threshold for peak identification. Expressed as a percent of the maximum intensity.
	top_label (str): string to label the top spectrum.
	bottom.label  (str): string to label the bottom spectrum.	
	xlim (tuple of ints): tuple of length 2, defining the beginning and ending values of the x-axis.
	x_threshold (float): numeric value specifying
	print_alignment (bool): whether the intensities should be printed
	print_graphic (bool):
	output_list (bool): whether the intensities should be returned
	"""
	## format spectra and normalize intensitites
	top_tmp = pd.DataFrame(data = spec_top, columns = ["mz", "intensity"])
	top_tmp["normalized"] = top_tmp.apply(normalize, args=(max(top_tmp["intensity"]),),axis=1)
	top_tmp = top_tmp[top_tmp["mz"].between(xlim[0],xlim[1])]
	top_plot = top_tmp[["mz", "normalized"]].copy() # data frame for plotting spectrum
	top_plot.columns = ["mz", "intensity"]
	top = top_plot[top_plot["intensity"] >= b] # data frame for similarity score calculation

	bottom_tmp = pd.DataFrame(data = spec_bottom, columns = ["mz", "intensity"])
	bottom_tmp["normalized"] = bottom_tmp.apply(normalize, args=(max(bottom_tmp["intensity"]),),axis=1)
	bottom_tmp = bottom_tmp[bottom_tmp["mz"].between(xlim[0],xlim[1])]
	bottom_plot = bottom_tmp[["mz", "normalized"]].copy() # data frame for plotting spectrum
	bottom_plot.columns = ["mz", "intensity"]
	bottom = bottom_plot[bottom_plot["intensity"] >= b] # data frame for similarity score calculation
	
	
	## align the m/z axis of the two spectra, the bottom spectrum is used as the reference
	
	#Unimplemented R code
	"""
	  for(i in 1:nrow(bottom))
		top["mz"][bottom["mz"][i] >= top["mz"] - t & bottom["mz"][i] <= top["mz"] + t] = bottom["mz"][i]
		top[,1][bottom[,1][i] >= top[,1] - t & bottom[,1][i] <= top[,1] + t] <- bottom[,1][i]
	  alignment <- merge(top, bottom, by = 1, all = TRUE)
	  if(length(unique(alignment[,1])) != length(alignment[,1])) warning("the m/z tolerance is set too high")
	alignment[,c(2,3)][is.na(alignment[,c(2,3)])] <- 0   # convert NAs to zero (R-Help, Sept. 15, 2004, John Fox)
	names(alignment) <- c("mz", "intensity.top", "intensity.bottom")
	"""
	alignment = pd.merge(top, bottom, on="mz", how="outer")
	alignment.fillna(value=0, inplace=True) # Convert NaN to 0
	alignment.columns=["mz", "intensity_top", "intensity_bottom"]
	if print_alignment:
		with pd.option_context('display.max_rows', None, 'display.max_columns', None):
			print(alignment)
	
	## similarity score calculation
	
	if x_threshold < 0:
		print("Error: x_threshold argument must be zero or a positive number")
		return 1
	
	
	#Unimplemented R code
	"""
	alignment <- alignment[alignment[,1] >= x.threshold, ]
	"""
	
	u = np.array(alignment.iloc[:,1])
	v = np.array(alignment.iloc[:,2])
	
	similarity_score = np.dot(u,v) / (np.sqrt(np.sum(np.square(u))) * np.sqrt(np.sum(np.square(v))))
	
	
	# Reverse Match
	reverse_alignment = pd.merge(top, bottom, on="mz", how="right")
	#reverse_alignment.fillna(value=0, inplace=True) # Convert NaN to 0
	reverse_alignment.columns=["mz", "intensity_top", "intensity_bottom"]
	u = np.array(reverse_alignment.iloc[:,1])
	v = np.array(reverse_alignment.iloc[:,2])
	
	reverse_similarity_score = np.dot(u,v) / (np.sqrt(np.sum(np.square(u))) * np.sqrt(np.sum(np.square(v))))
	
	## generate plot
	
	if print_graphic:
		fig, ax = plt.subplots()
		#fig.scatter(top_plot["mz"],top_plot["intensity"], s=0)
		ax.vlines(top_plot["mz"], 0, top_plot["intensity"], color="blue")
		ax.vlines(top_plot["mz"], 0, -top_plot["intensity"], color="red")
		ax.set_ylim(-125,125)
		ax.set_xlim(xlim[0], xlim[1])
		ax.axhline(color="black", linewidth=0.5)
		ax.set_ylabel("Intensity (%)")
		ax.set_xlabel("m/z", style="italic", family="serif")
		
		h_centre = xlim[0]+(xlim[1]-xlim[0])//2
		
		ax.text(h_centre, 110, top_label, horizontalalignment = "center", verticalalignment = "center")
		ax.text(h_centre, -110, bottom_label,horizontalalignment = "center", verticalalignment = "center")
		plt.show()
		
	#Unimplemented R code	
	"""   
		ticks <- c(-100, -50, 0, 50, 100)
		plot.window(xlim = c(0, 20), ylim = c(-10, 10))
	  
	  
	  if(output.list == TRUE) {
		
		# Grid graphics head to tail plot
		
		headTailPlot <- function() {
		  
		  pushViewport(plotViewport(c(5, 5, 2, 2)))
		  pushViewport(dataViewport(xscale = xlim, yscale = c(-125, 125)))
		  
		  grid.rect()
		  tmp <- pretty(xlim)
		  xlabels <- tmp[tmp >= xlim[1] & tmp <= xlim[2]]
		  grid.xaxis(at = xlabels)
		  grid.yaxis(at = c(-100, -50, 0, 50, 100))
		  
		  grid.segments(top_plot$mz,
						top_plot$intensity,
						top_plot$mz,
						rep(0, length(top_plot$intensity)),
						default.units = "native",
						gp = gpar(lwd = 0.75, col = "blue"))
		  
		  grid.segments(bottom_plot$mz,
						-bottom_plot$intensity,
						bottom_plot$mz,
						rep(0, length(bottom_plot$intensity)),
						default.units = "native",
						gp = gpar(lwd = 0.75, col = "red"))
		  
		  grid.abline(intercept = 0, slope = 0)
		  
		  grid.text("intensity (%)", x = unit(-3.5, "lines"), rot = 90)
		  grid.text("m/z", y = unit(-3.5, "lines"))
		  
		  popViewport(1)
		  pushViewport(dataViewport(xscale = c(0, 20), yscale = c(-10, 10)))
		  grid.text(top.label, unit(10, "native"), unit(9, "native"))
		  grid.text(bottom.label, unit(10, "native"), unit(-9, "native"))
		  
		  popViewport(2)
		  
		}
		
		p <- grid.grabExpr(headTailPlot())
		
	  }
	  
	  
	"""		
		
		
#	with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#		print(similarity_score)
		
	if output_list:
		return similarity_score, reverse_similarity_score, alignment
		# Unimplement R code
		"""
		return(list(similarity.score = similarity_score, 
			alignment = alignment,
			plot = p))
		"""
	else:
		return similarity_score, reverse_similarity_score

	# simscore <- as.vector((u %*% v)^2 / (sum(u^2) * sum(v^2)))   # cos squared

def normalize(row, max_val):
	#http://jonathansoma.com/lede/foundations/classes/pandas%20columns%20and%20functions/apply-a-function-to-every-row-in-a-pandas-dataframe/
	return (row["intensity"]/float(max_val))*100.0	


def chunks(l, n):
	#https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


def LibrarySearch(unknown, library_file_list, t = 0.25, b = 10, xlim = (50, 1200), x_threshold = 0):
	"""
	Parameters:
	unknown (numpy.array): Array containing the experimental spectrum's peak list with the m/z values in the first column and corresponding intensities in the second
	t (float): numeric value specifying the tolerance used to align the m/z values of the two spectra.
	b (float): numeric value specifying the baseline threshold for peak identification. Expressed as a percent of the maximum intensity.
	xlim (tuple of ints): tuple of length 2, defining the beginning and ending values of the x-axis.
	x_threshold (float): numeric value specifying
	"""
	
	match_list = []
	
	import jcamp
	
	## format spectra and normalize intensitites
	unknown_tmp = pd.DataFrame(data = unknown, columns = ["mz", "intensity"])
	unknown_tmp["normalized"] = unknown_tmp.apply(normalize, args=(max(unknown_tmp["intensity"]),),axis=1)
	unknown_tmp = unknown_tmp[unknown_tmp["mz"].between(xlim[0],xlim[1])]
	unknown_plot = unknown_tmp[["mz", "normalized"]].copy() # data frame for plotting spectrum
	unknown_plot.columns = ["mz", "intensity"]
	unknown = unknown_plot[unknown_plot["intensity"] >= b] # data frame for similarity score calculation
	
	for filename in library_file_list:
		try:
			jcamp_file = jcamp.jcamp_read(os.path.join(library_dir,filename))
			mz = jcamp_file["x"]
			intensity = jcamp_file["y"]
			name = jcamp_file[u'title']

			library_tmp = pd.DataFrame(data = np.column_stack((mz, intensity)), columns = ["mz", "intensity"])
			library_tmp["normalized"] = library_tmp.apply(normalize, args=(max(library_tmp["intensity"]),),axis=1)
			library_tmp = library_tmp[library_tmp["mz"].between(xlim[0],xlim[1])]
			library_plot = library_tmp[["mz", "normalized"]].copy() # data frame for plotting spectrum
			library_plot.columns = ["mz", "intensity"]
			library = library_plot[library_plot["intensity"] >= b] # data frame for similarity score calculation
		
		
			## align the m/z axis of the two spectra, the bottom spectrum is used as the reference
			alignment = pd.merge(unknown, library, on="mz", how="outer")
			alignment.fillna(value=0, inplace=True) # Convert NaN to 0
			alignment.columns=["mz", "intensity_top", "intensity_bottom"]
			
			## similarity score calculation
			
			if x_threshold < 0:
				print("Error: x_threshold argument must be zero or a positive number")
				return 1
		
		
			u = np.array(alignment.iloc[:,1])
			v = np.array(alignment.iloc[:,2])
			
			similarity_score = np.dot(u,v) / (np.sqrt(np.sum(np.square(u))) * np.sqrt(np.sum(np.square(v))))
			
			
			# Reverse Match
			reverse_alignment = pd.merge(unknown, library, on="mz", how="right")
			#reverse_alignment.fillna(value=0, inplace=True) # Convert NaN to 0
			reverse_alignment.columns=["mz", "intensity_top", "intensity_bottom"]
			u = np.array(reverse_alignment.iloc[:,1])
			v = np.array(reverse_alignment.iloc[:,2])
			
			reverse_similarity_score = np.dot(u,v) / (np.sqrt(np.sum(np.square(u))) * np.sqrt(np.sum(np.square(v))))
		
			match_list.append([name, similarity_score, reverse_similarity_score])
		except:
			pass
	# simscore <- as.vector((u %*% v)^2 / (sum(u^2) * sum(v^2)))   # cos squared
		
	print(len(match_list))
	
	return match_list


def SearchProcessWrapper(args):
	return LibrarySearch(*args)

def demo():
	# Read Unknown Spectrum
	import jcamp
	import os
	from multiprocessing import Pool

	jcamp_file = jcamp.jcamp_read("/media/VIDEO/ownCloud/GSR/GunShotMatch/JCAMP/spectra/Diphenylamine.JDX")

	mz = jcamp_file["x"]
	intensity = jcamp_file["y"]

	#mz, intensity = [50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256,257,258,259,260,261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285,286,287,288,289,290,291,292,293,294,295,296,297,298,299,300,301,302,303,304,305,306,307,308,309,310,311,312,313,314,315,316,317,318,319,320,321,322,323,324,325,326,327,328,329,330,331,332,333,334,335,336,337,338,339,340,341,342,343,344,345,346,347,348,349,350,351,352,353,354,355,356,357,358,359,360,361,362,363,364,365,366,367,368,369,370,371,372,373,374,375,376,377,378,379,380,381,382,383,384,385,386,387,388,389,390,391,392,393,394,395,396,397,398,399,400,401,402,403,404,405,406,407,408,409,410,411,412,413,414,415,416,417,418,419,420,421,422,423,424,425,426,427,428,429,430,431,432,433,434,435,436,437,438,439,440,441,442,443,444,445,446,447,448,449,450,451,452,453,454,455,456,457,458,459,460,461,462,463,464,465,466,467,468,469,470,471,472,473,474,475,476,477,478,479,480,481,482,483,484,485,486,487,488,489,490,491,492,493,494,495,496,497,498,499],[0,6945,0,0,1847,0,0,0,0,288,0,4629,0,0,825,0,0,839,0,0,1599,20,0,0,0,1234,1788,0,0,189,0,2500,5015,0,1909,222,0,0,3462,2057,2462,672,0,0,0,0,27807,0,0,0,0,0,0,3313,0,0,664,0,0,0,0,0,1430,0,0,2231,740,527,0,0,0,0,0,0,136,0,1330,1291,0,220,0,18381,0,14520,0,1471,0,0,0,0,0,0,749,1301,0,0,0,668,0,0,0,0,0,0,0,0,1421,0,0,825,0,0,0,1578,0,1093,0,0,0,0,0,0,0,0,0,0,0,0,0,1430,0,0,0,0,0,0,0,0,0,672,0,0,0,583,0,0,0,0,672,0,0,0,672,0,0,0,75,351552,0,9968,1962,0,0,0,0,0,749,0,0,0,0,0,0,749,0,0,0,0,0,672,0,0,749,0,0,825,0,2432,0,0,0,0,0,0,0,0,0,1362,0,0,0,1650,0,0,672,672,672,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,749,0,0,0,0,0,672,0,0,0,0,0,0,672,0,672,0,0,0,0,0,0,0,0,0,0,0,0,672,901,0,0,672,0,0,0,0,0,0,0,672,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,901,0,0,0,0,0,672,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,672,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,672,0,0,0,0,0,0,0,0,0,0,0,0,0,825,0,0,0,672,825,0,0,0,0,0,0,0,0,0,0,0,0,0,0,672,0,0,0]
	unknown_spectrum = 	np.column_stack((mz, intensity))



	#match_list = LibrarySearch(unknown_spectrum, b = 1, xlim = (45, 500))

	library_dir = "/media/VIDEO/ownCloud/GSR/GunShotMatch/JCAMP/spectra"

	library_file_list = [filename for filename in os.listdir(library_dir)]

	library_file_list = list(chunks(library_file_list, len(library_file_list)/100))

	args = [(unknown_spectrum, library, 0.25, 1, (45, 500)) for library in library_file_list]

	p = Pool(100)
	#match_list = p.map(LibrarySearch, args)
	match_list = p.map(SearchProcessWrapper, args)

	match_list = [y for x in match_list for y in x]

	from operator import itemgetter
	match_list = sorted(match_list, key=itemgetter(1),reverse=True)

	for entry in match_list[:100]:
		print(entry)

	
	
								   

