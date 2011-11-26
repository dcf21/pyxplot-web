# This file contains shared routines for database handling for the great pyxplot testing system

# Open any named db
def openaDB(dbname):
   import os
   from pysqlite2 import dbapi2 as sqlite
   # connection = sqlite.connect("/home/ftcb/ftcb/ftcb.db")
   connection = sqlite.connect(os.environ["HOME"] + "/sw/pyxplot/extras/testing/v0.2/" + dbname)
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
           
