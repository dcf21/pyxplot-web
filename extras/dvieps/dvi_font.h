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

#ifndef _PPL_DVI_FONT
#define _PPL_DVI_FONT 1

typedef struct TFMcharInfo {
   char wi;      // Width index
   char hi;      // Height index
   char di;      // Depth index
   char ii;      // Italic index
   char tag;
   char rem;
} TFMcharInfo;

// Information for dealing with ligatures
typedef struct TFMligKern {
   char skip_byte;
   char next_char;
   char op_byte;
   char remainder;
} TFMligKern;

typedef struct TFMextRec {
   char top, mid, bot, rep;
} TFMextRec;

typedef struct dviTFM {
   int lf;   // length of the entire file, in words
   int lh;   // length of the header data, in words
   int bc;   // smallest character code in the font
   int ec;   // largest character code in the font
   int nw;   // number of words in the width table
   int nh;   // number of words in the height table
   int nd;   // number of words in the depth table
   int ni;   // number of words in the italic correction table
   int nl;   // number of words in the lig/kern table
   int nk;   // number of words in the kern table
   int ne;   // number of words in the extensible character table
   int np;   // number of font parameter words 
   // Header
   int checksum;
   double ds;    // Design size of font
   char coding[40];
   char family[20];
   int face;
   // Tables
   TFMcharInfo *charInfo;
   double *width, *height, *depth, *italic;
   TFMligKern *ligKern;
   double *kern;
   TFMextRec * extensibleRecipie;
   double *param;
} dviTFM;

typedef struct dviFontDetails {
   int number;
   char *area;               // "Area" that the font is given as living in
   char *name;               // Font name
   int useSize, desSize;     // Use and design sizes
   dviTFM *tfm;              // Data from tfm file
} dviFontDetails;

// Call the first of these two functions, passing it a font structure
// It will find and read the corresponding TFM file
void dviGetTFM(dviFontDetails *font);
dviTFM *dviReadTFM(FILE *fp);

#endif
