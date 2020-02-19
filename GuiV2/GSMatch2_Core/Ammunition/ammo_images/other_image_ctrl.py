#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  other_image_ctrl.py
#
#  This file is part of GunShotMatch
#
#  Copyright (c) 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#  Based on wx.lib.agw.thumbnailctrl from wxPython
#  Copyright Andrea Gavana and Peter Damoc, 2005-2012
#  Licensed under the wxWindows Licence

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
# TODO List/Caveats
#
# 1. Thumbnail Creation/Display May Be Somewhat Improved From The Execution
#    Speed Point Of View;
#
# 2. The Implementation For wx.HORIZONTAL Style Is Still To Be Written;
#


"""
:class:`OtherImagesCtrl` is a widget that can be used to display a series of images in
a "thumbnail" format.

Description
===========

:class:`OtherImagesCtrl` is a widget that can be used to display a series of images in
a "thumbnail" format; it mimics, for example, the windows explorer behavior
when you select the "view thumbnails" option.
Images can be added using the AppendImage and InsertImage methods,
or a Thumb object can be created and added using the AppendThumb and InsertThumb methods

The code is based on wx.lib.agw.thumbnailctrl from wxPython, by Andrea Gavana and
Peter Damoc, but modified so that custom images can be added rather than populating
images from the file system.


Events Processing
=================

This class processes the following events:

==================================	==================================================
Event Name							Description
==================================	==================================================
``EVT_THUMBNAILS_CAPTION_CHANGED``	The thumbnail caption has been changed. Not used at present.
``EVT_THUMBNAILS_DCLICK``			The user has double-clicked on a thumbnail.
``EVT_THUMBNAILS_POINTED``			The mouse cursor is hovering over a thumbnail.
``EVT_THUMBNAILS_SEL_CHANGED``		The user has changed the selected thumbnail.
``EVT_THUMBNAILS_THUMB_CHANGED``	The thumbnail of an image has changed. Used internally.
``EVT_IMAGE_ADDED``					An image has been added
``EVT_IMAGE_DELETED``				An image has been deleted
``EVT_IMAGE_RENAMED``				An image has been renamed
==================================	==================================================
"""

# stdlib
import os
from functools import lru_cache

# 3rd party
from PIL import Image, ImageEnhance
import wx
from wx.lib.agw import thumbnailctrl
from domdf_wxpython_tools import file_dialog_wildcard

# this package
from GuiV2.GSMatch2_Core.Ammunition import ammo_images


# Events
ImgAddedEvent = wx.NewEventType()
EVT_IMAGE_ADDED = wx.PyEventBinder(ImgAddedEvent, 0)


class EvtImgAdded(wx.PyCommandEvent):
	eventType = ImgAddedEvent

	def __init__(self, windowID, obj):
		wx.PyCommandEvent.__init__(self, self.eventType, windowID)
		self.SetEventObject(obj)


ImgDeletedEvent = wx.NewEventType()
EVT_IMAGE_DELETED = wx.PyEventBinder(ImgDeletedEvent, 0)


class EvtImgDeleted(wx.PyCommandEvent):
	eventType = ImgDeletedEvent

	def __init__(self, windowID, obj):
		# TODO: Which Image
		wx.PyCommandEvent.__init__(self, self.eventType, windowID)
		self.SetEventObject(obj)

		
ImgRenamedEvent = wx.NewEventType()
EVT_IMAGE_RENAMED = wx.PyEventBinder(ImgRenamedEvent, 0)


class EvtImgRenamed(wx.PyCommandEvent):
	eventType = ImgRenamedEvent

	def __init__(self, windowID, obj):
		# TODO: Which Image
		wx.PyCommandEvent.__init__(self, self.eventType, windowID)
		self.SetEventObject(obj)


# TODO Exchange images
def thumbnail_key(item):
	"""
	Return the key to be used for sorting???
	"""
	return item.GetFileName()


class Thumb:
	"""
	This is an auxiliary class, to handle single thumbnail information for every thumb.
	"""
	
	def __init__(self, parent, image, caption=""):
		"""
		Default class constructor.

		:param parent: the main :class:`OtherImagesCtrl` window;
		:param parent:
		:type parent:
		:param image:
		:type image:
		:param caption: the thumbnail caption string;
		:type caption:
		"""
		
		self._original_image = image
		self._caption = caption
		self._id = 0
		self._parent = parent
		self._captionbreaks = []

		image = image.copy()
		
		image.thumbnail((300, 240))
		img = wx.Image(image.size[0], image.size[1])
		
		img.SetData(image.convert("RGB").tobytes())
		
		alpha = False
		if "A" in image.getbands():
			img.SetAlpha(image.convert("RGBA").tobytes()[3::4])
			alpha = True
		
		self._image = img
		self._original_size = self._original_image.size
		self._bitmap = img
		self._alpha = alpha
	
	def SetCaption(self, caption=""):
		"""
		Sets the thumbnail caption.

		:param caption: the thumbnail caption string.
		"""
		
		self._caption = caption
		self._captionbreaks = []
	
	def GetImage(self):
		"""
		Returns the thumbnail image.
		"""
		
		return self._image
	
	def SetImage(self, image):
		"""
		Sets the thumbnail image.

		:param image: a :class:wx.Image object.
		"""
		
		self._image = image
	
	def GetId(self):
		"""
		Returns the thumbnail identifier.
		"""
		
		return self._id
	
	def SetId(self, id=-1):
		"""
		Sets the thumbnail identifier.

		:param id: an integer specifying the thumbnail identifier.
		"""
		
		self._id = id
	
	def GetBitmap(self, width, height):
		"""
		Returns the associated bitmap.

		:param width: the associated bitmap width;
		:param height: the associated bitmap height.
		"""
		
		return self._DoGetBitmap(width, height, *self._original_size, self._image)
		
	def GetCaption(self, line=0):
		"""
		Returns the caption associated to a thumbnail.

		:param line: the caption line we wish to retrieve (useful for multiline caption strings).
		"""
		
		if line + 1 >= len(self._captionbreaks):
			return ""
		
		return self._caption

	def GetOriginalSize(self):
		"""
		Returns a tuple containing the original image width and height, in pixels.
		"""
		
		return self._original_size
	
	def GetCaptionLinesCount(self, width):
		"""
		Returns the number of lines for the caption.

		:param width: the maximum width, in pixels, available for the caption text.
		"""
		
		self.BreakCaption(width)
		return len(self._captionbreaks) - 1
	
	def BreakCaption(self, width):
		"""
		Breaks the caption in several lines of text (if needed).

		:param width: the maximum width, in pixels, available for the caption text.
		"""
		
		if len(self._captionbreaks) > 0 or width < 16:
			return
		
		self._captionbreaks.append(0)
		
		if len(self._caption) == 0:
			return
		
		pos = width // 16
		beg = 0
		end = 0
		
		dc = wx.MemoryDC()
		bmp = wx.Bitmap(10, 10)
		dc.SelectObject(bmp)
		
		while True:
			if pos >= len(self._caption):
				self._captionbreaks.append(len(self._caption))
				break
			
			sw, sh = dc.GetTextExtent(self._caption[beg:pos - beg])
			
			if sw > width:
				if end > 0:
					self._captionbreaks.append(end)
					beg = end
				
				else:
					self._captionbreaks.append(pos)
					beg = pos
				
				pos = beg + width // 16
				end = 0
			
			if pos < len(self._caption) and self._caption[pos] in [" ", "-", ",", ".", "_"]:
				end = pos + 1
			
			pos = pos + 1
		
		dc.SelectObject(wx.NullBitmap)
	
	def GetOriginalImage(self):
		return self._original_image
	
	def __eq__(self, other):
		if other.__class__ != self.__class__:
			return NotImplemented
		
		return self._original_image == other.GetOriginalImage() and self._caption == other._caption

	@staticmethod
	@lru_cache(10)
	def _DoGetBitmap(width, height, imgwidth, imgheight, image):
		img = image.Copy()
		
		if width < imgwidth or height < imgheight:
			scale = float(width) / imgwidth
			
			if scale > float(height) / imgheight:
				scale = float(height) / imgheight
			
			newW, newH = int(imgwidth * scale), int(imgheight * scale)
			if newW < 1:
				newW = 1
			if newH < 1:
				newH = 1
			
			img = img.Scale(newW, newH)
		
		bmp = img.ConvertToBitmap()
		
		return bmp


# class DropTarget(wx.FileDropTarget):
#
# 	def __init__(self, widget, parent):
# 		wx.FileDropTarget.__init__(self)
# 		self.widget = widget
# 		self.parent = parent
#
# 	def OnDropFiles(self, x, y, filenames):
# 		image = Image.open(filenames[0])
# 		self.parent.AppendImage(Thumb(self.widget, image, filenames[0]))
# 		return True


class OtherImagesCtrl(thumbnailctrl.ScrolledThumbnail):
	def __init__(
			self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
			size=wx.DefaultSize, thumboutline=thumbnailctrl.THUMB_OUTLINE_IMAGE):
		"""
		Default class constructor.

		:param parent: parent window. Must not be ``None``
		:param id: window identifier. A value of -1 indicates a default value
		:param pos: the control position. A value of (-1, -1) indicates a default position,
		chosen by either the windowing system or wxPython, depending on platform
		:param size: the control size. A value of (-1, -1) indicates a default size,
		chosen by either the windowing system or wxPython, depending on platform;
		:param thumboutline: outline style for :class:`OtherImagesCtrl`, which may be:
			=========================== ======= ==================================
			Outline Flag                 Value  Description
			=========================== ======= ==================================
			``THUMB_OUTLINE_NONE``            0 No outline is drawn on selection
			``THUMB_OUTLINE_FULL``            1 Full outline (image+caption) is drawn on selection
			``THUMB_OUTLINE_RECT``            2 Only thumbnail bounding rectangle is drawn on selection (default)
			``THUMB_OUTLINE_IMAGE``           4 Only image bounding rectangle is drawn.
			=========================== ======= ==================================
		"""
		
		wx.ScrolledWindow.__init__(self, parent, id, pos, size)
		
		self.SetThumbSize(96, 80)
		self._tOutline = thumboutline
		self._selected = -1
		self._pointed = -1
		self._labelcontrol = None
		self._pmenu = None
		self._gpmenu = None
		self._dragging = False
		self._checktext = False
		self._orient = thumbnailctrl.THUMB_VERTICAL
		self._dropShadow = True
		
		self._tCaptionHeight = []
		self._selectedarray = []
		self._tTextHeight = 16
		self._tCaptionBorder = 8
		self._tOutlineNotSelected = True
		self._mouseeventhandled = False
		self._highlight = False
		self._zoomfactor = 1.4
		self.SetCaptionFont()
		self._items = []
		
		self._enabletooltip = False
		
		self._parent = parent
		
		self._selectioncolour = "#009EFF"
		self.grayPen = wx.Pen("#A2A2D2", 1, wx.SHORT_DASH)
		self.grayPen.SetJoin(wx.JOIN_MITER)
		self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOX))
		
		t, b, s = thumbnailctrl.getShadow()
		self.shadow = wx.MemoryDC()
		self.shadow.SelectObject(s)
		
		self.ShowCaptions(True)
		# self.EnableDragging()
		# TODO: Disabled this for now as dragging caused entire PC to
		#  stutter while data being copied into drag&drop memory
		
		self._create_menus()
		self._bind_events()
		
		# filedroptarget = DropTarget(self, self)
		# self.SetDropTarget(filedroptarget)
	
	def _bind_events(self):
		self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
		self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
		self.Bind(wx.EVT_LEFT_DCLICK, self.OnMouseDClick)
		self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseDown)
		self.Bind(wx.EVT_RIGHT_UP, self.OnMouseUp)
		self.Bind(wx.EVT_MOTION, self.OnMouseMove)
		self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)
		self.Bind(thumbnailctrl.EVT_THUMBNAILS_THUMB_CHANGED, self.OnThumbChanged)
		self.Bind(wx.EVT_CHAR, self.OnChar)
		self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
		
		self.Bind(wx.EVT_SIZE, self.OnResize)
		self.Bind(wx.EVT_ERASE_BACKGROUND, lambda x: None)
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		
		self.Bind(wx.EVT_MENU, self.OnPopupView, id=ammo_images.ID_View_Image)
		self.Bind(wx.EVT_MENU, self.OnPopupCopy, id=ammo_images.ID_Copy_Image)
		self.Bind(wx.EVT_MENU, self.OnPopupSave, id=ammo_images.ID_Save_Image)
		self.Bind(wx.EVT_MENU, self.OnPopupDelete, id=ammo_images.ID_Delete_Image)
		self.Bind(wx.EVT_MENU, self.OnPopupExchangePropellant, id=ammo_images.ID_Exchange_Propellant)
		self.Bind(wx.EVT_MENU, self.OnPopupExchangeHeadstamp, id=ammo_images.ID_Exchange_Headstamp)
		self.Bind(wx.EVT_MENU, self.OnPopupRename, id=ammo_images.ID_Rename_Image)
		self.Bind(wx.EVT_MENU, self.OnSelectAll, id=ammo_images.ID_Select_All)
		self.Bind(wx.EVT_MENU, self.OnPopupAddImage, id=ammo_images.ID_Add_Image)
		self.Bind(wx.EVT_MENU, self.OnPopupPaste, id=ammo_images.ID_Paste_Image)
	
	def _create_menus(self):
		item_menu = wx.Menu()
		item_menu.Append(ammo_images.ID_View_Image, "View")
		item_menu.Append(ammo_images.ID_Select_All, "Select all")
		item_menu.AppendSeparator()
		item_menu.Append(ammo_images.ID_Copy_Image, "Copy")
		item_menu.Append(ammo_images.ID_Paste_Image, "Paste")
		item_menu.Append(ammo_images.ID_Save_Image, "Save")
		item_menu.Append(ammo_images.ID_Rename_Image, "Rename")
		# 'Exchange with' submenu
		sm = wx.Menu()
		sm.Append(ammo_images.ID_Exchange_Propellant, "Propellant")
		sm.Append(ammo_images.ID_Exchange_Headstamp, "Headstamp")
		item_menu.AppendSubMenu(sm, "Exchange with", '')
		item_menu.AppendSeparator()
		item_menu.Append(ammo_images.ID_Delete_Image, "Delete")
		
		self.SetPopupMenu(item_menu)
		
		global_menu = wx.Menu()
		global_menu.Append(ammo_images.ID_Add_Image, "Add Image")
		global_menu.Append(ammo_images.ID_Paste_Image, "Paste")
		self.SetGlobalPopupMenu(global_menu)
	
	def AppendImage(self, image, caption=''):
		"""
		Append the image to the control

		:param image:
		:type image:
		:param caption:
		:type caption:
		"""
		
		thumb = Thumb(self, image, caption)
		self.AppendThumb(thumb)
		return thumb
		
	def AppendThumb(self, thumb):
		"""
		Append a Thumb object to the control
		
		:param thumb:
		:type thumb:

		"""
		
		self._items.append(thumb)
		
		self._selectedarray = []
		self.UpdateProp()
		self.Refresh()
	
	def Delete(self):
		"""
		Deletes the selected thumbnails and their associated files.
		"""
		
		with wx.MessageDialog(
				self, 'Are you sure you want to delete the selected images?',
				'Confirmation',
				wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION
				) as dlg:
			
			if dlg.ShowModal() == wx.ID_YES:
				wx.BeginBusyCursor()
				for index in self._selectedarray:
					self._items[index] = None
				self._items = list(filter(None, self._items))

				self._selectedarray = []
				wx.EndBusyCursor()
				
				self.UpdateProp()
				self.Refresh()
	
	def DrawThumbnail(self, bmp, thumb, index):
		"""
		Draws a visible thumbnail.

		:param bmp: the thumbnail version of the original image;
		:param thumb: an instance of :class:`Thumb`;
		:param index: the index of the thumbnail to draw.
		"""
		
		dc = wx.MemoryDC()
		dc.SelectObject(bmp)
		
		x = self._tBorder / 2
		y = self._tBorder / 2
		
		# background
		dc.SetPen(wx.Pen(wx.BLACK, 0, wx.TRANSPARENT))
		dc.SetBrush(wx.Brush(self.GetBackgroundColour(), wx.BRUSHSTYLE_SOLID))
		dc.DrawRectangle(0, 0, bmp.GetWidth(), bmp.GetHeight())
		
		# image
		img = thumb.GetBitmap(self._tWidth, self._tHeight)
		ww = img.GetWidth()
		hh = img.GetHeight()
		
		if index == self.GetPointed() and self.GetHighlightPointed():
			factor = 1.5
			
			img = img.ConvertToImage()
			pil = Image.new('RGB', (img.GetWidth(), img.GetHeight()))
			pil.frombytes(bytes(img.GetData()))
			enh = ImageEnhance.Brightness(pil)
			enh = enh.enhance(1.5)
			img.SetData(enh.convert('RGB').tobytes())
			img = img.ConvertToBitmap()
		
		imgRect = wx.Rect(
				x + (self._tWidth - img.GetWidth()) / 2,
				y + (self._tHeight - img.GetHeight()) / 2,
				img.GetWidth(), img.GetHeight())
		
		if not thumb._alpha and self._dropShadow:
			dc.Blit(
					imgRect.x + 5, imgRect.y + 5,
					imgRect.width, imgRect.height,
					self.shadow, 500 - ww, 500 - hh)
		dc.DrawBitmap(img, imgRect.x, imgRect.y, True)
		
		colour = self.GetSelectionColour()
		selected = self.IsSelected(index)
		
		colour = self.GetSelectionColour()
		
		# draw caption
		sw, sh = 0, 0
		if self._showcaptions:
			textWidth = 0
			dc.SetFont(self.GetCaptionFont())
			mycaption = thumb.GetCaption(0)
			sw, sh = dc.GetTextExtent(mycaption)
			
			if sw > self._tWidth:
				mycaption = self.CalculateBestCaption(dc, mycaption, sw, self._tWidth)
				sw = self._tWidth
			
			textWidth = sw + 8
			tx = x + (self._tWidth - textWidth) / 2
			ty = y + self._tHeight
			
			txtcolour = "#7D7D7D"
			dc.SetTextForeground(txtcolour)
			
			tx = x + (self._tWidth - sw) / 2
			if hh >= self._tHeight:
				ty = y + self._tHeight + (self._tTextHeight - sh) / 2 + 3
			else:
				ty = y + hh + (self._tHeight - hh) / 2 + (self._tTextHeight - sh) / 2 + 3
			
			dc.DrawText(mycaption, tx, ty)
		
		# outline
		if self._tOutline != thumbnailctrl.THUMB_OUTLINE_NONE and (self._tOutlineNotSelected or self.IsSelected(index)):
			
			dotrect = wx.Rect()
			dotrect.x = x - 2
			dotrect.y = y - 2
			dotrect.width = bmp.GetWidth() - self._tBorder + 4
			dotrect.height = bmp.GetHeight() - self._tBorder + 4
			
			dc.SetPen(wx.Pen(
					(self.IsSelected(index) and [colour] or [wx.LIGHT_GREY])[0],
					0, wx.PENSTYLE_SOLID))
			
			dc.SetBrush(wx.Brush(wx.BLACK, wx.BRUSHSTYLE_TRANSPARENT))
			
			if self._tOutline == thumbnailctrl.THUMB_OUTLINE_FULL or self._tOutline == thumbnailctrl.THUMB_OUTLINE_RECT:
				
				imgRect.x = x
				imgRect.y = y
				imgRect.width = bmp.GetWidth() - self._tBorder
				imgRect.height = bmp.GetHeight() - self._tBorder
				
				if self._tOutline == thumbnailctrl.THUMB_OUTLINE_RECT:
					imgRect.height = self._tHeight
			
			dc.SetBrush(wx.TRANSPARENT_BRUSH)
			
			if selected:
				
				dc.SetPen(self.grayPen)
				dc.DrawRoundedRectangle(dotrect, 2)
				
				dc.SetPen(wx.Pen(wx.WHITE))
				dc.DrawRectangle(imgRect.x, imgRect.y, imgRect.width, imgRect.height)
				
				pen = wx.Pen((selected and [colour] or [wx.LIGHT_GREY])[0], 2)
				pen.SetJoin(wx.JOIN_MITER)
				dc.SetPen(pen)
				if self._tOutline == thumbnailctrl.THUMB_OUTLINE_FULL:
					dc.DrawRoundedRectangle(
							imgRect.x - 1, imgRect.y - 1,
							imgRect.width + 3, imgRect.height + 3, 2)
				else:
					dc.DrawRectangle(
							imgRect.x - 1, imgRect.y - 1,
							imgRect.width + 3, imgRect.height + 3)
			else:
				dc.SetPen(wx.Pen(wx.LIGHT_GREY))
				
				dc.DrawRectangle(
						imgRect.x - 1, imgRect.y - 1,
						imgRect.width + 2, imgRect.height + 2)
		
		dc.SelectObject(wx.NullBitmap)
	
	def GetItems(self):
		return self._items
	
	def GetLeftmostSelected(self):
		self._selectedarray.sort()
		if self._selectedarray:
			return self._selectedarray[0]
		return -1
	
	def GetRightmostSelected(self):
		self._selectedarray.sort()
		if self._selectedarray:
			return self._selectedarray[-1]
		return -1
	
	def GetSelectedItem(self, selIndex=-1):
		"""
		Returns the selected thumbnail.

		:param selIndex: the thumbnail index (i.e., the selection).
		"""
		
		return self.GetItem(self.GetSelection(selIndex))
	
	def GetSelection(self, selIndex=-1):
		"""
		Returns the selected thumbnail.

		:param selIndex: if not equal to -1, the index of the selected thumbnail.
		"""
		return self.GetLeftmostSelected()
	
	def GetThumbInfo(self, thumb=-1):
		"""
		Returns the thumbnail information.

		:param thumb: the index of the thumbnail for which we are collecting information.
		"""
		
		thumbinfo = None
		
		if thumb >= 0:
			thumbinfo = f"""Name: {self._items[thumb].GetFileName()}
Dimensions: {self._items[thumb].GetOriginalSize()}
Thumb: {self.GetThumbSize()[0:2]}"""
		
		return thumbinfo
	
	def InsertImage(self, pos, image, caption=''):
		"""
		Inserts a thumbnail in the specified position.

		:param pos: The index at which we wish to insert the new thumbnail.
		:type pos: int
		:param image:
		:type image:
		:param caption:
		:type caption:
		:return:
		:rtype:
		"""
		
		thumb = Thumb(self, image, caption)
		
		if pos < 0 or pos > len(self._items):
			self.AppendThumb(thumb)
		else:
			self.InsertThumb(pos, thumb)
		
		return thumb

	def InsertThumb(self, pos, thumb):
		"""
		Insert a Thumb object at the specified position
		
		:param pos: the index at which we wish to insert the new thumbnail.
		:type pos: int
		:param thumb:
		:type thumb:
		"""
		
		if pos < 0 or pos > len(self._items):
			self.AppendThumb(thumb)
		else:
			self._items.insert(pos, thumb)
		
			self._selectedarray = []
			self.UpdateProp()
			self.Refresh()
		
	def InsertItem(self, pos, image, caption=''):
		self.InsertImage(pos, image, caption)
	
	def IsSelected(self, index):
		"""
		Returns whether a thumbnail is selected or not.

		:param index: the index of the thumbnail to check for selection.
		"""
		
		return index in self._selectedarray
	
	def OnChar(self, event):
		"""
		Handles the ``wx.EVT_CHAR`` event for :class:`OtherImagesCtrl`.

		:param event: a :class:`KeyEvent` event to be processed.

		:note: You have these choices:

			(1) ``Del`` key deletes the selected thumbnails;
			(2) ``+`` key zooms in;
			(3) ``-`` key zooms out.
		"""
		
		if event.KeyCode == wx.WXK_DELETE:
			self.Delete()
		elif event.KeyCode in {wx.WXK_ADD, wx.WXK_NUMPAD_ADD, 43, 61}:
			self.ZoomIn()
		elif event.KeyCode in {wx.WXK_SUBTRACT, wx.WXK_NUMPAD_SUBTRACT, 45, 95}:
			self.ZoomOut()
		elif event.KeyCode in {wx.WXK_LEFT, wx.WXK_NUMPAD_LEFT}:
			self.SelectToLeft(event)
		elif event.KeyCode in {wx.WXK_RIGHT, wx.WXK_NUMPAD_RIGHT}:
			self.SelectToRight(event)
		
		event.Skip()
	
	def OnMouseDClick(self, event):
		"""
		Handles the ``wx.EVT_LEFT_DCLICK`` event for :class:`OtherImagesCtrl`.

		:param event: a :class:`MouseEvent` event to be processed.
		"""
		
		# TODO: Open image viewer
		
		eventOut = thumbnailctrl.ThumbnailEvent(thumbnailctrl.wxEVT_THUMBNAILS_DCLICK, self.GetId())
		self.GetEventHandler().ProcessEvent(eventOut)
	
	def OnMouseDown(self, event):
		"""
		Handles the ``wx.EVT_LEFT_DOWN`` and ``wx.EVT_RIGHT_DOWN`` events for :class:`OtherImagesCtrl`.

		:param event: a :class:`MouseEvent` event to be processed.
		"""
		
		x = event.GetX()
		y = event.GetY()
		x, y = self.CalcUnscrolledPosition(x, y)
		# get item number to select
		lastselected = self._selected
		self._selected = self.GetItemIndex(x, y)
		
		self._mouseeventhandled = False
		update = False
		
		if event.ControlDown():
			if self._selected == -1:
				self._mouseeventhandled = True
			elif not self.IsSelected(self._selected):
				self._selectedarray.append(self._selected)
				update = True
				self._mouseeventhandled = True
		
		elif event.ShiftDown():
			if self._selected != -1:
				begindex = self._selected
				endindex = lastselected
				if lastselected < self._selected:
					begindex = lastselected
					endindex = self._selected
				self._selectedarray = []
				
				for ii in range(begindex, endindex + 1):
					self._selectedarray.append(ii)
				
				update = True
			
			self._selected = lastselected
			self._mouseeventhandled = True
		
		else:
			if self._selected == -1:
				update = len(self._selectedarray) > 0
				self._selectedarray = []
				self._mouseeventhandled = True
			elif len(self._selectedarray) <= 1:
				try:
					update = len(self._selectedarray) == 0 or self._selectedarray[0] != self._selected
				except:
					update = True
				self._selectedarray = []
				self._selectedarray.append(self._selected)
				self._mouseeventhandled = True
		
		if update:
			self.ScrollToSelected()
			self.Refresh()
			eventOut = thumbnailctrl.ThumbnailEvent(thumbnailctrl.wxEVT_THUMBNAILS_SEL_CHANGED, self.GetId())
			self.GetEventHandler().ProcessEvent(eventOut)
		
		self.SetFocus()
	
	def OnMouseMove(self, event):
		"""
		Handles the ``wx.EVT_MOTION`` event for :class:`OtherImagesCtrl`.

		:param event: a :class:`MouseEvent` event to be processed.
		"""
		
		# -- drag & drop --
		if self._dragging and event.Dragging() and len(self._selectedarray) > 0:
			# Limitation: Can only drag&drop 1 at a time
			image = self.GetSelectedItem().GetOriginalImage()
			
			width, height = image.size
			bmp = wx.Bitmap.FromBuffer(width, height, image.tobytes())
			
			# Create BitmapDataObject
			bmp_data = wx.BitmapDataObject(bmp)
			
			source = wx.DropSource(self)
			source.SetData(bmp_data)
			icon = wx.Icon()
			icon.CopyFromBitmap(bmp)
			source.SetIcon(wx.DragLink, icon)
			source.DoDragDrop(wx.Drag_CopyOnly)
			# TODO: Why the weird effect when dragging?
		
		self.Refresh()
		eventOut = thumbnailctrl.ThumbnailEvent(thumbnailctrl.wxEVT_THUMBNAILS_POINTED, self.GetId())
		self.GetEventHandler().ProcessEvent(eventOut)
		event.Skip()
		
	def OnPopupAddImage(self, event):
		print("OnPopupAddImage")
		
		new_image = file_dialog_wildcard(
				self, "Choose an Image",
				ammo_images.images_wildcard.wildcard,
				style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
				)
		
		if not new_image:
			return
		
		filename = new_image[0]
		
		self.AppendImage(Image.open(filename), os.path.split(filename)[-1])
		
		event.Skip()
	
	def OnPopupCopy(self, event):
		print("OnPopupCopy")
		
		image = self.GetSelectedItem().GetOriginalImage()
		
		width, height = image.size
		bmp = wx.Bitmap.FromBuffer(width, height, image.tobytes())
		
		# Create BitmapDataObject
		bmp_data = wx.BitmapDataObject(bmp)
		
		# Write image from clipboard
		if wx.TheClipboard.Open():
			wx.TheClipboard.SetData(bmp_data)
			wx.TheClipboard.Flush()
		wx.TheClipboard.Close()
		event.Skip()
	
	def OnPopupDelete(self, event):
		print("OnPopupDelete")
		self.Delete()
		
		wx.PostEvent(self.GetEventHandler(), EvtImgAdded(self.GetId(), self))
		
		event.Skip()
	
	def OnPopupExchangeHeadstamp(self, event):
		print("OnPopupMenu: Popup Seven\n")
	
	def OnPopupExchangePropellant(self, event):
		print("OnPopupMenu: Popup Six\n")
	
	def OnPopupPaste(self, event):
		print("OnPopupPaste")
		
		# Create empty BitmapDataObject
		bmp_data = wx.BitmapDataObject()
		
		# Read image from clipboard
		wx.TheClipboard.Open()
		if wx.TheClipboard.GetData(bmp_data):
			wx.TheClipboard.Close()
			
			# https://stackoverflow.com/a/46606553/3092681
			# Get bitmap and convert to PIL Image
			bmp = bmp_data.GetBitmap()
			size = tuple(bmp.GetSize())
			buf = size[0] * size[1] * 3 * b"\x00"
			bmp.CopyToBuffer(buf)
			self.AppendImage(Image.frombuffer("RGB", size, buf, "raw", "RGB", 0, 1), "Pasted Image")
			event.Skip()
			
			wx.PostEvent(self.GetEventHandler(), EvtImgAdded(self.GetId(), self))
		
		else:
			# No image on clipboard
			wx.TheClipboard.Close()
	
	def OnPopupRename(self, event):
		print("OnPopupRename")
		
		thumb = self.GetSelectedItem()
		
		with wx.TextEntryDialog(self, "Rename Image", caption="Rename Image", value=thumb.GetCaption(0)) as dlg:
			if dlg.ShowModal() == wx.ID_OK:
				thumb.SetCaption(dlg.GetValue())
				
				wx.PostEvent(self.GetEventHandler(), EvtImgRenamed(self.GetId(), self))
		
		self.UpdateProp()
		self.Refresh()
		event.Skip()
	
	def OnPopupSave(self, event):
		print("OnPopupSave")
		
		image = self.GetSelectedItem()._original_image
		
		save_location = file_dialog_wildcard(
				self, "Save Image",
				ammo_images.images_wildcard.wildcard,
				style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
				)
		
		if not save_location:
			return
		
		image.save(save_location[0])
		event.Skip()
	
	def OnPopupView(self, event):
		print("OnPopupView")
		event.Skip()
	
	def OnResize(self, event):
		"""
		Handles the ``wx.EVT_SIZE`` event for :class:`OtherImagesCtrl`.

		:param event: a :class:`wx.SizeEvent` event to be processed.
		"""
		
		self.UpdateProp()
		self.ScrollToSelected()
		self.Refresh()
	
	def OnSelectAll(self, event):
		print("OnPopupSelectAll")

		self.SelectAll()
		event.Skip()
	
	def OnThumbChanged(self, event):
		"""
		Handles the ``EVT_THUMBNAILS_THUMB_CHANGED`` event for :class:`OtherImagesCtrl`.

		:param event: a :class:`ThumbnailEvent` event to be processed.
		"""
		
		for ii in range(len(self._items)):
			if self._items[ii].GetFileName() == event.GetString():
				
				self._items[ii].SetFilename(self._items[ii].GetFileName())
				if event.GetClientData():
					img = wx.Image(event.GetClientData())
					self._items[ii].SetImage(img)
		
		self.Refresh()
	
	def SelectAll(self):
		self.SelectMultiple([ii for ii in range(self.GetItemCount())])
	
	def SelectMultiple(self, indices):
		self._selectedarray = list(indices)
		eventOut = thumbnailctrl.ThumbnailEvent(thumbnailctrl.wxEVT_THUMBNAILS_SEL_CHANGED, self.GetId())
		self.GetEventHandler().ProcessEvent(eventOut)
		self.ScrollToSelected()
		self.Refresh()
	
	def SelectToLeft(self, event=None):
		"""
		Select the image to the left of the current position, if there is an image there

		:return:
		:rtype:
		"""
		
		index = self.GetLeftmostSelected()
		if index == 0:
			return -1
		else:
			if event and event.ShiftDown():
				self.SelectMultiple([*self._selectedarray, index - 1])
			else:
				self.SetSelection(index - 1)
				
	def SelectToRight(self, event=None):
		"""
		Select the image to the right of the current position, if there is an image there
		
		:return: The newly selected index, or -1 if the selection did not change
		:rtype:
		"""
		
		index = self.GetRightmostSelected()
		if index == self.GetItemCount():
			return -1
		else:
			if event and event.ShiftDown():
				self.SelectMultiple([*self._selectedarray, index+1])
			else:
				self.SetSelection(index + 1)
		
	def SetSelection(self, value=-1):
		"""
		Sets thumbnail selection.

		:param value: the thumbnail index to select.
		"""
		
		self._selected = value
		if value != -1:
			self._selectedarray = [value]
			eventOut = thumbnailctrl.ThumbnailEvent(thumbnailctrl.wxEVT_THUMBNAILS_SEL_CHANGED, self.GetId())
			self.GetEventHandler().ProcessEvent(eventOut)
			self.ScrollToSelected()
			self.Refresh()
	
	def ShowCaptions(self, show=True):
		"""
		Sets whether the user wants to show file names under the thumbnails or not.

		:param show: ``True`` to show file names under the thumbnails, ``False`` otherwise.
		"""
		
		self._showcaptions = show
		self.Refresh()
	
	def SortItems(self):
		""" Sorts the items accordingly to the :func:`~CmpThumb` function. """
		
		self._items.sort(key=thumbnail_key)
	
	def UpdateItems(self):
		""" Updates thumbnail items. """
		
		selected = self._selectedarray
		selectedfname = []
		selecteditemid = []
		
		for ii in range(len(self._selectedarray)):
			selectedfname.append(self.GetSelectedItem(ii).GetFileName())
			selecteditemid.append(self.GetSelectedItem(ii).GetId())
		
		self.UpdateProp()
		
		if len(selected) > 0:
			self._selectedarray = []
			for ii in range(len(self._items)):
				for jj in range(len(selected)):
					if self._items[ii].GetFileName() == selectedfname[jj] and \
							self._items[ii].GetId() == selecteditemid[jj]:
						
						self._selectedarray.append(ii)
						if len(self._selectedarray) == 1:
							self.ScrollToSelected()
			
			if len(self._selectedarray) > 0:
				self.Refresh()
				eventOut = thumbnailctrl.ThumbnailEvent(thumbnailctrl.wxEVT_THUMBNAILS_SEL_CHANGED, self.GetId())
				self.GetEventHandler().ProcessEvent(eventOut)
	
	def UpdateProp(self, checkSize=True):
		"""
		Updates :class:`OtherImagesCtrl` and its visible thumbnails.

		:param `checkSize`: ``True`` to update the items visibility if the window
		 size has changed.
		"""
		
		width = self.GetClientSize().GetWidth()
		self._cols = (width - self._tBorder) // (self._tWidth + self._tBorder)
		
		if self._cols <= 0:
			self._cols = 1
		
		tmpvar = (len(self._items) % self._cols and [1] or [0])[0]
		self._rows = len(self._items) // self._cols + tmpvar
		
		self._tCaptionHeight = []
		
		for row in range(self._rows):
			capHeight = 0
			
			for col in range(self._cols):
				ii = row * self._cols + col
				
				if len(self._items) > ii and self._items[ii].GetCaptionLinesCount(
						self._tWidth - self._tCaptionBorder
						) > capHeight:
					capHeight = self._items[ii].GetCaptionLinesCount(self._tWidth - self._tCaptionBorder)
			
			self._tCaptionHeight.append(capHeight)
		
		self.SetVirtualSize((
				self._cols * (self._tWidth + self._tBorder) + self._tBorder,
				self._rows * (self._tHeight + self._tBorder) + self.GetCaptionHeight(
						0, self._rows
						) + self._tBorder))
		
		self.SetSizeHints(
				self._tWidth + 2 * self._tBorder + 16,
				self._tHeight + 2 * self._tBorder + 8 + (
						self._rows and [self.GetCaptionHeight(0)] or [0]
						)[0])
		
		if checkSize and width != self.GetClientSize().GetWidth():
			self.UpdateProp(False)
	
	# Functions that we don't want to use
	def ThreadImage(self, *args, **kwargs):
		pass
	
	def LoadImages(self, *args, **kwargs):
		pass
	
	def ShowFileNames(self, *args, **kwargs):
		pass
	
	def ShowThumbs(self, *args, **kwargs):
		pass
	
	def Rotate(self, *args, **kwargs):
		pass
	
	def IsAudioVideo(self, *args, **kwargs):
		pass
	
	def IsVideo(self, *args, **kwargs):
		pass
	
	def IsAudio(self, *args, **kwargs):
		pass
	
	def DeleteFiles(self):
		pass
	
	def UpdateShow(self):
		self.UpdateProp()
