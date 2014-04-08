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
# Module: threads

from threading import *
import sys
import os
import copy
import traceback
import string

class KThread(Thread):
    """Thread that can be killed during its run()"""

    def join(self, timeout=None):
        """Kill it"""

        Thread.join(self, timeout)
        print "Thread killing himself"
        #os._exit(0)


class Process:

    def __init__(self, func, *param):
        self.__done = 0
        self.__result = None
        self.__status = "working"

        self.__C = Condition()

        # Seperate thread
        self.__T = Thread(target=self.Wrapper, args=(func, param))
        self.__T.setName("ProcessThread")
        self.__T.start()

    def __repr__(self):
        return "<Process at "+hex(id(self))+":"+self.__status+">"

    def __call__(self):
        self.__C.acquire()
        while self.__done == 0:
            self.__C.wait()
        self.__C.release()

        result = copy.copy(self.__result)
        return result

    def isDone(self):
        return self.__done

    def stop(self):
        # FIXME: this actually doesn't kill the running process
        # Needs to be done. Help?
        #Thread.join(self.__T, None)
        self.__T.join(0)

    def Wrapper(self, func, param):
        self.__C.acquire()
        try:
           self.__result = func(*param)
        except:
           self.__result = None
           print string.join(traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1],
           sys.exc_info()[2]), "")
        self.__done = 1
        self.__status = "self.__result"
        self.__C.notify()
        self.__C.release()

