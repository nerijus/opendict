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
Metaclasses
"""

from lib import errortype


class SearchResult:
    """Search result metaclass"""

    def __init__(self):
        """Set default values"""

        self.error = errortype.OK
        self.translation = ""
        self.words = []


    def setError(self, err):
        """Set error object"""

        self.error = err


    def getError(self):
        """Get error object"""

        return self.error


    def setTranslation(self, trans):
        """Set translation string"""

        self.translation = trans


    def getTranslation(self):
        """Get translation string"""

        return self.translation


    def setWordList(self, words):
        """Set word list"""

        self.words = words


    def getWordList(self):
        """Get word list"""

        return self.words



class Dictionary:
    """Dictionary interface"""

    active = True


    def start(self):
        """Allocate resources"""

        pass


    def stop(self):
        """Free resources"""

        pass
    

    def getType(self):
        """Return dictionary type"""

        return None
    

    def getName(self):
        """Return plugin name"""

        return None


    def getVersion(self):
        """Return version"""

        return None


    def getSize(self):
        """Return size in kylobites"""

        return None


    def getPath(self):
        """Return ditionary path"""

        pass


    def getAuthors(self):
        """Return list of authors"""

        return None


    def setEncoding(self, encoding):
        """Set encoding"""

        pass


    def getEncoding(self):
        """Return encoding used by dictionary"""

        return None
    

    def getUsesWordList(self):
        """Return boolean value of word list usage"""

        return None


    def getDescription(self):
        """Returns description text"""
        
        return None


    def getLicence(self):
        """Return licence text"""

        return None


    def getActive(self):
        return self.active


    def setActive(self, active=True):
        self.active = active
    

    def search(self, word):
        """Lookup word"""

        return None
