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
def main():

   # Fire up sqlite

   # CGI output
   form = cgi.FieldStorage()

   # Warnings to return to the user
   warnings = []

   # Parsed parameters
   params = {}

   # Parse the passed parameters
   for (field, check) in [["act", "[a-z]+$"], 
                          ["tid", "[0-9]+$"],
                          ["iid", "[0-9]+$"],
                          ["confirm", "[0-9]$"]]:
      action = form.getfirst(field)
      if (action!=None):
         if (re.match(check, action)):
            params[field] = action

   # Check whether the user has already confirmed
   if (not "confirm" in params):
      issueConfirmDenyPage(params)
      return

   # Check whether we can find anything useful to do
   if (not "act" in params):
      errPage("You need to tell me what to do!")

   # Instructions are to delete something
   if (params["act"]=="del"):
      if ("tid" in params):
         (connection, cursor) = openaDB("ppltest.db")
         deleteTest(int(params["tid"]), cursor)
         gcdb(connection, cursor)
         redirect303("mainPage.html")
      elif ("iid" in params):
         deleteVersion(params["iid"])
         redirect303("mainPage.html")
      else:
         errPage("You need to tell me which test to delete!")
   else:
      errPage("You need to tell me what to do!")
      
def issueConfirmDenyPage(params):
   # Parse the params (again)
   verb = None
   noun = None
   if (params["act"]=="del"):
      verb = "delete"
      if ("tid" in params):
         noun = "test id %s"%(params["tid"])
      elif ("iid" in params):
         noun = "PyXPlot version id %s"%(params["iid"])
      else:
         errPage("Confused about what to delete")
   else:
      errPage("Confused")
   (connection, cursor) = openaDB("webstuff.db")
   page = makePageTop("Yea or Nea?", "ppltest.css", cursor)
   page += u"<p>Please confirm that you would like to %s %s</p>"%(verb, noun)

   # Build new URL
   url = "confirmDeny.html?confirm=1"
   for i in params.keys(): url += "&%s=%s"%(i,params[i])
   page += makeButtonStrip("Tasks",[{"link":url, "text":"Continue"},
                                    {"link":"mainPage.html", "text":"Cancel"}])

   httpHeaders()
   print page
   gcdb(connection, cursor)
main()


