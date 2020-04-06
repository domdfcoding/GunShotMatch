#!/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  projectile_properties.py
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

colour_dropdown_choices = [
		"Golden, like Brass",
		"Red-Brown, like Copper",
		"Silvery, like Steel or Cupronickel",
		"Dull Grey, like Lead",
		]

type_dropdown_choices = [
		"Shot", "Slug", "Lead Round Nose (LRN)",
		"Wad Cutter (WC)", "Semi Wad Cutter (SWC)",
		"Full Metal Jacket (FMJ)", "Semi-Jacketed Hollow Point (SJHP)",
		"Jacketed Hollow Point (JHP)", "Soft Point (SP/JSP)",
		"Armour Piercing (AP)", "Blank", "Reloading Powder",
		]
# Ref: https://www.gunvault.com/blog/types-of-ammunition/

tip_type_dropdown_choices = [
		"Flat",
		"Round",
		"Spitzer",
		"Semi-Spitzer",
		"Hollow Point",
		"Plastic",
		]
# Ref: https://crimefictionbook.com/2016/04/28/from-hollow-points-to-spitzers-a-quick-guide-to-bullet-types/


class Projectile:
	"""
	Class for storing properties about a Projectile
	"""
	
	def __init__(
			self, colour='', type='', mass=0, tip_type='',
			has_boattail=False, tracer=False, notes=''):
		"""
		:param colour: The colour of the projectile
		:type colour: str, optional
		:param type: The type of projectile
		:type type: str, optional
		:param mass: The mass of the projectile, in grains
		:type mass: int or float, optional
		:param tip_type: The type of tip on the projectile
		:type tip_type: str, optional
		:param has_boattail: Whether the projectile has a boattail
		:type has_boattail: bool, optional
		:param tracer: Whether the projectile is a tracer
		:type tracer: bool, optional
		:param notes: Any other notes/remarks about the projectile
		:type notes: str, optional
		"""

		self.colour = Property(
				"projectile_colour", colour, list,
				help="The colour of the projectile", label="Colour",
				dropdown_choices=colour_dropdown_choices,
				)
		self.type = Property(
				"projectile_type", type, list,
				help="The type of projectile", label="Type",
				dropdown_choices=type_dropdown_choices,
				)
		self.tip_type = Property(
				"projectile_tip_type", tip_type, list,
				help="The type of tip on the projectile", label="Tip Type",
				dropdown_choices=tip_type_dropdown_choices,
				)
		self.has_boattail = Property(
				"projectile_has_boattail", has_boattail, bool,
				help="Does the projectile have a boattail?",
				label="Projectile has Boattail?",
				)
		self.tracer = Property(
				"projectile_tracer", tracer, bool,
				help="Is the projectile a tracer?",
				label="Projectile is Tracer?",
				)
		self.mass = Property(
				"projectile_mass", mass, Measurement(-1),
				help="The mass of the projectile",
				label="Projectile Mass (grains)",
				)
		self.notes = Property(
				"projectile_notes", notes, longstr,
				help="Notes & Remarks about the projectile", label="Notes & Remarks"
				)
	
	@classmethod
	@append_docstring_from(__init__)
	def from_list(cls, projectile_data):
		"""
		Create a ``Projectile`` object from a list, containing the properties
		in the order the arguments appear for the class
		
		:param projectile_data:
		:type projectile_data:
		
		:rtype: Projectile
		
		The properties must appear in the following order and have the following types:"""
		
		if isinstance(projectile_data, str):
			# Presumably from json
			projectile_data = json.loads(projectile_data)
		elif not isinstance(projectile_data, (list, tuple)):
			raise TypeError("'projectile_data' must be a list, a tuple, or a string that represents a list")
		
		return cls(*projectile_data)
	
	@classmethod
	def from_dict(cls, projectile_dict):
		return cls(**projectile_dict)
		
	@property
	def all_properties(self):
		"""
		Returns a list containing all of the properties, in the order they should be displayed

		:return:
		:rtype: list
		"""
		
		return [
			self.colour,
			self.type,
			self.mass,
			self.tip_type,
			self.has_boattail,
			self.tracer,
			self.notes,
			]
	
	def __dict__(self):
		projectile_dict = {}
		
		if self.colour:
			projectile_dict["colour"] = self.colour.value
		if self.type:
			projectile_dict["type"] = self.type.value
		if self.mass:
			projectile_dict["mass"] = self.mass.value
		if self.tip_type:
			projectile_dict["tip_type"] = self.tip_type.value
		if self.has_boattail:
			projectile_dict["has_boattail"] = self.has_boattail.value
		if self.tracer:
			projectile_dict["tracer"] = self.tracer.value
		if self.notes:
			projectile_dict["notes"] = self.notes.value
		
		return projectile_dict
	
	def __iter__(self):
		for key, value in self.__dict__().items():
			yield key, value
