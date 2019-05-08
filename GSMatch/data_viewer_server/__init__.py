from flask import Flask, request, jsonify, render_template, request, Blueprint
from flask_bootstrap import Bootstrap
from flask_marshmallow import Marshmallow
import os
import json
import hashlib
from utils import pubchempy as pcp
from utils.paths import maybe_make
from utils.mathematical import rounders
import numpy
import pickle
from threading import Thread
import requests
import sys

sys.stderr = sys.stdout

ma = Marshmallow()

app = Flask(__name__)
Bootstrap(app)
ma.init_app(app)

class Background(Thread):
	def __init__(self, url):
		Thread.__init__(self)
		self.url = url

	def run(self):
		requests.get(self.url)
		print("###GUNSHOTMATCH###:Ready")


@app.context_processor
def inject_functions():
	return dict(rounders=rounders, np=numpy, len=len)


@app.route("/shutdown")
def shutdown():
	print("###GUNSHOTMATCH###:Shutdown")
	sys.exit()


@app.route("/loader")
def loader():
	url = request.args.get("url",'#', type=str)
	index = request.args.get("index",0, type=int)
	background_thread = Background(f"{url}&index={index}")
	background_thread.start()
	return render_template("loading.html")

@app.route("/<path:samples>")
def peak_data(samples):
	index = request.args.get("index",0, type=int)
	filename = request.args.get("filename",'', type=str)
	samples = samples.split("/")
	
	print(filename)
	print(filename=='')
	
	if filename == '':
		raise ValueError("Please provide a filename with ?filename=")
	
	peak_data = []
	
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
		
		#html_file_name = os.path.join(html_file_directory, f"{CAS}_{rt}.html")
		
		if os.path.exists(os.path.join("cache", CAS)):
			with open(os.path.join("cache", CAS), "rb") as f:
				comp = pickle.load(f)
		else:
		#if True:
			comp = pcp.get_compounds(CAS, 'name')[0]
			# Save to cache
			with open(os.path.join("cache", CAS), "wb") as f:
				pickle.dump(comp, f)
	
	
	
	#return str(peak_data)
	return render_template("properties_template.html", comp=comp,
									  data=peak_data,
									  samples=samples,
									  )
	

	
	
	
	
	return str(samples.split("/"))
	
	per_page=request.args.get("per_page",5, type=int)
	posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=per_page, page=page)
	return render_template("home.html", posts=posts)

@app.route("/favicon.ico")
def favicon():
	return ''


app.run(debug=False)