#
# OpenDict
# Copyright (c) 2003-2005 Martynas Jocius <mjoc@akl.lt>
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

"""
Module for plain dictionaries
"""

import os
import traceback

import info
import meta
import util
import xmltools
from logger import systemLog, debugLog, DEBUG, INFO, WARNING, ERROR


class PlainDictInfo:
    """Plain dictionary configuration"""

    def __init__(self, directory):
        """Store configuration data"""

        self.config = xmltools.parsePlainDictConfig(\
                os.path.join(directory,
                             info.__PLAIN_DICT_CONFIG_DIR,
                             'config.xml'))

        self.directory = directory

        self.name = config.get('name')
        self.formatString = config.get('format')
        self.path = config.get('path')
        self.checksum = config.get('md5')
        self.encoding = config.get('encoding')


    def getFormatString(self):
        """Return format name"""

        return self.formatString


    def getName(self):
        """Return name"""

        return self.name


    def getPath(self):
        """Return full file path"""

        return self.path


    def getChecksum(self):
        """Return checksum"""

        return self.checksum


    def getEncoding(self):
        """Return encoding"""

        return self.encoding


    def getLicence(self):
        """Return licence text"""

        filePath = self.licence

        if filePath:
            if not os.path.exists(filePath):
                filePath = os.path.join(self.directory,
                                        info._PLAIN_DICT_DATA_DIR,
                                        self.licence)
                if not os.path.exists(filePath):
                    filePath = None

            errMsg = "Error: <i>licence file not found</i>"

            if not filePath:
                systemLog(ERROR, "Cannot find defined licence file for %s: %" \
                          % (self.getName(), e))
                return errMsg

            try:
                fd = open(filePath)
                data = fd.read()
                fd.close()
                return data
            except Exception, e:
                systemLog(ERROR, "Unable to read licence file for %s: %" \
                          % (self.getName(), e))
                return errMsg

        return None



class PlainDictionary(meta.Dictionary):
    """Plain dictionary class"""

    licenceFile = None
    

    def getConfigDir(self):
        """Return configuration directory path"""
        
        if os.path.exists(os.path.join(info.LOCAL_HOME,
                                       info.PLAIN_DICT_DIR,
                                       os.path.basename(self.getPath()))):
            path = os.path.join(info.LOCAL_HOME,
                                info.PLAIN_DICT_DIR,
                                os.path.basename(self.getPath()))
        else:
            path = os.path.join(info.GLOBAL_HOME,
                                info.PLAIN_DICT_DIR,
                                os.path.basename(self.getPath()))
            
        return path
    
    
    def setLicenceFile(self, licenceFile):
        """Set licence file path"""
        
        self.licenceFile = licenceFile
        
        
    def getLicence(self):
        """Return licence text"""
        
        filePath = self.licenceFile

        if filePath:
            if not os.path.exists(filePath):
                filePath = os.path.join(self.getConfigDir(),
                                        info._PLAIN_DICT_DATA_DIR,
                                        self.licenceFile)

                if not os.path.exists(filePath):
                    filePath = None

            errMsg = "Error: <i>licence file not found</i>"

            if not filePath:
                systemLog(ERROR,
                          "Cannot find defined licence file '%s' for '%s'" \
                          % (self.licenceFile, self.getName()))
                return errMsg

            try:
                fd = open(filePath)
                data = fd.read()
                fd.close()
                return data
            except Exception, e:
                systemLog(ERROR, "Unable to read licence file for %s: %" \
                          % (self.getName(), e))
                return errMsg

        return None


def _loadPlainDictionary(directory):
    """Load one dictionary and returns dictionary object"""

    import dicttype
    dictionary = None

    try:
        config = xmltools.parsePlainDictConfig(\
                os.path.join(directory,
                             info.__PLAIN_DICT_CONFIG_DIR,
                             'config.xml'))

        for t in dicttype.supportedTypes:
            if t.getIdName() == config.get('format'):
                Parser = t.getClass()

        if not Parser:
            raise Exception, "This is internal error and should not happen: " \
                  "no parser class found for dictionary in %s" % directory

        filePath = config.get('path')
        fileName = os.path.basename(filePath)
        home = info.LOCAL_HOME
        if directory.startswith(info.GLOBAL_HOME):
            home = info.GLOBAL_HOME

        if not os.path.exists(filePath):
            newPath = os.path.join(home, info.PLAIN_DICT_DIR,
                                   fileName, info.__PLAIN_DICT_FILE_DIR,
                                   fileName)
            if os.path.exists(newPath):
                filePath = newPath
            else:
                filePath = None

            
        if not filePath:
            raise Exception, "Dictionary file not found: %s" % fileName

        dictionary = Parser(filePath)
        dictionary.setEncoding(config.get('encoding'))
        dictionary.setName(config.get('name'))
        dictionary.setChecksum(config.get('md5'))
        dictionary.setLicenceFile(config.get('licence'))

    except Exception, e:
        traceback.print_exc()

    return dictionary


def loadPlainDictionaries():
    """Load dictionaries and return a list of dictionary objects"""


    dirs = []
    globalDictDir = os.path.join(info.GLOBAL_HOME,
                                 info.PLAIN_DICT_DIR)
    localDictDir = os.path.join(info.LOCAL_HOME,
                                info.PLAIN_DICT_DIR)


    if os.path.exists(globalDictDir):
        for directory in os.listdir(globalDictDir):
            if os.path.isdir(os.path.join(globalDictDir, directory)):
                dirs.append(os.path.join(globalDictDir, directory))

    if os.path.exists(localDictDir):
        for directory in os.listdir(localDictDir):
            if os.path.isdir(os.path.join(localDictDir, directory)):
                dirs.append(os.path.join(localDictDir, directory))


    dictionaries = []

    for directory in dirs:
        dictionary = _loadPlainDictionary(directory)
        if dictionary:
            dictionaries.append(dictionary)
        
    return dictionaries



def indexShouldBeMade(dictionary):
    """Check if index exists and is up to date.

    Return True if dictionary must be indexed.
    """

    filePath = dictionary.getPath()
    fileName = os.path.basename(filePath)

    dictLocalHome = os.path.join(info.LOCAL_HOME,
                                 info.PLAIN_DICT_DIR,
                                 fileName)

    dictGlobalHome = os.path.join(info.GLOBAL_HOME,
                                  info.PLAIN_DICT_DIR,
                                  fileName)

    if not os.path.exists(os.path.join(dictGlobalHome, 'data', 'index.xml')) \
           and not os.path.exists(os.path.join(dictLocalHome, 'data',
                                               'index.xml')):
        return True

    debugLog(INFO, "Old checksum: %s" % dictionary.getChecksum())
    newChecksum = util.getMD5Sum(filePath)
    debugLog(INFO, "New checksum: %s" % newChecksum)

    return dictionary.getChecksum() != newChecksum



def makeIndex(dictionary, currentlySetEncoding):
    """Index dictionary"""

    filePath = dictionary.getPath()
    fd = open(filePath)

    index = {}
    count = 0L
    
    for line in fd:
        try:
            literal = unicode(line[:2].lower(), dictionary.getEncoding())
        except:
            try:
                literal = unicode(line[:2].lower(), currentlySetEncoding)
                dictionary.setEncoding(currentlySetEncoding)
            except:
                raise Exception, "Unable to encode data in %s nor %s" \
                    % (dictionary.getEncoding(), currentlySetEncoding)
                    
        if not literal in index.keys():
            index[literal] = count

        count += len(line)


    fileName = os.path.basename(filePath)

    dictHome = os.path.join(info.LOCAL_HOME,
                            info.PLAIN_DICT_DIR,
                            fileName)


    toUnicode = lambda s: unicode(s, dictionary.getEncoding())

    doc = xmltools.generateIndexFile(index)
    xmltools.writeIndexFile(doc, os.path.join(dictHome, 'data', 'index.xml'))

    savePlainConfiguration(dictionary)



def loadIndex(dictionary):
    """Load index table"""

    dictIndex = os.path.join(dictionary.getConfigDir(),
                                 'data', 'index.xml')

    index = None

    if os.path.exists(dictIndex):
        index = xmltools.parseIndexFile(dictIndex)
    if not index:
        raise Exception, "Index for %s does not exist" % dictionary.getName()

    return index
     

def savePlainConfiguration(dictionary):
    """Write configuration to disk"""

    import dicttype

    if not dictionary.getType() in dicttype.plainTypes:
       systemLog(ERROR, "Request to write configuration to %s of type %s" \
           % (dictionary.getName(), dictionary.getType()))
       return

    md5sum = util.getMD5Sum(dictionary.getPath())
    dictDir = dictionary.getConfigDir()

    doc = xmltools.generatePlainDictConfig(name=dictionary.getName(),
                                           format=dictionary.getType().getIdName(),
                                           path=dictionary.getPath(),
                                           md5=md5sum,
                                           encoding=dictionary.getEncoding())

    xmltools.writePlainDictConfig(doc, os.path.join(dictDir,
                                                    'conf',
                                                    'config.xml'))
