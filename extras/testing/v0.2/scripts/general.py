# This file contains shared routines for database handling for the great pyxplot testing system

subdir = "ppltest"

# Open any named db
def openaDB(dbname):
   import os
   from pysqlite2 import dbapi2 as sqlite
   global subdir
   # connection = sqlite.connect("/home/ftcb/ftcb/ftcb.db")
   # os.system(os.path.join(rootdir(), "scripts", "runTestsBackend.py") + " >> /home/rpc25/ppltestlog &")
   # dbfn = os.path.join(os.environ["HOME"], subdir, "dbs", dbname)
   dbfn = os.path.join(rootdir(), "dbs", dbname)
   connection = sqlite.connect(dbfn)
   cursor = connection.cursor()
   return (connection, cursor)

# Extract zero or one items from the database
def getPossibleItemFromDB(sql, vars, cursor):
   cursor.execute(sql, vars)
   list = cursor.fetchall()
   if (len(list)==0): return None
   try: assert(len(list)==1)
   except: 
      print "%s"%list
      raise
   return list[0][0]

# Extract a single item from the database
def getFromDB(sql, vars, cursor):
   cursor.execute(sql, vars)
   list = cursor.fetchall()
   try: assert(len(list)==1)
   except: raise
   return list[0][0]


# Coerces a string to unicode if it is not None
def ucornone(string):
   if (string==None): return None
   else             : return unicode(string)
 

# Close database connections etc.
def gcdb(connection, cursor):
   cursor.close()
   connection.commit()
   return

def rootdir():
   import os
   global subdir
   return os.path.join("/home/ppltest", subdir)

# Produce a file string for a file id
def buildFileString(id):
   import os
   # return os.path.join(rootdir(), "cache/cache.%s"%(id))
   return "cache.%s"%(id)

# Insert a record for an "in-place" file into the files database
def insertInPlaceFileRecord(cursor):
   cursor.execute("INSERT INTO files (mode) VALUES (?);", (1,))
   id = getFromDB('SELECT id FROM files WHERE mode=? ORDER BY id DESC LIMIT 1;', (1,), cursor)
   fn = buildFileString(id)
   cursor.execute("UPDATE files SET value=? WHERE id=?;", (fn, id))
   return(id, fn)

# Insert some text into the files database and return the id for the newly created record
def insertIntoFileDB(text, cursor):
   cursor.execute("INSERT INTO files (mode,value) VALUES (?,?);", (0, text))
   fid = cursor.execute("SELECT id FROM files WHERE (mode=? AND value=?);", (0, text)).fetchall()[-1][0]
   return fid

# Delete a test thoroughly
def deleteTest(tid, cursor):
   cursor.execute("DELETE FROM tests WHERE (id=?);", (tid,))
   cursor.execute("DELETE FROM pendingTests WHERE (tid=?);", (tid,))
   cursor.execute("DELETE FROM instTestMap WHERE (tid=?);", (tid,))
   for i in cursor.execute("SELECT id,fid FROM outputs WHERE (tid=?);", (tid,)).fetchall():
      (oid, fid) = i
      deleteTestOutput(oid, fid, cursor)
   cursor.execute("DELETE FROM inputs WHERE (tid=?);", (tid,))
   cursor.execute("DELETE FROM testgroupmap WHERE (tid=?);", (tid,))
   return

def deleteTestOutput(oid, fid, cursor):
   if (fid == None): fid = getFromDB("SELECT fid FROM outputs WHERE (id=?);", (oid,), cursor)
   deleteFileFromDB(fid, cursor)
   for j in cursor.execute("SELECT fid FROM instoutmap WHERE (oid=?);", (oid, )).fetchall(): deleteFileFromDB(j[0], cursor)
   cursor.execute("DELETE FROM instoutmap WHERE (oid=?);", (oid,));
   cursor.execute("DELETE FROM outputs WHERE (id=?);", (oid,))

def deleteTestInput(iid, cursor):
   cursor.execute("DELETE FROM inputs WHERE (id=?);", (iid,))
   return
   
def deleteFileFromDB(fid, cursor):
   # We should do this properly, but running rm is scary
   cursor.execute("DELETE FROM files WHERE (id=?);", (fid,))
   return

def runTestOnAllVersions(tid, cursor):
   cursor.execute("INSERT OR IGNORE INTO pendingTests (iid, tid) SELECT id,? FROM pplVersions WHERE (hidden=0);", (tid,))
   launchTests()
   return

def launchTests():
   import os, os.path
   os.system(os.path.join(rootdir(), "scripts", "runTestsBackend.py") + " >> /home/ppltest/logs/ppltestlog &")
   return


# Logging
def log(string):
   import time, os
   pid = os.getpid()
   dts = time.asctime(time.localtime())
   print "[%s] %s: %s"%(pid,dts,string)

####################################################
# Routines taken from the test run backend         #
####################################################

# Obtain the output produced by a test
def obtainObtainedOutput(tid, oid, iid, cursor):
   fid = cursor.execute("SELECT fid FROM instoutmap WHERE (iid=? AND oid=?);", (iid, oid)).fetchall()
   if (len(fid)==0): 
      log("  No contents found for output %s"%oid)
      return None
   elif (len(fid)!=1):
      log("Error: odd fid result %s"%fid)
   fid = fid[0][0]
   fdetails = cursor.execute("SELECT mode, value FROM files WHERE (id=?);", (fid,)).fetchall()
   if (len(fdetails)==0):
      log("  Stored file %s appears to be missing!"%fid)
      return None
   (fmode, fval) = fdetails[0]
   return obtainFileContents(fmode,fval)


# Obtain the output expected from a test
def obtainExpectedOutput(tid, oid, mode, fid, Sobtained, cursor):
   # mode=0 => Compare against previous, 1=> Compare against stored value
   if (mode==0):
      previous = cursor.execute("SELECT iom.fid FROM instoutmap iom LEFT JOIN insttestmap itm ON (iom.iid=itm.iid) WHERE (itm.tid=? AND iom.oid=? AND itm.state=?);", (tid, oid, 2)).fetchall()
      if (len(previous)==0): 
         log("  No previous values found for output %s; taking input as canon"%oid)
         return Sobtained
      fid = previous[-1][0]
      log("  fid for previous value of output %s is %s"%(oid,fid))
   fdetails = cursor.execute("SELECT mode, value FROM files WHERE (id=?);", (fid,)).fetchall()
   if (len(fdetails)==0):
      log("  Stored file %s appears to be missing!"%fid)
      return ""
   (fmode, fval) = fdetails[0]
   return obtainFileContents(fmode,fval)

# And in the case where we make it with python
def obtainExpectedOutputFromScript(script, workdir):
   import os, os.path, re
   lines = []
   for line in script.split("\n"):
      if (line==""): continue
      if (re.match(r"[0-9(]", line)): lines.append("print %s"%line)
      else:               lines.append(line)
   # If some script has been generated, run it and return the output
   if (len(lines)>0):
      pythonScript = "\n".join(lines)
      fn = os.path.join(workdir, "script.py")
      fp = open(fn, "w")
      fp.write(pythonScript)
      fp.close()
      os.system("cd %s ; python script.py > script.out 2> script.err"%(workdir))
      fn = os.path.join(workdir, "script.out")
      fp = open(fn, "r")
      output = fp.read()
      fp.close()
      return output
   else:
      return ""

def obtainFileContentsFromDB(fid, cursor):
   fromDB = cursor.execute("SELECT mode, value FROM files WHERE (id=?);", (fid, )).fetchall()
   if (len(fromDB)<1): return None
   (mode, value) = fromDB[0]
   return obtainFileContents(mode, value)

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

def obtainDiffRules(idr, special, filename, cursor):
   import re
   log("  Obtaining diff rules special=%s idr=%s"%(special,idr))
   if (idr==0): diffrules = []
   elif (idr==-1):    # Default diff rules
      if (special == 0):   # Stdout
         diffrules = []
      elif (special == 1): # Stderr
         diffrules = [] # ["^==[0-9]+=="]   # Ignore valgrind output
      else:
         temp = re.search(r"\.[a-zA-Z0-9]+$", filename)
         if (temp==None):
            log("  Warning: failed to detect file type for %s; falling back to no diff rules"%filename)
            diffrules = []
         else:
            ending = temp.group(0)[1:]
            temp2 = getPossibleItemFromDB("SELECT rules FROM diffrules WHERE (extension=?);", (ending,), cursor)
            if (temp2==None): 
               log("  Warning: no diff rules found for ending %s"%(ending))
               diffrules = []
            else: 
               diffrules = temp2.split("\n")
   else:
      temp = getPossibleItemFromDB("SELECT rules FROM diffrules WHERE (id=?);", (idr,), cursor)
      if (temp==None):
         log("  Warning: diff rules set %s not found"%idr)
         diffrules = []
      else:
         diffrules = temp.split("\n")
   return diffrules

def hasMyTestPassed(so, se, diffrules):
   import re
   # Excessive formatting  and line ending wankery
   so = unicode(so).replace("\r\n", "\n").replace("\r", "\n")
   se = unicode(se).replace("\r\n", "\n").replace("\r", "\n")
   passFail = True
   details = []
   o = so.split("\n")
   e = se.split("\n")

   # Ignore terminal blank lines
   while (len(o)>0 and o[-1]==""): o.pop()

   if (len(o)==0 and len(e)!=0): 
      for line in e:
         if (line != ""):
            passFail = False
            break

   # Iterate through the lines in the obtained output, o
   while (len(o)>0):
      (to, lo) = shiftAndTest(o, diffrules)
      # If the line is not to be tested (it is excluded by the diff rules), store and continue
      if (to == False): details.append([2, lo, ""])
      # Else obtain the next expected line and test against that 
      else:
         te = False
         while (not te): (te, le) = shiftAndTest(e, diffrules)
         if (compareTestOutputLines(lo,le)): 
            details.append([1, lo, le])
         else:
            details.append([0, lo, le])
            passFail = False
   while (len(e)>0):
      te = False
      while (not te and len(e)>0): (te, le) = shiftAndTest(e, diffrules)
      if (le==""): continue
      if (te):
         details.append([0, "", le])
         passFail = False
         if (len(e)>0):
            details.append([0, "", "etc."])
            break
      
   return (passFail, details)

def isMyValgrindOutputWorrying(txt):
   import re
   txt = unicode(txt).replace("\r\n", "\n").replace("\r", "\n")
   passFail = True
   details = []
   failStrings = [r"Conditional jump or move", "at 0x", "by 0x"]
   for line in txt.split("\n"):
      i = 2
      mo = re.match(r"==[0-9]+==(.*)", line)
      if (mo):
         l = mo.group(1)
         for string in failStrings:
            if (re.search(string, l)):
               passFail = False
               i = 0
      details.append([i, line, ""])
   return (passFail, details)

def shiftAndTest(array, diffrules):
   import re
   if (len(array)==0): return (True, "")
   line = array.pop(0)
   keep = True
   # Check against the diff rules
   for dr in diffrules:
      if re.search(dr, line):
         keep = False
         break
   return (keep, line)


def compareTestOutputLines(o,e):
   import re
   eps = 1e-100
   if (o==e): return True
   # Try two similar moveto commands
   if (re.search(" moveto$", o) and re.search(" moveto$", e)):
      oL = o.split()
      eL = e.split()
      if (len(oL)==3 and len(eL)==3):
         try:
            oL = [float(i) for i in oL[:2]]
            eL = [float(i) for i in eL[:2]]
         except: return False
         d0=abs((oL[0]-eL[0])/(oL[0]+eL[0]+eps))
         d1=abs((oL[1]-eL[1])/(oL[1]+eL[1]+eps))
         if (d0+d1<1e-6): return True
         else:            return False
   # Try two similar numbers
   try: 
      fo = float(o)
      fe = float(e)
   except: return False
   den = abs(fo) + abs(fe)
   if (den==0.): return True
   if (abs(fo-fe)/den<1e-6): return True
   return False


def convertStringToArray(string, diffrules):
   # Convert to arrays and prepare to diff
   import re
   # Excessive formatting  and line ending wankery
   string = unicode(string).replace("\r\n", "\n").replace("\r", "\n")
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


# LOCKS
def takeOutLock(lock, blame=None):
   (connection, cursor) = openaDB("lock.db")
   N = getFromDB("SELECT COUNT(*) FROM locks WHERE (id=?);", (lock,), cursor) 
   if (N != 0): return False
   cursor.execute("INSERT INTO locks (id) VALUES (?);", (lock,))
   if (blame != None): cursor.execute("INSERT INTO lockOwner (id,name) VALUES (?,?);", (lock, blame))
   gcdb(connection, cursor)
   return True

def releaseLock(lock):
   (connection, cursor) = openaDB("lock.db")
   cursor.execute("DELETE FROM locks WHERE (id=?);", (lock,))
   cursor.execute("DELETE FROM lockOwner WHERE (id=?);", (lock,))
   gcdb(connection, cursor)
   return

# Check for a lock; return False if it has been taken out
def checkLock(lock):
   (connection, cursor) = openaDB("lock.db")
   N = getFromDB("SELECT COUNT(*) FROM locks WHERE (id=?);", (lock,), cursor) 
   gcdb(connection, cursor)
   if (N == 0): return True
   else:        return False
 
# Identify the user responsible for taking a lock out
def checkLockBlame(lock):
   (connection, cursor) = openaDB("lock.db")
   blame = cursor.execute("SELECT name FROM lockOwner WHERE (id=?);", (lock,)).fetchall()
   if (len(blame)==0): return None
   else: return blame[0][0]
   
#########

def insertNewPyxplotVersionIntoDatabase(pplBinary, Nsvn, cursor):
   import shutil
   import os
   (fid, fn) = insertInPlaceFileRecord(cursor)

   # Copy the file into place
   fn = os.path.join(rootdir(), "cache", fn)
   shutil.copy(pplBinary, fn)

   # Insert into instances database
   if (Nsvn != None): 
      nameStr = "PyXPlot 0.9 svn %s"%Nsvn
   else:
      nameStr = "PyXPlot (non-svn version)"
      Nsvn = 0

   cursor.execute("INSERT INTO pplversions (name, binary, svn) VALUES (?,?,?);", (nameStr, fid, Nsvn))

# Split a set of tests up into their groups
def splitTestResultsPerGroup(results, cursor):
   out = []
   groups = cursor.execute("SELECT g.id, g.name, g.visibility FROM testGroups g;").fetchall()
   for (gid, gnam, gvis) in groups:
      group = {"id":gid, "name":gnam, "visibility":gvis, "tests":{}}
      for j in cursor.execute("SELECT tid FROM testgroupmap WHERE (gid=?);", (gid,)).fetchall():
         i = j[0]
         group["tests"][i] = results[i]
         del results[i]
      if (len(group["tests"])>0): out.append(group)
   # Gather up the remaining tests
   if (len(results)>0):
      group    = {"id":-1, "name":"Others", "visibility":1, "tests":{}}
      for i in results.keys(): group["tests"][i] = results[i]
      out.append(group)
   return out
      

def addNewTest(d, cursor):
   for i in ["name", "script"]:
      if (not i in d):
         d[i] = ""
   cursor.execute("INSERT INTO tests (name, script) VALUES (?,?);", (d["name"], d["script"]))
   tid = getFromDB('SELECT id FROM tests ORDER BY id DESC LIMIT ?;', (1,), cursor)

   # Add default output from python script
   cursor.execute("INSERT INTO outputs (tid, special, mode, diffrules) VALUES (?,?,?,?);", (tid, 0, 0, 0))

   # Add default blank output on stderr
   # XXX Need to add a blank file too
   cursor.execute("INSERT INTO outputs (tid, special, mode, diffrules) VALUES (?,?,?,?);", (tid, 1, 3, -1))
   return tid

def copyFile(fid, cursor):
   text = getFromDB("SELECT value FROM files WHERE (id=?);", (fid,), cursor)
   return insertIntoFileDB(text, cursor)

   
