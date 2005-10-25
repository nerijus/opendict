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
import imp
import traceback
import string
import time

# main_is_frozen() returns True when running the exe, and False when
# running from a script.
def main_is_frozen():
    return (hasattr(sys, "frozen") or # new py2exe
	    hasattr(sys, "importers") # old py2exe
	    or imp.is_frozen("__main__")) # tools/freeze

# If application is not frozen to binary, try selecting wxPython 2.6 or 2.5
# on multiversioned wxPython installation.
if not main_is_frozen():
    try:
        import wxversion
        wxversion.select(["2.5", "2.6-unicode"])
    except Exception, e:
        print "You seem to have wxPython 2.4: %s" \
              % e

try:
    import wx
    import wxPython
except ImportError:
    print >> sys.stderr, "**"
    print >> sys.stderr, "** Error: wxPython library not found"
    print >> sys.stderr, "** Please install wxPython 2.5 or later to run OpenDict"
    print >> sys.stderr, "**"
    sys.exit(1)


try:
    import xml.dom.ext
except ImportError:
    print >> sys.stderr, "**"
    print >> sys.stderr, "** Error: Python/XML library not found"
    print >> sys.stderr, "** Please install python-xml (PyXML) to run OpenDict"
    print >> sys.stderr, "**"
    sys.exit(1)

# get_main_dir() returns the directory name of the script or the
# directory name of the exe
def get_main_dir():
    if main_is_frozen():
	return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.realpath(__file__))
    # or return os.path.dirname(sys.argv[0])

#
# Initial path
#
sys.path.insert(0, get_main_dir())

# OpenDict Modules
from lib import info
from lib.gui.mainwin import MainWindow
from lib.gui.errorwin import ErrorWindow
from lib.config import Configuration
from lib.logger import systemLog, debugLog, DEBUG, INFO, WARNING, ERROR
from lib import misc
from lib import info
from lib import newplugin
from lib import plaindict
from lib import util


class OpenDictApp(wx.App):
   """Top-level class of wxWindows application"""

   locale = wx.Locale()

   def OnInit(self):

      _ = wx.GetTranslation
      _start = time.time()

      wxVersion = []
      try:
          wxVersion = wx.__version__
      except Exception, e:
          try:
              wxVersion = wxPython.__version__
          except:
              pass

      if wxVersion.split('.') < ['2', '5']:
          from lib.gui import errorwin
          
          # Go away, wxPython 2.4!
          title = _("wxPython Version Error")
          msg = _("wxPython %s is installed on this system.\n\n" \
                 "OpenDict %s requires wxPython 2.5 to run smoothly. " \
                  "wxPython 2.4\n" \
                  "is not supported anymore because of huge number of " \
                  "bugs.\n\n" \
                  "Please get wxPython 2.5 from " \
                  "http://www.wxpython.org/download.php" \
                  % (wxVersion, info.VERSION))
          errorwin.showErrorMessage(title, msg)
          return False

      
      util.makeDirectories()
      
      systemLog(DEBUG, "Unicode version: %s" % wx.USE_UNICODE)
      
      # Init gettext support
      wx.Locale_AddCatalogLookupPathPrefix(os.path.join(info.GLOBAL_HOME,
                                                       'po'))
      self.locale.Init(wx.LANGUAGE_DEFAULT)
      self.locale.AddCatalog('opendict')

      # Data cache instance
      self.cache = {}
      
      # Dictionaries container
      # Mapping: name -> object
      self.dictionaries = {}

      # Failed dictionaries.
      # For error message that may be shown after creating main window
      self.invalidDictionaries = []
      
      self.config = Configuration()
      self.config.load()

      self.agreements = util.AgreementsManager(os.path.join(info.LOCAL_HOME,
                                                            'agreements.txt'))
      
      
      
      # Set unique ids
      for plugin in newplugin.loadDictionaryPlugins(self.dictionaries,
                                                    self.invalidDictionaries):
         self.config.ids[wx.NewId()] = plugin.getName()

      for plain in plaindict.loadPlainDictionaries(self.dictionaries):
         self.config.ids[wx.NewId()] = plain.getName()


      windowPos = (int(self.config.get('windowPosX')),
                                int(self.config.get('windowPosY')))
      windowSize = (int(self.config.get('windowWidth')),
                    int(self.config.get('windowHeight')))

      self.window = MainWindow(None, -1, "OpenDict",
                               windowPos,
                               windowSize,
                               style=wx.DEFAULT_FRAME_STYLE)
      
      try:
          systemLog(INFO, "OpenDict %s" % info.VERSION)
          systemLog(INFO, "wxPython %s" % wxVersion)
          systemLog(INFO, "Global home: %s:" % info.GLOBAL_HOME)
          systemLog(INFO, "Local home: %s" % info.LOCAL_HOME)
          systemLog(DEBUG, "Loaded in %f seconds" % (time.time() - _start))
      except Exception, e:
          print "Logger Error: Unable to write to log (%s)" % e
      
      self.window.Show(True)

      return True


if __name__ == "__main__":
   
   openDictApp = OpenDictApp(0)
   openDictApp.MainLoop()
