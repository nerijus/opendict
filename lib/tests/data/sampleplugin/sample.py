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
Sample OpenDict plugin (new type)
"""

import string
import sys


def init(libraryPath):
    """This is required method for all plugins. The one and only
    parameter gives OpenDict library path for requred imports. This
    method returns plugin instance."""

    sys.path.insert(0, libraryPath)
    
    return SampleDictionary()


class SampleDictionary:
    """Sample dictionary"""

    def __init__(self):
        """Import and save needed modules"""

        from lib import errortype, meta

        self.errorModule = errortype
        self.metaModule = meta


    def search(self, word):
        """Look up word"""

        trans = []
        words = []

        trans.append("<html><body>")

        for i in range(10):
            trans.append("Do you want to know what <pre>%s</pre> is žžčėčęė? So do I!" \
                         % word)


        for i in range(20):
            words.append("ž"+str(i)*5)

        trans.append("</body></html>")

        result = self.metaModule.SearchResult()
        result.status = self.errorModule.OK
        result.translation = "".join(trans)
        result.words = words

        return result
