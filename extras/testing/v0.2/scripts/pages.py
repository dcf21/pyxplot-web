#!/usr/bin/env python2.6


from general import *
from web import *
import cgi, re, sys
from pysqlite2 import dbapi2 as sqlite
import cgitb

# Stops stdout coercing everything to ascii
reload(sys)
sys.setdefaultencoding('utf-8')

cgitb.enable()

def main():
   form = cgi.FieldStorage()

   initialiseCookie()

   # page.py
   if "page" in form:
      page = form["page"].value
      if (not re.match(r"^[a-zA-Z0-9_\.-]+$", page)):
         errPage("Invalid page name specified")
         exit(1)
      else: 
         buildPage(page)
         exit(0)

# Build a page.  We can trust fn although it's been passed by a user
def buildPage(fn):
   # Variable to hold the HTML
   page = u""

   # Fire up sqlite
   (connection, cursor) = openaDB("webstuff.db")

   # Find the page
   try: pid = getFromDB('SELECT id FROM pages WHERE (page=?);',(fn,),cursor)
   except:
      errPage("Page %s not found!"%fn)
      exit(1)
   # Title
   title = getFromDB('SELECT name FROM pages WHERE (id=?);',(pid,),cursor)

   # Process the body for recipe lines
   body = getFromDB('SELECT body FROM pages WHERE (id=?);', (pid,),cursor)

   active = ["%s"%title, None, None]
   makePage({"title": title, "active":active}, body, cursor)

   # Close down
   cursor.close()
   connection.commit()
   connection.close()
   return

#
# Build a country page.  We can trust fn although it's been passed by a user
def makeCountryPage(fn):
   # Variable to hold the HTML
   page = u''

   # Fire up sqlite
   (connection, cursor) = openDB()

   # Check that the country exists
   try: cid = getFromDB('SELECT id FROM countries WHERE (filename=?);', (fn,), cursor)
   except:
      errPage("Can't find that country!")
      exit()

   name = getFromDB('SELECT name FROM countries WHERE (id=?);', (cid,), cursor)
   flag = getFromDB('SELECT flag FROM countries WHERE (id=?);', (cid,), cursor)
   links = getFromDB('SELECT links FROM countries WHERE (id=?);', (cid,), cursor)

   # Title
   title = "Recipes from %s -- The Fair Trade Cook Book"%(name)

   # Link bar
   active = ["Recipes", "Geographical", None]

   # Info box
   page += '<div id="countrycontent">\n'
   page += '<div id="countryflag">\n'
   page += "<h2>%s</h2>\n"%name
   page += '<img src="../flags/%s" alt="Flag of %s" /> \n'%(flag,name)
   page += "</div>\n"

   # Links
   page += '    <div id="countrylinks">%s    </div>\n'%links

   # Neighbours
   neighbourList = cursor.execute('SELECT c.name,c.filename,c.flag FROM countrymap AS cm LEFT JOIN countries AS c WHERE (cm.id1=? AND c.id=cm.id2);', (cid,)).fetchall()
   if (len(neighbourList)>0):
      page += '    <div id="countryneigh">\n      <p>\n        <h3> Neighbouring countries:</h3>  </p>\n'
      for line in neighbourList:
         page += '<div class="country"><a href="%s"> <img src="../flags/small/%s" alt="%s" /><div>%s</div></a></div>\n'%(line[1],line[2],line[0],line[0])
      page += "</div>\n"
   page += "</div>\n"

   # Recipes
   #recipes = cursor.execute('SELECT r.id,r.filename,r.name,r.summary,c.filename,c.flag FROM recipes AS r LEFT JOIN countries AS c ON (c.id=r.country) WHERE (r.visible IS "TRUE" AND c.id=?);', (cid, )).fetchall()
   recipes = cursor.execute('SELECT r.id FROM recipes AS r WHERE (r.country=? AND r.visible IS "TRUE");', (cid, )).fetchall()
   if (len(recipes)>0):
      page += "<h3>Recipes from %s</h3>\n"%name
      # Possibly need a suitable div here

      for recipe in recipes:
         page += makeNewRecipeListItem(recipe[0], cursor)
         # #flag
         # page += "<tr>\n   <td class=\"flag\"><a href=\"../countries/%s\"><img src=\"../flags/small/%s\" /></a></td>\n"%(recipe[4],recipe[5])
         # # Name and description of recipe
         # page += "   <td class=\"title\"><a class=\"recipeactive\" href=\"../recipes/%s\">%s</a></td>\n"%(recipe[1],recipe[2])
         # page += "   <td class=\"description\">%s</td>\n"%recipe[3]
         # # Icons for fair trade ingredients
         # ingIcons = cursor.execute('SELECT s.icon FROM subrecipes AS sr LEFT JOIN ingredientlinesmap AS ilm LEFT JOIN ingredientlines as il LEFT JOIN ingredients as ig LEFT JOIN suppliers AS s WHERE (sr.rid=? AND ilm.srid=sr.id AND ilm.ilid=il.id AND il.ingredient=ig.id AND s.id=ig.supplier ) ORDER BY ilm.sort;',(recipe[0],)).fetchall()
         # if (len(ingIcons)>0):
            # page += "<td class=\"rating\">"
            # for icon in ingIcons: page += "<img style=\"padding-left: 4px;\" src=\"%s\" />"%icon[0]
            # page += "</td>"
         # page += "</tr>\n"

   makePage({"title": title, "active":active}, page, cursor)

   # Close down
   cursor.close()
   connection.commit()
   connection.close()
   return




# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Build a recipe.  We can trust fn although it's been passed by a user
def buildRecipe(fn):
   # Fire up sqlite
   (connection, cursor) = openDB()

   # Find the recipe
   try: rid = getFromDB('SELECT id FROM recipes WHERE (filename=?);',(fn,),cursor)
   except:
      err404Page(cursor)
      errPage("Recipe not found!")
      exit(1)

   # Title
   title = getFromDB('SELECT name FROM recipes WHERE (id=?);',(rid,),cursor)

   # Link bar
   active = ["Recipes", None, None]

   # Main title
   body = "<h1><i>" + title + "</i></h1>\n"

   # recipe List box
   body += recipeListBox(rid, fn, cursor)

   # Description and possible picture
   picture = getPossibleItemFromDB("SELECT p.filename FROM recipes AS r LEFT JOIN pictures AS p WHERE (p.id=r.picture AND r.id=?);", (rid,),cursor)
   if (picture!=None): body += "<img align=\"middle\" src=\"%s\" />\n</td><td>\n"%picture
   body += "<p>\n"
   body += getFromDB('SELECT description FROM recipes WHERE (id=?);',(rid,),cursor)
   body += "</p>\n"
 
   # Method etc. header
   body += '<div id="ingredients">\n'
   # Place to store sources
   sources = {}
   # Each sub-recipe at a time
   cursor.execute('SELECT sr.id, sr.name1, sr.name2 FROM subrecipes AS sr WHERE (sr.rid=?) ORDER BY sr.sort;', (rid,))
   subRecipes = cursor.fetchall()
   if (len(subRecipes)>0):
      body += "   <h3>Ingredients</h3>\n"
      for subr in subRecipes:
         subrPrint = [subr[i] if subr[i]!=None else " " for i in [1,2]]
         body += renderIngredient(subrPrint[0], subrPrint[1])
   
         # Ingredients
         ingredients = cursor.execute('SELECT il.quantity,ig.name,ig.id FROM ingredientlinesmap AS ilm LEFT JOIN ingredientlines AS il ON (ilm.ilid=il.id) LEFT JOIN ingredients AS ig ON (il.ingredient=ig.id) WHERE (ilm.srid=?) ORDER BY ilm.sort;',(subr[0],)).fetchall()
         for (quantity, igname, igid) in ingredients:
            body += renderIngredient(quantity, igname)
            # Extract fairtrade sources
            source = cursor.execute('SELECT s.name,p.name FROM sourceingredientmap AS sim LEFT JOIN sources AS s ON (s.id=sim.sid) LEFT JOIN sources AS p ON (s.pid=p.id) WHERE (sim.iid=?);', (igid,)).fetchall()
            for (sname,pname) in source:
               if (sname==None): continue
               if (pname==None): sources[sname]="%s.htm"%sname
               else:             sources[sname]="%s.htm#%s"%(pname.lower().replace(" ","_"),sname)
      if (sources != {}): body += renderIngredient("<b>FAIRTRADE</b>", "<b>Sources</b>")
      for source in sources.keys(): body += renderIngredient("", "<a href=\"../sources/%s\">%s</a>"%(sources[source],source.capitalize().replace("_", " ")))

   body += '</div>'
   body += '<div id="method">'
   # Method
   body += getFromDB('SELECT method FROM recipes WHERE (id=?);',(rid,),cursor)
   body += '</div>\n<div id="clearrecipe"> </div>\n'

   makePage({"title": title, "active":active}, body, cursor)

   # Close down
   cursor.close()
   connection.commit()
   connection.close()
   return


def buildAlphabeticalIndex(letter):
   # Variable to hold the HTML
   body = u""

   # Fire up sqlite
   (connection, cursor) = openDB()

   # Title
   title = "\"%s\" recipes from the Fair Trade Cook Book"%(letter)

   # Link bar
   active = ["Recipes", "Alphabetical", "%s"%letter.upper()]

   # Body of the page
   body = "<h1><i>" + "Recipes in alphabetical order of title" + "</i></h1>\n"

   # The index starts here
   str = r"%s"%(letter) + '%'
   for recipe in cursor.execute('SELECT id FROM recipes WHERE (name LIKE ? AND visible IS "TRUE") ORDER BY name;', (str, )).fetchall():
      body += "%s"%(makeNewRecipeListItem(recipe[0],cursor))

   makePage({"title": title, "active":active}, body, cursor)

   # Close down
   cursor.close()
   connection.commit()
   connection.close()
   return
   

def searchPage():
   # Variable to hold the HTML
   page = u""

   # Fire up sqlite
   (connection, cursor) = openDB()

   # Title
   title = "Search recipes from the Fair Trade Cook Book"

   # Link bar
   active = ["Recipes", "Search", ""]

   body = "<h2>" + "Search" + "</h2>\n"

   body += getFromDB('SELECT text FROM htmlchunks WHERE name IS "search";', (), cursor)

   body += '<h3> Search results provided by <a href="http://www.google.com">google</a> </h3>\n'

   makePage({"title": title, "active":active}, body, cursor)

   # Close down
   cursor.close()
   connection.commit()
   connection.close()
   return

def buildCourseIndex(course):

   # Fire up sqlite
   (connection, cursor) = openDB()

   # Find the ID of the requested course
   try: cid = getPossibleItemFromDB('SELECT id FROM dishes WHERE (name LIKE ?);', (course,), cursor)
   except: errPage("Error finding course!")
   try: assert(cid!=None)
   except: errPage("Course not found!")

   name = getFromDB('SELECT name FROM dishes WHERE (id=?);', (cid,), cursor)
   title = name

   # Link bar
   active = ["Recipes", "By Course", name]
   # Main title
   body = "<h2>" + name + "</h2>\n"

   # The index starts here
   sdlist = cursor.execute('SELECT sd.id,sd.name FROM dishes AS d LEFT JOIN subdishes AS sd ON (sd.did=d.id) WHERE (d.id=?);', (cid,)).fetchall()
   if (len(sdlist)>1):
      body += "<p>Jump to: "
      list = []
      for (sdid, sdname) in sdlist:
         if (sdname != None): list.append("<a style=\"margin-left: .5em; margin-right: .5em;\" href=\"#%s\">%s</a>"%(sdid,sdname))
      body += " - ".join(list)
      body += "</p>\n"
   for (sdid, sdname) in sdlist:
      if (sdname!=None):  body += "<a name=\"%s\" /><h4>%s</h4>\n"%(sdid,sdname)
      for (rid,) in cursor.execute('SELECT d.rid FROM dishmap AS d LEFT JOIN recipes AS r ON (r.id=d.rid) WHERE (r.visible IS "TRUE" AND d.sdid=?);', (sdid,)).fetchall():
         body += makeNewRecipeListItem(rid, cursor)

   makePage({"title": title, "active":active}, body, cursor)

   # Close down
   cursor.close()
   connection.commit()
   connection.close()
   return
   
def countryList():
   # Fire up sqlite
   (connection, cursor) = openDB()

   # Title
   title = "Recipes from The Fair Trade Cook Book"
   active=["Recipes", "Geographical", None]
   
   page = u"<h2>Recipe index by Region, using the UN countries list</h2>\n<p>\n  Maps courtesy <b> <a href=\"http://www.cia.gov/cia/publications/factbook/\" target=\"_blank\" >CIA Factbook </a> </b> </p>\n"
   # Loop over continents
   i=0
   page += '<div class="pangea">\n'
   # for (id,name,map,N) in cursor.execute('SELECT cont.id,cont.name,cont.map,COUNT(*) AS cnt FROM continents AS cont LEFT JOIN countries AS count on cont.id=count.continent GROUP BY cont.id ORDER BY cnt DESC;').fetchall():
   for (id,name,map) in cursor.execute('SELECT c.id,c.name,c.map FROM continents as c ORDER BY sort;').fetchall():
      page += '<div class="continent"><h3>%s</h3>'%name
      page += '<a href="../maps/maps_l/%s" ><img src="../maps/%s" alt="%s" /> </a>\n'%(map,map,name)
      # page += "<td class=\"ctrycolumn\"><a id=\"%s\"></a><h3>%s </h3>\n"%(name.lower(),name)
      # page += "<a href=\"../maps/maps_l/%s\" ><img src=\"../maps/%s\" alt=\"%s\" /> </a><br />\n"%(map,map,name)
      list = cursor.execute('SELECT c.id,c.name,c.filename FROM countries AS c WHERE (continent=?);', (id,)).fetchall()
      for cid,cname,cfile in list:
         N = getFromDB('SELECT COUNT(*) FROM recipes WHERE (country=? AND visible IS "TRUE");', (cid,),cursor)
         if (N==0): clas="countryneeded"
         else:      clas="countryactive"
         page += '<div class="%s"><a href="../countries/%s">%s</a></div>\n'%(clas,cfile,cname)
      page += '</div>\n'
      i += 1
      if (i==3):
         page += '</div>\n<div id="pangea">\n'

   page += '</div>\n'
   makePage({"title": title, "active":active}, page, cursor)


   # Close down
   cursor.close()
   connection.commit()
   connection.close()
   return
   
def buildSourcesPage(pageName):
   # Variable to hold the HTML
   page = u''

   # Fire up sqlite
   (connection, cursor) = openDB()

   # Find the page
   sid = getPossibleItemFromDB("SELECT id FROM sources WHERE (name LIKE ?);", (pageName,),cursor)
   if (sid==None): 
      err404Page(cursor)
      exit(1)

   # Get the id of the parent page, if any
   pid = getFromDB("SELECT pid FROM sources WHERE (id=?);", (sid,), cursor)
   if (pid==None): pid=sid
   # Get proper name
   pageName = getFromDB("SELECT name FROM sources WHERE (id=?);", (sid,), cursor)

   # Title
   title = "Fair Trade sources from the Fair Trade Cook Book"

   # Link bar
   active = ["Sourcing", None, pageName]

   # Parent node
   page += getFromDB("SELECT content FROM sources WHERE (id=?);", (pid,), cursor)

   # Child nodes
   children = cursor.execute('SELECT name,content FROM sources WHERE (pid=?) ORDER BY name;', (pid,)).fetchall()
   if (len(children)>1):
      page += "<p>Jump to: "
      for (name, dum) in children: page += " <a style=\"padding-left: 1em;\" href=\"#%s\">%s</a>"%(name,name.capitalize().replace("_", " "))
      page += "</p>\n"
   for (name,content) in children:
      page += "<a name=\"%s\" />\n"%name
      page += "%s"%content
      page += "\n<hr />\n"

   makePage({"title": title, "active":active}, page, cursor)


   # Close down
   cursor.close()
   connection.commit()
   connection.close()
   return



# Main routine here
main()

