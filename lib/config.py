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
import codecs

from info import home, uhome
from misc import numVersion
from plugin import Plugin
import group
import info
import util
import parser


class Configuration:
   """This class is used for reading and writing config file.
   It also takes care of installing new plugins (but shouldn't)"""

   def __init__(self):
      """Initialize default values"""
      
      self.configFile = "opendict.conf"

      # TODO: Should not be here after removing register part from config
      import wxPython.wx
      self.app = wxPython.wx.wxGetApp()
      
      self.saveWinSize = 1
      self.saveWinPos = 0
      self.saveSashPos = 0
      self.useListWithRegs = 1
      self.useListWithGroups = 1

      self.dict = ""
      self.winSize = (600, 450)
      self.winPos = (-1, -1)
      self.sashPos = 160

      self.window = None
      self.plugins = {}
      self.registers = {}
      self.groups = {}
      self.ids = {}

      self.plugMenuIds = 200
      self.regMenuIds = 300
      self.groupMenuIds = 400

      #self.defaultEncoding = "utf-8"
      self.encoding = "UTF-8"
      self.fontFace = "Fixed"
      self.fontSize = 10
      
      self.dictServer = "dict.org"
      self.dictServerPort = "2628"


   # Deprecated
   def readConfigFile(self):
      try:
         fd = open(os.path.join(uhome, self.configFile), "r")
         if info.__unicode__:
             sw = codecs.lookup("utf-8")[3]
             fd = sw(fd)
      except:
         return

      gen = util.UniqueIdGenerator()

      for line in fd.readlines():
         line = line.strip()
         if line.find("REGISTER=") == 0:
            line = line.replace("REGISTER=", "").strip()
            if info.__unicode__:
                line = line.decode("utf-8")
            line = line.split("*")
            # FIXME: Should be handled using XML
            name = line[0]
            path = line[1]
            format = line[2]
            setEnc = line[3]
            dictionary = None
            if format.upper() == "SLOWO":
               dictionary = parser.SlowoParser(path)
            elif format.upper() == "MOVA":
               dictionary = parser.MovaParser(path)
            elif format.upper() == "TMX":
               dictionary = parser.TMXParser(path)
            elif format.upper() in ('DZ', 'DICT'):
               dictionary = parser.DictParser(pat)

            if dictionary:
               print "New register:", dictionary
               dictionary.setEncoding(setEnc)
               self.app.dictionaries[dictionary.getName()] = dictionary
            
            #self.registers[line[0]] = line[1:4]
            self.ids[gen.getID()] = dictionary
            #self.regMenuIds += 1
            
         elif line.find("GROUP=") == 0:
            line = line.replace("GROUP=", "").strip()
            if info.__unicode__:
                line = line.decode("utf-8")
            line = line.split("@@@")
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
            if info.__unicode__:
                self.dict = self.dict.decode("utf-8")
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
            self.encoding = line.replace("ENCODING=", "").strip()
         elif line.find("FONTFACE=") == 0:
            self.fontFace = line.replace("FONTFACE=", "").strip()
         elif line.find("FONTSIZE=") == 0:
            try:
               self.fontSize = int(line.replace("FONTSIZE=", "").strip())
            except:
               pass
         elif line.find("LISTREG=") == 0:
            self.useListWithRegs = int(bool(line.replace("LISTREG=","")))
         elif line.find("LISTGROUP=") == 0:
            self.useListWithGroups = int(bool(line.replace("LISTGROUP=","")))
         elif line.find("SERVER=") == 0:
            self.dictServer = line.replace("SERVER=", "")
         elif line.find("SERVER_PORT="):
            self.dictServerPort = line.replace("SERVER_PORT=", "")

      fd.close()

   def writeConfigFile(self):

      print "Writing new config file..."
      try:
         fd = open(os.path.join(uhome, self.configFile), "w")
         if info.__unicode__:
             sw = codecs.lookup("utf-8")[3]
             fd = sw(fd)
      except:
         print "Error: can't write config file"
         return 1
      
      if self.dict != "None":
         if self.plugins.has_key(self.dict) or \
         self.registers.has_key(self.dict) or \
         self.groups.has_key(self.dict):
            #print "Setting %s as default dict" % self.dict
            fd.write("DICT=%s\r\n" % self.dict)
      fd.write("ENCODING=%s\r\n" % self.encoding)
      fd.write("FONTFACE=%s\r\n" % self.fontFace)
      fd.write("FONTSIZE=%s\r\n" % self.fontSize)
      
      fd.write("SERVER=%s\r\n" % self.dictServer)
      fd.write("SERVER_PORT=%s\r\n" % self.dictServerPort)
      
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

