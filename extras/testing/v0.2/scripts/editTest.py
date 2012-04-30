#!/usr/bin/env python2.6

import cgi, re, sys
from pysqlite2 import dbapi2 as sqlite
import cgitb

# Stops stdout coercing everything to ascii
reload(sys)
sys.setdefaultencoding('utf-8')

cgitb.enable()

from general import *
from web import *

divcount = 0

# Test edit page
def editTest():

   testBigLock()

   # Fire up sqlite
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
      (connection, cursor) = openDB()
      page = renderTestEditForm(id, testCursor, cursor)
      sys.stdout.write(page)
      # except: headlessErrPage("Failed to render the test edit form!")
      gcdb(testConnection, testCursor)
      gcdb(connection, cursor)
      return

   # Do all the other stuff
   testEditFallout = parseTestEditSubmission(id, form, testCursor, warnings, updates)
   # Set the test as "new" as it has been edited
   testCursor.execute("UPDATE insttestmap SET state=? WHERE (tid=?);", (1, id))

   # Check to see if the page wanted us to be re-directed away 
   if ("redirect" in testEditFallout):
      gcdb(testConnection, testCursor)
      redirect303(testEditFallout["redirect"])
   # Other fallout work will go here
   (connection, cursor) = openDB()
   page = renderTestEditHead(id,testCursor, cursor)
   if ("text" in testEditFallout): page += testEditFallout["text"]
   # Warnings
   if (len(warnings)>0):
      page += "<h3 style='color: red'>Warnings</h3><p style='color:red'>\n"
      for warning in warnings: page += "%s<br />"%warning
      page += "</p>\n"

   # If we get back from parsing the page then we need to re-issue the edit page
   page += renderTestEditMain(id,testCursor,cursor)
   gcdb(testConnection, testCursor)
   gcdb(connection, cursor)

   httpHeaders()
   print page
   return

# Parse the data that we have just got back from the test edit form
def parseTestEditSubmission(id, form, cursor, warnings, updates):
   for key in ["name", "mode", "script"]:
      data = form.getfirst(key)
      if (data == "" or data == None): warnings.append("Supplied empty content for %s: ignoring!"%key)
      else                           : updates[key] = unicode(data).replace(u'\r\n', u'\n')

   # Deal with group input XXX
   group = form.getfirst("testGroup")
   if (group!=None):
      try: 
         group = int(group)
         cursor.execute("DELETE FROM testgroupmap WHERE (tid=?);", (id,))
         cursor.execute("INSERT INTO testgroupmap (tid, gid) VALUES (?,?);", (id, group))
      except:
         pass

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
         if (ofid<0): # New file
            if (outputCmpTxt==None): outputCmpTxt = ""
            cursor.execute("INSERT INTO files (mode,value) VALUES (?,?);", (0,outputCmpTxt))
            ofid = cursor.execute("SELECT id FROM files WHERE (mode=? AND value=?);", (mode, outputCmpTxt)).fetchall()[-1]
         elif (outputCmpTxt != None):
            cursor.execute("UPDATE files SET value=? WHERE (id=?);", (outputCmpTxt, ofid))

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
   if (mode == "0" and outcmptxt != ""):
      warnings.append("Output comparison text supplied: reverting to specified output")
      mode = "1"
   if (special != "2" or filename != ""):
      cursor.execute("INSERT INTO files (mode, value) VALUES (?,?);", (0,outcmptxt))
      fid = cursor.execute("SELECT id FROM files WHERE (mode=? AND value=?);", (0, outcmptxt)).fetchall()[-1][0]
      if (diffrules == "1"):
         cursor.execute("INSERT INTO diffrules (rules) VALUES (?);", (diffrutxt,))
         diffrules = cursor.execute("SELECT id FROM diffrules WHERE (rules=?);", (diffrutxt,)).fetchall()[-1]
      cursor.execute("INSERT INTO outputs (tid, special, mode, fid, filename, diffrules) VALUES (?,?,?,?,?,?);", (id, special, mode, fid, filename, diffrules))
      
   # Find the submit button
   subs = []
   output = {}
   for i in postkeys:
      if (re.match("sub", i)): subs.append(i)
   if (len(subs) > 0):  # Should never have more than one of these in normal usage
      submb = subs[0][:-1]   # Chop off the terminal digit
      if (submb == "sub"): return output
      if (submb == "subRun"):
         runTestOnAllVersions(id, cursor)
         output["redirect"] = "mainPage.html"
         return output
      if (submb == "subRet"):
         output["redirect"] = "mainPage.html"
         return output
      mg = re.match(r"sub_del_([io][nu])p_([0-9]+)$", subs[0])
      if (mg != None):
         if (mg.group(1)=="in"):
            deleteTestInput(int(mg.group(2)), cursor)
            return output
         elif (mg.group(1)=="ou"):
            deleteTestOutput(int(mg.group(2)), None, cursor)
            return output

         

   # Wrap up and go home
   page = u''
   page += "<p>"
   postkeys.sort()
   for i in postkeys: page = "%s %s &nbsp;"%(page,i)
   output["text"] = "%s</p>"%page 
   return output


def renderTestEditForm(id, testCursor, cursor):
   page = renderTestEditHead(id,testCursor,cursor)
   page += renderTestEditMain(id,testCursor, cursor)
   return page

def renderTestEditHead(id,testCursor, cursor):
   name = getFromDB("SELECT name FROM tests WHERE id=?;", (id, ), testCursor)
   page = makePageTop("Edit test", "index.css", cursor)
   return page


def subBut(dic):
   dic["i"]+=1
   text =  u'<input type="submit" name="sub%s" value="Save" />\n'%dic["i"]
   text += u'<input type="submit" name="subRun%s" value="Save and run" />\n'%dic["i"]
   text += u'<input type="submit" name="subRet%s" value="Save and return" />\n'%dic["i"]
   return text
   
# Produce the html for the main editor page
def renderTestEditMain(id,testCursor,cursor):
   global divcount
   page = ''
   nsub = {"i": 0}
   # Test group id (if any)
   gid = getPossibleItemFromDB("SELECT gid FROM testGroupMap WHERE (tid=?);", (id,), testCursor)
   if (gid==None): gid = ""

   # Big form'o'doom
   page += '</p>\n<div id="testEditForm">\n'
   page += '<form action="editTest.html" method="post" id="tehform">\n'
   page += "<input type='hidden' name='id' value='%s' />\n"%(id)
   page += "<input type='hidden' name='hidden' value='a' />\n"

   # Render the obvious content
   page += u'<div class="colourBox%s"><b>Basic data (test id=<span class="hl%s">%s</span>)</b>\n'%(dvcount(), divcount,id)
   page += subBut(nsub)
   page += u'<div class="lrel">\n'
   page += renderInputControl("name", "tests", "Test name", 100, 0, id, testCursor)
   page += "Group:" + renderOptionBox("name", "testGroups", "testGroup", ["",gid], testCursor)
   page += "</div>"
   mode = getFromDB("SELECT mode FROM tests WHERE id IS ?", (id,), testCursor)
   page += u'<div class="lrel">\n'
   page += renderRadioButton("Mode", "mode", mode, ["normal", "require no error", "require error"])
   page += "</div>"
   page += "</div>"
   # page += 'Visible: <input type="checkbox" name="visible" %s /><br />'%(visible)

   # Script and inputs
   page += u'<div class="colourBox%s"><b>Inputs</b>\n'%(dvcount())
   page += subBut(nsub)
   page += u'<div class="lrel">\n'
   page += u'<div class="colourSubBox%s">\n'%(divcount)
   # page += '<div class="colourBox%s">\n'%(dvcount())
   page += renderInputControl("script", "tests", "Script", 50, 10, id, testCursor)
   page += u'</div>'

   # Inputs
   page += renderTestInputs(id, testCursor,cursor, nsub)

   # Outputs
   page += renderTestOutputs(id, testCursor, cursor, nsub)


   page += subBut(nsub)
   page += '</form></div>'

   # page += "<p><a href='edit.py'>clear</a></p>\n"
   page += getFromDB('SELECT text FROM htmlchunks WHERE (name=?);',("footer",),cursor)
   return page


def renderTestOutputs(id, testCursor, cursor, nsub):
   text = u'<div class="colourBox%s"><b>Outputs</b>\n'%(dvcount())
   text += subBut(nsub)
   text += u'<div class="lrel">\n'
   # Render a blank output
   text += renderTestOutput(id,[-1,"",2,0,-1,-1], testCursor)
   Noup = 1
   # Render pre-existing outputs
   for outpt in testCursor.execute("SELECT id, filename, special, mode, fid, diffrules  FROM outputs WHERE (tid=?);", (id,)).fetchall():
      text += renderTestOutput(id,outpt,testCursor)
      Noup += 1
      if (Noup % 2 == 0):
         text += u'<div class="cl"></div></div>\n<div class="lrel">\n'
   text += '<div class="cl"></div></div>\n</div>\n'
   return text

def renderTestOutput(id, data,testCursor):
   global divcount
   (oid, ofn, osp, omd, ofid, odif) = data
   prefix = u"oup_%s_"%oid
   # Radio button for special
   if (int(oid)==-1): 
      tmp = "New output"
      dc = 2
      removeString = u""
   else:              
      tmp = "Old output"
      dc = divcount
      removeString = u'<input type="submit" name="sub_del_%s" value="Remove" />'%(prefix[:-1])
   text = u'<div class="colourSubBox%s">\n'%(dc)
   temp = renderRadioButton(tmp, "%s%s"%(prefix,"special"), osp, ["stdout", "stderr", "file"])
   # Filename
   temp += renderInputControlFromString("%s%s"%(prefix,"filename"), "", 50, 0, ofn)
   temp += removeString
   text += divit(temp, "lrel")
   # Mode
   text += divit(renderRadioButton("Compare output against", "%s%s"%(prefix,"mode"), omd, ["Last passed", "Specified", "Autogenerated", "Blank"]), "lrel")

   # Comparison text
   if (omd==1):
      fout = testCursor.execute("SELECT mode, value FROM files WHERE (id=?);", (ofid,)).fetchall()[0]
      if (len(fout)==0): fout = [0, ""]
      (fmode, fval) = fout
   else:
      fmode = 0
      fval = ""

   # XXX we don't support fmode=1 (file kept on disc) yet
   assert(fmode==0)
   text += renderInputControlFromString("%s%s"%(prefix,"outcmptxt"), "Specified output", 50, 10, fval)
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

   text += "</div>\n"
   return text

def dvcount():
   global divcount
   divcount = (divcount+1)%2
   return divcount

def renderTestInputs(id, testCursor, cursor, nsub):
   # text = u'<div class="colourBox%s"><b>Inputs</b><br />\n'%(dvcount())
   # Render a blank input
   text = renderTestInput(id,[-1,"",1, None], testCursor)
   text += u'<div class="cl"></div></div>\n<div class="lrel">\n'
   Ninp = 0
   # Render pre-existing inputs
   for inpt in testCursor.execute("SELECT id, filename, special, fid  FROM inputs WHERE (tid=?);", (id,)).fetchall():
      text += renderTestInput(id,inpt,testCursor)
      Ninp += 1
      if (Ninp % 2 == 0):
         text += u'<div class="cl"></div></div>\n<div class="lrel">\n'
   text += '<div class="cl"></div></div>\n</div>\n'
   return text

def renderTestInput(id, data,testCursor):
   global divcount
   iid = data[0]
   ifn = data[1]
   isp = data[2]
   fid = data[3]
   prefix = u"inp_%s_"%iid
   # First line: radio button and fileanme input
   # Radio button
   if (iid>=0):
      # Existing input: Cannot choose filename
      dc = divcount
      temp1 = divit("Existing input %s"%([": stdin", ""][isp]),"linl")
      if (isp==1): temp1 += divit(' file: <span class="hl%s">%s</span>'%(dc,ifn),"linl")
      temp1 += u'<input type="submit" name="sub_del_inp_%s" value="Remove" />'%(iid)
      if (fid==None): temp2 = u""
      else:
         oldFileContents = obtainFileContentsFromDB(fid, testCursor)
         llen = 40
         lines = oldFileContents.split("\n")
         for l in lines:
            if (len(l)>llen): llen = len(l)
         Nlines = 5
         if (len(lines)>5): Nlines = len(lines)
         temp2 = divit(renderInputControlFromString("%s%s"%(prefix,"text"), "File contents", llen, Nlines, cgi.escape(oldFileContents,True)), "lrel")
   else:
      # Filename box and option box (XXX WTF Firefox)
      dc = 2
      temp1 = divit(renderRadioButton("New input", "%s%s"%(prefix,"special"), isp, ["stdin", "file"]),"linl")
      temp = renderInputControlFromString("%s%s"%(prefix,"filename"), "Filename", 50, 0, ifn)
      temp += renderOptionBox("filename", "inputs", "%s%s"%(prefix, "selfn"), ["", ""], testCursor)
      temp1 += divit(temp,"linl")
      # Contents
      temp2 = divit(renderInputControlFromString("%s%s"%(prefix,"text"), "File contents", 50, 10, ""), "lrel")
   text = u'<div class="colourSubBox%s">\n'%(dc)
   text += (divit(temp1, "lrel") + temp2 + "</div>\n")
   return text

editTest()

