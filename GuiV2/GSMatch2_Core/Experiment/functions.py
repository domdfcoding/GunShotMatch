#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  Functions.py
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

from mathematical.utils import rounders
from GuiV2.GSMatch2_Core.Config import internal_config
import os


def create_msp(sample_name, mass_list, mass_spec):
	"""
	Generate .MSP files for NIST MS Search

	:param sample_name: The name of the sample
	:type sample_name: str
	:param mass_list:
	:type mass_list:
	:param mass_spec:
	:type mass_spec:
	"""
	
	print(os.path.join(internal_config.msp_dir, sample_name + ".MSP"))
	msp_file = open(os.path.join(internal_config.msp_dir, sample_name + ".MSP"), "w")
	msp_file.write("Name: {}\n".format(sample_name))
	msp_file.write("Num Peaks: {}\n".format(len(mass_list)))
	for mass, intensity in zip(mass_list, mass_spec):
		msp_file.write("{} {},\n".format(rounders(mass, "0.0"), intensity))
	msp_file.close()