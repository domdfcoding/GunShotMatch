#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  __init__.py
#
#  This file is part of GunShotMatch
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import pathlib

# 3rd party
from sqlalchemy import create_engine


# Create engine
db_uri = f"sqlite:///{pathlib.Path(__file__).parent / 'calibres.db'}"

engine = create_engine(db_uri)

__all__ = [
		"engine",
		"db_uri"
		]

