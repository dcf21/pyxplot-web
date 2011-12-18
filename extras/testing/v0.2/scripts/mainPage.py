#!/usr/bin/python

import cgi, re, sys
from pysqlite2 import dbapi2 as sqlite
import cgitb

# Stops stdout coercing everything to ascii
reload(sys)
sys.setdefaultencoding('utf-8')

cgitb.enable()

from general import *
from web import *


# Test edit page
def mainPage():

   # Fire up sqlite
   (connection, cursor) = openDB()
   (testConnection, testCursor) = openaDB("ppltest.db")

   # CGI output
   form = cgi.FieldStorage()

   # Warnings to return to the user
   warnings = []

   # Things to actually insert into the data base
   updates = {}

   # Check whether there is an edit to commit
   if (form.getfirst("hidden")==None):
      httpHeaders()
      page = renderMainPage(id, testCursor, cursor)
      sys.stdout.write(page)
      gcdb(testConnection, testCursor)
      gcdb(connection, cursor)
      return

   # Do all the other stuff
   #XXX all redundant after this point
   uploadOutcome = parseMainPageSubmission(id, form, testCursor, warnings, updates)

   # If the instructions say to redirect the user off elsewhere, do that
   if ("redirect" in uploadOutcome):
      redirect303(uploadOutcome["redirect"])

   httpHeaders()
   page = renderMainPageHead(id,testCursor, cursor)
   page += uploadOutcome["page"]
   # Warnings
   if (len(warnings)>0):
      page += "<h3 style='color: red'>Warnings</h3><p style='color:red'>\n"
      for warning in warnings: page += "%s<br />"%warning
      page += "</p><hr />\n"

   # If we get back from parsing the page then we need to re-issue the edit page
   page += renderMainPageMain(testCursor,cursor,uploadOutcome["partialData"])
   gcdb(testConnection, testCursor)
   gcdb(connection, cursor)

   print page
   return

# Parse the data that we have just got back in our form
def parseFileUploadSubmission(id, form, cursor, warnings, updates):
   import os, stat
   uploadOutcome = {"partialData":{}}
   page = u''
   for key in ["name"]:
      data = form.getfirst(key)
      if (data==None): warnings.append("Failed to supply item %s to edit script!"%key)
      if (data == ""): warnings.append("Supplied empty content for %s: ignoring!"%key)
      else           : uploadOutcome["partialData"][key] = unicode(data)
   id = form.getfirst(key)
   if (id != None and id != -1): uploadOutcome["partialData"]["id"] = id
   if (len(warnings)!=0): return uploadOutcome

   # Insert the file into the database
   cursor.execute("INSERT INTO files (mode) VALUES (?);", (1,))
   id = getFromDB('SELECT id FROM files WHERE mode=? ORDER BY id DESC LIMIT 1;', (1,), cursor)
   fn = buildFileString(id)
   cursor.execute("UPDATE files SET value=? WHERE id=?;", (fn, id))

   # Write the file to disc
   fp = open(fn, "w")
   while (True):
      chunk = form["file"].file.read(100000)
      if not chunk: break
      fp.write(chunk)
   fp.close()

   # Permissions
   os.chmod(fn, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)

   # Insert into instances database
   cursor.execute("INSERT INTO pplversions (name, binary) VALUES (?,?);", (uploadOutcome["partialData"]["name"], id))

   # We have all the required data
   page += "<p>Uploaded file %s sucessfully</p>"%(uploadOutcome["partialData"]["name"])

   uploadOutcome["page"] = page
   return  uploadOutcome



def renderMainPage(id, testCursor, cursor):
   page = renderMainPageHead(id,testCursor,cursor)
   page += renderMainPageMain(testCursor, cursor, None)
   return page

def renderMainPageHead(id,testCursor, cursor):
   page = makePageTop("PyXPlot test interface: Control deck", "index.css", cursor)
   page += "<h2>PyXPlot test interface: Control deck</h2>\n"
   page += "<hr>\n"
   return page

# Produce the html for the main editor page
def renderMainPageMain(testCursor,cursor, partialData):
   page = u''
   nsub = {"i": 0}

   page += renderMainPageAddButtons()

   # Set of boxes for ppl version, most recent first
   for (pplId, pplName) in testCursor.execute("SELECT id, name FROM pplversions ORDER BY id DESC;").fetchall():
      page += renderMainPagePplVersionBox(pplId, pplName, cursor, testCursor)
   return page

def renderMainPageAddButtons():
   page = u""
   page += '<div class="pplVersionBox">\n'
   page += '<div class="pplVersionBoxHead">Tasks<div class="buttonStrip">\n'
   page += '<a class="runall" href="addTest.html">Add new test</a>'
   page += '</div>\n</div>\n</div>\n'
   return page

def renderMainPagePplVersionBox(pplId, pplName, cursor, testCursor):
   page = u""
   page += '<div class="pplVersionBox">\n<div class="pplVersionBoxHead">PyXPlot version %s\n'%(pplName)
   page += '<div class="buttonStrip">'
   for (a,b) in [["all", "all"], ["new","new"], ["fail", "failed"]]:
      page += '<a class="run%s" href="runtests.html?act=run%s_%s">Run %s</a> - '%(a,a,pplId,b)
   page = '%s </div></div>\n <div class="testResults">'%(page[:-3])
   testResults = updateTestResults(pplId, testCursor)
   page += renderTestResults(pplId, testCursor, testResults)
   page += "</div>\n</div>\n"

   return page

# Render test result to the page
def renderTestResults(pplId, cursor, testResults):
   page = u""
   states = cursor.execute("SELECT text FROM teststates ORDER BY id ASC;").fetchall()
   tids = testResults.keys()
   tids.sort()
   for tid in tids:
      i=testResults[tid]
      page += '<div class="test%s" title="test %s - %s - %s"></div>'%(i["state"],tid,i["name"],states[i["state"]-1][0])
      #page += '<div class="test%s" title="test %s - %s - %s">%s</div>'%(i["state"],tid,i["name"],states[i["state"]-1][0],tid)
   return page


# Update test result map table for this instance, returning a complete list of test results at the present moment
def updateTestResults(pplId, cursor):
   allTests = {}
   testMap = {}
   # Obtain current state of test map
   for (tid, state) in cursor.execute("SELECT tid,state FROM insttestmap WHERE (iid=?);", (pplId,)).fetchall():
      testMap[tid] = state
   # Obtain complete list of tests
   for (tid, tname) in cursor.execute("SELECT id, name FROM tests;").fetchall():
      allTests[tid] = {"name": tname}
      if (tid in testMap): allTests[tid]["state"] = testMap[tid]
      else:      # If test not mapped, insert as "not run"
         cursor.execute("INSERT INTO insttestmap (iid, tid, state) VALUES (?,?,?);", (pplId, tid, 1))
         allTests[tid]["state"] = 1
   return allTests


      

mainPage()

