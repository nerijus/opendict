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

import md5


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
    


def getMD5Sum(filePath):
    """Return MD5 checksum for given file"""


    fd = open(filePath)
    data = fd.read()
    fd.close()

    generator = md5.new(data)

    return generator.hexdigest()

