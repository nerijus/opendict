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
Error types
"""

import wx
_ = wx.GetTranslation

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

    shortMessage = _("Success")
    longMessage = _("Search successfully finished.")



class ErrorNotFound(ErrorType):
    """Not found error class"""

    shortMessage = _("Not found")
    longMessage = _("Word or phrase not found. Try less letters or " \
                  "fewer words.")



class ErrorInternal(ErrorType):
    """Internal error class"""

    shortMessage = _("Internal error")
    longMessage = _("Internal error occured. Please send bug report to " \
                  "the dictionary's of current use authors. Thank you.")



class ErrorNotConnected(ErrorType):
    """Not connected error class"""

    shortMessage = _("Not connected")
    longMessage = _("This dictionary uses Internet connection " \
                  "to translate words. Please connect to the Internet and " \
                  "try again.")



class ErrorConnectionTimeout(ErrorType):
    """Not connected error class"""

    shortMessage = _("Connection Error")
    longMessage = _("Could not connect to host. " \
                  "Check your Internet connection or try later.")



class ErrorInvalidEncoding(ErrorType):
    """Invalid encoding error class"""

    shortMessage = _("Invalid encoding")
    longMessage = _("Selected encoding is not correct for " \
                  "this dictionary. Please select another from Edit > " \
                  "Character Encoding menu")



class ErrorOpenDict(ErrorType):
    """OpenDict bug class"""

    shortMessage = _("OpenDict Bug")
    longMessage = _("Internal error occured. Please send bug report to " \
                  "OpenDict authors to prevent this error in the future. " \
                  "Thank you!")


class ErrorCustom(ErrorType):
    """Custom error"""

    shortMessage = _("Unknown Error")
    longMessage = _("Unknown error occured.")

    def setMessage(self, msg):
        """Set custom message"""

        self.shortMessage = msg


    def setLongMessage(self, msg):
        """Set custom descriptive message"""

        self.longMessage = msg


# Error constant instances
OK = ErrorOk()
NOT_FOUND = ErrorNotFound()
INTERNAL_ERROR = ErrorInternal()
NOT_CONNECTED = ErrorNotConnected()
CONNECTION_ERROR = ErrorConnectionTimeout()
CONNECTION_TIMEOUT = CONNECTION_ERROR
INVALID_ENCODING = ErrorInvalidEncoding()
OPENDICT_BUG = ErrorOpenDict()
CUSTOM_ERROR = ErrorCustom()
