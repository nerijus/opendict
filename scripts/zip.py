from zipfile import ZipFile
from glob import glob
import sys
import os

def compress(z, dir):
    zip = ZipFile(z, "w")
    files = glob(os.path.join(dir, "*"))
    for file in files:
        zip.write(file)
    zip.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Usage: %s <zip file> <directory>" % sys.argv[0]
        sys.exit(1)

    print "Packing '%s' to '%s'..." % (sys.argv[2], sys.argv[1]),
    compress(sys.argv[1], sys.argv[2])
    print "done"
