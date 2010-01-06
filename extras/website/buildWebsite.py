#!/usr/bin/python

# This is a script to test different pyxplot versions

# rpc25, Sun Nov  8 13:36:29 CET 2009

# Default options (change with foo=bar on command line)

import sys, os, re, subprocess, shutil

options = {'pyxplot'       : "pyxplot8",  # Default config goes here 
           'sourceRoot'    : "source/",
           'targetRoot'    : "public_html/",
			  'rooturi'       : None,
			  'imguri'        : None,
			  'resuri'        : None,
			  'cssuri'        : None,
			  'configfile'    : None
			  }

variables = {}

currentObject = {'source'  : None,
					  'target'  : None,
					  'type'    : None}
 

# Parse command-line options
def parseCommandLine(options, argv):
   for argument in argv[1:]:
      try:    [key, value] = re.split('=', argument)
      except: 
         print "Bad command-line argument %s: skipping"%argument
         continue
		# All options are simple
		options[key] = value
		continue

      # # Simple options: set and continue
      # found = False
      # for option in ["rooturi", "version", "compareversion", "scriptdir", "workdir"]:
         # if (key == option) :
            # options[key] = value
            # found = True
            # break
      # if (found) : continue
 
      # # Options which require a list to be created (currently none)
      # for option in []:
         # if (key == option):
           # found = True
           # # Test to see if only a single value is specified
           # for item in re.split(",", value): options[key].append(item)
           # break
      # if (found): continue

      # Didn't understand this item
      # print "Failed to understand command-line argument %s: skipping"%argument


#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-
# The html parsing workhorse function
def parseHTMLFile(f):
	# Check that all the necessary things are defined
	assert(options['rooturi'] != None)
	assert(options['imguri'] != None)
	assert(options['resuri'] != None)
	assert(options['cssuri'] != None)
   for line in f:
		# Deal with magic tab substitution
	   line = re.sub(r'<<ROOT>>',   options['rooturi'], line)
	   line = re.sub(r'<<IMGDIR>>', options['imguri'], line)
	   line = re.sub(r'<<RESDIR>>', options['resuri'], line)
	   line = re.sub(r'<<CSSDIR>>', options['cssuri'], line)
		# Deal with variables
      for variable in variables.keys():
         line = re.sub(r"<<%s>>"%variable, variables[variable], line)
		# Deal with included files
		m = re.search(r'^(.*?)<<INCLUDE (.*?)>>(.*)', line)
		if (m):
        yield m.groups(1)
        for subline in parseFile(m.groups(2), options['includeDir']): yield subline
        yield m.groups(3)
     else:
        yield line

#   try: f = fopen(os.path.join(path, filename), 'r')
#   except:
#      print "Can't include file %s in path %s\n"%(filename, path)
#      raise

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-
# Config file parsing
def parseConfigFile(configFile, filesToCompare):
   try: f = open(configFile, "r")
   except:
      fail("Failed to open config file %s"%configFile)
      raise
   name = ""
   # for line in f:   # <-- can't use this as we want to have f.readline() elsewhere
	while (True):
		line = f.readline()
		if (line == ''): break    # EOF
      try: [key, value] = re.split(':\s+', line, 1)
      except: 
         print "Failed to parse config file entry %s: skipping"%line
         continue
		if (key == 'hostname')      :  setRootURI("http://%s/"%value)
		elif (key == 'root'):    
		   if (value[-1] == '/')    : setRootURI(value)
			else                     : setRootURI("%s/"%value)   
		elif (key == 'imagedir')    : options['imguri'] = fullURI(value)
		elif (key == 'cssdir')      : options['cssuri'] = fullURI(value)
		elif (key == 'resourcedir') : options['resuri'] = fullURI(value)
		elif (key == 'variable'):
		   try: [varname, varval] = re.split(':\s+', value, 1)
			except: 
			   print "Bad variable assignment %s -- skipping"%value
				continue
			variables['varname'] = varval
		elif (key == 'sourceroot')  : options['sourceRoot'] = value
		elif (key == 'targetroot')  : options['targetRoot'] = value
		# The following entries actually do arrange for files to be parsed
		elif (key == 'source' or key == 'target') :
			if (currentObject[key] != None):   # Already have an object: insert it
				insertObject(f)
			currentObject[key] = value;
		elif (key == 'type')        : currentObject[key] = value
		else:
			print "Confused by config file entry %s -- skipping"%line
	
	# Empty the object structure
	if (currentObject['source'] != None or currentObject['target'] != None): insertObject()
			
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-
# Insert an object into the output tree
def insertObject(configFileHandle):
	# First check that we have all the data that we require
	if (currentObject['source'] == None): # Read data from current config file
	   sourceData = readToEOD(configFileHandle, 'EOD')
		sourceFile = None
	else:
		sourceFile = os.path.join(options['sourceRoot'],currentObject['source'])
		if (sourceFile[-1] == '/'): sourceFile = sourceFile[:-1]    # Strip trailing /s
		[sourceFilename, sourceDir] = os.path.split(sourceFile)

	# Target
	try: assert(currentObject['target'] != None)
	except:
		fail("Target not specified for source %s!"%sourceFile)
		raise
	targetFile = os.path.join(options['targetRoot'],currentObject['target'])
	[targetFilename, targetDir] = os.path.split(targetFile)

	type = currentObject['type']

	# Check that the source object exists
	try: assert(os.path.exists(sourceFile))
	except:
		fail("Source object %s does not exist"%sourceFile)
		raise

	# Make the target directory if necessary
	if (!os.path.exists(targetDir)):
		try: os.makedirs(targetDir)
		except:
			fail("Failed to make target directory %s"%targetDir)
			raise
	try: assert(os.path.isdir(targetDir))
	except:
		fail("Target directory %s is not a directory!"%targetDir)
		raise
	
	# Deal with parsed html etc. files first
	if (type == "parsed"):
		# Produce file object for input
		if (sourceFile == None):    # Data read from current config file
			fin = tmpfile()
			for line in sourceData: fin.write(line)
			fin.seek(0,0)  # Re-wind temporary file
		else:   # Data in a file to be parsed
			try: fin = open(sourceFile, 'r')
			except:
				fail("Cannot open source file %s!"%sourceFile)
				raise
		# Produce file object for output
		try: fout = open(targetFile, 'w')
		except: 
			fail("Cannot open target file %s for writing!"%targetFile)
			raise
		# Write the output
		for line in parseHTMLFile(fin): fout.write(line)

		# And wrap up
		fin.close()
		fout.close()
	
	elif (type == 'inplace' or type == None):  # Write file as is in place
		if (sourceFile == None):   # Data read from config file
			try: fout = open(targetFile, 'w')
			except: 
				fail("Cannot open target file %s for writing!"%targetFile)
				raise
			# Write the output
			for line in sourceData: fout.write(line)
			fout.close()

		else:    # Data in file
			if (os.path.isdir(sourceFile)):
				try: shutil.copytree(sourceFile, targetFile, False)
				except:
					fail("Failed to copy source directory %s to target %s"%(sourceFile,targetFile))
					raise
			else:
				try: shutil.copy2(sourceFile, targetFile)
				except:
					fail("Failed to copy source file %s to target %s"%(sourceFile,targetFile))
					raise


#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-
# Library of utility functions

# fail prints an error message
def fail (error):
	sys.stderr.write(error)

# readToEOD reads data from a file until an EOD marker is found
def readToEOD(fileHandle, EOD):
	output = []
	while (True):
		line = fileHandle.readline()
		try: assert(line != '')
		except:
			print "EOF whilst reading data inline from config file!  Check your EOD statement!"
			raise
		if (line == "%s\n"%EOD): break      # Found EOD
		output.append(line)
	return output

# setRootURI sets the root URI and also subURIs
def setRootURI(uri):
	options['rooturi'] = uri
	options['imguri'] = "%simages/"%uri
	options['cssuri'] = "%scss/"%uri
	options['resuri'] = "%sresources/"%uri

# Turn a partial uri, say "images", into a full uri "http://www.srcf.ucam.org/images/" if necessary
def fullURI(uri):
	if (uri[-1] != '/') : uri = "%s/"%uri
	if (uri[0:4] == 'http') : return uri
	else                    : return "%s%s"%(options['rooturi'],uri)


##########################################################################################

# MAIN ROUTINE STARTS HERE
parseCommandLine(options, sys.argv)
assert(options['configfile'] != None)
parseConfigFile(options['configfile'])
