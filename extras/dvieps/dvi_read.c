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

int ReadUChar (FILE *fp, int *uc);
int ReadLongInt (FILE *fp, unsigned long int *uli, int n);
int ReadSignedInt (FILE *fp, signed long int *sli, int n);
int DisplayDVIOperator(DVIOperator *op);
int GetDVIOperator(DVIOperator *op, FILE *fp);

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

   i=0;

   fp = fopen(filename, "r");
   if (fp==NULL)
      dvi_fatal("dvi_read", 1, "dvi file does not exist!");

   /* Very simple DVI reader; just get each opcode and its attached data */
   while (!feof(fp)) {
      //printf("%d\n", ++i);
      if ((err=GetDVIOperator(&op, fp))!=0)
         return err;
      DisplayDVIOperator(&op);
   }
   /*
   for (i=128; i<250; i++) {
      op.op = i;
      printf("Operator %d\n", i);
      DisplayDVIOperator(&op);
   }
   */
   return 0;
}
   
int GetDVIOperator(DVIOperator *op, FILE *fp) {
   int i, v, err;

   // First read in the opcode
   if ((err=ReadUChar(fp,&v))!=0)
      return err;
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
      if ((err=ReadLongInt(fp, op->ul, Ndata))!=0)
         return err;
      return 0;

   } else if (v == DVI_W0) {
      return 0;

   } else if (v < DVI_W1234 + 4) {
      int Ndata;
      Ndata = v - DVI_W1234 + 1;
      if ((err=ReadLongInt(fp, op->ul, Ndata))!=0)
         return err;
      return 0;

   } else if (v == DVI_X0) {
      return 0;

   } else if (v < DVI_X1234 + 4) {
      int Ndata;
      Ndata = v - DVI_X1234 + 1;
      if ((err=ReadLongInt(fp, op->ul, Ndata))!=0)
         return err;
      return 0;

   } else if (v < DVI_DOWN1234 + 4) {
      int Ndata;
      Ndata = v - DVI_DOWN1234 + 1;
      if ((err=ReadLongInt(fp, op->ul, Ndata))!=0)
         return err;
      return 0;

   } else if (v == DVI_Y0) {
      return 0;

   } else if (v < DVI_Y1234 + 4) {
      int Ndata;
      Ndata = v - DVI_Y1234 + 1;
      if ((err=ReadLongInt(fp, op->ul, Ndata))!=0)
         return err;
      return 0;

   } else if (v == DVI_Z0) {
      return 0;

   } else if (v < DVI_Z1234 + 4) {
      int Ndata;
      Ndata = v - DVI_Z1234 + 1;
      if ((err=ReadLongInt(fp, op->ul, Ndata))!=0)
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
      // XXX In pyxplot, replace this with a call to crackmalloc XXX
      op->s[0] = (char *)malloc((Ndata+1)*sizeof(char));
      if (op->s==NULL) 
         dvi_fatal("dvi_read.c", 1, "malloc");
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
      // Mop up all the 233s
      while ((err=ReadUChar(fp,&v1))==0) {
         if (v1 != 233) {
            return -1;
         }
      }
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
      dvi_error("Unexpected EOF in dvi file!");
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
      fv = fv * 256 + v;
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
      fv = fv * 256 + v;
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
      //////printf("XXX 1\n");
   } else if (op->op < DVI_FNTNUMMIN) {
      s = (char *)dviops[op->op-DVI_CHARMAX-1];
      //printf("XXX 2\n");
   } else if (op->op <= DVI_FNTNUMMAX) {
      snprintf(s2, 128, "Font number %d", op->op);
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
