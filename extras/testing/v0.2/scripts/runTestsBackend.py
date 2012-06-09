#!/usr/bin/env python2.6

# This is a script to run tests for the pyxplot test system

# Original version rpc25, Sun Nov  8 13:36:29 CET 2009
# New version rpc25, Thu Dec  1 19:03:11 GMT 2011

import sys, os, re, subprocess
from general import *

options = {'pyxplot'       : "pyxplot8",  # Default config goes here 
           'run'           : [ ],
           'compare'       : [ ],
           'version'       : "current",
           'compareversion': "current",
           'scriptdir'     : ".",
           'workdir'       : "."}

instanceCache = {}


# Main routine
def runTestsBackend(options):
   # Initial setup
   log("Test system: initialising")
   initTestBackend(options)

   # Take out the lock on running tests
   if (not takeOutTestRunLock()): 
      log(" Failed to take out test run lock; aborting")
      return
   else:
      log(" Sucesfully aquired test lock")

   # Loop, carring out tests
   while (True):
      testsToRun = getPendingTests()
      log(" Retrieved %s tests"%(len(testsToRun)))
      if (len(testsToRun)==0): break
      for test in testsToRun: 
         log(" Running test iid=%s tid=%s"%(test[0],test[1]))
         result = runTest(test, options)
         log("  Run test with result %s"%result)
         removeFromPendingTests(test)

   # Finished: give the lock back again
   log(" About to return test lock")
   releaseTestRunLock()
   log("Sucesfully completed testing PyXPlot")
   log("")
   return

# Run a test
def runTest(test, options):
   import os
   import shutil
   global instanceCache
   # Obtain all the necessary details about the test
   (iid, tid) = test

   # Test database
   (connection, cursor) = openaDB("ppltest.db")

   # Global system state
   systemState = {}
   temp = cursor.execute("SELECT * FROM systemStates;").fetchall()
   for i in temp: systemState[i[1]] = int(i[2])

   # Locate the ppl instance
   if (not iid in instanceCache):
      (instMode, instLoc) = cursor.execute("SELECT f.mode, f.value FROM files f LEFT JOIN pplversions pv ON (pv.binary=f.id) WHERE (pv.id=?);", (iid,)).fetchall()[0]
      assert(int(instMode)==1)  # PyXPlot binary must be a file on disc
      instanceCache[iid] = os.path.join(rootdir(), "cache", instLoc)
   options["pyxplot"] = instanceCache[iid]

   # Make a directory for the test
   testname = "test_%s_%s"%(iid,tid)
   options["testdir"] = os.path.join(options["workdir"], testname)
   madeTestDir = False
   while (not madeTestDir):
      try: 
         os.mkdir(options["testdir"])
         madeTestDir = True
      except:
         options["testdir"] += "X"

   # Grab everything that we need to know about the test in order to run it
   (tMode, script) = cursor.execute("SELECT mode, script FROM tests WHERE (id=?);", (tid,)).fetchall()[0]
   inputs = cursor.execute("SELECT i.special, i.filename, f.mode, f.value FROM inputs i LEFT JOIN files f ON (f.id=i.fid) WHERE (i.tid=?);", (tid,)).fetchall()

   # Close the database connection as the next bit may take some time!
   gcdb(connection, cursor)

   # Make all the apropriate inputs
   options["stdin"] = None
   for i in inputs:
      (special, filename, mode) = i[0:3]
      fnout = os.path.join(options["testdir"], filename)
      if (int(special)==0):    # If this is data for stdin, store it apropriately
         if (int(mode)==0): options["stdin"] = i[3]
         else:
            fin = open(i[3], "r")
            options["stdin"] = fin.read()
            fin.close()
      else:                    # Write file into position
         if (int(mode)==0):
            fout = open(fnout, "w")
            fout.write(i[3])
            fout.close()
         else:
            shutil.copyfile(i[3], fnout)


   # Write the script into a file
   scriptfile = os.path.join(options["testdir"], "script.ppl")
   fout = open(scriptfile, "w")
   fout.write(script)
   fout.close()

   # Run pyxplot
   valgrind = u""
   if (systemState["Valgrind"] == 1): valgrind = " valgrind --log-file=valgrind.out "
   outfile = os.path.join(options["workdir"], "%s.stdout"%testname)
   errfile = os.path.join(options["workdir"], "%s.stderr"%testname)
   os.system("cd %s ; DISPLAY= %s %s script.ppl > %s 2> %s"%(options["testdir"],valgrind,options["pyxplot"],outfile,errfile))

   # Re-open test database
   (connection, cursor) = openaDB("ppltest.db")

   # Obtain details of the required outputs
   outputs = cursor.execute("SELECT id, special, filename, mode, diffrules, fid FROM outputs WHERE (tid=?);", (tid,)).fetchall()
   # outputs = cursor.execute("SELECT o.id, o.special, o.filename, o.mode, o.diffrules, f.mode, f.value FROM outputs o LEFT JOIN files f ON (f.id=o.fid) WHERE (o.tid=?);", (tid,)).fetchall()

   # Special output to test stderr when test_mode == 2
   if (int(tMode)==2): 
      outputs.append([-1, 1, "", 99, 1, -1])
      log("  Requiring an error to occur")

   # Capture Valgrind output
   if (systemState["Valgrind"]==1):
      fp = open(os.path.join(options["testdir"], "valgrind.out"), "r")
      valgrindOutput = fp.read()
      fp.close()
   else:
      valgrindOutput = None

   # Capture the outputs
   passed = True
   for i in outputs:
      (oid, special, filename, mode, idr, fid) = i
      # Correct location for stdout / stdin
      special = int(special)
      if (special==0):   filename = outfile
      elif (special==1): filename = errfile
      else:              filename = os.path.join(options["testdir"],filename)
      try: 
         fp = open(filename, "r")
         Sobtained = fp.read()
         fp.close()
      except:    # The test did not produce this required output
         log("  Test failed to produce output %s"%filename)
         passed = False
         Sobtained = None
         # Remove any previous output from database
         cursor.execute("DELETE FROM instoutmap WHERE (iid=? AND oid=?);", (iid, oid))
         continue

      # Expected output
      if (mode==99):    # MAGIC INTEGER VALUE to ensure that stderr is non-blank
         if (len(Sobtained)==0):
            passed = False
            log("  Test failed to produce output on stderr")
         continue
      if (mode==3): 
         Sexpected = u""
      # Obtain expected output 
      elif (mode == 2):
         log("  Obtaining expected output from python")
         Sexpected = obtainExpectedOutputFromScript(script, options["testdir"])
         # log("  Expected %s"%(Sexpected))
         # log("  Obtained %s"%(Sobtained))
      else:
         Sexpected = obtainExpectedOutput(tid, oid, int(mode), fid, Sobtained, cursor)

      diffrules = obtainDiffRules(int(idr), int(special), filename, cursor)
      # obtained = convertStringToArray(Sobtained, diffrules)
      # expected = convertStringToArray(Sexpected, diffrules)
      (passFail,details) = hasMyTestPassed(Sobtained, Sexpected, diffrules)
      if (not passFail):
         passed = False
         log("  Failed on output %s"%oid)
      # if (obtained != expected): 
      #   passed = False
      #   log("  Obtained output %s whilst expecting %s"%(obtained,expected))

      # Insert output into files data base
      fid = getPossibleItemFromDB("SELECT fid FROM instoutmap WHERE (iid=? AND oid=?);", (iid, oid), cursor)
      if (fid==None):
         fid = insertIntoFileDB(Sobtained, cursor)
         cursor.execute("INSERT INTO instoutmap (iid, oid, fid) VALUES (?,?,?);", (iid, oid, fid))
      else:
         cursor.execute("UPDATE files SET mode=?, value=? WHERE id=?;", (0, Sobtained, fid))

   # Store and test the output from valgrind
   cursor.execute("UPDATE insttestmap SET valgrind=? WHERE (iid=? AND tid=?);", (valgrindOutput, iid, tid))
   if (valgrindOutput != None):
      (passFail, details) = isMyValgrindOutputWorrying(valgrindOutput)
      if (not passFail):
         passed = False
         log("  Failed on valgrind output")


   state = getPossibleItemFromDB("SELECT state FROM insttestmap WHERE (iid=? AND tid=?);", (iid, tid), cursor)
   if (state==None): cursor.execute("INSERT INTO insttestmap (iid,tid,state) VALUES (?,?,?);", (iid, tid, 3-passed))
   else:             cursor.execute("UPDATE insttestmap SET state=? WHERE (iid=? AND tid=?);", (3-passed, iid, tid))

   # Write out the changes to the DB
   gcdb(connection, cursor)

   return passed
      



# Remove a completed test from the list of pending tests
def removeFromPendingTests(test):
   (connection, cursor) = openaDB("ppltest.db")
   pendingTests = cursor.execute("DELETE FROM pendingTests WHERE (iid=? AND tid=?);", (test[0], test[1])).fetchall()
   log(" Removed test")
   gcdb(connection, cursor)

# Obtain a list of pending tests from the database
def getPendingTests():
   (connection, cursor) = openaDB("ppltest.db")
   pendingTests = cursor.execute("SELECT iid, tid FROM pendingTests;").fetchall()
   gcdb(connection, cursor)
   return pendingTests

# Take out lock on running tests
def takeOutTestRunLock():
   return takeOutLock(1)

# Release lock on running tests
def releaseTestRunLock():
   releaseLock(1)
   return

# Initialise
def initTestBackend(options):
   import tempfile
   options["workdir"] = tempfile.mkdtemp() + '/'
   return

runTestsBackend(options)
