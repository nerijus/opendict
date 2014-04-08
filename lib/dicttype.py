#
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

"""
Dictionary types
"""

from lib import newplugin


class DictionaryType:
    """Dictionary type interface"""

    dictClass = None
    fileExtentions = None
    name = None
    shortIdName = None
 

    def getClass(self):
        """Return dictionary class"""

        return self.dictClass
    

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

    dictClass = newplugin.DictionaryPlugin
    fileExtentions = ('zip',)
    name = "OpenDict dictionary plugin"



class TypeSlowo(DictionaryType):
    """Slowo dictionary format"""

    import parser

    dictClass = parser.SlowoParser
    fileExtentions = ('dwa',)
    name = "Slowo dictionary"
    shortIdName = "slowo"



class TypeMova(DictionaryType):
    """Mova dictionary format"""

    import parser

    dictClass = parser.MovaParser
    fileExtentions = ('mova',)
    name = "Mova dictionary"
    shortIdName = "mova"

    

class TypeTMX(DictionaryType):
    """TMX dictionary format"""

    import parser

    dictClass = parser.TMXParser
    fileExtentions = ('tmx',)
    name = "TMX dictionary"
    shortIdName = "tmx"



class TypeDict(DictionaryType):
    """DICT dictionary type"""

    import parser

    dictClass = parser.DictParser
    fileExtentions = ('dict', 'dz',)
    name = "DICT dictionary"
    shortIdName = "dict"



# Constant instances
PLUGIN = TypePlugin()
SLOWO = TypeSlowo()
MOVA = TypeMova()
#TMX = TypeTMX()
DICT = TypeDict()

# Supported types tuple
supportedTypes = (PLUGIN, SLOWO, MOVA, DICT)

# Plain dictionary types (data file)
plainTypes = (SLOWO, MOVA, DICT)

# Types for which index table is made
indexableTypes = (SLOWO, MOVA)
