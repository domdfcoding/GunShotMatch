#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  __init__.py
"""Main file for data_viewer_server"""
#
#  This file is part of GunShotMatch
#
#  Copyright © 2019-2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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


# stdlib
import hashlib
import io
import json
import os
import pathlib
import pickle
import urllib.error
import urllib.request
import warnings

# 3rd party
import appdirs
import numpy
from chemistry_tools.constants import API_BASE
from chemistry_tools.lookup import get_compounds
from domdf_python_tools.paths import maybe_make
from flask import Flask, render_template, request, send_file
from indigo import Indigo
from indigo.renderer import IndigoRenderer
from mathematical.utils import rounders

# This package
from GuiV2.GSMatch2_Core.Project import ConsolidatedPeak, ConsolidatedSearchResult

app = Flask(__name__)


def prepare_cache_dir():
	cache_dir = pathlib.Path(appdirs.user_cache_dir("GunShotMatch"))
	if not cache_dir.exists():
		cache_dir.mkdir()
	cache_dir = cache_dir / "data_viewer_cache"
	if not cache_dir.exists():
		cache_dir.mkdir()
	
	return cache_dir

cache_dir = prepare_cache_dir()


@app.context_processor
def inject_functions():
	"""
	Adds certain Python functions to the jinja2 global scope
	
	:return: Dictionary of Python functions
	:rtype: dict
	"""
	
	return dict(rounders=rounders, np=numpy, len=len)


@app.route("/<path:samples>")
def peak_data(samples):
	print(request.args)
	samples = samples.split("/")
	
	if "data" in request.args:
		print(request.args.get("data", type=str))
		peak = ConsolidatedPeak.from_quoted_string(request.args.get("data", type=str))
		print(peak)
		
		CAS = peak.hits[0].cas
		Name = peak.hits[0].name
		rt = peak.rt
		
		if CAS.replace("-", '').replace("0", '') == '':
			# CAS Number is all zeros
			pickle_name = hashlib.md5(Name.encode("utf-8")).hexdigest()
			# html_file_name = os.path.join(html_file_directory, f"{pickle_name}_{rt}.html")
			
			if (cache_dir / pickle_name).exists():
				with open(cache_dir / pickle_name, "rb") as f:
					comp = pickle.load(f)
			else:
				# if True:
				comp = get_compounds(Name, 'name')[0]
				# Save to cache
				with open(cache_dir / pickle_name, "wb") as f:
					pickle.dump(comp, f)
		
		else:
			if (cache_dir / CAS).exists():
				with open(cache_dir / CAS, "rb") as f:
					comp = pickle.load(f)
			else:
				# if True:
				comp = get_compounds(CAS, 'name')[0]
				# Save to cache
				with open(cache_dir / CAS, "wb") as f:
					pickle.dump(comp, f)
		
		return render_template(
				"properties_template_2.html",
				comp=comp,
				peak=peak,
				samples=samples,
				)
		
	else:
		# Legacy mode
		
		index = request.args.get("index", 0, type=int)
		filename = request.args.get("filename", '', type=str)
		
		peak_data = []
		
		if filename == '':
			return "Please provide a filename with ?filename=", 400
		
		with open(os.path.join(filename), "r") as jsonfile:
			for i, peak in enumerate(jsonfile):
				if i == index:
					peak_data = json.loads(peak)
		
		if not peak_data:
			# Index was out of range
			return "Peak index out of range", 400
		
		CAS = peak_data["hits"][0]["CAS"]
		Name = peak_data["hits"][0]["Name"]
		rt = peak_data["average_rt"]
		
		if CAS.replace("-", '').replace("0", '') == '':
			# CAS Number is all zeros
			pickle_name = hashlib.md5(Name.encode("utf-8")).hexdigest()
			# html_file_name = os.path.join(html_file_directory, f"{pickle_name}_{rt}.html")
			
			if (cache_dir / pickle_name).exists():
				with open(cache_dir / pickle_name, "rb") as f:
					comp = pickle.load(f)
			else:
				# if True:
				comp = get_compounds(Name, 'name')[0]
				# Save to cache
				with open(cache_dir / pickle_name, "wb") as f:
					pickle.dump(comp, f)
		
		else:
			if (cache_dir / CAS).exists():
				with open(cache_dir / CAS, "rb") as f:
					comp = pickle.load(f)
			else:
				# if True:
				comp = get_compounds(CAS, 'name')[0]
				# Save to cache
				with open(cache_dir / CAS, "wb") as f:
					pickle.dump(comp, f)
		
		return render_template(
				"properties_template.html",
				comp=comp,
				data=peak_data,
				samples=samples,
				)


@app.route("/hit/<path:samples>")
def hit_data(samples):
	# print(request.args)
	samples = samples.split("/")
	
	maybe_make("cache")  # Internal Cache Directory
	
	if "data" in request.args:
		# print(request.args.get("data", type=str))
		hit = ConsolidatedSearchResult.from_quoted_string(request.args.get("data", type=str))
		# print(hit)
		
		CAS = hit.cas
		Name = hit.name
		
		if CAS.replace("-", '').replace("0", '') == '':
			# CAS Number is all zeros
			pickle_name = hashlib.md5(Name.encode("utf-8")).hexdigest()
			# html_file_name = os.path.join(html_file_directory, f"{pickle_name}_{rt}.html")
			
			if (cache_dir / pickle_name).exists():
				with open(cache_dir / pickle_name, "rb") as f:
					comp = pickle.load(f)
			else:
				# Check that a connection an be established to PubChem server
				try:
					urllib.request.urlopen(API_BASE, timeout=2)
				
				except urllib.error.HTTPError as e:
					if e.code == 400:
						pass
					else:
						raise e
					
				except urllib.error.URLError:
					warnings.warn("Unable to connect to PubChem server. Check your internet connection and try again.")
					return render_template(
							"properties_template_offline.html",
							hit=hit,
							samples=samples,
							)
				
				try:
					comp = get_compounds(CAS, 'name')[0]
				except IndexError:
					comp = None
					
				# Save to cache
				with open(cache_dir / pickle_name, "wb") as f:
					pickle.dump(comp, f)
		
		else:
			if (cache_dir / CAS).exists():
				with open(cache_dir / CAS, "rb") as f:
					comp = pickle.load(f)
			else:
				# if True:
				try:
					comp = get_compounds(CAS, 'name')[0]
				except IndexError:
					comp = None
				
				# Save to cache
				with open(cache_dir / CAS, "wb") as f:
					pickle.dump(comp, f)
		
		# TODO: Combine information from hit.reference_data and comp, e.g. synonyms
		
		return render_template(
				"properties_template_2.html",
				comp=comp,
				hit=hit,
				samples=samples,
				)
		
	else:
		# Legacy mode
		
		index = request.args.get("index", 0, type=int)
		filename = request.args.get("filename", '', type=str)
		
		peak_data = []
		
		if filename == '':
			return "Please provide a filename with ?filename=", 400
		
		with open(os.path.join(filename), "r") as jsonfile:
			for i, peak in enumerate(jsonfile):
				if i == index:
					peak_data = json.loads(peak)
		
		if not peak_data:
			# Index was out of range
			return "Peak index out of range", 400
		
		CAS = peak_data["hits"][0]["CAS"]
		Name = peak_data["hits"][0]["Name"]
		rt = peak_data["average_rt"]
		
		if CAS.replace("-", '').replace("0", '') == '':
			# CAS Number is all zeros
			pickle_name = hashlib.md5(Name.encode("utf-8")).hexdigest()
			# html_file_name = os.path.join(html_file_directory, f"{pickle_name}_{rt}.html")
			
			if (cache_dir / pickle_name).exists():
				with open(cache_dir / pickle_name, "rb") as f:
					comp = pickle.load(f)
			else:
				# if True:
				comp = get_compounds(Name, 'name')[0]
				# Save to cache
				with open(cache_dir / pickle_name, "wb") as f:
					pickle.dump(comp, f)
		
		else:
			if (cache_dir / CAS).exists():
				with open(cache_dir / CAS, "rb") as f:
					comp = pickle.load(f)
			else:
				# if True:
				comp = get_compounds(CAS, 'name')[0]
				# Save to cache
				with open(cache_dir / CAS, "wb") as f:
					pickle.dump(comp, f)
		
		return render_template(
				"properties_template.html",
				comp=comp,
				data=peak_data,
				samples=samples,
				)


@app.route("/favicon.ico")
def favicon():
	return ''


@app.route("/")
@app.route("/index.html")
def home():
	return render_template("index.html")


@app.route("/no_hit")
@app.route("/no-hit")
def no_hit():
	return render_template("no_hit.html")


@app.route("/smiles/<path:smiles_string>")
def smiles(smiles_string):
	# Render SMILES to PNG
	indigo = Indigo()
	renderer = IndigoRenderer(indigo)
	
	mol = indigo.loadMolecule(smiles_string)
	mol.layout()  # if not called, will be done automatically by the renderer
	indigo.setOption("render-output-format", "png")
	indigo.setOption("render-image-size", 250, 250)
	indigo.setOption("render-background-color", 1.0, 1.0, 1.0)
	indigo.setOption("render-coloring", True)
	
	indigo.setOption("aromaticity-model", "generic")
	mol.dearomatize()
	
	buf = renderer.renderToBuffer(mol)
	buf = io.BytesIO(buf)
	
	return send_file(
			buf,
			mimetype='image/png',
			as_attachment=False,
			)


if __name__ == "__main__":
	print(f"Data Viewer Server using '{cache_dir}' as cache directory")
	
	app.run(debug=True)
