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
   dbs = openaDB("ppltest.db")
   (connection, cursor) = dbs

   # CGI output
   form = cgi.FieldStorage()

   # Warnings to return to the user
   warnings = []

   # Parsed parameters
   params = {}

   # Parse the passed parameters
   for (field, check) in [["act", "[a-z]+$"], 
                          ["tid", "[0-9]+$"],
                          ["confirm", "[0-9]$"]]:
      action = form.getfirst(field)
      if (action!=None):
         if (re.match(check, action)):
            params[field] = action

   # Check whether the user has already confirmed
   if (not "confirm" in params):
      gcdb(connection, cursor)
      issueConfirmDenyPage(params)
      return

   # Check whether we can find anything useful to do
   if (not "act" in params):
      gcdbsAndErr(dbs, "You need to tell me what to do!")

   # Instructions are to delete something
   if (params["act"]=="del"):
      if ("tid" in params):
         deleteTest(int(params["tid"]), cursor)
         gcdb(connection, cursor)
         redirect303("mainPage.html")
      else:
         gcdbsAndErr(dbs, "You need to tell me which test to delete!")
   else:
      gcdbsAndErr(dbs, "You need to tell me what to do!")
      
def issueConfirmDenyPage(params):
   # Parse the params (again)
   verb = None
   noun = None
   if (params["act"]=="del"):
      verb = "delete"
      if ("tid" in params):
         noun = "test id %s"%(params["tid"])
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
   page += makeButtonStrip([{"link":url, "text":"Continue"},
                            {"link":"mainPage.html", "text":"Cancel"}])

   httpHeaders()
   print page
main()


