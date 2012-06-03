#!/usr/bin/env python2.6

import sys, os, re

from pysqlite2 import dbapi2 as sqlite

from general import *

def runTestsRemotely():
   
   # Fire up sqlite
   dbs = openaDB("ppltest.db")
   (connection, cursor) = dbs

   # Warnings to return to the user
   warnings = []

   if (len(sys.argv)<2):
      print "Usage: <pyxplot binary> [<test id> [<test id>... ] ]"
   pathToPyxplot = sys.argv[1]
   if (len(sys.argv)>2):
      tests = sys.argv[2:]
   else:
      tests = None

   # Add user-specified pyxplot as a new version
   insertNewPyxplotVersionIntoDatabase(pathToPyxplot, None, cursor)

   # Obtain version number
   pplId = getFromDB("SELECT id FROM pplversions ORDER BY id DESC LIMIT ?;", (1,), cursor)

   # Add all the tests
   if (tests==None): cursor.execute("INSERT OR IGNORE INTO pendingTests (iid, tid) SELECT ?, id FROM tests;", (pplId,))
   else:
      for tid in tests:
         cursor.execute("INSERT OR IGNORE INTO pendingTests (iid, tid) VALUES (?,?);", (pplId, tid))

   gcdb(connection, cursor)

   # Run the tests
   os.system(os.path.join(rootdir(), "scripts", "runTestsBackend.py") + " >> ppltestlog")

runTestsRemotely()

