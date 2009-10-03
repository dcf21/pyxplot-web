// dvi_font.c
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

int dviGetTFM(dviFontDetails *font) {
   char *TFMpath, *PFApath, *PFBpath;
   char *s;
   char errStr[SHORT_STRLEN];
   int err;
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
   // XXX Exercise for the reader: implement the ability of dviReadTFM to return errors
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
      if (PFBpath == NULL) {
         snprintf(errStr, SHORT_STRLEN, "dviGetTfm: Cannot find pfa or pfb file for font %s", font->name);
         dvi_error(errStr);
         return DVIE_NOFONT;
      }
      fpin = fopen(PFBpath, "r");
      if (fpin==NULL) {
         snprintf(errStr, SHORT_STRLEN, "dviGetTfm: Cannot open pfb file %s", PFBpath);
         dvi_error(errStr);
         return DVIE_ACCESS;
      }
      
      // Make a filename for the destination pfa file
      //free(PFApath);
      PFApath = (char *)mallocx(SHORT_STRLEN*sizeof(char));
      snprintf(PFApath, SHORT_STRLEN, "%s%s.pfa", TEMPDIR, font->name);
      fpout = fopen(PFApath, "w");
      if (fpout == NULL) {
         snprintf(errStr, SHORT_STRLEN, "dviGetTfm: Cannot write to pfa file %s", PFApath);
         dvi_error(errStr);
         return DVIE_ACCESS;
      }
      if ((err=pfb2pfa(fpin, fpout))!=0)
         return err;
      fclose(fpin);
      fclose(fpout);
      font->pfaPath = PFApath;
   }

   // Obtain the font name from the PFA file
   font->psName = psNameFromPFA(PFApath);
   return DVIE_SUCCESS;
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


// TFM-related routines
dviTFM *dviReadTFM(FILE *fp) {
   dviTFM *tfm;
   unsigned long int buff[12];
   int i;
   int lh;
   int Nchars;

   char *tit[12] = {"lf", "lh", "bc", "ec", "nw", "nh", "nd", "ni", "nl", "nk", "ne", "np"};

   tfm = (dviTFM *)mallocx(sizeof(dviTFM));

   // Read the file header
   for (i=0; i<12; i++) {
      ReadLongInt(fp, buff+i, 2);
   }
   tfm->lf = buff[0];
   tfm->lh = buff[1];
   tfm->bc = buff[2];
   tfm->ec = buff[3];
   tfm->nw = buff[4];
   tfm->nh = buff[5];
   tfm->nd = buff[6];
   tfm->ni = buff[7];
   tfm->nl = buff[8];
   tfm->nk = buff[9];
   tfm->ne = buff[10];
   tfm->np = buff[11];
   // XXX Debugging output
   printf("TFM! ");
   for (i=0; i<12; i++) {
      printf("%s:%lu  ", tit[i], buff[i]);
   }
   printf("\n");
   
   // We should have lf=6+lh+(ec-bc+1)+nw+nh+nd+ni+nl+nk+ne+np
   if (tfm->lf != 6 + tfm->lh + tfm->ec - tfm->bc + 1 + tfm->nw + tfm->nh + tfm->nd + tfm->ni + tfm->nl + tfm->nk + tfm->ne + tfm->np) {
      dvi_fatal("ReadTFM", -1, "TFM fail");
   }

   // Read the header (distinct from the file header...)
   lh = tfm->lh;
   ReadLongInt(fp, buff, 4); tfm->checksum = buff[0]; 
   lh--;
   tfm->ds = ReadFixWord(fp);
   lh--;
   printf("TFM: lh now %d\n", lh);
   if (lh>10) {
      int len;
      ReadUChar(fp, &len);
      printf("TFM: Coding length: %d\n", len);
      if (len>39) {
         dvi_error("Malformed DVI header!  coding len>40!");
         len=39;
      }
      for (i=0; i<39; i++) {
         int t;
         ReadUChar(fp,&t); tfm->coding[i] = t;
      }
      tfm->coding[len] = '\0';
      lh-=10;
   }
   if (lh>5) {
      int len;
      ReadUChar(fp, &len);
      if (len>19) {
         dvi_error("Malformed DVI header!  coding len>19!");
         len=19;
      }
      for (i=0; i<19; i++) {
         int t;
         ReadUChar(fp,&t); tfm->family[i] = t;
      }
      tfm->family[len] = '\0';
      lh-=5;
   }
   printf("TFM: coding:%s: family:%s: lh now %d\n", tfm->coding, tfm->family, lh);
   if (lh>0) {
      int temp;
      ReadUChar(fp, &temp);
      ReadUChar(fp, &temp);
      tfm->face = temp;
      ReadUChar(fp, &temp);
      ReadUChar(fp, &temp);
      lh--;
   }
   while (lh>0) {
      unsigned long int i;
      ReadLongInt(fp, &i, 4);
      lh--;
   }

   // Good, now we've got that over with...
   // Read the char info tables
   Nchars = tfm->ec - tfm->bc + 1;
   tfm->charInfo = (TFMcharInfo *)mallocx(Nchars*sizeof(TFMcharInfo));
   for (i=0; i<Nchars; i++) {
      int j;
      int t[4];
      for (j=0; j<4; j++) {
         ReadUChar(fp, t+j);
      }
      (tfm->charInfo+i)->wi = t[0];
      (tfm->charInfo+i)->hi = t[1]>>4;
      (tfm->charInfo+i)->di = t[1]&0xf;
      (tfm->charInfo+i)->ii = t[2]>>2;
      (tfm->charInfo+i)->tag = t[2]&0x3;
      (tfm->charInfo+i)->rem = t[3];
      /* printf("TFM i=%d t=%d,%d,%d w,h,di=%d,%d,%d\n", i, t[0],t[1],t[2],
                      (tfm->charInfo+i)->wi,
                      (tfm->charInfo+i)->hi,
                      (tfm->charInfo+i)->di); */
   }

   // Read the width, height, depth & italic tables
   tfm->width  = (double *)mallocx(tfm->nw*sizeof(double));
   tfm->height = (double *)mallocx(tfm->nh*sizeof(double));
   tfm->depth  = (double *)mallocx(tfm->nd*sizeof(double));
   tfm->italic = (double *)mallocx(tfm->ni*sizeof(double));
   for (i=0; i<tfm->nw; i++) {
      tfm->width[i] = ReadFixWord(fp);
   }
   for (i=0; i<tfm->nh; i++) {
      tfm->height[i] = ReadFixWord(fp);
   }
   for (i=0; i<tfm->nd; i++) {
      tfm->depth[i] = ReadFixWord(fp);
   }
   for (i=0; i<tfm->ni; i++) {
      tfm->italic[i] = ReadFixWord(fp);
   }

   // Read the lig_kern table
   tfm->ligKern = (TFMligKern *)mallocx(tfm->nl*sizeof(TFMligKern));
   for (i=0; i<tfm->nl; i++) {
      int j;

      ReadUChar(fp, &j);
      (tfm->ligKern+i)->skip_byte = j;
      ReadUChar(fp, &j);
      (tfm->ligKern+i)->next_char = j;
      ReadUChar(fp, &j);
      (tfm->ligKern+i)->op_byte = j;
      ReadUChar(fp, &j);
      (tfm->ligKern+i)->remainder = j;
   }

   // Read the kern table
   tfm->kern = (double *)mallocx(tfm->nk*sizeof(double));
   for (i=0; i<tfm->nk; i++) {
      tfm->kern[i] = ReadFixWord(fp);
   }

   // Read the extensible character recipies
   tfm->extensibleRecipe = (TFMextRec *)mallocx(tfm->ne*sizeof(TFMextRec));
   for (i=0; i<tfm->ne; i++) {
      int j;
      ReadUChar(fp, &j);
      (tfm->extensibleRecipe+i)->top = j;
      ReadUChar(fp, &j);
      (tfm->extensibleRecipe+i)->mid = j;
      ReadUChar(fp, &j);
      (tfm->extensibleRecipe+i)->bot = j;
      ReadUChar(fp, &j);
      (tfm->extensibleRecipe+i)->rep = j;
   }

   // We should read in the param aray at this point, but let's see if 
   // we can get away without doing, eh?

   return tfm;
}

// Read a TFM "fix_word", a signed four-byte int with the dp after 12 bits
// Note the lack of error handling!
double ReadFixWord(FILE *fp) {
   double fw;
   long signed int li;
   const double twoP20 = 1048576; // 2**20
   ReadSignedInt(fp, &li, 4);
   fw = (double) li / twoP20;
   return fw;
}
