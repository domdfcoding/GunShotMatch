#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  cef-wx-demo.py
#
#  This file is part of GunShotMatch
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import pathlib
import platform

# 3rd party
import appdirs
import wx

# this package
from CefBrowser import BrowserPanel, init_cefpython


cef = init_cefpython()

cef_appdir = pathlib.Path(appdirs.user_config_dir("GunShotMatch")) / "cefpython"
cef_settings = dict(
        log_file=str(cef_appdir / "debug.log"),
        cache_path=str(cef_appdir / "cache"),
        locales_dir_path=str(cef_appdir / "locales"),
        user_data_path=str(cef_appdir / "locales"),
        )

url = f'file://{pathlib.Path(appdirs.user_config_dir("GunShotMatch")) / "welcome.html"}'

    
class MainFrame(wx.Frame):

    def __init__(self):
        # Configuration
        
        # size = scale_window_size_for_high_dpi(900, 640)
        size = (900, 640)
        
        wx.Frame.__init__(
                self, parent=None, id=wx.ID_ANY,
                title='wxPython example', size=size)

        # Set wx.WANTS_CHARS style for the keyboard to work.
        # This style also needs to be set for all parent controls.
        self.browser_panel = BrowserPanel(url, self, style=wx.WANTS_CHARS)

        if platform.system() == "Linux":
            # On Linux must show before embedding browser, so that handle
            # is available (Issue #347).
            self.Show()
            wx.CallLater(100, self.browser_panel.embed_browser)
        else:
            self.browser_panel.embed_browser()
            self.Show()
        
        self.browser_panel.Refresh()
        
        
class App(wx.App):
    def __init__(self, redirect):
        self.timer = None
        self.timer_id = 1
        super(App, self).__init__(redirect=redirect)
        frame = MainFrame()
        self.SetTopWindow(frame)
        frame.Show()


if __name__ == '__main__':
    app = App(False)
    app.MainLoop()
