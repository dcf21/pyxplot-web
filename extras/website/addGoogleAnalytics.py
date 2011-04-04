#!/usr/bin/python
# $Id$

# This script walks through a tree of HTML (which should be in the cwd), and
# adds in the Google Analytics script to each page's header

import os,glob

assert os.path.exists("index.html") # Just double check that we're in the output HTML directory, not the svn working directory, before running the next command

os.system("rm -Rf .svn */.svn */*/.svn */*/*/.svn */*/*/*/.svn */*/*/*/*/.svn")

for fn in glob.glob("*.html")+glob.glob("*/*.html")+glob.glob("*/*/*.html")+glob.glob("*/*/*/*.html")+glob.glob("*/*/*/*/*.html")+glob.glob("*/*/*/*/*/*.html"):
 print fn
 contents = open(fn).read()
 lines = contents.split('\n')
 done = False
 for i in range(len(lines)):
  if lines[i].strip()=='</head>':
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
   break
 contents = "\n".join(lines)
 out = open(fn,"w")
 out.write(contents)
 out.close()

