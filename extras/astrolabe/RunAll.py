#!/usr/bin/python
# RunAll.py
# $Id$

import os
os.system("rm -Rf RunAllOut")
os.system("mkdir -p RunAllOut")

for lat in range(25,90,5):
  os.putenv("LATITUDE","%d"%lat)
  os.system("make clean")
  os.system("make -j 2 all")
  os.system("mv astrolabe2.pdf RunAllOut/astrolabe_full_%02d.pdf"%lat)
  os.system("mv astrolabe.pdf  RunAllOut/astrolabe_simp_%02d.pdf"%lat)
  os.system("make clean")

