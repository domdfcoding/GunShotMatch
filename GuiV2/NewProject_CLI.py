#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  NewProject_CLI.py
"""
GunShotMatch

Program for the analysis of OGSR samples to identify matching compounds
between samples.

"""
#
#  This file is part of GunShotMatch
#
#  Copyright © 2019 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import sys
import locale

# 3rd party

# this package
from GSMatch.utils.pynist import *
from GuiV2.GSMatch2_Core.NewProject import NewProject

sys.path.append("..")


__author__ = "Dominic Davis-Foster"
__copyright__ = "Copyright 2017-2019 Dominic Davis-Foster"

__license__ = "GPLv3"
__version__ = "1.0.0 Rework"
__email__ = "dominic@davis-foster.co.uk"

program_name = "GunShotMatch"
copyright = __copyright__

# Setup for reading strings with thousand separators as floats
# From https://stackoverflow.com/a/31074271
locale.setlocale(locale.LC_ALL, "")

verbose = False


def parse_arguments():
	"""
	Parse command line switches

	:return:
	"""
	
	import shutil
	import argparse
	parser = argparse.ArgumentParser()
	
	parser.add_argument("--samples", help="List of samples to run.", nargs='+')
	parser.add_argument("--name", help="Human-Readable Name for the Project.")
	parser.add_argument("--info", help="Show program info.", action='store_true')
	parser.add_argument("--default", help="Reload Default configuration.", action='store_true')
	
	args = parser.parse_args()
	
	if len(sys.argv) == 1:
		# logger.warning("No options supplied.")
		print("Error: No options supplied.")
		print('')
		parser.print_help(sys.stderr)
		sys.exit(1)
	
	if args.default:
		print("\nReloading Default Configuration")
		shutil.copyfile("./lib/default.ini", "./config.ini")
		sys.exit(0)
	
	return args


if __name__ == '__main__':
	from utils import timing
	from domdf_python_tools.terminal import clear
	
	clear()  # clear the display
	startup_string = f"""

{program_name} Version {__version__} running on {platform.system()}.
{copyright} Dominic Davis-Foster.
"""
	print(startup_string)
	
	gsm = NewProject()
	
	args = parse_arguments()
	
	if args.samples:
		gsm.config.prefixList = args.samples
	# overrides whatever was set from the config file
	
	# """Define Exit Functions"""
	# if "-h" not in str(sys.argv):
	# 	atexit.register(pynist.reload_ini, nist_path)
	
	if args.name:
		gsm.lot_name = args.name
	
	gsm.run()