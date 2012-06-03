#!/usr/bin/env python2.6

import sys, os, re

from pysqlite2 import dbapi2 as sqlite

from general import *

def viewTestsRemotely():
   
   # Fire up sqlite
   dbs = openaDB("ppltest.db")
   (connection, cursor) = dbs

   # Warnings to return to the user
   warnings = []

   # Obtain version number
   (pplId, pplName) = cursor.execute("SELECT id, name FROM pplversions WHERE (hidden != ?) ORDER BY id DESC LIMIT 1;", (1,)).fetchall()[0]
   # pplId = getFromDB("SELECT id FROM pplversions ORDER BY id DESC LIMIT ?;", (1,), cursor)

   # View all the tests
   testResults = queryTestResults(pplId, cursor)
   testResultGroups = splitTestResultsPerGroup(testResults, cursor)

   # Set of possible test states
   states = cursor.execute("SELECT text FROM teststates ORDER BY id ASC;").fetchall()

   # View test output
   for group in testResultGroups: 
      print 
      print "Test group %s"%group["name"]
      testResults = group["tests"]
      tids = testResults.keys()
      tids.sort()
      for tid in tids:
         i=testResults[tid]
         if (i["state"]==2): result = ".     "
         elif (i["state"]==1): result = "N     "
         else: result = states[i["state"]-1][0]
         print "%s test %s (%s)"%(result, tid,i["name"])
 
      # page += renderTestResultsGroup(group["name"], pplId, cursor, group["tests"])

   gcdb(connection, cursor)

# Update test result map table for this instance, returning a complete list of test results at the present moment
def queryTestResults(pplId, cursor):
   allTests = {}
   testMap = {}
   # Obtain current state of test map
   for (tid, state) in cursor.execute("SELECT tid,state FROM insttestmap WHERE (iid=?);", (pplId,)).fetchall(): testMap[tid] = state
   # Obtain complete list of tests
   for (tid, tname) in cursor.execute("SELECT id, name FROM tests;").fetchall():
      allTests[tid] = {"name": tname}
      if (tid in testMap): allTests[tid]["state"] = testMap[tid]
      else:      # If test not mapped, insert as "not run"
         allTests[tid]["state"] = 1
   return allTests


viewTestsRemotely()

