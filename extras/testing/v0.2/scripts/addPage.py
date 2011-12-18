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

httpHeaders()

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

   addNewTest(d, cursor)

   tid = getFromDB('SELECT id FROM tests ORDER BY id DESC LIMIT ?;', (1,), cursor)

   redirect303("editTest.html?id=%s\n"%tid)

   return

addTestRedirect()
