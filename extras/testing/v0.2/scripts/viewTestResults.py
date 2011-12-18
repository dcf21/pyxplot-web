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

   # Obtain expected and produced outputs from test
   outputs = cursor.execute("SELECT id, special, filename, mode, diffrules, fid FROM outputs WHERE (tid=?);", (tid,)).fetchall()

   passed = True
   textPass = u""
   textFail = u""
   for i in outputs:
      (oid, special, filename, mode, idr, fid) = i
      # Correct location for stdout / stdin
      special = int(special)
      if (special==0):   filename = "stdout"
      elif (special==1): filename = "stderr"
      else:              filename = os.path.join(options["testdir"],filename)

      # Obtain expected output 
      Sexpected = obtainExpectedOutput(tid, oid, int(mode), fid, Sobtained, cursor)
      Sobtained = obtainObtainedOutput(tid, oid, pplid, cursor)

      # Apply diff rules
      diffrules = obtainDiffRules(int(idr), special, filename, cursor)
      obtained = convertStringToArray(Sobtained, diffrules)
      expected = convertStringToArray(Sexpected, diffrules)

      # Render test output
      if (Sexpected==Sobtained): textPass += renderTestOutputPassed(Sobtained, filename)
      else: 
         textFail += renderTestOutputFailed(obtained, expected, filename)
         passed = False

   page = makePageTop("PyXPlot test output", "ppltest.css", webCursor)
   if (passed): page += renderPagePassed(textPass)
   else:        page += renderPageFailed(textPass, textFail)

   print page

def renderTestOutputFailed(ob, ex, filename):
   while (len(ob) < len(ex)): ob.append("")
   while (len(ex) < len(ob)): ex.append("")
   text = u'<div class="failedTestOutput"><div class="testOutputHeader">%s</div>\n'%filename
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

def renderTestOutputPassed(s, filename):
   return u'<div class="passedTestOutput"><div class="testOutputHeader">%s</div>\n'%filename + s + '</div>\n'

viewTestResultsPage()
