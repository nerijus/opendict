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
# Module: register.py

from wxPython.wx import *
import os

from info import home, uhome

_ = wxGetTranslation

class Register:

    """Class is used for making and loading hash table file
    of registered dictionaries, and registering of new files"""

    def __init__(self):
      self.app = wxGetApp()
      self.config = self.app.config

    def recognizeDictType(self, path):
      fd = open(path)
      line = fd.readline()
      fd.close()

      if line.find("  ") > -1 and line.find("=") == -1:
         return "mova"
      elif line.find("=") > -1:
         return "slowo"
      elif line.find("XML") > -1:
         return "tmx"
      else:
         return ""

    def loadHashTable(self, path):
      hash = {}

      hashFile = open(path)

      for line in hashFile.readlines():
         line = line.strip()
         hash[line.split(" ")[0]] = int(line.split(" ")[1])

      hashFile.close()
      return hash

    def makeHashTable(self, path, file):

      fdDict = open(path)
      self.config.checkDir("register")
      fdHash = open(os.path.join(uhome, "register", file+".hash"), "w")

      print "Indexing..."

      hash = {}

      line = fdDict.readline()
      l = line[0:2].lower().strip()
      n = 0

      hash[l] = n
      n += len(line)

      for line in fdDict.readlines():
         l = line[0:2].lower().strip()
         if not hash.has_key(l):
            hash[l] = n
         n += len(line)

      for l, p in hash.items():
         fdHash.write("%s %s\n" % (l, p))

      fdDict.close()
      fdHash.close()

    #
    # Method used by Installer class for file registering.
    # Returns registered dictionary name if success, None otherwise
    #
    def registerDictionary(self, path, format, name, encoding="utf-8"):
        file = os.path.split(path)[1]

        # Using file without prefix for name
        if format == "dz" or format == "dict":
            if file.find(".dz"):
                file = file.replace(".dict.dz", "")
            else:
                file = file.replace(".dict", "")

        if not self.config.registers.has_key(file):
            print "Registers has no %s, added" % file
            self.config.registers[file] = [path, format, encoding]
            self.config.ids[file] = self.config.regMenuIds
            self.config.regMenuIds += 1

            item = wxMenuItem(self.config.window.menuDict,
                              self.config.ids[file],
                              file)
            EVT_MENU(self.config.window, self.app.config.ids[file], 
                     self.config.window.onDefault)
            
            self.config.window.menuDict.InsertItem(self.config.window.menuDict.GetMenuItemCount()-2, item)
            print "%s menu id: %d" % (file, self.config.ids[file])
            
            if format != "dz":
                self.makeHashTable(path, file)
            
            self.config.window.lastInstalledDictName = file
            
            status = 0

        else:
            print "Registers has %s, skipped" % file
            status = 1
        #self.config.registers[file] = [path, format]

        return status
        
