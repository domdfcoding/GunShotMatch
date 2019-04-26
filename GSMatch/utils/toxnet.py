#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  toxnet.py
"""Read data from National Library of Medicine TOXNET"""
#  Copyright 2019 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
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

from bs4 import BeautifulSoup
import requests
from decimal import Decimal
from utils.property_format import *

def toxnet(cas):
	try:
		base_url = "https://toxnet.nlm.nih.gov"
		originURL = f"{base_url}/cgi-bin/sis/search2/r?dbs+hsdb:@term+@rn+@rel+{cas}"
		origin_page = requests.get(originURL)
		origin_soup = BeautifulSoup(origin_page.text, "html.parser")
		#print(originURL)
		#print(origin_soup.find("a", {"id": "anch_103"}))
		#print(origin_soup.find("input", {"name": "dfield"}))
		dataURL = origin_soup.find("input", {"name": "dfield"}).find_next_sibling("a")["href"][:-4]+"cpp"
		#print(dataURL)
		data_page = requests.get(base_url + dataURL)
		data_soup = BeautifulSoup(data_page.text, "html.parser")
	except AttributeError:
		raise ValueError(f"No Record was found for {cas}")
	
	physical_properties = {}
	
	for property in data_soup.findAll("h3"):
		property_name = str(property).replace("<h3>",'').replace(":</h3>",'')
		property_value_and_unit = property.nextSibling.replace("\n",'')
		
		if property_name in ["Molecular Formula", "Molecular Weight"]:
			continue
		
		if property_name == "Solubilities":
			property_name = "Solubility"
		
		#elif property_name == "Vapor Density":
		#	physical_properties[property_name] = property_value_and_unit.replace(" (Air= 1)",'')
		#else:
		#	physical_properties[property_name] = property_format(property_value_and_unit)
		
		physical_properties[property_name] = {}
		
		# Parse values
		# Temperatures
		if property_name in ["Boiling Point","Melting Point"]:
			property_value = property_value_and_unit.split(" deg C")[0]
			try:
				physical_properties[property_name]["Value"] = Decimal(property_value)
			except:
				physical_properties[property_name]["Value"] = property_format(property_value)
			physical_properties[property_name]["Unit"] = "°C"
			physical_properties[property_name]["Description"] = None
	
		# Strings
		elif property_name in ["Color/Form", "Odor", "Other Chemical/Physical Properties", "Solubility", "Spectral Properties"]:
			physical_properties[property_name]["Value"] = property_format(property_value_and_unit)
			physical_properties[property_name]["Unit"] = None
			physical_properties[property_name]["Description"] = None
		
		# Custom Units &c.
		elif property_name == "Density/Specific Gravity":
			try:
				physical_properties[property_name]["Value"] = Decimal(property_value_and_unit)
			except:
				physical_properties[property_name]["Value"] = property_format(property_value_and_unit)
			physical_properties[property_name]["Unit"] = "kg/m<sup>3</sup>"
			physical_properties[property_name]["Description"] = None
		elif property_name == "Vapor Density":
			#property_value = property_value_and_unit.split(" ")[0]
			physical_properties[property_name]["Value"] = property_format(property_value_and_unit.replace(" (Air= 1)",''))
			physical_properties[property_name]["Unit"] = "None"
			physical_properties[property_name]["Description"] = "Air=1"
			
		# TODO
		elif property_name == "Dissociation Constants":
			#property_value_list = property_value_and_unit.split(" ")
			#property_value = property_value_list[2]
			#physical_properties[property_name]["Value"] = property_value
			#physical_properties[property_name]["Unit"] = f"pKa @ {property_value_list[4]}°C"
			physical_properties[property_name]["Unit"] = None
			physical_properties[property_name]["Value"] = property_format(property_value_and_unit)
			physical_properties[property_name]["Description"] = None
		elif property_name == "Heat of Combustion":
			physical_properties[property_name]["Value"] = property_format(property_value_and_unit)
			physical_properties[property_name]["Unit"] = None
			physical_properties[property_name]["Description"] = None
			#TODO Extract J/KG value from string
		elif property_name == "Octanol/Water Partition Coefficient":
			#property_value = property_value_and_unit.split("log Kow = ")[1]
			#print(property_value)
			#print(property_value_and_unit.split("log Kow = "))
			## TODO Fix
			#physical_properties[property_name]["Value"] = property_value
			#physical_properties[property_name]["Unit"] = "log Kow"
			physical_properties[property_name]["Value"] = property_format(property_value_and_unit)
			physical_properties[property_name]["Unit"] = None
			physical_properties[property_name]["Description"] = None
		elif property_name == "Surface Tension":
			#property_value_list = property_value_and_unit.split(" ")
			#property_value = property_value_list[3]
			#print(property_value_list)
			#physical_properties[property_name]["Value"] = property_value
			#physical_properties[property_name]["Unit"] = f"N/M @ {property_value_list[6]}°C"
			physical_properties[property_name]["Value"] = property_format(property_value_and_unit)
			physical_properties[property_name]["Unit"] = None
			physical_properties[property_name]["Description"] = None
		elif property_name == "Vapor Pressure":
			#property_value_list = property_value_and_unit.split(" ")
			#property_value = property_value_list[0]
			#physical_properties[property_name]["Value"] = property_value
			#physical_properties[property_name]["Unit"] = f"mm Hg @ {property_value_list[4]}°C"
			physical_properties[property_name]["Value"] = property_format(property_value_and_unit)
			physical_properties[property_name]["Unit"] = None
			physical_properties[property_name]["Description"] = None
		#else:
		#	physical_properties[property_name] = property_value_and_unit
	

	return physical_properties

# Soup CAMEO Link from PubChem page if necessary



if __name__ == "__main__":
	import pprint
	pprint.pprint(toxnet("122-39-4"))
	#pprint.pprint(toxnet("85-98-3")) # No Record
	#pprint.pprint(toxnet("71-43-2"))

