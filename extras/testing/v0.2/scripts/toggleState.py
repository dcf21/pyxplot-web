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

   # Obtain the state id and test for sanity
   sid = form.getfirst("id")
   try:  sid = int(sid)
   except: gcdbsAndErr(dbs, "Invalid input")

   temp = cursor.execute("SELECT state FROM systemStates WHERE (id=?);", (sid, )).fetchall()[0]
   if (len(temp)==0): gcdbsAndErr(dbs, "Invalid state to toggle")

   cursor.execute("UPDATE systemStates SET state=? WHERE (id=?);", (1-int(temp[0]), sid))
     

   
   # Run the tests
   gcdb(connection, cursor)
   redirect303("mainPage.html")



      

runTestsPage()

