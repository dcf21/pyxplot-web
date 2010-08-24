# YBSC_process.py
#
# The PyXPlot code in this file is part of an astrolabe
#
# Copyright (C) 2010 Dominic Ford <dcf21@mrao.cam.ac.uk>
#
# $Id$
#
# PyXPlot is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# You should have received a copy of the GNU General Public License along with
# PyXPlot; if not, write to the Free Software Foundation, Inc., 51 Franklin
# Street, Fifth Floor, Boston, MA  02110-1301, USA

# ----------------------------------------------------------------------------

# Takes the Yale Bright Star Catalogue, and adds names of objects

import os
import gzip
import re

AU = 1.49598e11 # metres
LYR= 9.4605284e15 # lightyear in metres
pi = 3.14159

stars = {}

GreekAlphabet = {'Alp':r'\alpha' , 'Bet':r'\beta' , 'Gam':r'\gamma' , 'Del':r'\delta' , 'Eps':r'\epsilon' , 'Zet':r'\zeta' , 'Eta':r'\eta' , 'The':r'\theta' , 'Iot':r'\iota' , 'Kap':r'\kappa' , 'Lam':r'\lambda' , 'Mu':r'\mu' , 'Nu':r'\nu' , 'Xi':r'\xi' , 'Omi':'O' , 'Pi':r'\pi' , 'Rho':r'\rho' , 'Sig':r'\sigma' , 'Tau':r'\tau' , 'Ups':r'\upsilon' , 'Phi':r'\phi' , 'Chi':r'\chi' , 'Psi':r'\psi' , 'Ome':r'\omega'}

StarNames = {}
for line in open("RawData/bright_star_names.dat"):
 if len(line)<5: continue
 if (line[0]=='#'): continue
 bs = int(line[0:4])
 name = line[5:]
 StarNames[bs]=re.sub(' ','_',name.strip())

bs = 0
for line in open("RawData/YBSC.dat"):
 if len(line)<100: continue
 bs = bs + 1 # Bright Star Number
 try:
  hd     = int(line[25:31])
  ra_hrs = float(line[75:77])
  ra_min = float(line[77:79])
  ra_sec = float(line[79:82])
  dec_neg= (line[83]=='-')
  dec_deg= float(line[84:86])
  dec_min= float(line[86:88])
  dec_sec= float(line[88:90])
  mag    = float(line[102:107])
 except ValueError: continue
 StarNo = -1
 try:
  StarNo=int(line[4:7])
 except ValueError: pass

 Name1 = Name2 = Name3 = Name4 = "-"
 greek = line[7:10].strip()
 const = line[11:14].strip()
 num   = line[10]
 if greek in GreekAlphabet:
  GreekLetter = GreekAlphabet[greek]
  if num in '123456789': GreekLetter+="^%s"%num
  Name1 = r'$%s$'%GreekLetter
  Name2 = r'$%s$-%s'%(GreekLetter,const)
 if StarNo>0:
  Name4 = r'$%s$-%s'%(StarNo,const)

 if bs in StarNames: Name3 = StarNames[bs]

 RA = (ra_hrs + ra_min /60 + ra_sec /3600)/24*360
 DEC= (dec_deg+ dec_min/60 + dec_sec/3600)
 if dec_neg: DEC=-DEC

 stars[hd] = [RA, DEC, mag , Name1, Name2, Name3, Name4]

keys = stars.keys()
keys.sort()

os.system("mkdir -p ProcessedData")
output = open("ProcessedData/bright_stars.out","w")
for k in keys:
 item = stars[k]
 if item[3] == None: continue
 output.write("%6d %17.12f %17.12f %17.12f %s %s %s %s\n"%tuple([k] + item))
output.close()

