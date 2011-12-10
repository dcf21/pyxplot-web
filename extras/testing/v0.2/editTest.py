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
def editTest():

   # Fire up sqlite
   (connection, cursor) = openDB()
   (testConnection, testCursor) = openaDB("ppltest.db")

   # Check for the id number and sanitise it
   form = cgi.FieldStorage()
   id = form.getfirst("id")
   if (id==None): 
      errPage("Error: You have not supplied the id of the page that you would like to edit!")
      exit()
   if (not re.match("[0-9]+$", id)):
      errPage("Error: you have supplied an invalid test id.  Test IDs must be positive integers")
      exit()
   
   # Check that this test exists
   try: test = getFromDB("SELECT id FROM tests WHERE id IS ?;", (id,), testCursor)
   except: 
      errPage("Error: you are trying to edit a test that doesn't exist.")
      exit()


   # Warnings to return to the user
   warnings = []

   # Things to actually insert into the data base
   updates = {}

   # Check whether there is an edit to commit
   if (form.getfirst("hidden")==None):
      httpHeaders()
      page = renderTestEditForm(id, testCursor, cursor)
      sys.stdout.write(page)
      # except: headlessErrPage("Failed to render the test edit form!")
      gcdb(testConnection, testCursor)
      gcdb(connection, cursor)
      return

   # Do all the other stuff
   httpHeaders()
   page = renderTestEditHead(id,testCursor, cursor)
   page += parseTestEditSubmission(id, form, testCursor, warnings, updates)
   # Warnings
   if (len(warnings)>0):
      page += "<h3 style='color: red'>Warnings</h3><p style='color:red'>\n"
      for warning in warnings: page += "%s<br />"%warning
      page += "</p><hr />\n"

   # If we get back from parsing the page then we need to re-issue the edit page
   page += renderTestEditMain(id,testCursor,cursor)
   gcdb(testConnection, testCursor)
   gcdb(connection, cursor)

   print page
   return

# Parse the data that we have just got back in our form
def parseTestEditSubmission(id, form, cursor, warnings, updates):
   page = u''
   for key in ["name", "mode", "script"]:
      data = form.getfirst(key)
      if (data==None): headlessErrPage("Failed to supply item %s to edit script!"%key)
      if (data == ""): warnings.append("Supplied empty content for %s: ignoring!"%key)
      else           : updates[key] = unicode(data)

   # Update test
   for key in updates.keys(): cursor.execute("UPDATE tests SET %s = ? WHERE id IS ?;"%(key), (updates[key], id, ))

   postkeys = form.keys()

   # Test inputs
   iids = cursor.execute("SELECT id, special FROM inputs WHERE (tid=?);", (id,)).fetchall()
   # Loop over exected test inputs
   for (iid,oldspecial) in iids:
      prefix =  "inp_%s_"%(iid)
      special = form.getfirst("%s%s"%(prefix,"special"))
      if (special != oldspecial and special != None):
         cursor.execute("UPDATE inputs SET special = ? WHERE (id=?);", (special, iid))

   # New test input
   new = []
   prefix = "inp_-1_"
   for i in ["special", "filename", "selfn", "text"]:
      j = form.getfirst("%s%s"%(prefix, i))
      if (j==None): new.append("")
      else: new.append(j)
   # Test for incomplete data
   (special, filename, selfn, text) = new
   #if (None in new):
   #   warnings.append("Partial content recieved for new input: skipping")
   # Check that we have some content
   if (filename != ""):
      fid = insertIntoFileDB(text, cursor)
      cursor.execute("INSERT INTO inputs (tid,fid,filename,special) VALUES (?,?,?,?);", (id,fid,filename,special))
   elif (selfn != ""):
      (fid, filename) = cursor.execute("SELECT fid, filename FROM inputs WHERE (id=?);", (selfn,)).fetchall()[0]
      cursor.execute("INSERT INTO inputs (tid,fid,filename,special) VALUES (?,?,?,?);", (id,fid,filename,special))
      srgjnirjn=1
   elif (special == "0"):
      fid = insertIntoFileDB(text, cursor)
      cursor.execute("INSERT INTO inputs (tid,fid,filename,special) VALUES (?,?,?,?);", (id,fid,filename,special))


   # Old test outputs
   oids = cursor.execute("SELECT id, special, mode, fid, filename,diffrules FROM outputs WHERE (tid=?);", (id,)).fetchall()
   # Loop over exected test inputs
   for (oid, osp, omd, ofid, ofn, odr) in oids:
      prefix =  "oup_%s_"%(oid)

      for (field, value) in [["special", osp], ["filename",ofn], ["mode",omd]]:
         newval = form.getfirst("%s%s"%(prefix,field))
         if (newval != value and newval != None): cursor.execute("UPDATE outputs SET %s = ? WHERE (id=?);"%(field), (newval, oid))

      # Content if comparing against stored content
      if (omd==1):
         outputCmpTxt = form.getfirst("%s%s"%(prefix,"outcmptxt"))
         if (fid<0): # New file
            if (outputCmpTxt==None): outputCmpTxt = ""
            cursor.execute("INSERT INTO files (mode,value) VALUES (?,?);", (0,outputCmpTxt))
            fid = cursor.execute("SELECT id FROM files WHERE (mode=? AND value=?);", (mode, outputCmpTxt)).fetchall()[-1]
         elif (outputCmpTxt != None):
            cursor.execute("UPDATE files SET value=? WHERE (id=?);", (fid, outputCmpTxt))

      # Diff rules content
      nodr = form.getfirst("%s%s"%(prefix, "diffrules"))
      if (nodr != None):
         nodr = int(nodr)-1
         if (nodr < 1):
            if (nodr != odr): cursor.execute("UPDATE outputs SET diffrules=? WHERE (id=?);", (nodr, oid))
         else:
            drtxt = form.getfirst("%s%s"%(prefix,"diffrutxt"))
            if (drtxt != None):
               if (odr<1): # Completely new diff rules
                  cursor.execute("INSERT INTO diffrules (rules) VALUES (?);", (drtxt,))
                  nodr = cursor.execute("SELECT id FROM diffrules WHERE (rules=?);", (drtxt,)).fetchall()[-1]
                  cursor.execute("UPDATE outputs SET diffrules = ? WHERE (id=?);", (nodr, oid))
               else: # Possibly changed diff rules
                  cursor.execute("UPDATE diffrules SET rules=? WHERE (id=?);", (drtxt, odr))

   # New test outputs
   new = []
   prefix = "oup_-1_"
   for i in ["special", "filename", "mode", "outcmptxt", "diffrules", "diffrutxt"]:
      j = form.getfirst("%s%s"%(prefix, i))
      if (j==None): new.append("")
      else: new.append(j)
   (special, filename, mode, outcmptxt, diffrules, diffrutxt) = new
   diffrules = int(diffrules)-1
   #if (None in new):
   #   warnings.append("Partial content recieved for new output: skipping")
   # Check for some content
   if (special != "2" or filename != ""):
      cursor.execute("INSERT INTO files (mode, value) VALUES (?,?);", (0,outcmptxt))
      fid = cursor.execute("SELECT id FROM files WHERE (mode=? AND value=?);", (0, outcmptxt)).fetchall()[-1][0]
      if (diffrules == "1"):
         cursor.execute("INSERT INTO diffrules (rules) VALUES (?);", (diffrutxt,))
         diffrules = cursor.execute("SELECT id FROM diffrules WHERE (rules=?);", (diffrutxt,)).fetchall()[-1]
      cursor.execute("INSERT INTO outputs (tid, special, mode, fid, filename, diffrules) VALUES (?,?,?,?,?,?);", (id, special, mode, fid, filename, diffrules))
      
   # Wrap up and go home
   page += "<p>"
   postkeys.sort()
   for i in postkeys: page = "%s %s &nbsp;"%(page,i)
   return "%s</p>"%page 


         

        

      
      
      




def renderTestEditForm(id, testCursor, cursor):
   page = renderTestEditHead(id,testCursor,cursor)
   page += renderTestEditMain(id,testCursor, cursor)
   return page

def renderTestEditHead(id,testCursor, cursor):
   name = getFromDB("SELECT name FROM tests WHERE id=?;", (id, ), testCursor)
   page = makePageTop("PyXPlot test interface: edit test", "index.css", cursor)
   page += "<h2>PyXPlot test interface</h2>\n"
   page += "<p>Editing test id %s\n"%(id)  #  (<a href='../tests/%s' target='_blank'>view test</a> | <a href='edit.py?id=%s'>reload</a> discarding unsaved changes ).  Go to <a href='editors.py' target='_blank'>editors' interface</a></p>\n"%(id,filename,id)
   page += "<hr>\n"
   return page




def subBut(dic):
   return u'<input type="submit" name="sub%s" value="Save" />\n'%dic["i"]
   dic["i"]+=1
   
# Produce the html for the main editor page
def renderTestEditMain(id,testCursor,cursor):
   page = ''
   nsub = {"i": 0}
   # Big form'o'doom
   page += "</p>\n"
   page += '<form action="editTest.html" method="post" id="tehform">\n'
   page += "<input type='hidden' name='id' value='%s' />\n"%(id)
   page += "<input type='hidden' name='hidden' value='a' />\n"
   page += subBut(nsub)

   # Render the obvious content
   page += renderInputControl("name", "tests", "Test name", 100, 0, id, testCursor)
   page += "<br />"
   mode = getFromDB("SELECT mode FROM tests WHERE id IS ?", (id,), testCursor)
   page += renderRadioButton("Mode", "mode", mode, ["normal", "require no error", "require error"])
   # page += 'Visible: <input type="checkbox" name="visible" %s /><br />'%(visible)
   page += subBut(nsub)
   page += renderInputControl("script", "tests", "Script", 100, 10, id, testCursor)
   page += "<br />"

   # Inputs
   page += renderTestInputs(id, testCursor,cursor, nsub)

   # Outputs
   page += renderTestOutputs(id, testCursor, cursor, nsub)


   page += subBut(nsub)
   page += '</p></form>'

   # page += "<p><a href='edit.py'>clear</a></p>\n"
   page += getFromDB('SELECT text FROM htmlchunks WHERE (name=?);',("footer",),cursor)
   return page


def renderTestOutputs(id, testCursor, cursor, nsub):
   # Render pre-existing inputs
   text = u"<hr /><b>Outputs</b><br />\n"
   for outpt in testCursor.execute("SELECT id, filename, special, mode, fid, diffrules  FROM outputs WHERE (tid=?);", (id,)).fetchall():
      text += renderTestOutput(id,outpt,testCursor)
   # Render a blank output
   text += renderTestOutput(id,[-1,"",2,0,-1,-1], testCursor)
   return text

def renderTestOutput(id, data,testCursor):
   text = u""
   (oid, ofn, osp, omd, ofid, odif) = data
   prefix = u"oup_%s_"%oid
   # Radio button for special
   text += renderRadioButton("Output", "%s%s"%(prefix,"special"), osp, ["stdout", "stderr", "file"])
   # Filename
   text += renderInputControlFromString("%s%s"%(prefix,"filename"), "", 50, 0, ofn)
   text += "<br />"
   # Mode
   text += renderRadioButton("Mode", "%s%s"%(prefix,"mode"), omd, ["Compare against previous", "Compare against stored output"])
   text += "<br />"

   # Comparison text
   if (omd==1):
      fout = testCursor.execute("SELECT mode, value FROM files WHERE (id=?);", (ofid,)).fetchall()[0]
      if (len(fout)==0):
         fmode = 0
         fval = ""
      else:
         (fmode, fval) = fout
   else:
      fmode = 0
      fval = ""
   # XXX we don't support fmode=1 (file kept on disc) yet

   assert(fmode==0)
   text += renderInputControlFromString("%s%s"%(prefix,"outcmptxt"), "Stored value", 50, 10, fval)
   text += "<br />"

   # Existing: look up diff rules
   odifp = odif+1
   if (odif>0):
      odifp = 2
      diffrules = getPossibleItemFromDB("SELECT rules FROM diffrules WHERE (id=?);", (odif,), testCursor)
      if (diffrules == None): diffrules = ""
   else:
      diffrules = ""
   
   text += renderRadioButton("Diff rules", "%s%s"%(prefix, "diffrules"), odifp, ["Default", "None", "Custom (below)"])
   text += renderInputControlFromString("%s%s"%(prefix,"diffrutxt"), "", 50, 4, diffrules)

   
   return text


def renderTestInputs(id, testCursor, cursor, nsub):
   # Render pre-existing inputs
   text = u"<hr /><b>Inputs</b><br />\n"
   for inpt in testCursor.execute("SELECT id, filename, special  FROM inputs WHERE (tid=?);", (id,)).fetchall():
      text += renderTestInput(id,inpt,testCursor)
   # Render a blank input
   text += renderTestInput(id,[-1,"",1], testCursor)
   return text

def renderTestInput(id, data,testCursor):
   text = u""
   iid = data[0]
   ifn = data[1]
   isp = data[2]
   prefix = u"inp_%s_"%iid
   # Radio button
   text += renderRadioButton("Input", "%s%s"%(prefix,"special"), isp, ["stdin", "file"])
   # Existing input: Cannot choose filename
   if (iid>=0):
      text += "Filename: %s<br />"%(ifn)
   else:
      # Filename box
      text += renderInputControlFromString("%s%s"%(prefix,"filename"), "", 50, 0, ifn)
      # Option box
      text += renderOptionBox("filename", "inputs", "%s%s"%(prefix, "selfn"), ["", ""], testCursor)
      text += "<br />"
      # Contents
      text += renderInputControlFromString("%s%s"%(prefix,"text"), "File contents", 100, 10, "")
      text += "<br />"
   return text


      



editTest()

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
