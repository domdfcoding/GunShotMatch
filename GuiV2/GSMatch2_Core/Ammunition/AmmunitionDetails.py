#!/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  AmmunitionDetails.py
"""
A class to store information about a type of Ammunition
"""
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2019  Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import datetime
import io
import json

# 3rd party
from domdf_python_tools.doctools import append_docstring_from, is_documented_by

# this package
from GuiV2.GSMatch2_Core import Ammunition
from GuiV2.GSMatch2_Core.Ammunition import ammo_images
from GuiV2.GSMatch2_Core.InfoProperties import calibre_type, fixed_list, longstr, Property
from GuiV2.GSMatch2_Core.watchdog import user_info, time_now

PRIMER_TYPE_BOXER = "Boxer"
PRIMER_TYPE_BERDAN = "Berdan"
PRIMER_TYPE_RIMFIRE = "Rimfire"
PRIMER_TYPE_UNKNOWN = ""


class AmmunitionDetails:
	"""
	A class to store information about a type of Ammunition
	"""
	
	def __init__(
			self, name, user, device, date_created, date_modified, version,
			calibre='', year_of_manufacture=0, propellant_granules=None, projectile=None,
			description='', filename=None, manufacturer='', primer_type=PRIMER_TYPE_UNKNOWN,
			propellant_image=None, headstamp_image=None, other_images=None, notes='',
			# legacy projectile properties, if provided add to projectile
			projectile_type='', has_boattail=False, projectile_mass=0,
		):
		"""
		:param name: The name of the Ammunition
		:type name: str
		:param user: The username of the user who created the ``AmmunitionDetails`` object
		:type user: str
		:param device: The device which created the ``AmmunitionDetails`` object
		:type device: str
		:param date_created: The date and time the AmmunitionDetails record was created, in seconds from epoch
		:type date_created: float
		:param date_modified: The date and time the AmmunitionDetails record was last modified, in seconds from epoch
		:type date_modified: float
		:param version: File format version in semver format
		:type version: str
		:param calibre: The calibre of the Ammunition
		:type calibre: str
		:param year_of_manufacture: The year the Ammunition was manufactured
		:type year_of_manufacture: int
		:param propellant_granules: The properties of the propellant
		:type propellant_granules:
		:param projectile: The properties of the projectile
		:type projectile:
		:param description: A description of the Ammunition
		:type description: str
		:param filename:
		:type filename:
		:param manufacturer: The manufacturer of the ammunition
		:type manufacturer: str
		:param primer_type: The type of primer
		:type primer_type: str
		:param propellant_image: Base64 encoded image of propellant
		:type propellant_image:
		:param headstamp_image: Base64 encoded image of headstamp
		:type headstamp_image:
		:param other_images: List of other_images, where each is a tuple containing
		a string for the filename, and a Base64 encoded image
		:type other_images: list
		:param notes: Notes & Remarks about the ammunition
		:type notes: str
		
		Legacy properties
		:param projectile_type:
		:type projectile_type:
		:param has_boattail:
		:type has_boattail:
		:param projectile_mass:
		:type projectile_mass:
		"""
		
		# File Properties
		self.user = Property(
				"ammo_details_user", user, str,
				help="The user who created the Ammunition Details record",
				editable=False, label="User"
				)
		self.device = Property(
				"ammo_details_device", device, str,
				help="The device that created the Ammunition Details record",
				editable=False, label="Device"
				)
		self.date_created = Property(
				"ammo_details_date_created", date_created, datetime,
				help="The date the Ammunition Details record was created",
				editable=False, immutable=True, label="Date Created"
				)
		self.date_modified = Property(
				"ammo_details_date_modified", date_modified, datetime,
				help="The date the Ammunition Details record was last modified",
				editable=False, label="Date Modified"
				)
		self.version = Property(
				"ammo_details_version", version, str,
				help="The Ammunition Details file format version number",
				editable=False, label="Version"
				)
		self.filename = Property(
				"ammo_details_filename", filename, dir,
				help="The name of the Project file", label="Filename"
				)
		
		# Ammunition Information
		self.name = name
		self.description = Property(
				"ammo_details_description", description, longstr,
				help="A description of the Ammunition Details record",
				label="Description"
				)
		self.calibre = Property(
				"ammo_details_calibre", calibre, calibre_type,
				help="The calibre of the ammunition",
				label="Calibre"
				)
		self.manufacturer = Property(
				"ammo_details_manufacturer", manufacturer, str,
				help="The manufacturer of the ammunition",
				label="Manufacturer"
				)
		self.year_of_manufacture = Property(
				"ammo_details_year_of_manufacture", year_of_manufacture, int,
				help="The year the ammunition was manufactured",
				label="Year of Manufacture"
				)
		self.primer_type = Property(
				"ammo_details_primer_type", primer_type, fixed_list,
				help="The type of primer, either Berdan, Boxer or Rimfire. Blank if unknown",
				label="Primer Type", dropdown_choices=[
						PRIMER_TYPE_UNKNOWN,
						PRIMER_TYPE_BERDAN,
						PRIMER_TYPE_BOXER,
						PRIMER_TYPE_RIMFIRE
						])
		self.notes = Property(
				"ammo_details_notes", notes, longstr,
				help="Notes & Remarks about the ammunition", label="Notes & Remarks"
				)
		
		# Propellant
		if propellant_granules:
			self.propellant_granules = Ammunition.Granule.from_dict(propellant_granules)
		else:
			self.propellant_granules = Ammunition.Granule()
		
		# Projectile
		if projectile:
			self.projectile = Ammunition.Projectile.from_dict(projectile)
		else:
			self.projectile = Ammunition.Projectile()
		
		# legacy options
		if projectile_type != '':
			self.projectile.type.value = projectile_type
		if has_boattail:
			self.projectile.has_boattail.value = True
		if projectile_mass != 0:
			self.projectile.mass.value = projectile_mass
		
		# Images
		self.propellant_image = ammo_images.Base642Image(propellant_image)
		self.headstamp_image = ammo_images.Base642Image(headstamp_image)
		self.other_images = []

		if other_images is not None:
			for caption, image in other_images:
				self.other_images.append((caption, ammo_images.Base642Image(image)))
		
		self._panel = None
		
	@classmethod
	@append_docstring_from(__init__)
	def new_empty(cls):
		"""
		Create a new empty AmmunitionDetails record
		"""
		
		user, device = user_info()
		return cls(
			'', user, device,
			time_now(), time_now(),
			"1.0.0"
			)
	
	@classmethod
	@append_docstring_from(__init__)
	def new(
			cls, name, calibre='', year_of_manufacture=0,
			propellant_granules=None, projectile_properties=None,
			description='', filename=None, manufacturer='', primer_type=PRIMER_TYPE_UNKNOWN,
			propellant_image=None, headstamp_image=None, other_images=None, notes=''
			):
		"""
		Create a new AmmunitionDetails record
		"""
		user, device = user_info()
		return cls(
			name, user, device,
			time_now(), time_now(),
			"1.0.0", calibre, year_of_manufacture,
			propellant_granules, projectile_properties,
			description, filename, manufacturer, primer_type,
			propellant_image, headstamp_image, other_images, notes
			)
	
	@classmethod
	def load(cls, filename):
		"""
		Load an AmmunitionDetails record from file
		
		:param filename:
		:type filename:
		"""
		
		if isinstance(filename, io.BytesIO):
			return cls(**json.load(filename))
		else:
			with open(filename) as fp:
				return cls(**json.load(fp))
		
	def store(self, filename=None):
		"""
		Save the AmmunitionDetails record to a file
		
		:param filename: The filename to store the AmmunitionDetails record as.
		If None, the previous filename will continue to be used.
		:type filename: str or None
		
		:return:
		:rtype:
		"""
		
		if filename:
			self.filename.value = filename
		
		self.date_modified.value = time_now()

		with open(filename, mode="w") as ammo_details_file:
			
			ammunition_data = {
				"name": str(self.name),
				"user": str(self.user),
				"device": str(self.device),
				"date_created": float(self.date_created),
				"date_modified": float(self.date_modified),
				"description": str(self.description),
				"version": "1.0.0",
				"calibre": str(self.calibre),
				"manufacturer": str(self.manufacturer),
				"year_of_manufacture": str(self.year_of_manufacture),
				"primer_type": str(self.primer_type),
				"propellant_granules": dict(self.propellant_granules),
				"projectile": dict(self.projectile),
				"propellant_image": ammo_images.Image2Base64(self.propellant_image),
				"headstamp_image": ammo_images.Image2Base64(self.headstamp_image),
				"other_images": self.other_images_b64,
				"notes": str(self.notes),
				}
				
			# Save to file
			print(ammunition_data)
			for name, value in ammunition_data.items():
				print(name)
				print(type(value))
			json.dump(ammunition_data, ammo_details_file, indent=4)
		
		return self.filename.value
	
	@property
	def other_images_b64(self):
		other_images = []
		for caption, image in self.other_images:
			other_images.append((caption, ammo_images.Image2Base64(image)))
		
		return other_images
	
	@property
	def all_properties(self):
		"""
		Returns a list containing all of the properties, in the order they should be displayed
		
		:return:
		:rtype: list
		"""
		
		return [
				self.description,
				self.calibre,
				self.manufacturer,
				self.year_of_manufacture,
				self.primer_type,
				self.notes,
				# self.projectile_type,
				# self.projectile_mass,
				self.user,
				self.device,
				self.date_created,
				self.date_modified,
				self.version,
				]
	
	@property
	def ammunition_properties(self):
		"""
		Returns a list containing all properties relating to the ammunition, in the order they should be displayed
		
		:return:
		:rtype: list
		"""
		
		return [
				self.description,
				self.calibre,
				self.manufacturer,
				self.year_of_manufacture,
				self.primer_type,
				self.notes,
				]
		
	@property
	def file_properties(self):
		"""
		Returns a list containing all properties relating to the file, in the order they should be displayed
		
		:return:
		:rtype: list
		"""
		
		return [
				self.user,
				self.device,
				self.date_created,
				self.date_modified,
				self.version,
				]
		
	# @property
	# def propellant_properties(self):
	#
	# 	return self.propellant_granules.propgrid
	#
	# @property
	# def projectile_properties(self):
	#
	# 	return self.projectile.propgrid
	
	def __repr__(self):
		return f"AmmunitionDetails({self.name})"
	
	def __str__(self):
		return self.__repr__()
	
	def __eq__(self, other):
		return all([
				self.name == other.name,
				self.date_created == other.date_created,
				self.date_modified == other.date_modified,
				])


@is_documented_by(AmmunitionDetails.new)
def new(*args, **kwargs):
	return AmmunitionDetails.new(*args, **kwargs)


@is_documented_by(AmmunitionDetails.new_empty)
def new_empty():
	return AmmunitionDetails.new_empty()


@is_documented_by(AmmunitionDetails.load)
def load(*args, **kwargs):
	return AmmunitionDetails.load(*args, **kwargs)
