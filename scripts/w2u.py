#!/usr/bin/env python

# w2u
# Convert windows text file to unix text file
# (by changing line end symbol)
# Martynas Jocius <mjoc@delfi.lt>

import sys
import glob

def w2u(args):

   files = []
   for arg in args:
      files.extend(glob.glob(arg))

   for fname in files:
      print "Working on %s..." % fname
      old = open(fname)
   
      data = ""

      for line in old.readlines():
         data += line.rstrip() + "\n"

      new = open(fname, "w")
      new.write(data)
   
      old.close()
      new.close()

if __name__ == "__main__":

   if len(sys.argv) < 2:
      print "Usage: %s <file1> [file2] [file3] ..." % sys.argv[0]
      sys.exit(1)

   w2u(sys.argv[1:])

