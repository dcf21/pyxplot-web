#!/usr/bin/env python2.6

import cgi, re, sys, os, tempfile
from pysqlite2 import dbapi2 as sqlite
import cgitb

# Stops stdout coercing everything to ascii
reload(sys)
sys.setdefaultencoding('utf-8')

cgitb.enable()

from general import *
from web import *

def viewTestResultsPage():
   # Fire up sqlite
   dbs = openaDB("ppltest.db")
   (connection, cursor) = dbs

   # CGI output
   form = cgi.FieldStorage()

   # Warnings to return to the user
   warnings = []

   # Things to actually insert into the data base
   updates = {}

   pplid = form.getfirst("iid")
   tid = form.getfirst("tid")

   if (pplid==None or tid==None):           gcdbsAndErr(dbs, "Failed to supply the necessary inputs")
   elif (re.match("[0-9]+$", pplid)==None): gcdbsAndErr(dbs, "Failed to supply a valid ppl id")
   elif (re.match("[0-9]+$", tid)==None):   gcdbsAndErr(dbs, "Failed to supply a valid test id")

   # Test name
   testname = getFromDB("SELECT name FROM tests WHERE (id=?);", (tid,), cursor)
   (pplName, pplSVN) = cursor.execute("SELECT name, svn FROM pplVersions WHERE (id=?);", (pplid,)).fetchall()[0]

   pplName += "(%s)"%pplid

   # Obtain expected and produced outputs from test
   outputs = cursor.execute("SELECT id, special, filename, mode, diffrules, fid FROM outputs WHERE (tid=?);", (tid,)).fetchall()

   # Obtain result of test
   (istate, sstate)  = cursor.execute("SELECT itm.state, ts.text FROM insttestmap itm LEFT JOIN teststates ts ON (ts.id=itm.state) WHERE (itm.tid=? AND itm.iid=?);", (tid, pplid)).fetchall()[0]
   istate = int(istate)

   # XXX OLD # Special case: if there are neither inputs nor outputs use python to generate the expected answer
   # XXX OLD if (len(outputs)==0):
   # XXX OLD    Ninputs = int(getFromDB("SELECT COUNT(*) FROM inputs WHERE (tid=?);", (tid,), cursor))
   # XXX OLD    if (Ninputs == 0): 
   # XXX OLD       outputs = [[-1, 0, "", 2, None, None]]
   # XXX OLD       script = getFromDB("SELECT script FROM tests WHERE (id=?);", (tid,), cursor)

   textPass = u""
   textFail = u""
   script = getFromDB("SELECT script FROM tests WHERE (id=?);", (tid,), cursor)
   for i in outputs:
      (oid, special, filename, mode, idr, fid) = i
      mode = int(mode)
      # Correct location for stdout / stdin
      special = int(special)
      if (special==0):   filename = "stdout"
      elif (special==1): filename = "stderr"


      Sobtained = obtainObtainedOutput(tid, oid, pplid, cursor)
      if (Sobtained == None):
        if (mode == 3):
           Sobtained = ""
        else:
           textFail += renderTestOutputNone(filename)
           continue

      # Obtain expected output 
      if (mode == 2):
         tempdir = tempfile.mkdtemp()
         Sexpected = obtainExpectedOutputFromScript(script, tempdir)
      elif (mode == 3):
         Sexpected = ""
      else:
         Sexpected = obtainExpectedOutput(tid, oid, int(mode), fid, Sobtained, cursor)

      diffrules = obtainDiffRules(int(idr), special, filename, cursor)

      # Apply diff rules and test output
      (passFail, details) = hasMyTestPassed(Sobtained, Sexpected, diffrules)

      if (passFail):
         if (len(details)==0):
            textPass += renderTestOutputBlank(filename)
            continue
         elif (len(details) > 5 and special != 1):
            tmp = details[:5]
            tmp.append([1, "etc.", None])
         else:
            tmp = details
         textPass += renderTestOutputPassed(tmp, filename)
      else: 
         textFail += renderTestOutputFailed(details, filename)
         

      # obtained = convertStringToArray(Sobtained, diffrules)
      # expected = convertStringToArray(Sexpected, diffrules)

   (webConnection, webCursor) = openDB()
   page = makePageTop("Test output", "ppltest.css", webCursor)
   page += renderTestResultPage(tid, istate, textFail + textPass, testname, pplName, pplSVN, pplid)

   httpHeaders()
   print page

def renderTestResultPage(tid, istate, txt, testname, pplName, pplSVN, pplId):
   if (testname == "") : testname = "[no name]"
   if (istate == 1): passfail = "has not yet been run by"
   elif (istate==2): passfail = "passed when run by"
   elif (istate==3): passfail = "failed when run by"
   elif (istate==4): passfail = "crashed when run by"
   elif (istate==5): passfail = "can not be run by"
   else            : passfail = "is in an <b>undefined state</b> with"
   editLink = u'editTest.html?id=%s'%tid
   text = makeButtonStrip("Tasks", [{"link":editLink, "text":"Edit"},
                           {"link":"confirmDeny.html?tid=%s&act=del"%tid, "text":"Delete"},
                           {"link":"runtests.html?act=run%s_%s"%(tid,pplId), "text":"Re-run"},
                           {"link":"setTestState.html?act=passed&pplid=%s&tid=%s"%(pplId,tid), "text":"Mark as passed"}])
   text += u'<div><div>Test <a href="%s">%s</a> with id %s %s '%(editLink,hilight(testname),tid,passfail)
   text += u' PyXPlot version %s (svn %s).'%(hilight(pplName), hilight(pplSVN))
   if (txt != ""):
      text += u'  See output below</div>\n'
      text += txt
   else:
      text += '</div>\n'
   return text


def hilight(txt): return u'<span class="testOutputHeader">%s</span>'%txt

def renderTestOutputFailed(details, filename):
   text = u'<div class="failedTestOutput">File <span class="testOutputHeader">%s</span> contained the <a href="#firstBug">incorrect content</a>\n'%filename
   text += u'<div class="testLineContainer"><div class="testLineIndex">&nbsp;</div><div class="passedTestLine">Output produced</div><div class="passedTestLine">Output expected</div></div>\n'
   i = 1
   foundFirstBug = False
   for (t, o, e) in details:
      text += u'<div class="testLineContainer"><div class="testLineIndex">%s</div>'%i
      if (t==2):
         for j in [o, ""]: text += u'<div class="passedTestLine">%s</div>'%j
      elif (t==1):
         for j in [o, o]: text += u'<div class="passedTestLine">%s</div>'%j
      else:
         if (not foundFirstBug):
            text += u'<a name="firstBug" />'
            foundFirstBug = True
         for j in [o, e]: text += u'<div class="failedTestLine">%s</div>'%j
      text += "</div>\n"
      i += 1
   text += "</div>\n"
   return text


def renderTestOutputNone(filename):
   text = u'<div class="failedTestOutput">File <span class="testOutputHeader">%s</span> was not produced</div>\n'%filename
   return text
   
def renderTestOutputBlank(filename):
   text = u'<div class="passedTestOutput">File <span class="testOutputHeader">%s</span> was blank</div>\n'%filename
   return text



def renderTestOutputPassed(content, filename):
   txt = u'<div class="passedTestOutput">File <span class="testOutputHeader">%s</span> correctly contained the following content\n'%filename 
   for i in content:
      txt += u'<div class="testLineContainer"><div class="passedTestLine">%s</div><div class="passedTestLine">%s</div></div>\n'%(i[1],i[2])
   txt += '</div>\n'
   return txt

viewTestResultsPage()
