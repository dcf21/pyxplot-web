# ScriptToLatex.py
# $Id$

import sys,re

def title_string_texify(title):
 title    = re.sub(r'[\\]', r'gpzywxqqq', title) # LaTeX does not like backslashs
 title    = re.sub(r'[_]', r'\\_', title) # LaTeX does not like underscores....
 title    = re.sub(r'[&]', r'\\&', title) # LaTeX does not like ampersands....
 title    = re.sub(r'[%]', r'\\%', title) # LaTeX does not like percents....
 title    = re.sub(r'[$]', r'\\$', title) # LaTeX does not like $s....
 title    = re.sub(r'[{]', r'\\{', title) # LaTeX does not like {s....
 title    = re.sub(r'[}]', r'\\}', title) # LaTeX does not like }s....
 title    = re.sub(r'[#]', r'\\#', title) # LaTeX does not like #s....
 title    = re.sub(r'[\^]', r'\\^{}', title) # LaTeX does not like carets....
 title    = re.sub(r'[~]', r'$\\sim$', title) # LaTeX does not like tildas....
 title = re.sub(r'[<]', r'$<$', title) # LaTeX does not like < outside of mathmode....
 title = re.sub(r'[>]', r'$>$', title) # LaTeX does not like > outside of mathmode....
 title    = re.sub(r'gpzywxqqq', r'$\\backslash$', title) # LaTeX does not like backslashs
 return title

f = open(sys.argv[1])
fns = (sys.argv[2]=='1')
if fns: print "{\\footnotesize"
for line in f:
 if (len(line.strip())==0):
  if fns: print "}\\\\{\\footnotesize"
  else: print "\\\\"
  continue
 line = title_string_texify(line)
 for i in range(len(line)):
  if (line[i]!=' '):
   break;
 if (i>0):
  line2 = "\\phantom{"
  for j in range(i): line2 += "x"
  line2 += "}" + line.strip()
  line = line2
 else:
  line = line.strip()
 print "\\noindent{\\tt %s}\\newline"%line
if fns: print "}"

