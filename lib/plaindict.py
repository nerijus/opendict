#
# OpenDict
# Copyright (c) 2003-2005 Martynas Jocius <mjoc@akl.lt>
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
Module for plain dictionaries
"""

import os
import traceback

import info
import xmltools
import dicttype


def loadPlainDictionaries():
    """Load dictionaries and return tuple of dictionary objects"""


    dirs = []
    globalDictDir = os.path.join(info.GLOBAL_HOME,
                                 info.PLAIN_DICT_DIR)
    localDictDir = os.path.join(info.LOCAL_HOME,
                                info.PLAIN_DICT_DIR)


    if os.path.exists(globalDictDir):
        for directory in os.listdir(globalDictDir):
            if os.path.isdir(os.path.join(globalDictDir, directory)):
                dirs.append(os.path.join(globalDictDir, directory))

    if os.path.exists(localDictDir):
        for directory in os.listdir(localDictDir):
            if os.path.isdir(os.path.join(localDictDir, directory)):
                dirs.append(os.path.join(localDictDir, directory))


    dictionaries = []

    for directory in dirs:
        try:
            config = xmltools.parsePlainDictConfig(\
                os.path.join(directory,
                             info.__PLAIN_DICT_CONFIG_DIR,
                             'config.xml'))

            Parser = None

            for t in dicttype.supportedTypes:
                if t.getIdName() == config.get('format'):
                    Parser = t.getClass()

            if not Parser:
                raise "This is internal error and should not happen: " \
                      "no parser class found for dictionary in %s" % directory

            dictionary = Parser(config.get('path'))
            dictionaries.append(dictionary)
            
        except Exception, e:
            traceback.print_exc()

    return dictionaries


if __name__ == "__main__":
    print loadPlainDictionaries()
