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
import os

from gui.dictaddwin import DictAddWindow
import plugin
import register
import misc
import info
import dicttype

_ = wxGetTranslation

class Installer:
    """Default class used for installing plugins and registering
       dictionaries."""

    def __init__(self, mainWin, config):
        self.mainWin = mainWin
        self.config = config
        
    def showGUI(self):
        """Show graphical windows for selecting files and formats"""

        wildCard = "All files (*.*)|*.*|" \
                   "OpenDict plugins (*.zip)|*.zip|" \
                   "Slowo dictionaries (*.dwa)|*.dwa|" \
                   "Mova dictionaries (*.mova)|*.mova|" \
                   "TMX dictionaries (*.tmx)|*.tmx"
        
        fileDialog = wxFileDialog(self.mainWin,
                                  message=_("Choose dictionary file"),
                                  wildcard=_(wildCard),
                                  style=wxOPEN|wxCHANGE_DIR)
        fileDialog.CentreOnScreen()

        if fileDialog.ShowModal() == wxID_OK:
            filePath = fileDialog.GetPaths()[0]
        else:
            fileDialog.Destroy()
            return
        
        #fileName = os.path.split(filePath)[1]
        #rpos = fileName.rfind(".")
        #if rpos > 0:
        #    ext = fileName[rpos+1:]

        fileName = os.path.basename(filePath)
        extention = os.path.splitext(fileName)[1]

        extMapping = {}
        for t in dicttype.supportedTypes:
            for ext in t.getFileExtentions():
                extMapping[ext.lower()] = t

        print extMapping
      
        #textFormats = misc.dictFormats.keys()
        #textFormats.pop(textFormats.index("zip"))

        if not extention.lower() in extMapping.keys():
        #if rpos < 1 or ext.lower() not in ["zip"]+textFormats:
            print "Error: could not recognize!"
            window = DictAddWindow(self.mainWin, fileName, filePath)
            window.CentreOnScreen()
            window.Show(True)
        else:
            self.install(filePath, extention)

            
    def install(self, filePath, extention):
        """Copies files to special directories"""
        
        #ext = ext.lower()
        print "Installer.install() Ext:", ext
        #print misc.dictFormats.keys()
        #textFormats = misc.dictFormats.keys()
        #textFormats.pop(textFormats.index("zip"))
        plainFormats = []
        for t in dicttype.supportedTypes:
            if t != dicttype.PLUGIN:
                for ext in t.getFileExtentions():
                    plainFormats.append(ext)
        
        try:
            if extention in plainFormats:
                print "Registering..."
                #reg = register.Register()
                status = register.registerDictionary(filePath)
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


# ===========================================================================

def registerDictionary(filePath):
    """Register dictionary"""

    fileName = os.path.basename(filePath)
    dictionaryName = os.path.splitext(fileName)[0]

    dictDir = os.path.join(info.LOCAL_HOME,
                           info.__DICT_DIR,
                           info.__FILE_DICT_DIR,
                           fileName)


    if os.path.exists(dictDir):
        raise "Dictionary '%s' already exists"
    
    print "Will be installed in %s" % dictDir

    extention = os.path.splitext(fileName)[1][1:]
    
    #print extention
    dictType = None

    for t in dicttype.supportedTypes:
        for ext in t.getFileExtentions():
            #print ext
            if ext.lower() == extention.lower():
                dictType = t
                break

    if not dictType:
        raise "Dictionary type for '%s' still unknown! " \
              "This may be internal error." % fileName

    print dictType
    

if __name__ == "__main__":
    registerDictionary("/dsfs/dfghgh/sd.mova")
