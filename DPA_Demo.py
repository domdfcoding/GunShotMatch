#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  DPA_Demo.py
#  
#  Copyright 2019 Dominic Davis-Foster <domdf@ryzen>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
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


import sys, os
sys.path.append("..")

from pyms.Experiment.IO import load_expr
from pyms.Peak.List.DPA.Class import PairwiseAlignment
from pyms.Peak.List.DPA.Function import align_with_tree, exprl2alignment

# define the input experiments list
prefixList = [ "ELEY_1_SUBTRACT", "ELEY_2_SUBTRACT", "ELEY_3_SUBTRACT", "ELEY_4_SUBTRACT", "ELEY_5_SUBTRACT"]

# within replicates alignment parameters
Dw = 2.5  # rt modulation [s]
Gw = 0.30 # gap penalty

# do the alignment
print('Aligning')
expr_list = []
expr_dir = "Results/Experiments/"
for expr_code in prefixList:
    file_name = os.path.join(expr_dir, expr_code + ".expr")
    expr = load_expr(file_name)
    expr_list.append(expr)
F1 = exprl2alignment(expr_list)
T1 = PairwiseAlignment(F1, Dw, Gw)
A1 = align_with_tree(T1, min_peaks=2)

A1.write_csv('output/rt.csv', 'output/area.csv')
