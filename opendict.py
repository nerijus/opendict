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

from wxPython.wx import *

import sys
import os
import traceback
import string

if sys.platform == "win32":
   # MS Windows user
   sys.path = [os.path.join(os.curdir, "lib")] + sys.path
else:
   # Unix-like system user
   sys.path.insert(0, "/usr/share/opendict/lib")
   sys.path.insert(0, os.curdir+"/lib")

# OpenDict Modules
try:
   from info import home, uhome, __version__
   from gui.mainwin import MainWindow
   from gui.errorwin import ErrorWindow
   from config import Configuration
   from register import Register
   from plugin import initPlugins, installPlugin
   import misc
except:
   try:
      import misc
      misc.printError()
   except:
      print "*** Fatal Error***"
      print "No system-wide installation found and program is not executed in"
      print "its top-level directory"
   sys.exit(1)

class OpenDictApp(wxApp):

   """Top-level class of wxWindows application"""

   l = wxLocale()

   def OnInit(self):

      _ = wxGetTranslation
      
      try:
         # Init gettext support
         wxLocale_AddCatalogLookupPathPrefix(os.path.join(home, "locale"))
         self.l.Init(wxLANGUAGE_DEFAULT)
         self.l.AddCatalog("opendict")
         
         self.config = Configuration()
         self.config.readConfigFile()

         # FIXME: check gui.pluginwin line 123, can't directly import
         # plugin there.
         self.installPlugin = installPlugin

         initPlugins(self.config)
         self.reg = Register()

         self.window = MainWindow(None, -1, "OpenDict",
                                  self.config.winPos,
                                  self.config.winSize,
                                  style=wxDEFAULT_FRAME_STYLE)

         self.config.window = self.window

         self.window.Show(True)

      except:
         print "\n*** Fatal Error ***"

         msg = string.join(traceback.format_exception(
               sys.exc_info()[0], sys.exc_info()[1],
               sys.exc_info()[2]), "")

         msg += "\n[Information]\n" \
                "OpenDict: %s\n" \
                "Python: %s\n" \
                "wxPython: %s\n" \
                "Platform: %s" % (__version__, sys.version,
                                  wx.__version__, sys.platform)

         print msg
         
         try:
            errWin = ErrorWindow(None, -1, _("Error"), msg,
                                 size=(300, 300),
                                 style=wxDEFAULT_FRAME_STYLE)
     
            errWin.Show(true)
         except:
            print "Unable to show window with the message above"
            msg = string.join(traceback.format_exception(
                  sys.exc_info()[0], sys.exc_info()[1],
                  sys.exc_info()[2]), "")
            print msg
            
         return False

      return True


if __name__ == "__main__":
   print "OpenDict %s\n" % __version__
   print "HOME:", home
   print "USER HOME:", uhome

   openDictApp = OpenDictApp(0)
   openDictApp.MainLoop()


