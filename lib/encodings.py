#
# OpenDict
# Copyright (c) 2005 Martynas Jocius <mjoc at akl.lt>
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
Character encodings
"""

import info

if info.__unicode__:
    toWX = fromWX = lambda s: s
else:
    import locale
    localeCharset = locale.getpreferredencoding()
    print localeCharset
    
    def toWX(s):
        print 'toWX():', type(s)
        return s.encode(localeCharset, 'replace')

    def fromWX(s):
        print 'fromWX():', type(s)
        return unicode(s, localeCharset)


print toWX
print fromWX