#!/usr/bin/python

# This is a script to test different pyxplot versions

# rpc25, Sun Nov  8 13:36:29 CET 2009

# Default options (change with foo=bar on command line)

import sys, os, re

options = {'pyxplot'       : "pyxplot8",  # Default config goes here 
           'run'           : [ '000000' ],
           'compare'       : [ ],
           'version'       : "current",
           'compareversion': "current",
           'scriptdir'     : ".",
           'workdir'       : "."}

# Parse command-line options
def parseCommandLine(options, argv):
   for argument in argv[1:]:
      try:    [key, value] = re.split('=', argument)
      except: 
         print "Bad command-line argument %s: skipping"%argument
         continue
      # Simple options: set and continue
      found = False
      for option in ["pyxplot", "version", "compareversion", "scriptdir", "workdir"]:
         if (key == option) :
            options[key] = value
            found = True
            break
      if (found) : continue

      # Options which require a list to be created
      for option in ["run", "compare"]:
         if (key == option):
           found = True
           # Test to see if only a single value is specified
           for item in re.split(",", value): options[key].append(item)
           break
      if (found): continue

      # Didn't understand this item
      print "Failed to understand command-line argument %s: skipping"%argument

   # If we are doing comparions we need to have a directory to do them in
   if (len(options['compare']) > 0):
      options['comparedir'] = options['workdir'] + "/" + options['compareversion']

# Some basic checks on the sanity of the supplied options
def sanityCheck(options):
   print "Sanity check..."
   assert(os.path.isdir(options['scriptdir']))
   assert(os.path.isdir(options['workdir']))
   # Obviously you can fool the following test.  Don't.
   assert(options['workdir'] != options['scriptdir'])
   # Checks we need if we're doing comparisons
   if (len(options['compare']) > 0):
      assert(os.path.isdir(options['comparedir']))

def runTest(test, options):
   print "running test %s"%test
   scriptdir = options['scriptdir'] + '/' + test
   workdir = options['workdir'] + '/' + test
   # Check that the scripts exist
   try:    assert(os.path.isdir(scriptdir))
   except:
      print "Cannot find script directory for %s: %s.  Skipping"%(test, scriptdir)
      return
   # Check that there's somewhere to put them
   try: assert(not os.path.exists(workdir))
   except:
      print "Working dir for test %s, %s exists.  Skipping"%(test, workdir)
      return
   # Make the working directory
   os.system("cp -r %s %s"%(scriptdir,workdir))

   # Check to see whether there's a test.ppl script and if so run
   scriptfile = workdir + "/" + 'test.ppl'
   if (os.path.isfile(scriptfile)):
      os.system("cd %s ; %s %s > output 2> errors"%(workdir, options['pyxplot'], scriptfile))
      return

   # Check to see whether there's a test.sh script
   scriptfile = workdir + "/" + 'test.sh'
   if (os.path.isfile(scriptfile)):
      os.system("mv %s %s"%(scriptfile, scriptfile + ".orig"))
      fin = open(scriptfile + ".orig", "r")
      fout = open(scriptfile, "w")
      for line in fin:
         re.sub('PYXPLOT', options['pyxplot'], line)
         fout.write(line)
      fin.close()
      fout.close()
      os.system("cd %s; chmod u+x test.sh ; ./test.sh > output 2> errors"%workdir)
      return

   print "Cannot find script for test %s: skipping"%test


def compareTest(test, options):
   print "comparing test %s"%test

##################################################
# MAIN ROUTINE STARTS HERE
parseCommandLine(options, sys.argv)

sanityCheck(options)

# Run the requested tests
for test in options['run']:
   runTest(test, options)

# Do the requested comparisons
for test in options['compare']:
   compareTest(test, options)

