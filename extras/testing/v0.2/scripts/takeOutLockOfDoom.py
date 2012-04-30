#!/usr/bin/env python2.6

import cgi, re, sys, os, os.path, shutil
from pysqlite2 import dbapi2 as sqlite

from general import *
from web import redirect303, makeHttpHeaders, errPage, headlessErrPage

def main():
   username = os.environ["REMOTE_USER"]

   # Firstly take the BLoD out to prevent any further check-ins
   if (not takeOutLock(3, username)):
      errPage("Failed to take the BLoD out!")
      exit()

   # Update svn
   import pysvn
   cl = pysvn.Client()

   # Comit any changes to the data base 
   dbDir = os.path.join(rootdir(), "dbs")
   cl.checkin([dbDir], "Automatic checkin of database by %s"%username)

   redirect303("mainPage.html")

   return
      
      
main()
