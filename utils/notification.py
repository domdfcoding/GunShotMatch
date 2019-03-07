#!/usr/bin/env python3

"""Desktop Notifications for Linux (GObject) and Windows 10
"""

import platform
import os
import time

if platform.platform().startswith("Windows-10"):
	try:
		# https://github.com/jithurjacob/Windows-10-Toast-Notifications
		from win10toast import ToasterNotifier
		which = 1
	except:
		which = 2
		
elif platform.platform().startswith("Linux"):
	try:
		# https://www.devdungeon.com/content/desktop-notifications-linux-python
		import gi
		gi.require_version('Notify', '0.7')
		from gi.repository import Notify, GdkPixbuf
		Notify.init("GunShotMatch Notification")
		which = 0
	except:
		which = 2
else:
	which = 2

def notification(header = '', body = '', icon = None, duration = 5, threaded = True):
	if which == 1:
		toaster.show_toast(header, body, icon_path = os.path.abspath(icon), duration = duration, threaded = threaded)
	elif which == 0:
		# Create the notification object
		notification = Notify.Notification.new(summary = header, body = body)
		# Use GdkPixbuf to create the proper image type
		if icon != None:
			if not icon.endswith("ico"):
				image = GdkPixbuf.Pixbuf.new_from_file(os.path.abspath(icon))
				# Use the GdkPixbuf image
				notification.set_icon_from_pixbuf(image)
				notification.set_image_from_pixbuf(image)
		notification.show()
		time.sleep(duration)
		notification.close()
		Notify.uninit()
	return

if __name__ == "__main__":
	if which == 1:
		icon = "GunShotMatch.ico"
	elif which == 0:
		icon = "GunShotMatch logo32.png"
	else:
		import sys
		sys.exit(1)
	notification("Header", "Body Body Body\nBody Body Body", icon, duration = 2)
		
