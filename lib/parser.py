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
import traceback
import xml.parsers.expat
from wxPython.wx import wxGetApp

#from misc import errors
from extra import dictclient
from extra import dictdlib
import info
import misc
import errortype
import meta


#WORD_BG = "#cad1e5" # Normal blue
WORD_BG = "#dde2f1" # Bright blue

# TODO:
# 1. Remove wx from this module
# 2. Add start() stop() methods to parser classes
# 3. Apply new error system


# TODO: Check algorithm
## def binarySearchIndex(data, word):

##    sub = data

##    while len(sub) > 1:
##       index = len(sub) / 2
##       #w = re.findall("\<u\>(.*?)\<\/u\>", sub[index])[0]
##       w = sub[index]
##       c = cmp(w, word)
##       if c == -1:
##          sub = sub[index:]
##       elif c == 1:
##          sub = sub[:index]
##       else:
##          break

##       return data.index(sub[0])


class SlowoParser(meta.Dictionary):
   """
   Built-in Slowo Parser

   Parses file in Slowo format.
   """

   def __init__(self, filePath):
      """Initialize"""

      self.filePath = filePath
      self.needsList = True
      
      self.encoding = None
      self.name = os.path.splitext(os.path.basename(filePath))[0]

      # Additional information
      self.encoding = None
      self.checksum = None
      self.index = None

      self.configChanged = False


   def start(self):
      """Open file handle"""

      print "DEBUG Opening file %s" % self.filePath
      self.fd = open(self.filePath)


   def stop(self):
      """Close file handle"""

      try:
         print "DEBUG Closing file..."
         self.fd.close()
      except:
         pass


   def setIndex(self, index):
      """Set index table"""

      self.index = index


   def getPath(self):
      """Return full file path"""

      return self.filePath


   def setChecksum(self, newSum, first=False):
      """Set checksum. Used after checksum change"""

      if self.checksum == None:
         self.configChanged = True

      self.checksum = newSum


   def getChecksum(self):
      """Return checksum"""

      return self.checksum


   def getType(self):
      """Return dictionary type"""

      import dicttype
      return dicttype.SLOWO


   def getName(self):
      """Return file name"""

      return self.name


   def setEncoding(self, encoding):
      """Set encoding"""

      self.encoding = encoding
      self.configChanged = True


   def getEncoding(self):
      """Return encoding set for that dictionary"""

      return self.encoding


   def getUsesWordList(self):
      """Return True if uses word list, False otherwise"""

      return self.needsList


   def _appendTranslation(self, html, orig, trans):
      """Appends HTML strings to list"""

      html.append("<table width=\"100%\"><tr>")
      html.append("<td bgcolor=\"%s\">" % WORD_BG)
      html.append("<b>%s</b></td></tr>" % orig)
      html.append("<tr><td>")
      html.append("<p>%s</p>" % trans)
      html.append("</td></tr></table>")
      

   def search(self, word):
      """Lookup word"""

      _start = time.time()

      word_lowered = word.lower().encode(self.getEncoding())

      #
      # Seek to the beginning of the block
      #
      position = 0L
      if word_lowered[:2] in self.index.keys():
         position = self.index[word_lowered[:2]]

      print "DEBUG Index: %s->%d" % (word_lowered[:2], position)
      print "DEBUG SlowoParser: Seeking to %d" % position
      
      self.fd.seek(position)

      html = []

      html.append("<html><head>")
      html.append("<meta http-equiv=\"Content-Type\" " \
                  "content=\"text/html; charset=%s\">" \
                  % str(self.getEncoding()))
      html.append("<head><body>")

      found = False
      words = []

      result = meta.SearchResult()

      # DEBUG
      _linesRead = 0

      for line in self.fd.xreadlines():
         _linesRead += 1
         line = line.strip()
         try:
            orig, end = line.split('=', 1)
            orig = orig.strip()
            chunks = end.split(';')

            translation = ["<ul>"]
            for chunk in chunks:
               comment = []
               trans = chunk.split('//')
               
               if len(trans) > 1:
                  comment = trans[1:]

               trans = trans[:1]
                  
               trans = "".join(trans).strip()
               comment = "".join(comment).strip()
               
               if len(trans) and len(comment) != 0:
                  translation.append("<li>%s (<i>%s</i>)</li>" \
                                     % (trans, comment))
               elif len(trans):
                  translation.append("<li>%s</li>" % trans)

            translation.append("</ul>")

            translation = "".join(translation)

         except:
            traceback.print_exc()
            continue

         if line.lower().startswith(word_lowered):   
            
            if not orig.lower().startswith(word_lowered):
               break
            
            if orig.lower() == word_lowered and not found:
               found = True
               self._appendTranslation(html, orig, translation)               
               
            words.append(orig)
            if len(words) == 1:
               suggestedWord = orig
               suggestedTrans = translation
         elif len(words):
            break

      print "%d lines scanned" % _linesRead
      
      if not found:
         if words:
            self._appendTranslation(html, suggestedWord, suggestedTrans)
         else:
            result.setError(errortype.NOT_FOUND)

      html.append("</font></body></html>")

      try:
         translation = "".join(html)
      except:
         result.setError(errortype.INVALID_ENCOFING)
         translation = ""
      
      result.setTranslation(translation)
      result.setWordList(words)

      print "DEBUG SlowoParser: search took %f seconds" \
            % (time.time() - _start)

      return result



class MovaParser(meta.Dictionary):
   """
   Built-in Mova Parser

   Parses file in 'Mova' dictionary format and does
   the search.
   """

   def __init__(self, filePath):
      """Initialize"""

      self.filePath = filePath
      self.needsList = True

      self.name = os.path.splitext(os.path.basename(filePath))[0]

      # Additional variables
      self.encoding = None
      self.checksum = None
      self.index = None
      

      # If this is True when closing, the new configuration will be
      # written to disk
      self.configChanged = False


   def start(self):
      """Open file handle"""

      print "DEBUG Opening file %s" % self.filePath
      self.fd = open(self.filePath)

      # TODO: Will be indexed
      #self.data = self.fd.readlines()
      #print "%d lines read" % len(self.data)
      

   def stop(self):
      """Close file handle"""

      try:
         print "DEBUG Closing file..."
         self.fd.close()
      except:
         pass
         

   def setIndex(self, index):
      """Set index table"""

      self.index = index


   def getPath(self):
      """Return full file path"""

      return self.filePath


   def setChecksum(self, newSum, first=False):
      """Set checksum. Used after chekcsum change"""

      if self.checksum == None:
         self.configChanged = True

      self.checksum = newSum

      # If checksum is set not for the first time, remember to
      # update configuration
      #if not first:
      #   self.configChanged = True


   def getChecksum(self):
      """Return checksum"""

      return self.checksum
      

   def getType(self):
      """Return dictionary type"""

      import dicttype
      return dicttype.MOVA


   def getName(self):
      """Return file name"""

      return self.name


   def setEncoding(self, encoding):
      """Set encoding"""

      self.encoding = encoding
      self.configChanged = True


   def getEncoding(self):
      """Return encoding set for this dictionary"""

      return self.encoding


   def getUsesWordList(self):
      """Return True if uses word list, False otherwise"""

      return self.needsList


   def _appendTranslation(self, html, orig, trans):
      """Appends HTML strings to list"""

      html.append("<table width=\"100%\"><tr>")
      html.append("<td bgcolor=\"%s\">" % WORD_BG)
      html.append("<b>%s</b></td></tr>" % orig)
      html.append("<tr><td>")
      html.append("<p>%s</p>" % trans)
      html.append("</td></tr></table>")
      

   def search(self, word):
      """Lookup word"""

      _start = time.time()

      word_lowered = word.lower().encode(self.getEncoding())

      #
      # Seek to the beginning of the block
      #
      position = 0L
      if word_lowered[:2] in self.index.keys():
         position = self.index[word_lowered[:2]]

      print "DEBUG Index: %s->%d" % (word_lowered[:2], position)

      print "DEBUG MovaParser: Seeking to %d" % position
      self.fd.seek(position)

      html = []

      html.append("<html><head>")
      html.append("<meta http-equiv=\"Content-Type\" " \
                  "content=\"text/html; charset=%s\">" \
                  % str(self.getEncoding()))
      html.append("<head><body>")

      found = False
      words = []

      result = meta.SearchResult()

      # DEBUG
      _linesRead = 0

      for line in self.fd.xreadlines():
         _linesRead += 1
         line = line.strip()
         try:
            orig, trans = line.split("  ", 1)
         except:
            continue

         if line.lower().startswith(word_lowered):   
            
            if not orig.lower().startswith(word_lowered):
               break
            
            if orig.lower() == word_lowered and not found:
               found = True
               self._appendTranslation(html, orig, trans)               
               
            words.append(orig)
            if len(words) == 1:
               suggestedWord = orig
               suggestedTrans = trans
         elif len(words):
            break

      print "%d lines scanned" % _linesRead
      
      if not found:
         if words:
            self._appendTranslation(html, suggestedWord, suggestedTrans)
         else:
            result.setError(errortype.NOT_FOUND)

      html.append("</font></body></html>")

      try:
         translation = "".join(html)
      except:
         result.setError(errortype.INVALID_ENCOFING)
         translation = ""
      
      result.setTranslation(translation)
      result.setWordList(words)

      print "DEBUG MovaParser: Search took %f seconds" % (time.time() - _start)

      return result



# FIXME: Deprecated
class TMXParser(meta.Dictionary):
    """Built-in TMX parser.
    Reads TMX files and does the search.
    """

    def __init__(self, filePath):

       print "***"
       print "*** WARNING:"
       print "*** TMX implementation is fuzzy and should not be used yet!"
       print "***"

       #self.window = window
       self.name = os.path.splitext(os.path.basename(filePath))[0]
       #self.needsList = wxGetApp().config.useListWithRegs
       self.needsList = True
       self.encoding = None

       self.mapping = {}
       self.header = {}
       self.trans = []
       self.inSeg = 0
       self.lang = ""


    def start(self):
       """Allocate resources"""

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

   def __init__(self, filePath):
      """Initialize"""

      self.filePath = filePath
      self.needsList = True
      self.name = os.path.splitext(os.path.splitext(os.path.basename(filePath))[0])[0]
      self.encoding = 'UTF-8'
      self.checksum = None

      self.configChanged = False

      self.dict = None
      self.definitions = None


   def start(self):
      """Allocate resources"""

      indexFile = os.path.join(os.path.dirname(self.filePath),
                               self.name)
      self.dict = dictdlib.DictDB(indexFile)


   def stop(self):
      """Free resources"""

      if self.dict:
         del self.dict


   def getPath(self):
      """Return full file path"""

      return self.filePath


   def getType(self):
      """Return dictionary type"""

      import dicttype
      return dicttype.DICT


   def getName(self):
      """Return file name"""
      
      return self.name


   def setEncoding(self, encoding):
      """Set encoding"""

      self.encoding = encoding
      #pass
   

   def getEncoding(self):
      """Return encoding set for that dictionary"""

      return self.encoding


   def setChecksum(self, newSum):
      """Set checksum. Used after chekcsum change"""

      if self.checksum == None:
         self.configChanged = True

      self.checksum = newSum


   def getUsesWordList(self):
      """Return True if uses word list, False otherwise"""

      return self.needsList


   def _getTranslation(self, word):
      """Return word and translation code without formatting
      full HTML document"""


      translations = self.dict.getdef(word)

      orig = None
      translation = None
      
      for source in translations:
         try:
            source = source.encode(self.encoding, 'replace')
         except:
            result.setError(errortype.INVALID_ENCODING)
            break
         
         chunks = source.split('\n')
         map(string.strip, chunks)
         
         orig = chunks[0]
         pron = re.findall("\[(.*?)\]", orig)
         if len(pron) > 0:
            orig = "<b>%s</b> [<i>%s</i>]" % \
                   (orig.replace(" [%s]" % pron[0], ""), pron[0])
         else:
            orig = "<b>%s</b>" % orig

         translation = ['<ul>']
         for c in chunks[1:]:
            if len(c) > 0:
               translation.append("<li>%s</li>" % c)
         translation.append('</ul>')

         translation = "".join(translation)
         
         links = re.findall("{(.*?)}", translation)
         for link in links:
            translation = translation.replace("{%s}" % link,
                                              "<a href=\"%s\">%s</a>" \
                                              % (link, link))

      return (orig, translation)


   def search(self, word):
      """Lookup word"""

      _start = time.time()

      result = meta.SearchResult()

      try:
         word_lowered = word.lower().encode(self.getEncoding())
      except:
         result.setError(errortype.INVALID_ENCODING)
         return result
      

      if self.definitions is None:
         self.definitions = self.dict.getdeflist()
         self.definitions.sort()

      words = []

      for definition in self.definitions:
         if definition.lower().startswith(word_lowered):
            words.append(definition)

      html = []

      html.append("<html><head>")
      html.append("<meta http-equiv=\"Content-Type\" " \
                  "content=\"text/html; charset=%s\">" \
                  % str(self.getEncoding()))
      html.append("<head><body>")

      (orig, translation) = self._getTranslation(word)

      if not translation:
         if len(words):
            print "Retrying search..."
            _word = words[0]
            orig, translation = self._getTranslation(_word)
            if not translation:
               result.setError(errortype.NOT_FOUND)
         else:
            result.setError(errortype.NOT_FOUND)
            translation = ""

      html.append("<table width=\"100%\"><tr>")
      html.append("<td bgcolor=\"%s\">" % WORD_BG)
      html.append("<b>%s</b></td></tr>" % orig)
      html.append("<tr><td>")
      html.append("<p>%s</p>" % translation)
      html.append("</td></tr></table>")
      html.append("</body></html>")

      result.setTranslation("".join(html))
      result.setWordList(words)

      print "DEBUG DictParser: Search took % f seconds" \
            % (time.time() - _start)

      return result


# TODO:
# 1. This is not a parser, move to another module
# 2. Add needed methods
# 
class DictConnection(meta.Dictionary):
   """Built-in DICT client
   Connects to a DICT server abd does the search.
   """

   def __init__(self, server, port, db, strategy):

      self.server = server
      self.port = port
      self.db = db
      self.strategy = strategy
      self.encoding = "UTF-8"
      self.needsList = 0


   def getUsesWordList(self):
      """Return True if uses word list, False otherwise"""

      return self.needsList


   def setEncoding(self, encoding):
      """Set encoding"""

      self.encoding = encoding


   def getEncoding(self):
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
         translation = string.join(trans[1:], "<br>"+"&nbsp;"*4)

         links = re.findall("{(.*?)}", str)
         for link in links:
            translation = str.replace("{%s}"%link,
                              "<a href=\"%s\">%s</a>"%(link, link))
         result += "%s<p>" % translation

      #return (result, alt, 0)
         
      result += "</font></body></html>"
      
      if not found:
         errno = 1

      return (result, [], errno)
