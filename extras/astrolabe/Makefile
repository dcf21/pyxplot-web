# Makefile
#
# This Makefile makes the various parts of a model astrolabe as described by
# Dominic Ford's paper in the Journal of the British Astronomical Association
# (2011).
#
# Copyright (C) 2010 Dominic Ford <dcf21@mrao.cam.ac.uk>
#
# $Id: astrolabe.ppl 938 2010-08-29 00:35:38Z dcf21 $
#
# This code is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# You should have received a copy of the GNU General Public License along with
# PyXPlot; if not, write to the Free Software Foundation, Inc., 51 Franklin
# Street, Fifth Floor, Boston, MA  02110-1301, USA

# ----------------------------------------------------------------------------

all:
	pyxplot astrolabe.ppl
	cd doc ; pdflatex astrolabe.tex ; pdflatex astrolabe.tex

clean:
	rm -Rf astrolabes ProcessedData
	rm -Rf doc/*.aux doc/*.dvi doc/*.log doc/*.pdf doc/*.ps
