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
# Module: installer.py

from wxPython.wx import *
import os

from gui.dictaddwin import DictAddWindow
import plugin
import register
import misc

_ = wxGetTranslation

class Installer:
    """Default class used for installing plugins and registering
       dictionaries."""

    def __init__(self, mainWin, config):
        self.mainWin = mainWin
        self.config = config
        
    def showGUI(self):
        
        fileDialog = wxFileDialog(self.mainWin, _("Choose dictionary file"), "", "",
                                  "", wxOPEN)
        fileDialog.CentreOnScreen()

        if fileDialog.ShowModal() == wxID_OK:
            filePath = fileDialog.GetPaths()[0]
        else:
            fileDialog.Destroy()
            return
        
        fileName = os.path.split(filePath)[1]
        rpos = fileName.rfind(".")
        if rpos > 0:
            ext = fileName[rpos+1:]
      
        textFormats = misc.dictFormats.keys()
        textFormats.pop(textFormats.index("zip"))
      
        if rpos < 1 or ext.lower() not in ["zip"]+textFormats:
            print "Error: could not recognize!"
            window = DictAddWindow(self.mainWin, fileName, filePath)
            window.CentreOnScreen()
            window.Show(True)
        else:
            self.install(filePath, ext)
            
    def install(self, filePath, ext):
        ext = ext.lower()
        print "Installer.install() Ext:", ext
        print misc.dictFormats.keys()
        textFormats = misc.dictFormats.keys()
        textFormats.pop(textFormats.index("zip"))
        
        try:
            if ext in textFormats:
                print "Registering..."
                reg = register.Register()
                status = reg.registerDictionary(filePath, ext, 
                                                self.config.defaultEnc)
                if (status == 0):
                    self.mainWin.SetStatusText(_("Instalation complete"))
                elif (status == 1):
                    self.mainWin.SetStatusText(_("Error: dictionary is already installed"))
            elif ext == "zip":
                print "Installing plugin"
                status = plugin.installPlugin(self.config, filePath)
                
                if (status == 0):
                    self.mainWin.SetStatusText(_("Instalation complete"))
                elif (status == 1):
                    self.mainWin.SetStatusText(_("Error: dictionary is already installed"))
                elif (status == 2):
                    self.mainWin.SetStatusText(_("Error: installation failed"))
                elif (status == 3):
                    self.mainWin.SetStatusText(_("Installation canceled"))
                    
        except:
            # Can this happen?
            self.mainWin.SetStatusText(_("Error: installation failed"))
            status = 1
            misc.printError()

