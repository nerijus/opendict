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
# Module: config.py

import os
import string

from info import home, uhome
from misc import numVersion
from plugin import Plugin
import group

class Configuration:

   """This class is used for reading and writing config file.
   It also takes care of installing new plugins (but shouldn't)"""

   def __init__(self):
      self.saveWinSize = 1
      self.saveWinPos = 1
      self.saveSashPos = 0
      self.useListWithRegs = 1
      self.useListWithGroups = 1

      self.dict = ""
      self.winSize = (400, 300)
      self.winPos = (-1, -1)
      self.sashPos = 120

      self.window = None
      self.plugins = {}
      self.registers = {}
      self.groups = {}
      self.ids = {}

      self.plugMenuIds = 200
      self.regMenuIds = 300
      self.groupMenuIds = 400

      self.defaultEnc = "utf-8"
      self.encoding = self.defaultEnc
      self.fontFace = "Fixed"
      self.fontSize = "2"

   def readConfigFile(self):
      try:
         fd = open(os.path.join(uhome, "config.txt"), "r")
      except:
         return

      for line in fd.readlines():
         if line.find("REGISTER=") == 0:
            line = line.replace("REGISTER=", "").strip().split("*")
            self.registers[line[0]] = line[1:4]
            self.ids[line[0]] = self.regMenuIds
            self.regMenuIds += 1
         elif line.find("GROUP=") == 0:
            line = line.replace("GROUP=", "").strip().split("@@@")
            name = line[0]

            try:
               dicts = line[1].split("*")
            except:
               dicts = []

            self.groups[name] = dicts
            self.ids[name] = self.groupMenuIds
            self.groupMenuIds += 1
         elif line.find("DICT=") == 0:
            self.dict = line.replace("DICT=", "").strip()
         elif line.find("WINSIZE=") == 0:
            self.winSize = line.replace("WINSIZE=", "").split()
            self.winSize[0] = int(self.winSize[0].strip())
            self.winSize[1] = int(self.winSize[1].strip())
            self.saveWinSize = 1
         elif line.find("WINPOS=") == 0:
            self.winPos = line.replace("WINPOS=", "").split()
            self.winPos[0] = int(self.winPos[0].strip())
            self.winPos[1] = int(self.winPos[1].strip())
            self.saveWinPos = 1
         elif line.find("SASHPOS=") == 0:
            self.sashPos = int(line.replace("SASHPOS=", ""))
            self.saveSashPos = 1
         elif line.find("ENCODING=") == 0:
            self.defaultEnc = line.replace("ENCODING=", "").strip()
         elif line.find("FONTFACE=") == 0:
            self.fontFace = line.replace("FONTFACE=", "").strip()
         elif line.find("FONTSIZE=") == 0:
            self.fontSize = line.replace("FONTSIZE=", "").strip()
         elif line.find("LISTREG=") == 0:
            self.useListWithRegs = int(line.replace("LISTREG=", ""))
         elif line.find("LISTGROUP=") == 0:
            self.useListWithGroups = int(line.replace("LISTGROUP=", ""))

      fd.close()

   def writeConfigFile(self):

      print "Writing new config file..."
      try:
         fd = open(os.path.join(uhome, "config.txt"), "w")
      except:
         print "Error: can't write config file"
         return 1
      
      if self.dict != "None":
         if self.plugins.has_key(self.dict) or \
         self.registers.has_key(self.dict) or \
         self.groups.has_key(self.dict):
            print "Setting %s as default dict" % self.dict
            fd.write("DICT=%s\r\n" % self.dict)
      fd.write("ENCODING=%s\r\n" % self.defaultEnc)
      fd.write("FONTFACE=%s\r\n" % self.fontFace)
      fd.write("FONTSIZE=%s\r\n" % self.fontSize)
      if self.saveWinSize == 1:
         fd.write("WINSIZE=%s %s\r\n" % (self.winSize[0], self.winSize[1]))
      if self.saveWinPos == 1:
         fd.write("WINPOS=%s %s\r\n" % (self.winPos[0], self.winPos[1]))
      if self.saveSashPos == 1:
         fd.write("SASHPOS=%s\r\n" % self.sashPos)
      fd.write("LISTREG=%s\r\n" % self.useListWithRegs)
      fd.write("LISTGROUP=%s\r\n" % self.useListWithGroups)
      for d in self.registers.keys():
         fd.write("REGISTER=%s*%s*%s*%s\r\n" % (d, self.registers[d][0],
                                              self.registers[d][1],
                                              self.registers[d][2]))
      for name, dicts in self.groups.items():
         fd.write("GROUP=%s@@@" % name)

         l = []
         for item in group.filesToNames(dicts, self):
            print "Item:", item
            if item in self.registers.keys():
               l.append(item)
            elif item in self.plugins.keys():
               item = self.plugins[item].dir
               l.append(item)

         fd.write("%s\r\n" % string.join(l, "*"))

      fd.close()
      
      return 0

   def checkDir(self, dir):
      """Check if directory exists. Create one if not"""

      if not os.path.exists(os.path.join(uhome, dir)):
         os.mkdir(os.path.join(uhome, dir))


   # Temporary function, will be removed
   def p(self):

      print "Config File Contents:"
      print " Load dictionary:", self.dict
      print " Window Size:", self.winSize, "(save=%s)" % self.saveWinSize
      print " Window Position:", self.winPos, "(save=%s)" % self.saveWinPos
      print " Sash Position:", self.sashPos, "(save=%s)" % self.saveSashPos
