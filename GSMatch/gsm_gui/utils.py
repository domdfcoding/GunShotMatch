def collapse_label(text, collapsed=True):
	import sys
	if sys.platform == "win32":
		return f"{text} {'>>' if collapsed else '<<'}"
	else:
		return f"{'⯈' if collapsed else '⯆'} {text}"

def get_toolbar_icon(icon_name, size=24):
	import wx
	return wx.Bitmap(wx.ArtProvider.GetBitmap(f"wx{icon_name}", "wxART_TOOLBAR_C",wx.Size(size,size)))