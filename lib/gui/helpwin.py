# -*- coding: UTF-8 -*-

# OpenDict
# Copyright (c) 2003-2004 Martynas Jocius <mjoc@akl.lt>
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
# Module: gui.helpwin

from wxPython.wx import *
from wxPython.html import *
import wx
import os
import sys

from info import home, __version__
import enc

_ = wxGetTranslation


class LicenseWindow(wxFrame):
   """Licence window class"""

   def __init__(self, parent, id, title, pos=wxDefaultPosition,
                size=wxDefaultSize, style=wxCENTRE): # centre!
      wxFrame.__init__(self, parent, id, title, pos, size, style)

      vbox = wxBoxSizer(wxVERTICAL)

      # TODO: which is better: html or plain text?
      scWinAbout = wxScrolledWindow(self, -1, wxPyDefaultPosition,
                                    wxSize(-1, -1))
      text = wxTextCtrl(scWinAbout, -1,
                        style=wxTE_MULTILINE | wxTE_READONLY)
      text.write(open(os.path.join(home, "copying.txt")).read())
      scBox = wxBoxSizer(wxVERTICAL)
      scBox.Add(text, 1, wxALL | wxEXPAND, 1)
      scWinAbout.SetSizer(scBox)
      vbox.Add(scWinAbout, 1, wxALL | wxEXPAND, 2)

      self.buttonClose = wxButton(self, 2002, _("Close"))
      vbox.Add(self.buttonClose, 0, wxALL | wxALIGN_RIGHT, 2)

      self.SetSizer(vbox)

      EVT_BUTTON(self, 2002, self.onClose)


   def onClose(self, event):
      """This method is invoked when Close button is clicked"""
      
      self.Destroy()
      

class CreditsWindow(wxDialog):
   """Credits window class"""
   
   def __init__(self, parent, id, title, pos=wxDefaultPosition,
                size=wxDefaultSize):
      wxDialog.__init__(self, parent, id, title, pos, size)
      
      vbox = wxBoxSizer(wxVERTICAL)
      
      nb = wxNotebook(self, -1)
      
      # "Written by" panel
      writePanel = wxPanel(nb, -1)
      vboxWrite = wxBoxSizer(wxVERTICAL)
      writtenString = unicode("Martynas Jocius <mjoc@akl.lt>\n" \
                              "Mantas Kriaučiūnas <mantas@akl.lt>",
                              "UTF-8")
      written = _(enc.toWX(writtenString))
      labelWrite = wxStaticText(writePanel, -1, written)
      vboxWrite.Add(labelWrite, 0, wxALL, 10)
      writePanel.SetSizer(vboxWrite)
      
      nb.AddPage(writePanel, _("Written By"))
      
      # "Translations" panel
      tPanel = wxPanel(nb, -1)
      vboxTP = wxBoxSizer(wxVERTICAL)
      transString = unicode("Irena Baliukonytė " \
                            "<irena.baliukonyte@mif.vu.lt>\n" \
                            "Martynas Jocius <mjoc@akl.lt>",
                            "UTF-8")
      trans = _(enc.toWX(transString))
      labelTP = wxStaticText(tPanel, -1, trans)
      vboxTP.Add(labelTP, 0, wxALL, 10)
      tPanel.SetSizer(vboxTP)
      
      nb.AddPage(tPanel, _("Translated By"))
      vbox.Add(nb, 1, wxALL | wxEXPAND, 3)
      
      buttonClose = wxButton(self, 2005, _("Close"))
      vbox.Add(buttonClose, 0, wxALL | wxALIGN_RIGHT, 5)
      
      self.SetSizer(vbox)
      
      EVT_BUTTON(self, 2005, self.onClose)

      
   def onClose(self, event):
      """This method is invoked when Close button is clicked"""
      
      self.Destroy()
      

class AboutWindow(wxDialog):
   """Information window about OpenDict"""

   def __init__(self, parent, id, title, pos=wxDefaultPosition,
                size=wxDefaultSize, style=wxDEFAULT_DIALOG_STYLE):
      wxDialog.__init__(self, parent, id, title, pos, size, style)

      hboxButtons = wxBoxSizer(wxHORIZONTAL)
      vbox = wxBoxSizer(wxVERTICAL)

      bmp = wxBitmap(os.path.join(home, "pixmaps", "icon-96x96.png"),
                     wxBITMAP_TYPE_PNG)
      vbox.Add(wxStaticBitmap(self, -1, bmp, wxPoint(-1, -1)), 0, wxALL |
      wxCENTRE, 5)

      title = _("OpenDict %s" % __version__)
      copy = "Copyright %s 2003-2005 Martynas Jocius <mjoc@akl.lt>" % \
             unicode("\302\251", "UTF-8")
      desc = _("OpenDict is multiplatform dictionary.")
      page = "http://opendict.sourceforge.net"

      titleLabel = wxStaticText(self, -1, title,
                                style=wx.ALIGN_CENTER)
      titleLabel.SetFont(wx.Font(18, wx.SWISS, wx.BOLD, wx.BOLD))
      vbox.Add(titleLabel, 1, wxALL | wxALIGN_CENTER, 5)

      copyLabel = wxStaticText(self, -1, copy, style=wx.ALIGN_CENTER)
      copyLabel.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))
      vbox.Add(copyLabel, 1, wxALL | wxALIGN_CENTER, 5)

      descLabel = wxStaticText(self, -1, desc, style=wx.ALIGN_CENTER)
      descLabel.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
      vbox.Add(descLabel, 1, wxALL | wxALIGN_CENTER, 5)

      pageLabel = wxStaticText(self, -1, page, style=wx.ALIGN_CENTER)
      pageLabel.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
      vbox.Add(pageLabel, 1, wxALL | wxALIGN_CENTER, 5)

      vbox.Add(wxStaticLine(self, -1), 0, wxALL | wxEXPAND, 5)

      self.buttonCredits = wxButton(self, 2004, _("Credits"))
      hboxButtons.Add(self.buttonCredits, 1, wxALL | wxALIGN_LEFT, 3)
      
      self.buttonOK = wxButton(self, 2003, _("Close"))
      hboxButtons.Add(self.buttonOK, 1, wxALL | wxALIGN_RIGHT, 3)
      
      vbox.Add(hboxButtons, 0, wxALL | wxEXPAND, 5)

      self.SetSizer(vbox)
      vbox.Fit(self)

      EVT_BUTTON(self, 2003, self.onClose)
      EVT_BUTTON(self, 2004, self.onCredits)


   def onClose(self, event):
      self.Destroy()

      
   def onCredits(self, event):
      creditsWindow = CreditsWindow(self, -1, "Credits",
                                         size=(500, 150))
      creditsWindow.CentreOnScreen()
      creditsWindow.Show()
