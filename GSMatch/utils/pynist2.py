#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  pynist2.py
"""
Python Interface to NIST MS Search
"""
#
#  This file is part of GunShotMatch
#
#  Copyright © 2018-2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  generate_ini contains the .ini file from NIST MS Search
#      Copyright NIST
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
#  Requires NIST MS Search to be installed on your computer.
#  A fully functional demo version is available from:
#       http://chemdata.nist.gov/mass-spc/ms-search/
#
#  Makes calls to the NIST MS Search API as described here:
#       http://chemdata.nist.gov/mass-spc/ms-search/docs/Ver20Man_11.pdf


__author__ = "Dominic Davis-Foster"
__copyright__ = "Copyright 2018 Dominic Davis-Foster"

__license__ = "GPLv3"
__version__ = 0.25
__email__ = "dominic@davis-foster.co.uk"

# stdlib
import io
import os
import platform
import shutil
import sys
import time
from subprocess import PIPE, Popen

# 3rd party
from domdf_python_tools.paths import parent_path

# this package
from GSMatch.utils.pynist import generate_ini, nistError, reload_ini

generate_ini = generate_ini
reload_ini = reload_ini
nistError = nistError


class PyNist(object):
	def __init__(self, nistpath=None):
		self._nistpath = nistpath
	
	def check_nistpath(self):
		if not self._nistpath:
			raise ValueError("'nistpath' not set")
	
	def test(self):
		self.check_nistpath()
		print("foo")
	
	def force_close(self):
		"""
		Closes NIST MS Search (the hard way)
		"""
		args = []
		if platform.system() == "Linux":
			args.append("wine")
		Popen(args + ["Taskkill", "/IM", "nistms.exe", "/F"], stdout=PIPE, stderr=PIPE)
	
	def cleanup(self):
		import platform
		
		for filename in os.listdir(self._nistpath):
			if os.path.splitext(filename)[-1].upper() == ".HLM":
				os.unlink(os.path.join(self._nistpath, filename))
		
		locator_path = open(os.path.join(self._nistpath, "AUTOIMP.MSD"), "r").read()
		
		if platform.system() == "Linux":
			import getpass
			locator_path = "/home/{}/.wine/drive_c/SEARCH/SEARCH.MSD".format(getpass.getuser())
		
		while locator_path[0] == ' ':
			locator_path = locator_path[1:]
		locator_path = parent_path(locator_path)
		
		for filename in os.listdir(locator_path):
			for prefix in prefixList:
				if prefix in filename:
					os.unlink(os.path.join(os.path.abspath(locator_path), filename))
	
	def search(self, spectrum, search_len=1):
		attempts = 101
		while True:  # attempts > 100:
			attempts = 0
			# if type(spectrum) == dict
			# still needs to be coded to convert from dictionary or list to MSP
			spectrum_file = os.path.basename(spectrum)
			file_extension = os.path.splitext(spectrum)[-1]
			# still needs coding to convert from xy to msp.
			# if file_extension.lower() == ".msp":
			
			spectrum_name = os.path.splitext(spectrum_file)[0]
			
			if not os.path.exists(os.path.join(self._nistpath, "AUTOIMP.MSD")):
				if not os.path.isdir("C:/SEARCH/"):
					os.makedirs("C:/SEARCH/")
				with open(os.path.join(self._nistpath, "AUTOIMP.MSD"), "w") as f:
					f.write("C:/SEARCH/SEARCH.MSD")
			
			locator_path = open(os.path.join(self._nistpath, "AUTOIMP.MSD"), "r").read()
			
			if platform.system() == "Linux":
				import getpass
				with open(os.path.join(self._nistpath, "AUTOIMP.MSD"), "w") as f:
					f.write("C:/SEARCH/SEARCH.MSD")
				locator_path = "/home/{}/.wine/drive_c/SEARCH/SEARCH.MSD".format(getpass.getuser())
			
			while locator_path[0] == ' ':
				locator_path = locator_path[1:]
			
			if not os.path.exists(parent_path(locator_path)):
				os.makedirs(parent_path(locator_path))
			
			shutil.copyfile(spectrum, os.path.join(parent_path(locator_path), spectrum_file))
			
			with open(locator_path, "w") as f:
				f.write(os.path.join(parent_path(locator_path), spectrum_file))
			
			if os.path.exists(os.path.join(self._nistpath, "SRCREADY.TXT")):
				os.unlink(os.path.join(self._nistpath, "SRCREADY.TXT"))
			if os.path.exists(os.path.join(self._nistpath, "SRCRESLT.TXT")):
				os.unlink(os.path.join(self._nistpath, "SRCRESLT.TXT"))
			
			if platform.system() == "Linux":
				Popen(["wine", os.path.join(self._nistpath, "nistms$.exe"), "/par=2"], stdout=PIPE, stderr=PIPE)
			else:
				Popen([os.path.join(self._nistpath, "nistms$.exe"), "/par=2"], stdout=PIPE, stderr=PIPE)
			
			time.sleep(2 + (0.2 * search_len))
			
			# From https://www.quora.com/How-can-I-delete-the-last-printed-line-in-Python-language
			print("\r\033[K", end=''),  # clear line
			while not os.path.isfile(os.path.join(self._nistpath, "SRCREADY.TXT")):
				# print(attempts)
				time.sleep(0.2)
				# sys.stdout.write("\rWaiting for SRCREADY.TXT. Attempt {}".format(attempts))
				print("\rWaiting for SRCREADY.TXT. Attempt {}\r".format(attempts), end='')
				attempts += 1
				if attempts > 300:
					print("\rclosing nist line {}\r".format(sys._getframe().f_lineno), end='')
					self.force_close()
					search_results = ''
					continue
			
			searches_done = 0
			while searches_done != str(search_len):
				ready_file = open(os.path.join(self._nistpath, "SRCREADY.TXT"))
				searches_done = ready_file.readlines()[0].rstrip("\r\n").replace("\n", "").replace("\r", "")
				# print(searches_done)
				ready_file.close()
				# sys.stdout.write(
				# 		"\rWaiting for searches to finish. Currently {}/{} done. Attempt {}".format(
				# 				int(searches_done), int(search_len), int(attempts)
				# 				)
				# 		)
				print(
						f"\r\rWaiting for searches to finish. Currently {int(searches_done)}/{int(search_len)} done. "
						f"Attempt {int(attempts)}\r", end=''),
				time.sleep(0.5)
				attempts += 1
				if attempts > 300:
					print("\rclosing nist line {}\r".format(sys._getframe().f_lineno), end='')
					self.force_close()
					continue
			
			while not os.path.exists(os.path.join(self._nistpath, "SRCRESLT.TXT")):
				time.sleep(0.2)
				print("\rWaiting for SRCRESLT.TXT, Attempt {}\r".format(attempts), end='')
				attempts += 1
				if attempts > 300:
					print("\rclosing nist line {}\r".format(sys._getframe().f_lineno), end='')
					self.force_close()
					continue
			
			# search_results = open(os.path.join(nist_dir,"SRCRESLT.TXT"),"rt",encoding="latin-1").read() #
			search_results = io.open(os.path.join(self._nistpath, "SRCRESLT.TXT"), "rt", encoding="latin-1").read()  #
			print(search_results)
			try:
				os.unlink(os.path.join(self._nistpath, "SRCRESLT.TXT"))
				os.unlink(os.path.join(self._nistpath, "SRCREADY.TXT"))
			except:
				pass
			
			if len(search_results) == 0:
				print("\rclosing nist line {}\r".format(sys._getframe().f_lineno), end='')
				self.force_close()
				time.sleep(0.5)
			else:
				time.sleep(0.5)
				break
		
		time.sleep(0.5)
		
		# try:
		# 	os.unlink(os.path.join(nist_dir,"SRCRESLT.TXT"))
		# except:
		# 	time.sleep(2)
		# 	os.unlink(os.path.join(nist_dir,"SRCRESLT.TXT"))
		
		return search_results


p = PyNist()
p.test()


if __name__ == '__main__':
	sys.exit(1)
