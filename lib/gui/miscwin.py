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

import wx
import wx.html
import shutil
import traceback

from lib.logger import systemLog, debugLog, DEBUG, INFO, WARNING, ERROR
from lib import enc
from lib.gui import errorwin

_ = wx.GetTranslation


class PluginLicenceWindow(wx.Dialog):

   def __init__(self, parent, id, title, msg, pos=wx.DefaultPosition,
                size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE):
      wx.Dialog.__init__(self, parent, id, title, pos, size, style)

      vbox = wx.BoxSizer(wx.VERTICAL)
      vboxButtons = wx.BoxSizer(wx.HORIZONTAL)

      htmlWin = wx.html.HtmlWindow(self, -1, style=wx.SUNKEN_BORDER)
      htmlWin.SetFonts('Helvetica', 'Fixed', [10]*5)

      error = False
      
      try:
          encodedText = enc.toWX(unicode(msg, 'UTF-8'))
          htmlWin.SetPage(encodedText)
      except Exception, e:
          systemLog(ERROR, "Unable to encode/show licence text: %s" % e)
          htmlWin.SetPage(_("Error: <i>unable to show licence text</i>"))
          error = True

      vbox.Add(htmlWin, 1, wx.ALL | wx.EXPAND, 5)

      if not error:
          self.buttonNo = wx.Button(self, wx.ID_CANCEL, _("Do not accept"))
          vboxButtons.Add(self.buttonNo, 0, wx.ALL, 2)
          
          self.buttonYes = wx.Button(self, wx.ID_OK, _("Accept"))
          vboxButtons.Add(self.buttonYes, 0, wx.ALL, 2)
      else:
          self.buttonNo = wx.Button(self, wx.ID_CANCEL, _("Close"))
          vboxButtons.Add(self.buttonNo, 0, wx.ALL, 2)

      vbox.Add(vboxButtons, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
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



class InvalidDictWindow(wx.Dialog):

   def __init__(self, parent, id, title, dicts, pos=wx.DefaultPosition,
                size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE):
      wx.Dialog.__init__(self, parent, id, title, pos, size, style)

      self.dicts = {}
      self.buttons = {}

      vbox = wx.BoxSizer(wx.VERTICAL)
      vboxButtons = wx.BoxSizer(wx.HORIZONTAL)
      vboxDicts = wx.BoxSizer(wx.VERTICAL)

      grid = wx.FlexGridSizer(2, 2, 5, 5)

      msg =  _("You have directories that containt invalid dictionaries " \
               "and cannot be loaded. \nYou can try to remove these " \
               "directories right now.")

      vbox.Add(wx.StaticText(self, -1, msg),
               0, wx.ALL, 5)

      row = 0
      for d in dicts:
         grid.Add(wx.StaticText(self, -1, d),
                  0, wx.ALIGN_CENTER_VERTICAL)
         rid = wx.NewId()
         self.dicts[rid] = d
         b = wx.Button(self, rid, _("Remove"))
         self.buttons[rid] = b
         grid.Add(b, 1, wx.ALIGN_CENTER_VERTICAL)
         wx.EVT_BUTTON(self, rid, self.onRemove)

      vbox.Add(grid, 0, wx.ALL, 10)
      vbox.Add(wx.StaticLine(self, -1), 1, wx.ALL | wx.EXPAND, 1)

      self.buttonClose = wx.Button(self, wx.ID_CANCEL, _("Close"))
      vboxButtons.Add(self.buttonClose, 0, wx.ALL, 5)

      vbox.Add(vboxButtons, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
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
    
