#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
#  Copyright (c) 2017-2019 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
#



__all__ = ["AboutDialog",
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
		   "LogCtrl",
		   "My_Axes",
		   "paths_dialog",
		   "style_picker",
		   "thread_boilerplates",
		   "threads",
		   ]

from . import constants
from .Config import GSMConfig
from . import My_Axes
from . import PeakAlignment


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
	return (inferred_samples)



if __name__ == '__main__':
	print(infer_samples("./Results/CSV/"))