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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301 USA
#

import time
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
      self.fd = open(self.filePath, 'rb')


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

      # The word comes encoded in the dictionary's encoding. The dictionary
      # file is read as bytes and each line is decoded with that same
      # encoding, so everything below works on text (str).
      encoding = self.getEncoding()
      if isinstance(word, bytes):
         word = word.decode(encoding)

      word_lowered = word.lower()

      #
      # Seek to the beginning of the block
      #
      position = self.index.get(word_lowered[:2], 0)

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

      for line in self.fd:
         _linesRead += 1
         try:
            line = line.decode(encoding).strip()
         except UnicodeDecodeError:
            continue
         try:
            orig = ""
            end = ""
            try:
                orig, end = line.split('=', 1)
            except ValueError as e:
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
      self.fd = open(self.filePath, 'rb')
      

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

      # The word comes encoded in the dictionary's encoding. The dictionary
      # file is read as bytes and each line is decoded with that same
      # encoding, so everything below works on text (str).
      encoding = self.getEncoding()
      if isinstance(word, bytes):
         word = word.decode(encoding)

      word_lowered = word.lower()

      #
      # Seek to the beginning of the block
      #
      position = self.index.get(word_lowered[:2], 0)

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

      for line in self.fd:
         _linesRead += 1
         try:
            line = line.decode(encoding).strip()
         except UnicodeDecodeError:
            continue
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
      self.stripKeys = True


   def start(self):
      """Allocate resources"""

      name = os.path.splitext(os.path.splitext(\
         os.path.basename(self.filePath))[0])[0]
      indexFile = os.path.join(os.path.dirname(self.filePath),
                               name)
      self.dict = dictdlib.DictDB(indexFile)

      # Unless the database has this entry, dictfmt kept only ASCII letters,
      # digits and spaces in the index keys (a word ending in a non-ASCII
      # letter is indexed without it) and dictd strips searched words
      # the same way
      self.stripKeys = not self.dict.hasdef(b'00-database-allchars')


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


   # Index keys are stripped (see start()), so real headwords have to be
   # read from definitions. Do that only for a reasonable number of keys.
   MAX_STRIPPED_KEYS = 200


   def _stripWord(self, word):
      """Return word the way dictfmt writes it to the index of a database
      built without the 00-database-allchars entry: only ASCII letters,
      digits, space and tab are kept, so 8-bit letters are lost."""

      return bytes(b for b in word
                   if b < 128 and (chr(b).isalnum() or b in b' \t'))


   def _splitDefinition(self, source):
      """Decode raw definition and return (headword, pronunciation,
      lines of translation)"""

      source = source.decode(self.encoding)
      chunks = source.split('\n')

      orig = chunks[0]
      pron = re.findall(r"\[(.*?)\]", orig)
      if len(pron) > 0:
         return (orig.replace(" [%s]" % pron[0], ""), pron[0], chunks[1:])

      return (orig, None, chunks[1:])


   def _getTranslations(self, key, wanted=None, strict=False):
      """Return a list of (word, translation) HTML code pairs for all
      definitions stored under the index key, without formatting full
      HTML document. Several words can share one (stripped) key, so if
      wanted (text) is given, definitions with that headword (or starting
      with it) are preferred. If there are none, all definitions are
      returned, unless strict is true."""

      found = []

      for source in self.dict.getdef(key):
         headword, pron, lines = self._splitDefinition(source)

         if pron:
            orig = "<b>%s</b> [<i>%s</i>]" % (headword, pron)
         else:
            orig = "<b>%s</b>" % headword

         translation = ['<ul>']
         for c in lines:
            if len(c) > 0:
               translation.append("<li>%s</li>" % c)
         translation.append('</ul>')

         translation = "".join(translation)
         
         links = re.findall("{(.*?)}", translation)
         for link in links:
            translation = translation.replace("{%s}" % link,
                                              "<a href=\"%s\">%s</a>" \
                                              % (link, link))

         found.append((headword.strip(), orig, translation))

      if wanted is not None:
         wanted = wanted.strip().lower()
         exact = [f for f in found if f[0].lower() == wanted]
         starting = [f for f in found if f[0].lower().startswith(wanted)]
         if strict:
            found = exact or starting
         else:
            found = exact or starting or found

      return [(orig, translation) for (headword, orig, translation) in found]


   def _lookup(self, word):
      """Return (word, translation) HTML code pairs for the word (bytes
      in the dictionary encoding)"""

      wanted = word.decode(self.encoding, 'replace')
      results = self._getTranslations(word, wanted)

      if not results and self.stripKeys:
         lowered = word.lower()
         stripped = self._stripWord(lowered)
         if stripped and stripped != lowered:
            debugLog(DEBUG, "Looking up stripped key %s" % stripped)
            results = self._getTranslations(stripped, wanted, strict=True)

      return results


   def _findHeadwords(self, prefix, wanted):
      """Return headwords (bytes) starting with wanted (text) from
      definitions stored under index keys starting with prefix"""

      if not prefix:
         return []

      keys = [k for k in self.definitions if k.lower().startswith(prefix)]
      if len(keys) > self.MAX_STRIPPED_KEYS:
         return []

      wanted = wanted.strip().lower()
      words = []

      for key in keys:
         for source in self.dict.getdef(key):
            headword = self._splitDefinition(source)[0].strip()
            if headword.lower().startswith(wanted):
               headword = headword.encode(self.encoding)
               if not headword in words:
                  words.append(headword)

      return words


   def search(self, word):
      """Lookup word"""

      _start = time.time()

      result = meta.SearchResult()

      if isinstance(word, str):
         word = word.encode(self.encoding)

      word_lowered = word.lower()
      
      if self.definitions is None:
         self.definitions = self.dict.getdeflist()
         self.definitions.sort()

      try:
         words = []

         for definition in self.definitions:
            if definition.lower().startswith(word_lowered):
               words.append(definition)

         if not words and self.stripKeys:
            stripped = self._stripWord(word_lowered)
            if stripped != word_lowered:
               words = self._findHeadwords(stripped,
                                           word.decode(self.encoding,
                                                       'replace'))

         results = self._lookup(word)

         if not results and len(words):
            debugLog(DEBUG, "Retrying search...")
            results = self._lookup(words[0])
      except UnicodeDecodeError as e:
         systemLog(ERROR, "Unable to decode definition in %s: %s" \
                   % (self.encoding, e))
         result.setError(errortype.INVALID_ENCODING)
         return result

      if not results:
         result.setError(errortype.NOT_FOUND)

      html = []

      html.append("<html><head>")
      html.append("<meta http-equiv=\"Content-Type\" " \
                  "content=\"text/html; charset=%s\">" \
                  % str(self.getEncoding()))
      html.append("<head><body>")

      for (orig, translation) in results:
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

      # The word comes encoded in the connection's encoding
      if isinstance(word, bytes):
         word = word.decode(self.getEncoding())

      try:
         conn = dictclient.Connection(self.server, self.port,
                                      self.getEncoding())
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
         
         pron = re.findall(r"\[(.*?)\]", orig) # 1st comment type
         pronPatt = " [%s]"
         
         if len(pron) == 0:
            pron = re.findall(r"\/(.*?)\/", orig) # 2nd comment type
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
