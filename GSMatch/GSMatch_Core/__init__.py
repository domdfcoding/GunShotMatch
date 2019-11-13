#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  __init__.py
"""GunShotMatch Core Components"""
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2017-2019 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
#
#
# Copyright for other files in this module:
#
# utils.charts:
#
# mean_peak_area, mean_peak_area_multiple and peak_area adapted from
#     https://python-graph-gallery.com/13-percent-stacked-barplot/
#     Copyright (C) 2017 The python graph gallery
#
# radar_chart adapted from https://python-graph-gallery.com/391-radar-chart-with-several-individuals/
#     Copyright (C) 2017 The python graph gallery
#
# PlotSpectrum adapted from SpectrumSimilarity.R
#     Part of OrgMassSpecR
#     Copyright Nathan Dodder <nathand@sccwrp.org>
# -----
#
# utils.ChromatogramDisplay:
#     Adapted from PyMS in 2019 by Dominic Davis-Foster
#     Copyright (C) 2005-2012 Vladimir Likic
#     Available under the GNU GPL Version 2
# -----



__all__ = [
	"AboutDialog",
	"border_config",
	"browse_tab",
	"ChartViewer",
	"ChromatogramDisplay",
	"compare_tab",
	"Comparison",
	"constants",
	"Config",
	"help_tab",
	"Launcher",
	"launcher_tab",
	"My_Axes",
	"paths_dialog",
	"thread_boilerplates",
	"threads",
]


from GSMatch.GSMatch_Core.Config import GSMConfig

from . import constants, My_Axes, PeakAlignment


def read_peaks_json(jsonfile):
	import json
	return [json.loads(x) for x in open(jsonfile, "r").readlines()]


def pretty_name_from_info(infofile):
	import os
	return os.path.splitext(os.path.split(infofile)[-1])[0]


def infer_samples(csvpath):
	import os
	
	inferred_samples = []
	directory_listing = os.listdir(csvpath)
	for filename in directory_listing:
		# if filename.lower().endswith(".csv"):
		if filename.endswith("GC_80.CSV"):
			# print filename[:-9]+'MS_80.CSV'
			if os.path.isfile(os.path.join(csvpath, filename[:-9] + 'MS_80.CSV')):
				inferred_samples.append(filename[:-10])
	
	inferred_samples.sort()
	return inferred_samples


if __name__ == '__main__':
	print(infer_samples("./Results/CSV/"))
