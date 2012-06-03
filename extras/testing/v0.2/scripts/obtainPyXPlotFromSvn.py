#!/usr/bin/env python2.6

import cgi, re, sys, os, os.path, shutil
from pysqlite2 import dbapi2 as sqlite

from general import *

# Import a PyXPlot version from the repositary and insert it into the database

workingCopy = "/societies/pyxplot/code/pyxplot9"

def main():
   global workingCopy

   log ("Attempting to obtain PyXPlot from svn")

   if (takeOutLock(2)!=True):
      log("Failed to take out lock")
      return
   else:
      log(" Sucessfully obtained lock")

   import pysvn
   cl = pysvn.Client()

   # Update the working copy to the latest version
   log(" Updating the working copy")
   cl.update(workingCopy)
   log("  ...done")

   # Obtain the revision number of the latest version
   Nsvn = cl.info(workingCopy).revision.number

   # Obtain the revision number of the latest version in the db
   (connection, cursor) = openaDB("ppltest.db")
   NsvnDB = getFromDB("SELECT svn FROM pplVersions ORDER BY svn DESC LIMIT 1;", [], cursor)
   # Deal with there being no svn versions in the DB
   if (NsvnDB == None): NsvnDB = -1
   if (int(NsvnDB) >= int(Nsvn)):
      log(" Latest version %s already in database (DB version %s)"%(Nsvn,NsvnDB))
      finish(connection, cursor)
      return
   # The next step will be slooow so be a good boy and give the database back
   gcdb(connection, cursor)

   log(" Building pyxplot")

   os.system("cd %s ; ./configure > /dev/null && nice -15 make -j 5 > /dev/null"%workingCopy)
   log("  ...done")

   pplBinary = os.path.join(workingCopy, "bin", "pyxplot")

   # Insert a record for this version into the files database
   (connection, cursor) = openaDB("ppltest.db")
   insertNewPyxplotVersionIntoDatabase(pplBinary, Nsvn, cursor)
   log(" Success!")

   finish(connection, cursor)
   return
      
      
def finish(con, cur):
   gcdb(con, cur)
   releaseLock(2)
   log("Finished up")
   return

main()
