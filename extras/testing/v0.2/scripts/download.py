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

def downloadPage():
   testBigLock()

   # Fire up sqlite
   dbs = openaDB("ppltest.db")
   (connection, cursor) = dbs

   # CGI output
   form = cgi.FieldStorage()

   oid = form.getfirst("oid")
   pplid = form.getfirst("pplid")
   
   if (pplid==None or oid==None):           gcdbsAndErr(dbs, "Failed to supply the necessary inputs")
   elif (re.match("[0-9]+$", pplid)==None): gcdbsAndErr(dbs, "Failed to supply a valid ppl id")
   elif (re.match("[0-9]+$", oid)==None):   gcdbsAndErr(dbs, "Failed to supply a valid output id")

   details = cursor.execute("SELECT tid, special, filename, mode, fid FROM outputs WHERE (id=?);", (oid,)).fetchall()
   if (len(details)==0): errPage("That output does not exist")
   (tid, special, filename, mode, fid) = details[0]

   # Filename to write file out to
   outfn = "%s_%s_%s"%(oid,pplid,filename)
   outfp = open(os.path.join(rootdir(), "downloads", outfn), "w")


   # Write out obtained output
   Sobtained = obtainObtainedOutput(tid, oid, pplid, cursor)
   outfp.write(Sobtained)
   outfp.close()

   redirect303("downloads/%s"%outfn)

downloadPage()



     

