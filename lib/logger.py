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

import os
import time

from lib import info


INFO = 0
WARNING = 1
ERROR = 2
DEBUG = 3

_logDir = os.path.join(info.LOCAL_HOME, info.LOG_DIR)

_systemLogFile = os.path.join(_logDir, 'system.log')
_debugLogFile = os.path.join(_logDir, 'debug.log')


# Enable or disable logging
logging = False


def systemLog(messageType, message):
    """Write message system log"""

    if not logging:
        return

    dateStr = time.strftime("%Y-%m-%d %H:%M:%S")

    typeStr = 'ERROR'
    if messageType == INFO:
        typeStr = 'INFO'
    elif messageType == WARNING:
        typeStr = 'WARNING'
    elif messageType == DEBUG:
        typeStr = 'DEBUG'

    try:
        fd = open(_systemLogFile, 'a+')
        print >> fd, dateStr, typeStr, message
        fd.close()
    except Exception, e:
        print "LOGGER ERROR: Unable to write message '%s'" % repr(message)


def debugLog(messageType, message):
    """Write message system log"""

    if not logging:
        return

    dateStr = time.strftime("%Y-%m-%d %H:%M:%S")

    typeStr = 'ERROR'
    if messageType == INFO:
        typeStr = 'INFO'
    elif messageType == WARNING:
        typeStr = 'WARNING'
    elif messageType == DEBUG:
        typeStr = 'DEBUG'

    print dateStr, typeStr, message
    
