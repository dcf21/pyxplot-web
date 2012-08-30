#!/usr/bin/python
# $Id$

# This script walks through a tree of HTML (which should be in the cwd), and
# adds in the Google Analytics script to each page's header

import os,glob

assert os.path.exists("0.8") # Just double check that we're in the output HTML directory, not the svn working directory, before running the next command

os.system("rm -Rf .svn */.svn */*/.svn */*/*/.svn */*/*/*/.svn */*/*/*/*/.svn")

for fn in glob.glob("0.*/doc/html/*.html") + glob.glob("current/doc/html/*.html"):
 #print fn
 contents = open(fn).read()
 lines = contents.split('\n')
 i = hadMeta = hadTitle = hadHead = hadBody = hadEndBody = 0
 while (i<len(lines)):
   if (not hadMeta) and lines[i].strip().startswith("""<meta name"""):
     lines.insert(i,r"""<meta name="description" content="Pyxplot: A data processing, graph plotting and vector graphics suite">
<meta name="keywords" content="Pyxplot, graph plotting, vector graphics, LaTeX, equations, scripting">
<meta name="author" content="Dominic Ford" />""")
     hadMeta=1
   elif (not hadTitle) and lines[i].strip().startswith("""<title>"""):
     if (lines[i][7]==":"): lines[i] = r"""<title>Pyxplot Users' Guide"""+lines[i][7:]
     else:                  lines[i] = r"""<title>Pyxplot Users' Guide: """+lines[i][7:]
     hadTitle=1
   elif (not hadHead) and lines[i].strip()=='</head>':
     lines.insert(i,r"""<script type="text/javascript">
  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-22395429-2']);
  _gaq.push(['_trackPageview']);
  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();
</script>""")
     hadHead=1
   elif (not hadBody) and lines[i].strip()=='<body>':
     lines.insert(i+1,r"""<table width="100%"><tr><td style="vertical-align:top;">""")
     hadBody=1
   elif (not hadEndBody) and lines[i].strip()=='</body>':
     lines.insert(i,r"""<p style="text-align:center;">"""+open("../source/include/advert_footer.html").read()+"""</p></td><td width="170" style="vertical-align:top;">"""+open("../source/include/advert_sidebar.html").read()+"""</td></tr></table>""")
     hadEndBody=1
   i+=1
 contents = "\n".join(lines)
 out = open(fn,"w")
 out.write(contents)
 out.close()

