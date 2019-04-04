#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright 2019 Dominic Davis-Foster
#
# Adapted from SpectrumSimilarity.R
# Part of OrgMassSpecR
# Copyright 2011-2017 Nathan Dodder <nathand@sccwrp.org>

import numpy as np
import pandas as pd

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
	if print_graphic:
		import matplotlib.pyplot as plt

	
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
	reverse_alignment = reverse_alignment.dropna() #Remove rows containing NaN
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
		# Unimplemented R code
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




