#!/usr/bin/python

# This is a script to test different pyxplot versions

# rpc25, Sun Nov  8 13:36:29 CET 2009

# Default options (change with foo=bar on command line)

import sys, os, re, subprocess, shutil, copy, tempfile

options = {'pyxplot'       : "pyxplot9",  # Default config goes here 
           'sourceRoot'    : "source/",
           'targetRoot'    : "public_html/",
           'rooturi'       : None,
           'imguri'        : None,
           'resuri'        : None,
           'cssuri'        : None,
           'includedir'    : None,
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
def parseHTMLFile(f, localOpts, localVars):
   # Check that all the necessary things are defined
   assert(localOpts['rooturi'] != None)
   assert(localOpts['imguri'] != None)
   assert(localOpts['resuri'] != None)
   assert(localOpts['cssuri'] != None)
   for line in f:
      # Deal with magic tab substitution
      line = re.sub(r'<<ROOT>>',   localOpts['rooturi'], line)
      line = re.sub(r'<<IMGDIR>>', localOpts['imguri'], line)
      line = re.sub(r'<<RESDIR>>', localOpts['resuri'], line)
      line = re.sub(r'<<CSSDIR>>', localOpts['cssuri'], line)
      # Deal with substitution of variables
      for variable in localVars.keys():
         line = re.sub(r"<<VARIABLE %s>>"%variable, localVars[variable], line)
      # Deal with setting variables
      m = re.search(r'<<SET (.+?): *(.*?)>>', line)
      while (m):
         localVars[m.group(1)] = m.group(2)
         line = re.sub(r'<<SET (.+?): *(.*?)>>', '', line)
         m = re.search(r'<<SET (.+?): *(.*?)>>', line)
      # Deal with included files
      m = re.search(r'^(.*?)<<INCLUDE (.+?)>>(.*)', line)
      if (m):
        yield m.group(1)
        fileToInclude = os.path.join(localOpts['includedir'], m.group(2))
        try: f2 = open(fileToInclude, 'r')
        except: 
           fail ("Failed to include file %s"%(fileToInclude))
           raise
        for subline in parseHTMLFile(f2, localOpts, localVars): yield subline
        f2.close()
        yield m.group(3)
      else:
        yield line

#   try: f = fopen(os.path.join(path, filename), 'r')
#   except:
#      print "Can't include file %s in path %s\n"%(filename, path)
#      raise

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-
# Config file parsing
def parseConfigFile(configFile):
   try: f = open(configFile, "r")
   except:
      fail("Failed to open config file %s"%configFile)
      raise
   name = ""
   # for line in f:   # <-- can't use this as we want to have f.readline() elsewhere
   while (True):
      line = f.readline()
      if (line == ''): break    # EOF
      line = line.strip()
      if (line == ''): continue # Blank line
      if (line[0] == '#'): continue # Comment
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
      elif (key == 'includedir')  : options['includedir'] = value
      elif (key == 'variable'):
         try: [varname, varval] = re.split(':\s*', value, 1)
         except: 
            print "Bad variable assignment %s -- skipping"%value
            continue
         variables[varname] = varval
      elif (key == 'sourceroot')  : options['sourceRoot'] = value
      elif (key == 'targetroot')  : options['targetRoot'] = value
      # The following entries actually do arrange for files to be parsed
      elif (key == 'source' or key == 'target') :
         if (currentObject[key] != None):   # Already have an object: insert it
            print "Inserting object with source %s and target %s"%(currentObject['source'],currentObject['target'])
            insertObject(f, currentObject, options, variables)
         currentObject[key] = value;
      elif (key == 'type')        : currentObject[key] = value
      elif (key == 'examples')    :   # Examples are handled separately
         assert(value == 'start')
         if (currentObject['source'] != None or currentObject['target'] != None): 
            insertObject(f, currentObject, options, variables)
         doExamples(f)
      elif (key == 'pyxplot')     : options['pyxplot'] = value
      else:
         print "Confused by config file entry %s -- skipping"%line
   
   # Empty the object structure
   if (currentObject['source'] != None or currentObject['target'] != None): insertObject(f, currentObject, options, variables)
         
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-
# Insert an object into the output tree
def insertObject(configFileHandle, localObject, localOpts, localVars):
   # First check that we have all the data that we require
   if (localObject['source'] == None): # Read data from current config file
      sourceData = readToEOD(configFileHandle, 'EOD')
      sourceFile = None
   else:
      sourceFile = os.path.join(localOpts['sourceRoot'],localObject['source'])
      if (sourceFile[-1] == '/'): sourceFile = sourceFile[:-1]    # Strip trailing /s
      [sourceDir, sourceFilename] = os.path.split(sourceFile)

   # Target
   if (localObject['target'] == None): targetFile = os.path.join(localOpts['targetRoot'],localObject['source'])
   else: targetFile = os.path.join(localOpts['targetRoot'],localObject['target'])
   [targetDir, targetFilename] = os.path.split(targetFile)

   type = localObject['type']

   # Make the target directory if necessary
   if (not os.path.exists(targetDir)):
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
         fin = os.tmpfile()
         for line in sourceData: fin.write(line)
         fin.seek(0,0)  # Re-wind temporary file
      else:   # Data in a file to be parsed
         # Check that the source object exists
         try: assert(os.path.exists(sourceFile))
         except:
            fail("Source object %s does not exist"%sourceFile)
            raise
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
      for line in parseHTMLFile(fin, localOpts, localVars): fout.write(line)

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
   # Re-set current object structure
   localObject['source'] = None
   localObject['target'] = None
   localObject['type'] = None

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-
# Examples
def doExamples (configFH):
   examplesTree = {
                  'root'    : None,
                  'nodes'   : []
                  }
   while (True):
      [key, value] = examplesGetConfigLine(configFH)
      if (key == '' and value == '')             : continue
      elif (key == 'exampleroot')                : examplesTree['root'] = value
      elif (key == 'examplerootpage')            : examplesTree['rootpage'] = value
      elif (key == 'examplenodepage')            : examplesTree['nodepage'] = value
      elif (key == 'exampleleafpage')            : examplesTree['leafpage'] = value
      elif (key == 'node')                       : examplesTree['nodes'].append(getExamplesNode(configFH))
      elif (key == 'examples' and value == 'end'): break
      else: fail ("Confused by examples entry %s: %s -- skipping"%(key,value))
   
   renderExamples(examplesTree)
         

def getExamplesNode(configFH):
   node = {
            'name'   : None,
            'dir'    : None,
            'image'  : None,
            'leaves' : []
            }
   while (True):
      [key, value] = examplesGetConfigLine(configFH)
      if (key == '' and value == '')             : continue
      elif (key == 'nodename')                   : node['name'] = value
      elif (key == 'nodedir')                    : node['dir'] = value
      elif (key == 'nodeimg')                    : node['image'] = value
      elif (key == 'leaf')                       : node['leaves'].append(getExamplesLeaf(configFH))
      elif (key == 'node' and value == 'end')  : break
      else: fail ("Confused by examples node entry %s: %s -- skipping"%(key,value))
   
   try: assert(node['leaves'] != [])
   except:
      fail("Empty examples node %s!"%node['name'])
      raise

   # Default image is output of first leaf
   if (node['image'] == None): node['image'] = os.path.join(node['leaves'][0]['dir'], 'output_sm.png')

   # Check that all the necessary information has been supplied
   for x in 'name', 'dir':
      try: assert(node[x] != None)
      except:
         fail("Node is missing %s!"%x)
         raise

   return node

def getExamplesLeaf(configFH):
   leaf = {
            'name'       : None,
            'dir'        : None,
            'scriptfile' : None,
            'caption'    : None,
            'notes'      : None,
            'datafiles'  : []
            }
   while (True):
      [key, value] = examplesGetConfigLine(configFH)
      if (key == '' and value == '')             : continue
      elif (key == 'leafname')                   : leaf['name'] = value
      elif (key == 'leafdir')                    : leaf['dir'] = value
      elif (key == 'script')                     : leaf['scriptfile'] = value
      elif (key == 'caption')                    : leaf['caption'] = value
      elif (key == 'notes')                      : leaf['notes'] = value
      elif (key == 'datafile')                   : leaf['datafiles'].append(value)
      elif (key == 'leaf' and value == 'end')    : break
      else: fail ("Confused by examples leaf entry %s: %s -- skipping"%(key,value))
      
   # Check that all the necessary information has been supplied
   for x in 'name', 'dir', 'scriptfile', 'caption', 'notes':
      try: assert(leaf[x] != None)
      except:
         fail("Leaf %s is missing %s!"%(leaf['name'],x))
         raise

   return leaf

def renderExamples(tree):
   # Make a local copy of the variables and config for use in rendering examples
   examplesOptions = copy.copy(options)
   examplesVariables = copy.copy(variables)
   object = {}

   # Walk the tree, generating URIs for each node and leaf
   if (tree['root'][-1] != '/') : tree['root'] = "%s/"%tree['root']
   tree['uri'] = examplesOptions['rooturi'] + tree['root']
   for node in tree['nodes']:
      node['uri'] = tree['uri'] + node['dir'] + '/'
      for leaf in node['leaves']:
         leaf['uri'] = node['uri'] + leaf['dir'] + '/'
      # Generate 'next' and 'previous' uris for the leaves where appropriate
      for i in range(len(node['leaves'])):
         if (i==0) : node['leaves'][i]['prevuri'] = None
         else      : node['leaves'][i]['prevuri'] = node['leaves'][i-1]['uri']
         if (i==len(node['leaves'])-1): node['leaves'][i]['nexturi'] = None
         else                         : node['leaves'][i]['nexturi'] = node['leaves'][i+1]['uri'] 

   # Render root node
   object['target'] = "%sindex.html"%tree['root']
   object['source'] = None                                 # Read from a supplied filehandle
   object['type'] = 'parsed'
   # Write the file to use for the root node to a temporary file
   ftmp = os.tmpfile()
   fin = open(os.path.join(options['includedir'],tree['rootpage']), 'r')
   line = fin.readline()
   while (line.strip() != '<<EXAMPLES>>'):
      ftmp.write(line)
      line = fin.readline()
      assert(line != '')
   # Write boxes for examples
   nodeCount = 0
   for node in tree['nodes']:
      if   (nodeCount  ==0): ftmp.write("<tr>\n")
      elif (nodeCount%2==0): ftmp.write("</tr><tr>\n")
      ftmp.write("<<SET exampleuri: %s>>\n"%node['uri'])
      ftmp.write("<<SET exampleimageuri: %s%s>>\n"%(node['uri'],node['image']))
      ftmp.write("<<SET examplename: %s>>\n"%node['name'].replace("_", " "))
      f = open(os.path.join(options['includedir'], 'examples-box.html'), 'r')  # UGLY
      for line in f: ftmp.write(line)
      f.close()
      nodeCount+=1
   if ((nodeCount>0)and(nodeCount%2==1)): ftmp.write("<td></td>\n")
   if  (nodeCount>0)                    : ftmp.write("</tr>\n")
   line = fin.readline()
   while (line != ''): 
      ftmp.write(line)
      line = fin.readline()
   ftmp.write("EOD\n")
   # Now render the file
   ftmp.seek(0,0)
   insertObject(ftmp, object, examplesOptions, examplesVariables)
   ftmp.close()

   for node in tree['nodes']:
      renderExamplesNode(node, tree, examplesOptions, examplesVariables)

def renderExamplesNode(node, tree, opt, var):
   object = {'source'  : None,
             'type'    : 'parsed'}
   object['target'] = os.path.join(tree['root'], node['dir'], 'index.html')
   ftmp = os.tmpfile()
   # Set the "examplename" variable so that we get the page title correct
   ftmp.write("<<SET examplename: %s>>\n"%node['name'].replace("_", " "))
   fin = open(os.path.join(options['includedir'],tree['nodepage']), 'r')
   line = fin.readline()
   while (line.strip() != '<<EXAMPLES>>'):
      ftmp.write(line)
      line = fin.readline()
      assert(line != '')
   # Write boxes for examples
   nodeCount = 0
   for leaf in node['leaves']:
      if   (nodeCount  ==0): ftmp.write("<tr>\n")
      elif (nodeCount%2==0): ftmp.write("</tr><tr>\n")
      ftmp.write("<<SET exampleuri: %s>>\n"%leaf['uri'])
      ftmp.write("<<SET exampleimageuri: %s%s>>\n"%(leaf['uri'],'output_sm.png'))
      ftmp.write("<<SET examplename: %s>>\n"%leaf['name'].replace("_", " "))
      f = open(os.path.join(options['includedir'], 'examples-box.html'), 'r')  # UGLY
      for line in f: ftmp.write(line)
      f.close()
      nodeCount+=1
   if ((nodeCount>0)and(nodeCount%2==1)): ftmp.write("<td></td>\n")
   if  (nodeCount>0)                    : ftmp.write("</tr>\n")
   line = fin.readline()
   while (line != ''): 
      ftmp.write(line)
      line = fin.readline()
   ftmp.write("EOD\n")
   # Now render the node
   ftmp.seek(0,0)
   insertObject(ftmp, object, opt, var)
   ftmp.close()

   for leaf in node['leaves']:
      renderExamplesLeaf(leaf, node, tree, opt, var)

def renderExamplesLeaf(leaf, node, tree, opt, var):
   print "Working on example %s %s."%(node['dir'], leaf['dir'])

   # First write the index.html file
   object = {'source'  : None,
             'type'    : 'parsed'}
   object['target'] = os.path.join(tree['root'], node['dir'], leaf['dir'], 'index.html')
   ftmp = os.tmpfile()
   ftmp.write("<<SET nodename: %s>>\n"%node['name'].replace("_", " "))
   ftmp.write("<<SET exampleuri: %s>>\n"%leaf['uri'])
   ftmp.write("<<SET exampleimageuri: %s%s>>\n"%(leaf['uri'],'output.png'))
   ftmp.write("<<SET examplename: %s>>\n"%leaf['name'].replace("_", " "))
   var['caption'] = leaf['caption']
   var['scriptfile'] = leaf['scriptfile']
   var['notes'] = leaf['notes']
   fin = open(os.path.join(options['includedir'],tree['leafpage']), 'r')
   line = fin.readline()
   while (line.strip() != '<<NAVBOXES>>'):
      ftmp.write(line)
      line = fin.readline()
      assert(line != '')
   # Write navboxes
   ftmp.write('<div class="examplebuttons" style="width:150px;"><div class="examplebutton">\n')
   if (leaf['prevuri']!=None): ftmp.write('<a href="%sindex.html"><img src="<<ROOT>>images/arrow_back2.png" style="padding:4px;" title="Previous example" alt="Prev"></a>\n'%leaf['prevuri'])
   else                      : ftmp.write('<img src="<<ROOT>>images/arrow_back3.png" style="padding:4px;" title="Previous example" alt="Prev">\n')
   ftmp.write('</div>\n<div class="examplebutton">\n')
   if (leaf['nexturi']!=None): ftmp.write('<a href="%sindex.html"><img src="<<ROOT>>images/arrow_forward2.png" style="padding:4px;" title="Next example" alt="Next"></a>\n'%leaf['nexturi'])
   else                      : ftmp.write('<img src="<<ROOT>>images/arrow_forward3.png" style="padding:4px;" title="Next example" alt="Next">\n')
   ftmp.write('</div></div>\n')
   # Write example downloads box
   ftmp.write('<p style="text-align:center; clear: both; margin-bottom:4px;">Download this example:</p>\n')
   ftmp.write('<div class="exampledownloads">\n')
   filelist = ['script.ppl', 'output.eps', 'output.png']
   for file in leaf['datafiles']: 
      m = re.match('.*/(.*?)$', file)
      filelist.append(m.group(1))
   for file in filelist:
      ftmp.write('<div class="exampledownload"><a href="%s/%s">%s</a></div>\n'%(leaf['uri'],file,file))
   ftmp.write('</div>\n')
   line = fin.readline()
   while (line != ''): 
      ftmp.write(line)
      line = fin.readline()
   #for line in fin: ftmp.write(line)
   ftmp.write("EOD\n")
   # Now render the leaf
   ftmp.seek(0,0)
   insertObject(ftmp, object, opt, var)
   ftmp.close()

   # Now render the contents of the scriupt
	# XXX The error handling in this bit is fucking dreadful.  Please sort it out.
   tempdir = tempfile.mkdtemp()
   shutil.copy2(os.path.join(options['includedir'],leaf['scriptfile']), "%s/script.ppl"%tempdir)
   for datafile in leaf['datafiles']: shutil.copy2(os.path.join(options['includedir'],datafile), tempdir)
   os.system("cp .pyxplotrc %s"%tempdir) # Make sure that ppl uses default configuration options
   pplobj = subprocess.Popen(opt['pyxplot'], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, cwd=tempdir)
   [output, errors] = pplobj.communicate('set width 6\nset fontsize 1.2\nset term eps\nset out "output.eps"\nload "script.ppl"\nset term png trans dpi 110\nset output "output.png"\nrefresh\nset term png trans dpi 90\nset output "output_sm.png"\nrefresh')
   # In an ideal world we'd do something useful with the output here
   if (len(errors.strip())>0):
     sys.stderr.write("PyXPlot error:\n%s"%errors)
     raise RuntimeError
   leafdir = os.path.join(opt['targetRoot'],tree['root'], node['dir'], leaf['dir'])
   for file in ['output.eps', 'output.png', 'output_sm.png', 'script.ppl']: shutil.copy2("%s/%s"%(tempdir,file), leafdir)
   for file in leaf['datafiles']: shutil.copy2(os.path.join(options['includedir'],file), leafdir)
   shutil.rmtree(tempdir)


def examplesGetConfigLine(f):
   line = f.readline()
   try: assert (line != '')
   except: 
      fail ("EOF encountered whilst processing examples!")
      raise
   line = line.strip()
   if (line == ''): return ['', ''] # Blank line
   if (line[0] == '#'): return ['', ''] # Comment
   try: [key, value] = re.split(':\s+', line, 1)
   except: 
      print "Failed to parse config file entry %s: skipping"%line
      return ['', '']
   return [key, value]

#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-
# Library of utility functions

# fail prints an error message
def fail (error):
   sys.stderr.write("%s\n"%error)

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
