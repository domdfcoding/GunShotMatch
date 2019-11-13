#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  threads.py
"""Functions for executing code in separate threads"""
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

# stdlib
import os
import re
import sys
import time
import datetime
import traceback
import threading
import subprocess

# 3rd party
import requests

import wx.html2
import wx.richtext
from wx.adv import NotificationMessage

from domdf_wxpython_tools.events import SimpleEvent

# this package
from GSMatch.GSMatch_Core.thread_boilerplates import LogEventBoilerplate as ProjectLogEvent
from GSMatch.GSMatch_Core.thread_boilerplates import LogEventBoilerplate as ConversionLogEvent
from GSMatch.GSMatch_Core.thread_boilerplates import LogEventBoilerplate as ComparisonLogEvent


myEVT_PROJECT = SimpleEvent()
myEVT_CONVERSION2 = SimpleEvent()
myEVT_COMPARISON2 = SimpleEvent()
myEVT_DATA_VIEWER2 = SimpleEvent()
myEVT_STATUS2 = SimpleEvent()

# Based on https://wiki.wxpython.org/Non-Blocking%20Gui
kill_status_thread = False


class StatusThread(threading.Thread):
	# Includes code from https://gist.github.com/samarthbhargav/5a515a399f7113137331
	def __init__(self, parent, value):
		"""
		:param parent: The gui object that should recieve the value
		:param value: value to 'calculate' to
		"""
		self._stopevent = threading.Event()
		threading.Thread.__init__(self, name="StatusThread")
		self._parent = parent
		self._value = value
	
	def run(self):
		"""Overrides Thread.run. Don't call this directly its called internally
		when you call Thread.start().
		"""
		wait_time = 1.0
		while not self._stopevent.isSet():
			time.sleep(0.1)  # our simulated calculation time
			wait_time -= 0.1
			if wait_time < 0.0:
				myEVT_STATUS2.trigger()
				wait_time = 1.0
	
	def join(self, timeout=None):
		""" Stop the thread and wait for it to end. """
		self._stopevent.set()
		threading.Thread.join(self, timeout)


##########################

myEVT_CONVERSION = wx.NewEventType()
myEVT_CONVERSION_LOG = wx.NewEventType()
EVT_CONVERSION = wx.PyEventBinder(myEVT_CONVERSION, 1)
EVT_CONVERSION_LOG = wx.PyEventBinder(myEVT_CONVERSION_LOG, 1)
conversion_thread_running = False


class ConversionThread(threading.Thread):
	def __init__(self, parent, file_list):
		"""
		param parent: The gui object that should receive events
		"""
		threading.Thread.__init__(self)
		self._parent = parent
		self.file_list = file_list
	
	def run(self):
		"""Overrides Thread.run. Don't call this directly its called internally
		when you call Thread.start().
		"""
		try:
			global conversion_thread_running
			conversion_thread_running = True
			
			for raw_file in self.file_list:
				process = subprocess.Popen([
					"wine",
					"./lib/WatersRaw.exe",
					"-i",
					os.path.join(self._parent.Config.RAW_DIRECTORY, raw_file)
				], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				
				for line in iter(process.stdout.readline, b''):
					if not re.match(r'^\s*$', line.decode(
							"utf-8")):  # line is empty (has only the following: \t\n\r and whitespace)print(line.decode("utf-8"))
						evt = ConversionLogEvent(myEVT_CONVERSION_LOG, -1, log_text=line.decode("utf-8"))
						wx.PostEvent(self._parent, evt)
			
			# Conversion is now done
			evt = ConversionLogEvent(myEVT_CONVERSION_LOG, -1, log_text="Conversion Finished\n")
			wx.PostEvent(self._parent, evt)
			
			# Send desktop notification
			# 	notification.notification(header = "GunShotMatch",
			# 			body = 'Conversion finished\n'+", ".join(self.file_list),
			# 			icon = "./lib/GunShotMatch.ico", duration = 5, threaded = True)
			
			NotificationMessage(
				"GunShotMatch",
				message='Import finished\n' + ", ".join(self.file_list),
				parent=None,
				flags=wx.ICON_INFORMATION
			).Show()
			
			conversion_thread_running = False
			# evt = ConversionEvent(myEVT_CONVERSION, -1)
			# wx.PostEvent(self._parent, evt)
			myEVT_CONVERSION2.trigger()
			
		except:
			# a runtime error was being raised when the main window closed
			traceback.print_exc()
			conversion_thread_running = False

###########################


class FlaskThread(threading.Thread):
	def __init__(self, parent, url):
		"""
		:param parent: The gui object to send events to
		"""
		# self._stopevent = threading.Event()
		threading.Thread.__init__(self, name="FlaskThread")
		self._parent = parent
		self.url = url
	
	def run(self):
		"""Overrides Thread.run. Don't call this directly its called internally
		when you call Thread.start().
		"""
		requests.get(self.url)
		myEVT_DATA_VIEWER2.set_receiver(self._parent)
		myEVT_DATA_VIEWER2.trigger()
		
		
###########################

myEVT_COMPARISON_LOG = wx.NewEventType()
EVT_COMPARISON_LOG = wx.PyEventBinder(myEVT_COMPARISON_LOG, 1)
comparison_thread_running = False


class ComparisonThread(threading.Thread):
	def __init__(self, parent, left_sample, right_sample, Config, a_value):
		"""
		:param parent: The gui object that should receive events
		"""
		
		threading.Thread.__init__(self)
		self._parent = parent
		self.left_sample = left_sample
		self.right_sample = right_sample
		self.Config = Config
		self.a_value = a_value
	
	def run(self):
		"""Overrides Thread.run. Don't call this directly its called internally
		when you call Thread.start().
		"""
		from multiprocessing import Process
		
		try:
			global comparison_thread_running
			comparison_thread_running = True
			
			p = Process(target=comparison_wrapper, args=(
				self.left_sample, self.right_sample, self.Config, self.a_value))
			open("comparison.log", "w").close()
			p.start()
			
			line_idx = 0
			
			success = False
			
			while True:
				with open("comparison.log", "r") as logfile:
					try:
						line = logfile.readlines()[line_idx]
						
						evt = ComparisonLogEvent(myEVT_COMPARISON_LOG, -1, log_text=line)
						wx.PostEvent(self._parent, evt)
						
						line_idx += 1
						
						if line.startswith("Finished!"):
							success = True
							break
						elif line.startswith("An Error Occurred!"):
							break
					except:
						pass
			
			p.join()

			# TODO: Handle errors from process
			
			if success:
				# Comparison is now done
				evt = ComparisonLogEvent(myEVT_COMPARISON_LOG, -1, log_text="Comparison Finished\n")
				wx.PostEvent(self._parent, evt)
				
				NotificationMessage(
					"GunShotMatch",
					message=f'Comparison finished\n{os.path.splitext(os.path.split(self.left_sample)[-1])[0]}, {os.path.splitext(os.path.split(self.right_sample)[-1])[0]}',
					parent=None, flags=wx.ICON_INFORMATION).Show()
				
				myEVT_COMPARISON2.trigger()
				
			else:
				# Comparison failed
				evt = ComparisonLogEvent(myEVT_COMPARISON_LOG, -1, log_text="Comparison Failed\n")
				wx.PostEvent(self._parent, evt)
				
				NotificationMessage(
					"GunShotMatch",
					message='An Error Occurred\nCheck the Comparison Log for Details',
					parent=None,
					flags=wx.ICON_INFORMATION
				).Show()
			
			comparison_thread_running = False

		except:
			traceback.print_exc()
			comparison_thread_running = False
	# a runtime error was being raised when the main window closed
	
	
def comparison_wrapper(left_sample, right_sample, config, a_value):
	from GSMatch.GSMatch_Comparison import GSMCompare
	
	sys.stderr = sys.stdout
	sys.stdout = open("comparison.log", "w", 1)
	
	try:
		comparison = GSMCompare(left_sample, right_sample, config)
		comparison.setup_data()
		comparison.setup_charts()
		comparison.pca()
		comparison.peak_comparison(a_value)
		comparison.make_archive()
		
		print("Finished!")
	
	except:
		trace = traceback.format_exception(*sys.exc_info(), None, None)
		for line in trace:
			print(line)
		print("An Error Occurred!")
		

#########################

myEVT_PROJECT_LOG = wx.NewEventType()
EVT_PROJECT_LOG = wx.PyEventBinder(myEVT_PROJECT_LOG, 1)
project_thread_running = False


class ProjectThread(threading.Thread):
	def __init__(self, parent, file_list, pretty_name, config):
		"""
		:param parent: The gui object that should receive events
		"""
		threading.Thread.__init__(self)
		self._parent = parent
		self.file_list = file_list
		self.pretty_name = pretty_name
		self.Config = config
	
	def run(self):
		"""Overrides Thread.run. Don't call this directly its called internally
		when you call Thread.start().
		"""
		from multiprocessing import Process
		
		try:
			global project_thread_running
			project_thread_running = True
			
			prefixList = []
			for jcamp_file in self.file_list:
				prefixList.append(os.path.splitext(jcamp_file)[0])
				
			p = Process(target=project_wrapper, args=(prefixList, self.pretty_name, self.Config))
			
			open("new_project.log", "w").close()
			p.start()
			
			line_idx = 0
			
			success = False
			
			while True:
				with open("new_project.log", "r") as logfile:
					try:
						line = logfile.readlines()[line_idx]
						
						project_log(self._parent, line)
						
						line_idx += 1
						
						if line.startswith("Finished!"):
							success = True
							break
						elif line.startswith("An Error Occurred!"):
							break
					except:
						pass
			
			p.join()
			
			# TODO: Handle errors from process
			
			if success:
				
				project_log(self._parent, "New Project Created\n")
				
				NotificationMessage(
					"GunShotMatch",
					message='New Project Created\n' + ", ".join(self.file_list),
					parent=None,
					flags=wx.ICON_INFORMATION
				).Show()
				
			else:
				# Conversion somehow failed
				project_log(self._parent, "An Error Occurred: Check the details above for details.\n")
				# project_log(self._parent, "Exit Code : {}\n".format(returncode))
				
				NotificationMessage(
					"GunShotMatch",
					message='An Error Occurred in "New Project"\nCheck the log for details',
					parent=None,
					flags=wx.ICON_ERROR
				).Show()
			
			project_thread_running = False
			myEVT_PROJECT.trigger()
			
		except:
			traceback.print_exc()
			conversion_thread_running = False
	# a runtime error was being raised when the main window closed
	

def project_wrapper(prefix_list, pretty_name, config):
	from GSMatch import NewProject
	
	sys.stderr = sys.stdout
	sys.stdout = open("new_project.log", "w", 1)
	try:
		gsm = NewProject.NewProject(config)
		gsm.config.prefixList = prefix_list
		# overrides whatever was set from the config file
		
		gsm.lot_name = pretty_name
		start_time = datetime.datetime.now()
		gsm.run()
		end_time = datetime.datetime.now()
		print(end_time-start_time)
		print("Finished!")
	
	except:
		trace = traceback.format_exception(*sys.exc_info(), None, None)
		for line in trace:
			print(line)
		print("An Error Occurred!")


def project_log(instance, log_text):
	evt = ProjectLogEvent(myEVT_PROJECT_LOG, -1, log_text=log_text)
	wx.PostEvent(instance, evt)

#########################


myEVT_QUEUE = wx.NewEventType()
EVT_QUEUE = wx.PyEventBinder(myEVT_QUEUE, 1)
queue_thread_running = False


class QueueThread(threading.Thread):
	def __init__(self, parent):
		"""
		:param parent: The gui object
		"""
		threading.Thread.__init__(self)
		self.parent = parent
	
	def run(self):
		"""Overrides Thread.run. Don't call this directly its called internally
		when you call Thread.start().
		"""
		try:
			global queue_thread_running
			queue_thread_running = True
			
			while project_thread_running:
				time.sleep(1)
			
			self.parent.project_log_text_control.Clear()
			self.parent.new_project_notebook.ChangeSelection(2)
			
			if self.parent.project_queue_grid.GetSelectedRows():
				queue_selection = self.parent.project_queue_grid.GetSelectedRows()
			else:
				queue_selection = list(range(self.parent.project_queue_grid.GetNumberRows()))
			
			for queue_entry in queue_selection:
				
				self.parent.project_queue_grid.SetCellValue(queue_entry, 0, "Waiting")
				self.parent.Config.bb_points = self.parent.project_queue_grid.GetCellValue(queue_entry, 3)
				self.parent.Config.bb_scans = self.parent.project_queue_grid.GetCellValue(queue_entry, 4)
				self.parent.Config.noise_thresh = self.parent.project_queue_grid.GetCellValue(queue_entry, 5)
				self.parent.Config.target_range = self.parent.project_queue_grid.GetCellValue(queue_entry, 6).split(",")
				self.parent.Config.exclude_ions = self.parent.project_queue_grid.GetCellValue(queue_entry, 7)
				self.parent.Config.tophat = self.parent.project_queue_grid.GetCellValue(queue_entry, 8)
				self.parent.Config.tophat_unit = self.parent.project_queue_grid.GetCellValue(queue_entry, 9)
				self.parent.Config.mass_range = self.parent.project_queue_grid.GetCellValue(queue_entry, 10).split(",")
				
				self.parent.Config.rt_modulation = self.parent.project_queue_grid.GetCellValue(queue_entry, 11)
				self.parent.Config.gap_penalty = self.parent.project_queue_grid.GetCellValue(queue_entry, 12)
				self.parent.Config.min_peaks = self.parent.project_queue_grid.GetCellValue(queue_entry, 13)
				
				self.parent.Config.do_quantitative = self.parent.project_queue_grid.GetCellValue(queue_entry, 14)
				self.parent.Config.do_qualitative = self.parent.project_queue_grid.GetCellValue(queue_entry, 15)
				self.parent.Config.do_merge = self.parent.project_queue_grid.GetCellValue(queue_entry, 16)
				self.parent.Config.do_counter = self.parent.project_queue_grid.GetCellValue(queue_entry, 17)
				self.parent.Config.do_spectra = self.parent.project_queue_grid.GetCellValue(queue_entry, 18)
				self.parent.Config.do_charts = self.parent.project_queue_grid.GetCellValue(queue_entry, 19)
				
				# Check if the thread is already running:
				while project_thread_running:
					time.sleep(1)
				
				print("")
				# Clear log
				# self.parent.project_log_text_control.Clear()
				self.parent.save_config()
				
				# Files to process
				sample_list = self.parent.project_queue_grid.GetCellValue(queue_entry, 1).split(",")
				
				print("")
				project_log(self.parent, "Starting processing of:\n")
				project_log(self.parent, ", ".join(sample_list))
				project_log(self.parent, "\n\n")
				
				# self.parent.project_log_text_control.AppendText("Starting processing of:\n")
				# self.parent.project_log_text_control.AppendText(", ".join(sample_list))
				# self.parent.project_log_text_control.AppendText("\n\n")
				
				pretty_name = self.parent.project_queue_grid.GetCellValue(queue_entry, 2)
				print(pretty_name)
				
				self.parent.project = ProjectThread(self.parent, sample_list, pretty_name, self.parent.Config)
				self.parent.project.start()
				self.parent.project_queue_grid.SetCellValue(queue_entry, 0, "Running")
				while project_thread_running:
					time.sleep(1)
				self.parent.project_queue_grid.SetCellValue(queue_entry, 0, "Done")
				print(f"{queue_entry} Done")
				
				time.sleep(5)
			
			# project_thread_running = False
			# evt = QueueEvent(myEVT_QUEUE, -1)
			# wx.PostEvent(self.parent, evt)
			print("Queue Done")
			
		except:
			# a runtime error was being raised when the main window closed
			traceback.print_exc()
			conversion_thread_running = False

#################################


class StdoutLog(object):
	def __init__(self, filename):
		self.file = open(filename, "wb", 0)
	
	def write(self, text):
		self.file.write(text.encode("utf-8"))
