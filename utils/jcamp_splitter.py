#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  jcamp_splitter.py
#  
#  Split JCAMP File containing multiple spectra into one file per spectrum
#  
#  

import os
import sys


remove_punctuation_map = dict((ord(char), None) for char in '\/*?:"<>|')



for filename in os.listdir("/media/VIDEO/ownCloud/GSR/GunShotMatch/JCAMP/spectra"):
	output_buffer = []
	with open(os.path.join("/media/VIDEO/ownCloud/GSR/GunShotMatch/JCAMP/spectra",filename)) as f:
		txt = f.read()
		#print(txt)
	txt = txt.split("\n")
	#print(txt)
	for line in txt:
	#	print(type(line))
		if line.startswith("##END"):
			pass
		elif line.startswith("##TITLE"):
			pass
		elif line.startswith("##CAS NAME"):
			sample_name = line[11:]
			print(sample_name)
			output_buffer.append(line)
		else:
			output_buffer.append(line)
	
	with open(os.path.join("/media/VIDEO/ownCloud/GSR/GunShotMatch/JCAMP/spectra",filename),"w") as f:
		f.write("##TITLE={}\n".format(sample_name))
		for line in output_buffer:
			f.write(line)
			f.write("\n")
		
		
		#print(line)
	#txt = [line.rstrip('\r\n') for line in f.read()]
	#print txt
	#sys.exit()
   
