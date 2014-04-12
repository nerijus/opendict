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
# Module: config.py

import os
import string
import codecs

from lib.logger import systemLog, debugLog, DEBUG, INFO, WARNING, ERROR
from lib.misc import numVersion
from lib import info
from lib import util
from lib import parser
from lib import xmltools


class ActiveDictConfig(object):
    """Config file manager for activated dictionaries. Operates with
    names of dictionaries only."""

    def __init__(self):
      self.filePath = os.path.join(info.LOCAL_HOME, "active.conf")

      # If config file does not exist (this is the first time),
      # set special attribute init=True to notify that
      if not os.path.exists(self.filePath):
          self.init = True
      else:
          self.init = False

      self.dicts = []


    def load(self):
        """Load list of active dictionaries."""

        try:
            for line in open(self.filePath):
                name = line.strip()
                name = unicode(name, 'UTF-8')
                self.dicts.append(name)
        except IOError, e:
            pass


    def save(self):
        """Save list of active dictionaries."""

        fd = open(self.filePath, 'w')
        for d in self.dicts:
            name = d.encode('UTF-8')
            print >> fd, name
        fd.close()


    def enabled(self, name):
        """Return True if this dictionary is enabled."""

        if name in self.dicts:
            return True

        return False


    def add(self, name):
        """Add new dictionary to the list."""

        if type(name) == str:
            name = unicode(name, 'UTF-8')

        if not name in self.dicts:
            self.dicts.append(name)


    def remove(self, name):
        """Remove dictionary from the list."""

        if type(name) == str:
            name = unicode(name, 'UTF-8')

        if name in self.dicts:
            self.dicts.remove(name)



class Configuration:
   """This class is used for reading and writing config file.
   It also takes care of installing new plugins (but shouldn't)"""

   def __init__(self):
      """Initialize default values"""

      self.activedict = ActiveDictConfig()
      self.activedict.load()
      
      self.filePath = os.path.join(info.LOCAL_HOME, "opendict.xml")
      self.props = {}

      # TODO: Should not be here after removing register part from config
      import wx
      self.app = wx.GetApp()

      #
      # Default values
      #
      self.set('saveWindowSize', 'True')
      self.set('saveWindowPos', 'True')
      self.set('saveSashPos', 'True')

      self.set('defaultDict', '')
      self.set('windowWidth', '550')
      self.set('windowHeight', '370')
      self.set('windowPosX', '-1')
      self.set('windowPosY', '-1')
      self.set('sashPos', '160')

      # Internal variables
      self.window = None
      self.ids = {}

      self.plugMenuIds = 200
      self.regMenuIds = 300
      self.groupMenuIds = 400

      self.set('encoding', 'UTF-8')
      self.set('fontFace', 'Fixed')
      self.set('fontSize', '10')
      
      self.set('dictServer', 'dict.org')
      self.set('dictServerPort', '2628')
      self.set('dict-server-encoding', 'UTF-8')

      self.repository = \
               'http://opendict.sf.net/Repository/Data/opendict-add-ons.xml'


   def get(self, name):
      """Return property value"""

      return self.props.get(name)


   def set(self, name, value):
      """Set property"""

      self.props[name] = value



   def load(self):
      """Load configuration from file to memory"""

      try:
         if os.path.exists(self.filePath):
            self.props.update(xmltools.parseMainConfig(self.filePath))
      except Exception, e:
         systemLog(ERROR, "Unable to read configuration file: %s" % e)

      # Old configurations may still keep outdated entry, rewrite it
      self.set('repository-list', self.repository)



   def save(self):
      """Write configuration to disk"""

      doc = xmltools.generateMainConfig(self.props)
      xmltools.writeConfig(doc, os.path.join(info.LOCAL_HOME,
                                             self.filePath))



   def checkDir(self, dir):
      """Check if directory exists. Create one if not"""

      raise DeprecationWarning

      if not os.path.exists(os.path.join(uhome, dir)):
         os.mkdir(os.path.join(uhome, dir))
