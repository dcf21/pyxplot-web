# This file contains shared routines for database handling for the great pyxplot testing system

subdir = "/ppltest/"

# Open any named db
def openaDB(dbname):
   import os
   from pysqlite2 import dbapi2 as sqlite
   global subdir
   # connection = sqlite.connect("/home/ftcb/ftcb/ftcb.db")
   connection = sqlite.connect(os.environ["HOME"] + subdir  + dbname)
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

def workdir():
   import os
   global subdir
   return os.environ["HOME"] + subdir

# Produce a file string for a file id
def buildFileString(id):
   return workdir() + "cache/cache.%s"%(id) 

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
   import os, os.path
   lines = []
   for line in script.split("\n"):
      if (line==""): continue
      lines.append("print %s"%line)
   # If some script has been generated, run it and return the output
   if (len(lines)>0):
      pythonScript = "\n".join(lines)
      fn = os.path.join(workdir, "script.py")
      fp = open(fn, "w")
      fp.write(pythonScript)
      fp.close()
      os.system("cd %s ; python script.py > script.out"%(workdir))
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
   if (idr==0): diffrules = []
   elif (idr==-1):    # Default diff rules
      if (special!=2): diffrules = []
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

def convertStringToArray(string, diffrules):
   # Convert to arrays and prepare to diff
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
def takeOutLock(lock):
   (connection, cursor) = openaDB("lock.db")
   N = getFromDB("SELECT COUNT(*) FROM locks WHERE (id=?);", (lock,), cursor) 
   if (N != 0): return False
   cursor.execute("INSERT INTO locks (id) VALUES (?);", (lock,))
   gcdb(connection, cursor)
   return True

def releaseLock(lock):
   (connection, cursor) = openaDB("lock.db")
   cursor.execute("DELETE FROM locks WHERE (id=?);", (lock,))
   gcdb(connection, cursor)
   return

#########
def addNewTest(d, cursor):
   for i in ["name", "script"]:
      if (not i in d):
         d[i] = ""
   cursor.execute("INSERT INTO tests (name, script) VALUES (?,?);", (d["name"], d["script"]))
   return
