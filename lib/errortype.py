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
Error types
"""

class ErrorType:
    """Error type interface"""

    shortMessage = None
    longMessage = None

    def getShortMessage(self):
        """Return short message"""

        return self.shortMessage


    def getLongMessage(self):
        """Return long message"""

        return self.longMessage


    def getMessage(self):
        """Alternative for getShortMessage()"""

        return self.getShortMessage()
    


class ErrorOk(ErrorType):
    """No error class"""

    shortMessage = u"Success"
    longMessage = u"Search successfully finished."



class ErrorNotFound(ErrorType):
    """Not found error class"""

    shortMessage = u"Not found"
    longMessage = u"Word or phrase not found. Try less letters or " \
                  "fewer words."



class ErrorInternal(ErrorType):
    """Internal error class"""

    shortMessage = u"Internal error"
    longMessage = u"Internal error occured. This may be the " \
                  "bug of the dictionary you use at the moment, or this can " \
                  "be a bug of OpenDict itself. Please send bug report to " \
                  "OpenDict and dictionary of current use authors. Thank you."



class ErrorNotConnected(ErrorType):
    """Not connected error class"""

    shortMessage = u"Not connected"
    longMessage = u"This dictionary uses Internet connection " \
                  "to translate words. Please connect to the Internet and " \
                  "try again."



class ErrorConnectionTimeout(ErrorType):
    """Not connected error class"""

    shortMessage = u"Connection timeout"
    longMessage = u"Timed out while waiting for requested " \
                  "translation. Check if your Internet connection is alive."



class ErrorInvalidEncoding(ErrorType):
    """Invalid encoding error class"""

    shortMessage = u"Invalid encoding"
    longMessage = u"Selected encoding is not correct for " \
                  "this dictionary. Please select another from Edit -> " \
                  "Character Encoding menu"



class ErrorOpenDict(ErrorType):
    """OpenDict bug class"""

    shortMessage = u"OpenDict Bug"
    longMessage = u"Internal error occured. Please send bug report to " \
                  "OpenDict authors to prevent this error in the future. " \
                  "Thank you!"


# Error constant instances
OK = ErrorOk()
NOT_FOUND = ErrorNotFound()
INTERNAL_ERROR = ErrorInternal()
NOT_CONNECTED = ErrorNotConnected()
CONNECTION_TIMEOUT = ErrorConnectionTimeout()
INVALID_ENCODING = ErrorInvalidEncoding()
OPENDICT_BUG = ErrorOpenDict()
