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
Metaclasses
"""

import errortype


class SearchResult:
    """Search result metaclass"""

    def __init__(self):
        """Set default values"""

        self.status = errortype.OK
        self.translation = ""
        self.words = []


class Dictionary:
    """Dictionary interface"""

    def getType(self):
        """Return dictionary type"""

        return None
    

    def getName(self):
        """Return plugin name"""

        return None


    def getVersion(self):
        """Return version"""

        return None


    def getAuthors(self):
        """Return list of authors"""

        return None


    def getEncoding(self):
        """Return encoding used by dictionary"""

        return None
    

    def getUsesWordList(self):
        """Return boolean value of word list usage"""

        return None


    def getDescription(self):
        """Returns description text"""
        
        return None
    

    def search(self, word):
        """Lookup word"""

        return None
