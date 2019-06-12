#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  install.py
#  
#  Copyright 2019 dom13 <dom13@DOM-XPS>
"""
This file is a work in progress.
Proceed with Caution.

GunShotMatch post-install script
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

def test_wx():
	# wxPython
	import platform, os
	if platform.system() != "Linux":
		return 0
		
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
	
	if not need_install:
		return 0
	
	import webbrowser
	
	print("""There are some prebuilt wheels available. If you have a Linux similar enough to those used to build the wheels you can use them and not need to build the wheels yourself.""")
	print("Do you want to view the [w]heels, view the [s]ource code, or abort (x)? ")
	result = input("Alternatively, type then name of your Linux distribution and we'll do our best to sort you out")
	if result[0] == "w":
		webbrowser.open("https://extras.wxpython.org/wxPython4/extras/linux/", 2)
	elif result[0] == "s":
		webbrowser.open("https://github.com/wxWidgets/Phoenix", 2)
	elif result.lower().replace(".",'').replace(' ','') == "ubuntu1804":
		os.system("pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-18.04 wxPython")
		os.system(
			"wget -q -O /tmp/libpng12.deb http://mirrors.kernel.org/ubuntu/pool/main/libp/libpng/libpng12-0_1.2.54-1ubuntu1_amd64.deb && dpkg -i /tmp/libpng12.deb && rm /tmp/libpng12.deb")
	elif result.lower().replace(".",'').replace(' ','') == "ubuntu1604":
		os.system("pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-16.04 wxPython")
		os.system(
			"wget -q -O /tmp/libpng12.deb http://mirrors.kernel.org/ubuntu/pool/main/libp/libpng/libpng12-0_1.2.54-1ubuntu1_amd64.deb && dpkg -i /tmp/libpng12.deb && rm /tmp/libpng12.deb")
	elif result.lower().replace(".",'').replace(' ','') == "ubuntu1404":
		os.system("pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-14.04 wxPython")

	elif result.lower().replace(".",'').replace(' ','') == "debian9":
		os.system("pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/debian-9 wxPython")
	elif result.lower().replace(".",'').replace(' ','') == "debian8":
		os.system("pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/debian-8 wxPython")
	elif result.lower().replace(".",'').replace(' ','') == "debian8":
		os.system("pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/debian-8 wxPython")
	
	elif result.lower().replace(".",'').replace(' ','') == "fedora23":
		os.system("pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/fedora-23 wxPython")
	elif result.lower().replace(".",'').replace(' ','') == "fedora26":
			os.system("pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/fedora-26 wxPython")
	elif result.lower().replace(".",'').replace(' ','') == "fedora27":
			os.system("pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/fedora-27 wxPython")
	elif result.lower().replace(".",'').replace(' ','') == "fedora28":
			os.system("pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/fedora-28 wxPython")
	elif result.lower().replace(".",'').replace(' ','') == "fedora24":
			os.system("pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/fedora-24 wxPython")
	
	elif result.lower().replace(".",'').replace(' ','') == "centos7":
			os.system("pip install -U -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/centos-7 wxPython")

	else:
		return 1
		
	
def patch_openpyxl():
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
	test_wx()
	patch_openpyxl()
	
