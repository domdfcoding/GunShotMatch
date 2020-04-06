#!/usr/bin/env python
# -*- coding: utf-8 -*-

# http://akiscode.com/articles/sha-1directoryhash.shtml
# Copyright © 2009 Stephen Akiki
# Copyright © 2019 Dominic Davis-Foster
# MIT License (Means you can do whatever you want with this)
#  See http://www.opensource.org/licenses/mit-license.php
# Error Codes:
#   -1 -> Directory does not exist
#   -2 -> General error (see stack traceback)


def GetHashofDirs(directory, verbose=0):
	import hashlib, os
	SHAhash = hashlib.sha1()
	if not os.path.exists(directory):
		return -1
	
	try:
		for root, dirs, files in os.walk(directory):
			for names in files:
				if verbose == 1:
					print('Hashing', names)
				filepath = os.path.join(root, names)
				try:
					with open(filepath, 'rb') as f1:
						while 1:
							# Read file in as little chunks
							buf = f1.read(4096)
							if not buf:
								break
							SHAhash.update(hashlib.sha1(buf).hexdigest().encode("utf-8"))
				except:
					# You can't open the file for some reason
					continue
	
	except:
		import traceback
		# Print the stack traceback
		traceback.print_exc()
		return -2
	
	return SHAhash.hexdigest()
