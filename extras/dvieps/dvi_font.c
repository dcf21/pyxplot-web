// dvi_read.c
//
// The code in this file is part of PyXPlot
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

// Functions for manupulating dvi files -- font section

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "dvi_read.h"
#include "dvi_font.h"
#include "dvi_lib.h"
#include <kpathsea/kpathsea.h>

void dviGetTFM(dviFontDetails *font) {
   char *TFMpath;
   char *s;
   // Prod kpathsea
   kpse_set_program_name("pyxplot8", NULL);
   // kpse_init_prog();
   s = (char *)mallocx((strlen(font->name)+5)*sizeof(char));
   sprintf(s, "%s.tfm", font->name);
   TFMpath = (char *)kpse_find_tfm(s);
   printf("Font file %s: TFM path: %s\n", font->name, TFMpath);
   return;
}
