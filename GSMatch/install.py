#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  install.py
#  
#  Copyright 2019 dom13 <dom13@DOM-XPS>
"""
This file is a work in progress.
Proceed with Caution.
"""
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
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
#  

import pip


# Required Modules and Versions
dependencies = {
	'matplotlib':"2.2.3",
	'numpy':'1.16.0',
	'openpyxl':'2.5.12',
	'pandas':'0.23.4', 
#	'pillow':'5.1.0',
	'progressbar2':'3.39.2',
	'scipy':'1.2.0',
}

def install():
	# get list of currently installed packages
	installed_packages = pip.get_installed_distributions()
	installed_packages_list = sorted(["%s==%s" % (i.key, i.version)
		 for i in installed_packages])
	
	installed_versions = {}
	missing_modules = []
	
	for i in installed_packages:
		installed_versions[i.key] = i.version
	
		
	for module in dependencies:
		required_version = dependencies[module]
		if module in installed_versions:
			current_version = installed_versions[module]
		else:
			current_version = 0
		
		if required_version > current_version:
			print("{} > {} is required, but {}".format(module, required_version, 'it is not installed.' if current_version==0 else '{} is installed.'.format(current_version)))
			missing_modules.append(module)
		
	if missing_modules == []:
		print("All modules are up to date.")
	else:	
		print("""\nThe following modules are going to be installed:
{}""".format(' '.join(missing_modules)))
		result = raw_input("Do you want to continue? [Y/n] ").lower()
		if result.startswith('y') or len(result) == 0:
			for module in missing_modules:
				pip.main(['install', '{}>={}'.format(module, dependencies[module])])

		else:
			print("Abort.")
	
	# wxPython
	
	need_install = False
		
	try:
		import wx
		print(int(wx.version()[0])<4)
		if int(wx.version()[0]) < 4:
			need_install = True
		print("wxPython Version 4 or greater is required, but {} is installed.".format(wx.version()[:5]))
	except:
		need_install = True
		print("wxPython Version 4 or greater is required, but it is not installed.")
		
	if need_install:
		print("Installing wxPython. Please wait...")
		 
		import platform, os
		if platform.system() == "Linux":
			os.system("pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-16.04 wxPython")		
		
			os.system("wget -q -O /tmp/libpng12.deb http://mirrors.kernel.org/ubuntu/pool/main/libp/libpng/libpng12-0_1.2.54-1ubuntu1_amd64.deb && dpkg -i /tmp/libpng12.deb && rm /tmp/libpng12.deb")

		else:
			os.system("python pip install -U wxPython")
	
		
	# Patch openpyxl
	import openpyxl
	import os.path
	opxl_path =  os.path.split(openpyxl.__file__)[0]
	#print opxl_path
	
	if not os.path.isfile(os.path.join(opxl_path,"GSM_Patch.txt")):
		print("Patching openpyxl. Please wait...")
		
		import shutil
		
		for directory in os.listdir("lib/openpyxl-patch"):
			print(directory)
			for filename in os.listdir(os.path.join("lib/openpyxl-patch",directory)):
				print(filename)
				original_file = os.path.join(opxl_path,directory,filename) # original file
				backup_file = os.path.join(opxl_path,directory,(filename+".bak")) # backup of original file
				patched_file = os.path.join("lib/openpyxl-patch",directory,filename) # patched file
				
				shutil.move(original_file, backup_file)
				shutil.copy(patched_file, original_file)
		
		with open(os.path.join(opxl_path,"GSM_Patch.txt"), 'w') as f:
			f.write("GunShotMatch patch for openpyxl installed. The original versions have been preserved with .py.bak extensions.")
	
	else:
		print("openpyxl is already patched.")

if __name__ == '__main__':
	import sys
	sys.exit(install())
