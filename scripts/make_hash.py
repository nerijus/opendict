#!/usr/bin/env python

# MakeHash
# Utility for dictionary hash table making
# mjoc, 2003

import sys

if len(sys.argv) < 3:
    print("Usage: %s <dict_file> <hash_file>" % sys.argv[0])
    sys.exit(1)

dict = open(sys.argv[1], "r")
hash = open(sys.argv[2], "w")

line = dict.readline()
l = line[0].lower()
n = 0

hash.write(l+" "+repr(n)+"\n")
n += len(line)

for line in dict.readlines():
    if line[0].lower() != l:
        l = line[0]
        hash.write(l+" "+repr(n)+"\n")
    n += len(line)

dict.close()
hash.close()
