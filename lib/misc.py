# OpenDict
# Copyright (c) 2003 Martynas Jocius <mjoc@delfi.lt>
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
# Module: misc

from wxPython.wx import wxGetTranslation, wxGetApp
import string
import traceback
import sys

_ = wxGetTranslation

errors = {1: _("Not found"),
          2: _("Dictionary error, please report to its author"),
          3: _("Syntax error"),
          4: _("Connection error"),
          5: _("Time out"),
          6: _("Unsupported encoding")}


# There encodings will work only if the system has installed fonts
# for them.
encodings = {"Unicode (UTF-8)": "utf-8",
             "Western (ISO-8859-1)": "iso-8859-1",
             "Central European (ISO-8859-2)": "iso-8859-2",
             "Nordic (ISO-8859-10)": "iso-8859-10",
             "South European (ISO-8859-3)": "iso-8859-3",
             "Greek (ISO-8859-7)": "iso-8859-7",
             "Baltic (ISO-8859-13)": "iso-8859-13",
             "Cyrilic (KOI8-R)": "koi8-r",
             "Arabic (ISO-8859-6)": "iso-8859-6"}

fontFaces = {"Fixed": "fixed",
             "Arial": "Arial",
             "Helvetica": "helvetica",
             "Courier": "courier",
             "Times": "Times",
             "Verdana": "Verdana",
             "Lucida": "Lucida"}

fontSizes = ["1", "2", "3", "4", "6", "8", "10", "12"]

def numVersion(str):
    """Return a float number made from x.y.z[-preV] version number"""

    nver = str.split('-')[0]
    numbers = nver.split('.')
    try:
        return (float(numbers[0]) + float(numbers[1]) * 0.1 + float(number[2]) * 0.01)
    except:
        return 0.0

def printError():
    print string.join(traceback.format_exception(sys.exc_info()[0],
                                                 sys.exc_info()[1],
                                                 sys.exc_info()[2]), "")
                                                 
def savePrefs(frame):
   """Saves window preferences when exiting"""
   
   print "Saving window preferences"
   app = wxGetApp()
   
   if app.config.saveWinSize == 1:
      app.config.winSize = frame.GetSize()
   if app.config.saveWinPos == 1:
      app.config.winPos = frame.GetPosition()
      if app.config.winPos[0] == -1:
         app.config.winPos[0] = 0
   if app.config.saveSashPos == 1:
      app.config.sashPos = frame.splitter.GetSashPosition()

