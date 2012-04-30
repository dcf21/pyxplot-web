#!/usr/bin/env python2.6

import cgi, re, sys, os
from pysqlite2 import dbapi2 as sqlite
import cgitb

# Stops stdout coercing everything to ascii
reload(sys)
sys.setdefaultencoding('utf-8')

cgitb.enable()

from general import *
from web import *

# Test edit page
def runTestsPage():

   testBigLock()

   # Fire up sqlite
   dbs = openaDB("ppltest.db")
   (connection, cursor) = dbs

   # CGI output
   form = cgi.FieldStorage()

   # Warnings to return to the user
   warnings = []

   action = form.getfirst("act")

   # Check whether there is an edit to commit
   if (action==None): gcdbsAndErr(dbs, "You need to tell me what to do!")
      

   # Work out what we're supposed to do
   mo = re.match("run([a-z0-9]+)_([a-z0-9]+)$", action)
   if (mo==None): gcdbsAndErr(dbs, "You need to tell me what to do!")

   atype = mo.group(1)
   pplId = mo.group(2)

   # Mode 1: one ppl version specified
   if (re.match("[0-9]+$", pplId)):

      # Test that the ppl version exists
      if (int(getFromDB("SELECT COUNT(*) FROM pplVersions WHERE (id=?);", (pplId,), cursor))!=1):
          gcdbsAndErr(dbs, "Your ppl instance does not exist")
   
      if (atype == "all"):
         cursor.execute("INSERT OR IGNORE INTO pendingTests (iid, tid) SELECT ?, id FROM tests;", (pplId,))
      elif (atype == "new"):
         cursor.execute("INSERT OR IGNORE INTO pendingTests (iid, tid) SELECT ?, itm.tid FROM insttestmap itm WHERE (iid=? AND state=1);", (pplId,pplId))
      elif (atype == "fail"):
         cursor.execute("INSERT OR IGNORE INTO pendingTests (iid, tid) SELECT ?, itm.tid FROM insttestmap itm WHERE (iid=? AND state=3);", (pplId,pplId))
      elif (re.match("[0-9]+$", atype)):   # Run a particular test
         cursor.execute("INSERT OR IGNORE INTO pendingTests (iid, tid) VALUES (?,?);", (pplId, atype))
      else:
         gcdbsAndErr(dbs, "Did not understand answer")

   elif (pplId == "all"):
      if (atype == "all"):
         cursor.execute("INSERT OR IGNORE INTO pendingTests (iid, tid) SELECT itm.iid, itm.tid FROM insttestmap itm;")
      elif (atype == "new"):
         cursor.execute("INSERT OR IGNORE INTO pendingTests (iid, tid) SELECT itm.iid, itm.tid FROM insttestmap itm WHERE (state=1);")
      elif (atype == "fail"):
         cursor.execute("INSERT OR IGNORE INTO pendingTests (iid, tid) SELECT itm.iid, itm.tid FROM insttestmap itm WHERE (state=3);")
      elif (re.match("[0-9]+$", atype)):   # Run a particular test
         cursor.execute("INSERT OR IGNORE INTO pendingTests (iid, tid) SELECT itm.iid, itm.tid FROM insttestmap itm WHERE (tid=?);", (atype,))
      else:
         gcdbsAndErr(dbs, "Did not understand answer")


   else:
      gcdbsAndErr(dbs, "Did not understand request")
   
   # Run the tests
   gcdb(connection, cursor)
   launchTests()
   redirect303("mainPage.html")



      

runTestsPage()

