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

   # Check that the Big Lock has not been taken out
   testBigLock()

   # Fire up sqlite
   dbs = openaDB("ppltest.db")
   (connection, cursor) = dbs

   # CGI output
   form = cgi.FieldStorage()

   # Warnings to return to the user
   warnings = []


   # Obtain the ppl version to hide
   action = form.getfirst("act")
   pplid = form.getfirst("pplid")

   # Check whether there is an edit to commit
   if (pplid==None or action==None): gcdbsAndErr(dbs, "You need to tell me what to do!")

   # Check for a valid action and version
   try: pplid = int(pplid)
   except: gcdbsAndErr(dbs, "Invalid ppl version")
   if (action != "show" and action != "hide"): gcdbsAndErr(dbs, "Invalid action")

   # Test that the ppl version exists
   hidden = 1
   if (action=="show"): hidden = 0
   cursor.execute("UPDATE pplVersions SET hidden=? WHERE (id=?);", (hidden, pplid))

   # Run the tests
   gcdb(connection, cursor)
   redirect303("mainPage.html")



      

runTestsPage()

