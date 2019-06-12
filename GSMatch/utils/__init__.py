#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
"""\
GunShotMatch Utilities Module

Shared Functions for GunShotMatch

Copyright 2018, 2019 Dominic Davis-Foster <dominic@davis-foster.co.uk>

This package is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
MA 02110-1301, USA.

Copyright for other files in this module:

utils.charts:

mean_peak_area, mean_peak_area_multiple and peak_area adapted from
    https://python-graph-gallery.com/13-percent-stacked-barplot/
    Copyright (C) 2017 The python graph gallery

radar_chart adapted from https://python-graph-gallery.com/391-radar-chart-with-several-individuals/
    Copyright (C) 2017 The python graph gallery

PlotSpectrum adapted from SpectrumSimilarity.R
    Part of OrgMassSpecR
    Copyright Nathan Dodder <nathand@sccwrp.org>
-----

utils.ChromatogramDisplay:
    Adapted from PyMS in 2019 by Dominic Davis-Foster
    Copyright (C) 2005-2012 Vladimir Likic
    Available under the GNU GPL Version 2
-----

utils.DirectoryHash:
    Copyright 2009 Stephen Akiki.
    http://akiscode.com/articles/sha-1directoryhash.shtml
    Available under the MIT License
-----

utils.jcamp:
    Copyright (c) 2013 Nathan Hagen <and.the.light.shattered@gmail.com>
    Available under the MIT License
-----

utils.MassSpectraPlot
    Copyright 2015 Martin N.
    https://github.com/matrixx567/MassSpectraPlot
    Available under the MIT Licence.
    Adapted in 2017 by Dominic Davis-Foster.
-----

utils.mathematical:
    RepresentsInt from https://stackoverflow.com/questions/1265665/python-check-if-a-string-represents-an-int-without-using-try-except
        Copyright 2009 Triptych
        Licensed Under CC-BY-SA
-----

utils.progbar:
	Based on http://wxpython-users.1045709.n5.nabble.com/Gauge-in-Statusbar-td2321906.html
	Copyright 2005 Ray Pasco
	Adapted in 2019 by Dominic Davis-Foster
-----

utils.pubchempy:
	Copyright Matt Swain <m.swain@me.com>
	Available under the MIT License
	Adapted in 2019 by Dominic Davis-Foster
-----

utils.pynist:
    generate_ini contains the .ini file from NIST MS Search
        Copyright NIST
-----

utils.SpectrumSimilarity:
    Originally from SpectrumSimilarity.R
    Part of OrgMassSpecR
    Copyright 2011-2017 Nathan Dodder <nathand@sccwrp.org>
    Adapted in 2019 by Dominic Davis-Foster
-----

utils.spreadsheet:
    convert_to_xlsx from http://coderscrowd.com/app/public/codes/view/201
        Copyright 2014 Tim Kacprowski
-----

utils.timing:
    Copyright 2009 PaulMcG
    From http://stackoverflow.com/a/1557906/6009280
    Licensed under CC-BY-SA
    Adapted 2018 by Dominic Davis-Foster
-----

"""

__all__ = ["charts",
		   "DirectoryHash",
		   "jcamp",
		   "MassSpectraPlot",
		   "mathematical",
		   "progbar",
		   "pynist",
		   "SpectrumSimilarity",
		   "utils",
		   "timing",
		   "uibar",
		   ]

