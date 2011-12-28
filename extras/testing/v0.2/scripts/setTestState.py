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
   tid = form.getfirst("tid")

   # Check whether there is an edit to commit
   if (pplid==None or tid==None or action==None): gcdbsAndErr(dbs, "You need to tell me what to do!")

   # Check for a valid action and version
   try: 
      pplid = int(pplid)
      tid = int(tid)
   except: 
      gcdbsAndErr(dbs, "Invalid input")
   if (action != "passed"): gcdbsAndErr(dbs, "Invalid action")

   cursor.execute("UPDATE insttestmap SET state=? WHERE (iid=? AND tid=?);", (2, pplid, tid))

   gcdb(connection, cursor)
   redirect303("mainPage.html")



      

runTestsPage()

