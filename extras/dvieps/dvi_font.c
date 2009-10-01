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
#define TEMPDIR "/tmp/"

int pfb2pfa(FILE *in, FILE *out);
char *psNameFromPFA(char *PFApath);

void dviGetTFM(dviFontDetails *font) {
   char *TFMpath, *PFApath, *PFBpath;
   char *s;
   FILE *TFMfp;
	FILE *fpin, *fpout;

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
	
   // Additionally obtain the pfa file
   s = (char *)mallocx((strlen(font->name)+5)*sizeof(char));
   sprintf(s, "%s.pfa", font->name);
   PFApath = (char *)kpse_find_file(s, kpse_type1_format, true);
   if (PFApath != NULL) {
      font->pfaPath = PFApath;
   } else {
      // Make a PFA file from the PFB file (assuming that one exists)
      sprintf(s, "%s.pfb", font->name);
      PFBpath = (char *)kpse_find_file(s, kpse_type1_format, true);
      if (PFBpath == NULL)
         dvi_fatal("dviGetTfm", -1, "Cannot find pfa or pfb file for font!");
      fpin = fopen(PFBpath, "r");
      if (fpin==NULL) 
         dvi_fatal("dviGetTfm", -1, "Cannot open pfb file!");
      
      // Make a filename for the destination pfa file
      //free(PFApath);
      PFApath = (char *)mallocx(SHORT_STRLEN*sizeof(char));
      snprintf(PFApath, SHORT_STRLEN, "%s%s.pfa", TEMPDIR, font->name);
      fpout = fopen(PFApath, "w");
      if (fpout == NULL)
         dvi_fatal("dviGetTfm", -1, "Cannot write to pfa file!");
      if (pfb2pfa(fpin, fpout)!=0)
         dvi_error("Error from pfa2pfb!");
      fclose(fpin);
      fclose(fpout);
      font->pfaPath = PFApath;
   }

   // Obtain the font name from the PFA file
   font->psName = psNameFromPFA(PFApath);
   return;
}

// Extract the font name from a PFA file
// XXX This is an entirely empirical algorithm and may not be general!
// If the font name is longer than SHORT_STRLEN this will fail (safely)...
char *psNameFromPFA(char *PFApath) {
   FILE *fp;
   char *s;
   char buf[SHORT_STRLEN], c;
   int i;

   if ((fp = fopen(PFApath, "r"))==NULL)
      dvi_fatal("psNameFromPFA", -1, "Cannot open pfa file");
   // Forward file to the first space
   c = '\0';
   while (c!=' ') {
      c = getc(fp);
   }
   // Grab characters until the next space
   i=0;
   while ((c=getc(fp))!=' ' && i<SHORT_STRLEN-1) {
      buf[i] = c;
      i++;
   }
   buf[i] = '\0';
   // Produce a malloced string with the name in and return it
   s = (char *)mallocx((i+1)*sizeof(char));
   snprintf(s, i+1, "%s", buf);
   return s;
}

// Convert pfb file to pfa file
int pfb2pfa(FILE *in, FILE *out) {
   int i, j;    // Loop variables
   int len;     // Record length
   char c;      // Input string

	while(!feof(in)) {
		if (getc(in) != 128)
			dvi_fatal("pfb2pfa", -1, "Error in pfb file format!");
		i = getc(in);
      if (i==1) {
         // Ascii text record
         len = getc(in) | getc(in)<<8 | getc(in)<<16 | getc(in)<<24;
         for (j=0; j<len ; j++) {
            if ((c=getc(in)) == '\r') {
               putc('\n', out);
            } else {
               putc(c, out);
            }
         }

      } else if (i==2) {
         // Binary data record
         len = getc(in) | getc(in)<<8 | getc(in)<<16 | getc(in)<<24;
         for(j=0; j<len; j++) {
            fprintf(out, "%02x", getc(in));
            if ((j+1) % 30 == 0) putc('\n', out);
         }
         putc('\n', out);

      } else if (i==3) {
         // EOF
         break;

      } else {
         dvi_fatal("pfb2pfa", -1, "Corrupt pfb file!");
      }
   }
   return 0;
}

