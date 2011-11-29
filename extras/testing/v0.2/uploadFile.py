#!/usr/bin/python

import cgi, re, sys
from pysqlite2 import dbapi2 as sqlite
import cgitb

# Stops stdout coercing everything to ascii
reload(sys)
sys.setdefaultencoding('utf-8')

cgitb.enable()

from general import *
from web import *

# Test edit page
def uploadFile():

   # Fire up sqlite
   (connection, cursor) = openDB()
   (testConnection, testCursor) = openaDB("ppltest.db")

   # CGI output
   form = cgi.FieldStorage()

   # Warnings to return to the user
   warnings = []

   # Things to actually insert into the data base
   updates = {}

   # Check whether there is an edit to commit
   if (form.getfirst("hidden")==None):
      httpHeaders()
      page = renderFileUploadForm(id, testCursor, cursor)
      sys.stdout.write(page)
      gcdb(testConnection, testCursor)
      gcdb(connection, cursor)
      return

   # Do all the other stuff
   uploadOutcome = parseFileUploadSubmission(id, form, testCursor, warnings, updates)

   # If the instructions say to redirect the user off elsewhere, do that
   if ("redirect" in uploadOutcome):
      redirect303(uploadOutcome["redirect"])

   httpHeaders()
   page = renderFileUploadHead(id,testCursor, cursor)
   page += uploadOutcome["page"]
   # Warnings
   if (len(warnings)>0):
      page += "<h3 style='color: red'>Warnings</h3><p style='color:red'>\n"
      for warning in warnings: page += "%s<br />"%warning
      page += "</p><hr />\n"

   # If we get back from parsing the page then we need to re-issue the edit page
   page += renderFileUploadMain(testCursor,cursor,uploadOutcome["partialData"])
   gcdb(testConnection, testCursor)
   gcdb(connection, cursor)

   print page
   return

# Parse the data that we have just got back in our form
def parseFileUploadSubmission(id, form, cursor, warnings, updates):
   import os, stat
   uploadOutcome = {"partialData":{}}
   page = u''
   for key in ["name"]:
      data = form.getfirst(key)
      if (data==None): warnings.append("Failed to supply item %s to edit script!"%key)
      if (data == ""): warnings.append("Supplied empty content for %s: ignoring!"%key)
      else           : uploadOutcome["partialData"][key] = unicode(data)
   id = form.getfirst(key)
   if (id != None and id != -1): uploadOutcome["partialData"]["id"] = id
   if (len(warnings)!=0): return uploadOutcome

   # Insert the file into the database
   cursor.execute("INSERT INTO files (mode) VALUES (?);", (1,))
   id = getFromDB('SELECT id FROM files WHERE mode=? ORDER BY id DESC LIMIT 1;', (1,), cursor)
   fn = buildFileString(id)
   cursor.execute("UPDATE files SET value=? WHERE id=?;", (fn, id))

   # Write the file to disc
   fp = open(fn, "w")
   while (True):
      chunk = form["file"].file.read(100000)
      if not chunk: break
      fp.write(chunk)
   fp.close()

   # Permissions
   os.chmod(fn, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC)

   # Insert into instances database
   cursor.execute("INSERT INTO pplversions (name, binary) VALUES (?,?);", (uploadOutcome["partialData"]["name"], id))

   # We have all the required data
   page += "<p>Uploaded file %s sucessfully</p>"%(uploadOutcome["partialData"]["name"])

   uploadOutcome["page"] = page
   return  uploadOutcome



def renderFileUploadForm(id, testCursor, cursor):
   page = renderFileUploadHead(id,testCursor,cursor)
   page += renderFileUploadMain(testCursor, cursor, None)
   return page

def renderFileUploadHead(id,testCursor, cursor):
   page = makePageTop("PyXPlot test interface: Upload binary file", "index.css", cursor)
   page += "<h2>PyXPlot test interface</h2>\n"
   page += "<p>Uploading new binary file\n"
   page += "<hr>\n"
   return page




def subBut(dic):
   return u'<input type="submit" name="sub%s" value="Save" />\n'%dic["i"]
   dic["i"]+=1
   
# Produce the html for the main editor page
def renderFileUploadMain(testCursor,cursor, partialData):
   page = ''
   nsub = {"i": 0}

   if (partialData == None): partialData = {}
   # Big form'o'doom
   page += "</p>\n"
   page += '<form action="uploadFile.html" method="post" enctype="multipart/form-data" id="tehform">\n'
   if ("id" in partialData): id = partialData["id"]
   else:                     id = -1
   page += "<input type='hidden' name='id' value='%s' />\n"%(id)
   page += "<input type='hidden' name='hidden' value='a' />\n"
   page += subBut(nsub)

   # Render the obvious content
   val = ""
   if ("name" in partialData): val = partialData["name"]
   page += renderInputControlFromString("name", "Release Name", 50, 0, val)
   page += "<br />"
   page += '<input type="file" name="file" />'
   page += subBut(nsub)
   page += '</p></form>'

   # page += "<p><a href='edit.py'>clear</a></p>\n"
   page += getFromDB('SELECT text FROM htmlchunks WHERE (name=?);',("footer",),cursor)
   return page


uploadFile()

def bar():
   # The ingredients.  Pain and suffering.
   page += '<h3>Ingredients</h3><input type="submit" name="sub1" value="Save changes" /><br />\n'
   # First fetch all the sub-recipes
   subrlist = cursor.execute("SELECT id,sort,name1,name2 FROM subrecipes WHERE rid=? ORDER BY sort;", (id,)).fetchall()
   for subr in subrlist:
      page += "Section heading<br />\n"
      tlist = [""]
      if (subr[2]==None): tlist.append("")
      else              : tlist.append(subr[2])
      tlist.append(None)
      tlist.append(None)
      if (subr[3]==None): tlist.append("")
      else              : tlist.append(subr[3])
      page += renderIngredientLine(subr[0],tlist)
      page += "Ingredients<br />\n"

      # For each sub-test fetch the ingredientlines
      illist = cursor.execute("SELECT il.id,il.quantity,il.main,il.ingredient,ig.name FROM ingredientlines il LEFT JOIN ingredientlinesmap ilm ON (il.id=ilm.ilid) LEFT JOIN ingredients ig ON ig.id=il.ingredient WHERE ilm.srid=? ORDER BY ilm.sort;", (subr[0],)).fetchall()
      for il in illist: page += renderIngredientLine(subr[0],il)

      # Blank lines for fresh ingredients
      for i in range(5): page += renderIngredientLine(subr[0],["new%s"%i,"","FALSE","",""])
   # One blank subrecipe line
   page += "New section heading<br />\n"
   page += renderIngredientLine("new", ["", "", "FALSE", "", ""])

        


   page += '<h3>Test method</h3><input type="submit" name="sub2" value="Save changes" /><br />\n'
   page += renderInputControl("method", "Method", 100, 50, id, cursor)

