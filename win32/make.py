# Make Win32 executable for OpenDict

import os
import sys

#sys.path = [os.path.join(os.curdir, "lib")] + sys.path
sys.path = ["C:\\Program files\\OpenDict-dev\Opendict-source\lib"] + sys.path

odlist = "wx.Python.html,shutil,zipfile,string,"

list = "encodings,codecs,xml,ConfigParser,"\
"Cookie,copy,ftplib,glob,gopherlib,gzip,htmllib,HTMLParser,httplib,"\
"locale,re,sgmllib,socket,stat,StringIO,threading,thread,"\
"urllib,urllib2,urlparse,uu,warnings,webbrowser"

command = "C:\\python24\\python.exe setup.py py2exe -w " \
          "--icon ..\\pixmaps\\icon.ico -i %s " \
          "--packages encodings --force-imports encodings" % (odlist+list)
#command = "C:\\python22\\python.exe setup.py py2exe  --icon ..\\pixmaps\\icon.ico"
print "Command: '%s'\n" % command

out = os.popen(command)

print "\"dist\" directory will be created."
print "Compiling, will take a minute...\n", out.read()

raw_input("<Enter>...")
