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

#define SHORT_STRLEN 2048

void dviGetTFM(dviFontDetails *font) {
   char *TFMpath, *PFXpath;
   char *s;
	char buf[SHORT_STRLEN];
   FILE *TFMfp;
	FILE *fp;
	dlListItem *item;
	int len;

   // Prod kpathsea
   kpse_set_program_name("pyxplot8", NULL);
   // kpse_init_prog();
   // Get the TFM file
   s = (char *)mallocx((strlen(font->name)+5)*sizeof(char));
   sprintf(s, "%s.tfm", font->name);
   TFMpath = (char *)kpse_find_tfm(s);
   printf("Font file %s: TFM path: %s\n", font->name, TFMpath);
   TFMfp = fopen(TFMpath, "r");
   font->tfm = dviReadTFM(TFMfp);
	
   // Additionally obtain the pfa or pfb file
	// Make a list to put it in (first item is needlessly blank)
	item = dlNewList();
	dviFontDetails->pfa = item;
	s = (char *)mallocx(sizeof(char));
	*s = '\0';
	item->p = (void *)s;

   sprintf(s, "%s.pfa", font->name);
   PFXpath = (char *)kpse_find_file(s, kpse_type1_format, true);
   if (PFXpath != NULL) {
		// Download the PFA file
		fp = fopen(PFXpath, "r");
		if (fp==NULL) dvi_fatal("dvi_font.c", "Failed to open PFA file!", -1);
		while (!feof(fp)) {
			file_readline(fp, buf, SHORT_STRLEN);
		   // XXX The next bit of code should be re-written to handle truncated strings properly!
			len = strlen(buf)+1;
			if (len==SHORT_STRLEN)
				dvi_error("Warning!  Possible truncation of dvi file!");
			s = (char *)mallocx(len*sizeof(char));
			snprintf(s, len, "%s", buf);
			item = dlAppendItem(item);
			item->p = (char *)s;
		}
		fclose(fp);
	} else {
		// We can't find a pfa file to grab, so make one from a pfb file if available
		sprintf(s, "%s.pfb", font->name);
		PFXpath = (char *)kpse_find_file(s, kpse_type1_format, true);
		if (PFXpath == NULL) 
			dvi_fatal("dvi_font.c", "Cannot find PFB path corresponding to font!", "-1");
		fp = fopen(PFXpath, "r");
		if (fp==NULL) dvi_fatal("dvi_font.c", "Failed to open PFB file!", -1);
		while (!feof(fp)) {
			// XXX grab the PFB and turn it into a PFA!
	   }
		fclose(fp);
	}
	return;
}
