# ValgrindTest.py
# $Id$

import glob,os,time

CORE_PATH = "/tmp/coredump"

os.system("rm -Rf examples output")
os.system("mkdir -p examples/eps")
os.system("mkdir -p output")
os.system("cp ../../pyxplot8/doc/examples/* examples")

examples = glob.glob("../../pyxplot8/doc/examples/ex_*.ppl")
examples.sort()

for example in examples:
 time.sleep(1)
 TestName = os.path.split(example)[1][:-4]
 stderr_file = "output/%s.stderr"%(TestName)
 cmd = "valgrind pyxplot8 %s 2> %s"%(example,stderr_file)
 print cmd
 os.system(cmd)

