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
import os

from info import home, __version__

_ = wxGetTranslation

class ManualWindow(wxFrame):

   def __init__(self, parent, id, title, pos=wxDefaultPosition,
                size=wxDefaultSize, style=wxCENTRE): # centre!
      wxFrame.__init__(self, parent, id, title, pos, size, style)

      vbox = wxBoxSizer(wxVERTICAL)

      self.htmlWin = wxHtmlWindow(self, -1)
      self.htmlWin.LoadPage(os.path.join(home, "doc", "Manual.html"))
      vbox.Add(self.htmlWin, 1, wxALL | wxEXPAND, 3)

      self.buttonClose = wxButton(self, 2001, _("Close"))
      vbox.Add(self.buttonClose, 0, wxALL | wxCENTRE, 2)

      self.SetSizer(vbox)

      EVT_BUTTON(self, 2001, self.onClose)

   def onClose(self, event):
      self.Destroy()


class LicenseWindow(wxFrame):

   def __init__(self, parent, id, title, pos=wxDefaultPosition,
                size=wxDefaultSize, style=wxCENTRE): # centre!
      wxFrame.__init__(self, parent, id, title, pos, size, style)

      vbox = wxBoxSizer(wxVERTICAL)

      #self.htmlWin = wxHtmlWindow(self, -1)
      #self.htmlWin.LoadPage(os.path.join(home, "copying.txt"))
      #vbox.Add(self.htmlWin, 1, wxALL | wxEXPAND, 3)

      # FIXME: which is better: html or plain text?
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
      vbox.Add(self.buttonClose, 0, wxALL | wxCENTRE, 2)

      self.SetSizer(vbox)

      EVT_BUTTON(self, 2002, self.onClose)

   def onClose(self, event):
      self.Destroy()

class CreditsWindow(wxDialog):
   
   def __init__(self, parent, id, title, pos=wxDefaultPosition,
                size=wxDefaultSize):
      wxDialog.__init__(self, parent, id, title, pos, size)
      
      vbox = wxBoxSizer(wxVERTICAL)
      
      nb = wxNotebook(self, -1)
      
      # "Written by" panel
      writePanel = wxPanel(nb, -1)
      vboxWrite = wxBoxSizer(wxVERTICAL)
      written = _("Martynas Jocius <mjoc@akl.lt>\n" \
                "Mantas Kriauciunas <mantas@akl.lt>")
      labelWrite = wxStaticText(writePanel, -1, written)
      vboxWrite.Add(labelWrite, 0, wxALL, 10)
      writePanel.SetSizer(vboxWrite)
      
      nb.AddPage(writePanel, _("Written By"))
      
      # "Translations" panel
      tPanel = wxPanel(nb, -1)
      vboxTP = wxBoxSizer(wxVERTICAL)
      trans = _("Lithuanian:\n" \
                "   Irena Baliukonyte <irena.baliukonyte@mif.vu.lt>\n" \
                "   Martynas Jocius <mjoc@akl.lt>")
      labelTP = wxStaticText(tPanel, -1, trans)
      vboxTP.Add(labelTP, 0, wxALL, 10)
      tPanel.SetSizer(vboxTP)
      
      nb.AddPage(tPanel, _("Translated By"))
      
      # "Graphics" panel
      gPanel = wxPanel(nb, -1)
      vboxGP = wxBoxSizer(wxVERTICAL)
      graphics = _("Gediminas Cekanauskas <hmm@mail.lt>")
      labelGP = wxStaticText(gPanel, -1, graphics)
      vboxGP.Add(labelGP, 0, wxALL, 10)
      gPanel.SetSizer(vboxGP)
      
      nb.AddPage(gPanel, _("Logo & Icon"))

      # "Funder" panel
      fundPanel = wxPanel(nb, -1)
      vboxFund = wxBoxSizer(wxVERTICAL)
      funder = _("Vilnius City Municipal Government, " \
                 "the Republic of Lithuania")
      labelFund = wxStaticText(fundPanel, -1, funder)
      vboxFund.Add(labelFund, 0, wxALL, 10)
      fundPanel.SetSizer(vboxFund)
      
#   Advertisement period has expired, will be removed 
#   nb.AddPage(fundPanel, _("Sponsor"))
      
      vbox.Add(nb, 1, wxALL | wxEXPAND, 3)
      
      buttonClose = wxButton(self, 2005, _("Close"))
      vbox.Add(buttonClose, 0, wxALL | wxALIGN_RIGHT, 5)
      
      self.SetSizer(vbox)
      
      EVT_BUTTON(self, 2005, self.onClose)
      
   def onClose(self, event):
      self.Destroy()

class AboutWindow(wxDialog):

   """Information window about OpenDict"""

   def __init__(self, parent, id, title, pos=wxDefaultPosition,
                size=wxDefaultSize, style=wxDEFAULT_DIALOG_STYLE):
      wxDialog.__init__(self, parent, id, title, pos, size, style)

      hboxButtons = wxBoxSizer(wxHORIZONTAL)
      vbox = wxBoxSizer(wxVERTICAL)

      bmp = wxBitmap(os.path.join(home, "pixmaps", "logo.xpm"), wxBITMAP_TYPE_XPM)
      vbox.Add(wxStaticBitmap(self, -1, bmp, wxPoint(-1, -1)), 0, wxALL |
      wxCENTRE, 5)

      about = _("""OpenDict %s
Copyright (c) 2003-2005 Martynas Jocius <mjoc@akl.lt>

Multiplatform free dictionary program.

Home page: http://opendict.sourceforge.net""") % __version__

      vbox.Add(wxStaticText(self, -1, about), 1,
               wxALL, 5)

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
