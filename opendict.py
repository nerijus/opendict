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

try:
    from wxPython.wx import *
    import wx
    import wxPython
except ImportError:
    print >> sys.stderr, "**"
    print >> sys.stderr, "** Error: wxPython library not found"
    print >> sys.stderr, "** Please install wxPython 2.5 or newer to run OpenDict"
    print >> sys.stderr, "**"
    sys.exit(1)


try:
    import xml.dom.ext
except ImportError:
    print >> sys.stderr, "**"
    print >> sys.stderr, "** Error: Python/XML library not found"
    print >> sys.stderr, "** Please install python-xml to run OpenDict"
    print >> sys.stderr, "**"
    sys.exit(1)

if sys.platform == "win32":
   # MS Windows user
   sys.path = [os.path.join(os.curdir, "lib")] + sys.path
else:
   # Unix-like system
   sys.path.insert(0, "/usr/share/opendict/lib")

# OpenDict Modules
import info
from gui.mainwin import MainWindow
from gui.errorwin import ErrorWindow
from config import Configuration
from register import Register
from plugin import initPlugins, installPlugin
from logger import systemLog, debugLog, DEBUG, INFO, WARNING, ERROR
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
      _start = time.time()

      if wxPython.__version__.split('.') < ['2', '5']:
         from gui import errorwin

         # Go away, wxPython 2.4!
         title = _("wxPython Version Error")
         msg = _("wxPython %s is installed on this system.\n\n" \
                 "OpenDict %s requires wxPython 2.5 to run smoothly. " \
                 "wxPython 2.4\n" \
                 "is not supported anymore because of huge number of " \
                 "bugs.\n\n" \
                 "Please get wxPython 2.5 from " \
                 "http://www.wxpython.org/download.php" \
                 % (wxPython.__version__, info.VERSION))
         errorwin.showErrorMessage(title, msg)
         return False
      
      
      systemLog(DEBUG, "Unicode version: %s" % wx.USE_UNICODE)
      
      # Init gettext support
      wxLocale_AddCatalogLookupPathPrefix(os.path.join(info.GLOBAL_HOME,
                                                       'locale'))
      self.l.Init(wxLANGUAGE_DEFAULT)
      self.l.AddCatalog('opendict')

      # Data cache instance
      self.cache = {}
      
      # Dictionaries container
      # Mapping: name -> object
      self.dictionaries = {}
      
      self.config = Configuration()
      self.config.load()

      self.agreements = util.AgreementsManager(os.path.join(info.LOCAL_HOME,
                                                            'agreements.txt'))
      
      
      # FIXME: check gui.pluginwin line 123, can't directly import
      # plugin there.
      self.installPlugin = installPlugin
      
      
      # Load new-style plugins
      for plugin in newplugin.loadDictionaryPlugins():
         self.dictionaries[plugin.getName()] = plugin
         self.config.ids[wx.NewId()] = plugin.getName()

      for plain in plaindict.loadPlainDictionaries():
         self.dictionaries[plain.getName()] = plain
         self.config.ids[wx.NewId()] = plain.getName()

         
      # TODO: Remove in the future
      self.reg = Register()

      windowPos = (int(self.config.get('windowPosX')),
                                int(self.config.get('windowPosY')))
      windowSize = (int(self.config.get('windowWidth')),
                    int(self.config.get('windowHeight')))

      self.window = MainWindow(None, -1, "OpenDict",
                               windowPos,
                               windowSize,
                               style=wxDEFAULT_FRAME_STYLE)
      
      # FIXME: Avoid this
      self.config.window = self.window

      systemLog(DEBUG, "Loaded in %f seconds" % (time.time() - _start))
      
      self.window.Show(True)

      return True


if __name__ == "__main__":
   
   systemLog(INFO, "OpenDict %s" % info.VERSION)
   systemLog(INFO, "Global home: %s:" % info.GLOBAL_HOME)
   systemLog(INFO, "Local home: %s" % info.LOCAL_HOME)

   openDictApp = OpenDictApp(0)
   openDictApp.MainLoop()

