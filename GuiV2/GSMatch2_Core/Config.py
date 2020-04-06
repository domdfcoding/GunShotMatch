#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Config.py
"""GunShotMatch configuration classes"""
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
import atexit
import configparser
import pathlib
import sys

# 3rd party
import appdirs
from domdf_python_tools.paths import maybe_make, relpath2
from domdf_wxpython_tools.ColourPickerPanel import default_colours
from domdf_wxpython_tools.StylePickerPanel import default_styles

# this package

# TODO: pathlib support

homedir = pathlib.Path.home()


def parse_directory(directory):
	"""

	:type directory: str or pathlib.Path
	"""
	
	if not isinstance(directory, pathlib.Path):
		directory = pathlib.Path(directory)
	
	if directory:
		if directory.is_file():
			return directory.parent
		else:
			return directory
	else:
		return homedir


class InternalConfig:
	"""
	GunShotMatch Internal Configuration Class
	"""
	
	def __init__(self):
		"""
		Initialise GunShotMatch configuration
		"""
		
		self._configfile = pathlib.Path(appdirs.user_config_dir("GunShotMatch")) / "internal_config.ini"
		self.Config = configparser.ConfigParser()
		self.recent_projects = []

		if not self._configfile.is_file():
			print("Creating Internal Configuration file")
			self.__load_defaults()
		else:
			print("Loading Internal Configuration")
			self._load_from_file()
			
	def __load_defaults(self):
		# Touch file
		maybe_make(self._configfile.parent)
		
		self._configfile.write_text("""
[main]

[paths]

[recent_projects]

[charts]
		""")
		
		self._load_from_file()
		return
	
	def _load_from_file(self):
		self.Config.read(self.configfile)
		
		if "main" not in self.Config:
			self.Config["main"] = {}
		if "paths" not in self.Config:
			self.Config["paths"] = {}
		if "recent_projects" not in self.Config:
			self.Config["recent_projects"] = {}
		if "charts" not in self.Config:
			self.Config["charts"] = {}
			
		self.nist_path = self.Config.get("paths", "NistPath", fallback=homedir.absolute())
		
		# Directories
		self.csv_dir = pathlib.Path(self.Config.get(
				"paths", "CSVPath",
				fallback=(homedir / "Documents" / "GunShotMatch" / "CSV Reports")
				)).absolute()
		self.spectra_dir = pathlib.Path(self.Config.get(
				"paths", "SpectraPath",
				fallback=(homedir / "Documents" / "GunShotMatch" / "Spectra Images")
				)).absolute()
		self.charts_dir = pathlib.Path(self.Config.get(
				"paths", "ChartsPath",
				fallback=(homedir / "Documents" / "GunShotMatch" / "Charts")
				)).absolute()
		self.msp_dir = pathlib.Path(self.Config.get(
				"paths", "MSPPath",
				fallback=(homedir / "Documents" / "GunShotMatch" / "MSP Files")
				)).absolute()
		self.results_dir = pathlib.Path(self.Config.get(
				"paths", "ResultsPath",
				fallback=(homedir / "Documents" / "GunShotMatch" / "Results")
				)).absolute()
		self.log_dir = pathlib.Path(self.Config.get(
				"paths", "logdir",
				fallback=(homedir / "Documents" / "GunShotMatch" / "Logs")
				)).absolute()
		
		# Recent Projects
		for i in range(9, -1, -1):
			self.add_recent_project(*(self.Config.get(
					"recent_projects", f"recent{i}",
					fallback=',.'
					).split(",")))
		
		# Main
		self.show_welcome_dialog = self.Config.getboolean(
				"main", "show_welcome_dialog",
				fallback=True)
		self.exit_on_closing_welcome_dialog = self.Config.getboolean(
				"main", "exit_on_closing_welcome_dialog",
				fallback=False)
		self.last_project = self.Config.get(
				"main", "last_project",
				fallback=homedir)
		self.last_experiment = self.Config.get(
				"main", "last_experiment",
				fallback=homedir)
		self.last_datafile = self.Config.get(
				"main", "last_datafile",
				fallback=homedir)
		self.last_method = self.Config.get(
				"main", "last_method",
				fallback=homedir)
		self.last_ammo = self.Config.get(
				"main", "last_ammo",
				fallback=homedir)
		self.last_export = self.Config.get(
				"main", "last_export",
				fallback=homedir)
		self.last_maximized = self.Config.get(
				"main", "last_maximized",
				fallback=True)
		self.last_size = tuple(int(x) for x in self.Config.get(
				"main", "last_size",
				fallback="-1, -1").split(","))
		self.last_position = tuple(int(x) for x in self.Config.get(
				"main", "last_position",
				fallback="-1, -1").split(","))
		
		# Charts
		self.chart_styles = self.Config.get(
				"charts", "styles",
				fallback=default_styles[:])
		if isinstance(self.chart_styles, str):
			self.chart_styles = self.chart_styles.split(",")
		
		self.chart_colours = self.Config.get(
				"charts", "colours",
				fallback=default_colours[:])
		if isinstance(self.chart_colours, str):
			self.chart_colours = [f"#{colour}" for colour in self.chart_colours.split(",")]
			
	@property
	def configfile(self):
		"""
		Returns the path of the .ini file from which the configuration was loaded

		:return: Configuration file path
		:rtype: str
		"""
		
		return self._configfile
	
	@property
	def nist_path(self):
		"""
		Returns the path of the NIST MS Search program

		:rtype: str
		"""
		return str(self._nist_path)
	
	@nist_path.setter
	def nist_path(self, value):
		"""
		Sets the path to the NIST MS Search program

		:type value: str or pathlib.Path
		"""
		
		if value:
			if not isinstance(value, pathlib.Path):
				value = pathlib.Path(value)
		
			self._nist_path = value
	
	@property
	def csv_dir(self):
		"""
		Returns the directory where CSV reports will be stored

		:rtype: str
		"""
		
		return str(self._csv_dir)
	
	@csv_dir.setter
	def csv_dir(self, value):
		"""
		Sets the directory where CSV reports will be stored.
		The directory will be created if it does not already exist.

		:type value: str or pathlib.Path
		"""
		
		if value:
			if not isinstance(value, pathlib.Path):
				value = pathlib.Path(value)
			
			self._csv_dir = value
			maybe_make(self._csv_dir)
	
	@property
	def spectra_dir(self):
		"""
		Returns the directory where Mass Spectra images will be stored

		:rtype: str
		"""
		
		return str(self._spectra_dir)
	
	@spectra_dir.setter
	def spectra_dir(self, value):
		"""
		Sets the directory where Mass Spectra images will be stored.
		The directory will be created if it does not already exist.

		:type value: str or pathlib.Path
		"""
		
		if value:
			if not isinstance(value, pathlib.Path):
				value = pathlib.Path(value)
				
			self._spectra_dir = value
			maybe_make(self._spectra_dir)
	
	@property
	def charts_dir(self):
		"""
		Returns the directory where Charts will be stored

		:rtype: str
		"""
		
		return str(self._charts_dir)
	
	@charts_dir.setter
	def charts_dir(self, value):
		"""
		Sets the directory where Charts will be stored.
		The directory will be created if it does not already exist.

		:type value: str or pathlib.Path
		"""
		
		if value:
			if not isinstance(value, pathlib.Path):
				value = pathlib.Path(value)
				
			self._charts_dir = value
			maybe_make(self._charts_dir)
	
	@property
	def msp_dir(self):
		"""
		Returns the directory where MSP files for NIST MS Search will be stored

		:rtype: str
		"""
		
		return str(self._msp_dir)
	
	@msp_dir.setter
	def msp_dir(self, value):
		"""
		Sets the directory where MSP files for NIST MS Search will be stored.
		The directory will be created if it does not already exist.

		:type value: str or pathlib.Path
		"""
		
		if value:
			if not isinstance(value, pathlib.Path):
				value = pathlib.Path(value)
				
			self._msp_dir = value
			maybe_make(self._msp_dir)
	
	@property
	def results_dir(self):
		"""
		Returns the directory where Results will be stored

		:rtype: str
		"""
		
		return str(self._results_dir)
	
	@results_dir.setter
	def results_dir(self, value):
		"""
		Sets the directory where Results will be stored.
		The directory will be created if it does not already exist.

		:type value: str or pathlib.Path
		"""
		
		if value:
			if not isinstance(value, pathlib.Path):
				value = pathlib.Path(value)
			
			self._results_dir = value
			maybe_make(self._results_dir)
	
	@property
	def log_dir(self):
		"""
		Returns the directory where log files will be stored

		:rtype: str
		"""
		
		return str(self._log_dir)
	
	@log_dir.setter
	def log_dir(self, value):
		"""
		Sets the directory where log files will be stored.
		The directory will be created if it does not already exist.

		:type value: str or pathlib.Path
		"""
		
		if value:
			if not isinstance(value, pathlib.Path):
				value = pathlib.Path(value)
			
			self._log_dir = value
			maybe_make(self._log_dir)
	
	@property
	def last_experiment(self):
		"""
		
		:rtype: str
		"""
		
		return str(self._last_experiment)
	
	@last_experiment.setter
	def last_experiment(self, value):
		"""
		
		:type value: str or pathlib.Path
		"""
		
		self._last_experiment = parse_directory(value)
		# if not isinstance(value, pathlib.Path):
		# 	value = pathlib.Path(value)
		#
		# if value:
		# 	if value.is_file():
		# 		self._last_experiment = value.parent
		# 	else:
		# 		self._last_experiment = value
		# else:
		# 	self._last_experiment = homedir
		
	@property
	def last_ammo(self):
		"""

		:rtype: str
		"""

		return self._last_ammo
	
	@last_ammo.setter
	def last_ammo(self, value):
		"""
		
		:type value: str or pathlib.Path
		"""
		
		self._last_ammo = parse_directory(value)
		# if not isinstance(value, pathlib.Path):
		# 	value = pathlib.Path(value)
		#
		# if value:
		# 	if value.is_file():
		# 		self._last_ammo = value.parent
		# 	else:
		# 		self._last_ammo = value
		# else:
		# 	self._last_ammo = homedir
			
	@property
	def last_export(self):
		"""

		:rtype: str
		"""

		return self._last_export
	
	@last_export.setter
	def last_export(self, value):
		"""
		
		:type value: str or pathlib.Path
		"""
		
		self._last_export = parse_directory(value)
	
	@property
	def last_method(self):
		"""

		:rtype: str
		"""
		
		return self._last_method
	
	@last_method.setter
	def last_method(self, value):
		"""
		
		:type value: str or pathlib.Path
		"""
		
		if not isinstance(value, pathlib.Path):
			value = pathlib.Path(value)
		
		if value:
			if value.is_file():
				self._last_method = value.parent
			else:
				self._last_method = value
		else:
			self._last_method = homedir
			
	@property
	def last_project(self):
		"""

		:rtype: str
		"""
		
		return self._last_project
	
	@last_project.setter
	def last_project(self, value):
		"""
		
		:type value: str or pathlib.Path
		"""
		
		if not isinstance(value, pathlib.Path):
			value = pathlib.Path(value)
		
		if value:
			if value.is_file():
				self._last_project = value.parent
			else:
				self._last_project = value
		else:
			self._last_project = homedir\
	
	@property
	def chart_colours(self):
		"""

		:rtype: str
		"""
		
		return self._chart_colours
	
	@chart_colours.setter
	def chart_colours(self, value):
		self._chart_colours = value
		
	@property
	def chart_styles(self):
		
		return self._chart_styles
	
	@chart_styles.setter
	def chart_styles(self, value):
		self._chart_styles = value
			
	@property
	def last_datafile(self):
		"""

		:rtype: str
		"""
		
		return self._last_datafile
	
	@last_datafile.setter
	def last_datafile(self, value):
		"""
		
		:type value: str or pathlib.Path
		"""
		
		if not isinstance(value, pathlib.Path):
			value = pathlib.Path(value)
		
		if value:
			if value.is_file():
				self._last_datafile = value.parent
			else:
				self._last_datafile = value
		else:
			self._last_datafile = homedir
	
	@property
	def recent_projects(self):
		recent_projects = self._recent_projects[:10]
		
		while len(recent_projects) < 10:
			recent_projects.append(("", "."))
		
		return recent_projects
	
	@recent_projects.setter
	def recent_projects(self, value):
		self._recent_projects = []
		
		for recent_proj in value:
			self._recent_projects.append((str(recent_proj[0]), str(recent_proj[1])))
		
		#self._recent_projects = value
	
	def add_recent_project(self, name, filename):
		# Check that the file exists
		if not pathlib.Path(filename).is_file():
			return
		
		# If the project is already in the recent projects remove it
		self._recent_projects = [
			project for project in self._recent_projects
			if (project[0] != name and project[1] != filename)
			or project[1] == "."
			]
		
		self._recent_projects.insert(0, (name, str(filename)))
	
	def remove_recent_project(self, idx=None, name=None, filename=None):
		
		if idx is not None:
			del self._recent_projects[idx]
		
		elif name and filename:
			
			# If the project is already in the recent projects remove it
			self._recent_projects = [
				project for project in self._recent_projects
				if (project[0] != name and project[1] != filename)
				or project[1] == "."
				]
		
		else:
			raise SyntaxError("Must supply an index of the project to remove, or supply both its name and filename.")
		
		self._recent_projects.append(("", "."))
	
	@property
	def show_welcome_dialog(self):
		return self._show_welcome_dialog
	
	@show_welcome_dialog.setter
	def show_welcome_dialog(self, value):
		if isinstance(value, str):
			if value == "True":
				self._show_welcome_dialog = True
			if value == "False":
				self._show_welcome_dialog = False
		else:
			self._show_welcome_dialog = bool(value)
	
	@property
	def last_maximized(self):
		return self._last_maximized
	
	@last_maximized.setter
	def last_maximized(self, value):
		self._last_maximized = bool(value)
		
	@property
	def last_position(self):
		return self._last_position
	
	@last_position.setter
	def last_position(self, value):
		self._last_position = value
		
	@property
	def last_size(self):
		return self._last_size
	
	@last_size.setter
	def last_size(self, value):
		self._last_size = value
	
	def save_config(self):
		"""
		Saves the configuration
		"""
		
		# Configuration
		self.Config.set("paths", "NistPath", self.nist_path.replace("\\", "/"))
		
		def process_path(path):
			return str(relpath2(path)).replace("\\", "/")
		
		self.Config.set("paths", "csvpath", process_path(self.csv_dir))
		self.Config.set("paths", "spectrapath", process_path(self.spectra_dir))
		self.Config.set("paths", "chartspath", process_path(self.charts_dir))
		self.Config.set("paths", "msppath", process_path(self.msp_dir))
		self.Config.set("paths", "resultspath", process_path(self.results_dir))
		self.Config.set("paths", "logdir", process_path(self.log_dir))
		
		# Recent projects
		for i in range(9, -1, -1):
			recent_project = self.recent_projects[i]
			project_name = recent_project[0]
			filename = str(recent_project[1])
			self.Config.set("recent_projects", f"recent{i}", f"{project_name},{filename}")
			self.Config.set("recent_projects", f"recent{i}", ",".join(self.recent_projects[i]))
		
		# Main
		self.Config.set("main", "show_welcome_dialog", str(self.show_welcome_dialog))
		self.Config.set("main", "exit_on_closing_welcome_dialog", str(self.exit_on_closing_welcome_dialog))
		self.Config.set("main", "last_project", str(self.last_project))
		self.Config.set("main", "last_datafile", str(self.last_datafile))
		self.Config.set("main", "last_method", str(self.last_method))
		self.Config.set("main", "last_experiment", str(self.last_experiment))
		self.Config.set("main", "last_export", str(self.last_export))
		self.Config.set("main", "last_ammo", str(self.last_ammo))
		self.Config.set("main", "last_maximized", str(self.last_maximized))
		self.Config.set("main", "last_size", ",".join([str(x) for x in self.last_size]))
		self.Config.set("main", "last_position", ",".join([str(x) for x in self.last_position]))
		
		# Charts
		self.Config.set("charts", "styles", ",".join(self.chart_styles))
		self.Config.set("charts", "colours", ",".join(self.chart_colours).replace("#", ""))

		with open(self.configfile, "w") as f:
			self.Config.write(f)


internal_config = InternalConfig()
atexit.register(internal_config.save_config)


if __name__ == "__main__":
	sys.exit(1)
