// dvi_read.c
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

// Functions for manupulating dvi files

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "dvi_read.h"
#include "dvi_lib.h"
#include "dvi_font.h"

int DisplayDVIOperator(DVIOperator *op);
int GetDVIOperator(DVIOperator *op, FILE *fp);

void outputPostscript(FILE *fp, dviInterpreterState *interp);

// The following is useful for output sometimes
const char *dviops[58] = {
   "set1", "set2", "set3", "set4",
   "setrule", 
   "put1", "put2", "put3", "put4",
   "putrule",
   "nop", "bop", "eop",
   "push", "pop",
   "right1", "right2", "right3", "right4",
   "w0", "w1", "w2", "w3", "w4",
   "x0", "x1", "x2", "x3", "x4",
   "down1", "down2", "down3", "down4",
   "y0", "y1", "y2", "y3", "y4",
   "z0", "z1", "z2", "z3", "z4", // Big hole in the labels here...
   "fnt1", "fnt2", "fnt3", "fnt4",
   "special1", "special2", "special3", "special4",
   "fntdef1", "fntdef2", "fntdef3", "fntdef4",
   "pre", "post", "postpost"};

int ReadDviFile(char *filename) {
   FILE *fp;
   DVIOperator op;
   int i;
   dviInterpreterState *interpreter;
   int POST=0;
   int err;

   op.s[0] = NULL;
   op.s[1] = NULL;

   // Set up the interpreter
   interpreter = dviNewInterpreter();

   fp = fopen(filename, "r");
   if (fp==NULL)
      dvi_fatal("dvi_read", 1, "dvi file does not exist!");

   // This is the main loop for the dvi parser
   while (!feof(fp)) {
		// Read the next operator from the dvi file
      if ((err=GetDVIOperator(&op, fp))!=0) {
         if (err > DVIE_WARNING) {
            return err;
         } else {
            continue;
         }
      }
      DisplayDVIOperator(&op);
      // A slightly more sophisticated interpreter that makes some postscript
      if (!POST) {
         err = dviInterpretOperator(interpreter, &op);
         if (err > DVIE_WARNING) 
            return err;
      }
      for (i=0; i<2; i++) {
         if (op.s[i]!=NULL) {
            free(op.s[i]);
            op.s[i] = NULL;
         }
      }
      // If we've hit the post then we can break out
      if (op.op==DVI_POST) {
         POST = 1;
         break;
      }
   }

   fclose(fp);

   fp = fopen("output.ps", "w");
   outputPostscript(fp, interpreter);
   fclose(fp);

   dviDeleteInterpreter(interpreter);

   return 0;
}

// Read in a DVI Operator and any additional data that it comes with   
// A useful reference for the meaning and size of the additional data is
// http://www-users.math.umd.edu/~asnowden/comp-cont/dvi.html
int GetDVIOperator(DVIOperator *op, FILE *fp) {
   int i, v, err;

   // First read in the opcode
   if ((err=ReadUChar(fp,&v))!=0) {
      dvi_error("Error reading operator from disc!");
      return err;
   }
   op->op = v;

   // Now work out what it represents and get any extra data if needed
   if (v < DVI_CHARMIN) {
      dvi_error("Illegal opcode whilst parsing DVI file!");
      return -1;

   } else if (v >= DVI_CHARMIN && v <= DVI_CHARMAX) {
      return 0;

   } else if (v < DVI_SET1234+4) {
      int Ndata;
      Ndata = v - DVI_SET1234 + 1;
      if ((err=ReadLongInt(fp, op->ul, Ndata))!=0)
         return err;
      // Set to DVI_SET1234 for convenience later (we don't need to know whether it's 1, 2, 3 or 4)
      // op->op = DVI_SET1234;
      return 0;

   } else if (v == DVI_SETRULE) {
      if ((err = ReadSignedInt(fp, op->sl, 4))!=0)
         return 0;
      if ((err = ReadSignedInt(fp, op->sl+1, 4))!=0)
         return 0;
      return 0;

   } else if (v < DVI_PUT1234+4) {
      int Ndata;
      Ndata = v - DVI_PUT1234 + 1;
      if ((err=ReadLongInt(fp, op->ul, Ndata))!=0)
         return err;
      return 0;

   } else if (v == DVI_PUTRULE) {
      if ((err = ReadSignedInt(fp, op->sl, 4))!=0)
         return 0;
      if ((err = ReadSignedInt(fp, op->sl+1, 4))!=0)
         return 0;
      return 0;

   } else if (v == DVI_NOP) {
      return 0;

   } else if (v == DVI_BOP) {
      for (i=0; i<10; i++) {
         if ((err = ReadLongInt(fp, op->ul+i, 4))!=0)
            return 0;
      }
      if ((err= ReadSignedInt(fp, op->sl, 4))!=0)
         return 0;
      return 0;

   } else if (v >= DVI_EOP && v <= DVI_POP) {
      return 0;

   } else if (v < DVI_RIGHT1234 + 4) {
      int Ndata;
      Ndata = v - DVI_RIGHT1234 + 1;
      if ((err=ReadSignedInt(fp, op->sl, Ndata))!=0)
         return err;
      // Set to DVI_RIGHT1234 for convenience later (we don't need to know whether it's 1, 2, 3 or 4)
      // op->op = DVI_RIGHT1234;
      return 0;

   } else if (v == DVI_W0) {
      return 0;

   } else if (v < DVI_W1234 + 4) {
      int Ndata;
      Ndata = v - DVI_W1234 + 1;
      if ((err=ReadSignedInt(fp, op->sl, Ndata))!=0)
         return err;
      return 0;

   } else if (v == DVI_X0) {
      return 0;

   } else if (v < DVI_X1234 + 4) {
      int Ndata;
      Ndata = v - DVI_X1234 + 1;
      if ((err=ReadSignedInt(fp, op->sl, Ndata))!=0)
         return err;
      return 0;

   } else if (v < DVI_DOWN1234 + 4) {
      int Ndata;
      Ndata = v - DVI_DOWN1234 + 1;
      if ((err=ReadSignedInt(fp, op->sl, Ndata))!=0)
         return err;
      return 0;

   } else if (v == DVI_Y0) {
      return 0;

   } else if (v < DVI_Y1234 + 4) {
      int Ndata;
      Ndata = v - DVI_Y1234 + 1;
      if ((err=ReadSignedInt(fp, op->sl, Ndata))!=0)
         return err;
      return 0;

   } else if (v == DVI_Z0) {
      return 0;

   } else if (v < DVI_Z1234 + 4) {
      int Ndata;
      Ndata = v - DVI_Z1234 + 1;
      if ((err=ReadSignedInt(fp, op->sl, Ndata))!=0)
         return err;
      return 0;

   } else if (v >= DVI_FNTNUMMIN && v <= DVI_FNTNUMMAX) {
      return 0;

   } else if (v <= DVI_FNT1234) {
      int Ndata;
      Ndata = v - DVI_FNT1234 + 1;
      if ((err=ReadLongInt(fp, op->ul, Ndata))!=0)
         return err;
      return 0;

   } else if (v <= DVI_SPECIAL1234) {
      int Ndata;
      Ndata = v - DVI_SPECIAL1234 + 1;
      if ((err=ReadLongInt(fp, op->ul, Ndata))!=0)
         return err;
      return 0;

   } else if (v <= DVI_FNTDEF1234) {
      int i, Ndata;
      Ndata = v - DVI_FNTDEF1234 + 1;
      if ((err=ReadLongInt(fp, op->ul, Ndata))!=0)
         return err;
      for (i=1; i<4; i++) {
         if ((err=ReadLongInt(fp, op->ul+i, 4))!=0)
            return err;
      }
      for (i=4; i<6; i++) {
         if ((err=ReadLongInt(fp, op->ul+i, 1))!=0)
            return err;
      }
      Ndata = op->ul[4] + op->ul[5];
      op->s[0] = (char *)mallocx((Ndata+1)*sizeof(char));
      op->s[0][Ndata] = '\0';
      for (i=0; i<Ndata; i++) {
         int j;
         if ((err=ReadUChar(fp, &j))!=0)
            return err;
         op->s[0][i] = (char) j;
      }


      return 0;

   } else if (v == DVI_PRE) {
      int i, v1;
      if ((err=ReadUChar(fp, &v1))!=0)
         return err;
      op->ul[0] = v1;
      for (i=1; i<4; i++) {
         if ((err=ReadLongInt(fp, op->ul+i, 4))!=0)
            return err;
      }
      if ((err=ReadUChar(fp,&v1))!=0)
         return err;
      // Throw away the DVI comment
      for (i=v1; i>0; i--) {
         if ((err=ReadUChar(fp,&v1))!=0)
            return err;
      }
      return 0;
   
   } else if (v == DVI_POST) {
      for (i=0; i<6; i++) {
         if ((err=ReadLongInt(fp, op->ul+i,4))!=0)
            return err;
      }
      for (i=6; i<8; i++) {
         if ((err=ReadLongInt(fp, op->ul+i,2))!=0)
            return err;
      }
      return 0;

   } else if (v == DVI_POSTPOST) {
      int v1;
      if ((err=ReadLongInt(fp, op->ul,4))!=0)
         return err;
      if ((err=ReadUChar(fp,&v1))!=0)
         return err;
      op->ul[1] = v1;
      // Mop up all the 223s
      /* while (!feof(fp)) {
         if ((err=ReadUChar(fp,&v1))!=0)
            return err;
         if (v1 != 223)
            return v1;
      } */
      return 0;
   } else {
      dvi_error("Unidentified opcode in dvi file!");
      return -1;
   }

   // Once we've got an operator we return, so we should never get here
   dvi_fatal("dvi_read.c", 252, "GetDVIOperator: you are not reading this error message!");
   return -1;
}


// Read an unsigned char from a dvi file
int ReadUChar (FILE *fp, int *uc) {
   int i;
   i = getc(fp);
   if (i==EOF) {
      dvi_fatal("Unexpected EOF in dvi file!", -1, "ReadUChar");
      return -1;
   }
   *uc = i;
   return 0;
}

// Read a long int from a dvi file (using the DVI long int format)
int ReadLongInt (FILE *fp, unsigned long int *uli, int n) {
   int err,v,i;
   unsigned long int fv;
   if ((err=ReadUChar(fp, &v))!=0)
      return err;
   fv = v;
   for (i=0; i<n-1; i++) {
      if ((err=ReadUChar(fp, &v))!=0)
         return err;
      fv = (fv<<8) |  v;
   }
   *uli = fv;
   return 0;
}

// Read a signed int from a dvi file
int ReadSignedInt (FILE *fp, signed long int *sli, int n) {
   int err, v, i;
   signed long int fv;
   if ((err=ReadUChar(fp, &v))!=0)
      return err;
   fv = v<128?v:v-256;
   for (i=0; i<n-1; i++) {
      if ((err=ReadUChar(fp, &v))!=0)
         return err;
      fv = (fv<<8) |  v;
   }
   *sli = fv;
   return 0;
}

// Provide a display of a dvi operator (for debugging purposes)
int DisplayDVIOperator(DVIOperator *op) {
   char *s, s2[128];
   s = NULL;
   if (op->op <= DVI_CHARMAX) {
      int i;
      i=op->op;
      if (i>=31 && i<=126) {
         snprintf(s2, 128, "Character %d %s", i, (char *)&i);
      } else {
         snprintf(s2, 128, "Character %d", i);
      }
      s = s2;

      // Special cases
   } else if (op->op == DVI_PRE) {
      snprintf(s2, 128, "%s %lu %lu %lu %lu", "pre", *(op->ul), *(op->ul+1), *(op->ul+2), *(op->ul+3));
      s=s2;
   } else if (op->op == DVI_FNTDEF1234) {
      snprintf(s2, 128, "%s N=%lu d=%lu n=%s", "fnt def", *(op->ul), *(op->ul+4), (op->s[0]));
      s=s2;

   } else if (op->op < DVI_FNTNUMMIN) {
      s = (char *)dviops[op->op-DVI_CHARMAX-1];
      if (strlen(s)==2 && (char)s[1]>'0') {
         snprintf(s2, 128, "%s %lu", dviops[op->op-DVI_CHARMAX-1], *(op->ul));
         s=s2;
      }
   } else if (op->op <= DVI_FNTNUMMAX) {
      snprintf(s2, 128, "Font number %d", op->op-DVI_FNTNUMMIN);
      s = s2;
   } else if (op->op <= DVI_POSTPOST) {
      int i;
      i = op->op-DVI_CHARMAX-1-(DVI_FNTNUMMAX-DVI_FNTNUMMIN+1);
      s = (char *)dviops[i];
   } else {
      snprintf(s2, 128, "ERROR!!!");
      s=s2;
   }
   if (DVI_DEBUG) printf("%s\n", s);
   return 0;
}


// This is a test routine that turns the output of parsing the dvi file
// into a multi-page (if appropriate) ps file (so emulates dvips) for testing
// purposes.
void outputPostscript(FILE *fp, dviInterpreterState *interp) {
   dlListItem *page = interp->output->pages;
   dlListItem *text;
   dlListItem *font;
   char *pfaFile;
   FILE *fp2;
   int i=0;
   int c;
   double *bb;

   fprintf(fp, "%%!PS-Adobe-2.0\n");
   fprintf(fp, "%%%%Title: pp output\n");
   fprintf(fp, "%%%%Pages: %d\n", interp->output->Npages);
   fprintf(fp, "%%%%DocumentFonts: ");
   font = interp->fonts;
   while (font != NULL) {
      fprintf(fp, "%s ", ((dviFontDetails *)(font->p))->psName);
      font = font->nxt;
   }
   fprintf(fp, "\n");
   fprintf(fp, "%%%%EndComments\n");
   fprintf(fp, "\n");
   // Include the fonts
   font = interp->fonts;
   while (font != NULL) {
      pfaFile = ((dviFontDetails *)font->p)->pfaPath;
      fp2 = fopen(pfaFile, "r");
      if (fp2==NULL) {
         fprintf(stderr, "OutputPostscript: Failed to open file %s\n", pfaFile);
         exit(1);
      }
      while ((c=getc(fp2))!=EOF) {
         putc(c, fp);
      }
      fclose(fp2);
      font = font->nxt;
   }


   while (page != NULL) {
      ++i;
      fprintf(fp, "%%%%Page: %d %d\n", i, i);
      // Paint on the bounding box
      bb = ((postscriptPage *)(page->p))->boundingBox;
      fprintf(fp, "gsave\n");
      fprintf(fp, "%f %f moveto\n", bb[0], bb[1]);
      fprintf(fp, "%f %f lineto\n", bb[0], bb[3]);
      fprintf(fp, "%f %f lineto\n", bb[2], bb[3]);
      fprintf(fp, "%f %f lineto closepath stroke\n", bb[2], bb[1]);
      fprintf(fp, "grestore\n");
      text = ((postscriptPage *)(page->p))->text;
      while (text != NULL) {
         fprintf(fp, "%s", (char *)text->p);
         text = text->nxt;
      }
      fprintf(fp, "showpage\n");
      page = page->nxt;
   }
}
