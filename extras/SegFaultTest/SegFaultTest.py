# SegFaultTest.py
# $Id$

# Before running this script, run the shell commands:
# ln -s ../../pyxplot8/doc/examples examples
# sudo echo "/tmp/coredump" > /proc/sys/kernel/core_pattern
# ulimit -c unlimited

import glob,os

CORE_PATH = "/tmp/coredump"

os.system("mkdir -p examples/eps")
os.system("mkdir -p output")

examples = glob.glob("../../pyxplot8/doc/examples/ex_*.ppl")

run = 0
while 1:
 for example in examples:
  run+=1
  TestName = os.path.split(example)[1][:-4]
  stderr_file = "output/%s.%d.stderr"%(TestName,run)
  cmd = "pyxplot8 %s 2> %s"%(example,stderr_file)
  print cmd
  os.system(cmd)
  if (os.path.getsize(stderr_file)<1):
   os.system("rm %s"%stderr_file)
  if os.path.exists(CORE_PATH):
   os.system("mv %s output/%s.%d.core"%(CORE_PATH,TestName,run))

