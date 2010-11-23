# SpeedTrial.py
# $Id$

import glob,os,time

bins = glob.glob("bins/*")

os.system("rm -Rf examples output")
os.system("mkdir -p examples/eps")
os.system("mkdir -p output")
os.system("cp ../../pyxplot8/doc/examples/* examples")

examples = glob.glob("../../pyxplot8/doc/examples/ex_*.ppl")
examples.sort()

id = os.getpid()

output = open("output/SpeedTrial_%s"%id,"w")
output.write("%16s "%"")
for binary in bins:
 output.write("%16s "%binary)
output.write("\n\n")

for example in examples:
 TestName = os.path.split(example)[1][:-4]
 output.write("%16s "%TestName)
 for binary in bins:
  time.sleep(1)
  cmd = "bash -c '(time %s %s) &> /tmp/SpeedTrial_%s'"%(binary,example,id)
  print cmd
  os.system(cmd)
  UserTime=-1
  for line in open("/tmp/SpeedTrial_%s"%id):
   if (len(line)<1): continue
   words=line.split()
   if len(words)!=2: continue
   if words[0]!='user': continue
   UserTime=words[1]
  output.write("%16s "%UserTime)
 output.write("\n")
 output.flush()

