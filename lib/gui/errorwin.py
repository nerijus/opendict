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
# Module: gui.errorwin

import wx
import sys
import os
import traceback

_ = wx.GetTranslation


from lib import info


def showErrorMessage(title, msg):
   """Show error message dialog"""
   
   window = wx.MessageDialog(None,
                            msg, 
                            title, 
                            wx.OK | wx.ICON_ERROR)
   window.CenterOnScreen()
   window.ShowModal()
   window.Destroy()


def showInfoMessage(title, msg):
   """Show info message dialog"""
   
   window = wx.MessageDialog(None,
                            msg, 
                            title, 
                            wx.OK | wx.ICON_INFORMATION)
   window.CenterOnScreen()
   window.ShowModal()
   window.Destroy()
   
   

class ErrorWindow(wx.Frame):

   """This window is shown when OpenDict can't start because
      of some error."""

   def __init__(self, parent, id, title, error, pos=wx.DefaultPosition,
                size=wx.DefaultSize, style=wx.CENTRE):
      wx.Frame.__init__(self, parent, id, title, pos, size, style)

      raise "Deprecated"

      vbox = wx.BoxSizer(wx.VERTICAL)

      vbox.Add(wx.StaticText(self, -1, _("An error occured:")), 0,
               wx.ALL | wx.EXPAND, 5)

      errMsg = wx.TextCtrl(self, -1, size=(-1, 200),
                       style=wx.TE_MULTILINE | wx.TE_READONLY)
      errMsg.WriteText(error)
      vbox.Add(errMsg, 1,
               wx.ALL | wx.EXPAND, 10)

      vbox.Add(wx.StaticText(self, -1, msg), 0,
               wx.ALL | wx.EXPAND, 5)

      self.buttonClose = wx.Button(self, 200, _("Close"))
      vbox.Add(self.buttonClose, 0, wx.ALL | wx.CENTRE, 2)


      self.SetSizer(vbox)
      self.Fit()

      wx.EVT_CLOSE(self, self.onCloseWindow)
      wx.EVT_BUTTON(self, 200, self.onExit)
