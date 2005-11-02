"""
  html2text.py

  convert an html doc to text
"""


# system libraries
import os, sys, string, time, getopt
import re

WIDTH = 80

def tag_replace (data,center,indent, use_ansi = 0):
  data = re.sub ("\s+", " ", data)
  data = re.sub ("(?s)<!--.*?-->", "", data)
  data = string.replace (data, "\n", " ")
  output = []

  # modified 6/17/99 splits on all cases of "img" tags
  # imgs = re.split ("(?s)(<img.*?>)", data)
  imgs = re.split ("(?si)(<img.*?>)", data)

  for img in imgs:
    if string.lower(img[:4]) == "<img":
      alt = re.search ("(?si)alt\s*=\s*\"([^\"]*)\"", img)
      if not alt:
        alt = re.search ("(?si)alt\s*=([^\s]*)", img)
      if alt:
        output.append ("%s" % img[alt.start(1):alt.end(1)])
      else:
        output.append ("[img]")
    else:
      output.append (img)
  data = string.join (output, "")
  data = re.sub ("(?i)<br>", "\n", data)
  data = re.sub ("(?i)<hr[^>]*>", "\n" + "-"*50 + "\n", data)
  data = re.sub ("(?i)<li>", "\n* ", data)
  if use_ansi:
    data = re.sub ("(?i)<h[0-9]>", "\n[32m", data)
  else:
    data = re.sub ("(?i)<h[0-9]>", "\n", data)
  if use_ansi:
    data = re.sub ("(?i)</h[0-9]>", "[0m\n", data)
  else:
    data = re.sub ("(?i)</h[0-9]>", "\n", data)
  data = re.sub ("(?i)<ul>", "\n<UL>\n", data)
  data = re.sub ("(?i)</ul>", "\n</UL>\n", data)
  data = re.sub ("(?i)<center>", "\n<CENTER>\n", data)
  data = re.sub ("(?i)</center>", "\n</CENTER>\n", data)
  data = re.sub ("(?i)</div>", "\n", data)
  if use_ansi:
    data = re.sub ("(?i)<b>", "[1m", data)
    data = re.sub ("(?i)</b>", "[0m", data)
    data = re.sub ("(?i)<i>", "[2m", data)
    data = re.sub ("(?i)</i>", "[0m", data)
    data = re.sub ("(?i)<title>", "\n<CENTER>\n[31m", data)
    data = re.sub ("(?i)</title>", "[0m\n</CENTER>\n", data)
  else:
    data = re.sub ("(?i)<title>", "\n<CENTER>\n", data)
    data = re.sub ("(?i)</title>", "\n</CENTER>\n", data)
  data = re.sub ("(?i)<p>", "\n", data)
  data = re.sub ("(?i)<tr[^>]*>", "\n", data)
  data = re.sub ("(?i)</table>", "\n", data)
  data = re.sub ("(?i)<td[^>]*>", "\t", data)
  data = re.sub ("(?i)<th[^>]*>", "\t", data)
  data = re.sub (" *\n", "\n", data)
  lines = string.split (data, "\n")
  output = []
  for line in lines:
    if line == "<UL>":
      indent = indent + 1
    elif line == "</UL>":
      indent = indent - 1
      if indent < 0: indent = 0
    elif line == "<CENTER>":
      center = center + 1
    elif line == "</CENTER>":
      center = center - 1
      if center < 0: center = 0
    else:
      if center:
        line = "  "*indent + string.strip(line)
        nline = re.sub("\[.*?m", "", line)
        nline = re.sub ("<[^>]*>", "", nline)
        c = WIDTH/2 - (len (nline) / 2)
        output.append (" "*c + line)
      else:
        output.append ("  "*indent + line)
  data = string.join (output, "\n")
  data = re.sub (" *\n", "\n", data)
  data = re.sub ("\n\n\n*", "\n\n", data)
  data = re.sub ("<[^>]*>", "", data)
  return (data, center, indent)

def html2text (data, use_ansi = 0, is_latin1 = 0):
  pre = re.split("(?s)(<pre>[^<]*</pre>)", data)
  out = []
  indent = 0
  center = 0
  for part in pre:
    if part[:5] != "<pre>":
      (res, center, indent) = tag_replace (part,center,indent, use_ansi)
      out.append (res)
    else:
      part = re.sub("(?i)</*pre>", "", part)
      out.append (part)
  data = string.join (out)
  data = re.sub ("&gt;", ">", data)
  data = re.sub ("&lt;", "<", data)
  data = re.sub ("&nbsp;", " ", data)
 
  return data


def usage(progname):
  print "usage: %s --help <htmlfile>" % progname
  print __doc__

def main(argc, argv):
  progname = argv[0]
  alist, args = getopt.getopt(argv[1:], "", ["help"])

  for (field, val) in alist:
    if field == "--help":
      usage(progname)
      return

  if len(args):
    file = args[0]
  else:
    return

  progname = argv[0]

  fp = open (file)
  data = fp.read()
  fp.close()

  if data:
    print (html2text(data))
  else:
    print "Document contained no data"

if __name__ == "__main__":
  main(len(sys.argv), sys.argv)


