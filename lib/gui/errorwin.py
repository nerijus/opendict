# OpenDict
# Copyright (c) 2003 Martynas Jocius <mjoc@akl.lt>
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

from wxPython.wx import *
import sys
import os
import traceback

_ = wxGetTranslation


from lib import info


def showErrorMessage(title, msg):
   """Show error message dialog"""
   
   window = wxMessageDialog(None,
                            msg, 
                            title, 
                            wxOK | wxICON_ERROR)
   window.CenterOnScreen()
   window.ShowModal()
   window.Destroy()


def showInfoMessage(title, msg):
   """Show info message dialog"""
   
   window = wxMessageDialog(None,
                            msg, 
                            title, 
                            wxOK | wxICON_INFORMATION)
   window.CenterOnScreen()
   window.ShowModal()
   window.Destroy()
   
   

class ErrorWindow(wxFrame):

   """This window is shown when OpenDict can't start because
      of some error."""

   def __init__(self, parent, id, title, error, pos=wxDefaultPosition,
                size=wxDefaultSize, style=wxCENTRE):
      wxFrame.__init__(self, parent, id, title, pos, size, style)

      raise "Deprecated"

      vbox = wxBoxSizer(wxVERTICAL)

      vbox.Add(wxStaticText(self, -1, _("An error occured:")), 0,
               wxALL | wxEXPAND, 5)

      errMsg = wxTextCtrl(self, -1, size=(-1, 200),
                       style=wxTE_MULTILINE | wxTE_READONLY)
      errMsg.WriteText(error)
      vbox.Add(errMsg, 1,
               wxALL | wxEXPAND, 10)

      vbox.Add(wxStaticText(self, -1, msg), 0,
               wxALL | wxEXPAND, 5)

      self.buttonClose = wxButton(self, 200, _("Close"))
      vbox.Add(self.buttonClose, 0, wxALL | wxCENTRE, 2)


      self.SetSizer(vbox)
      self.Fit()

      EVT_CLOSE(self, self.onCloseWindow)
      EVT_BUTTON(self, 200, self.onExit)
