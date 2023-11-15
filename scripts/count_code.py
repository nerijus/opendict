#!/usr/bin/env python

# Count OpenDict Code Lines
# Copyright (c) Martynas Jocius <mjoc@delfi.lt>
# Licensed under the GNU GPL.

import sys
import glob

def count(file):

    fd = open(file)

    all = 0
    code = 0

    for line in fd.readlines():
        all += 1
        if line.strip() == "":
            continue
        if line.find("#") > -1:
            if line[0] == "#":
                continue
            elif line[0:line.index("#")].strip() == "":
                continue
        code += 1

    print("%s:" % file)
    print("   Number of lines: ", all)
    print("   Number of code lines:", code)

    return (all, code)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: %s <file> [file1] [file2] ..." % sys.argv[0])
        sys.exit(1)

    lines = 0
    code = 0
    
    for arg in sys.argv[1:]:
        for file in glob.glob(arg):
            new = count(file)
            lines += new[0]
            code += new[1]

    print("\nTotal number of lines: %d" % lines)
    print("Total number of code lines: %d" % code)
