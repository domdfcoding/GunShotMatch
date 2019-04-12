#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  pynist.py
from __future__ import print_function
_version = 0.25
#  
"""Python Interface to NIST MS Search"""
#
#  Copyright 2018 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#	generate_ini contains the .ini file from NIST MS Search
#		Copyright NIST
#  
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
#  
#  Requires NIST MS Search to be installed on your computer. 
#  A fully functional demo version is available from:
#		http://chemdata.nist.gov/mass-spc/ms-search/
#
#  Makes calls to the NIST MS Search API as described here:
#		http://chemdata.nist.gov/mass-spc/ms-search/docs/Ver20Man_11.pdf


__author__ = "Dominic Davis-Foster"
__copyright__ = "Copyright 2018 Dominic Davis-Foster"

__license__ = "GPL"
__version__ = "0.1.0"
__email__ = "dominic@davis-foster.co.uk"

import os
import traceback
import platform
import shutil
import time
import io

from subprocess import Popen, PIPE
try:
	from paths import parent_path
except ModuleNotFoundError:
	from utils.paths import parent_path

"""Generates the INI file for NIST MS Search and copies it in place of 
the current config."""
def generate_ini(nist_path, lib_name, num_hits):
	"""Generate Configuration"""
	config = """[MAIN]
Version=2.0
Library Directory={0}
Program=NIST MS
Active Frame=2
Placement_flags=2
Placement_show=3
Active Show=3
Display Warning=1
Placement_minx=-1
Placement_miny=-1
Placement_maxx=-1
Placement_maxy=-1
Placement_left=89
Placement_top=130
Placement_right=1768
Placement_bottom=1074
Wrong Libraries=
Web Permission=0
Web SOS Permission=0
[Search Options]
Automatic=1
Ignore Precursor=1
Parent Mass=0
Precursor Tolerance=1.6
Ions Tolerance=0.8
Alt Peak Matching=1
Peptide Search=0
Type=1
As MW=1
MW=1
Reverse=0
Penalize=0
Search with MW=1
Preasearch=0
Apply Limits=0
Min Mass Type=0
Min Mass=1
Max Mass ON=0
Max Mass=2000
Min Abund ON=0
Min Abund=1
Printing=0
Return Focus=0
Hits to Print={2}
Print Spectra=1
Print Structure=1
Apply MaxLength=0
MaxLength=2000
Sort Mode=0
Match Clusters=1
Match Rings=1
Show Struct Homolog=1
Weighting=0
Use Specified Parent=0
Precursor Tolerance Units=0
Ions Tolerance Units=0
Ignore Precursor Tolerance=1.6
Ignore Precursor Tolerance Units=0
INCHIKEY=
Ion Mode=0
[Libraries]
Library_0=mainlib
Library_1={1}
Library_2=
Library_3=
Library_4=
Library_5=
Library_6=
Library_7=
Library_8=
Library_9=
Library_10=
Library_11=
Library_12=
Library_13=
Library_14=
Library_15=
Library_16=
Library_17=
Library_18=
Library_19=
Library_20=
Library_21=
Library_22=
Library_23=
Library_24=
Library_25=
Library_26=
Library_27=
Library_28=
Library_29=
Library_30=
Library_31=
Library_32=
Library_33=
Library_34=
Library_35=
Library_36=
Library_37=
Library_38=
Library_39=
Library_40=
Library_41=
Library_42=
Library_43=
Library_44=
Library_45=
Library_46=
Library_47=
Library_48=
Library_49=
Library_50=
Library_51=
Library_52=
Library_53=
Library_54=
Library_55=
Library_56=
Library_57=
Library_58=
Library_59=
Library_60=
Library_61=
Library_62=
Library_63=
Library_64=
Library_65=
Library_66=
Library_67=
Library_68=
Library_69=
Library_70=
Library_71=
Library_72=
Library_73=
Library_74=
Library_75=
Library_76=
Library_77=
Library_78=
Library_79=
Library_80=
Library_81=
Library_82=
Library_83=
Library_84=
Library_85=
Library_86=
Library_87=
Library_88=
Library_89=
Library_90=
Library_91=
Library_92=
Library_93=
Library_94=
Library_95=
Library_96=
Library_97=
Library_98=
Library_99=
Library_100=
Library_101=
Library_102=
Library_103=
Library_104=
Library_105=
Library_106=
Library_107=
Library_108=
Library_109=
Library_110=
Library_111=
Library_112=
Library_113=
Library_114=
Library_115=
Library_116=
Library_117=
Library_118=
Library_119=
Library_120=
Library_121=
Library_122=
Library_123=
Library_124=
Library_125=
Library_126=
Order_0=1 1
Order_1=1 1
Order_2=0
Order_3=1 1
Order_4=1 1
Order_5=1 1
Order_6=1 1
Order_7=1 2
Order_8=1 1
Order_9=1 1
Order_10=0
Order_11=1 1
[ICHI]
On=1
Isotope=1
Stereo=0
Derivative=0
[Search Options]
Automatic=1
[Library Search]
SpecList Tab=1
Placement_flags=0
Placement_show=1
Layout=1
Hit Splitter Orientation=1
List Tab=0
Compare Tab=1
Hit Tab=0
Unknown Tab=0
Replicates=0
Exact Match=0
Splitter=0.424818
List Splitter=0 0
Unknown Splitter=0.481338
Unknown Splitter Orientation=1
Compare Splitter=0 0
Hit Splitter=0.481338
SpecList Splitter=0.481338
SpecList Splitter Orientation=1
Placement_minx=-1
Placement_miny=-1
Placement_maxx=-9
Placement_maxy=-38
Placement_left=0
Placement_top=1
Placement_right=1399
Placement_bottom=547
Hits Column=27 40 38 238 80 63 0 0 68 38 39 0 0 0 0 0 0 0 0 0 0 0 0 31 0 0 0 0
SpecList Column=27 40 39 51 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
Hits Column Order=28 1 2 4 5 7 6 14 8 12 23 22 15 17 18 24 25 16 19 9 10 3 11 13 20 21 26 27 28
SpecList Order=28 1 2 4 5 7 6 14 8 12 23 22 15 17 18 24 25 16 19 9 10 3 11 13 20 21 26 27 28
[Library Hit]
Order Number=1
Structure Only=0
Library=0
Structure Size=50
Match=1
Probability=1
Reverse Match=1
Clear History=0
No. Syn=0
No. DBs=0
Font Name=MS Shell Dlg
Font Pts=-8
Font Width=0
Font Esc=0
Font Orientation=0
Font Weight=400
Font IUSC=0
Font PCQP=654311424
Color=0 255 16711680 16777215 16777215 0
Short Lib=1
Selected Column=27 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26
[Other Hit]
Order Number=1
Structure Only=0
Library=0
Structure Size=50
Match=0
Probability=0
Reverse Match=0
Clear History=0
No. Syn=1
No. DBs=1
Font Name=MS Shell Dlg
Font Pts=-8
Font Width=0
Font Esc=0
Font Orientation=0
Font Weight=400
Font IUSC=0
Font PCQP=654311424
Color=0 255 16711680 16777215 16777215 0
Short Lib=1
Selected Column=27 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26
[Library Spec List]
Order Number=1
Structure Only=0
Library=0
Structure Size=50
Match=0
Probability=0
Reverse Match=0
Clear History=0
No. Syn=1
No. DBs=1
Font Name=MS Shell Dlg
Font Pts=-8
Font Width=0
Font Esc=0
Font Orientation=0
Font Weight=400
Font IUSC=0
Font PCQP=654311424
Color=0 255 16711680 16777215 16777215 0
Short Lib=1
Selected Column=27 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26
[Peptide Search Options]
Cysteine Modification=0
Comment Fields=Contributor
Show Fields On Plot=0
TF qry=0
E Omssa=0
TF lib=0
RevImp=1
Weight Omssa=0
Weight Num Rep=0
Weight Qtof=0
Treshold=0
NumMP=0
[Exact Mass Search Options]
ExMass Type=2
ExMass Value=CO
ExMass Units=0
ExMass Tolerance=500
ExMass Gain Type=0
ExMass Gain Value=
ExMass Charge=1
ExMass Correction=0
ExMass Precursor Type=0
ExMass Peaks=1
[Precursor Search Options]
Type=0
Value=114.0662
Units=0
Tolerance=50
Charge=1
Polarity=1
Protonation=0
Isotope=0
[Library Hit Plot]
Mass Label=1
Pep Label=0
Font Name=MS Shell Dlg
Font Pts=-8
Font Width=0
Font Esc=0
Font Orientation=0
Font Weight=400
Font IUSC=0
Font PCQP=654311424
Color=0 255 16711680 0 255 16777215
Limits ON=0
Wrap=0
MW=0
CAS=0
Formula=0
Threshold=0
Structure=1
Width=1
Loss Label=0
[Library SpecList Plot]
Mass Label=1
Pep Label=0
Font Name=MS Shell Dlg
Font Pts=-8
Font Width=0
Font Esc=0
Font Orientation=0
Font Weight=400
Font IUSC=0
Font PCQP=654311424
Color=0 255 16711680 0 255 16777215
Limits ON=0
Wrap=0
MW=0
CAS=0
Formula=0
Threshold=0
Structure=1
Width=1
Loss Label=0
[SpecList Hit]
Library=0
Font Name=MS Shell Dlg
Font Pts=-8
Font Width=0
Font Esc=0
Font Orientation=0
Font Weight=400
Font IUSC=0
Font PCQP=654311424
Color=0 255 16711680 16777215 16777215 0
Structure Only=0
Structure Size=50
Clear History=0
Short Lib=1
Selected Column=27 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26
[RI Search Options]
Use RI in Search=0
Column Type=1
Override Selected Column=0
Use Other NonPolar=1
Library Uncpecified=1
Window=10
Slope=2
[Import]
RI type=3
Filter=11
Synonyms=1
MS1 Accurate mass=0
Coeff=1 0
Add to speclist=0
Precursor Accuracy=4
Peak Accuracy=4
Insource Peak Accuracy=4
Threshold Percent Active=0
Threshold Percent=0
Threshold Absolute Active=0
Threshold Absolute=0
[RI]
Unspecified RI=3
[Structure Import]
Dir=C:\\NISTDEMO\\MSSEARCH\\
Filter=1
[Export]
Filter=1
Synonyms=0
MS1 Accurate mass=0
Coeff=1 0
Add to speclist=0
Precursor Accuracy=4
Peak Accuracy=4
Insource Peak Accuracy=4
Threshold Percent Active=0
Threshold Percent=0
Threshold Absolute Active=0
Threshold Absolute=0
RI type=3
[BAR-Summary]
Bars=11
ScreenCX=1920
ScreenCY=1080
[REPORT]
Ten Largest Peaks=1
Compound Info=1
Mass Intensity List=0
Synonyms=1
Plot=1
Structure=1
First Hits=1
First Hits Number=3
Unknown=0
RI=0
[Substructure Export]
Filter=1
Dir=
[Substructure Import]
Filter=1
Dir=
[Search AnyPeaks Options]
Other=0
Peaks=0
Hitlist size=100
Peak0=
Peak1=
Peak2=
Peak3=
Peak4=
Peak5=
Peak6=
Peak7=
Peak8=
Peak9=
Peak10=
[Other Searches Options]
CAS=1501-05-9
MW=1
ID=1-2
EPA=
Formula=
Seq Hitlist size=100
[Constraints]
Library ON=0
Formula ON=0
MW ON=0
AnyPeaks ON=0
Sequentiial ON=0
Exact MW ON=0
Precursor=0
Active MW=0
MINMW=1
MAXMW=2000
Active Name=0
Name Fragment=
Elements Value=0
Elements Present=0
Mode Elements=0
Num Elements=0
Elements0=
Elements1=
Elements2=
Elements3=
Elements4=
Elements5=
Elements6=
Elements7=
Elements8=
Elements9=
Num Compare Elements=0
Compare Elements0=
Compare Elements1=
Compare Elements2=
Compare Elements3=
Compare Elements4=
Compare Elements5=
Compare Elements6=
Compare Elements7=
Compare Elements8=
Compare Elements9=
Active Peaks=0
Mode Peaks=1
Num AnyPeaks=0
Active OtherDB=0
OtherDB=0
Active Instrument Type=0
Instrument Type=0
Active Tags=0
Tags=
Active Peptide Sequence=0
Peptide Sequence=
Active Proton=0
Proton Mode=0
Proton Low=
Proton Hi=
Proton Exact=
Active Charge=0
Charge Mode=0
Charge Low=
Charge Hi=
Charge Exact=
Active Residue=0
Residue Mode=0
Residue Low=
Residue Hi=
Residue Exact=
Active Exact MW=0
ExMass Type=0
ExMass Value=
ExMass Units=0
ExMass Tolerance=
ExMass Gain Type=0
ExMass Gain Value=
ExMass Charge=1
ExMass Correction=0
ExMass Precursor Type=0
ExMass Peaks=1
Active Precursor Type=0
Precursor Type=0
[Library Unknown Plot]
Font Name=MS Shell Dlg
Font Pts=-8
Font Width=0
Font Esc=0
Font Orientation=0
Font Weight=400
Font IUSC=0
Font PCQP=654311424
Color=0 255 16711680 0 255 16777215
Limits ON=0
Wrap=0
MW=0
CAS=0
Formula=0
Threshold=0
Structure=1
Width=1
Mass Label=1
Pep Label=0
Loss Label=0
[Library Unknown Text]
Font Name=MS Shell Dlg
Font Pts=-8
Font Width=0
Font Esc=0
Font Orientation=0
Font Weight=400
Font IUSC=0
Font PCQP=654311424
Color=16711680 0 255 8421376 16777215
Ten Peaks=1
Compound=1
Intensity=0
Synonyms=1
Rows=0
Noise=0
Wrap Synonyms=0
RI=1
RI All=1
RI Num=2
[Library Hit Text]
Font Name=MS Shell Dlg
Font Pts=-8
Font Width=0
Font Esc=0
Font Orientation=0
Font Weight=400
Font IUSC=0
Font PCQP=654311424
Color=16711680 0 255 8421376 16777215
Ten Peaks=1
Compound=1
Intensity=0
Synonyms=1
Rows=0
Noise=0
Wrap Synonyms=0
RI=1
RI All=1
RI Num=2
[Library SpecList Text]
Font Name=MS Shell Dlg
Font Pts=-8
Font Width=0
Font Esc=0
Font Orientation=0
Font Weight=400
Font IUSC=0
Font PCQP=654311424
Color=16711680 0 255 8421376 16777215
Ten Peaks=1
Compound=1
Intensity=0
Synonyms=1
Rows=0
Noise=0
Wrap Synonyms=0
RI=1
RI All=1
RI Num=2
[Library Compare]
Font Name=MS Shell Dlg
Font Pts=-8
Font Width=0
Font Esc=0
Font Orientation=0
Font Weight=400
Font IUSC=0
Font PCQP=654311424
Color=0 255 16711680 32768 16777215 16711935 8421504
Limit ON=0
Threshold=0
Show=1
Show Structure=0
Independent Zoom=0
Width=1
Mass Label=1
Pep Label=0
Loss Label=0
[Library Histogram]
Font Name=MS Shell Dlg
Font Pts=-8
Font Width=0
Font Esc=0
Font Orientation=0
Font Weight=400
Font IUSC=0
Font PCQP=654311424
Color=0 16711680 255 16777215
Discret=25
Axis=1
Automatic=1
Min=0
Max=1000
[Library Display]
Neutral Loss=0
Scale=2
Min mz=0
Max mz=1000
Default Search Anchor=1
Search Anchor=0
Default Hit Anchor=1
Hit Anchor=0
Max Loss=70
mz=10
[Show Derivative]
Silylation=0
Acylation=0
Oximation=0
Mondendate=0
Bidentate=0
Silylation Selected=0
Acylation Selected=0
Oximation Selected=0
Mondendate Selected=0
Bidentate Selected=0
[Incremental Search]
Placement_flags=2
Placement_show=3
Placement_minx=-1
Placement_miny=-1
Placement_maxx=-9
Placement_maxy=-38
Placement_left=44
Placement_top=44
Placement_right=1443
Placement_bottom=591
Key=5CHLORO2METHYL4ISO
Splitter=0.3282
Layout=1
Plot Splitter=0.484395
Plot Splitter Orientation=0
List Tab=0
Spectrum Tab=0
Alpha=0
[Incremental View]
Font Name=MS Shell Dlg
Font Pts=-8
Font Width=0
Font Esc=0
Font Orientation=0
Font Weight=400
Font IUSC=0
Font PCQP=654311424
Color=0 255 16711680 16777215 16777215 0
Auto Display=1
Structure Only=50
[Incremental Plot]
Font Name=MS Shell Dlg
Font Pts=-8
Font Width=0
Font Esc=0
Font Orientation=0
Font Weight=400
Font IUSC=0
Font PCQP=654311424
Color=0 255 16711680 0 255 16777215
Limits ON=0
Wrap=0
MW=0
CAS=0
Formula=0
Threshold=0
Structure=1
Width=1
Mass Label=1
Pep Label=0
Loss Label=0
[Incremental Text]
Font Name=MS Shell Dlg
Font Pts=-8
Font Width=0
Font Esc=0
Font Orientation=0
Font Weight=400
Font IUSC=0
Font PCQP=654311424
Color=16711680 0 255 8421376 16777215
Ten Peaks=1
Compound=1
Intensity=0
Synonyms=1
Rows=0
Noise=0
Wrap Synonyms=0
RI=1
RI All=1
RI Num=2
[Other Search]
Placement_flags=0
Placement_show=1
Placement_minx=-1
Placement_miny=-1
Placement_maxx=-9
Placement_maxy=-38
Placement_left=22
Placement_top=22
Placement_right=1421
Placement_bottom=569
Splitter=0.324818
Layout=1
Plot Splitter=0.482759
Plot Splitter Orientation=0
List Tab=0
Spectrum Tab=0
Replicates=0
Search Mode=6
Column=27 40 38 51 0 0 0 0 0 38 39 0 0 0 0 0 0 0 0 0 0 0 0 31 0 0 0 0
Column Order=28 1 2 4 5 7 6 14 8 12 23 22 15 17 18 24 25 16 19 9 10 3 11 13 20 21 26 27 28
[Other Plot]
Font Name=MS Shell Dlg
Font Pts=-8
Font Width=0
Font Esc=0
Font Orientation=0
Font Weight=400
Font IUSC=0
Font PCQP=654311424
Color=0 255 16711680 0 255 16777215
Limits ON=0
Wrap=0
MW=0
CAS=0
Formula=0
Threshold=0
Structure=1
Width=1
Mass Label=1
Pep Label=0
Loss Label=0
[Other Text]
Font Name=MS Shell Dlg
Font Pts=-8
Font Width=0
Font Esc=0
Font Orientation=0
Font Weight=400
Font IUSC=0
Font PCQP=654311424
Color=16711680 0 255 8421376 16777215
Ten Peaks=1
Compound=1
Intensity=0
Synonyms=1
Rows=0
Noise=0
Wrap Synonyms=0
RI=1
RI All=1
RI Num=2
[Compare]
Placement_flags=0
Placement_show=1
Placement_minx=-1
Placement_miny=-1
Placement_maxx=65
Placement_maxy=24
Placement_left=66
Placement_top=66
Placement_right=1465
Placement_bottom=613
Splitter=0.242739 0.242739
Tab=0
[Compare Plot]
Font Name=MS Shell Dlg
Font Pts=-8
Font Width=0
Font Esc=0
Font Orientation=0
Font Weight=400
Font IUSC=0
Font PCQP=654311424
Color=0 255 16711680 0 255 16777215
Limits ON=0
Wrap=0
MW=0
CAS=0
Formula=0
Threshold=0
Structure=1
Width=1
Mass Label=1
Pep Label=0
Loss Label=0
[Compare Result]
Font Name=MS Shell Dlg
Font Pts=-8
Font Width=0
Font Esc=0
Font Orientation=0
Font Weight=400
Font IUSC=0
Font PCQP=654311424
Color=0 255 16711680 32768 16777215 16711935 8421504
Limit ON=0
Threshold=0
Show=1
Show Structure=0
Independent Zoom=0
Width=1
Mass Label=1
Pep Label=0
Loss Label=0
[Compare List]
Font Name=MS Shell Dlg
Font Pts=-8
Font Width=0
Font Esc=0
Font Orientation=0
Font Weight=400
Font IUSC=0
Font PCQP=654311424
Color=32768 0 255 16711680 16777215 0 255
Names=1
No Structure=0
Limits ON=0
Threshold=0
Spectra on Page=3
Overwrite=1
Insert=1
Hits=3
Wrap=0
MW=0
CAS=0
Formula=0
Width=1
Mass Label=1
Pep Label=0
Loss Label=0
[Compare Display]
Neutral Loss=0
Scale=2
Min mz=0
Max mz=1000
Default Search Anchor=1
Search Anchor=0
Default Hit Anchor=1
Hit Anchor=0
Max Loss=70
mz=10
[SpecList]
Placement_flags=0
Placement_show=1
Placement_minx=-1
Placement_miny=-1
Placement_maxx=65
Placement_maxy=24
Placement_left=88
Placement_top=88
Placement_right=1487
Placement_bottom=635
Splitter=0.324818
Layout=1
Plot Splitter=0.482759
Plot Splitter Orientation=0
List Tab=0
Spectrum Tab=0
Column=27 40 120 317 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
Column Order=28 1 2 4 5 7 6 14 8 12 23 22 15 17 18 24 25 16 19 9 10 3 11 13 20 21 26 27 28
[SpecList Plot]
Font Name=MS Shell Dlg
Font Pts=-8
Font Width=0
Font Esc=0
Font Orientation=0
Font Weight=400
Font IUSC=0
Font PCQP=654311424
Color=0 255 16711680 0 255 16777215
Limits ON=0
Wrap=0
MW=0
CAS=0
Formula=0
Threshold=0
Structure=1
Width=1
Mass Label=1
Pep Label=0
Loss Label=0
[SpecList Text]
Font Name=MS Shell Dlg
Font Pts=-8
Font Width=0
Font Esc=0
Font Orientation=0
Font Weight=400
Font IUSC=0
Font PCQP=654311424
Color=16711680 0 255 8421376 16777215
Ten Peaks=1
Compound=1
Intensity=0
Synonyms=1
Rows=0
Noise=0
Wrap Synonyms=0
RI=1
RI All=1
RI Num=2
[BAR-Bar0]
BarID=59419
Bars=7
Bar#0=0
Bar#1=32768
Bar#2=0
Bar#3=59647
Bar#4=0
Bar#5=59392
Bar#6=0
[BAR-Bar1]
BarID=32768
Visible=0
XPos=0
YPos=0
MRUWidth=0
Docking=1
MRUDockID=0
MRUDockLeftPos=0
MRUDockTopPos=0
MRUDockRightPos=0
MRUDockBottomPos=0
MRUFloatStyle=4
MRUFloatXPos=-2147483648
MRUFloatYPos=0
[BAR-Bar2]
BarID=59422
Bars=3
Bar#0=0
Bar#1=32769
Bar#2=0
[BAR-Bar3]
BarID=32769
Visible=0
XPos=0
YPos=0
MRUWidth=0
Docking=1
MRUDockID=0
MRUDockLeftPos=0
MRUDockTopPos=0
MRUDockRightPos=0
MRUDockBottomPos=0
MRUFloatStyle=4
MRUFloatXPos=-2147483648
MRUFloatYPos=0
[BAR-Bar4]
BarID=59420
Bars=3
Bar#0=0
Bar#1=32770
Bar#2=0
[BAR-Bar5]
BarID=32770
Visible=0
XPos=0
YPos=0
MRUWidth=0
Docking=1
MRUDockID=0
MRUDockLeftPos=0
MRUDockTopPos=0
MRUDockRightPos=0
MRUDockBottomPos=0
MRUFloatStyle=4
MRUFloatXPos=-2147483648
MRUFloatYPos=0
[BAR-Bar6]
BarID=59421
Bars=3
Bar#0=0
Bar#1=32771
Bar#2=0
[BAR-Bar7]
BarID=32771
Visible=0
XPos=0
YPos=0
MRUWidth=0
Docking=1
MRUDockID=0
MRUDockLeftPos=0
MRUDockTopPos=0
MRUDockRightPos=0
MRUDockBottomPos=0
MRUFloatStyle=4
MRUFloatXPos=-2147483648
MRUFloatYPos=0
[BAR-Bar8]
BarID=59393
MRUWidth=0
[BAR-Bar9]
BarID=59647
XPos=0
MRUWidth=107
Docking=1
MRUDockID=59419
MRUDockLeftPos=0
MRUDockTopPos=-1
MRUDockRightPos=1920
MRUDockBottomPos=33
MRUFloatStyle=8196
MRUFloatXPos=-2147483648
MRUFloatYPos=0
[BAR-Bar10]
BarID=59392
YPos=33
MRUWidth=253
Docking=1
MRUDockID=0
MRUDockLeftPos=0
MRUDockTopPos=33
MRUDockRightPos=270
MRUDockBottomPos=66
MRUFloatStyle=8196
MRUFloatXPos=-2147483648
MRUFloatYPos=0
""".format(nist_path, lib_name, num_hits)

	try:
		#Repace nistms.INI configuration
		ini_file = os.path.join(nist_path,"nistms.INI")
		ini_bak = os.path.join(nist_path,"nistms.INI.bak")
		if os.path.isfile(ini_file):
			if os.path.isfile(ini_bak):
				os.unlink(ini_bak)
			os.rename(ini_file,ini_bak)	

		"""Write Configuration to file"""
		with open(ini_file,"w") as f:
			f.write(config)
			
	except:
		traceback.print_exc()	#print the error
		#nist_cleanup()
		sys.exit(1)

"""Reloads Original Configuration File"""
def reload_ini(nist_path):
	
	close_nist()
	
	ini_file = os.path.join(nist_path,"nistms.INI")
	ini_bak = os.path.join(nist_path,"nistms.INI.bak")
	
	if os.path.isfile(ini_bak):
		if os.path.isfile(ini_file):
			os.unlink(ini_file)
		os.rename(ini_bak,ini_file)

"""Closes NIST MS Search (the hard way)"""
def close_nist():
	if platform.system() == "Linux":
		Popen(["wine","Taskkill", "/IM", "nistms.exe", "/F"],stdout=PIPE, stderr=PIPE)
	else:
		Popen(["Taskkill", "/IM", "nistms.exe", "/F"],stdout=PIPE, stderr=PIPE)

class nistError(Exception):
	def __init__(self, value):
		self.parameter = value
	def __str__(self):
		return repr(self.parameter)

def nist_db_connector(nist_dir, spectrum, search_len = 1):
	attempts = 101
	while True:#attempts > 100:
		attempts = 0
		#if type(spectrum) == dict
		# still needs to be coded to convert from dictionary or list to MSP
		spectrum_file = os.path.basename(spectrum)
		file_extension = os.path.splitext(spectrum)[-1]
		#still needs coding to convert from xy to msp.
		#if file_extension.lower() == ".msp":
		
		spectrum_name = os.path.splitext(spectrum_file)[0]

		if not os.path.exists(os.path.join(nist_dir,"AUTOIMP.MSD")):
			if not os.path.isdir("C:/SEARCH/"):
				os.makedirs("C:/SEARCH/")
			with open(os.path.join(nist_dir,"AUTOIMP.MSD"),"w") as f:
				f.write("C:/SEARCH/SEARCH.MSD")
			
		locator_path = open(os.path.join(nist_dir,"AUTOIMP.MSD"),"r").read()
		
		if platform.system() == "Linux":
			import getpass
			with open(os.path.join(nist_dir,"AUTOIMP.MSD"),"w") as f:
				f.write("C:/SEARCH/SEARCH.MSD")
			locator_path = "/home/{}/.wine/drive_c/SEARCH/SEARCH.MSD".format(getpass.getuser())
		
		while locator_path[0]==' ':
			locator_path = locator_path[1:]

		if not os.path.exists(parent_path(locator_path)):
			os.makedirs(parent_path(locator_path))
		
		shutil.copyfile(spectrum,os.path.join(parent_path(locator_path),spectrum_file))
		
		with open(locator_path,"w") as f:
			f.write(os.path.join(parent_path(locator_path),spectrum_file))
		
		if os.path.exists(os.path.join(nist_dir,"SRCREADY.TXT")):
			os.unlink(os.path.join(nist_dir,"SRCREADY.TXT"))
		if os.path.exists(os.path.join(nist_dir,"SRCRESLT.TXT")):
			os.unlink(os.path.join(nist_dir,"SRCRESLT.TXT"))
		
		if platform.system() == "Linux":
			Popen(["wine",os.path.join(nist_dir,"nistms$.exe"), "/par=2"],stdout=PIPE, stderr=PIPE)
		else:
			Popen([os.path.join(nist_dir,"nistms$.exe"), "/par=2"],stdout=PIPE, stderr=PIPE)
		
#		while not os.path.exists(os.path.join(nist_dir,"SRCRESLT.TXT")):
#			time.sleep(0.1)
#			attempts += 1
#			if attempts > 100:
#				close_nist()
#				#if platform.system() == "Linux":
#				#	Popen(["wine","Taskkill", "/IM", "nistms.exe", "/F"],stdout=PIPE, stderr=STDOUT)
#				#else:
#				#	Popen(["Taskkill", "/IM", "nistms.exe", "/F"],stdout=PIPE, stderr=STDOUT)
#				
#				#raise nistError

		time.sleep(2 + (0.2*search_len))
		
		#sys.stdout.write("\033[F") #back to previous line
		#sys.stdout.write("\r\033[K") #clear line	from https://www.quora.com/How-can-I-delete-the-last-printed-line-in-Python-language
		print("\r\033[K", end=''), #clear line	from https://www.quora.com/How-can-I-delete-the-last-printed-line-in-Python-language
		while not os.path.isfile(os.path.join(nist_dir,"SRCREADY.TXT")):
			#print(attempts)
			time.sleep(0.2)
			#sys.stdout.write("\rWaiting for SRCREADY.TXT. Attempt {}".format(attempts))
			print("\rWaiting for SRCREADY.TXT. Attempt {}\r".format(attempts),end='')
			attempts +=1
			if attempts > 300:
				print("\rclosing nist line {}\r".format(sys._getframe().f_lineno),end='')
				close_nist()
				search_results = ''
				continue
		
		searches_done = 0
		while searches_done != str(search_len):
			ready_file = open(os.path.join(nist_dir,"SRCREADY.TXT"))
			searches_done = ready_file.readlines()[0].rstrip("\r\n").replace("\n","").replace("\r","")
			#print(searches_done)
			ready_file.close()
			#sys.stdout.write("\rWaiting for searches to finish. Currently {}/{} done. Attempt {}".format(int(searches_done),int(search_len),int(attempts)))
			print("\r\rWaiting for searches to finish. Currently {}/{} done. Attempt {}\r".format(int(searches_done),int(search_len),int(attempts)), end=''),
			time.sleep(0.5)
			attempts +=1
			if attempts > 300:
				print("\rclosing nist line {}\r".format(sys._getframe().f_lineno),end='')
				close_nist()
				continue
			
		while not os.path.exists(os.path.join(nist_dir,"SRCRESLT.TXT")):
			time.sleep(0.2)
			print("\rWaiting for SRCRESLT.TXT, Attempt {}\r".format(attempts),end='')
			attempts +=1
			if attempts > 300:
				print("\rclosing nist line {}\r".format(sys._getframe().f_lineno),end='')
				close_nist()
				continue
		
		#search_results = open(os.path.join(nist_dir,"SRCRESLT.TXT"),"rt",encoding="latin-1").read() #
		search_results = io.open(os.path.join(nist_dir,"SRCRESLT.TXT"),"rt",encoding="latin-1").read() #
		
		try:
			os.unlink(os.path.join(nist_dir,"SRCRESLT.TXT"))
			os.unlink(os.path.join(nist_dir,"SRCREADY.TXT"))
		except:
			pass
			
		if len(search_results) == 0:
			print("\rclosing nist line {}\r".format(sys._getframe().f_lineno),end='')
			close_nist()
			time.sleep(0.5)
		else:
			time.sleep(0.5)
			break
			
	time.sleep(0.5)
	
	#try:
	#	os.unlink(os.path.join(nist_dir,"SRCRESLT.TXT"))
	#except:
	#	time.sleep(2)
	#	os.unlink(os.path.join(nist_dir,"SRCRESLT.TXT"))
		
	return search_results 

def nist_cleanup(nist_path):
	import platform
	
	for filename in os.listdir(nist_path):
		if os.path.splitext(filename)[-1].upper() == ".HLM":
			os.unlink(os.path.join(nist_path,filename))
		
	locator_path = open(os.path.join(nist_path,"AUTOIMP.MSD"),"r").read()
	
	if platform.system() == "Linux":
		import getpass
		locator_path = "/home/{}/.wine/drive_c/SEARCH/SEARCH.MSD".format(getpass.getuser())
	
	while locator_path[0]==' ':
		locator_path = locator_path[1:]
	locator_path = parent_path(locator_path)
	
	for filename in os.listdir(locator_path):
		for prefix in prefixList:
			if prefix in filename:
				os.unlink(os.path.join(os.path.abspath(locator_path),filename))

if __name__ == '__main__':
	import sys
	sys.exit(1)
