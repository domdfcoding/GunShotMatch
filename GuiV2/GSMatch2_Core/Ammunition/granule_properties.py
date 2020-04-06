#!/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  granule_properties.py
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
import json

# 3rd party
from domdf_python_tools.doctools import append_docstring_from

# this package
from GuiV2.GSMatch2_Core.InfoProperties import longstr, Measurement, Property


shape_dropdown_choices = [
	"Disc",
	"Perforated Disc, Trail Boss, etc.",
	"---",
	"Rod or Cylinder",
	"Cord, e.g. Cordite",
	"Extruded Tube, Perforated Rod, etc."
	"Multi-Perforated Rod"
	"Slotted Tube"
	"---",
	"Spherical Ball",
	"Cracked Ball"
	"Flattened Ball",
	"---",
	"Square Flake",
	"Trapezium Flake",
	"Ribbon, Rectangular Flake, etc."
	"Other Flake Shape",
	"---",
	"Random Chips",
	]
# Refs:
# 	https://archives.fbi.gov/archives/about-us/lab/forensic-science-communications/fsc/april2002/mccord.htm
# 	https://www.vihtavuori.com/tech-blog-powder-grain-shapes/
# 	https://projects.nfstc.org/firearms/module05/fir_m05_t04_04.htm#
# 	Shooting Incident Reconstruction, by Lucien C. Haag and Michael G. Haag
# 	Military Ballistics: A Basic Manual, C. L. Farrar and D. W. Leeming
# 	Trapezium shape based on observations of propellant images in
# 		Propellant Profiles, 5th Ed, by Wolfe Publishing Company
#


class Granule:
	"""
	Class for storing properties about a Projectile
	"""
	def __init__(
			self, colour='', shape='', width=0, diameter=0,
			length=0, thickness=0, notes=''
			):
		"""
		:param colour: The colour of the propellant granules
		:type colour: str, optional
		:param shape: The shape of the propellant granules
		:type shape: str, optional
		:param width: The width of the propellant granules
		:type width: int or float, optional
		:param diameter: The diameter of the of the propellant granules
		:type diameter: int or float, optional
		:param length: The length of the of the propellant granules
		:type length: int or float, optional
		:param thickness: The thickness of the of the propellant granules
		:type thickness: int or float, optional
		:param notes: Any other notes/remarks about the propellant
		:type notes: str, optional
		"""
		
		self.colour = Property(
				"propellant_colour", colour, str,
				help="The colour of the propellant", label="Colour"
				)
		self.shape = Property(
				"propellant_shape", shape, list,
				help="The shape of the propellant", label="Shape",
				dropdown_choices=shape_dropdown_choices
				)
		self.width = Property(
				"propellant_width", width, Measurement(0),
				help="The width of the propellant", label="Width (μm)"
				)
		self.diameter = Property(
				"propellant_diameter", diameter, Measurement(0),
				help="The diameter of the propellant", label="Diameter (μm)"
				)
		self.length = Property(
				"propellant_length", length, Measurement(0),
				help="The length of the propellant", label="Length (μm)"
				)
		self.thickness = Property(
				"propellant_thickness", thickness, Measurement(0),
				help="The thickness of the propellant", label="Thickness (μm)"
				)
		self.notes = Property(
				"propellant_notes", notes, longstr,
				help="Notes & Remarks about the propellant", label="Notes & Remarks"
				)
	
	@classmethod
	@append_docstring_from(__init__)
	def from_list(cls, granule_data):
		"""
		Create a ``Granule`` object from a list, containing the properties
		in the order the arguments appear for the class

		:param granule_data:
		:type granule_data:

		:rtype: Granule

		The properties must appear in the following order and have the following types:"""
		
		if isinstance(granule_data, str):
			# Presumably from json
			granule_data = json.loads(granule_data)
		elif not isinstance(granule_data, (list, tuple)):
			raise TypeError("'granule_data' must be a list, a tuple, or a string that represents a list")
		
		return cls(*granule_data)
	
	@classmethod
	def from_dict(cls, granule_dict):
		return cls(**granule_dict)
		
	@property
	def all_properties(self):
		"""
		Returns a list containing all of the properties, in the order they should be displayed

		:return:
		:rtype: list
		"""
		
		return [
				self.colour,
				self.shape,
				self.width,
				self.diameter,
				self.length,
				self.thickness,
				self.notes,
				]
	
	def __dict__(self):
		granule_dict = {}
		
		if self.colour:
			granule_dict["colour"] = self.colour.value
		if self.shape:
			granule_dict["shape"] = self.shape.value
		if self.width:
			granule_dict["width"] = self.width.value
		if self.diameter:
			granule_dict["diameter"] = self.diameter.value
		if self.length:
			granule_dict["length"] = self.length.value
		if self.thickness:
			granule_dict["thickness"] = self.thickness.value
		if self.notes:
			granule_dict["notes"] = self.notes.value
		
		return granule_dict
	
	def __iter__(self):
		for key, value in self.__dict__().items():
			yield key, value
