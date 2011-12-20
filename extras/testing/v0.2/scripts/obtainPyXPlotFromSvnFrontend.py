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

# Test edit page
def main():

   # Run the tests
   os.system(os.path.join(workdir(), "scripts", "obtainPyXPlotFromSvn.py") + " >> /home/rpc25/ppltestlog &")

   redirect303("mainPage.html")

main()

