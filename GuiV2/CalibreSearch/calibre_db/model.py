#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  model.py
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2020  Dominic Davis-Foster <dominic@davis-foster.co.uk>
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

# 3rd party
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# this package
from GuiV2.CalibreSearch.calibre_db import engine
from GuiV2.CalibreSearch.calibre_db.types import DecimalType, ListType

Base = declarative_base()


class CalibreModel(Base):
	"""Calibre data model"""
	__tablename__ = "calibres"
	# __table_args__ = {"schema": "example"}
	
	id = Column(Integer, primary_key=True, nullable=False)
	name = Column(String(100), nullable=False)
	other_names = Column(ListType, nullable=True)
	bullet_diameter = Column(DecimalType, nullable=True)
	neck_diameter = Column(DecimalType, nullable=True)
	shoulder_diameter = Column(DecimalType, nullable=True)
	base_diameter = Column(DecimalType, nullable=True)
	rim_diameter = Column(DecimalType, nullable=True)
	rim_thickness = Column(DecimalType, nullable=True)
	case_length = Column(DecimalType, nullable=True)
	cartridge_length = Column(DecimalType, nullable=True)
	case_type_rimmed = Column(Integer, nullable=True, default=0)
	case_type_belted = Column(Boolean, nullable=True, default=False)
	case_type_bottleneck = Column(Boolean, nullable=True, default=False)
	case_type_rebated = Column(Boolean, nullable=True, default=False)
	type = Column(String, nullable=False)
	
	def __repr__(self):
		return f'CalibreModel({self.id})'
	
	def __str__(self):
		return self.__repr__()

# class Calibre:
# 	def __init__(
# 			self, name, id=None,
# 			case_type_rimmed=None,
# 			case_type_belted = None,
# 			case_type_bottleneck = None,
# 			case_type_rebated = None,
# 			bullet_diameter = None,
# 			neck_diameter = None,
# 			shoulder_diameter = None,
# 			base_diameter = None,
# 			rim_diameter = None,
# 			rim_thickness = None,
# 			case_length = None,
# 			cartridge_length = None,
# 			):
#
# 	if id:
# 		self.id = int(id)
# 	else
# 		self.id = None
#
#


# Create All Tables
Base.metadata.create_all(engine)