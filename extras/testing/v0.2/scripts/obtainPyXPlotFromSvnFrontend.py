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

   # Check that the Big Lock has not been taken out
   testBigLock()

   # Run the backend command
   os.system(os.path.join(rootdir(), "scripts", "obtainPyXPlotFromSvn.py") + " >> /home/rpc25/ppltestlog &")

   redirect303("mainPage.html")

main()

