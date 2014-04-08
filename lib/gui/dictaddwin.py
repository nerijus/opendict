# -*- coding: utf-8 -*-

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
# Module: gui.dictaddwin

import wx

from lib import misc

_ = wx.GetTranslation

# IDs range: 6300-6310
class DictAddWindow(wx.Dialog):

    def __init__(self, parent, fname, filePath):
        wx.Dialog.__init__(self, parent, -1, 
                         _("Add new dictionary"), wx.DefaultPosition, 
                         wx.DefaultSize, wx.DEFAULT_DIALOG_STYLE)
        
        self.filePath = filePath
        vboxMain = wx.BoxSizer(wx.VERTICAL)
        
        msg1 = _("The file format of \"%s\" could not be \nrecognized by its" \
                 " extention. Please select one\nfrom the list:") % fname
        label1 = wx.StaticText(self, -1, msg1)
        vboxMain.Add(label1, 0, wx.ALL | wx.EXPAND, 5)
        
        choices = [misc.dictFormats["zip"], # OpenDict plugin
                   _("\"%s\" dictionary format") % misc.dictFormats["dwa"],
                   _("\"%s\" dictionary format") % misc.dictFormats["mova"],
                   _("\"%s\" dictionary format") % misc.dictFormats["tmx"],
                   _("\"%s\" dictionary format") % misc.dictFormats["dz"]]
        
        self.box = wx.ListBox(self, -1, wx.Point(-1, -1),
                        wx.Size(-1, -1), choices, wx.LB_SINGLE)
        
        vboxMain.Add(self.box, 1, wx.ALL | wx.EXPAND, 3)
        
        hboxButtons = wx.BoxSizer(wx.HORIZONTAL)
        
        buttonOK = wx.Button(self, wx.ID_OK, _("OK"))
        hboxButtons.Add(buttonOK, 0, wx.ALL, 1)
        
        buttonCancel = wx.Button(self, 6302, _("Cancel"))
        hboxButtons.Add(buttonCancel, 0, wx.ALL, 1)
        
        vboxMain.Add(hboxButtons, 0, wx.ALL | wx.CENTER, 2)
        
        self.SetSizer(vboxMain)
        self.Fit()
        
        wx.EVT_BUTTON(self, wx.ID_OK, self.onOK)
        wx.EVT_BUTTON(self, 6302, self.onCancel)
    
    def onOK(self, event):
        parent = self.GetParent()
        i = self.box.GetSelection()
        ext = ""
        
        if i == 0:
            ext = "zip"
        elif i == 1:
            ext = "dwa"
        elif i == 2:
            ext = "mova"
        elif i == 3:
            ext = "tmx"
        elif i == 4:
            ext == "dz"
        
        from installer import Installer
        installer = Installer(parent, parent.app.config)
        installer.install(self.filePath, ext)
        
        self.Destroy()
    
    def onCancel(self, event):
        self.GetParent().dictType = None
        self.Destroy()
