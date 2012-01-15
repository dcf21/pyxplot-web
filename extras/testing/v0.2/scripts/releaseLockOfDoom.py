#!/usr/bin/env python2.6

import cgi, re, sys, os, os.path, shutil
from pysqlite2 import dbapi2 as sqlite

from general import *
from web import redirect303, makeHttpHeaders

def main():
   # Update svn
   import pysvn
   cl = pysvn.Client()

   # Update the working copy to the latest version
   dbDir = os.path.join(rootdir(), "dbs")
   cl.update(dbDir)

   # Release the lock
   releaseLock(3)

   redirect303("mainPage.html")

   return
      
      
main()
