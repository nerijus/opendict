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
# Module: group

from wxPython.wx import wxGetApp, wxGetTranslation
import os

from info import home, uhome
from parser import SlowoParser
from parser import MovaParser
from parser import TMXParser
from parser import DictParser
from misc import errors

_ = wxGetTranslation

class DictionaryGroup:

   def __init__(self, dicts, window):

      #self.window = window # may be unused there, elsewhere?
      self.dicts = {}
      self.app = wxGetApp()
      self.needsList = self.app.config.useListWithGroups

      for di in dicts:
         print "   Item: %s" % di,

         if di in self.app.config.registers.keys():
            print "[register]"
            item = self.app.config.registers[di]
            print "Item: '%s' '%s'" % (item[0], item[1])
            if item[1] == "Slowo":
               print "loaded slowo"
               d = SlowoParser(item[0], window)
               if os.path.exists(os.path.join(uhome, "register", di+".hash")):
                  d.hash = self.app.reg.loadHashTable(os.path.join(uhome, "register", di+".hash"))
               else:
                  d.hash = self.app.reg.loadHashTable(os.path.join(home, "register", di+".hash"))
               #d.hash = self.app.reg.loadHashTable(os.path.join(home, "register", di+".hash"))
               self.dicts[di] = d
            elif item[1] == "Mova":
               print "loaded mova"
               d = MovaParser(item[0], window)
               if os.path.exists(os.path.join(uhome, "register", di+".hash")):
                  d.hash = self.app.reg.loadHashTable(os.path.join(uhome, "register", di+".hash"))
               else:
                  d.hash = self.app.reg.loadHashTable(os.path.join(home, "register", di+".hash"))
               #d.hash = self.app.reg.loadHashTable(os.path.join(home, "register", di+".hash"))
               self.dicts[di] = d
            elif item[1] == "TMX":
               d = TMXParser(item[0], window)
               self.dicts[di] = d
            elif item[1] == "Dict":
               os.chdir(os.path.split(item[0])[0])
               d = DictParser(di, window)
               self.dicts[di] = d

         else:
            print "[plugin]"
            for p in self.app.config.plugins.values():
               if p.dir == di:
                  self.dicts[p.name] = p.load(window)

   def add(self, name, object):

      print "Adding %s to the group" % name
      self.dicts[name] = object

   def search(self, word):

      errno = 0
      print "Group: searching for '%s'" % word

      # FIXME: too old html. wx.html hrrr?

      result = "<html><head>" \
               "<meta http-equiv=\"Content-Type\" "\
               "content=\"text/html; charset=%s\">" \
               "</head><body>" \
               "<font face=\"%s\" size=\"%s\">" % (self.app.window.encoding,
                                                   self.app.config.fontFace,
                                                   self.app.config.fontSize)


      found = 0
      wordlist = []

      for name, dict in self.dicts.items():
         lres = list(dict.search(word))
         wordlist.extend(lres[1])

         # Define an encoding for this dictionary
         #if name in self.app.config.registers:
         #   encoding = self.app.config.registers[name][2]
         #else:
         #   encoding = self.app.window.encoding
         #
         #print "%s --> %s" % (name, encoding)
         encoding = self.app.window.encoding

         # Windows' py2exe doesn't support codecs, but it seems to display character
         # correct without decoding.
         if os.name == "posix":
            try:
               if encoding != "":
                  result += "<table><tr><td bgcolor=\"#cccccc\">" \
                            "<b>%s</b></td></tr></table>" % unicode(name,
                                                                    encoding,
                                                                    "replace")
            except:
               print "Failed to encodode '%s'... to %s, iso-8859-1 used" \
                     % (name[:10], encoding)
               result += "<table><tr><td bgcolor=\"#cccccc\">" \
                        "<b>%s</b></td></tr></table>" % unicode(name,
                                                                "iso-8859-1",
                                                                "replace")

            if type(lres[0]) != type(u''):
               try:
                  lres[0] = unicode(lres[0], encoding, "replace")
               except:
                  print "Failed to encodode '%s'... to %s, iso-8859-1 used" \
                         % (lres[0][:10], encoding)
                  lres[0] = unicode(lres[0], "iso-8859-1", "replace")

         else:
            result += "<table><tr><td bgcolor=\"#cccccc\">" \
                      "<b>%s</b></td></tr></table>" % name
         
         

         if not lres[2]:
             result += "%s<p>" % lres[0]
             found = 1
         else:
             error = errors[lres[2]]
             result += "<font color=\"#a00808\">%s</font><p>" % \
             _(error)

      result += "</font></body></html>"

      try:
         u = {}
         for x in wordlist:
            u[x] = 1
      except:
         pass
      else:
         wordlist = u.keys()
         wordlist.sort()

      if not found:
         errno = 1

      return (result, wordlist, errno)

def filesToNames(files, config):

    l = []

    for d in files:
        if d in config.registers.keys():
            # register
            l.append(d)

        else:
            # plugin
            for p in config.plugins.values():
                if p.dir == d:
                    l.append(p.name)

    return l


def namesToFiles(names, config):

    l = []

    for n in names:
        if n in config.registers.keys():
            l.append(n)
        else:
            for p in config.plugins.values():
                if p.name == n:
                    l.append(p.dir)

    return l

def namesToGroup(names, config):

   l = []

   for n in names:
      if n in config.registers.keys():
         l.append([n, config.registers[n][1]])
      else:
         for p in config.plugins.values():
            if p.name == n:
               l.append([p.dir, ""])

   return l
