#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  timing.py
#  
#  Copyright 2009 PaulMcG <https://stackoverflow.com/users/165216/paulmcg>
#  Licensed under CC-BY-SA
#
#  Adapted 2018 by Dominic Davis-Foster <dominic@davis-foster.co.uk>
#	Changes include:
#		 Removing all print functions except the elapsed time at the end
#		 Using time() in place of clock() to take into account time when python is paused
#
# source: http://stackoverflow.com/a/1557906/6009280

import atexit
#from time import clock
import time
from functools import reduce


def seconds_to_str(t):
    return "%d:%02d:%02d.%03d" % \
           reduce(lambda ll, b: divmod(ll[0], b) + ll[1:],
                  [(t * 1000,), 1000, 60, 60])


line = "=" * 40


def log(s, elapsed=None):
    print(line)
#    print(seconds_to_str(time.time()), '-', s)
    #print(seconds_to_str(clock()), '-', s)
    if elapsed:
        print("Elapsed time:", elapsed)
    print(line)
    print('')


def endlog():
    #end = clock()
    end = time.time()
    elapsed = end - start
    log("End Program", seconds_to_str(elapsed))


def now():
    return seconds_to_str(time.time())
    #return seconds_to_str(clock())


#start = clock()
start = time.time()
atexit.register(endlog)
#log("Start Program")
