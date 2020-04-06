#  !/usr/bin/env python
#   -*- coding: utf-8 -*-
#
#  welcome_page.py
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

# stdlib
import base64
import datetime
import pathlib
from io import BytesIO

# 3rd party
import appdirs
import wx
from importlib_resources import read_text
from jinja2 import Template

# this package
from GuiV2.icons import get_icon


def get_new_expr_icon():
	icon = get_icon("new-experiment", 24)
	buf = BytesIO()
	icon.ConvertToImage().SaveFile(buf, "image/png")
	return base64.b64encode(buf.getvalue()).decode("utf-8")


def get_new_project_icon():
	return get_b64_icon(wx.ART_NEW)


def get_b64_icon(icon_name):
	icon = get_icon(icon_name, 24)
	buf = BytesIO()
	icon.ConvertToImage().SaveFile(buf, "image/png")
	return base64.b64encode(buf.getvalue()).decode("utf-8")


def get_open_icon():
	return get_b64_icon(wx.ART_FILE_OPEN)


def get_welcome_page():
	news = [
			{
					"title": "First News Item",
					"date": datetime.datetime.today(),
					"url": "#",
					"content": "This is a news item",
					},
			{
					"title": "Second News Item",
					"date": datetime.datetime.today(),
					"url": "#",
					"content": "This is a news item",
					},
			{
					"title": "Third News Item",
					"date": datetime.datetime.today(),
					"url": "http://bbc.co.uk/news",
					"content": "This is a news item",
					},
			]
	
	# TODO: Get news from server
	
	template = Template(read_text("GuiV2.GSMatch2_Core.GUI", "welcome.html"))
	
	return template.render(
			news=news,
			open_icon=get_open_icon(),
			new_project_icon=get_new_project_icon(),
			new_expr_icon=get_new_expr_icon(),
			project_navigator_image=project_navigator_image,
			view_toolbar_image=view_toolbar_image,
			reset_view_icon=get_b64_icon(wx.ART_GO_HOME),
			previous_view_icon=get_b64_icon(wx.ART_GO_TO_PARENT),
			select_icon=get_b64_icon("default-cursor"),
			zoom_icon=get_b64_icon("zoom"),
			pan_icon=get_b64_icon("gimp-tool-move"),
			spectrum_click_icon=get_b64_icon("mass-spectrum"),
			spectrum_id_icon=get_b64_icon("mass-spectrum-123"),
			spectrum_rt_icon=get_b64_icon("mass-spectrum-rt"),
			toolbar_background_colour=wx.SystemSettings.GetColour(wx.SYS_COLOUR_BACKGROUND).GetAsString(
				wx.C2S_CSS_SYNTAX),
			)


def render_welcome_page():
	output_file = pathlib.Path(appdirs.user_config_dir("GunShotMatch")) / "welcome.html"
	
	with open(output_file, "w") as fp:
		fp.write(get_welcome_page())
	
	return output_file


project_navigator_image = """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
Sy3I3t7+5s2bG9avv3zlSl5eHp1ONzc379KlC4/Ho9PpixYt0tHR2R4TQ+4uDgkJqZEPThDilUX4
PNW5aeNGkVD477VrJcXF9vb2AoHA09Nz27Zt0dHRmZmZ6enpurq6dnZ2aqqqOI5vWL9eX0/v2LFj
Oe/fczgcPV1dHMdr50DOlErzwqVbD5eIqlMLS0vLN2/eaGlpjR0zJjIykoySY9gaVSB56+LiIkvT
ellMqr41MDckZO26dXJif5qJWUTWYsn3QmJi4uDBgyVDnj179uzZM3J3nMTaDLNfv36K2hHPv757
x12T8XN6mVBucmNB0sg/hcETjhyReiw7OawW4/Lly2RIZWXFL1LVbLbq5cuXvb29dHR0G6Up4TiK
omfOnh05cqS5ufnDBw/IhUMKktDV0+Pz+Zf/+cfT0/MnVvPTp4I7d1JqvHTNCP+HtUwHB4fay/uK
TB9JjOiKXyRff9QhkGgiViSq8p6mvWe38rBgIz/+8cZSSsLI32LwpqldQ73Mn9vP/saTX2Rh7Lhx
KSkp+fn5ALAoMhJBkEYq6GcYqX7z+TvNdGqHosyvkBU/j8BxAicAxwEHIAgCw4EAAicAJwAnHEVY
+rorCIq0nLtdorctOjt30Lq7QkmB7afE7xz2nUiB++Z6woHEK/czckuFTC0TO/dOwyeP9NKttyMl
enEkMiJz6EH3hrGCnMeJ0ivLx6y6XMjHAaUrq+ub2Xt1G/Z7P1ed5jNI/0bjND5kHWXw60CsLyZ7
+8+3oLy8vLDwk56e3syZM/r269tIpTR/EACA49ivYJ9m/EsmsiJOnz794cMHOU8aGBj069dP0aGT
UNjCr5PEGOOr/8T4eONe7WcZLmPXTGr9+XRLVMVQH4XX36F5VqTGBocdztHz6zMyxNFAWVCU/eRB
GY/exLp1rKKkFHMcvT7IS1lYVZSTdunIjjkp2atj57RRpc7Tp7zM5uFlJiQc+dIVUP6lDIg/n6W8
zGZJmd7e3jNnzszLy5Maa2hoGB0dXQ9+EuGEQCjIf1xNkzUpkwAcIwiRqIIrxbgcE6dWrZS/4pEa
fsyH2wdi4v9+8KoA17T1C5wxs68d7c6qwREZA+PixliiAIBn7Z8w4XyrjUdnu1ZrzHu0b82Rtxbj
ojeOtq3O269zn8+v9af7h7ftPnMnswjRtvbuO2V6oLs2CgB4wbWtKw/cycr9WMoFZV2btkNmBA9y
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
"""

view_toolbar_image = """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
QmCC
"""

if __name__ == '__main__':
	
	app = wx.App()
	print(get_welcome_page())
	print(render_welcome_page())