#!/usr/bin/env python2.6
#
# Test pyxplot arithmetic by generating and evaluating arithmetic statements
# rpc25, Tue Jul  7 08:00:58 BST 2009
# Modified for new test arangements Wed Dec 28 13:21:30 GMT 2011

import os, sys, random, math
from general import *

# Table of symbols
symbolTable = ["+", "-", "*", "/", "**"]
# Table of equalities
eqSymbolTable = [">", "<", ">=", "<=", "==", "!="]

# Number of bracket pairs to include in the expression
# Nbrackets = math.floor(random.random()*11)
Nbrackets = 2

# Generate mathematical expression
def generateExpression(Nbrackets):
   leftBracketCount = 0
   rightBracketCount = 0
   expression = ""
   number = 0
   operator = ""
   finished = False
   while (not finished):
      # First add a number
      if (operator == '**'): number = int(getNumber(-5, 5))
      else:                  number = getNumber(-100, 100)
      if (number < 0): expression = expression + " (%g) "%number
      else:            expression = expression + " %g "%number

      # Then a close bracket if necessary
      if (rightBracketCount < leftBracketCount and random.random() > .75):
         expression = expression + " ) "
         rightBracketCount += 1

      # Now add an operator
      gotOperator = False
      if (random.random() > .1): newOperator = symbolTable[int(math.floor(random.random()*len(symbolTable)))]
      else:                    newOperator = eqSymbolTable[int(math.floor(random.random()*len(symbolTable)))]
      
      while (operator == '**' and newOperator == '**'):
         newOperator = symbolTable[int(math.floor(random.random()*len(symbolTable)))]
      operator = newOperator
      expression = expression + " %s "%operator

      # Perhaps an open bracket?
      if (leftBracketCount < Nbrackets and operator != '**' and random.random() > .75):
         expression = expression + "("
         leftBracketCount += 1

      # Check if we can terminate the expression (and if we want to)
      if (rightBracketCount == leftBracketCount and rightBracketCount == Nbrackets):
         if (random.random() > .8):
            if (operator == '**'): number = int(getNumber(-5, 5))
            else:                  number = getNumber(-100, 100)
            expression = expression + " %g "%number
            finished = True
   return expression
            
def getNumber(minVal, maxVal):
   # random.random()*10**(random.random()*20-10)
   return random.random()*(maxVal-minVal) + minVal

# Evaluate expression using pyxplot
def ppEval(expression):
   f = open('/tmp/pptest', 'w')
   f.write("""print "%20.13e"%(""" + "%s)\n"%expression)
   f.close()
   os.system("pyxplot8 -q -mono /tmp/pptest > /tmp/pptestOut 2> /tmp/crap")
   f = open('/tmp/pptestOut', 'r')
   ppOutput = f.readline()
   f.close()
   print ppOutput
   try: assert(len(ppOutput)!=0)
   except: 
      print "Evaluation of %s produced no output!"%expression
      raise
   ppOutput = ppOutput.strip()
   return float(ppOutput)

def generateScript(Nbrackets):
   done = False
   while (not done):
      script = generateExpression(Nbrackets)
      try: pyVal = eval(script)
      except:  continue
      done = True
   return "(%s)+0"%script


difference = 0
sum = 1
counter = 0

script = u""
for i in range(100):
   script += "%s\n"%generateScript(Nbrackets)

d = {"script":script, "name":"Arithmetic"}


(connection, cursor) = openaDB("ppltest.db")
addNewTest(d, cursor)
gcdb(connection, cursor)
