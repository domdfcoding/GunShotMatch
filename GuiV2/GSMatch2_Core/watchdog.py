#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  watchdog.py
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2019-2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import datetime
import getpass
import socket


class AuditRecord:
	def __init__(self, *, record_dict=None):
		if record_dict:
			self.__user = record_dict["user"]
			self.__device = record_dict["device"]
			self.__date = datetime.datetime.fromtimestamp(record_dict["date"])
		else:
			self.__user, self.__device = user_info()
			self.__date = datetime.datetime.now()
	
	@property
	def user(self):
		return self.__user
	
	@property
	def device(self):
		return self.__device
	
	@property
	def date(self):
		return self.__date.timestamp()
	
	@property
	def date_string(self):
		return self.__date.strftime("%d/%m/%Y %H:%M:%S")
	
	def __bool__(self):
		return True
	
	def __str__(self):
		return f"AuditRecord(user='{self.user}', device='{self.device}', date='{self.date_string}')"
	
	def __repr__(self):
		return self.__str__()
	
	def __dict__(self):
		return {
				"user": self.user,
				"device": self.device,
				"date": self.date
				}
	
	def __iter__(self):
		for key, value in self.__dict__().items():
			yield key, value


def user_info():
	"""
	Returns the username of the current user and the hostname of the computer

	:rtype: tuple of str
	"""
	return getpass.getuser(), socket.gethostname()


def time_now():
	"""
	Returns a timestamp for the current time

	:rtype: float
	"""
	return datetime.datetime.now().timestamp()
