#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# OpenDict
# Copyright (c) 2003 Martynas Jocius <mjoc@akl.lt>
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

import sys
import os
import traceback
import string
import time

from wxPython.wx import *
import wx

if sys.platform == "win32":
   # MS Windows user
   sys.path = [os.path.join(os.curdir, "lib")] + sys.path
else:
   # Unix-like system
   sys.path.insert(0, "/usr/share/opendict/lib")
   #sys.path.insert(0, os.curdir+"/lib")

# OpenDict Modules
#from info import home, uhome, __version__
import info
from gui.mainwin import MainWindow
from gui.errorwin import ErrorWindow
from config import Configuration
from register import Register
from plugin import initPlugins, installPlugin
import misc
import info
import newplugin
import plaindict
import util


class OpenDictApp(wxApp):
   """Top-level class of wxWindows application"""

   l = wxLocale()

   def OnInit(self):

      _ = wxGetTranslation
      
      print "DEBUG Unicode version:", wx.USE_UNICODE
      
      # Init gettext support
      wxLocale_AddCatalogLookupPathPrefix(os.path.join(info.GLOBAL_HOME,
                                                       "locale"))
      self.l.Init(wxLANGUAGE_DEFAULT)
      self.l.AddCatalog("opendict")
      
      # Dictionaries container
      # Mapping: name -> object
      self.dictionaries = {}
      
      self.config = Configuration()
      self.config.readConfigFile()
      
      
      # FIXME: check gui.pluginwin line 123, can't directly import
      # plugin there.
      self.installPlugin = installPlugin
      
      
      # Load new-style plugins
      for plugin in newplugin.loadDictionaryPlugins():
         self.dictionaries[plugin.getName()] = plugin
         self.config.ids[util.generateUniqueID()] = plugin.getName()

      for plain in plaindict.loadPlainDictionaries():
         self.dictionaries[plain.getName()] = plain
         self.config.ids[util.generateUniqueID()] = plain.getName()
         
         
      # TODO: Remove in the future
      self.reg = Register()
      
      self.window = MainWindow(None, -1, "OpenDict",
                               self.config.winPos,
                               self.config.winSize,
                               style=wxDEFAULT_FRAME_STYLE)
      
      # FIXME: Avoid this
      self.config.window = self.window
      
      self.window.Show(True)

      return True


if __name__ == "__main__":

   if len(sys.argv) == 2 and sys.argv[1] in ("-h", "--help"):
      print "Usage: %s [OPTIONS]" % sys.argv[0]
      print
      print "OPTIONS:"
      print "  -h, --help        show this help"
      #print "  --splash          enable splash screen"
      print "  --home=<DIR>      specify home directory"

      sys.exit(0)
   
   print "INFO OpenDict %s\n" % info.VERSION
   print "INFO Global home:", info.GLOBAL_HOME
   print "INFO Local home:", info.LOCAL_HOME

   openDictApp = OpenDictApp(0)
   openDictApp.MainLoop()

