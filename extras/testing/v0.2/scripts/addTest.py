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

# Test addition script
def addTestRedirect():
   (connection, cursor) = openaDB("ppltest.db")

   d = {}

   # CGI output
   form = cgi.FieldStorage()

   name = form.getfirst("name")
   if (name != None and re.match("^[a-zA-Z ]*$", name)):
      d["name"] = name

   script = form.getfirst("script")
   if (script != None):
      d["script"] = script

   tid = addNewTest(d, cursor)

   gcdb(connection, cursor)

   redirect303("editTest.html?id=%s"%tid)

   return

addTestRedirect()
