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
import shutil
import traceback

from lib.logger import systemLog, debugLog, DEBUG, INFO, WARNING, ERROR
from lib import enc
from lib.gui import errorwin

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



class InvalidDictWindow(wxDialog):

   def __init__(self, parent, id, title, dicts, pos=wxDefaultPosition,
                size=wxDefaultSize, style=wxDEFAULT_DIALOG_STYLE):
      wxDialog.__init__(self, parent, id, title, pos, size, style)

      self.dicts = {}
      self.buttons = {}

      vbox = wx.BoxSizer(wx.VERTICAL)
      vboxButtons = wx.BoxSizer(wx.HORIZONTAL)
      vboxDicts = wx.BoxSizer(wx.VERTICAL)

      grid = wxFlexGridSizer(2, 2, 5, 5)

      msg =  _("You have directories that containt invalid dictionaries " \
               "and cannot be loaded. \nYou can try to remove these " \
               "directories right now.")

      vbox.Add(wx.StaticText(self, -1, msg),
               0, wxALL, 5)

      row = 0
      for d in dicts:
         grid.Add(wxStaticText(self, -1, d),
                  0, wxALIGN_CENTER_VERTICAL)
         rid = wx.NewId()
         self.dicts[rid] = d
         b = wx.Button(self, rid, _("Remove"))
         self.buttons[rid] = b
         grid.Add(b, 1, wxALIGN_CENTER_VERTICAL)
         EVT_BUTTON(self, rid, self.onRemove)
         #print d

      vbox.Add(grid, 0, wxALL, 10)
      vbox.Add(wx.StaticLine(self, -1), 1, wxALL | wxEXPAND, 1)

      self.buttonClose = wxButton(self, wx.ID_CANCEL, _("Close"))
      vboxButtons.Add(self.buttonClose, 0, wxALL, 5)

      vbox.Add(vboxButtons, 0, wxALL | wxALIGN_RIGHT, 5)
      self.SetSizer(vbox)

      self.Fit()


   def onRemove(self, event):

      path = self.dicts[event.GetId()]

      try:
         shutil.rmtree(path)
         self.buttons[event.GetId()].Disable()
      except Exception, e:
         traceback.print_exc()
         title = _("Unable to remove")
         msg = _("Unable to remove directory \"%s\": %s") % (path, e)
         errorwin.showErrorMessage(title, msg)



def showInvalidDicts(parentWin, invalidDicts):
    """Show licence agreement window"""

    dialog = InvalidDictWindow(None, -1,  _("Invalid Dictionaries"),
                               invalidDicts)
    result = dialog.ShowModal()
    dialog.Destroy()
    
