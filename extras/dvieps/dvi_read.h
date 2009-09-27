// dvi_read.h
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

#ifndef _PPL_DVI
#define _PPL_DVI 1

// "Public" function definitions
int ReadDviFile(char *filename);
int ReadDviErrorString(char *error, int stlen);

// Error-handling functions (dvi_error.c)
void dvi_error(char *error);
void dvi_fatal(char *func, int returnCode, char *error);

// "Public" structure definitions
// Structure to store a DVI operator and the data that goes with it
typedef struct DVIOperator {
   unsigned char op; 
   unsigned long int ul[10]; 
   signed long int sl[2]; 
   char *s[2];
} DVIOperator;

// Structure to store the state of a dvi interpreter
typedef struct dviStack {
   signed long int h,v,w,x,y,z;
} dviStack;

#define DVI_ERRORSTR_LEN 2048
extern char DviErrorString[DVI_ERRORSTR_LEN];

// The following definitions are stolen from PyX
//
#define DVI_CHARMIN       0 // typeset a character and move right (range min)
#define DVI_CHARMAX     127 // typeset a character and move right (range max)
#define DVI_SET1234     128 // typeset a character and move right
#define DVI_SETRULE     132 // typeset a rule and move right
#define DVI_PUT1234     133 // typeset a character
#define DVI_PUTRULE     137 // typeset a rule
#define DVI_NOP         138 // no operation
#define DVI_BOP         139 // beginning of page
#define DVI_EOP         140 // ending of page
#define DVI_PUSH        141 // save the current positions (h, v, w, x, y, z)
#define DVI_POP         142 // restore positions (h, v, w, x, y, z)
#define DVI_RIGHT1234   143 // move right
#define DVI_W0          147 // move right by w
#define DVI_W1234       148 // move right and set w
#define DVI_X0          152 // move right by x
#define DVI_X1234       153 // move right and set x
#define DVI_DOWN1234    157 // move down
#define DVI_Y0          161 // move down by y
#define DVI_Y1234       162 // move down and set y
#define DVI_Z0          166 // move down by z
#define DVI_Z1234       167 // move down and set z
#define DVI_FNTNUMMIN   171 // set current font (range min)
#define DVI_FNTNUMMAX   234 // set current font (range max)
#define DVI_FNT1234     238 // set current font
#define DVI_SPECIAL1234 242 // special (dvi extention)
#define DVI_FNTDEF1234  246 // define the meaning of a font number
#define DVI_PRE         247 // preamble
#define DVI_POST        248 // postamble beginning
#define DVI_POSTPOST    249 // postamble ending

#define DVI_VERSION     2   // dvi version

#endif
