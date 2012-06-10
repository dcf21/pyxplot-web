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


# Test edit page
def mainPage():

   # Check that the Big Lock has not been taken out
   testBigLock()

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
   #XXX The following function does not, in fact, exist (!)
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

   fn = os.path.join(rootdir(), "cache", fn)
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
   page = None
   # Establish whether a new version of pyxplot is being added
   (lockCon, lockCur) = openaDB("lock.db")
   iLock = int(getFromDB("SELECT COUNT(*) FROM locks WHERE (id=2);", [], lockCur))
   gcdb(lockCon, lockCur)
   if (iLock != 0):
      if (page==None): page = makePageTop("Control deck", "index.css", cursor, '<meta http-equiv="refresh" content="10">\n')  
      page += '<div class="warning">PyXPlot version currently being added.  This page will refresh shortly.</div>\n'
   # Establish whether there are any tests running
   Ntests = int(getFromDB("SELECT COUNT(*) FROM pendingTests;", [], testCursor))
   if (Ntests > 0): 
      if (page==None): page = makePageTop("Control deck", "index.css", cursor, '<meta http-equiv="refresh" content="10">\n')  
      page += '<div class="warning">%s tests are currently running.  This page will refresh shortly.</div>\n'%Ntests
   
   if (page==None): page = makePageTop("Control deck", "index.css", cursor)
   page += renderMainPageMain(testCursor, cursor, None)
   return page


# Produce the html for the main editor page
def renderMainPageMain(testCursor,cursor, partialData):
   page = u''
   nsub = {"i": 0}

   # Button strip along the top of the main page
   page += renderMainPageAddButtons(testCursor)

   # Set of boxes for ppl version, most recent first
   for (pplId, pplName) in testCursor.execute("SELECT id, name FROM pplversions WHERE (hidden != ?) ORDER BY id DESC;", (1,)).fetchall():
      page += renderMainPagePplVersionBox(pplId, pplName, cursor, testCursor)

   # Hidden ppl versions
   bs = []
   for (id, name, svn) in testCursor.execute("SELECT id, name, svn from pplVersions WHERE (hidden=1);").fetchall(): 
      bs.append({"link":"hideVersion.html?pplid=%s&act=show"%id, "text":'%s</a>'%(name)})
   if (len(bs)>0): page += makeButtonStrip("Show hidden versions", bs)

      

   return page

# Button strip along the top of the main page
def renderMainPageAddButtons(cursor):
   # Default button set
   buttonSet = [{"link":"addTest.html", "text":"Add test"},
                {"link":"addNewVersionFromSVN.html", "text":"Add version from svn"},
                {"link":"runtests.html?act=runall_all", "text":"Run all tests"},
                {"link":"runtests.html?act=runfail_all", "text":"Run failed tests", "class":"runfail"},
                {"link":"runtests.html?act=runnew_all", "text":"Run new tests", "class":"runnew"},
                {"link":"takeOutLockOfDoom.html", "text":"Take out BLoD", "class":"runfail"},
                ]
   # Get system states
   for (sid, name, state) in cursor.execute("SELECT * FROM systemStates;").fetchall():
      bclass = "buttOn"
      if (int(state)==0): bclass = "buttOff"
      buttonSet.append({"link":"toggleState.html?id=%s"%(sid), "text":name, "class":bclass})
   return makeButtonStrip("Tasks", buttonSet)

def renderMainPagePplVersionBox(pplId, pplName, cursor, testCursor):
   i = []
   title = u'Version %s\n'%(pplName)
   # Button strip
   for (a,b) in [["all", "all"], ["new","new"], ["fail", "failed"]]: i.append({"class":"run%s"%a, "link":"runtests.html?act=run%s_%s"%(a,pplId), "text":"Run %s"%b})
   i.append({"link":"hideVersion.html?act=hide&pplid=%s"%pplId,"text":"Hide"})
   i.append({"link":"confirmDeny.html?iid=%s&act=del&confirm=1"%pplId, "text":"Delete"})
 
   page = makeButtonStrip(title, i)[:-7]   # -7 strips off </div> at the end
   # Results
   # Obtain results as dictionary (indexed by tid) of dictionaries (keys: name, state)
   testResults = updateTestResults(pplId, testCursor)
   # Split test results up by group
   testResultGroups = splitTestResultsPerGroup(testResults, testCursor)
   for group in testResultGroups: page += renderTestResultsGroup(group["name"], pplId, testCursor, group["tests"])
     
   # page += renderTestResultsGroup("Others", pplId, testCursor, testResults)
   page += "</div>\n"

   return page

# Render test result to the page
def renderTestResultsGroup(groupName, pplId, cursor, testResults):
   # Determine verbosity of output
   verbose = int(getFromDB('SELECT state FROM systemStates WHERE (name=?);', ("Verbose", ), cursor))

   page = u""
   page += '<span class="testResults">'
   page += '<div class="lrel">%s</div>\n'%groupName
   page += '<div class="lrel">'
   states = cursor.execute("SELECT text FROM teststates ORDER BY id ASC;").fetchall()
   tids = testResults.keys()
   tids.sort()
   page += '<ul>'
   if (verbose==0):
      for tid in tids:
         i=testResults[tid]
         page += '<a href="viewtest.html?iid=%s&tid=%s"><div class="test%s" title="test %s - %s - %s"></div></a>'%(pplId,tid,i["state"],tid,i["name"],states[i["state"]-1][0])
   else:
      for tid in tids:
         i=testResults[tid]
         page += '<a href="viewtest.html?iid=%s&tid=%s"><div class="test%sb">test %s - %s - %s</div></a>'%(pplId,tid,i["state"],tid,i["name"],states[i["state"]-1][0])
      # page += '<div class="test%s" title="test %s - %s - %s"></div>'%(i["state"],tid,i["name"],states[i["state"]-1][0])
      # Can't use li as Firefox fails to render it as clickable
      # page += '<a href="viewtest.html?iid=%s&tid=%s"><li class="test%s" title="test %s - %s - %s"> </li></a>'%(pplId,tid,i["state"],tid,i["name"],states[i["state"]-1][0])
      #page += '<div class="test%s" title="test %s - %s - %s">%s</div>'%(i["state"],tid,i["name"],states[i["state"]-1][0],tid)
   page += '</ul>\n'
   page += "</div>\n"
   page += "</span>\n"
   return page


# Update test result map table for this instance, returning a complete list of test results at the present moment
def updateTestResults(pplId, cursor):
   allTests = {}
   testMap = {}
   # Obtain current state of test map
   for (tid, state) in cursor.execute("SELECT tid,state FROM insttestmap WHERE (iid=?);", (pplId,)).fetchall(): testMap[tid] = state
   # Obtain complete list of tests
   for (tid, tname) in cursor.execute("SELECT id, name FROM tests;").fetchall():
      allTests[tid] = {"name": tname}
      if (tid in testMap): allTests[tid]["state"] = testMap[tid]
      else:      # If test not mapped, insert as "not run"
         cursor.execute("INSERT INTO insttestmap (iid, tid, state) VALUES (?,?,?);", (pplId, tid, 1))
         allTests[tid]["state"] = 1
   return allTests


mainPage()

