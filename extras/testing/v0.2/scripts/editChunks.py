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

# Main editors' interface
def editChunks():

   # Fire up sqlite
   (connection, cursor) = openDB()

   form = cgi.FieldStorage()
   postkeys = form.keys()

   # Warnings to return to the user
   warnings = []
   redirects = []
   updates = {}

   # Look to see if there is an edit to commit
   if (form.getfirst("hidden")==None):
      httpHeaders()
      page = renderChunkEditorsForm(cursor)
      sys.stdout.write(page)
      return


   # Check that we have all the expected items
   oldchunks = cursor.execute("SELECT id, name, text FROM htmlchunks;").fetchall()
   for (id,name,text) in oldchunks:
      newtext = form.getfirst("chunk_%s"%id)
      if (newtext == None): errPage("Missing chunk %s"%name)
      updates[id] = newtext

   for id in updates.keys():
      cursor.execute("UPDATE htmlchunks SET text=? WHERE (id=?);", (updates[id], id, ))

   httpHeaders()
   page = renderChunkEditorsHead(cursor)

   # Warnings
   if (len(warnings)>0):
      page += "<h3 style='color: red'>Warnings</h3><p style='color:red'>\n"
      for warning in warnings: page += "%s<br />"%warning
      page += "</p><hr />\n"


   page += renderChunkEditorsMain(cursor)
   sys.stdout.write(page)
   cursor.close()
   connection.commit()
   connection.close()
   return

def renderChunkEditorsForm(cursor):
   page = renderChunkEditorsHead(cursor)
   page += renderChunkEditorsMain(cursor)
   return page

def renderChunkEditorsHead(cursor):
   page = makePageTop("PyXPlot test system user interface", "index.css", cursor)
   page += "<a name='top' /><h2>PyXPlot test system - edit user interface</h2>\n"
   # page += "<p>Go to <a href='editors.py'>editors' interface</a>.</p>\n"
   page += "<hr>\n"
   return page

# Produce the html for the main editor page
def renderChunkEditorsMain(cursor):
   page = ''
   # Big form'o'doom
   page += "</p><a name='top' />\n"
   page += '<form action="editChunks.html" method="post" id="tehform">\n'
   page += '<input type="hidden" name="hidden" value="Hidden key" \>\n'
   page += '<a href="editChunks.py">Reload</a><hr />\n'
   page += '<p>This page allows you to edit the chunks of html that are pasted into other pages.</p>'

   page += '<hr />\n'

   data = cursor.execute("SELECT id,name,text FROM htmlchunks;").fetchall()
   page += "<p>Skip to: "

   for (id, name, text) in data: page += '<a href="#%s">%s</a> '%(id,name)

   for (id, name, text) in data:
      nlines = len(text.splitlines())+10
      page += '<p><a name="%s">%s</a> <button name="sub_%s" value="SUB">Save changes</button> Go to <a href="#top">Top</a><br /><textarea name="%s" rows=%s cols=100 >%s</textarea></p>\n'%(id,name,id,"chunk_%s"%id,nlines,cgi.escape(text, True))


   page += "</form></body></html>\n"

   
   return page




# initialiseCookie()


editChunks()
