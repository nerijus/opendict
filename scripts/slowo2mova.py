#!/usr/bin/env python

# slowo2mova
# Copyright (c) 2003 Martynas Jocius <mjoc@delfi.lt>

import sys

def slowo2mova(sfName, mfName):

    fdSlowo = open(sfName)
    fdMova = open(mfName, "w")

    for line in fdSlowo.readlines():
        fdMova.write(line.split("=")[0].strip()+"  "+line.split("=")[1].strip()+"\n")

    fdSlowo.close()
    fdMova.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Usage %s <slowo file> <mova file>" % sys.argv[0]
        sys.exit(1)

    slowo2mova(sys.argv[1], sys.argv[2])
    
