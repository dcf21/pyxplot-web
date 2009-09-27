// dvi_list.c
//
// The code in this file is not really part of PyXPlot
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

// A linked-list library -- functions
//
#include <stdio.h>
#include <stdlib.h>

#include "dvi_lib.h"
#include "dvi_list.h"

// Private function to create a new list item
dlListItem *dlNewListItem();

dlListItem *dlNewListItem() {
   dlListItem *item;

   item = (dlListItem *)mallocx(sizeof(dlListItem));
   item->prv = NULL;
   item->nxt = NULL;
   return item;
}

// Create a new list with a single item
dlListItem *dlNewList() {
   return dlNewListItem();
}

// Append an item to a list
dlListItem *dlAppendItem(dlListItem *list) {
   dlListItem *item;
   // Find the end of the list, dealing with circular lists
   item = list;
   while ((item->nxt != NULL) && (item->nxt != list)) {
      item = item->nxt;
   }
   // Create a new item and insert it in the appropriate place
   item->nxt = dlNewListItem();
   // Set new item to point back correctly
   item->nxt->prv = item;
   return item->nxt;
}

// Prepend an item to a list
dlListItem *dpPrependItem(dlListItem *list) {
   dlListItem *item;
   // Find the beginning of the list, dealing with circular lists
   item = list;
   while ((item->prv != NULL) && (item->prv != list)) {
      item = item->prv;
   }
   // Create a new item and insert it in the appropriate place
   item->prv = dlNewListItem();
   // Set new item to point back correctly
   item->prv->nxt = item;
   return item->prv;
}

// Splice an item into a list after the current item
dlListItem *dlSpliceItem(dlListItem *list) {
   dlListItem *item;
   // Save the item that the current item points to
   item = list->nxt;
   list->nxt = dlNewListItem();
   list->nxt->prv = list;
   list->nxt->nxt = item;
   if (item != NULL) {
      item->prv = list->nxt;
   }
   return list->nxt;
}

// Delete an item from a list
// Any pointers only contained within the item will be lost!
dlListItem *dlDeleteItem(dlListItem *list) {
   dlListItem *prev, *next;
   prev = list->prv;
   next = list->nxt;
   // Patch over the hole
   if (prev != NULL) 
      prev->nxt = next;
   if (next != NULL)
      next->prv = prev;
   free(list);
   return prev==NULL?next:prev;
}

// Delete an entire list
void dlDeleteList(dlListItem *list) {
   dlListItem *item;
   // Find the beginning of the list, dealing with circular lists
   item = list;
   while ((item->prv != NULL) && (item->prv != list)) {
      item = item->prv;
   }
   // Terminate a circular list
   if (item->prv == list)
      item->nxt = NULL;
   // Recurse through the list deleting it
   while (item != NULL) {
      dlListItem *next;
      next = item->nxt;
      dlDeleteItem(item);
      item = next;
   }
   return;
}
