#!/usr/bin/env python
# learn how to use zipfile module

import sys, zipfile, os, os.path

def unzip_file_into_dir(file, dir):
    os.mkdir(dir, 0777)
    zfobj = zipfile.ZipFile(file)
    for name in zfobj.namelist():
        if name.endswith('/'):
            os.mkdir(os.path.join(dir, name))
        else:
            outfile = open(os.path.join(dir, name), 'wb')
            outfile.write(zfobj.read(name))
            outfile.close()

def main():
    unzip_file_into_dir(open(sys.argv[1]), sys.argv[2])

if __name__ == '__main__': main()
