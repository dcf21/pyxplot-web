# This python script takes a list of units as output by the "show units" command
# and turns it into an appendix for the PyXPlot manual

# $Id$

import re

x = open("unitlist.in")
out = open("unitlist.out","w")

output  = ""
output2 = ""
UnitTypes = {}

for line in x:
 l1 = line.split("'")
 l2 = line.split("(")
 if (len(l1)<2): continue

 output += "{\\tt\\footnotesize %s} & {\\tt\\footnotesize %s} & {\\tt\\footnotesize %s} & {\\tt\\footnotesize %s} & "%(l1[1],l1[3],l1[5],l1[7])
 test = re.search(r"is a unit of ([A-Za-z0-9_]*)", line);
 output += "%s "%test.group(1);
 if (len(l2)>1): output += "(%s) "%l2[1].split(")")[0]
 output += "\\\\\n"

 if test.group(1) not in UnitTypes: UnitTypes[test.group(1)] = [l1[1]]
 else                             : UnitTypes[test.group(1)].append(l1[1])

 if (len(l1)>9):
  output += "\\multicolumn{5}{|r|}{\\footnotesize Also known as the"
  i=8;
  while (len(l1)>i+1):
   if (i>8) and (len(l1)> i+3): output += ", the"
   if (i>8) and (len(l1)<=i+3): output += " and the"
   output += " {\\tt %s}"%l1[i+1]
   i+=2
  output += ".} \\\\\n"

quantities = UnitTypes.keys()
quantities.sort()

for q in quantities:
 q2 = re.sub("_"," ",q)
 output2 += "\\noindent The following units of {\\bf %s} are recognised:\\newline\n\\noindent the "%q2
 units = UnitTypes[q]
 units.sort()
 for i in range(len(units)):
  u = units[i]
  if   (i>0) and (i==len(units)-1): output2 += " and the "
  elif (i>0)                      : output2 += ", the "
  
  output2+="{\\tt %s}"%u
  first = False
 output2+=".\\vspace{5mm}\n\n"

output  = re.sub("_",r"\_",output )
output2 = re.sub("_",r"\_\-",output2)

out.write(r"""\begin{landscape}
\begin{center}
\begin{longtable}{|lllll|}
\hline \endfoot
\hline
\multicolumn{4}{|l}{\bf Name} & \\
\multicolumn{2}{|l}{\bf Full} & \multicolumn{2}{l}{\bf Abbrev} & {\bf Unit of} \\
{\bf sing.} & {\bf pl.} & {\bf sing.} & {\bf pl.} & \\ \hline \endhead
""")

out.write(output);

out.write(r"""\end{longtable}
\end{center}
\end{landscape}

""");

out.write(output2)

x.close()
out.close()

