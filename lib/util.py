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

"""
Utility functions
"""

import os
import md5

import info


class UniqueIdGenerator:
    """Unique ID generator (using singleton design pattern)"""


    class _RealGenerator:
        """Unique ID generator"""

        def __init__(self, start=0):
            """Set starting ID value"""
            
            self.id = start
            
            
        def getID(self):
            """Return unique ID"""
            
            self.id += 1
            return self.id

    
    __instance = None


    def __init__(self, start=0):
        """Create new instance if not exists yet"""

        if UniqueIdGenerator.__instance is None:
            UniqueIdGenerator.__instance = self._RealGenerator(start)


    def getID(self):
        """Return unique ID"""

        return self.__instance.getID()


def generateUniqueID():
    """Helper function for getting unique ID"""

    gen = UniqueIdGenerator(7000)
    return gen.getID()


def getMD5Sum(filePath):
    """Return MD5 checksum for given file"""


    fd = open(filePath)
    data = fd.read()
    fd.close()

    generator = md5.new(data)

    return generator.hexdigest()


def makeDirectories():
    """Make needed directories if not exist"""

    

    plainDir = os.path.join(info.LOCAL_HOME,
                            info.PLAIN_DICT_DIR)
    pluginDir = os.path.join(info.LOCAL_HOME,
                             info.PLUGIN_DICT_DIR)


    if not os.path.exists(info.LOCAL_HOME):
        try:
            print "DEBUG %s does not exist, creating..." % info.LOCAL_HOME
            os.mkdir(info.LOCAL_HOME)
        except Exception, e:
            print "ERROR Unable to create %s (%s)" % (info.LOCAL_HOME, e)

    if not os.path.exists(os.path.join(info.LOCAL_HOME, info.__DICT_DIR)):
        try:
            print "DEBUG %s does not exist, creating..." \
                  % os.path.join(info.LOCAL_HOME, info.__DICT_DIR)
            os.mkdir(os.path.join(info.LOCAL_HOME, info.__DICT_DIR))
        except Exception, e:
            print "ERROR Unable to create %s (%s)" \
                  % (os.path.join(info.LOCAL_HOME, info.__DICT_DIR), e)

    if not os.path.exists(plainDir):
        try:
            print "DEBUG %s does not exist, creating..." % plainDir
            os.mkdir(plainDir)
        except Exception, e:
            print "ERROR Unable to create %s (%s)" % (plainDir, e)

    
    if not os.path.exists(pluginDir):
        try:
            print "DEBUG %s does not exist, creating..." % pluginDir
            os.mkdir(pluginDir)
        except Exception, e:
            print "ERROR Unable to create %s (%s)" % (pluginDir, e)


if __name__ == "__main__":
    makeDirectories()
    
