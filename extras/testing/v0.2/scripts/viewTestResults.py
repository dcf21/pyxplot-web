#!/usr/bin/python

import cgi, re, sys, os
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

   # Obtain expected and produced outputs from test
   outputs = cursor.execute("SELECT id, special, filename, mode, diffrules, fid FROM outputs WHERE (tid=?);", (tid,)).fetchall()

   # Obtain result of test
   (istate, sstate)  = cursor.execute("SELECT itm.state, ts.text FROM insttestmap itm LEFT JOIN teststates ts ON (ts.id=itm.state) WHERE (itm.tid=? AND itm.iid=?);", (tid, pplid)).fetchall()[0]
   istate = int(istate)

   textPass = u""
   textFail = u""
   for i in outputs:
      (oid, special, filename, mode, idr, fid) = i
      # Correct location for stdout / stdin
      special = int(special)
      if (special==0):   filename = "stdout"
      elif (special==1): filename = "stderr"

      # Obtain expected output 
      Sobtained = obtainObtainedOutput(tid, oid, pplid, cursor)

      if (Sobtained == None):
        textFail += renderTestOutputNone(filename)
        continue
      Sexpected = obtainExpectedOutput(tid, oid, int(mode), fid, Sobtained, cursor)

      # Apply diff rules
      diffrules = obtainDiffRules(int(idr), special, filename, cursor)
      obtained = convertStringToArray(Sobtained, diffrules)
      expected = convertStringToArray(Sexpected, diffrules)

      # Render test output
      if (expected==obtained): 
         if (len(obtained)==0):
            textPass += renderTestOutputBlank(filename)
            continue
         elif (len(obtained) > 5):
            tmp = obtained[:5]
            tmp.append("etc.")
         else:
            tmp = obtained
         textPass += renderTestOutputPassed(tmp, filename)
      else: 
         textFail += renderTestOutputFailed(obtained, expected, filename)

   (webConnection, webCursor) = openDB()
   page = makePageTop("Test output", "ppltest.css", webCursor)
   page += renderTestResultPage(tid, istate, textFail + textPass, testname, pplName, pplSVN)

   httpHeaders()
   print page

def renderTestResultPage(tid, istate, txt, testname, pplName, pplSVN):
   if (testname == "") : testname = "[no name]"
   if (istate == 1): passfail = "has not yet been run by"
   elif (istate==2): passfail = "passed when run by"
   elif (istate==3): passfail = "failed when run by"
   elif (istate==4): passfail = "crashed when run by"
   elif (istate==5): passfail = "can not be run by"
   else            : passfail = "is in an <b>undefined state</b> with"
   text = u'<div><div>Test <a href="editTest.html?id=%s">%s</a> with id %s %s '%(tid,hilight(testname),tid,passfail)
   text += u' PyXPlot version %s (svn %s).'%(hilight(pplName), hilight(pplSVN))
   if (txt != ""):
      text += u'  See output below</div>\n'
      text += txt
   else:
      text += '</div>\n'
   return text


def hilight(txt): return u'<span class="testOutputHeader">%s</span>'%txt
  


def renderTestOutputFailed(ob, ex, filename):
   while (len(ob) < len(ex)): ob.append("")
   while (len(ex) < len(ob)): ex.append("")
   text = u'<div class="failedTestOutput">Test failed.  Filename: <span class="testOutputHeader">%s</span>\n'%filename
   text += u'<div class="testLineContainer"><div class="failedTestLine">Output produced</div><div class="failedTestLine">Output expected</div></div>\n'
   for i in range(len(ob)):
      o = ob[i]
      e = ex[i]
      text += u'<div class="testLineContainer">'
      if (o==e):
         for j in [o, e]: text += u'<div class="passedTestLine">%s</div>'%j
      else:
         for j in [o, e]: text += u'<div class="failedTestLine">%s</div>'%j
      text += "</div>\n"
   text += "</div>\n"
   return text

def renderTestOutputNone(filename):
   text = u'<div class="failedTestOutput">Test failed.  Filename: <span class="testOutputHeader">%s</span> was not produced</div>\n'%filename
   return text
   
def renderTestOutputBlank(filename):
   text = u'<div class="passedTestOutput">Filename: <span class="testOutputHeader">%s</span> was blank</div>\n'%filename
   return text

def renderTestOutputPassed(content, filename):
   txt = u'<div class="passedTestOutput"><div class="testOutputHeader">%s</div>\n'%filename 
   for i in content:
      txt += u'<div class="passedTestLine">%s</div>\n'%i
   txt += '</div>\n'
   return txt

viewTestResultsPage()
