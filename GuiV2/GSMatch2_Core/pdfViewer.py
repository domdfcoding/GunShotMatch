# Name:		 pdfViewer.py
#
# Purpose:	  A PDF file viewer
#
# Adepted from: wx.lib.pdfviewer
# Author:	   David Hughes	 dfh@forestfield.co.uk
# Copyright:	Forestfield Software Ltd
# Licence:	  wxWindows Licence

# History:	  Created 17 Aug 2009
#			   08 Oct 2011, Michael Hipp	michael@redmule.com
#			   Added prompt, printer_name, orientation options to
#			   pdfViewer.Print(). Added option to pdfViewer.LoadFile() to
#			   accept a file-like object as well as a path string
#
#----------------------------------------------------------------------------

"""

This module provides the :class:`~wx.lib.pdfviewer.viewer.pdfViewer` to view PDF
files.
"""
"""
:class:`~wx.lib.pdfviewer.viewer.pdfViewer` class is derived from :class:`wx.ScrolledWindow` class
and can display and print PDF files.

Description
===========

The  :class:`~wx.lib.pdfviewer.viewer.pdfViewer` class is derived from :class:`wx.ScrolledWindow`
and can display and print PDF files. The whole file can be scrolled from
end to end at whatever magnification (zoom-level) is specified.

The viewer uses PyMuPDF (version 1.9.2 or later) or PyPDF2.
If neither of them are installed an import error exception will be raised.

PyMuPDF contains the Python bindings for the underlying MuPDF library, a cross platform,
complete PDF rendering library that is GPL licenced.

Further details on PyMuPDF can be found via https://pymupdf.readthedocs.io/en/latest/


Usage
=====

Sample usage::

	import wx
	import wx.lib.sized_controls as sc

	from wx.lib.pdfviewer import pdfViewer

	class PDFViewer(sc.SizedFrame):
		def __init__(self, parent, **kwds):
			super(PDFViewer, self).__init__(parent, **kwds)

			paneCont = self.GetContentsPane()
		
			self.viewer = pdfViewer(paneCont, wx.ID_ANY, wx.DefaultPosition,
									wx.DefaultSize,
									wx.HSCROLL|wx.VSCROLL|wx.SUNKEN_BORDER)

			self.viewer.SetSizerProps(expand=True, proportion=1)


	if __name__ == '__main__':
		import wx.lib.mixins.inspection as WIT
		app = WIT.InspectableApp(redirect=False)

		pdfV = PDFViewer(None, size=(800, 600))
		pdfV.viewer.LoadFile(r'a path to a .pdf file')
		pdfV.Show()

		app.MainLoop()


Alternatively you can drive the viewer from controls in your own application.

Externally callable methods are:

:meth:`~wx.lib.pdfviewer.viewer.pdfViewer.LoadFile`

:meth:`~wx.lib.pdfviewer.viewer.pdfViewer.Save`

:meth:`~wx.lib.pdfviewer.viewer.pdfViewer.Print`

:meth:`~wx.lib.pdfviewer.viewer.pdfViewer.SetZoom`

:meth:`~wx.lib.pdfviewer.viewer.pdfViewer.GoPage`

The viewer renders the pdf file content using Cairo if installed,
otherwise :class:`wx.GraphicsContext` is used. Printing is achieved by writing
directly to a :class:`wx.PrinterDC` and using :class:`wx.Printer`.

"""


import wx
from six import BytesIO, string_types
from wx.lib.pdfviewer.viewer import pypdfProcessor, pdfViewer as libpdfViewer, GraphicsContext

# Requires PyMuPDF / fitz
# see http://pythonhosted.org/PyMuPDF - documentation & installation
import fitz


#----------------------------------------------------------------------------

class pdfViewer(libpdfViewer):
	"""
	View pdf file in a scrolled window.  Contents are read from PDF file
	and rendered in a GraphicsContext. Show visible window contents
	as quickly as possible then, when using pyPDF, read the whole file and build
	the set of drawing commands for each page. This can take time for a big file or if
	there are complex drawings eg. ReportLab's colour shading inside charts and a
	progress bar can be displayed by setting self.ShowLoadProgress = True (default)
	"""
	def __init__(self, parent, nid, pos, size, style):
		"""
		Default class constructor.

		:param wx.Window `parent`: parent window. Must not be ``None``;
		:param integer `nid`: window identifier. A value of -1 indicates a default value;
		:param `pos`: the control position. A value of (-1, -1) indicates a default position,
		 chosen by either the windowing system or wxPython, depending on platform;
		:type `pos`: tuple or :class:`wx.Point`
		:param `size`: the control size. A value of (-1, -1) indicates a default size,
		 chosen by either the windowing system or wxPython, depending on platform;
		:type `size`: tuple or :class:`wx.Size`
		:param integer `style`: the button style (unused);

		"""
		wx.ScrolledWindow.__init__(self, parent, nid, pos, size,
								style | wx.NO_FULL_REPAINT_ON_RESIZE)
		self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)	 # recommended in wxWidgets docs
		self._showLoadProgress = False

		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_SIZE, self.OnResize)
		self.Bind(wx.EVT_SCROLLWIN, self.OnScroll)
		self.Bind(wx.EVT_IDLE, self.OnIdle)
		self.have_file = False
		self.resizing = False
		self.numpages = None
		self.zoomscale = -1	 # fit page to screen width
		self.nom_page_gap = 20  # nominal inter-page gap (points)
		self.scrollrate = 20	# pixels per scrollbar increment
		self.page_buffer_valid = False
		self.page_after_zoom_change = None
		self.ClearBackground()

#----------------------------------------------------------------------------

	# This section defines the externally callable methods:
	# LoadFile, Save, Print, SetZoom, and GoPage
	# also the getter and setter for ShowLoadProgress
	# that is only applicable if using PyPDF2

	def LoadFile(self, pdf_file):
		"""
		Read pdf file. Assume all pages are same size, for now.

		:param `pdf_file`: can be either a string holding
		a filename path or a file-like object.
		"""
		def create_fileobject(filename):
			"""
			Create and return a file object with the contents of filename,
			only used for testing.
			"""
			f = open(filename, 'rb')
			stream = f.read()
			return BytesIO(stream)

		self.pdfpathname = ''
		if isinstance(pdf_file, string_types):
			# a filename/path string, save its name
			self.pdfpathname = pdf_file
			# remove comment from next line to test using a file-like object
			# pdf_file = create_fileobject(pdf_file)
		self.pdfdoc = mupdfProcessor(self, pdf_file)

		self.numpages = self.pdfdoc.numpages
		self.pagewidth = self.pdfdoc.pagewidth
		self.pageheight = self.pdfdoc.pageheight
		self.page_buffer_valid = False
		self.Scroll(0, 0)			   # in case this is a re-LoadFile
		self.CalculateDimensions()	  # to get initial visible page range
		# draw and display the minimal set of pages
		self.pdfdoc.DrawFile(self.frompage, self.topage)
		self.have_file = True
		# now draw full set of pages
		wx.CallAfter(self.pdfdoc.DrawFile, 0, self.numpages-1)

	def PrintPreview(self, printer_name=None, orientation=None):
		pdd = wx.PrintDialogData()
		pdd.SetMinPage(1)
		pdd.SetFromPage(1)
		pdd.SetMaxPage(self.numpages)
		pdd.SetToPage(self.numpages)
		pdata = pdd.GetPrintData()
		if printer_name:
			pdata.SetPrinterName(printer_name)
		if orientation:
			pdata.SetOrientation(orientation)
		# PrintData does not return actual PrintQuality - it can't as printer_name not known
		# but it defaults to wx.PRINT_QUALITY_HIGH, overriding user's own setting for the
		# printer. However calling SetQuality with a value of 0 seems to leave the printer
		# setting untouched
		pdata.SetQuality(0)
		printer = wx.Printer(pdd)
		# printout = pdfPrintout('', self)
		preview = wx.PrintPreview(pdfPrintout('', self), pdfPrintout('', self))
		# preview.Print(prompt=True)
		preview_frame = wx.PreviewFrame(preview, self)
		preview_frame.Initialize()
		preview_frame.Show()

	def Print(self, prompt=True, printer_name=None, orientation=None):
		"""
		Print the pdf.

		:param boolean `prompt`: show the print dialog to the user (True/False). If
		 False, the print dialog will not be shown and the pdf will be printed
		 immediately. Default: True.
		:param string `printer_name`: the name of the printer that is to
		 receive the printout. Default: as set by the O/S.
		:param `orientation`: select the orientation (:class:`wx.PORTRAIT` or
		 :class:`wx.LANDSCAPE`) for the printout. Default: as set by the O/S.
		"""
		pdd = wx.PrintDialogData()
		pdd.SetMinPage(1)
		pdd.SetFromPage(1)
		pdd.SetMaxPage(self.numpages)
		pdd.SetToPage(self.numpages)
		pdata = pdd.GetPrintData()
		if printer_name:
			pdata.SetPrinterName(printer_name)
		if orientation:
			pdata.SetOrientation(orientation)
		# PrintData does not return actual PrintQuality - it can't as printer_name not known
		# but it defaults to wx.PRINT_QUALITY_HIGH, overriding user's own setting for the
		# printer. However calling SetQuality with a value of 0 seems to leave the printer
		# setting untouched
		pdata.SetQuality(0)
		printer = wx.Printer(pdd)
		printout = pdfPrintout('', self)
		if (not printer.Print(self, printout, prompt=prompt) and
					   printer.GetLastError() == wx.PRINTER_ERROR):
			dlg = wx.MessageDialog(self, 'Unable to perform printing',
							  'Printer' , wx.OK | wx.ICON_INFORMATION)
			dlg.ShowModal()
			dlg.Destroy()
		printout.Destroy()


#----------------------------------------------------------------------------

	# This section is concerned with rendering a sub-set of drawing commands on demand

	def CalculateDimensions(self):
		"""
		Compute the required buffer sizes to hold the viewed rectangle and
		the range of pages visible. Set self.page_buffer_valid = False if
		the current set of rendered pages changes
		"""

		self.frompage = 0
		self.topage = 0
		device_scale = wx.ClientDC(self).GetPPI()[0]/72.0   # pixels per inch/points per inch
		self.font_scale_metrics =  1.0
		self.font_scale_size = 1.0
		# for Windows only with wx.GraphicsContext the rendered font size is too big
		# in the ratio of screen pixels per inch to points per inch
		# and font metrics are too big in the same ratio for both for Cairo and wx.GC
		if wx.PlatformInfo[1] == 'wxMSW':
			self.font_scale_metrics = 1.0 / device_scale
			self.font_scale_size = 1.0 / device_scale

		self.winwidth, self.winheight = self.GetClientSize()
		
		self.Ypage = self.pageheight + self.nom_page_gap
		if self.zoomscale > 0.0:
			self.scale = self.zoomscale * device_scale
		else:
			if int(self.zoomscale) == -1:   # fit width
				self.scale = self.winwidth / self.pagewidth
			else:						   # fit page
				self.scale = self.winheight / self.pageheight
		self.Xpagepixels = int(round(self.pagewidth*self.scale))
		self.Ypagepixels = int(round(self.Ypage*self.scale))

		# adjust inter-page gap so Ypagepixels is a whole number of scroll increments
		# and page numbers change precisely on a scroll click
		idiv = self.Ypagepixels/self.scrollrate
		nlo = idiv * self.scrollrate
		nhi = (idiv + 1) * self.scrollrate
		if nhi - self.Ypagepixels < self.Ypagepixels - nlo:
			self.Ypagepixels = nhi
		else:
			self.Ypagepixels = nlo
		self.page_gap = self.Ypagepixels/self.scale - self.pageheight

		self.maxwidth = max(self.winwidth, self.Xpagepixels)
		self.maxheight = max(self.winheight, self.numpages*self.Ypagepixels)
		self.SetVirtualSize((self.maxwidth, self.maxheight))
		self.SetScrollRate(self.scrollrate, self.scrollrate)

		xv, yv = self.GetViewStart()
		dx, dy = self.GetScrollPixelsPerUnit()
		self.x0, self.y0   = (xv * dx, yv * dy)
		self.frompage = int(min(self.y0/self.Ypagepixels, self.numpages-1))
		self.topage = int(min((self.y0+self.winheight-1)/self.Ypagepixels, self.numpages-1))
		self.pagebufferwidth = max(self.Xpagepixels, self.winwidth)
		self.pagebufferheight = (self.topage - self.frompage + 1) * self.Ypagepixels

		self.page_y0 = self.frompage * self.Ypagepixels
		self.page_x0 = 0
		self.xshift = self.x0 - self.page_x0
		self.yshift = self.y0 - self.page_y0
		if not self.page_buffer_valid:  # via external setting
			self.cur_frompage = self.frompage
			self.cur_topage = self.topage
		else:   # page range unchanged? whole visible area will always be inside page buffer
			if self.frompage != self.cur_frompage or self.topage != self.cur_topage:
				self.page_buffer_valid = False	# due to page buffer change
				self.cur_frompage = self.frompage
				self.cur_topage = self.topage
		return

	def Render(self):
		"""
		Recalculate dimensions as client area may have been scrolled or resized.
		The smallest unit of rendering that can be done is the pdf page. So render
		the drawing commands for the pages in the visible rectangle into a buffer
		big enough to hold this set of pages. Force re-creating the page buffer
		only when client view moves outside it.
		With PyPDF2, use gc.Translate to render each page wrt the pdf origin,
		which is at the bottom left corner of the page.
		"""
		if not self.have_file:
			return
		self.CalculateDimensions()
		if not self.page_buffer_valid:
			# Initialize the buffer bitmap.
			self.pagebuffer = wx.Bitmap(self.pagebufferwidth, self.pagebufferheight)
			self.pdc = wx.MemoryDC(self.pagebuffer)	 # must persist

			gc = GraphicsContext.Create(self.pdc)	   # Cairo/wx.GraphicsContext API

			# white background
			path = gc.CreatePath()
			path.AddRectangle(0, 0,
								self.pagebuffer.GetWidth(), self.pagebuffer.GetHeight())
			gc.SetBrush(wx.WHITE_BRUSH)
			gc.FillPath(path)

			for pageno in range(self.frompage, self.topage+1):
				self.xpageoffset = 0 - self.x0
				self.ypageoffset = pageno*self.Ypagepixels - self.page_y0
				gc.PushState()
				gc.Translate(self.xpageoffset, self.ypageoffset)
				# scaling is done inside RenderPage
				self.pdfdoc.RenderPage(gc, pageno, scale=self.scale)
				# Show inter-page gap
				gc.SetBrush(wx.Brush(wx.Colour(180, 180, 180)))		#mid grey
				gc.SetPen(wx.TRANSPARENT_PEN)
				gc.DrawRectangle(
						0, self.pageheight*self.scale,
						self.pagewidth*self.scale, self.page_gap*self.scale
						)
				gc.PopState()
			gc.PushState()
			gc.Translate(0-self.x0, 0-self.page_y0)
			self.RenderPageBoundaries(gc)
			gc.PopState()

		self.page_buffer_valid = True
		self.Refresh(0) # Blit appropriate area of new or existing page buffer to screen

		# ensure we stay on the same page after zoom scale is changed
		if self.page_after_zoom_change:
			self.GoPage(self.page_after_zoom_change)
			self.page_after_zoom_change = None

#============================================================================

class mupdfProcessor(object):
	"""
	Create an instance of this class to open a PDF file, process the contents of
	each page and render each one on demand using the GPL mupdf library, which is
	accessed via the python-fitz package bindings (version 1.9.1 or later)
	"""
	def __init__(self, parent, pdf_file):
		"""
		:param `pdf_file`: a File object or an object that supports the standard
		read and seek methods similar to a File object.
		Could also be a string representing a path to a PDF file.
		"""
		self.parent = parent
		if isinstance(pdf_file, string_types):
			# a filename/path string, pass the name to fitz.open
			pathname = pdf_file
			self.pdfdoc = fitz.open(pathname)
		else:
			# assume it is a file-like object, pass the stream content to fitz.open
			# and a '.pdf' extension in pathname to identify the stream type
			pathname = 'fileobject.pdf'
			if pdf_file.tell() > 0:	 # not positioned at start
				pdf_file.seek(0)
			stream = bytearray(pdf_file.read())
			self.pdfdoc = fitz.open(pathname, stream)

		self.numpages = self.pdfdoc.pageCount
		page = self.pdfdoc.loadPage(0)
		self.pagewidth = page.bound().width
		self.pageheight = page.bound().height
		self.page_rect = page.bound()
		self.zoom_error = False	 #set if memory errors during render

	def DrawFile(self, frompage, topage):
		"""
		This is a no-op for mupdf. Each page is scaled and drawn on
		demand during RenderPage directly via a call to page.getPixmap()
		"""
		self.parent.GoPage(frompage)

	def RenderPage(self, gc, pageno, scale=1.0):
		" Render the set of pagedrawings into gc for specified page "
		page = self.pdfdoc.loadPage(pageno)
		matrix = fitz.Matrix(scale, scale)
		try:
			pix = page.getPixmap(matrix=matrix)   # MUST be keyword arg(s)
			bmp = wx.Bitmap.FromBuffer(pix.width, pix.height, pix.samples)
			gc.DrawBitmap(bmp, 0, 0, pix.width, pix.height)
			self.zoom_error = False
		except (RuntimeError, MemoryError):
			if not self.zoom_error:	 # report once only
				self.zoom_error = True
				dlg = wx.MessageDialog(self.parent, 'Out of memory. Zoom level too high?',
							  'pdf viewer' , wx.OK |wx.ICON_EXCLAMATION)
				dlg.ShowModal()
				dlg.Destroy()

class pdfPrintout(wx.Printout):
	"""
	Class encapsulating the functionality of printing out the document. The methods below
	over-ride those of the base class and supply document-specific information to the
	printing framework that calls them internally.
	"""
	def __init__(self, title, view):
		"""
		Pass in the instance of dpViewer to be printed.
		"""
		wx.Printout.__init__(self, title)
		self.view = view

	def HasPage(self, pageno):
		"""
		Report whether pageno exists.
		"""
		if pageno <= self.view.numpages:
			return True
		else:
			return False

	def GetPageInfo(self):
		"""
		Supply maximum range of pages and the range to be printed
		These are initial values passed to Printer dialog, where they
		can be amended by user.
		"""
		maxnum = self.view.numpages
		return (1, maxnum, 1, maxnum)

	def OnPrintPage(self, page):
		"""
		Provide the data for page by rendering the drawing commands
		to the printer DC, MuPDF returns the page content from an internally
		generated bitmap and sfac sets it to a high enough resolution that
		reduces anti-aliasing blur but keeps it small to minimise printing time
		"""
		sfac = 4.0
		pageno = page - 1	   # zero based
		width = self.view.pagewidth
		height = self.view.pageheight
		self.FitThisSizeToPage(wx.Size(width*sfac, height*sfac))
		dc = self.GetDC()

		gc = wx.GraphicsContext.Create(dc)
		
		self.view.pdfdoc.RenderPage(gc, pageno, sfac)
		return True
