#
# OpenDict
# Copyright (c) 2005 Martynas Jocius <mjoc@akl.lt>
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

# TODO: rename to "dictplugin.py"

"""
New plugin module
"""

import os
import sys
import traceback
import xml.dom.minidom

import info
import meta
from logger import systemLog, debugLog, DEBUG, INFO, WARNING, ERROR


class PluginInfo:
    """Plugin information"""


    def __init__(self, xmlData):
        """Parse XML data and store it into class attributes"""

        self.name = None
        self.version = None
        self.authors = []
        self.module = {}
        self.encoding = None
        self.usesWordList = None
        self.opendictVersion = None
        self.pythonVersion = None
        self.platforms = []
        self.description = None

        self.xmlData = xmlData
        self._parse()

    
    def _parse(self):
        """Parse plugin information XML data"""
        
        doc = xml.dom.minidom.parseString(self.xmlData)

        # Get name
        for nameElement in doc.getElementsByTagName('name'):
            for node in nameElement.childNodes:
                if node.nodeType == node.TEXT_NODE:
                    self.name = node.data

        # Get version
        for versionElement in doc.getElementsByTagName('version'):
            for node in versionElement.childNodes:
                if node.nodeType == node.TEXT_NODE:
                    self.version = node.data

        # Get authors
        for authorElement in doc.getElementsByTagName('author'):
            authorName = authorElement.getAttribute('name')
            authorEMail = authorElement.getAttribute('email')
            self.authors.append({'name': authorName, 'email': authorEMail})

        # Get module
        for moduleElement in doc.getElementsByTagName('module'):
            moduleName = None
            for node in moduleElement.childNodes:
                if node.nodeType == node.TEXT_NODE:
                    moduleName = node.data
            moduleLang = moduleElement.getAttribute('lang')
            self.module = {'name': moduleName, 'lang': moduleLang}

        # Get encoding
        for encodingElement in doc.getElementsByTagName('encoding'):
            for node in encodingElement.childNodes:
                if node.nodeType == node.TEXT_NODE:
                    self.encoding = node.data

        # Get info about word list usage
        for wordListElement in doc.getElementsByTagName('uses-word-list'):
            for node in wordListElement.childNodes:
                if node.nodeType == node.TEXT_NODE:
                    self.usesWordList = node.data.lower() == 'true'

        # Get required OpenDict version
        for odVersionElement in doc.getElementsByTagName('opendict-version'):
            for node in odVersionElement.childNodes:
                if node.nodeType == node.TEXT_NODE:
                    self.opendictVersion = node.data

        # Get required Python version
        for pyVersionElement in doc.getElementsByTagName('python-version'):
            for node in pyVersionElement.childNodes:
                if node.nodeType == node.TEXT_NODE:
                    self.pythonVersion = node.data

        # Get supported platforms
        for platformElement in doc.getElementsByTagName('platform'):
            platformName = platformElement.getAttribute('name')
            self.platforms.append({'name': platformName})
        self.platforms.sort()

        # Get description
        for descElement in doc.getElementsByTagName('description'):
            for node in descElement.childNodes:
                if node.nodeType == node.TEXT_NODE:
                    self.description = node.data



class DictionaryPlugin(meta.Dictionary):
    """Dictionary plugin handler"""

    def __init__(self, path):
        """Prepare plugin and plugin information objects"""

        self.path = path

        try:
            self.info = self._loadInfo(path)
        except Exception, e:
            raise InvalidPluginException, e

        try:
            self.dictionary = self._loadPlugin(path)
        except Exception, e:
            raise InvalidPluginException, e


    def getType(self):
        """Return dictionary type"""

        import dicttype
        return dicttype.PLUGIN


    def getName(self):
        """Return plugin name"""

        return self.info.name


    def getPath(self):
        """Return plugin location"""

        return self.path


    def getVersion(self):
        """Return version"""

        return self.info.version


    def getAuthors(self):
        """Return list of authors"""

        return self.info.authors


    def getModule(self):
        """Return module info"""

        return self.info.module


    def getEncoding(self):
        """Return encoding used by dictionary"""

        return self.info.encoding
    

    def getUsesWordList(self):
        """Return boolean value of word list usage"""

        return self.info.usesWordList


    def getOpendictVersion(self):
        """Return required min OpenDict version"""

        return self.info.opendictVersion


    def getPythonVersion(self):
        """Return required min Python version"""

        return self.info.pythonVersion


    def getPlatforms(self):
        """Return supported platforms"""
        
        return self.info.platforms


    def getDescription(self):
        """Returns description text"""
        
        return self.info.description
        

    def search(self, word):
        """Lookup word"""

        return self.dictionary.search(word)
        

    def _loadInfo(self, path):
        """Load plugin information"""

        try:
            fd = open(os.path.join(path, "plugin.xml"))
            xmlData = fd.read()
            fd.close()

            info = PluginInfo(xmlData)
            return info
        except Exception, e:
            raise InvalidPluginException, \
                  "Unable to load plugin info (%s)" % e
    

    def _loadPlugin(self, path):
        """Load plugin"""

        moduleName = os.path.splitext(self.info.module.get('name'))[0]
        fullPath = os.path.join(path, moduleName)

        sys.path.insert(0, path)
        module =  __import__(moduleName)
        sys.path.remove(path)

        instance = module.init(info.home)

        return instance


    # Usable?
    def isValid(self):
        """Validate plugin. Validates both plugin and plugin info objects"""

        try:
            assert hasattr(self.info, "name")
            assert hasattr(self.info, "version")
            assert hasattr(self.info, "authors")
            assert hasattr(self.info, "module")
            assert hasattr(self.info, "encoding")
            assert hasattr(self.info, "usesWordList")
            assert hasattr(self.info, "opendictVersion")
            assert hasattr(self.info, "pythonVersion")
            assert hasattr(self.info, "platforms")
            assert hasattr(self.info, "description")
            
            assert hasattr(self.dictionary, "search")
            assert callable(self.dictionary.search)
            
            return True
        except:
            return False


def _loadDictionaryPlugin(directory):
    """Load dictionary plugin"""

    plugin = None

    try:
        systemLog(INFO, "Loading %s..." % directory)
        plugin = DictionaryPlugin(directory)
    except InvalidPluginException, e:
        systemLog(ERROR, "Unable to load plugin from %s (%s)" % (directory, e))
        traceback.print_exc

    return plugin


def loadDictionaryPlugins():
    """Load plugins. Returns list of PluginHandler objects"""

    pluginDirs = []
    globalPluginPath = os.path.join(info.GLOBAL_HOME,
                                    info.__DICT_DIR,
                                    info.__PLUGIN_DICT_DIR)
    localPluginPath = os.path.join(info.LOCAL_HOME,
                                   info.__DICT_DIR,
                                   info.__PLUGIN_DICT_DIR)
    
    if os.path.exists(localPluginPath):
        pluginDirs = [os.path.join(localPluginPath, fileName) \
                      for fileName in os.listdir(localPluginPath) \
                      if os.path.isdir(os.path.join(localPluginPath,
                                                    fileName))]

    if os.path.exists(globalPluginPath):
        for fileName in os.listdir(globalPluginPath):
            if os.path.isdir(os.path.join(globalPluginPath, fileName)) \
               and not fileName in pluginDirs:
                pluginDirs.append(fileName)

    plugins = []

    for dirName in pluginDirs:
        plugin = _loadDictionaryPlugin(dirName)
        if plugin:
            plugins.append(plugin)

    return plugins



class InvalidPluginException(Exception):
    """This exception should be raised if plugin has some errors"""
    

if __name__ == "__main__":
    loadPlugins()
    
