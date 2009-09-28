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

// Functions for manupulating dvi interpreters

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "dvi_read.h"
#include "dvi_lib.h"

// Produce a new dvi interpreter (for a new dvi file, say)
dviInterpreterState *dviNewInterpreter() {
   dviInterpreterState *interp;
   interp = (dviInterpreterState *)mallocx(sizeof(dviInterpreterState));
   // Initially the stack is empty
   interp->stack = NULL;
   interp->output = (postscriptState *)mallocx(sizeof(postscriptState));
   // No postscript yet
   interp->output->pages = NULL;
   interp->output->Npages = 0;
   interp->output->currentPage = NULL;
   // Set default positional variables etc.
   interp->h=0;
   interp->v=0;
   interp->w=0;
   interp->x=0;
   interp->y=0;
   interp->z=0;
   interp->f=0;
   interp->scale=0.;

   return interp;
}

// Interperate an operator
void dviInterpretOperator(dviInterpreterState *interp, DVIOperator *op) {
   return;
}
