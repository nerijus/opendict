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

"""
Dictionary types
"""

class DictionaryType:
    """Dictionary type interface"""

    fileExtentions = None
    name = None
    shortIdName = None

    def getFileExtentions(self):
        """Return file extention"""

        return self.fileExtentions


    def getName(self):
        """Return type name"""

        return self.name


    def getIdName(self):
        """Return short ID name"""

        return self.shortIdName


class TypePlugin(DictionaryType):
    """Dictionary plugin"""

    fileExtentions = ('zip',)
    name = "OpenDict dictionary plugin"

##     def getFileExtentions(self):
##         """Return file extention"""

##         return self.fileExtentions


##     def getName(self):
##         """Return type name"""

##         return self.name



class TypeSlowo(DictionaryType):
    """Slowo dictionary format"""

    fileExtentions = ('dwa',)
    name = "Slowo dictionary"
    shortIdName = "slowo"

##     def getFileExtentions(self):
##         """Return file extention"""

##         return self.fileExtentions


##     def getName(self):
##         """Return type name"""

##         return self.name



class TypeMova(DictionaryType):
    """Mova dictionary format"""

    fileExtentions = ('mova',)
    name = "Mova dictionary"
    shortIdName = "mova"

##     def getFileExtentions(self):
##         """Return file extention"""

##         return self.fileExtentions


##     def getName(self):
##         """Return type name"""

##         return self.name
    

class TypeTMX(DictionaryType):
    """TMX dictionary format"""

    fileExtentions = ('tmx',)
    name = "TMX dictionary"
    shortIdName = "tmx"

##     def getFileExtentions(self):
##         """Return file extention"""

##         return self.fileExtentions

    
##     def getName(self):
##         """Return type name"""

##         return self.name
    


class TypeDict(DictionaryType):
    """DICT dictionary type"""

    fileExtentions = ('dict', 'dz',)
    name = "DICT dictionary"
    shortIdName = "dict"

##     def getFileExtentions(self):
##         """Return file extention"""

##         return self.fileExtentions


##     def getName(self):
##         """Return type name"""

##         return self.name


# Constant instances
PLUGIN = TypePlugin()
SLOWO = TypeSlowo()
MOVA = TypeMova()
TMX = TypeTMX()
DICT = TypeDict()

# Supported types tuple
supportedTypes = (PLUGIN, SLOWO, MOVA, TMX, DICT)
