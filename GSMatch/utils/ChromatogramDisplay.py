"""
Class to Display Ion Chromatograms and TIC
"""
# Adapted from PyMS in 2019 by Dominic Davis-Foster

#############################################################################
#                                                                           #
#    PyMS software for processing of metabolomic mass-spectrometry data     #
#    Copyright (C) 2005-2012 Vladimir Likic                                 #
#                                                                           #
#    This program is free software; you can redistribute it and/or modify   #
#    it under the terms of the GNU General Public License version 2 as      #
#    published by the Free Software Foundation.                             #
#                                                                           #
#    This program is distributed in the hope that it will be useful,        #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of         #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
#    GNU General Public License for more details.                           #
#                                                                           #
#    You should have received a copy of the GNU General Public License      #
#    along with this program; if not, write to the Free Software            #
#    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.              #
#                                                                           #
#############################################################################

import matplotlib.pyplot as plt
import numpy
import sys
sys.path.append('/x/PyMS/')

from pyms.GCMS.Class import IonChromatogram 
from pyms.Utils.Error import error
from pyms.Display.Class import Display as StockDisplay

class Display(StockDisplay):
	"""
	:summary: Class to display Ion Chromatograms and Total
			  Ion Chromatograms from GCMS.Class.IonChromatogram
		
			  Uses matplotlib module pyplot to do plotting

	:author: Sean O'Callaghan
	:author: Vladimir Likic
	"""
	
	def __init__(self, figure, axes):
		"""
		:summary: Initialises an instance of Display class
		"""
		
		# Container to store plots
		self.__tic_ic_plots = []
		
		# color dictionary for plotting of ics; blue reserved
		# for TIC
		self.__col_ic = {0:'r', 1:'g', 2:'k', 3:'y', 4:'m', 5:'c'}
		self.__col_count = 0  # counter to keep track of colors
		
		# Peak list container
		self.__peak_list = []
		
		#Plotting Variables
		self.__fig = figure
		self.__ax = axes


	def plot_ics(self, ics, labels = None):
		
		"""
		:summary: Adds an Ion Chromatogram or a
		list of Ion Chromatograms to plot list
		
		:param ics: List of Ion Chromatograms m/z channels
			for plotting
		:type ics: list of pyms.GCMS.Class.IonChromatogram
		
		:param labels: Labels for plot legend
		:type labels: list of StringType
			"""
		
		if not isinstance(ics, list):
			if isinstance(ics, IonChromatogram):
				ics = [ics]
			else:
				error("ics argument must be an IonChromatogram\
				or a list of Ion Chromatograms")
		
		if not isinstance(labels, list) and labels != None:
			labels = [labels]
		# TODO: take care of case where one element of ics is
		# not an IonChromatogram
		

		intensity_list = []
		time_list = ics[0].get_time_list()
		
		
		for i in range(len(ics)):
			intensity_list.append(ics[i].get_intensity_array())
			

		# Case for labels not present
		if labels == None:
			for i in range(len(ics)):
				self.__tic_ic_plots.append(self.__ax.plot(time_list, \
					intensity_list[i], self.__col_ic[self.__col_count]))
			if self.__col_count == 5:
				self.__col_count = 0
			else:
				self.__col_count += 1
		
		# Case for labels present
		else:
			for i in range(len(ics)):
			
				self.__tic_ic_plots.append(self.__ax.plot(time_list, \
					intensity_list[i], self.__col_ic[self.__col_count]\
						, label = labels[i]))
				if self.__col_count == 5:
					self.__col_count = 0
				else:
					self.__col_count += 1
		
	def plot_tic(self, tic, label=None, minutes=False):
		
		"""
		:summary: Adds Total Ion Chromatogram to plot list
		
		:param tic: Total Ion Chromatogram
		:type tic: pyms.GCMS.Class.IonChromatogram
		
		:param label: label for plot legend
		:type label: StringType
			"""
			
		if not isinstance(tic, IonChromatogram):
			error("TIC is not an Ion Chromatogram object")
			
			
		intensity_list = tic.get_intensity_array()
		time_list = tic.get_time_list()
		if minutes:
			time_list = [time/60 for time in time_list]
		
		self.__tic_ic_plots.append(self.__ax.plot(time_list, intensity_list,\
		label=label))
		
	def plot_peaks(self, peak_list, label = "Peaks"):
		
		"""
		:summary: Plots the locations of peaks as found
			by PyMS.
			
		:param peak_list: List of peaks
		:type peak_list: list of pyms.Peak.Class.Peak
		
		:param label: label for plot legend
		:type label: StringType
			"""
			
		if not isinstance(peak_list, list):
			error("peak_list is not a list")
			
		time_list = []
		height_list=[]
		
		# Copy to self.__peak_list for onclick event handling
		self.__peak_list = peak_list
		
		for peak in peak_list:
			time_list.append(peak.get_rt())
			height_list.append(sum(peak.get_mass_spectrum().mass_spec))
			
		self.__tic_ic_plots.append(self.__ax.plot(time_list, height_list, 'o',\
			label = label))