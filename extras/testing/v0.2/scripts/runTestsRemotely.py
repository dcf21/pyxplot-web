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

   pathToPyxplot = sys.argv[1]

   # Add user-specified pyxplot as a new version
   insertNewPyxplotVersionIntoDatabase(pathToPyxplot, None, cursor)

   # Obtain version number
   newPplVersion = getFromDB("SELECT id FROM pplversions ORDER BY id DESC LIMIT ?;", (1,), cursor)

   # Add all the tests
   cursor.execute("INSERT OR IGNORE INTO pendingTests (iid, tid) SELECT ?, id FROM tests;", (pplId,))

   # Run the tests
   os.system(os.path.join(rootdir(), "scripts", "runTestsBackend.py") + " >> ppltestlog")

runTestsRemotely()

