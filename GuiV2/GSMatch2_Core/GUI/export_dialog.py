#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  ExportDialog.py
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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

# 3rd party
import wx
from pubsub import pub

# this package
from GuiV2.GSMatch2_Core.custom_bitmap_button import CustomBitmapButton
from GuiV2.icons import get_icon


class ExportDialog(wx.Dialog):
	def __init__(
			self, parent, id=wx.ID_ANY, title='', pos=wx.DefaultPosition,
			style=wx.DEFAULT_DIALOG_STYLE, name=wx.DialogNameStr
			):
		
		wx.Dialog.__init__(
				self, parent=parent, id=id, title=title, pos=pos, size=(468, 420),
				style=style | wx.DEFAULT_DIALOG_STYLE, name=name
				)
		
		self.proj_report_btn = CustomBitmapButton(self, wx.ID_ANY, get_icon("export_project_report", 110), "Project Report")
		self.expr_report_btn = CustomBitmapButton(self, wx.ID_ANY, get_icon(wx.ART_REPORT_VIEW, 110), "Experiment Report")
		self.expr_data_btn = CustomBitmapButton(self, wx.ID_ANY, get_icon("export_jdx", 110), "Experiment Data")
		
		self.method_btn = CustomBitmapButton(self, wx.ID_ANY, get_icon("method", 110), "Method")
		self.ammo_details_btn = CustomBitmapButton(self, wx.ID_ANY, get_icon("ammo-details", 110), "Ammo Details")
		
		self.current_view_pdf_btn = CustomBitmapButton(self, wx.ID_ANY, get_icon("export-pdf", 110), "PDF")
		self.current_view_images_btn = CustomBitmapButton(self, wx.ID_ANY, get_icon("export_images", 110), "Images")
		self.current_view_csv_btn = CustomBitmapButton(self, wx.ID_ANY, get_icon("LibreOffice_Calc", 110), "CSV")
		
		self._set_properties()
		self._do_layout()
		self._bind_events()

	def _set_properties(self):
		self.SetTitle("Export")

		def set_size(obj, size):
			obj.SetMinSize(size)
			obj.SetSize(size)
			obj.SetMaxSize(size)
		
		for obj in {
				self.proj_report_btn,
				self.current_view_csv_btn,
				self.current_view_pdf_btn,
				self.current_view_images_btn,
				self.expr_data_btn,
				self.expr_report_btn,
				self.method_btn,
				self.ammo_details_btn,
				}:
			set_size(obj, (140, 140))
		
		set_size(self, (468, -1))

	def _do_layout(self):
		outer_sizer = wx.BoxSizer(wx.VERTICAL)
		
		grid_sizer_1 = wx.GridSizer(1, 3, 0, 0)
		grid_sizer_1.Add(self.proj_report_btn, 1, 0, 0)
		grid_sizer_1.Add(self.expr_report_btn, 1, 0, 0)
		grid_sizer_1.Add(self.expr_data_btn, 1, 0, 0)
		outer_sizer.Add(grid_sizer_1, 0, wx.ALL ^ wx.BOTTOM, 23)
		
		grid_sizer_2 = wx.GridSizer(1, 3, 0, 0)
		grid_sizer_2.Add(self.method_btn, 1, 0, 0)
		grid_sizer_2.Add(self.ammo_details_btn, 1, 0, 0)
		# grid_sizer_2.Add(self.expr_data_btn, 1, 0, 0)
		outer_sizer.Add(grid_sizer_2, 0, wx.LEFT | wx.RIGHT, 23)
		
		outer_sizer.AddSpacer(10)
		
		current_view_box = wx.StaticBoxSizer(wx.VERTICAL, self, "Current View")
		grid_sizer_2 = wx.GridSizer(1, 3, 0, 0)
		grid_sizer_2.Add(self.current_view_pdf_btn, 1, 0, 0)
		grid_sizer_2.Add(self.current_view_images_btn, 1, 0, 0)
		grid_sizer_2.Add(self.current_view_csv_btn, 1, 0, 0)
		current_view_box.Add(grid_sizer_2, 0, wx.ALL, 3)
		
		outer_sizer.Add(current_view_box, 1, wx.ALL ^ wx.TOP, 20)
		
		btns = self.CreateStdDialogButtonSizer(wx.CLOSE)
		outer_sizer.Add(btns, 0, wx.ALIGN_RIGHT | wx.BOTTOM | wx.RIGHT, 12)
		
		self.SetSizer(outer_sizer)
		outer_sizer.Fit(self)
		self.Layout()
	
	def _bind_events(self):
		self.Bind(wx.EVT_BUTTON, self.on_proj_report, self.proj_report_btn)
		self.Bind(wx.EVT_BUTTON, self.on_expr_report, self.expr_report_btn)
		self.Bind(wx.EVT_BUTTON, self.on_expr_data, self.expr_data_btn)
		
		self.Bind(wx.EVT_BUTTON, self.on_method, self.method_btn)
		self.Bind(wx.EVT_BUTTON, self.on_ammo_details, self.ammo_details_btn)
		
		self.Bind(wx.EVT_BUTTON, self.on_pdf, self.current_view_pdf_btn)
		self.Bind(wx.EVT_BUTTON, self.on_images, self.current_view_images_btn)
		self.Bind(wx.EVT_BUTTON, self.on_csv, self.current_view_csv_btn)
	
	def on_proj_report(self, event):
		pass
	
	def on_expr_report(self, event):
		pass
	
	def on_expr_data(self, event):
		pass
	
	def on_method(self, event):
		wx.CallAfter(pub.sendMessage, "export_method")
		self.Destroy()
	
	def on_ammo_details(self, event):
		wx.CallAfter(pub.sendMessage, "export_ammo_details")
		self.Destroy()
	
	def on_pdf(self, event):
		wx.CallAfter(pub.sendMessage, "export_current_pdf")
		self.Destroy()
	
	def on_images(self, event):
		pass
	
	def on_csv(self, event):
		pass

# end of class ExportDialog


if __name__ == "__main__":
	myapp = wx.App()
	ExportDialog(None).ShowModal()
