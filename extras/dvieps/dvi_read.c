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

// Functions for manupulating dvi files

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "dvi_read.h"
#include "dvi_lib.h"
#include "dvi_font.h"

int ReadUChar (FILE *fp, int *uc);
int ReadLongInt (FILE *fp, unsigned long int *uli, int n);
int ReadSignedInt (FILE *fp, signed long int *sli, int n);
double ReadFixWord(FILE *fp);
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
   int err, i;
   dviInterpreterState *interpreter;

   op.s[0] = NULL;
   op.s[1] = NULL;

   // Set up the interpreter
   interpreter = dviNewInterpreter();

   fp = fopen(filename, "r");
   if (fp==NULL)
      dvi_fatal("dvi_read", 1, "dvi file does not exist!");

   /* Very simple DVI reader; just get each opcode and its attached data */
   while (!feof(fp)) {
      if ((err=GetDVIOperator(&op, fp))!=0) {
         char s[1024];
         snprintf(s, 1024, "Error %d in getting operator!", err);
         dvi_error(s);
         break;
         return err;
      }
      DisplayDVIOperator(&op);
      // A slightly more sophisticated interpreter that makes some postscript
      dviInterpretOperator(interpreter, &op);
      for (i=0; i<2; i++) {
         if (op.s[i]!=NULL) {
            free(op.s[i]);
            op.s[i] = NULL;
         }
      }
      // If we've hit the post post then we can break out
      if (op.op==DVI_POSTPOST)
         break;
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
      if ((err=ReadLongInt(fp, op->ul, Ndata))!=0)
         return err;
      op->sl[0] = op->ul[0];
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
      //printf("XXX 2\n");
   } else if (op->op <= DVI_FNTNUMMAX) {
      snprintf(s2, 128, "Font number %d", op->op-DVI_FNTNUMMIN);
      s = s2;
      //printf("XXX 3\n");
   } else if (op->op <= DVI_POSTPOST) {
      int i;
      i = op->op-DVI_CHARMAX-1-(DVI_FNTNUMMAX-DVI_FNTNUMMIN+1);
      s = (char *)dviops[i];
      //printf("XXX 4 %d %d\n",i, op->op);
   } else {
      snprintf(s2, 128, "ERROR!!!");
      s=s2;
      printf("XXX 5\n");
   }
   printf("%s\n", s);
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
      text = ((postscriptPage *)(page->p))->text;
      while (text != NULL) {
         fprintf(fp, "%s", (char *)text->p);
         text = text->nxt;
      }
      fprintf(fp, "showpage\n");
      page = page->nxt;
   }
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
      (tfm->charInfo+i)->hi = t[1]<<4;
      (tfm->charInfo+i)->di = t[1]&0xf;
      (tfm->charInfo+i)->ii = t[2]<<2;
      (tfm->charInfo+i)->tag = t[2]&0x3;
      (tfm->charInfo+i)->rem = t[3];
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
   const long int twoP20 = 1048576; // 2**20
   ReadSignedInt(fp, &li, 4);
   fw = (double) li / (double) twoP20;
   return fw;
}


