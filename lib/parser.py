# -*- coding: utf-8 -*-

# OpenDict
# Copyright (c) 2003 Martynas Jocius <mjoc@delfi.lt>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your opinion) any later version.
#
# This program is distributed in the hope that will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MECHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more detals.
#
# You shoud have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# 02111-1307 USA
#
# Module: parser

import time
import string
import re
import os
import xml.parsers.expat
from wxPython.wx import wxGetApp

from misc import errors
from extra import dictclient
from extra import dictdlib
import info
import misc
import errortype
import meta


def binarySearchIndex(data, word):

   sub = data

   while len(sub) > 1:
      index = len(sub) / 2
      #w = re.findall("\<u\>(.*?)\<\/u\>", sub[index])[0]
      w = sub[index]
      c = cmp(w, word)
      if c == -1:
         sub = sub[index:]
      elif c == 1:
         sub = sub[:index]
      else:
         break

      return data.index(sub[0])


class SlowoParser(meta.Dictionary):
   """
   Built-in Slowo Parser

   Parses file in Slowo dictionary format and does
   the search.
   """

   def __init__(self, file):

      #self.window = window
      self.needsList = wxGetApp().config.useListWithRegs
      self.fd = open(file)

      self.encoding = None
      self.name = os.path.split(file)[1]


   def getType(self):
      """Return dictionary type"""

      return dicttype.SLOWO


   def getName(self):
      """Return file name"""

      return self.name


   def setEncoding(self, encoding):
      """Set encoding"""

      self.encoding = encoding


   def getEncoding(self):
      """Return encoding set for that dictionary"""

      return self.encoding


   def getUsesWordList(self):
      """Return True if uses word list, False otherwise"""

      return self.needsList


   def search(self, word):
      """Lookup word"""
      
      errno = 0
      word_lowered = word.lower()
      self.time = time.time()
      l = word_lowered[0:2]

      pos = 0
      if self.hash.has_key(l) == 0:
         if len(word_lowered) == 1:
            keys = self.hash.keys()
            keys.sort()
            for k in keys:
               try:
                   if k[0] == l:
                       pos = self.hash[k]
                       self.fd.seek(pos)
                       break
               except:
                   misc.printError()
                   return ("", [], 6)
         else:
            return ("", [], 1)

      else:
         pos = self.hash[l]
         self.fd.seek(pos)

      keys = self.hash.keys()
      keys.sort()
      end = pos

      if len(l) == 1:
         i = 0
         for k in keys:
            if k[0] == l:
               i = keys.index(k)

         if i < len(keys) - 1:
            end = self.hash[keys[i+1]]
         else:
            end = -1
      else:
         if keys.index(l) != len(keys) - 1:
            end = self.hash[keys[keys.index(l)+1]]
         else:
            end = -1

      if end > -1:
         data = self.fd.read(end-pos).split("\n")
      else:
         data = self.fd.read().split("\n")
         
      

      # Unused until we're sure that the dictionary is well-sorted
      #data = data[binarySearchIndex(data, word):]

      result = "<html><head>" \
               "<meta http-equiv=\"Content-Type\" " \
               "content=\"text/html; charset=%s\">" \
               "</head><body>"
               #"<font face=\"%s\" size=\"%s\">" % (self.window.encoding,
               #                                    self.window.app.config.fontFace,
               #                                    self.window.app.config.fontSize)


      found = 0
      list = []
      appended = 0
      
      for line in data:
         #if info.__unicode__:
             #try:
             #    line = line.decode(self.window.encoding)
             #except:
             #    return ("", [], 6)
         
         if line.lower().find(word_lowered) > -1:
            orig = line.split("=")[0].strip()
            
            if orig.lower().find(word_lowered) != 0:
               continue
            if found == 0:
               found = 1
               result += "<u><b>%s</b></u><br>" % orig
               trans = line.split("=")[1].split("//")[0].split(";")
               map(string.strip, trans)
            
               result += "<table><tr><td>"
               result += "&nbsp;"*3+str("<br>"+"&nbsp;"*3).join(trans)
               #result += string.join(trans, "<br>" + "&nbsp;"*4)
               if line.find("//") > -1:
                  comm = line.split("//")[1].split(";")[0].strip()
               
                  if len(comm) > 0:
                     result += "<br>" + "&nbsp;"*4 + "<i>(%s)</i>" % comm
                     
               result += "</td></tr></table>"

            # Gtk has list size limitation
            if os.name == "posix":
                if appended < 2000:
                    list.append(orig)
                    appended += 1
            else:
                list.append(orig)

      result += "</font></body></html>"
      
      #print result
      #print type(result)
      #print self.window.encoding

      if found == 0:
         errno = 1

      print "SlowoParser: Search took %s sec" % (time.time() - self.time)

      return (result, list, errno)


   def makeHashTable(self):

      print "Indexing..."
      self.hash = {}

      self.fd.seek(0)
      line = self.fd.readline()
      l = line[0:2].lower()
      n = 0

      self.hash[l] = n
      n += len(line)

      for line in self.fd.readlines():
         l = line[0:2].lower()
         if not self.hash.has_key(l):
            self.hash[l] = n
         n += len(line)

      for l, p in self.hash.items():
         print l, p


class MovaParser(meta.Dictionary):
   """
   Built-in Mova Parser

   Parses file in 'Mova' dictionary format and does
   the search.
   """

   def __init__(self, file):

      #self.window = window
      self.needsList = wxGetApp().config.useListWithRegs
      self.fd = open(file)

      assert self.fd.read(1024).find("  ") > -1

      self.encoding = None
      
      self.name = os.path.split(file)[1]


   def getType(self):
      """Return dictionary type"""

      return dicttype.MOVA


   def getName(self):
      """Return file name"""

      return self.name


   def setEncoding(self, encoding):
      """Set encoding"""

      self.encoding = encoding


   def getEncoding(self):
      """Return encoding set for this dictionary"""

      return self.encoding


   def getUsesWordList(self):
      """Return True if uses word list, False otherwise"""

      return self.needsList


   def search(self, word):
      """Lookup word"""

      errno = 0
      #self.time = time.time()
      word_lowered = word.lower()
      l = word_lowered[0:2]

      pos = 0
      if self.hash.has_key(l) == 0:
         if len(word) == 1:
            keys = self.hash.keys()
            keys.sort()
            for k in keys:
               try:
                   if k[0] == l:
                       pos = self.hash[k]
                       self.fd.seek(pos)
                       break
               except:
                   misc.printError()
                   return ("", [], 6)
         else:
            return ("", [], 1)

      else:
         pos = self.hash[l]
         self.fd.seek(pos)


      keys = self.hash.keys()
      keys.sort()
      end = pos

      if len(l) == 1:
         i = 0
         #for k in keys:
            #print "k type: ", type(k)
            
            #print type(k), type(l)
            #if info.__unicode__:
            #    try:
            #        if k[0].decode(self.window.encoding) == l:
            #            i = keys.index(k)
            #    except:
            #        return ("", [], 6)

         if i < len(keys) - 1:
            end = self.hash[keys[i+1]]
         else:
            end = -1
      else:
         if keys.index(l) != len(keys) - 1:
            end = self.hash[keys[keys.index(l)+1]]
         else:
            end = -1

      if end > -1:
         data = self.fd.read(end-pos).split("\n")
      else:
         data = self.fd.read().split("\n")

      #data = data[binarySearchIndex(data, word):]

      result = "<html><head>" \
               "<meta http-equiv=\"Content-Type\" " \
               "content=\"text/html; charset=%s\">" \
               "</head><body>"
               #"<font face=\"%s\" size=\"%s\">" % (self.window.encoding,
               #                                    self.window.app.config.fontFace,
               #                                    self.window.app.config.fontSize)


      found = 0
      list = []

      for line in data:
         #try:
         #   line = line.decode(self.window.encoding)
         #except:
         #   return ("", [], 6)

         #print type(line)
         #line = line.decode(self.window.encoding)
         #print type(line)
              
         if line.lower().find(word_lowered) > -1:
            orig = line.split("  ")[0].strip()
            if orig.lower().find(word_lowered) != 0:
               continue
            if found == 0:
               found = 1
               result += "<b><u>%s</u></b><br>" % orig + "&nbsp;"*4
               trans = '&nbsp;&nbsp;'.join(line.split("  ")[1:]).strip()
               result += "<table><tr><td>"
               result += "&nbsp;"*4 + "%s<p>" % trans
               result += "</td></tr></table>"

            list.append(orig)

      result += "</font></body></html>"

      if found == 0:
         errno = 1
      #print "Search took %s sec" % (time.time() - self.time)

      return (result, list, errno)

   def makeHashTable(self):

      print "Indexing..."
      self.hash = {}

      self.fd.seek(0)
      line = self.fd.readline()
      l = line[0:2].lower()
      n = 0

      self.hash[l] = n
      n += len(line)

      for line in self.fd.readlines():
         l = line[0:2].lower()
         if not self.hash.has_key(l):
            self.hash[l] = n
         n += len(line)


# TODO: Rewrite this one
class TMXParser(meta.Dictionary):
    """Built-in TMX parser.
    Reads TMX files and does the search.
    """

    def __init__(self, file=""):

       #self.window = window
       self.name = file
       self.needsList = wxGetApp().config.useListWithRegs
       self.encoding = None

       self.mapping = {}
       self.header = {}
       self.trans = []
       self.inSeg = 0
       self.lang = ""

       parser = xml.parsers.expat.ParserCreate()
       parser.StartElementHandler = self.startElement
       parser.EndElementHandler = self.endElement
       parser.CharacterDataHandler = self.charData

       if file != "":
          fd = open(file)
          parser.Parse(fd.read(), 1)
          fd.close()

       for word in self.mapping.keys():
           print self.mapping[word]


    def getType(self):
      """Return dictionary type"""

      return dicttype.TMX


    def getName(self):
       """Return file name"""

       return self.name


    def setEncoding(self, encoding):
      """Set encoding"""

      self.encoding = encoding

    
    def getEncoding(self):
       """Return encoding set for that dictionary"""
       
       return wxGetApp().config.encoding


    def getUsesWordList(self):
       """Return True if uses word list, False otherwise"""
       
       return self.needsList

           
    def startElement(self, name, attrs):
       """Part of SAX parsing method"""

       if name == "tu":
          self.inTu = 1
       elif name == "tuv":
          self.inTuv = 1
          self.lang = attrs["lang"]
       elif name == "seg":
          self.inSeg = 1
       elif name == "header":
          self.header["srclang"] = attrs["srclang"]
          self.header["creationtool"] = attrs["creationtool"]
          self.header["creationtoolversion"] = attrs["creationtoolversion"]
          self.header["o-tmf"] = attrs["o-tmf"]
          self.header["adminlang"] = attrs["adminlang"]
          self.header["datatype"] = attrs["datatype"]
          self.header["segtype"] = attrs["segtype"]


    def endElement(self, name):
       """Part of SAX parsing method"""

       if name == "tu":
          self.inTu = 0
          self.mapping.setdefault(self.orig, []).extend(self.trans)
          self.trans = []
       elif name == "tuv":
          self.inTuv = 0
       elif name == "seg":
          self.inSeg = 0


    def charData(self, data):
       """Part of SAX parsing method"""

       if self.inSeg:
          if self.lang == self.header["srclang"]:
             self.orig = data
          else:
             self.trans.append(data)
             #print "TMXParser: data '%s'" % data


    def search(self, word):
       """Lookup word"""
       
       errno = 0

       result = "<html><head>" \
                "<meta http-equiv=\"Content-Type\" " \
                "content=\"text/html; charset=%s\">" \
                "</head><body>"
                #"<font face=\"%s\" size=\"%s\">" % (self.window.encoding,
                #                                    self.window.app.config.fontFace,
                #                                    self.window.app.config.fontSize)

       keys = self.mapping.keys()
       avail = []
       found = 0
       word_lowered = word.lower()

       for key in keys:
          if key.lower().find(word_lowered) == 0:
             avail.append(key)
             if not found:
                 result += "<u><b>%s</b></u><br>" % key
                 result += "<table><tr><td>"
                 result += "&nbsp;"*3+str("<br>"+"&nbsp;"*3).join(self.mapping[key])
                 result += "</td></tr></table>"
                 found = 1

       result += "</font></body></html>"

       if len(avail) == 0:
          errno = 1

       return (result, avail, errno)


    def makeHashTable(self):
       pass
         

class DictParser(meta.Dictionary):
   """Built-in dictd dictionaries parser.
   Reads dictd dictionaries and does the search.
   """

   def __init__(self, path):

      #self.window = window
      self.needsList = 0

      # Hrrr!!!
      if path.find(".dict.dz") > -1:
         self.name = path.replace(".dict.dz", "")
      else:
         self.name = path.replace(".dict", "")

      self.encoding = None

      self.dict = dictdlib.DictDB(self.name)

      self.name = os.path.split(self.name)[1]


   def getType(self):
      """Return dictionary type"""

      return dicttype.DICT


   def getName(self):
      """Return file name"""
      
      return self.name


   def setEncoding(self, encoding):
      """Set encoding"""

      self.encoding = encoding
   

   def getEncoding(self):
      """Return encoding set for that dictionary"""

      return wxGetApp().config.encoding


   def getUsesWordList(self):
      """Return True if uses word list, False otherwise"""

      return self.needsList


   def search(self, word):
      """Lookup word"""

      word_lowered = word.lower()
      errno = 0

      result = "<html><head>" \
               "<meta http-equiv=\"Content-Type\" " \
               "content=\"text/html; charset=%s\">" \
               "</head><body>"
               #"<font face=\"%s\" size=\"%s\">" % (self.window.encoding,
               #                                    self.window.app.config.fontFace,
               #                                    self.window.app.config.fontSize)


      list = self.dict.getdef(word)
      if len(list) == 0:
         list = self.dict.getdef(word.lower())
         if len(list) == 0:
            list = self.dict.getdef(word.title())
      for defstr in list:
         trans = defstr.split("\n")
         orig = trans[0]
         pron = re.findall("\[(.*?)\]", orig)
         if len(pron) > 0:
            orig = "<b><u>%s</u></b> [<i>%s</i>]<br>" % \
                   (orig.replace(" [%s]"%pron[0], ""), pron[0])
         else:
            orig = "<b><u>%s</u></b><br>" % orig

         result += orig + "&nbsp;"*4
         str = string.join(trans[1:], "<br>"+"&nbsp;"*4)
         links = re.findall("{(.*?)}", str)
         for link in links:
            str = str.replace("{%s}"%link,
                              "<a href=\"%s\">%s</a>"%(link, link))
         result += str.replace(" ", "&nbsp;")+ "<p>"

      if len(list) == 0:
         errno = 1

      result += "</font></body></html>"

      return (result, [], errno)


# TODO: add needee methods
class DictConnection(meta.Dictionary):
   """Built-in DICT client
   Connects to a DICT server abd does the search.
   """

   def __init__(self, server, port, db, strategy):

      #self.window = window
      self.server = server
      self.port = port
      self.db = db
      self.strategy = strategy
      self.encoding = None
      self.needsList = 0


   def getUsesWordList(self):
      """Return True if uses word list, False otherwise"""

      return self.needsList


   def setEncoding(self, encoding):
      """Set encoding"""

      self.encoding = encoding


   def getEncoding(self, encoding):
      """Return encoding"""

      return self.encoding


   def search(self, word):
      """Lookup word"""

      errno = 0

      try:
         conn = dictclient.Connection(self.server, self.port)
      except:
         return ("", [], 4)

      result = "<html><head>" \
               "<meta http-equiv=\"Content-Type\" " \
               "content=\"text/html; charset=%s\">" \
               "</head><body>"
               #"<font face=\"%s\" size=\"%s\">" % (self.window.encoding,
               #                                    self.window.app.config.fontFace,
               #                                    self.window.app.config.fontSize)


      found = 0

      try:
         #data = conn.match(self.db, "prefix", word)
         data = conn.define(self.db, word)
      except:
          data = []

      #alt = []
          
      for d in data:
         #alt.append(d.getdefstr().split("\n")[0])
         #result += "<p>"+d.getdefstr()
         #continue
         
         found = 1
         result += "<table><tr><td bgcolor=\"#cccccc\">" \
                   "<b>%s</b></td></tr></table>" % d.db.getdescription()

         trans = d.getdefstr().split("\n")
         orig = trans[0]
         
         print "Word:", word, "Orig:", orig
         
         #if orig != word:
         #alt.append(orig)

         pron = re.findall("\[(.*?)\]", orig)
         if len(pron) > 0:
            orig = "<b><u>%s</u></b> [<i>%s</i>]<br>" % \
                   (orig.replace(" [%s]"%pron[0], ""), pron[0])
         else:
            orig = "<b><u>%s</u></b><br>" % orig

         result += orig + "&nbsp;"*4
         str = string.join(trans[1:], "<br>"+"&nbsp;"*4)

         links = re.findall("{(.*?)}", str)
         for link in links:
            str = str.replace("{%s}"%link,
                              "<a href=\"%s\">%s</a>"%(link, link))
         result += "%s<p>" % str

      #return (result, alt, 0)
         
      result += "</font></body></html>"
      
      if not found:
         errno = 1

      return (result, [], errno)
