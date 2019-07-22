#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  __init__.py
"""Main file for data_viewer_server"""
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2019 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  GunShotMatch is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  GunShotMatch is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

import os
import sys
import json
import numpy
import pickle
import hashlib

from utils import pubchempy as pcp

from mathematical.utils import rounders

from domdf_python_tools.paths import maybe_make

from flask import Flask, request, render_template


sys.stderr = sys.stdout

app = Flask(__name__)

@app.context_processor
def inject_functions():
	return dict(rounders=rounders, np=numpy, len=len)

@app.route("/<path:samples>")
def peak_data(samples):
	index = request.args.get("index",0, type=int)
	filename = request.args.get("filename",'', type=str)
	samples = samples.split("/")
	peak_data = []
	
	if filename == '':
		raise ValueError("Please provide a filename with ?filename=")
		
	with open(os.path.join(filename),"r") as jsonfile:
		for i, peak in enumerate(jsonfile):
			if i == index:
				peak_data = json.loads(peak)
	
	if peak_data == []:
		# Index was out of range
		raise IndexError("Peak index out of range")
	
	CAS = peak_data["hits"][0]["CAS"]
	Name = peak_data["hits"][0]["Name"]
	rt = peak_data["average_rt"]
	
	maybe_make("cache")  # Internal Cache Directory
	
	if CAS.replace("-", '').replace("0", '') == '':
		# CAS Number is all zeros
		pickle_name = hashlib.md5(Name.encode("utf-8")).hexdigest()
		#html_file_name = os.path.join(html_file_directory, f"{pickle_name}_{rt}.html")
		
		if os.path.exists(os.path.join("cache", pickle_name)):
			with open(os.path.join("cache", pickle_name), "rb") as f:
				comp = pickle.load(f)
		else:
		#if True:
			comp = pcp.get_compounds(Name, 'name')[0]
			# Save to cache
			with open(os.path.join("cache", CAS), "wb") as f:
				pickle.dump(comp, f)
	
	else:
		if os.path.exists(os.path.join("cache", CAS)):
			with open(os.path.join("cache", CAS), "rb") as f:
				comp = pickle.load(f)
		else:
		#if True:
			comp = pcp.get_compounds(CAS, 'name')[0]
			# Save to cache
			with open(os.path.join("cache", CAS), "wb") as f:
				pickle.dump(comp, f)
	

	return render_template("properties_template.html",
						   comp=comp,
						   data=peak_data,
						   samples=samples,
						   )


@app.route("/favicon.ico")
def favicon():
	return ''


if __name__ == "__main__":
	app.run(debug=False)