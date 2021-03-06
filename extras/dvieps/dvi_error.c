// dvi_error.c
//
// The code in this file is part of PyXPlot
// <http://www.pyxplot.org.uk>
//
// Copyright (C) 2006-8 Dominic Ford <coders@pyxplot.org.uk>
//               2008   Ross Church
//
// $Id$
//
// PyXPlot is free software; you can redistribute it and/or modify it under the
// terms of the GNU General Public License as published by the Free Software
// Foundation; either version 2 of the License, or (at your option) any later
// version.
//
// You should have received a copy of the GNU General Public License along with
// PyXPlot; if not, write to the Free Software Foundation, Inc., 51 Franklin
// Street, Fifth Floor, Boston, MA  02110-1301, USA

// ----------------------------------------------------------------------------

// Simple error-handling functions for the ppl dvi code
//
#include <stdio.h>
#include <stdlib.h>

#include "dvi_read.h"

#define DVI_ERROR_STRLEN 2048
char dviErrorMessage[DVI_ERROR_STRLEN];

// Deal with non-fatal errors
void dvi_error(char *error) {
   snprintf(dviErrorMessage, DVI_ERROR_STRLEN, "%s\n", error);
   return;
   // fprintf(stderr, "dvi: ERROR: %s\n", error);
}

// Deal with fatal errors
void dvi_fatal(char *func, int returnCode, char *error) {
   fprintf(stderr, "dvi: FATAL: %s: %s\n", func, error);
   exit(returnCode);
}
