#!/usr/bin/env python2.6
#
# Test pyxplot arithmetic by generating and evaluating arithmetic statements
# rpc25, Tue Jul  7 08:00:58 BST 2009
# Modified for new test arangements Wed Dec 28 13:21:30 GMT 2011

import os, sys, random, math
from general import *


# Generate mathematical expression
def generateExpression(Nbrackets, symbolTable, eqSymbolTable):
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
      # if (number < 0): expression = expression + " (%g) "%number
      # else:            expression = expression + " %g "%number
      expression = expression + " %g "%number

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

# Generate mathematical expression
def generateExpressionWithVariables(Nbrackets, symbolTable, eqSymbolTable):
   leftBracketCount = 0
   rightBracketCount = 0
   script = ""
   expression = ""
   number = 0
   operator = ""
   finished = False
   variables = ["a", "b", "c", "z", "badger", "x", "X", "y", "Y", "fishfork", "aquaplane", "hhhhhhhhhhhhhhhhhhhhhhhhhhhhhh"]
   # Give the variables values
   for i in variables:
      number = getNumber(-100, 100)
      script += "%s = %s\n"%(i,number)
   while (not finished):
      # First add a number
      assert (operator != "**")
      variable = random.choice(variables)
      # if (number < 0): expression = expression + " (%g) "%number
      # else:            expression = expression + " %g "%number
      expression = expression + " %s "%variable

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
   return [script, expression]
            
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

def generateScriptWithVariables(Nbrackets, symbolTable, eqSymbolTable):
   done = False
   while (not done):
      script = generateExpressionWithVariables(Nbrackets, symbolTable, eqSymbolTable)
      try: 
         exec(script[0])
         pyVal = eval(script[1])
      except:  continue
      done = True
      print pyVal
   return "%s\n(%s)+0"%(script[0],script[1])


def generateScript(Nbrackets, symbolTable, eqSymbolTable):
   done = False
   while (not done):
      script = generateExpression(Nbrackets, symbolTable, eqSymbolTable)
      try: pyVal = eval(script)
      except:  continue
      done = True
      print pyVal
   return "(%s)+0"%script

# Generate a script to do arithmetic tests
def generateArithmeticScript():
   # Table of symbols
   symbolTable = ["+", "-", "*", "/", "**"]
   # symbolTable = ["+", "*", "**"]
   # Table of equalities
   eqSymbolTable = [">", "<", ">=", "<=", "==", "!="]
   script = u""
   for i in range(100):
      # Number of bracket pairs to include in the expression
      Nbrackets = math.floor(random.random()*11)
      script += "%s\n"%generateScript(Nbrackets, symbolTable, eqSymbolTable)
   d = {"script":script, "name":"Arithmetic"}
   return d

# Generate a script to do arithmetic tests
def generateAlgebraScript():
   # Table of symbols
   symbolTable = ["+", "-", "*", "/"]
   # symbolTable = ["+", "*", "**"]
   # Table of equalities
   eqSymbolTable = [">", "<", ">=", "<=", "==", "!="]
   script = u""
   for i in range(100):
      # Number of bracket pairs to include in the expression
      Nbrackets = math.floor(random.random()*11)
      script += "%s\n"%generateScriptWithVariables(Nbrackets, symbolTable, eqSymbolTable)
   d = {"script":script, "name":"Algebra"}
   return d



# d = generateArithmeticScript()
# d = generateAlgebraScript()
d = generateArithmeticScript()

(connection, cursor) = openaDB("ppltest.db")
addNewTest(d, cursor)
# print d
gcdb(connection, cursor)
