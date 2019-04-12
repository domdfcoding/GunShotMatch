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


import sys
sys.path.append("..")

import re
import os
import time
import traceback
import threading
import subprocess

from gsm_core import EventBoilerplate as ProjectEvent
from gsm_core import EventBoilerplate as ConversionEvent
from gsm_core import EventBoilerplate as ComparisonEvent
from gsm_core import LogEventBoilerplate as ProjectLogEvent
from gsm_core import LogEventBoilerplate as ConversionLogEvent
from gsm_core import LogEventBoilerplate as ComparisonLogEvent

import wx.html2
import wx.richtext
from wx.adv import NotificationMessage
import multiprocessing
from multiprocessing.queues import Queue


# Statusbar and Importer Code
# Based on https://wiki.wxpython.org/Non-Blocking%20Gui
myEVT_STATUS = wx.NewEventType()
EVT_STATUS = wx.PyEventBinder(myEVT_STATUS, 1)
myEVT_QUEUE = wx.NewEventType()
EVT_QUEUE = wx.PyEventBinder(myEVT_QUEUE, 1)
myEVT_CONVERSION = wx.NewEventType()
myEVT_CONVERSION_LOG = wx.NewEventType()
EVT_CONVERSION = wx.PyEventBinder(myEVT_CONVERSION, 1)
EVT_CONVERSION_LOG = wx.PyEventBinder(myEVT_CONVERSION_LOG, 1)
myEVT_PROJECT = wx.NewEventType()
myEVT_PROJECT_LOG = wx.NewEventType()
EVT_PROJECT = wx.PyEventBinder(myEVT_PROJECT, 1)
EVT_PROJECT_LOG = wx.PyEventBinder(myEVT_PROJECT_LOG, 1)
myEVT_COMPARISON = wx.NewEventType()
EVT_COMPARISON = wx.PyEventBinder(myEVT_COMPARISON, 1)
myEVT_COMPARISON_LOG = wx.NewEventType()
EVT_COMPARISON_LOG = wx.PyEventBinder(myEVT_COMPARISON_LOG, 1)

class StatusEvent(wx.PyCommandEvent):
	"""Event to signal that a new status is ready to be displayed"""
	
	def __init__(self, etype, eid, value=None):
		"""Creates the event object"""
		wx.PyCommandEvent.__init__(self, etype, eid)
		self._value = value
	
	def GetValue(self):
		"""Returns the value from the event.
		@return: the value of this event

		"""
		return self._value


kill_status_thread = False


class StatusThread(threading.Thread):
	# Includes code from https://gist.github.com/samarthbhargav/5a515a399f7113137331
	def __init__(self, parent, value):
		"""
		@param parent: The gui object that should recieve the value
		@param value: value to 'calculate' to
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
				evt = StatusEvent(myEVT_STATUS, -1, self._value)
				wx.PostEvent(self._parent, evt)
				wait_time = 1.0
	
	def join(self, timeout=None):
		""" Stop the thread and wait for it to end. """
		self._stopevent.set()
		threading.Thread.join(self, timeout)
	
	"""	global kill_status_thread
		try:
			while True:
				print(kill_status_thread)
				if kill_status_thread:
					break
				time.sleep(1) # our simulated calculation time
				evt = StatusEvent(myEVT_STATUS, -1, self._value)
				wx.PostEvent(self._parent, evt)
			print("Status Thread Exiting")
		except RuntimeError:
			print("StatusThread Exiting")
			return
			# a runtime error was being raised when the main window closed"""





class ConversionThread(threading.Thread):
	def __init__(self, parent, file_list):
		"""
		@param parent: The gui object that should recieve the value
		@param value: value to 'calculate' to
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
				process = subprocess.Popen(["wine",
											"./lib/WatersRaw.exe",
											"-i",
											os.path.join(self._parent.Config.get("main", "rawpath"),
														 raw_file)
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
			#	notification.notification(header = "GunShotMatch",
			#			body = 'Conversion finished\n'+", ".join(self.file_list),
			#			icon = "./lib/GunShotMatch.ico", duration = 5, threaded = True)
			
			NotificationMessage("GunShotMatch",
								message='Import finished\n' + ", ".join(self.file_list),
								parent=None, flags=wx.ICON_INFORMATION).Show()
			
			conversion_thread_running = False
			evt = ConversionEvent(myEVT_CONVERSION, -1)
			wx.PostEvent(self._parent, evt)
		except:
			traceback.print_exc()
			conversion_thread_running = False
	# a runtime error was being raised when the main window closed
 
class ComparisonThread(threading.Thread):
	def __init__(self, parent, left_sample, right_sample, Config, a_value):
		"""
		@param parent: The gui object that should recieve the value
		@param value: value to 'calculate' to
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
			
			p = Process(target=self.comparison_wrapper, args=(self.left_sample,
															  self.right_sample,
															  self.Config,
															  self.a_value))
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
				
				NotificationMessage("GunShotMatch",
									message=f'Comparison finished\n{os.path.splitext(os.path.split(self.left_sample)[-1])[0]}, {os.path.splitext(os.path.split(self.right_sample)[-1])[0]}',
									parent=None, flags=wx.ICON_INFORMATION).Show()
				
				evt = ComparisonEvent(myEVT_COMPARISON, -1)
				wx.PostEvent(self._parent, evt)
				
			else:
				# Comparison failed
				evt = ComparisonLogEvent(myEVT_COMPARISON_LOG, -1, log_text="Comparison Failed\n")
				wx.PostEvent(self._parent, evt)
				
				NotificationMessage("GunShotMatch",
									message='An Error Occurred\nCheck the Comparison Log for Details',
									parent=None, flags=wx.ICON_INFORMATION).Show()
			
			comparison_thread_running = False

			
		except:
			traceback.print_exc()
			comparison_thread_running = False
	# a runtime error was being raised when the main window closed
	
	def comparison_wrapper(self, left_sample, right_sample, Config, a_value):
		from GSMatch_Comparison import GSMCompare
		
		sys.stderr = sys.stdout
		sys.stdout = open("comparison.log", "w", 1)
		
		try:
			comparison = GSMCompare(left_sample, right_sample, Config)
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
		

class ProjectThread(threading.Thread):
	def __init__(self, parent, file_list, pretty_name):
		"""
		@param parent: The gui object that should recieve the value
		@param value: value to 'calculate' to
		"""
		threading.Thread.__init__(self)
		self._parent = parent
		self.file_list = file_list
		self.pretty_name = pretty_name
	
	def run(self):
		"""Overrides Thread.run. Don't call this directly its called internally
		when you call Thread.start().
		"""
		try:
			global project_thread_running
			project_thread_running = True
			
			prefixList = []
			for jcamp_file in self.file_list:
				prefixList.append(os.path.splitext(jcamp_file)[0])
			
			args = ["python3", "-u", "./GSMatch_Rework.py", "--samples"] + prefixList + ["--name", self.pretty_name]
			
			process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			
			for line in iter(process.stdout.readline, b''):
				if not re.match(r'^\s*$', line.decode(
						"utf-8")):  # line is empty (has only the following: \t\n\r and whitespace)print(line.decode("utf-8"))
					if line != b'\r\x1b[K\n':
						# self._parent.project_log_text_control.AppendText(line.decode("utf-8"))
						project_log(self._parent, line.decode("utf-8"))
			for line in iter(process.stderr.readline, b''):
				if not re.match(r'^\s*$', line.decode(
						"utf-8")):  # line is empty (has only the following: \t\n\r and whitespace)print(line.decode("utf-8"))
					if line != b'\r\x1b[K\n':
						# self._parent.project_log_text_control.AppendText(line.decode("utf-8"))
						project_log(self._parent, line.decode("utf-8"))
			
			# From https://stackoverflow.com/q/36596354/3092681
			while process.poll() is None:
				# Process hasn't exited yet, let's wait some
				time.sleep(0.5)
			returncode = process.returncode
			
			if returncode == 0:
				# Conversion is now done
				project_log(self._parent, "New Project Created\n")
				
				NotificationMessage("GunShotMatch",
									message='New Project Created\n' + ", ".join(self.file_list),
									parent=None, flags=wx.ICON_INFORMATION).Show()
			else:
				# Conversion somehow failed
				project_log(self._parent, "An Error Occurred: Check the details above for details.\n")
				project_log(self._parent, "Exit Code : {}\n".format(returncode))
				
				NotificationMessage("GunShotMatch",
									message='An Error Occurred in "New Project"\nCheck the log for details',
									parent=None, flags=wx.ICON_ERROR).Show()
			
			project_thread_running = False
			evt = ProjectEvent(myEVT_PROJECT, -1)
			wx.PostEvent(self._parent, evt)
		except:
			traceback.print_exc()
			conversion_thread_running = False
	# a runtime error was being raised when the main window closed


def project_log(instance, log_text):
	evt = ProjectLogEvent(myEVT_PROJECT_LOG, -1, log_text=log_text)
	wx.PostEvent(instance, evt)


class QueueThread(threading.Thread):
	def __init__(self, parent):
		"""
		@param parent: The gui object
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
				self.parent.Config.set("import", "bb_points",
									   self.parent.project_queue_grid.GetCellValue(queue_entry, 3))
				self.parent.Config.set("import", "bb_scans",
									   self.parent.project_queue_grid.GetCellValue(queue_entry, 4))
				self.parent.Config.set("import", "noise_thresh",
									   self.parent.project_queue_grid.GetCellValue(queue_entry, 5))
				self.parent.Config.set("import", "target_range",
									   self.parent.project_queue_grid.GetCellValue(queue_entry, 6))
				self.parent.Config.set("import", "exclude_ions",
									   self.parent.project_queue_grid.GetCellValue(queue_entry, 7))
				self.parent.Config.set("import", "tophat", self.parent.project_queue_grid.GetCellValue(queue_entry, 8))
				self.parent.Config.set("import", "tophat_unit",
									   self.parent.project_queue_grid.GetCellValue(queue_entry, 9))
				self.parent.Config.set("import", "mass_range",
									   self.parent.project_queue_grid.GetCellValue(queue_entry, 10))
				
				self.parent.Config.set("alignment", "rt_modulation",
									   self.parent.project_queue_grid.GetCellValue(queue_entry, 11))
				self.parent.Config.set("alignment", "gap_penalty",
									   self.parent.project_queue_grid.GetCellValue(queue_entry, 12))
				self.parent.Config.set("alignment", "min_peaks",
									   self.parent.project_queue_grid.GetCellValue(queue_entry, 13))
				
				self.parent.Config.set("analysis", "do_quantitative",
									   self.parent.project_queue_grid.GetCellValue(queue_entry, 14))
				self.parent.Config.set("analysis", "do_qualitative",
									   self.parent.project_queue_grid.GetCellValue(queue_entry, 15))
				self.parent.Config.set("analysis", "do_merge",
									   self.parent.project_queue_grid.GetCellValue(queue_entry, 16))
				self.parent.Config.set("analysis", "do_counter",
									   self.parent.project_queue_grid.GetCellValue(queue_entry, 17))
				self.parent.Config.set("analysis", "do_spectra",
									   self.parent.project_queue_grid.GetCellValue(queue_entry, 18))
				self.parent.Config.set("analysis", "do_charts",
									   self.parent.project_queue_grid.GetCellValue(queue_entry, 19))
				
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
				
				#	self.parent.project_log_text_control.AppendText("Starting processing of:\n")
				#	self.parent.project_log_text_control.AppendText(", ".join(sample_list))
				#	self.parent.project_log_text_control.AppendText("\n\n")
				
				pretty_name = self.parent.project_queue_grid.GetCellValue(queue_entry, 2)
				print(pretty_name)
				
				self.parent.project = ProjectThread(self.parent, sample_list, pretty_name)
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
			traceback.print_exc()
			conversion_thread_running = False
# a runtime error was being raised when the main window closed



class StdoutLog(object):
	def __init__(self, filename):
		self.file = open(filename, "wb", 0)
	
	def write(self, text):
		self.file.write(text.encode("utf-8"))
	
conversion_thread_running = False
project_thread_running = False
queue_thread_running = False
comparison_thread_running = False
