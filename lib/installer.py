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
import zipfile
import shutil
import traceback

from gui.dictaddwin import DictAddWindow
from gui import errorwin
import plugin
import register
import misc
import info
import dicttype
import xmltools
import util
import enc
import plaindict
import newplugin

_ = wxGetTranslation

class Installer:
    """Default class used for installing plugins and registering
       dictionaries."""

    def __init__(self, mainWin, config):
        self.mainWin = mainWin
        self.config = config

        
    def showGUI(self):
        """Show graphical window for selecting files and formats"""

        wildCard = "All files (*.*)|*.*|" \
                   "OpenDict plugins (*.zip)|*.zip|" \
                   "Slowo dictionaries (*.dwa)|*.dwa|" \
                   "Mova dictionaries (*.mova)|*.mova|" \
                   "DICT dictionaries (*.dz)|*.dz"
        
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

        fileName = os.path.basename(filePath)
        extention = os.path.splitext(fileName)[1][1:]

        extMapping = {}
        for t in dicttype.supportedTypes:
            for ext in t.getFileExtentions():
                extMapping[ext.lower()] = t

        if not extention.lower() in extMapping.keys():
            print "ERROR Unable to recognise %s format" % filePath
            window = DictAddWindow(self.mainWin, fileName, filePath)
            window.CentreOnScreen()
            window.Show(True)
        else:
            self.install(filePath, extention)

            
    def install(self, filePath, extention):
        """Install dictionary"""
 
        try:
            if extention.lower() in dicttype.PLUGIN.getFileExtentions():
                try:
                    directory = installDictionaryPlugin(filePath)
                    if directory:
                        dictionary = newplugin._loadDictionaryPlugin(directory)
                        print "Installed dict:", dictionary
                        self.mainWin.addDictionary(dictionary)
                except Exception, e:
                    traceback.print_exc()
                    errorwin.showErrorMessage(_("Installation failed"),
                                              enc.toWX(str(e)))
                    self.mainWin.SetStatusText(_("Installation failed"))
                    return

            else:
                try:
                    directory = installPlainDictionary(filePath)
                    if directory:
                        dictionary = plaindict._loadPlainDictionary(directory)
                        print "Installed dict:", dictionary
                        self.mainWin.addDictionary(dictionary)
                except Exception, e:
                    traceback.print_exc()
                    errorwin.showErrorMessage(_("Installation failed"),
                                              enc.toWX(str(e)))
                    self.mainWin.SetStatusText(_("Installation failed"))
                    return
        except:
            # Can this happen?
            self.mainWin.SetStatusText(_("Error: installation failed"))
            status = 1
            misc.printError()

        self.mainWin.SetStatusText(_("Dictionary successfully installed"))


# ===========================================================================

def installPlainDictionary(filePath):
    """Install plain dictionary and return directory path"""

    if not os.path.exists(filePath):
        raise Exception, _("File %s does not exist") % filePath

    if not os.path.isfile(filePath):
        raise Exception, _("%s is not a file") % filePath

    util.makeDirectories()

    fileName = os.path.basename(filePath)
    dictionaryName = os.path.splitext(fileName)[0]

    dictDir = os.path.join(info.LOCAL_HOME,
                           info.__DICT_DIR,
                           info.__PLAIN_DICT_DIR,
                           fileName)

    # Check existance
    if os.path.exists(dictDir):
        raise Exception, _("Dictionary '%s' already exists") % dictionaryName
    
    extention = os.path.splitext(fileName)[1][1:]
    dictType = None

    # Determine type
    for t in dicttype.supportedTypes:
        for ext in t.getFileExtentions():
            if ext.lower() == extention.lower():
                dictType = t
                break

    if not dictType:
        raise Exception, "Dictionary type for '%s' still unknown! " \
              "This may be internal error." % fileName

    # Create directories
    try:
        os.mkdir(dictDir)
        os.mkdir(os.path.join(dictDir, info.__PLAIN_DICT_CONFIG_DIR))
        os.mkdir(os.path.join(dictDir, info.__PLAIN_DICT_FILE_DIR))
        os.mkdir(os.path.join(dictDir, info.__PLAIN_DICT_DATA_DIR))
    except Exception, e:
        print "ERROR Unable to create dicrectories, aborted (%s)" % e
        try:
            shutil.rmtree(dictDir)
        except Exception, e:
            print "ERROR Unable to remove directories (%s)" % e


    # Determine info
    dictFormat = dictType.getIdName()
    md5sum = util.getMD5Sum(filePath)

    # Write configuration
    doc = xmltools.generatePlainDictConfig(name=dictionaryName,
                                           format=dictFormat,
                                           path=filePath,
                                           md5=md5sum,
                                           encoding='UTF-8')

    print "DEBUG Writing dictionary configuration..."
    xmltools.writePlainDictConfig(doc, os.path.join(dictDir,
                                                    'conf',
                                                    'config.xml'))


    return dictDir


def installDictionaryPlugin(filePath):
    """Install dictionary plugin and return directory path"""

    # Check if file exists
    if not os.path.exists(filePath):
        raise Exception, _("File %s does not exist") % filePath

    # Check if it is file
    if not os.path.isfile(filePath):
        raise Exception, _("%s is not a file") % filePath

    # Check if it is ZIP archive
    if os.path.splitext(filePath)[1].lower()[1:] != "zip":
        raise Exception, _("%s is not OpenDict dictionary plugin" % filePath)

    util.makeDirectories()

    zipFile = zipfile.ZipFile(filePath, 'r')

    # Test CRC
    if zipFile.testzip():
        raise Exception, _("Dictionary plugin file is corrupted")

    # Check if empty
    try:
        topDirectory = zipFile.namelist()[0]
    except Exception, e:
        raise Exception, _("Plugin file is empty (%s)" % e)

    configFileExists = False
    topLevelDirExists = False

    # Check for validity
    for fileInZip in zipFile.namelist():
        dirName = os.path.dirname(fileInZip)
        fileName = os.path.basename(fileInZip)

        if fileName == "plugin.xml":
            configFileExists = True

        if len(fileName) == 0 \
           and len(dirName.split('/')) == 1:
            topLevelDirExists = True

    if not configFileExists \
       or not topLevelDirExists:
        raise Exception, _("Selected file is not valid OpenDict plugin")

    pluginsPath = os.path.join(info.LOCAL_HOME,
                              info.PLUGIN_DICT_DIR)

    # Check if already installed
    if os.path.exists(os.path.join(info.LOCAL_HOME,
                                   info.PLUGIN_DICT_DIR,
                                   topDirectory)):
        raise Exception, _("This plugin dictionary already installed. " \
                           "If you want to upgrade it, please remove " \
                           "old version first.")

    # Install
    try:
        for fileInZip in zipFile.namelist():
            dirName = os.path.dirname(fileInZip)
            fileName = os.path.basename(fileInZip)

            if len(fileName) == 0:
                dirToCreate = os.path.join(pluginsPath, dirName)
                if not os.path.exists(dirToCreate):
                    print "Creating", dirToCreate
                    os.mkdir(dirToCreate)
            else:
                fileToWrite = os.path.join(pluginsPath, dirName, fileName)
                print "Writing:", fileToWrite
                fd = open(fileToWrite, 'w')
                fd.write(zipFile.read(fileInZip))
                fd.close()
    except Exception, e:
        try:
            shutil.rmtree(os.path.join(pluginsPath, topLevelDir))
        except Exception, e:
            print "ERROR %s" % e
            raise _("Error while removing created directories after " \
                    "plugin installation failure. This may be " \
                    "permission or disk space error.")

        print "ERROR %s" % e
        raise _("Unable to install plugin")


    return os.path.join(info.LOCAL_HOME,
                        info.PLUGIN_DICT_DIR,
                        topDirectory)


def removePlainDictionary(dictInstance):
    """Remove dictionary configuration"""

    filePath = dictInstance.getPath()
    fileName = os.path.basename(filePath)

    dictDir = os.path.join(info.LOCAL_HOME, info.PLAIN_DICT_DIR, fileName)

    try:
        print "DEBUG Removing %s..." % dictDir
        shutil.rmtree(dictDir)
    except Exception, e:
        raise Exception, str(e)


def removePluginDictionary(dictInstance):
    """Remove plugin dictionary"""

    filePath = dictInstance.getPath()
    fileName = os.path.basename(filePath)

    dictDir = os.path.join(info.LOCAL_HOME, info.PLUGIN_DICT_DIR, fileName)

    try:
        print "DEBUG Removing %s..." % dictDir
        shutil.rmtree(dictDir)
    except Exception, e:
        raise Exception, str(e)
    

## if __name__ == "__main__":
##     #try:
##     #    installPlainDictionary("/home/mjoc/")
##     #except Exception, e:
##     #    print "ERROR %s" % e

##     try:
##         installDictionaryPlugin("/home/mjoc/sampleplugin2.zip")
##     except Exception, e:
##         print "ERROR %s" % e
        
