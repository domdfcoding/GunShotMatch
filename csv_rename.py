#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  csv_rename.py
#  
#  Copyright 2018 Dominic Davis-Foster <domdf@dominic-desktop>
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

import os, time
from  utils.helper import RepresentsInt
import progressbar

ingest_path = "./Results/CSV_ingest"

def main(args):
	
	#pbar_len = 0
	filenames = []
	
	
	"""# get number of files to rename
	widgets = ['Loading ',progressbar.AnimatedMarker(),  ' ', progressbar.Timer(),]
	for filename in os.listdir("./CSV_ingest"):
		file_path, file_extension = os.path.splitext(os.path.join("./CSV_ingest",filename))
		if file_extension.upper() == ".CSV":
			if RepresentsInt(file_path[-5:]):
				pbar_len += 1
				filenames.append(filename)
	
	#widgets = [' [', progressbar.Timer(), '] ',
	#progressbar.Bar(),
	#' (', progressbar.ETA(), ') ',
	
	
	
	#progressbar.widgets.AnimatedMarker(), ' ','Generating XLSX Output.', ' ', progressbar.Timer(),]
	
	
	
	#bar = progressbar.ProgressBar(widgets=widgets, max_value=pbar_len,redirect_stdout=True).start()
#	bar_step = 1
#	bar = progressbar.ProgressBar(max_value=pbar_len,redirect_stdout=True)
	"""
	
	for filename in os.listdir(ingest_path):
	#for filename in filenames:
		file_path, file_extension = os.path.splitext(os.path.join(ingest_path,filename))
		#print file_path
		#print file_extension	
		if file_extension.upper() == ".CSV":
			if RepresentsInt(file_path[-5:]):
				file_size = str(os.path.getsize(os.path.join(ingest_path,filename)))
				#print file_size
				#print file_size[0]
				#print len(file_size)
				# if file_size[0] == "8" and len(file_size) == 4:
					# #print "GC"
					# print("Renaming {} to {}GC_80.CSV\t\tSize {}".format(filename, file_path[:-13], file_size))
					# os.rename(os.path.join(ingest_path,filename),file_path[:-13] + "GC_80.CSV")
				if len(file_size) == 4:
					#print "GC"
					print("Renaming {} to {}GC_80.CSV\t\tSize {}".format(filename, file_path[:-13], file_size))
					os.rename(os.path.join(ingest_path,filename),file_path[:-13] + "GC_80.CSV")
				elif len(file_size) == 7:
					#print "MS"
					print("Renaming {} to {}MS_80.CSV\t\tSize {}".format(filename, file_path[:-13], file_size))
					os.rename(os.path.join(ingest_path,filename),file_path[:-13] + "MS_80.CSV")
				# elif file_size[0] == "9" and len(file_size) == 4:
					# #print "GC"
					# print("Renaming {} to {}GC_80.CSV\t\tSize {}".format(filename, file_path[:-13], file_size))
					# os.rename(os.path.join(ingest_path,filename),file_path[:-13] + "GC_80.CSV")
				# elif file_size[0] == "3" and len(file_size) == 7:
					# #print "MS"
					# print("Renaming {} to {}MS_80.CSV\t\tSize {}".format(filename, file_path[:-13], file_size))
					# os.rename(os.path.join(ingest_path,filename),file_path[:-13] + "MS_80.CSV")
				# elif file_size[0] == "4" and len(file_size) == 7:
					# #print "MS"
					# print("Renaming {} to {}MS_80.CSV\t\tSize {}".format(filename, file_path[:-13], file_size))
					# os.rename(os.path.join(ingest_path,filename),file_path[:-13] + "MS_80.CSV")
			#	elif file_size[0] == "3" and len(file_size) == 4:
			#		#print "MS"
			#		print("Renaming {} to {}GC_30.CSV\t\tSize {}".format(filename, file_path[:-13], file_size))
			#		os.rename(os.path.join("./CSV_ingest",filename),file_path[:-13] + "GC_30.CSV")
#				bar.update(bar_step)
#				bar_step += 1
				time.sleep(0.1)
	
	print("Finished")
	
if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
