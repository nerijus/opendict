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
import util
import xmltools
import dicttype


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

    

def _loadPlainDictionary(directory):
    """Load one dictionary and returns dictionary object"""

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

        dictionary = Parser(config.get('path'))
        dictionary.setEncoding(config.get('encoding'))
        dictionary.setChecksum(config.get('md5'), True)
        
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

    print "File name:", fileName

    dictLocalHome = os.path.join(info.LOCAL_HOME,
                                 info.PLAIN_DICT_DIR,
                                 fileName)

    dictGlobalHome = os.path.join(info.GLOBAL_HOME,
                                  info.PLAIN_DICT_DIR,
                                  fileName)

    print dictLocalHome
    print dictGlobalHome

    if not os.path.exists(os.path.join(dictGlobalHome, 'data', 'index.xml')) \
           and not os.path.exists(os.path.join(dictLocalHome, 'data', 'index.xml')):
        return True

    print "Old checksum:", dictionary.getChecksum()
    newChecksum = util.getMD5Sum(filePath)
    print "New checksum:", newChecksum

    return dictionary.getChecksum() != newChecksum



def makeIndex(dictionary):
    """Index dictionary"""

    filePath = dictionary.getPath()
    fd = open(filePath)

    index = {}
    count = 0L
    
    for line in fd:
        #print "%s -- %d" % (repr(line), len(line))
        literal = unicode(line[:2].lower(), dictionary.getEncoding())
        #count += len(line)

        #if len(start) == 0:
        #    continue

        if not literal in index.keys():
            index[literal] = count

        #print "%d += %d" % (count, len(line)-2)
        count += len(line)


    fileName = os.path.basename(filePath)

    dictHome = os.path.join(info.LOCAL_HOME,
                            info.PLAIN_DICT_DIR,
                            fileName)


    toUnicode = lambda s: unicode(s, dictionary.getEncoding())

    #try:
    #    map(toUnicode, index)

    doc = xmltools.generateIndexFile(index)
    xmltools.writeIndexFile(doc, os.path.join(dictHome, 'data', 'index.xml'))

    #fd = open(os.path.join(dictHome, 'data', 'index.xml'), 'w')
    #fd.write(xmlData)
    #doc.write(fd)
    #fd.close()
    #fd.close()
    
    #print index
    
    #keys = index.keys()
    #keys.sort()
    #for k in keys:
    #    print "'%s' -> %d" % (k, index[k])
    

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
        

if __name__ == "__main__":
    #print loadPlainDictionaries()
    class D:
        def getPath(self):
            return "/home/mjoc/test.mova"
        
    print makeIndex(D())
