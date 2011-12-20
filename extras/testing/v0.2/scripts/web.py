# This file contains shared web routines for the great pyxplot testing system

from general import *
import cgi

cookie = None

def openDB():
   return openaDB("webstuff.db")

def err404Page(cursor):
   page = "Status: 404\n"
   page += makeHttpHeaders()
   page += makePageTop("Error 404: page not found", None, cursor)
   page += "<h1>Error 404:  page not found</h1>\n"
   page += "<p>Unfortunately the page you were looking for on the fair trade cook book could not be found</p>\n"
   page += getFromDB('SELECT text FROM htmlchunks WHERE (name=?);',("footer",),cursor)
   cursor.close()
   print page
   exit(0)

def redirect303(address):
   page = "Status: 303\n"
   page += "Location: %s\n"%address
   page += makeHttpHeaders()
   print page
   exit(0)

def errPage(err):
   httpHeaders()
   headlessErrPage(err)

def headlessErrPage(err):
   print "<html><head>Error!</head><body>\n"
   print "%s\n"%err
   print "</body></html>\n"
   exit()

def httpHeaders():
   print makeHttpHeaders()

def makeHttpHeaders():
   str=u"Content-Type: text/html; charset=UTF-8\n"
   # str += cookie.output()
   str += "\n\n"     # HTML follows
   return str

# Wrap something in a simple div
def divit(text, dname):
   return u'<div class="%s">%s</div>\n'%(dname, text)


# Make the stuff at the top of all the pages
def makePageTop(title, css, cursor, headExtra = ""):
   import re
   text = u""
   # Pre-title text
   text += getFromDB('SELECT text FROM htmlchunks WHERE (name=?);',("pretitlehead",),cursor)
   text += u"PyXPlot test interface: %s"%title
   # Post-title
   text += getFromDB('SELECT text FROM htmlchunks WHERE (name=?);',("posttitlehead",),cursor)
   # Ugly hack!
   if (css != None): text = re.sub(r"recipe.css", css, text)
   text += u'<h2><a href="mainPage.html">PyXPlot test interface</a>: %s</h2>\n'%(title)
   # And another one!
   text = re.sub(r"</head>", headExtra + "</head>", text)
   return text

def makePageHead(title, cursor):
   text = u""
   text += getFromDB('SELECT text FROM htmlchunks WHERE (name=?);',("pretitlehead",),cursor)
   text += title
   text += getFromDB('SELECT text FROM htmlchunks WHERE (name=?);',("posttitlehead",),cursor)
   return text

# This routine does all the work
# params: dict of {key: value} pairs containing any information needed
# content: a string containing content to put into the main body of the page
# cursor: db cursor
def makePage(params, content, cursor):
   page = ""

   # Sanity check of some things in params
   try:    
      title = params["title"]
      assert(len(title)>0)
   except: errPage("Unexpected internal error: No page title")

   try: 
      active = params["active"]
      assert(len(active)>0)
   except: errPage("Unexpected internal error: no active list")

   # Head section
   page += makePageHead(title, cursor)

   # Body section
   page += '<div id="page-container">\n'
   
   # # Sidebar
   # # page += '<div id="sidebar">\n'
   # page += getFromDB('SELECT text FROM htmlchunks WHERE (name=?);', ("sidebartop",), cursor)
   # page += makeSideBarContent(active, cursor)
   # page += '</div>'   # End of side bar

   # # Top navigation
   # page += makeNavTop(active, cursor)

   # Content
   page += '<div id="content">\n'
   page += content
   page += '</div>\n'

   # May at a later date want to do something funky in the footer
   page += makePageFoot(cursor)

   # Now print the page
   httpHeaders()
   print page

   return

def makePageFoot(cursor):
   return getFromDB('SELECT text FROM htmlchunks WHERE (name=?);',("footer",),cursor)


def initialiseCookie():
   import os
   import Cookie
   from pysqlite2 import dbapi2 as sqlite

   global cookie

   # Open the session database
   (sessionConnection, sessionCursor) = openaDB("session.db")
   try: 
      cookie = Cookie.SimpleCookie(os.environ["HTTP_COOKIE"])
   except:
      # There is no cookie yet
      cookie = Cookie.SimpleCookie()
   # Try to extract the session ID
   try: 
      session = cookie["session"].value
   except:
      session = makeNewSession(sessionCursor)
      cookie["session"] = session

   sessionCursor.close()
   sessionConnection.commit()
   sessionConnection.close()

   return



def makeNewSession(sessionCursor):
   count = 2
   while (count > 1):
      tstring = getFromDB('SELECT datetime("now");', (), sessionCursor)
      sessionCursor.execute("INSERT INTO session (atime,mtime,ctime) VALUES (?,?,?);", (tstring,tstring,tstring,))
      count = getFromDB("SELECT COUNT(id) FROM session WHERE atime=? AND mtime=? AND ctime=?;", (tstring,tstring,tstring,), sessionCursor)
   id = getFromDB("SELECT id FROM session WHERE atime=? AND mtime=? AND ctime=?;", (tstring,tstring,tstring,), sessionCursor)
   return id

def renderInputControl(field, table, name, w, h, id, cursor):
   val = getFromDB("SELECT %s FROM %s WHERE id IS ?;"%(field,table), (id,), cursor)
   text = u''
   # text = u'<p>val=%s table=%s field=%s</p>'%(val,table,field)
   text += renderInputControlFromString(field, name, w, h, val)
   return text

def renderInputControlFromString(formname, name, w, h, val):
   if (h==0): return '<div class="linl">%s: <input type="text" name="%s" value="%s" size="%s" /></div>\n'%(name, formname, cgi.escape(val,True),w)
   else     : return '<div class="linl">%s</div>\n<div class="lrel"><textarea name="%s" rows="%s" cols="%s" >\n%s\n</textarea></div>\n'%(name,formname,h,w,cgi.escape(val,True))

def renderOptionBox(field, table, formname, default, cursor):
   options = cursor.execute("SELECT %s,id FROM %s;"%(field,table)).fetchall()
   text = u'<select name="%s">\n'%(formname)
   found = False
   for option in options:
      if (option[1] == default[1]):
         sel = ' selected="selected"'
         found = True
      else:
         sel = ""
      text += '<option %s label="%s" value="%s" />\n'%(sel,option[0],option[1])
   if (not found):
      text += '<option selected="selected" label="%s" value="%s" />\n'%(default[0],default[1])
   text += "</select>\n"
   return text


def renderRadioButton(name, formname, value, options):
   text = u"%s: "%name
   for i in range(len(options)):
      if (i==value): chk = 'checked="checked"'
      else         : chk = ""
      text += '<input type="radio" name="%s" value="%s" %s />%s\n'%(formname,i,chk,options[i])
   return text



######################################
# New for the ppl website

  

######################################
# Stuff that I probably won't want

def makeMenuBar(active, cursor):
   bar = u"<table class=\"strip\">\n"
   # Make strip 1
   items = cursor.execute("SELECT name,page FROM pages ORDER BY id;")
   list = []
   for (name,page) in items: list.append([name, "../pages/%s"%page])
   bar += makeMenuStrip(list, active[0])
   # Spacer
   bar += "<tr><td>&nbsp;</td></tr>\n"
   # Make strip 2
   list = [("Alphabetical", "../alphabetic_index/a.htm"), ("By Course", "../courses_index/starters.htm"), ("Geographical", "../indices/region_index.htm"), ("Search", "../pages/search.htm")]
   bar += makeMenuStrip(list, active[1])

   # If necessary make strip 3
   if (active[1]=="Alphabetical"):
      bar += "<tr><td>&nbsp;</td></tr>\n"
      strip = "</tr></table>\n"
      # chrs = [chr(i) for i in 
      list = [("%s"%(chr(i)), "../alphabetic_index/%s.htm"%(chr(i).lower())) for i in xrange(ord('A'), ord('Z')+1)]
      strip += u"<table class=\"strip\"><tr>"
      for (name, link) in list:
         if (name==active[2]): clas="letterstripactive"
         else:              clas="letterstripInactive"
         strip += "<td>   &nbsp; <a href=\"%s\" class=\"%s\">%s</a> </td>\n"%(link,clas,name)
      bar += strip

   elif (active[1]=="By Course"):
      bar += "<tr><td>&nbsp;</td></tr>\n"
      list = []
      for i in cursor.execute('SELECT name FROM dishes;').fetchall():
         name = i[0]
         list.append(("%s"%name, "../courses_index/%s.htm"%name.lower()))
      bar += makeMenuStrip(list, active[2])

   elif (active[0]=="Sourcing"):
      bar += "<tr><td>&nbsp;</td></tr>\n"
      list = []
      for i in cursor.execute('SELECT name FROM sources WHERE (level=0);').fetchall():
         name = i[0]
         fn = "../sources/%s.htm"%name.lower().replace(" ","_")
         list.append(("%s"%name, "%s"%fn))
      bar += makeMenuStrip(list, active[2])

      

   bar += "</table>\n"
   return bar
  
# Make html for the green title bar that goes along the top of the screen
# "active" is a list that tells us which entry is active in each of the three bars
def makeMenuStrip(list, active):
   strip = u"<tr>"
   for (name, link) in list:
      if (name==active): clas="active1"
      else:              clas="inactive1"
      strip += "<td class=\"click\">   &nbsp; <a href=\"%s\" class=\"%s\">%s</a> </td>\n"%(link,clas,name)
   strip += "</tr>\n"
   return strip


# Make an item to go in a list of recipes
def makeRecipeListItem(rid, cursor):
   text = u""
   recipe=cursor.execute('SELECT r.id,r.filename,r.name,r.summary,c.filename,c.flag FROM recipes AS r LEFT JOIN countries AS c WHERE (r.id=? AND c.id=r.country) ORDER BY r.name;', (rid, )).fetchall()
   if (len(recipe)!=1): return ""
   recipe = recipe[0]
   # flag
   text += "<tr>\n   <td class=\"flag\"><a href=\"../countries/%s\"><img src=\"../flags/small/%s\" /></a></td>\n"%(recipe[4],recipe[5])
   # Name and description of recipe
   text += "   <td class=\"title\"><a class=\"recipeactive\" href=\"../recipes/%s\">%s</a></td>\n"%(recipe[1],recipe[2])
   text += "   <td class=\"description\">%s</td>\n"%recipe[3]
   # Icons for fair trade ingredients
   ingIcons = cursor.execute('SELECT s.icon FROM subrecipes AS sr LEFT JOIN ingredientlinesmap AS ilm ON (ilm.srid=sr.id) LEFT JOIN ingredientlines as il ON (ilm.ilid=il.id) LEFT JOIN ingredients as ig ON (il.ingredient=ig.id ) LEFT JOIN suppliers AS s WHERE (sr.rid=? AND s.id=ig.supplier ) ORDER BY ilm.sort;',(recipe[0],)).fetchall()
   if (len(ingIcons)>0):
      text += "<td class=\"rating\" >"
      for icon in ingIcons: text += "<img style=\"padding-left: 4px;\" src=\"%s\" />"%icon[0]
      text += "</td>"
   text += "</tr>\n"
   return text


# Check a filename for sanity and uniqueness
# returns [BOOLEAN bail, STRING error].  None => all OK
def sanitiseFilename(fn, cursor):
   import re
   if (not re.match(r"^[a-z0-9_\.'-]+$", fn)): return([True, "Invalid filename specified"])
   tempid = getPossibleItemFromDB("SELECT id FROM recipes WHERE filename=?;", (fn, ), cursor)
   if (tempid != None): return([False, "Tried to add new page %s which already exists!"%fn])
   return None

# Make html for the green title bar that goes along the top of the screen
# "active" is a list that tells us which entry is active in each of the three bars
def makeSidebarItem(item, active, myid):
   (name, link) = item
   if (name==active): clas="active1"
   else:              clas="inactive1"
   return u'<div class="%s"><a href="%s" class="%s">%s</a> </div>\n'%(myid,link,clas,name)

def makeSideBarContent(active, cursor):
   text = u""
   # Make strip 1
   items = cursor.execute("SELECT name,page FROM pages ORDER BY id;")
   list = [[name, "../pages/%s"%page] for name, page in items]
   for item in list:
      text += '<div class="sidespacer"></div>\n'
      text += makeSidebarItem(item, active[0], "sideitem")
      if (item[0]=="Recipes"):
         sublist = [("Alphabetical", "../alphabetic_index/a.htm"), ("By Course", "../courses_index/starters.htm"), ("Geographical", "../indices/region_index.htm"), ("Search", "../pages/search.htm")]
         for subitem in sublist: text += makeSidebarItem(subitem, active[1], "sidesubitem")
   return text

# Make html for the green title bar that goes along the top of the screen
# "active" is a list that tells us which entry is active in each of the three bars
def makeTopNavItem(item, active):
   (name, link) = item
   if (name==active): myid="topnav-button-selected"
   else:              myid="topnav-button-idle"
   return u'<div class="%s"><a href=\"%s\">%s</a> </div>\n'%(myid,link,name)

# Navigation for the top of the page
def makeNavTop(active, cursor):
   text = u''
   # Static block of text
   text += getFromDB("SELECT text FROM htmlchunks WHERE (name=?);", ("navtop",), cursor)
   if (active[1]=="Alphabetical"):
      list = [("%s"%(chr(i)), "../alphabetic_index/%s.htm"%(chr(i).lower())) for i in xrange(ord('A'), ord('Z')+1)]
      for item in list: text += makeTopNavItem(item, active[2])
   elif (active[1]=="By Course"):
      for i in cursor.execute('SELECT name FROM dishes;').fetchall():
         name = i[0]
         item = (("%s"%name, "../courses_index/%s.htm"%name.lower()))
         text += makeTopNavItem(item, active[2])
   elif (active[0]=="Sourcing"):
      for i in cursor.execute('SELECT name FROM sources WHERE (level=0);').fetchall():
         name = i[0]
         fn = "../sources/%s.htm"%name.lower().replace(" ","_")
         item = ("%s"%name, "%s"%fn)
         text += makeTopNavItem(item, active[2])
   else:
      text += makeTopNavItem(["%s"%active[0], '#'], active[0])
   text += getFromDB("SELECT text FROM htmlchunks WHERE (name=?);", ("navtopend",), cursor)
   return text


# Make an item to go in a list of recipes
def makeNewRecipeListItem(rid, cursor):
   text = u"<div class='recipelistitem'>"
   recipe=cursor.execute('SELECT r.id,r.filename,r.name,r.summary,c.filename,c.flag,c.name FROM recipes AS r LEFT JOIN countries AS c WHERE (r.id=? AND c.id=r.country) ORDER BY r.name;', (rid, )).fetchall()
   if (len(recipe)!=1): return ""
   recipe = recipe[0]
   # flag
   text += '<div class="recipelistflag"><a href="../countries/%s"><img src="../flags/small/%s" alt="Flag of %s" /></a></div>'%(recipe[4],recipe[5],recipe[6])
   # Name and description of recipe
   text += '<div class="recipelistname"><a class="recipeactive" href="../recipes/%s">%s</a></div>\n'%(recipe[1],recipe[2])
   text += '<div class="recipelisttext">%s</div>\n'%recipe[3]
   # Icons for fair trade ingredients
   ingIcons = cursor.execute('SELECT s.icon,s.name FROM subrecipes AS sr LEFT JOIN ingredientlinesmap AS ilm ON (ilm.srid=sr.id) LEFT JOIN ingredientlines as il ON (ilm.ilid=il.id) LEFT JOIN ingredients as ig ON (il.ingredient=ig.id ) LEFT JOIN suppliers AS s WHERE (sr.rid=? AND s.id=ig.supplier ) ORDER BY ilm.sort;',(recipe[0],)).fetchall()
   if (len(ingIcons)>0):
      text += '<div class="recipelistpix">'
      for item in ingIcons: text += '<img src="%s" alt="%s" />'%(item[0],item[1])
      text += "</div>"
   text += "</div>\n"
   text += '<div class="recipelistspacer"> </div>\n'
   # text += '<div class="recipelistspacer2"> </div>\n'
   return text

def redirectUserCourse(course,subcourse):
   # Fire up sqlite
   (connection, cursor) = openDB()

   # Find the ID of the requested course
   try: cid = getPossibleItemFromDB('SELECT id FROM dishes WHERE (name LIKE ?);', (course,), cursor)
   except: errPage("Error finding course!")
   try: assert(cid!=None)
   except: errPage("Course not found!")

   # Find the ID of the requested sub-course
   try: scid = getPossibleItemFromDB('SELECT id FROM subdishes WHERE (name LIKE ?);', (subcourse,), cursor)
   except: errPage("Error finding subcourse!")
   try: assert(scid!=None)
   except: errPage("Sub-course not found!")

   # Consistency
   testcid = getFromDB('SELECT did FROM subdishes WHERE (id=?);', (scid,),cursor)
   try: assert(testcid==cid)
   except: errPage("Sub-course does not match course! %s %s"%(cid,testcid))


   # Find the address to redirect to
   address = "%s.htm#%s"%(course,scid)
   redirect303(address)
   exit(0)


def renderIngredient(quantity, igname):
   body  = u'<div class="ingredient">'
   body += '<div class="quantity">%s</div>'%quantity
   body += '<div class="stuff">%s</div>'%igname
   body += '</div>\n'
   return body


def recipeListBox(myrid, rfn, cursor):
   text = u'<div id="listbox">\n'
   text += '<div class="boxhead"><a href="../lists/manage.htm">Manage recipe list</a></div>\n'

   session = cookie["session"].value

   (sessionConnection, sessionCursor) = openaDB("session.db")
   recipes = sessionCursor.execute("SELECT rid, fac FROM sessionmap WHERE sid=?;", (session,)).fetchall()
   if (len(recipes)==0):
      text += "<p>Your list contains no recipes</p>"
   else:
      for item in recipes:
         rid = item[0]
         fac = item[1]
         try: 
            (name, fn) = cursor.execute('SELECT name, filename FROM recipes WHERE (id=? AND visible IS "TRUE");', (rid,)).fetchall()[0]
         except:
            continue
         text += '<div class="listboxitem">%s <a href="../recipes/%s">%s</a></div>\n'%(fac,fn,name)



   # For now print the session number
   text += "Ur session number is %s\n"%session
   
   # Form to allow addition of recipes
   if (myrid != None):
      text += '<form action="%s" method="post" id="addrec">\n'%(rfn)
      text += '<input type="hidden" name="session" value="%s" />\n'%(session)
      text += '<button name="add" value="%s"><img src="../icns/plus.png" alt="Add %s to list" /></button>\n'%(myrid,rfn)
   
   text += "</div>\n"
   
   return text

def addRecipeToSession(session, fn, toAdd):
   # (connection, cursor) = openDB()
   # try: rid = getFromDB("SELECT id FROM recipes WHERE filename=?;", (fn,), cursor)
   # except: 
      # errPage("Invalid data submitted!")
      # exit(1)
   # cursor.close()
   # connection.commit()
   # connection.close()

   rid = toAdd
   # errPage("to add %s"%toAdd)

   (sessionConnection, sessionCursor) = openaDB("session.db")
   count = getFromDB("SELECT COUNT(*) FROM session WHERE (id=?);", (session,), sessionCursor)
   if (count != 1):
      errPage("Internal database corruption detected: stopping")
      exit(1)
   fac = getPossibleItemFromDB("SELECT fac FROM sessionmap WHERE (sid=? AND rid=?);", (session, rid), sessionCursor)
   if (fac == None):
      sessionCursor.execute("INSERT INTO sessionmap (sid,rid,fac) VALUES (?,?,1.0);", (session, rid, ))
   else:
      fac += 1.0
      sessionCursor.execute("UPDATE sessionmap SET fac=? WHERE (sid=? AND rid=?);", (fac, session, rid, ))

   #errPage("fac: %s"%fac)
   sessionCursor.execute('UPDATE session SET atime=datetime("NOW"), mtime=datetime("NOW"), ctime=datetime("NOW") WHERE id=?;', (session,))

   sessionCursor.close()
   sessionConnection.commit()
   sessionConnection.close()

   return
   
# Take a set of recipes and multiplicative factors and turn them into a recipe list
def makeIngredientsList(ridlist, cursor):
   text = u'<div class="iglist">\n'

   # First obtain a list of supermarket aisles
   aislelist = cursor.execute("SELECT (aid,name) FROM aisle WHERE (aid NOT 999);").fetchall()
   for (aid, aname) in aislelist:
      ilist = []
      # Loop over the recipes accreting ingredients for this aisle
      for (rid,fac) in ridlist:
         tempilist = cursor.execute("SELECT (il,quantity, i.name) FROM recipes r LEFT JOIN subrecipes sr ON sr.rid=r.id LEFT JOIN ingredientlinesmap ilm ON ilm.srid=sr.id LEFT JOIN ingredientlines il ON il.id=ilm.ilid LEFT JOIN ingredients i ON i.id=il.ingredient LEFT JOIN aislemap am ON am.iid=i.id WHERE (am.aid=? AND r.id=?)")
         if (fac != 1): facstr = "%s x "%(fac)
         else:          facstr = ""
         for (quantity,name) in tempilist: ilist.append("%s%s"%(facstr,quantity), name)

      # XXX do some sorting here
      text += '<div class="aisle">\n<div class="aislename">%s\n</div>\n'%(aname)
      for (quantity, igname) in ilist: text += renderIngredient(quantity, igname)
      text += '</div>\n'

   text += '</div>\n'
   return text

   
def gcdbsAndErr(dbs, err):
   gcdb(dbs[0], dbs[1])
   errPage(err)
   exit(1)
