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

from wxPython.wx import *
from wxPython.html import *
import wx

from lib.logger import systemLog, debugLog, DEBUG, INFO, WARNING, ERROR
from lib import enc

_ = wxGetTranslation


class PluginLicenceWindow(wxDialog):

   def __init__(self, parent, id, title, msg, pos=wxDefaultPosition,
                size=wxDefaultSize, style=wxDEFAULT_DIALOG_STYLE):
      wxDialog.__init__(self, parent, id, title, pos, size, style)

      vbox = wxBoxSizer(wxVERTICAL)
      vboxButtons = wxBoxSizer(wxHORIZONTAL)

      htmlWin = wxHtmlWindow(self, -1, style=wxSUNKEN_BORDER)
      htmlWin.SetFonts('Helvetica', 'Fixed', [10]*5)

      error = False
      
      try:
          encodedText = enc.toWX(unicode(msg, 'UTF-8'))
          htmlWin.SetPage(encodedText)
      except Exception, e:
          systemLog(ERROR, "Unable to encode/show licence text: %s" % e)
          htmlWin.SetPage(_("Error: <i>unable to show licence text</i>"))
          error = True

      vbox.Add(htmlWin, 1, wxALL | wxEXPAND, 5)

      if not error:
          self.buttonNo = wxButton(self, wx.ID_CANCEL, _("Do not accept"))
          vboxButtons.Add(self.buttonNo, 0, wxALL, 2)
          
          self.buttonYes = wxButton(self, wx.ID_OK, _("Accept"))
          vboxButtons.Add(self.buttonYes, 0, wxALL, 2)
      else:
          self.buttonNo = wxButton(self, wx.ID_CANCEL, _("Close"))
          vboxButtons.Add(self.buttonNo, 0, wxALL, 2)

      vbox.Add(vboxButtons, 0, wxALL | wxALIGN_RIGHT, 5)
      self.SetSizer(vbox)



def showLicenceAgreement(parentWindow, licenceText):
    """Show licence agreement window"""

    dialog = PluginLicenceWindow(parentWindow, -1, _("Licence Agreement"),
                                 licenceText, size=(600, 400))
    result = dialog.ShowModal()
    dialog.Destroy()
    
    if result == wx.ID_OK:
        return True

    return False

