# -*- coding: utf-8 -*-

# OpenDict
# Copyright (c) 2003 Martynas Jocius <mjoc@delfi.lt>
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

from wxPython.wx import *

import plugin
import misc

_ = wxGetTranslation

# IDs range: 6300-6310
class DictAddWindow(wxDialog):

    def __init__(self, parent, fname, filePath):
        wxDialog.__init__(self, parent, -1, 
                         _("Add new dictionary"), wxDefaultPosition, 
                         wxDefaultSize, wxDEFAULT_DIALOG_STYLE)
        
        self.filePath = filePath
        vboxMain = wxBoxSizer(wxVERTICAL)
        
        msg1 = _("The file format of \"%s\" could not be \nrecognized by its" \
                 " extention. Please select one\nfrom the list:") % fname
        label1 = wxStaticText(self, -1, msg1)
        vboxMain.Add(label1, 0, wxALL | wxEXPAND, 5)
        
        choices = [misc.dictFormats["zip"], # OpenDict plugin
                   _("\"%s\" dictionary format") % misc.dictFormats["dwa"],
                   _("\"%s\" dictionary format") % misc.dictFormats["mova"],
                   _("\"%s\" dictionary format") % misc.dictFormats["tmx"],
                   _("\"%s\" dictionary format") % misc.dictFormats["dz"]]
        
        self.box = wxListBox(self, -1, wxPoint(-1, -1),
                        wxSize(-1, -1), choices, wxLB_SINGLE)
        
        vboxMain.Add(self.box, 1, wxALL | wxEXPAND, 3)
        
        hboxButtons = wxBoxSizer(wxHORIZONTAL)
        
        buttonOK = wxButton(self, wxID_OK, _("OK"))
        hboxButtons.Add(buttonOK, 0, wxALL, 1)
        
        buttonCancel = wxButton(self, 6302, _("Cancel"))
        hboxButtons.Add(buttonCancel, 0, wxALL, 1)
        
        vboxMain.Add(hboxButtons, 0, wxALL | wxCENTER, 2)
        
        self.SetSizer(vboxMain)
        self.Fit()
        
        EVT_BUTTON(self, wxID_OK, self.onOK)
        EVT_BUTTON(self, 6302, self.onCancel)
    
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
        
        print "Format:", ext
        
        from installer import Installer
        installer = Installer(parent, parent.app.config)
        installer.install(self.filePath, ext)
        
        #try:
        #    if ext in misc.dictFormats.values()[0:-1]:
        #        print "Registering..."
        #        parent.app.reg.registerDictionary(self.filePath, 
        #                 misc.dictFormats.keys()[misc.dictFormats.values().index(name)], 
        #                 parent.app.config.defaultEnc)
        #    else:
        #        print "Installing plugin..."
        #        plugin.installPlugin(parent.app.config, self.filePath)
        #except:
        #    misc.printError()
        #    parent.SetStatusText(_("Error: installation failed"))
        # 
        self.Destroy()
    
    def onCancel(self, event):
        self.GetParent().dictType = None
        self.Destroy()
