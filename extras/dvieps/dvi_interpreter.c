// dvi_interpreter.c
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

// Functions for manupulating dvi interpreters

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>

#include "dvi_read.h"
#include "dvi_lib.h"
#include "dvi_font.h"

#define SHORT_STRLEN 2048

// Postscript functions
int dviPostscriptLineto(dviInterpreterState *interp);
int dviPostscriptClosepathFill(dviInterpreterState *interp);
int dviChngFnt(dviInterpreterState *interp, int fn);
int dviSpecialColourCommand(dviInterpreterState *interp, char *command);
int dviSpecialColourStackPush(dviInterpreterState *interp, char *psText);
int dviSpecialColourStackPop(dviInterpreterState *interp);

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

// Functions called by operator interpreter functions
void dviSpecialChar(dviInterpreterState *interp, DVIOperator *op);
int dviSpecialImplement(dviInterpreterState *interp);
int dviNonAsciiChar(dviInterpreterState *interp, int c, char move);
void dviUpdateBoundingBox(dviInterpreterState *interp, double width, double height, double depth);

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


// Interpret an operator
// This is a wrapper round the functions below
int dviInterpretOperator(dviInterpreterState *interp, DVIOperator *op) {
   int (*func)(dviInterpreterState *interp, DVIOperator *op) = NULL;
   int i=0;
   int err;
   char errStr[SHORT_STRLEN];

   // Deal with the processing of DVI extensions (DIV_XXX/SPECIAL)
   if (interp->special > 0) {
      if (op->op <= DVI_CHARMAX) {
         dviSpecialChar(interp, op);
         return DVIE_SUCCESS;
      } else {
         // The following function turns the special flag off, and hence 
         // op is evaluated below
         if ((err=dviSpecialImplement(interp)) > DVIE_WARNING) {
            return err;
         }
      }
   }

	// This if statement extends the lookup table of operator functions
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
      dvi_error("DVI interpreter found illegal operator!");
      return DVIE_CORRUPT;
   }
   if (func==NULL) {
      snprintf(errStr, SHORT_STRLEN, "FAILed to find function for operator %d i=%d !\n", op->op, i);
      dvi_error(errStr);
      return DVIE_CORRUPT;
   }

   // If we are not typesetting a character and moving right, check if we need to set accumulated text
   // if (interp->currentString != NULL)
   if (op->op > DVI_SET1234+3 && interp->currentString != NULL)
      dviTypeset(interp);

	// Call the function to interpret the operator
   return (*func)(interp, op);
}

/////////////////////////////////////////////////////////////////////////////////////////////////////
// Functions that implement operators
//
// Typeset a special character
int dviNonAsciiChar(dviInterpreterState *interp, int c, char move) {
   char *s;
   dviStackState *postPos, *dviPos;   // Current positions in dvi and postscript code
   double width, height, depth, size[3];
   int chars;

   postPos = interp->output->currentPosition;
   dviPos = interp->state;
   
   // First check if we need to move before typesetting
   if (postPos== NULL) {
      dviPostscriptMoveto(interp);
      interp->output->currentPosition = dviCloneInterpState(dviPos);
   } else if (postPos->h != dviPos->h || postPos->v != dviPos->v) {
      dviPostscriptMoveto(interp);
   }

   // Bounding box stuff
   dviGetCharSize(interp, (char)c, size);
   // Convert back into dvi units
   width  = size[0] / interp->scale;
   height = size[1] / interp->scale;
   depth  = size[2] / interp->scale;
   printf("width of glyph %g height of glyph %g\n", width, height);
   dviUpdateBoundingBox(interp, width, height, depth);

   // Count the number of characters to write to the ps string
   chars = 15;
   s = (char *)mallocx(chars*sizeof(char));
   snprintf(s, chars, "(\\%o) show\n", c);

   // Send the string off to the postscript routine and clean up memory
   dviPostscriptAppend(interp, s);
   free(s);
   free(interp->currentString);
   interp->currentString = NULL;
   interp->currentStrlen = 0;

   // Adjust the current position
   if (move == DVI_YES) {
      interp->state->h += width;
      interp->output->currentPosition->h += width;
   }
   return 0;
}

// Interpreter functions for various types of dvi operators
int dviInOpChar(dviInterpreterState *interp, DVIOperator *op) {
   int charToTypeset = op->op;
   char *s;

   // Typeset non-printable characters separately
   if (charToTypeset<48 || 
                   (charToTypeset>57 && charToTypeset<65) ||
                   (charToTypeset>90 && charToTypeset<97) ||
                   charToTypeset > 126) {
      // Clear the queue if there's anything on it
      if (interp->currentString != NULL) 
         dviTypeset(interp);
      dviNonAsciiChar(interp, charToTypeset, DVI_YES);
      return 0;
   }

   // See if we have anywhere to put the character
   if (interp->currentString == NULL) {
      interp->currentString = (char *)mallocx(SHORT_STRLEN*sizeof(char));
      *(interp->currentString) = '\0';
      interp->currentStrlen = SHORT_STRLEN;
   // If the string is full, extend it
   } else if (strlen(interp->currentString) == interp->currentStrlen-2) {
      interp->currentStrlen += SHORT_STRLEN;
      interp->currentString = (char *) realloc(interp->currentString, interp->currentStrlen*sizeof(char));
   }
   // Write the character to the string
   s = interp->currentString+strlen(interp->currentString); // s now points to the \0
   if (charToTypeset == 40) {
      snprintf(s, 3, "%s", "\\(");
   } else if (charToTypeset == 41) {
      snprintf(s, 3, "%s", "\\)");
   } else {
      snprintf(s, 2, "%s", (char *)&charToTypeset);
   }
   return 0;
}

// DVI_SET1234
int dviInOpSet1234(dviInterpreterState *interp, DVIOperator *op) {
   return dviNonAsciiChar(interp, op->ul[0], DVI_YES);
}

// DVI_SETRULE
// Set a rule and move right
int dviInOpSetRule(dviInterpreterState *interp, DVIOperator *op) {
   int err = DVIE_SUCCESS;
   //
   // Don't set a rule if movements are -ve
   if (op->sl[0]<0 || op->sl[1]<0) {
      printf("Silent Rule!\n");
      interp->state->h += op->sl[1];
      dviPostscriptMoveto(interp);
   } else {
      dviUpdateBoundingBox(interp, (int)op->sl[1], (int)op->sl[0], 0.);
      dviPostscriptMoveto(interp);
      interp->state->v -= op->sl[0];
      if ((err=dviPostscriptLineto(interp)) > DVIE_WARNING)
         return err;
      interp->state->h += op->sl[1];
      if ((err=dviPostscriptLineto(interp)) > DVIE_WARNING)
         return err;
      interp->state->v += op->sl[0];
      if ((err=dviPostscriptLineto(interp)) > DVIE_WARNING)
         return err;
      if ((err=dviPostscriptClosepathFill(interp)) > DVIE_WARNING)
         return err;
   }
   return err;
}

// DVI_PUT
int dviInOpPut1234(dviInterpreterState *interp, DVIOperator *op) {
   dviNonAsciiChar(interp, op->ul[0], DVI_NO);
   return 0;
}

// DVI_PUTRULE
// Set a rule and don't move right
int dviInOpPutRule(dviInterpreterState *interp, DVIOperator *op) {
   int err=DVIE_SUCCESS;
   // Don't set a rule if movements are -ve
   if (op->sl[0]<0 || op->sl[1]<0) {
      printf("Silent Rule!\n");
   } else {
      dviUpdateBoundingBox(interp, (int)op->sl[1], (int)op->sl[0], 0.);
      dviPostscriptMoveto(interp);
      interp->state->v -= op->sl[0];
      if ((err=dviPostscriptLineto(interp)) > DVIE_WARNING)
         return err;
      interp->state->h += op->sl[1];
      if ((err=dviPostscriptLineto(interp)) > DVIE_WARNING)
         return err;
      interp->state->v += op->sl[0];
      if ((err=dviPostscriptLineto(interp)) > DVIE_WARNING)
         return err;
      if ((err=dviPostscriptClosepathFill(interp)) > DVIE_WARNING)
         return err;
      interp->state->h -= op->sl[1];
   }
   return err;
}

// DVI_NOP
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

// DVI_EOP
int dviInOpEop(dviInterpreterState *interp, DVIOperator *op) {
   double *bb;
   // Set appropriate postscript bounding box from dvi bb
   // left bottom right top
   bb = interp->boundingBox;
   // Convert bounding box from DVI to PS units
   bb[0] *= interp->scale;
   bb[1] = 765 - bb[1] * interp->scale;
   bb[2] *= interp->scale;
   bb[3] = 765 - bb[3] * interp->scale;
   // Move pointer to postscript
   interp->output->currentPage->boundingBox = bb;
   interp->boundingBox = NULL;
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
   newItem->p = (void *)dviCloneInterpState(interp->state);
   /* mallocx(sizeof(dviStackState));
   memcpy(newItem->p, (void *)interp->state, sizeof(dviStackState)); */
   return 0;
}

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
   // Unset the special flag
   interp->special = 0;
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
   interp->state->y = op->sl[0];
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
   interp->state->z = op->sl[0];
   interp->state->v += interp->state->z;
   return 0;
}

// DVI_FNTi
int dviInOpFnt(dviInterpreterState *interp, DVIOperator *op) {
   int fn;
   fn = op->op - DVI_FNTNUMMIN;
   return dviChngFnt(interp, fn);
}

// DVI_FNT1234
int dviInOpFnt1234(dviInterpreterState *interp, DVIOperator *op) {
   dviChngFnt(interp, op->ul[0]);
   return 0;
}

// DVI_SPECIAL1234
int dviInOpSpecial1234(dviInterpreterState *interp, DVIOperator *op) {
   int spesh;
   spesh = op->op - DVI_SPECIAL1234+1;
   interp->special = spesh;
   interp->spString = (char *)mallocx(SHORT_STRLEN*sizeof(char));
   *(interp->spString) = '\0';
   printf("Special! %d %lu %d\n", spesh, op->ul[0], strlen(interp->spString));
   // NOP
   return 0;
}

// DVI_FNTDEF1234
int dviInOpFntdef1234(dviInterpreterState *interp, DVIOperator *op) {
   // XXX Should perhaps check that we're not re-defining an existing font here
   // XXX Could check that we're not after POST and hence that we need to do this
   dlListItem *item;
   dviFontDetails *font;
   int i;

   // Create a list place to put the font in and a structure for it
   if (interp->fonts == NULL) {
      item = dlNewList();
      interp->fonts = item;
   } else {
      item = dlAppendItem(interp->fonts);
   }
   font = mallocx(sizeof(dviFontDetails));
   item->p = (void *)font;
   // Populate with information from operator
   font->number = op->ul[0];
   font->area = (char *)mallocx((op->ul[4]+1)*sizeof(char));
   for (i=0; i<op->ul[4]; i++)
      font->area[i] = op->s[0][i];
   font->area[op->ul[4]] = '\0';
   font->name = (char *)malloc((op->ul[5]+1)*sizeof(char));
   for (i=0; i<op->ul[5]; i++)
      font->name[i] = op->s[0][op->ul[4]+i];
   font->name[op->ul[5]] = '\0';
   font->useSize = op->ul[2];
   font->desSize = op->ul[3];

   // parse the TFM file for useful data
   return dviGetTFM(font);
}

// DVI_PRE
int dviInOpPre(dviInterpreterState *interp, DVIOperator *op) {
   unsigned long i, num, den, mag;
   i = op->ul[0];
   num = op->ul[1];
   den = op->ul[2];
   mag = op->ul[3];
   if (i != 2) {
      dvi_error("Error interpreting dvi file: not dvi version 2!");
      return 1;
   }
   // Convert mag, num and den into points (for ps)
   interp->scale = (double)mag / 1000. * (double)num / (double)den
           / 1.e3 * 72. / 254;    
   printf("Scale %g V=%lu num=%lu den=%lu mag=%lu\n", interp->scale,i,num,den,mag);
   return 0;
}

// DVI_POST -- nop
int dviInOpPost(dviInterpreterState *interp, DVIOperator *op) {
   return 0;
}

// DVI_POSTPOST -- nop
int dviInOpPostPost(dviInterpreterState *interp, DVIOperator *op) {
   return 0;
}

/////////////////////////////////////////////////////////////////////////////////////////////////////

// Functions for implementing special operators (DVI_SPECIAL)

// Accumulate characters output in special mode into a string
void dviSpecialChar(dviInterpreterState *interp, DVIOperator *op) {
   int c;
   char *s;
   c = op->op;
   s = interp->spString+strlen(interp->spString);
   snprintf(s, SHORT_STRLEN, "%s", (char *)&c);
   return;
}

// Implement an accumulated special-mode command
int dviSpecialImplement(dviInterpreterState *interp) {
   int err = DVIE_SUCCESS;
   char errString[SHORT_STRLEN];

   printf("Special!  Final string=%s\n", interp->spString);
   // Test for a colour string
   if (strncmp(interp->spString, "color ", 6) == 0) {
      dviSpecialColourCommand(interp, interp->spString+6);
   } else {
      // Unhandled special command (e.g. includegraphics)
      snprintf(errString, SHORT_STRLEN, "Warning! ignoring unhandled DVI special string %s\n", interp->spString);
      dvi_error(errString);
      err = DVIE_WARNING;
   }

   // Clean up
   free(interp->spString);
   interp->spString = NULL;
   interp->special = 0;
   return err;
}

// Handle latex colour commands
int dviSpecialColourCommand(dviInterpreterState *interp, char *command) {
   char psText[SHORT_STRLEN];
   // Skip over any leading spaces
   while (command[0] == ' ') 
      command++;
   // See what sort of colour command it is

   if (strncmp(command, "push ", 4)==0) {
      // New colour to push onto stack
      printf("%s says push\n", command);
      command += 5;
      while (command[0] == ' ')
         command++;
      if (strncmp(command, "cmyk ", 5)==0) {
         // CMKY colour
         command += 5;
         snprintf(psText, SHORT_STRLEN, "%s setcmykcolor\n", command);
      } else if (strncmp(command, "rgb ", 4)==0) {
         // rgb colour
         command += 4;
         snprintf(psText, SHORT_STRLEN, "%s setrgbcolor\n", command);
      } else if (strncmp(command, "Black", 5)==0) {
         snprintf(psText, SHORT_STRLEN, "0 0 0 setrgbcolor\n");
      } else if (strncmp(command, "gray ", 5)==0 || strncmp(command, "grey ", 5)==0) {
         command += 5;
         snprintf(psText, SHORT_STRLEN, "%s %s %s setrgbcolor\n", command, command, command);
      } else {
         snprintf(psText, SHORT_STRLEN, "Failed to comprehend colour %s\n", command);
         dvi_error(psText);
         return 1;
      }
      dviSpecialColourStackPush(interp, psText);
      return 0;

   } else if (strncmp(command, "pop", 3)==0) {
      // Pop a colour off the stack
      return dviSpecialColourStackPop(interp);

   } else {
      snprintf(psText, SHORT_STRLEN, "Warning! Ignoring incomprehensible colour command %s\n", command);
      dvi_error(psText);
      return 3;
   }
   return 0;
}

// Pop a colour instruction off the end of the stack
int dviSpecialColourStackPop(dviInterpreterState *interp) {
   dlListItem *item;
   
   // Find the end of the colour stack
   item = interp->colStack;
   if (item==NULL) {
      dvi_error("Warning!  DVI colour pop from empty stack!\n");
      return 1;
   }
   while (item->nxt != NULL) 
      item = item->nxt;

   // Lop off the last item
   item = dlDeleteItem(item);
   // Set colour to item on top of stack
   if (item==NULL) {
      // Hit the bottom of the colour stack; default colour is black
      interp->colStack = NULL;
      dviPostscriptAppend(interp, "0 0 0 setrgbcolor\n");
   } else {
      dviPostscriptAppend(interp, (char *)item->p);
   }
   return 0;
}

// Push a colour onto the colour stack
int dviSpecialColourStackPush(dviInterpreterState *interp, char *psText) {
   dlListItem *item;
   char *s;
   int len;
   // Make a new stack item and list if necessary
   if (interp->colStack == NULL) {
      item = dlNewList();
      interp->colStack = item;
   } else {
      item = dlAppendItem(interp->colStack);
   }
   // Stick the string onto the stack
   len = strlen(psText)+1;
   s = (char *)mallocx(len*sizeof(char));
   snprintf(s, len, "%s", psText);
   item->p = (void *)s;

   // Also append to the postscript stack
   dviPostscriptAppend(interp, psText);

   return 0;
}


/////////////////////////////////////////////////////////////////////////////////////////////////////

// Functions for manipulating interpreters

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
   interp->curFnt = NULL;
   interp->scale=0.;
   // No string currently being assembled
   interp->currentString = NULL;
   interp->currentStrlen = 0;
   // No fonts currently
   interp->fonts = NULL;

   // Nothing special occuring
   interp->special = 0;  // Not in special mode
   interp->spString = NULL;

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
}

// Clone an interpreter state, returning a pointer to the new version
// XXX Make the name of this function consistent with usage elsewhere or vice versa
dviStackState *dviCloneInterpState(dviStackState *orig) {
   void *clone;
   clone = mallocx(sizeof(dviStackState));
   memcpy(clone, (void *)orig, sizeof(dviStackState));
   return (dviStackState *) clone;
}

/////////////////////////////////////////////////////////////////////////////////////////////////////
//
// Functions for producing and manipulating postscript pages

// Produce a new page of postscript
postscriptPage *dviNewPostscriptPage() {
   postscriptPage *page;
   page = (postscriptPage *)mallocx(sizeof(postscriptPage));
   page->boundingBox = NULL;
   //page->position[0] = 0;
   //page->position[1] = 0;
   page->text = NULL;
   //page->currentPosition = NULL; // No position set initially
   return page;
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

/////////////////////////////////////////////////////////////////////////////////////////////////////
//
// Functions for producing postscript commands

// Append a string to the set of postscript strings
void dviPostscriptAppend(dviInterpreterState *interp, char *new) {
   dlListItem *item;   // Temporary storage for a list item
   char *s;            // A temporary string pointer
   int len;
   // Check to see if there are any strings there already
   if (interp->output->currentPage->text == NULL) {
      interp->output->currentPage->text = dlNewList();
      item = interp->output->currentPage->text;
   } else {
      item = dlAppendItem(interp->output->currentPage->text);
   }
   // Grab the new string and copy it into place
   len = strlen(new)+1;
   s = (char *)mallocx(len*sizeof(char));
   strncpy(s, new, len);
   item->p = (void *)s;
   return;
}

// Write some postscript to move to the current co-ordinates
void dviPostscriptMoveto(dviInterpreterState *interp) {
   char s[SHORT_STRLEN];
   double x, y;
   x = interp->state->h * interp->scale;
   y = 765 - interp->state->v * interp->scale;
   snprintf(s, SHORT_STRLEN, "%f %f moveto\n", x, y);
   dviPostscriptAppend(interp, s);
   // If we don't have a current position make one, else set the current ps position to the dvi one
   if (interp->output->currentPosition == NULL) {
      interp->output->currentPosition = dviCloneInterpState(interp->state);
   } else {
      interp->output->currentPosition->h = interp->state->h;
      interp->output->currentPosition->v = interp->state->v;
   }
}

// Write some postscript to draw a line to the current co-ordinates
int dviPostscriptLineto(dviInterpreterState *interp) {
   char s[SHORT_STRLEN];
   double x, y;
   x = interp->state->h * interp->scale;
   y = 765 - interp->state->v * interp->scale;
   snprintf(s, SHORT_STRLEN, "%f %f lineto\n", x, y);
   dviPostscriptAppend(interp, s);
   // If we don't have a current position make one, else set the current ps position to the dvi one
   if (interp->output->currentPosition == NULL) {
      dvi_error("Postscript error: lineto command issued with NULL current state!");
      return DVIE_INTERNAL;
   } else {
      interp->output->currentPosition->h = interp->state->h;
      interp->output->currentPosition->v = interp->state->v;
   }
   return DVIE_SUCCESS;
}

// Write some postscript to close a path
int dviPostscriptClosepathFill(dviInterpreterState *interp) {
   char s[SHORT_STRLEN];
   double x, y;
   x = interp->state->h * interp->scale;
   y = 765 - interp->state->v * interp->scale;
   snprintf(s, SHORT_STRLEN, "closepath fill\n");
   dviPostscriptAppend(interp, s);
   if (interp->output->currentPosition == NULL) {
      dvi_error("Postscript error: closepath command issued with NULL current state!");
      return DVIE_INTERNAL;
   } else {
      free(interp->output->currentPosition);
      interp->output->currentPosition = NULL;
   }
   return DVIE_SUCCESS;
}

// Typeset the current buffered text
void dviTypeset(dviInterpreterState *interp) {
   // This subroutine does the bulk of the actual postscript work, typesetting runs of characters
   dviStackState *postPos, *dviPos;   // Current positions in dvi and postscript code
   char *s;
   double width, height, depth;
   double size[3];               // Width, height, depth
   int chars;

   postPos = interp->output->currentPosition;
   dviPos = interp->state;
   
   // First check if we need to move before typesetting
   if (postPos== NULL) {
      dviPostscriptMoveto(interp);
      interp->output->currentPosition = dviCloneInterpState(dviPos);
   //} else {//if (postPos->h != dviPos->h || postPos->v != dviPos->v) {
   } else if (postPos->h != dviPos->h || postPos->v != dviPos->v) {
      dviPostscriptMoveto(interp);
   }
   s = interp->currentString;
   width = 0.;
   height = 0.;
   depth = 0.;
   while (*s != '\0') {
      dviGetCharSize(interp, *s, size);
      width += size[0];
      height = size[1]>height ? size[1] : height;
      depth = size[2]>depth ? size[2] : depth;
      s++;
   }
   // Convert back into dvi units
   width /= interp->scale;
   height /= interp->scale;
   depth /= interp->scale;
   printf("width of glyph %g height of glyph %g\n", width, height);
   dviUpdateBoundingBox(interp, width, height, depth);
   
   // Count the number of characters to write to the ps string
   chars = strlen(interp->currentString)+9;
   s = (char *)mallocx(chars*sizeof(char));
   snprintf(s, chars, "(%s) show\n", interp->currentString);
   
   // Send the string off to the postscript routine and clean up memory
   dviPostscriptAppend(interp, s);
   free(s);
   free(interp->currentString);
   interp->currentString = NULL;
   interp->currentStrlen = 0;

   // Adjust the current position
   interp->state->h += width;
   interp->output->currentPosition->h += width;
   return;
}

// Change to a new font
int dviChngFnt(dviInterpreterState *interp, int fn) {
   dlListItem *item;
   int len;
   char *s;
   dviFontDetails *font;
   double size;
   
   interp->f = fn;
   // Find the font in the list
   interp->curFnt = NULL;
   item = interp->fonts;
   while (item != NULL) {
      if (((dviFontDetails *)item->p)->number == fn) {
         interp->curFnt = item;
         break;
      }
      item = item->nxt;
   }
   if (interp->curFnt == NULL) {
      dvi_error("Corrupt DVI file: failed to find current font!");
      return 2;
   }

   // XXX Fount size???
   font = (dviFontDetails *)item->p;
   len = strlen(font->psName) + 20;
   //\XXX 12 selectfont\n\0
   s = (char *)mallocx(len*sizeof(char));
   size = font->useSize*interp->scale;
   printf("Font useSize %d size %g changed to %d\n", font->useSize, size, (int)ceil(size-.5));
   snprintf(s, len, "/%s %d selectfont\n", font->psName, (int)ceil(size-.5));
   dviPostscriptAppend(interp, s);
   free(s);
   return 0;
}

// Get the size (width, height, depth) of a glyph
void dviGetCharSize(dviInterpreterState *interp, char s, double *size) {
   dviTFM *tfm;       // Details of this font
   int chnum;                 // Character number in this font
   TFMcharInfo *chin;         // Character info for this character
   int wi, hi, di;            // Index
   //double width;              // Final character width
	dviFontDetails *font;      // Font information (for tfm and use size)
   
	font = (dviFontDetails *)interp->curFnt->p;
   tfm = font->tfm;
   chnum = s - tfm->bc;
   chin = tfm->charInfo+chnum;

   wi = (int)chin->wi;
   hi = (int)chin->hi;
   di = (int)chin->di;
   size[0] = tfm->width[wi] * font->useSize * interp->scale;
   size[1] = tfm->height[hi] * font->useSize * interp->scale;
   size[2] = tfm->depth[di] * font->useSize * interp->scale;

   printf("Character %d chnum %d has indices %d %d %d width %g height %g depth %g useSize %g\n", s, chnum, wi, di, hi, size[0], size[1], size[2], font->useSize*interp->scale);
   return;
}

/*
// Get the height of a character to be rendered
float dviGetCharHeight(dviInterpreterState *interp, char s) {
   // XXX Write this function (requires font knowledge...)
   return 12.;
}

// Get the width of a character to be rendered
float dviGetCharWidth(dviInterpreterState *interp, char s) {
   dviTFM *tfm;       // Details of this font
   int chnum;                 // Character number in this font
   TFMcharInfo *chin;         // Character info for this character
   int wi;                    // Width index
   double width;              // Final character width
	dviFontDetails *font;      // Font information (for tfm and use size)
   
	font = (dviFontDetails *)interp->curFnt->p;
   tfm = font->tfm;
   chnum = s - tfm->bc;
   chin = tfm->charInfo+chnum;
   wi = (int)chin->wi;
   width = tfm->width[wi] * font->useSize * interp->scale;

   printf("Character %d chnum %d has width index %d width %g useSize %g\n", s, chnum, wi, width, font->useSize*interp->scale);
   return width;
}
*/

// Update a bounding box with the position and size of the current object to be typeset
void dviUpdateBoundingBox(dviInterpreterState *interp, double width, double height, double depth) {
   double *bb;
   double bbObj[4];      // Bounding box of the object that we are typeseting
   
   // left bottom right top
   // DVI counts down from the top (and this is all DVI units)
   bbObj[0] = interp->state->h;
   bbObj[1] = interp->state->v + depth;
   bbObj[2] = interp->state->h + width;
   bbObj[3] = interp->state->v - height;

   // Check to see if we already have a bounding box
   if (interp->boundingBox == NULL) {
      bb = (double *)mallocx(4*sizeof(double));
      bb[0] = bbObj[0];
      bb[1] = bbObj[1];
      bb[2] = bbObj[2];
      bb[3] = bbObj[3];
      interp->boundingBox = bb;
      
   } else {
      // Check against current bounding box
      bb = interp->boundingBox;
      bb[0] = bb[0] < bbObj[0] ? bb[0] : bbObj[0];
      bb[1] = bb[1] > bbObj[1] ? bb[1] : bbObj[1];
      bb[2] = bb[2] > bbObj[2] ? bb[2] : bbObj[2];
      bb[3] = bb[3] < bbObj[3] ? bb[3] : bbObj[3];
   }
   return;
}
