#!/usr/bin/env python

# MakeHash
# Utility for dictionary hash table making
# mjoc, 2003

import sys

if len(sys.argv) < 3:
    print "Usage: %s <dict_file> <hash_file>" % sys.argv[0]
    sys.exit(1)

fdDict = open(sys.argv[1])
fdHash = open(sys.argv[2], "w")
 
print "Indexing..."

hash = {}

line = fdDict.readline()
l = line[0:2].lower()
n = 0

hash[l] = n
n += len(line)

for line in fdDict.readlines():
    l = line[0:2].lower()
    if not hash.has_key(l):
        hash[l] = n
    n += len(line)

for l, p in hash.items():
    fdHash.write("%s %s\n" % (l, p))

fdDict.close()
fdHash.close()
 
