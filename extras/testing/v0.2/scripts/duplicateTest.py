#!/usr/bin/env python2.6

import cgi, re, sys
from pysqlite2 import dbapi2 as sqlite
import cgitb

# Stops stdout coercing everything to ascii
reload(sys)
sys.setdefaultencoding('utf-8')

cgitb.enable()

from general import *
from web import *

divcount = 0

# Test edit page
def duplicateTest():

   testBigLock()

   # Fire up sqlite
   (testConnection, testCursor) = openaDB("ppltest.db")

   # Check for the id number and sanitise it
   form = cgi.FieldStorage()
   id = form.getfirst("tid")
   if (id==None): 
      errPage("Error: You have not supplied the id of the test that you would like to duplicate!")
      exit()
   if (not re.match("[0-9]+$", id)):
      errPage("Error: you have supplied an invalid test id.  Test IDs must be positive integers")
      exit()
   
   # Check that this test exists
   try: test = getFromDB("SELECT id FROM tests WHERE id IS ?;", (id,), testCursor)
   except: 
      errPage("Error: you are trying to duplicate a test that doesn't exist.")
      exit()


   # Warnings to return to the user
   warnings = []

   # Things to actually insert into the data base
   updates = {}

   (connection, cursor) = openDB()

   # Obtain basic data about the old test
   (mode, script, name) = cursor.execute("SELECT mode, script, name FROM tests WHERE (id=?);", (id,)).fetchall()[0]
   name = "Copy of %s"%name

   # Make the new test to duplicate into
   cursor.execute("INSERT INTO tests (name, script) VALUES (?,?);", (d["name"], d["script"]))
   ntid = getFromDB('SELECT id FROM tests ORDER BY id DESC LIMIT ?;', (1,), cursor)

   # Obtain the expected outputs
   outputs = cursor.execute("SELECT id, special, filename, mode, diffrules, fid FROM outputs WHERE (tid=?);", (id,)).fetchall()
   # For each output, copy the file and put it back into place
   for (oid, osp, ofn, om, odr, ofid) in outputs:
      ofid = copyFile(ofid)
      cursor.execute("INSERT INTO outputs (tid, special, filename, mode, diffrules, fid) VALUES (?,?,?,?,?,?);", (ntid, osp, ofn, om, odr, ofid, )) 


duplicateTest()

