
GV_COMMAND=/usr/bin/gv
GV_OPT=--
MAKE_COMMAND=/usr/bin/make
# MAKEFILE
#
# The code in this file is part of PyXPlot
# <http://www.pyxplot.org.uk>
#
# Copyright (C) 2006-8 Dominic Ford <coders@pyxplot.org.uk>
#               2008   Ross Church
#
# $Id: $
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

# Makefile for ppl_dvips test code
#
# GV_COMMAND=/usr/bin/gv

# Location of final code. Change the value of USRDIR below to install PyXPlot
# to a location other than /usr/local:

USRDIR=/usr/local
BINDIR=${USRDIR}/bin
SRCDIR=${USRDIR}/share/pyxplot
DOCDIR=${USRDIR}/share/doc/pyxplot
MANDIR=${USRDIR}/man/man1

VERSION = 0.8.0
DATE    = 36/15/2012

COMPILE = $(CC) -Wall -c -g 
LINK    = $(CC) -Wall -lm -lreadline -ljpeg -lkpathsea -g 

OPTIMISATION = -O0

DEBUG   = -D DEBUG=1 -D MEMDEBUG=1
NODEBUG = -D DEBUG=0 -D MEMDEBUG=0

SRCDIR  = src
OBJDIR  = obj
BINDIR  = bin


SRC = dvi_read.c ppl_dvips.c dvi_error.c dvi_list.c dvi_lib.c dvi_interpreter.c dvi_font.c
HDR = dvi_read.h dvi_lib.h dvi_list.h dvi_font.h

OBJ = $(SRC:%.c=%.o)

all: ppl_dvips

%.o:         %.c $(HDR)
	$(COMPILE) $(OPTIMISATION) $(DEBUG) $< -o $@

ppl_dvips: $(OBJ) $(HDR)
	$(LINK) $(OPTIMISATION) $(OBJ)         -o ppl_dvips
