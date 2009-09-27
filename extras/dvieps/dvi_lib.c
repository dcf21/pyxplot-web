// dvi_lib.h
//
// The code in this file is not really part of PyXPlot
// <http://www.pyxplot.org.uk>
//
// Copyright (C) 2006-8 Dominic Ford <coders@pyxplot.org.uk>
//               2008   Ross Church
//
// $Id: $
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

// functions used within the dvi module

#include <stdlib.h>
#include "dvi_read.h"

void *mallocx(size_t size) {
   void *p;
   p = malloc(size);
   if (p==NULL)
      dvi_fatal("mallocx", 1, "malloc failed!");
   return p;
}


