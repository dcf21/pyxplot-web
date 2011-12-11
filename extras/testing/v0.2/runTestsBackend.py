#!/usr/bin/python

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
   initTestBackend(options)

   # Take out the lock on running tests
   if (not takeOutTestRunLock()): 
      log("Failed to take out test run lock; aborting")
      return

   # Loop, carring out tests
   while (True):
      testsToRun = getPendingTests()
      log("Retrieved %s tests"%(len(testsToRun)))
      if (len(testsToRun)==0): break
      for test in testsToRun: 
         result = runTest(test, options)
         log("Run test with result %s"%result)
         removeFromPendingTests(test)

   # Finished: give the lock back again
   releaseTestRunLock()
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

   # Locate the ppl instance
   if (not iid in instanceCache):
      (instMode, instLoc) = cursor.execute("SELECT f.mode, f.value FROM files f LEFT JOIN pplversions pv ON (pv.binary=f.id) WHERE (pv.id=?);", (iid,)).fetchall()[0]
      assert(int(instMode)==1)  # PyXPlot binary must be a file on disc
      instanceCache[iid] = instLoc
   options["pyxplot"] = instanceCache[iid]

   # Make a directory for the test
   testname = "test_%s_%s"%(iid,tid)
   options["testdir"] = os.path.join(options["workdir"], testname)
   os.mkdir(options["testdir"])

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
   outfile = os.path.join(options["workdir"], "%s.stdout"%testname)
   errfile = os.path.join(options["workdir"], "%s.stderr"%testname)
   os.system("cd %s ; DISPLAY= %s script.ppl > %s 2> %s"%(options["testdir"],options["pyxplot"],outfile,errfile))

   # Re-open test database
   (connection, cursor) = openaDB("ppltest.db")

   # Obtain details of the required outputs
   outputs = cursor.execute("SELECT id, special, filename, mode, diffrules, fid FROM outputs WHERE (tid=?);", (tid,)).fetchall()
   # outputs = cursor.execute("SELECT o.id, o.special, o.filename, o.mode, o.diffrules, f.mode, f.value FROM outputs o LEFT JOIN files f ON (f.id=o.fid) WHERE (o.tid=?);", (tid,)).fetchall()

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
         log("Test failed to produce output %s"%filename)
         passed = False
         Sobtained = ""

      # Obtain expected output 
      Sexpected = obtainExpectedOutput(tid, oid, int(mode), fid, Sobtained, cursor)

      # Diff rules
      idr = int(idr)
      if (idr==0): diffrules = []
      elif (idr==-1):    # Default diff rules
         if (special!=2):
            diffrules = []
         else:
            temp = re.search(r"\.[a-zA-Z0-9]+$", filename)
            if (temp==None):
               log("Warning: failed to detect file type for %s; falling back to no diff rules"%filename)
               diffrules = []
            else:
               ending = temp.group(0)[1:]
               temp2 = getPossibleItemFromDB("SELECT rules FROM diffrules WHERE (extension=?);", (ending,), cursor)
               if (temp2==None): 
                  log("Warning: no diff rules found for ending %s"%(ending))
                  diffrules = []
               else: 
                  diffrules = temp2.split("\n")
      else:
         temp = getPossibleItemFromDB("SELECT rules FROM diffrules WHERE (id=?);", (idr,), cursor)
         if (temp==None):
            log("Warning: diff rules set %s not found"%idr)
            diffrules = []
         else:
            diffrules = temp.split("\n")
                  


      # Check this output for correctness
      # log("Testing output %s against %s"%(Sobtained,Sexpected))

      obtained = convertStringToArray(Sobtained, diffrules)
      expected = convertStringToArray(Sexpected, diffrules)
      if (obtained != expected): passed = False

      # Insert output into files data base
      fid = getPossibleItemFromDB("SELECT fid FROM instoutmap WHERE (iid=? AND oid=?);", (iid, oid), cursor)
      if (fid==None):
         fid = insertIntoFileDB(Sobtained, cursor)
         cursor.execute("INSERT INTO instoutmap (iid, oid, fid) VALUES (?,?,?);", (iid, oid, fid))
      else:
         cursor.execute("UPDATE files SET mode=?, value=? WHERE id=?;", (0, Sobtained, fid))

   state = getPossibleItemFromDB("SELECT state FROM insttestmap WHERE (iid=? AND tid=?);", (iid, tid), cursor)
   if (state==None): cursor.execute("INSERT INTO insttestmap (iid,tid,state) VALUES (?,?,?);", (iid, tid, 3-passed))
   else:             cursor.execute("UPDATE insttestmap SET state=? WHERE (iid=? AND tid=?);", (3-passed, iid, tid))

   # Write out the changes to the DB
   gcdb(connection, cursor)

   return passed
      

def convertStringToArray(string, diffrules):
   # Convert to arrays and prepare to diff
   string.replace("\r\n", "\n")    # Windows
   l = []
   for i in string.split("\n"):
      keep = True
      # Check against the diff rules
      for dr in diffrules:
         if re.search(dr, i):
            keep = False
            break
      if (keep): l.append(i)
   while (len(l)>0 and l[-1]==""): l.pop()
   return l



# Obtain the output expected from a test
def obtainExpectedOutput(tid, oid, mode, fid, Sobtained, cursor):
   # mode=0 => Compare against previous, 1=> Compare against stored value
   if (mode==0):
      previous = cursor.execute("SELECT iom.fid FROM instoutmap iom LEFT JOIN insttestmap itm ON (iom.iid=itm.iid) WHERE (itm.tid=? AND iom.oid=? AND itm.state=?);", (tid, oid, 2)).fetchall()
      if (len(previous)==0): 
         log("No previous values found for output %s; taking input as canon"%oid)
         return Sobtained
      fid = previous[-1][0]
      log("fid for previous value of output %s is %s"%(oid,fid))
   fdetails = cursor.execute("SELECT mode, value FROM files WHERE (id=?);", (fid,)).fetchall()
   if (len(fdetails)==0):
      log("Stored file %s appears to be missing!"%fid)
      return ""
   (fmode, fval) = fdetails[0]
   return obtainFileContents(fmode,fval)



def obtainFileContents(mode, value):
   text = u""
   if (int(mode)==0): return value
   else:
      fp = open(value, "r")
      try: text = fp.read()
      except:
         fp.close()
         raise
      fp.close()
      return text


# Remove a completed test from the list of pending tests
def removeFromPendingTests(test):
   (connection, cursor) = openaDB("ppltest.db")
   pendingTests = cursor.execute("DELETE FROM pendingTests WHERE (iid=? AND tid=?);", (test[0], test[1])).fetchall()
   log("Removed test")
   gcdb(connection, cursor)

# Obtain a list of pending tests from the database
def getPendingTests():
   (connection, cursor) = openaDB("ppltest.db")
   pendingTests = cursor.execute("SELECT iid, tid FROM pendingTests;").fetchall()
   log("Retrieved tests")
   gcdb(connection, cursor)
   return pendingTests

# Take out lock on running tests
def takeOutTestRunLock():
   (connection, cursor) = openaDB("lock.db")
   N = getFromDB("SELECT COUNT(*) FROM locks WHERE (id=?);", (1,), cursor) 
   if (N != 0): return False
   cursor.execute("INSERT INTO locks (id) VALUES (?);", (1,))
   gcdb(connection, cursor)
   return True

# Release lock on running tests
def releaseTestRunLock():
   (connection, cursor) = openaDB("lock.db")
   cursor.execute("DELETE FROM locks WHERE (id=?);", (1,))
   gcdb(connection, cursor)
   return

# Initialise
def initTestBackend(options):
   import tempfile
   options["workdir"] = tempfile.mkdtemp() + '/'
   return

# Logging
def log(string):
   print string

log("Hellllooooooo")
runTestsBackend(options)
