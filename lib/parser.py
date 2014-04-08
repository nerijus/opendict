#
# OpenDict
# Copyright (c) 2003-2006 Martynas Jocius <martynas.jocius@idiles.com>
# Copyright (c) 2007 IDILES SYSTEMS, UAB <support@idiles.com>
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

import time
import string
import re
import os
import traceback
import xml.parsers.expat

from lib.extra import dictclient
from lib.extra import dictdlib
from lib import info
from lib import misc
from lib import errortype
from lib import meta
from lib import plaindict
from lib.logger import systemLog, debugLog, DEBUG, INFO, WARNING, ERROR


WORD_BG = "#dde2f1" # Bright blue
DICT_BG = "#b4bedb"

class SlowoParser(plaindict.PlainDictionary):
   """
   Built-in Slowo Parser

   Parses file in Slowo format.
   """

   def __init__(self, filePath):
      """Initialize"""

      self.filePath = filePath
      self.needsList = True
      
      self.name = os.path.splitext(os.path.basename(filePath))[0]

      # Additional information
      self.encoding = None
      self.checksum = None
      self.index = None

      self.configChanged = False


   def start(self):
      """Open file handle"""

      debugLog(DEBUG, "Opening file %s" % self.filePath)
      self.fd = open(self.filePath)


   def stop(self):
      """Close file handle"""

      try:
         debugLog(DEBUG, "Closing file %s" % self.filePath)
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

      from lib import dicttype
      return dicttype.SLOWO


   def setName(self, name):
      """Set new name"""

      self.name = name


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

      word_lowered = word.lower()

      encodedIndex = {}
      for literal in self.index:
         encodedIndex[literal.encode(self.getEncoding())] = \
                      self.index.get(literal)

      #
      # Seek to the beginning of the block
      #
      position = 0L
      if word_lowered[:2] in encodedIndex.keys():
         position = encodedIndex[word_lowered[:2]]

      debugLog(DEBUG, "Index: %s->%d" % (word_lowered[:2], position))
      debugLog(DEBUG, "SlowoParser: Seeking to %d" % position)
      
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
            try:
                orig, end = line.split('=', 1)
            except ValueError, e:
                systemLog(ERROR, '%s (line %s)' % (e, line))
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

      debugLog(DEBUG, "%d lines scanned" % _linesRead)
      
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

      debugLog(DEBUG, "SlowoParser: search took %f seconds" \
            % (time.time() - _start))

      return result



class MovaParser(plaindict.PlainDictionary):
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

      debugLog(DEBUG, "Opening file %s" % self.filePath)
      self.fd = open(self.filePath)
      

   def stop(self):
      """Close file handle"""

      try:
         debugLog(DEBUG, "Closing file %s" % self.filePath)
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

      from lib import dicttype
      return dicttype.MOVA


   def setName(self, name):
      """Set new name"""

      self.name = name


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

      word_lowered = word.lower()

      encodedIndex = {}
      for literal in self.index:
         encodedIndex[literal.encode(self.getEncoding())] = \
                      self.index.get(literal)

      #
      # Seek to the beginning of the block
      #
      position = 0L
      if word_lowered[:2] in encodedIndex.keys():
         position = encodedIndex[word_lowered[:2]]

      debugLog(DEBUG, "Index: %s->%d" % (word_lowered[:2], position))
      debugLog(DEBUG, "MovaParser: Seeking to %d" % position)
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

      debugLog(DEBUG, "%d lines scanned" % _linesRead)
      
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

      debugLog(DEBUG, "MovaParser: Search took %f seconds" \
               % (time.time() - _start))

      return result



# FIXME: Deprecated
class TMXParser(plaindict.PlainDictionary):
    """Built-in TMX parser.
    Reads TMX files and does the search.
    """

    def __init__(self, filePath):

       systemLog(WARNING, "***")
       systemLog(WARNING, "*** WARNING:")
       systemLog(WARNING, "*** TMX implementation is fuzzy and should " \
                 "not be used yet!")
       systemLog(WARNING, "***")

       self.name = os.path.splitext(os.path.basename(filePath))[0]
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


    def getType(self):
      """Return dictionary type"""

      return dicttype.TMX


    def setName(self, name):
      """Set new name"""

      self.name = name


    def getName(self):
       """Return file name"""

       return self.name


    def setEncoding(self, encoding):
      """Set encoding"""

      self.encoding = encoding

    
    def getEncoding(self):
       """Return encoding set for that dictionary"""
       
       return wx.GetApp().config.encoding


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
       found = False
       word_lowered = word.lower()

       for key in keys:
          if key.lower().find(word_lowered) == 0:
             avail.append(key)
             if not found:
                 result += "<u><b>%s</b></u><br>" % key
                 result += "<table><tr><td>"
                 result += "&nbsp;"*3+str("<br>"+"&nbsp;"*3).join(self.mapping[key])
                 result += "</td></tr></table>"
                 found = True

       result += "</font></body></html>"

       if len(avail) == 0:
          errno = 1

       return (result, avail, errno)


    def makeHashTable(self):
       pass
         


class DictParser(plaindict.PlainDictionary):
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

      name = os.path.splitext(os.path.splitext(\
         os.path.basename(self.filePath))[0])[0]
      indexFile = os.path.join(os.path.dirname(self.filePath),
                               name)
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

      from lib import dicttype
      return dicttype.DICT

   
   def setName(self, name):
      """Set new name"""

      self.name = name


   def getName(self):
      """Return file name"""
      
      return self.name


   def setEncoding(self, encoding):
      """Set encoding"""

      self.encoding = encoding
   

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

      word_lowered = word.lower()
      
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
            debugLog(DEBUG, "Retrying search...")
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

      debugLog(DEBUG, "DictParser: Search took % f seconds" \
            % (time.time() - _start))

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
      self.name = 'Connection to DICT server'


   def getUsesWordList(self):
      """Return True if uses word list, False otherwise"""

      return self.needsList


   def setName(self, name):
      """Set new name"""

      self.name = name


   def getName(self):
      """Return name"""

      return self.name


   def setEncoding(self, encoding):
      """Set encoding"""

      self.encoding = encoding


   def getEncoding(self):
      """Return encoding"""

      return self.encoding


   def search(self, word):
      """Lookup word"""

      result = meta.SearchResult()

      try:
         conn = dictclient.Connection(self.server, self.port)
      except:
         result.setError(errortype.CONNECTION_ERROR)
         return result

      html = []
      html.append("<html><head>" \
                  "<meta http-equiv=\"Content-Type\" " \
                  "content=\"text/html; charset=%s\">" \
                  "</head><body>" % self.getEncoding())

      found = False

      try:
         data = conn.define(self.db, word)
      except:
         data = []

      for d in data:
         found = True

         html.append("<p><table width=\"100%\"><tr>")
         html.append("<td bgcolor=\"%s\">" % DICT_BG)
         html.append("<b><i>%s</i></b></td></tr>" % d.getdb().getdescription())

         source = d.getdefstr()
         source = source.replace('<', '&lt;')
         source = source.replace('>', '&gt;')
         orig = source.split("\n", 1)[0]
         
         pron = re.findall("\[(.*?)\]", orig) # 1st comment type
         pronPatt = " [%s]"
         
         if len(pron) == 0:
            pron = re.findall("\/(.*?)\/", orig) # 2nd comment type
            pronPatt = " /%s/"
         if len(pron) == 0:
            pron = re.findall(r"\\(.*?)\\", orig) # 3rd comment type
            pronPatt = " \\%s\\"
         
         if len(pron) > 0:
            orig = "<b>%s</b> [<i>%s</i>]" % \
                   (orig.replace(pronPatt % pron[0], ""), pron[0])
         else:
            orig = "<b>%s</b>" % orig

         html.append("<tr><td bgcolor=\"%s\">" % WORD_BG)
         html.append("%s</td></tr>" % orig)

         source = source.replace('\n\n', '<br><br>')
         
         translation = ' '.join(source.split('\n')[:])
         links = re.findall("{(.*?)}", translation)
         for link in links:
            translation = translation.replace("{%s}" % link,
                              "<a href=\"%s\">%s</a>" % (link, link))
         html.append("<tr><td>%s</td></tr>" % translation)
         html.append("</table></p>")

      html.append("</body></html>")

      result.setTranslation(''.join(html))
      
      if not found:
         result.setError(errortype.NOT_FOUND)

      return result
