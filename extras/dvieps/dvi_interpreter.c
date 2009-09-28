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

// Interpreter functions for various types of dvi operators
int dviInOpChar(dviInterpreterState *interp, DVIOperator *op);
int dviInOpSet1234(dviInterpreterState *interp, DVIOperator *op);
int dviInOpSetRule(dviInterpreterState *interp, DVIOperator *op);
int dviInOpPut1234(dviInterpreterState *interp, DVIOperator *op);
int dviInOpPutRule(dviInterpreterState *interp, DVIOperator *op);
int dviInOpNop(dviInterpreterState *interp, DVIOperator *op);
int dviInOpBop(dviInterpreterState *interp, DVIOperator *op);
int dviInOpEop(dviInterpreterState *interp, DVIOperator *op);
int dviInOpPush(dviInterpreterState *interp, DVIOperator *op);
int dviInOpPop(dviInterpreterState *interp, DVIOperator *op);
int dviInOpRight1234(dviInterpreterState *interp, DVIOperator *op);
int dviInOpW0(dviInterpreterState *interp, DVIOperator *op);
int dviInOpW1234(dviInterpreterState *interp, DVIOperator *op);
int dviInOpX0(dviInterpreterState *interp, DVIOperator *op);
int dviInOpX1234(dviInterpreterState *interp, DVIOperator *op);
int dviInOpDown1234(dviInterpreterState *interp, DVIOperator *op);
int dviInOpY0(dviInterpreterState *interp, DVIOperator *op);
int dviInOpY1234(dviInterpreterState *interp, DVIOperator *op);
int dviInOpZ0(dviInterpreterState *interp, DVIOperator *op);
int dviInOpZ1234(dviInterpreterState *interp, DVIOperator *op);
int dviInOpFnt(dviInterpreterState *interp, DVIOperator *op);
int dviInOpFnt1234(dviInterpreterState *interp, DVIOperator *op);
int dviInOpSpecial1234(dviInterpreterState *interp, DVIOperator *op);
int dviInOpFntdef1234(dviInterpreterState *interp, DVIOperator *op);
int dviInOpPre(dviInterpreterState *interp, DVIOperator *op);
int dviInOpPost(dviInterpreterState *interp, DVIOperator *op);
int dviInOpPostPost(dviInterpreterState *interp, DVIOperator *op);

// Big table of the operator functions to allow quick lookup without a big fat if statement
int (*dviOpTable[58])(dviInterpreterState *interp, DVIOperator *op);
void makeDviOpTable() {
   dviOpTable[0] = dviInOpSet1234;
   dviOpTable[1] = dviInOpSet1234;
   dviOpTable[2] = dviInOpSet1234;
   dviOpTable[3] = dviInOpSet1234;
   dviOpTable[4] = dviInOpSetRule;
   dviOpTable[5] = dviInOpPut1234;
   dviOpTable[6] = dviInOpPut1234;
   dviOpTable[7] = dviInOpPut1234;
   dviOpTable[8] = dviInOpPut1234;
   dviOpTable[9] = dviInOpPutRule;
   dviOpTable[10] = dviInOpNop;
   dviOpTable[11] = dviInOpBop;
   dviOpTable[12] = dviInOpEop;
   dviOpTable[13] = dviInOpPush;
   dviOpTable[14] = dviInOpPop;
   dviOpTable[15] = dviInOpRight1234;
   dviOpTable[16] = dviInOpRight1234;
   dviOpTable[17] = dviInOpRight1234;
   dviOpTable[18] = dviInOpRight1234;
   dviOpTable[19] = dviInOpW0;
   dviOpTable[20] = dviInOpW1234;
   dviOpTable[21] = dviInOpW1234;
   dviOpTable[22] = dviInOpW1234;
   dviOpTable[23] = dviInOpW1234;
   dviOpTable[24] = dviInOpX0;
   dviOpTable[25] = dviInOpX1234;
   dviOpTable[26] = dviInOpX1234;
   dviOpTable[27] = dviInOpX1234;
   dviOpTable[28] = dviInOpX1234;
   dviOpTable[29] = dviInOpDown1234;
   dviOpTable[30] = dviInOpDown1234;
   dviOpTable[31] = dviInOpDown1234;
   dviOpTable[32] = dviInOpDown1234;
   dviOpTable[33] = dviInOpY0;
   dviOpTable[34] = dviInOpY1234;
   dviOpTable[35] = dviInOpY1234;
   dviOpTable[36] = dviInOpY1234;
   dviOpTable[37] = dviInOpY1234;
   dviOpTable[38] = dviInOpZ0;
   dviOpTable[39] = dviInOpZ1234;
   dviOpTable[40] = dviInOpZ1234;
   dviOpTable[41] = dviInOpZ1234;
   dviOpTable[42] = dviInOpZ1234;
   // Big hole here where we ignore FONTi
   dviOpTable[43] = dviInOpFnt1234;
   dviOpTable[44] = dviInOpFnt1234;
   dviOpTable[45] = dviInOpFnt1234;
   dviOpTable[46] = dviInOpFnt1234;
   dviOpTable[47] = dviInOpSpecial1234;
   dviOpTable[48] = dviInOpSpecial1234;
   dviOpTable[49] = dviInOpSpecial1234;
   dviOpTable[50] = dviInOpSpecial1234;
   dviOpTable[51] = dviInOpFntdef1234;
   dviOpTable[52] = dviInOpFntdef1234;
   dviOpTable[53] = dviInOpFntdef1234;
   dviOpTable[54] = dviInOpFntdef1234;
   dviOpTable[55] = dviInOpPre;
   dviOpTable[56] = dviInOpPost;
   dviOpTable[57] = dviInOpPostPost;
   return;
}


// Interpreter functions for various types of dvi operators
int dviInOpChar(dviInterpreterState *interp, DVIOperator *op) {
   return 0;
}
int dviInOpSet1234(dviInterpreterState *interp, DVIOperator *op) {
   return 0;
}
int dviInOpSetRule(dviInterpreterState *interp, DVIOperator *op) {
   return 0;
}
int dviInOpPut1234(dviInterpreterState *interp, DVIOperator *op) {
   return 0;
}
int dviInOpPutRule(dviInterpreterState *interp, DVIOperator *op) {
   return 0;
}
int dviInOpNop(dviInterpreterState *interp, DVIOperator *op) {
   return 0;
}

//DVI_BOP
int dviInOpBop(dviInterpreterState *interp, DVIOperator *op) {
   // Generate a new page
   dlListItem *newItem;
   // Extend the list that we are adding the new page to
   if (interp->output->currentPage == NULL) {
      // This is the first page
      newItem = dlNewList();
      interp->output->pages = newItem;
   } else {
      newItem = dlAppendItem(interp->output->pages);
   }
   newItem->p = (void *) dviNewPostscriptPage();
   interp->output->currentPage = (postscriptPage *)newItem->p;
   interp->output->Npages++;
   // Check that the stack is empty
   if (interp->stack != NULL) {
      dvi_error("Warning: malformed DVI file: stack not empty at start of new page!");
      dlDeleteList(interp->stack);
      interp->stack = NULL;
   }
   // There should not be a string in progress on the stack
   if (interp->currentStrlen != 0) {
      dvi_error("Warning: error in DVI interpreter: string on stack at newpage!");
      interp->currentStrlen = 0;
      free(interp->currentString);
      interp->currentString = NULL;
   }
   // Set the default state values
   interp->state->h = 0;
   interp->state->v = 0;
   interp->state->w = 0;
   interp->state->x = 0;
   interp->state->y = 0;
   interp->state->z = 0;
   // Leave f as it is undefined after a new page
   return 0;
}

int dviInOpEop(dviInterpreterState *interp, DVIOperator *op) {
   return 0;
}

// DVI_PUSH
int dviInOpPush(dviInterpreterState *interp, DVIOperator *op) {
   // Push the current state on to the stack
   dlListItem *newItem;
   if (interp->stack == NULL) {
      newItem = dlNewList();
      interp->stack = newItem;
   } else {
      newItem = dlAppendItem(interp->stack);
   }
   // Create a new stack object and clone the stack on to it
   newItem->p = mallocx(sizeof(dviStackState));
   memcpy(newItem->p, (void *)interp->state, sizeof(dviStackState));
   return 0;
}
//
// DVI_POP
int dviInOpPop(dviInterpreterState *interp, DVIOperator *op) {
   // Pop the previous state off the stack
   dlListItem *item;
   if (interp->stack == NULL) {
      dvi_error("WARNING: corrupt dvi file (attempt to pop off empty stack)!");
      return 1;
   }
   // Remove the old state and replace it with the top one on the stack
   free(interp->state);
   item = interp->stack;
   while (item->nxt != NULL) 
      item = item->nxt;
   interp->state = (dviStackState *)item->p;
   item->p = NULL;
   dlDeleteItem(item);
   // If the stack is now empty remove the dangling pointer
   if (item==interp->stack)
      interp->stack = NULL;
   return 0;
}

// DVI_RIGHT1234
int dviInOpRight1234(dviInterpreterState *interp, DVIOperator *op) {
   interp->state->h += op->sl[0];
   return 0;
}

// DVI_W0
int dviInOpW0(dviInterpreterState *interp, DVIOperator *op) {
   interp->state->h += interp->state->w;
   return 0;
}

// DVI_W1234
int dviInOpW1234(dviInterpreterState *interp, DVIOperator *op) {
   interp->state->w = op->sl[0];
   interp->state->h += interp->state->w;
   return 0;
}

// DVI_X0
int dviInOpX0(dviInterpreterState *interp, DVIOperator *op) {
   interp->state->h += interp->state->x;
   return 0;
}

// DVI_X1234
int dviInOpX1234(dviInterpreterState *interp, DVIOperator *op) {
   interp->state->x = op->sl[0];
   interp->state->h += interp->state->x;
   return 0;
}

// DVI_DOWN1234
int dviInOpDown1234(dviInterpreterState *interp, DVIOperator *op) {
   interp->state->v += op->sl[0];
   return 0;
}

// DVI_Y0
int dviInOpY0(dviInterpreterState *interp, DVIOperator *op) {
   interp->state->v += interp->state->y;
   return 0;
}

// DVI_Y1234
int dviInOpY1234(dviInterpreterState *interp, DVIOperator *op) {
   interp->state->y += op->sl[0];
   interp->state->v += interp->state->y;
   return 0;
}

// DVI_Z0
int dviInOpZ0(dviInterpreterState *interp, DVIOperator *op) {
   interp->state->v += interp->state->z;
   return 0;
}

// DVI_Z1234
int dviInOpZ1234(dviInterpreterState *interp, DVIOperator *op) {
   interp->state->z += op->sl[0];
   interp->state->v += interp->state->z;
   return 0;
}

int dviInOpFnt(dviInterpreterState *interp, DVIOperator *op) {
   return 0;
}

int dviInOpFnt1234(dviInterpreterState *interp, DVIOperator *op) {
   return 0;
}

// DVI_SPECIAL1234
int dviInOpSpecial1234(dviInterpreterState *interp, DVIOperator *op) {
   // NOP
   return 0;
}

int dviInOpFntdef1234(dviInterpreterState *interp, DVIOperator *op) {
   return 0;
}

// DVI_PRE
int dviInOpPre(dviInterpreterState *interp, DVIOperator *op) {
   unsigned long i, num, den, mag;
   i = op->ul[0];
   num = op->ul[0];
   den = op->ul[0];
   mag = op->ul[0];
   if (i != 2) {
      dvi_error("Error interpreting dvi file: not dvi version 2!");
      return 1;
   }
   // Convert mag, num and den into points (for ps)
   interp->scale = (double)mag / 1000. * (double)num / (double)den
           / 1.e4 / 25.4 * 72.;    
   return 0;
}
int dviInOpPost(dviInterpreterState *interp, DVIOperator *op) {
   return 0;
}
int dviInOpPostPost(dviInterpreterState *interp, DVIOperator *op) {
   return 0;
}



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
   interp->state = (dviStackState *)mallocx(sizeof(dviStackState));
   interp->state->h=0;
   interp->state->v=0;
   interp->state->w=0;
   interp->state->x=0;
   interp->state->y=0;
   interp->state->z=0;
   interp->f=0;
   interp->scale=0.;
   // No string currently being assembled
   interp->currentString = NULL;
   interp->currentStrlen = 0;

   // Make the big table of operators
   makeDviOpTable();

   return interp;
}

// Delete an interpreter
void dviDeleteInterpreter(dviInterpreterState *interp) {
   dviInterpreterState *state;
   dlListItem *item;
   free(interp->state);
   if (interp->currentStrlen != 0) {
      free(interp->currentString);
      interp->currentStrlen=0;
   }
   // Delete anything on the stack
   item = interp->stack;
   while (item != NULL) {
      state = item->p;
      if (state!=NULL) {
         free(state);
         item->p = NULL;
      }
      item = item->nxt;
   }
   // Delete the stack
   dlDeleteList(interp->stack);
   interp->stack = NULL;

   // Delete any remaining postscript output
   if (interp->output != NULL)
      dviDeletePostscriptState(interp->output);
   
   // Delete the interpreter shell
   free(interp);
   printf("Freeing the interpreter!\n");
}
   

// Delete a page of postscript output
void dviDeletePostscriptPage(postscriptPage *page) {
   if (page->boundingBox != NULL) {
      free(page->boundingBox);
      page->boundingBox = NULL;
   }
   // The text is a list of simple strings, so we can delete it
   dlClearList(page->text);
   dlDeleteList(page->text);
   free(page);
}

// Clear a set of postscript pages and state
void dviDeletePostscriptState(postscriptState *state) {   
   if (state->Npages > 0) {
      dlListItem *page = state->pages;
      while (page != NULL) {
         dviDeletePostscriptPage((postscriptPage *)page->p);
         page = page->nxt;
      }
      dlDeleteList(state->pages);
      state->Npages = 0;
      state->currentPage = NULL;
   }
   free(state);
}






// Produce a new page of postscript
postscriptPage *dviNewPostscriptPage() {
   postscriptPage *page;
   page = (postscriptPage *)mallocx(sizeof(postscriptPage));
   page->boundingBox = NULL;
   page->position[0] = 0;
   page->position[1] = 0;
   page->text = NULL;
   return page;
}


// Interperate an operator
void dviInterpretOperator(dviInterpreterState *interp, DVIOperator *op) {
   int ret;
   int (*func)(dviInterpreterState *interp, DVIOperator *op) = NULL;
   int i=0;

   if (op->op <= DVI_CHARMAX) {
      func = dviInOpChar;
   } else if (op->op < DVI_FNTNUMMIN) {
      i = op->op-DVI_CHARMAX-1;
      func = (dviOpTable[i]);
   } else if (op->op < DVI_FNTNUMMAX) {
      func = dviInOpFnt;
   } else if (op->op <= DVI_POSTPOST) {
      i = op->op-DVI_CHARMAX-1-(DVI_FNTNUMMAX-DVI_FNTNUMMIN+1);
      func = (dviOpTable[i]);
   } else {
      dvi_error("ERROR: DVI interpreter found illegal operator!");
      func = NULL;
   }
   if (func==NULL) {
      printf("FAILed to find function for operator %d i=%d !\n", op->op, i);
      return;
   }
   ret = (*func)(interp, op);
   printf("State: h=%ld v=%ld w=%ld x=%ld y=%ld z=%ld\n", interp->state->h, interp->state->v, interp->state->w, interp->state->x, interp->state->y, interp->state->z);
   printf("\n");
   return;
}
