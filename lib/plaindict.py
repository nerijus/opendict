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



class PlainDictionary(meta.Dictionary):
    """Plain dictionary class"""

    def getConfigDir(self):
       """Return configuration directory path"""

       path = os.path.join(info.LOCAL_HOME,
                           info.PLAIN_DICT_DIR,
                           os.path.basename(self.getPath()))

       return path


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
            raise "This is internal error and should not happen: " \
                  "no parser class found for dictionary in %s" % directory

        # Constant %FULL_PLAIN_PATH% can be used to define dictionary file
        # path. If so, it is replaced with full file path in local or
        # system directory, depending on parameter 'directory' given.

        fileName = os.path.basename(config.get('path').replace('%FULL_PLAIN_PATH%', ''))
        home = info.LOCAL_HOME
        if directory.startswith(info.GLOBAL_HOME):
            home = info.GLOBAL_HOME
        fileName = os.path.basename(fileName)
        fullFileDir = os.path.join(home, info.PLAIN_DICT_DIR,
                                    fileName, info.__PLAIN_DICT_FILE_DIR) + \
                                    os.path.sep

        dictionary = Parser(config.get('path').replace('%FULL_PLAIN_PATH%',
                                                       fullFileDir))
        dictionary.setEncoding(config.get('encoding'))
        dictionary.setName(config.get('name'))
        dictionary.setChecksum(config.get('md5'))

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

    fileName = os.path.basename(dictionary.getPath())

    dictLocalIndex = os.path.join(info.LOCAL_HOME,
                                 info.PLAIN_DICT_DIR,
                                 fileName, 'data', 'index.xml')
    
    dictGlobalIndex = os.path.join(info.LOCAL_HOME,
                                 info.PLAIN_DICT_DIR,
                                 fileName, 'data', 'index.xml')

    index = None

    if os.path.exists(dictLocalIndex):
        index = xmltools.parseIndexFile(dictLocalIndex)
    elif os.path.exists(dictGlobalIndex):
        index = xmltoos.parserIndexFile(dictGlobalIndex)

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
