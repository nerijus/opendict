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


#from info import home, uhome
import info


def showErrorMessage(title, msg):

   #if msg == "":
   #   msg = traceback.format_exception(sys.exc_info()[0], sys.exc_info()[1], 
   #                                    sys.exc_info()[2])[3]
   #print "MSG:", msg
   window = wxMessageDialog(None,
                            msg, 
                            _(title), 
                            wxOK | wxICON_ERROR)
   window.CenterOnScreen()
   window.ShowModal()
   window.Destroy()
   

class ErrorWindow(wxFrame):

   """This window is shown when OpenDict can't start because
      of some error."""

   def __init__(self, parent, id, title, error, pos=wxDefaultPosition,
                size=wxDefaultSize, style=wxCENTRE):
      wxFrame.__init__(self, parent, id, title, pos, size, style)

      vbox = wxBoxSizer(wxVERTICAL)

      vbox.Add(wxStaticText(self, -1, _("An error occured:")), 0,
               wxALL | wxEXPAND, 5)

      errMsg = wxTextCtrl(self, -1, size=(-1, 200),
                       style=wxTE_MULTILINE | wxTE_READONLY)
      errMsg.WriteText(error)
      vbox.Add(errMsg, 1,
               wxALL | wxEXPAND, 10)

      #msg = _("This may be a configuration error due to lost files and may\n" \
      #      "be fixed by editing %s\n" \
      #      "by hand using text editor and removing corruped entries,\n" \
      #      "or this error may be a bug in the program. If so, please\n" \
      #      "copy this error text and report a bug to developers at\n" \
      #      "http://opendict.not.yet/bugs.html\n" \
      #      "Thank you.") % os.path.join("", "config.txt")

      vbox.Add(wxStaticText(self, -1, msg), 0,
               wxALL | wxEXPAND, 5)

      self.buttonClose = wxButton(self, 200, _("Close"))
      vbox.Add(self.buttonClose, 0, wxALL | wxCENTRE, 2)


      self.SetSizer(vbox)
      self.Fit()

      EVT_CLOSE(self, self.onCloseWindow)
      EVT_BUTTON(self, 200, self.onExit)


   #def onCloseWindow(self, event):
   #   self.Destroy() # ??
   #   sys.exit(1) # FIXME: how to exit without this?
      #wxGetApp().window.Close(True)


   #def onExit(self, event):
   #   self.Close(True)
