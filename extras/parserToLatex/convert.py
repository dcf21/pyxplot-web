# convert.py
# $Id$

from sys import stdout

for line in open("../../pyxplot9/buildScripts/parser_data.dat"):
 line = line.strip()
 if len(line)<1: continue
 if line[0]=='#': continue
 words = line.split()
 typelist = {}
 for word in words:
  if   word=='=': continue
  elif word=='DATABLOCK': continue
  elif word=='CODEBLOCK': stdout.write("<codeblock> ")
  elif word=='{': stdout.write("[ ")
  elif word=='}': stdout.write("] ")
  elif word=='(': stdout.write("[ ")
  elif word==')': stdout.write("] ")
  elif word=='~': stdout.write("] [ ")
  elif word=='<': stdout.write("( ")
  elif word=='|': stdout.write("| ")
  elif word=='>': stdout.write(") ")
  elif word=='[': stdout.write("{ ")
  elif word.startswith("]:"): stdout.write("} ")
  elif word.startswith("%"):
    k = word.split(":")[1]
    stdout.write("<%s> "%k)
    if   word[1]=='a': typelist[k]="The name of an axis, e.g. x, y3, z5"
    elif word[1]=='A': typelist[k]="An angle"
    elif word[1]=='b': typelist[k]="An expression that evaluates to a Boolean"
    elif word[1]=='c': typelist[k]="The name of a color, or an expression evaluating to a color"
    elif word[1]=='d': typelist[k]="An integer expression"
    elif word[1]=='D': typelist[k]="A distance"
    elif word[1]=='e': typelist[k]="An algebraic expression (dollars not allowed)"
    elif word[1]=='E': typelist[k]="An algebraic expression (dollars allowed)"
    elif word[1]=='f': typelist[k]="An expression that evaluates to a real, dimensionless number"
    elif word[1]=='g': typelist[k]="An algebraic expression (no equals signs or dollars)"
    elif word[1]=='o': typelist[k]="An expression that evaluates to any object"
    elif word[1]=='p': typelist[k]="A position -- (x,y) or a vector/list"
    elif word[1]=='P': typelist[k]="A position with a possible third component"
    elif word[1]=='q': typelist[k]="An expression that evaluates to a string"
    elif word[1]=='r': typelist[k]="The whole of the rest of the line as a string"
    elif word[1]=='s': typelist[k]="A word made of alphabetic characters"
    elif word[1]=='S': typelist[k]="A word made of any non-whitespace characters, except quotes"
    elif word[1]=='u': typelist[k]="An expression that evaluates to a number"
  else: stdout.write("%s "%(word.split(":")[0].split("@")[0]))
 stdout.write("\n\n")
 keys = typelist.keys()
 keys.sort()
 for k in keys: stdout.write("%s: %s\n"%(k,typelist[k]))
 stdout.write("\n\n")

