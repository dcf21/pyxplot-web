#!/usr/bin/env python2.6

# This is a script to test different pyxplot versions

# rpc25, Sun Nov  8 13:36:29 CET 2009

# Default options (change with foo=bar on command line)

import sys, os, re, subprocess

options = {'pyxplot'       : "pyxplot8",  # Default config goes here 
           'run'           : [ ],
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

# Prepare working directories
def prepareDirs(options):
   # Make an appropriate working directory for this version
   options['runningdir'] = options['workdir'] + "/" + options['version']
   if (os.path.exists(options['runningdir'])):
      print "Directory %s already exists!"%options['runningdir']
      try: assert(os.path.isdir(options['runningdir']))
      except: 
         print "FAIL: %s is not a directory!"%options['runningdir']
         raise
   else: os.mkdir(options['runningdir'])

   # If we are doing comparions...
   if (len(options['compare']) > 0):
      # Version to compare to
      options['comparetodir'] = options['workdir'] + "/" + options['compareversion']
      # Place to put comparisons
      options['comparedir'] = options['workdir'] + "/%s%s%s"%(options['version'],"VS",options['compareversion'])
      os.mkdir(options['comparedir'])

# Some basic checks on the sanity of the supplied options
def sanityCheck(options):
   print "Sanity check..."
   assert(os.path.isdir(options['scriptdir']))
   assert(os.path.isdir(options['workdir']))
   assert(os.path.isdir(options['runningdir']))
   # Checks we need if we're doing comparisons
   if (len(options['compare']) > 0):
      assert(os.path.isdir(options['comparedir']))

######################################################################
# Run a test
def runTest(test, options):
   print "running test %s"%test
   scriptdir = options['scriptdir'] + '/' + test
   workdir = options['runningdir'] + '/' + test
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

######################################################################
# Test comparion routines
def parseConfigFile(configFile, filesToCompare):
   try: f = open(configFile, "r")
   except:
      print "Failed to open config file %s"%configFile
      raise
   name = ""
   for line in f:
      try: [key, value] = re.split(':\s+', line, 1)
      except: 
         print "Failed to parse config file entry %s"%line
         continue
      if (key == 'name'):
         name = value
         # Check that we already have this filename and add a default entry if not
         try:    test = filesToCompare[name]
         except: filesToCompare[name] = {'type':'text', 'exclude':[]}
      elif (key == 'type'):    filesToCompare[name]['type'] = value
      elif (key == 'exclude'): filesToCompare[name]['exclude'].append(value) 
      elif (key == 'notes'):   break
      else:                    print "Incomprehensible config file key %s"%key
   f.close()

   # Add default entries for eps files
   for key in filesToCompare.keys():
      if (filesToCompare[key]['type'] == 'eps'):
         filesToCompare[key]['exclude'].append("^%%CreationDate: ")

######################################################################
# Compare two tests
def compareTest(test, options):
   print "comparing test %s"%test
   runningDir = options['runningdir'] + "/%s"%test
   comparetoDir = options['comparetodir'] + "/%s"%test
   for dir in [runningDir, comparetoDir]:
      if (not os.path.isdir(dir)):
         print "Skipping test %s: directory %s missing"%(test,dir)
         return
   testDir = options['comparedir'] + "/%s"%test
   try: assert(not os.path.exists(testDir))
   except: 
      print "Output of comparison %s already exists!  Skipping."%testDir
   os.mkdir(testDir)
   assert(os.path.isdir(testDir))

   # The set of files to compare.  Always compare output and errors
   filesToCompare = {'output': {'type':'text', 'exclude':[]}, 
                     'errors': {'type':'text', 'exclude':[]}}
   # Parse the config file for this test
   configFile = runningDir + "/config"
   parseConfigFile(configFile, filesToCompare)

   # Loop through the output files doing the comparison
   for file in filesToCompare.keys():
      file1 = "%s/%s"%(runningDir,file)
      file2 = "%s/%s"%(comparetoDir,file)
      if (not (os.path.isfile(file1) and os.path.isfile(file2))):
         print "Can't find one of two files to compare: %s %s"%(file1,file2)
         continue
      diffobj = subprocess.Popen("diff %s %s"%(file1,file2), shell=True, stdout=subprocess.PIPE)
      diff = re.split("\n",diffobj.communicate()[0])
      # Parse the diff
      output = []
      header = ''
      cache = []
      for line in diff:
         if (len(line)==0): continue
         if (line[0:3] == '---'):
            if (len(cache)>0): cache.append(line)
            continue
         # Check for a new section of diff
         if (line[0] != ">" and line[0] != "<"):
            if (len(cache) > 0):
               output.append(header)
               for l in cache: output.append(l)
               cache = []
            header = line
         else:
            # Check against all the exclusion regexes
            exclude = False
            for regex in filesToCompare[file]['exclude']:
               if (re.search(regex, line) != None):
                  exclude = True
                  break
            if (not exclude): cache.append(line)
      # Catch any output cached but not written to output buffer yet
      if (len(cache) > 0):
         output.append(header)
         for l in cache: output.append(l)
         cache = []

      if (len(output) > 0):
         outputFile = testDir + "/%s"%file
         f = open(outputFile, "w")
         for line in output: f.write("%s\n"%line)
         f.close()
         os.system("wc -l %s"%outputFile)


##################################################
# MAIN ROUTINE STARTS HERE
parseCommandLine(options, sys.argv)
prepareDirs(options)
sanityCheck(options)

# Run the requested tests
for test in options['run']:
   runTest(test, options)

# Do the requested comparisons
for test in options['compare']:
   compareTest(test, options)

