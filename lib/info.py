# OpenDict
# Copyright (c) 2003-2004 Martynas Jocius <mjoc@delfi.lt>
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
# Module: info

import sys
import os

from wxPython.wx import wxGetTranslation
import wxPython.wx
import wx

_ = wxPython.wx.wxGetTranslation

# OpenDict version
__version__ = "0.5.7"

# Unicode support
#if wxPython.wx.__version__[-1] == "u":
#    __unicode__ = True
#else:
#    __unicode__ = False
__unicode__ = wx.USE_UNICODE

# FIXME: bad idea
# Default encoding for non-unicode string conversion to unicode
#__enc__ = "iso-8859-13"

# Home Directory
#if len(sys.argv) >= 2 and sys.argv[1] != "--splash":
home = uhome = None

for arg in sys.argv:
   if arg.startswith("--home="):
      uhome = arg[7:]
      #uhome = home
      
if not home:
   if sys.platform == "win32":
      # MS Windows user
      import _winreg
      x = _winreg.ConnectRegistry(None, _winreg.HKEY_CURRENT_USER)
      try:
         y = _winreg.OpenKey(x, "SOFTWARE\OpenDict\Settings")
         home = _winreg.QueryValueEx(y, "Path")[0]
      except:
         home = "C:\\Program Files\\OpenDict"
      if not os.path.exists(home):
         home = os.curdir
      uhome = home

   else:
      # Unix-like system
      if not uhome:
         if not os.path.exists(os.environ["HOME"]+"/.opendict"):
            os.mkdir(os.environ["HOME"]+"/.opendict")
         uhome = os.environ["HOME"]+"/.opendict"

      # This is system-wide installation
      if os.path.exists("/usr/share/opendict"):
         home = "/usr/share/opendict"
      else:
         home = os.curdir
