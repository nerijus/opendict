# -*- coding: UTF-8 -*-

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
# Module: gui.helpwin

#from wx import *
#from wx.html import *
import wx
import os
import sys

from lib.logger import systemLog, debugLog, DEBUG, INFO, WARNING, ERROR
from lib import enc
from lib import info

_ = wx.GetTranslation


class LicenseWindow(wx.Frame):
   """Licence window class"""

   def __init__(self, parent, id, title, pos=wx.DefaultPosition,
                size=wx.DefaultSize, style=wx.CENTRE):
      wx.Frame.__init__(self, parent, id, title, pos, size, style)

      vbox = wx.BoxSizer(wx.VERTICAL)

      #
      # Read licence file
      #
      try:
         fd = open(os.path.join(info.GLOBAL_HOME, 'copying.html'))
         data = fd.read()
         fd.close()
      except Exception, e:
         systemLog(ERROR, "Unable to read licence file: %s" % e)
         data = "Error: <i>licence file not found</i>"

      scWinAbout = wx.ScrolledWindow(self, -1, wx.DefaultPosition,
                                    wx.Size(-1, -1))

      htmlWin = wx.html.HtmlWindow(scWinAbout, -1, style=wx.SUNKEN_BORDER)
      htmlWin.SetFonts('Helvetica', 'Fixed', [10]*5)
      htmlWin.SetPage(data)
      
      scBox = wx.BoxSizer(wx.VERTICAL)
      scBox.Add(htmlWin, 1, wx.ALL | wx.EXPAND, 1)
      scWinAbout.SetSizer(scBox)
      vbox.Add(scWinAbout, 1, wx.ALL | wx.EXPAND, 5)

      self.buttonClose = wx.Button(self, 2002, _("Close"))
      vbox.Add(self.buttonClose, 0, wx.ALL | wx.ALIGN_RIGHT, 5)

      self.SetSizer(vbox)

      wx.EVT_BUTTON(self, 2002, self.onClose)


   def onClose(self, event):
      """This method is invoked when Close button is clicked"""
      
      self.Destroy()
      

class CreditsWindow(wx.Dialog):
   """Credits window class"""
   
   def __init__(self, parent, id, title, pos=wx.DefaultPosition,
                size=wx.DefaultSize):
      wx.Dialog.__init__(self, parent, id, title, pos, size)
      
      vbox = wx.BoxSizer(wx.VERTICAL)
      
      nb = wx.Notebook(self, -1)
      
      # "Written by" panel
      writePanel = wx.Panel(nb, -1)
      vboxWrite = wx.BoxSizer(wx.VERTICAL)
      writtenString = unicode("Martynas Jocius <martynas.jocius@idiles.com>\n"
                              "Nerijus Baliūnas <nerijusb@dtiltas.lt>\n"
                              "Mantas Kriaučiūnas <mantas@akl.lt>",
                              "UTF-8")
      written = enc.toWX(writtenString)
      labelWrite = wx.StaticText(writePanel, -1, written)
      vboxWrite.Add(labelWrite, 0, wx.ALL, 10)
      writePanel.SetSizer(vboxWrite)
      
      nb.AddPage(writePanel, _("Written By"))
      
      # "Translations" panel
      tPanel = wx.Panel(nb, -1)
      vboxTP = wx.BoxSizer(wx.VERTICAL)
      transString = unicode("Martynas Jocius <martynas.jocius@idiles.com>",
                            "UTF-8")
      trans = enc.toWX(transString)
      labelTP = wx.StaticText(tPanel, -1, trans)
      vboxTP.Add(labelTP, 0, wx.ALL, 10)
      tPanel.SetSizer(vboxTP)
      
      nb.AddPage(tPanel, _("Translated By"))

      # "Thanks" panel
      thPanel = wx.Panel(nb, -1)
      vboxThP = wx.BoxSizer(wx.VERTICAL)
      thanksString = _("Ports:\n\n") + u"Debian/Ubuntu:\n    Kęstutis Biliūnas <kebil@kaunas.init.lt>\n\nMacOS X:\n    Linas Valiukas <shirshegsm@gmail.com>"
      thanks = enc.toWX(thanksString)
      labelThP = wx.StaticText(thPanel, -1, thanks)
      vboxThP.Add(labelThP, 0, wx.ALL, 10)
      thPanel.SetSizer(vboxThP)
      nb.AddPage(thPanel, _("Thanks To"))


      # "Sponsor" panel
      sponsorPanel = wx.Panel(nb, -1)
      vboxSP = wx.BoxSizer(wx.VERTICAL)
      sponsorString = _("OpenDict project is sponsored by IDILES.\n"
        "Visit company's website at http://www.idiles.com.\n\n"
        "Report problems by email address support@idiles.com.")
      sponsor = enc.toWX(sponsorString)
      labelSP = wx.StaticText(sponsorPanel, -1, sponsor)
      vboxSP.Add(labelSP, 0, wx.ALL, 10)
      sponsorPanel.SetSizer(vboxSP)
      nb.AddPage(sponsorPanel, _("Sponsors"))
      
      vbox.Add(nb, 1, wx.ALL | wx.EXPAND, 3)
      
      buttonClose = wx.Button(self, 2005, _("Close"))
      vbox.Add(buttonClose, 0, wx.ALL | wx.ALIGN_RIGHT, 5)
      
      self.SetSizer(vbox)
      
      wx.EVT_BUTTON(self, 2005, self.onClose)

      
   def onClose(self, event):
      """This method is invoked when Close button is clicked"""
      
      self.Destroy()
      

class AboutWindow(wx.Dialog):
   """Information window about OpenDict"""

   def __init__(self, parent, id, title, pos=wx.DefaultPosition,
                size=wx.DefaultSize, style=wx.DEFAULT_DIALOG_STYLE):
      wx.Dialog.__init__(self, parent, id, title, pos, size, style)

      hboxButtons = wx.BoxSizer(wx.HORIZONTAL)
      vbox = wx.BoxSizer(wx.VERTICAL)

      bmp = wx.Bitmap(os.path.join(info.GLOBAL_HOME,
                                  "pixmaps", "icon-96x96.png"),
                     wx.BITMAP_TYPE_PNG)
      vbox.Add(wx.StaticBitmap(self, -1, bmp, wx.Point(-1, -1)), 0, wx.ALL |
      wx.CENTRE, 5)

      title = "OpenDict %s" % info.VERSION
      copy = "Copyright %(c)s 2003-2006 Martynas Jocius <martynas.jocius@idiles.com>\n" \
            "Copyright %(c)s 2007 IDILES SYSTEMS, UAB <support@idiles.com>" \
             % {'c': unicode("\302\251", "UTF-8")}
      desc = _("OpenDict is a multiplatform dictionary.")
      page = "http://opendict.idiles.com"

      titleLabel = wx.StaticText(self, -1, title,
                                style=wx.ALIGN_CENTER)
      titleLabel.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
      vbox.Add(titleLabel, 1, wx.ALL | wx.ALIGN_CENTER, 5)

      copyLabel = wx.StaticText(self, -1, copy, style=wx.ALIGN_CENTER)
      copyLabel.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD))
      vbox.Add(copyLabel, 1, wx.ALL | wx.ALIGN_CENTER, 5)

      descLabel = wx.StaticText(self, -1,
        _("OpenDict is a multiplatform dictionary."), style=wx.ALIGN_CENTER)
      descLabel.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
      vbox.Add(descLabel, 1, wx.ALL | wx.ALIGN_CENTER, 5)

      pageLabel = wx.StaticText(self, -1, page, style=wx.ALIGN_CENTER)
      pageLabel.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.NORMAL))
      vbox.Add(pageLabel, 1, wx.ALL | wx.ALIGN_CENTER, 5)

      vbox.Add(wx.StaticLine(self, -1), 0, wx.ALL | wx.EXPAND, 5)

      self.buttonCredits = wx.Button(self, 2004, _("Credits"))
      hboxButtons.Add(self.buttonCredits, 0, wx.ALL | wx.ALIGN_LEFT, 3)
      
      self.buttonLicence = wx.Button(self, 2006, _("Licence"))
      hboxButtons.Add(self.buttonLicence, 0, wx.ALL | wx.ALIGN_LEFT, 3)
      
      self.buttonOK = wx.Button(self, 2003, _("Close"))
      hboxButtons.Add(self.buttonOK, 0, wx.ALL | wx.ALIGN_RIGHT, 3)
      
      vbox.Add(hboxButtons, 0, wx.ALL | wx.ALIGN_CENTER, 5)

      self.SetSizer(vbox)
      vbox.Fit(self)

      wx.EVT_BUTTON(self, 2003, self.onClose)
      wx.EVT_BUTTON(self, 2004, self.onCredits)
      wx.EVT_BUTTON(self, 2006, self.onLicence)


   def onClose(self, event):
      self.Destroy()

      
   def onCredits(self, event):
      creditsWindow = CreditsWindow(self, -1, "Credits",
                                         size=(500, 240))
      creditsWindow.CentreOnScreen()
      creditsWindow.Show()

      
   def onLicence(self, event):
      licenseWindow = LicenseWindow(self, -1,
                                _("Licence"),
                                size=(500, 400),
                                style=wx.DEFAULT_FRAME_STYLE)
      licenseWindow.CenterOnScreen()
      licenseWindow.Show(True)


