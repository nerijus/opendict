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

import os
import zipfile
import shutil
import traceback

from lib.gui.dictaddwin import DictAddWindow
from lib.gui import errorwin
from lib import misc
from lib import info
from lib import dicttype
from lib import xmltools
from lib import util
from lib import enc
from lib import plaindict
from lib import newplugin

_ = wx.GetTranslation

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
        
        fileDialog = wx.FileDialog(self.mainWin,
                                  message=_("Choose dictionary file"),
                                  wildcard=wildCard,
                                  style=wx.OPEN|wx.CHANGE_DIR)
        fileDialog.CentreOnScreen()

        if fileDialog.ShowModal() == wx.ID_OK:
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
            title = _("Recognition Error")
            msg = _("File %s is not supported by OpenDict") % fileName
            errorwin.showErrorMessage(title, msg)
            return
        else:
            self.install(filePath)

            
    def install(self, filePath):
        """Install dictionary"""

        extention = os.path.splitext(filePath)[1][1:]
        succeeded = False
 
        try:
            if extention.lower() in dicttype.PLUGIN.getFileExtentions():
                try:
                    directory, dtype = installPlugin(filePath)
                    if directory:
                        if dtype.lower() == 'plugin':
                            dictionary = newplugin._loadDictionaryPlugin(directory)
                        else:
                            dictionary = plaindict._loadPlainDictionary(directory)
                        self.mainWin.addDictionary(dictionary)
                        succeeded = True
                        
                except Exception, e:
                    errorwin.showErrorMessage(_("Installation failed"),
                                              e.args[0] or '')
                    self.mainWin.SetStatusText(_("Installation failed"))
                    return

            else:
                try:
                    directory = installPlainDictionary(filePath)
                    if directory:
                        dictionary = plaindict._loadPlainDictionary(directory)
                        self.mainWin.addDictionary(dictionary)
                        succeeded = True
                except Exception, e:
                    traceback.print_exc()
                    errorwin.showErrorMessage(_("Installation Error"),
                                              e.args[0] or '')
                    self.mainWin.SetStatusText(_("Error: Installation failed"))
                    return
        except:
            # Can this happen?
            self.mainWin.SetStatusText(_("Error: Installation failed"))
            traceback.print_exc()

        if succeeded:
            title = _("Dictionary installed")
            msg = _("Dictionary successfully installed. You can choose it " \
                    "from \"Dictionaries\" menu now.")
            errorwin.showInfoMessage(title, msg)



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
        raise Exception, _("Dictionary \"%s\" is already installed") \
            % dictionaryName
    
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
        os.mkdir(os.path.join(dictDir, info._PLAIN_DICT_DATA_DIR))
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
                                           version=None,
                                           authors={},
                                           path=filePath,
                                           md5=md5sum,
                                           encoding='UTF-8',
                                           description=None)

    xmltools.writePlainDictConfig(doc, os.path.join(dictDir,
                                                    'conf',
                                                    'config.xml'))


    return dictDir


def installPlugin(filePath):
    """Install dictionary plugin and return directory path"""

    # Check if file exists
    if not os.path.exists(filePath):
        raise Exception, _("File %s does not exist") % filePath

    # Check if it is file
    if not os.path.isfile(filePath):
        raise Exception, _("%s is not a file") % filePath

    # Check if it is ZIP archive
    if os.path.splitext(filePath)[1].lower()[1:] != "zip":
        raise Exception, _("%s is not OpenDict dictionary plugin") % filePath

    util.makeDirectories()

    try:
        zipFile = zipfile.ZipFile(filePath, 'r')
    except Exception, e:
        raise Exception, _("File \"%s\" is not valid ZIP file") % \
              os.path.basename(filePath)

    # Test CRC
    if zipFile.testzip():
        raise Exception, _("Dictionary plugin file is corrupted")

    # Check if empty
    try:
        topDirectory = zipFile.namelist()[0]
    except Exception, e:
        raise Exception, _("Plugin file is empty (%s)") % e

    configFileExists = False
    pluginConfigExists = False
    plainConfigExists = False
    topLevelDirExists = False

    # Check for validity
    for fileInZip in zipFile.namelist():
        dirName = os.path.dirname(fileInZip)
        fileName = os.path.basename(fileInZip)

        if fileName == "plugin.xml":
            pluginConfigExists = True

        if fileName == 'config.xml':
            plainConfigExists = True

        if len(fileName) == 0 \
           and len(dirName.split('/')) == 1:
            topLevelDirExists = True

    if ((not plainConfigExists) and (not pluginConfigExists)) \
       or (not topLevelDirExists):
        raise Exception, _("Selected file is not valid OpenDict plugin")


    dtype = None
    if plainConfigExists:
        directory = _installPlainPlugin(filePath)
        dtype = 'plain'
    elif pluginConfigExists:
        directory = _installNormalPlugin(filePath)
        dtype = 'plugin'

    return (directory, dtype)
        

def _installNormalPlugin(filePath):
    """Install 'normal' OpenDict plugin"""

    zipFile = zipfile.ZipFile(filePath, 'r')

    topDirectory = zipFile.namelist()[0]
    pluginsPath = os.path.join(info.LOCAL_HOME,
                              info.PLUGIN_DICT_DIR)

    # Check if already installed
    if os.path.exists(os.path.join(info.LOCAL_HOME,
                                   info.PLUGIN_DICT_DIR,
                                   topDirectory)):
        raise Exception, _("This dictionary already installed. " \
                           "If you want to upgrade it, please remove " \
                           "old version first.")

    installFile = os.path.join(topDirectory, 'install.py')
    
    if installFile in zipFile.namelist():
        data = zipFile.read(installFile)

        try:
            struct = {}
            exec data in struct
        except Exception, e:
            title = _("Installation Error")
            msg = _("Installation tool for this dictionary failed to start. " \
                    "Please report this problem to developers.")
            errorwin.showErrorMessage(title, msg)
            return

        install = struct.get('install')
        if not install:
            title = _("Installation Error")
            msg = _("Installation tool for this dictionary failed to start. " \
                    "Please report this problem to developers.")
            errorwin.showErrorMessage(title, msg)
            return

        if not install(info.GLOBAL_HOME, info.LOCAL_HOME):
            title = _("Installation Aborted")
            msg = _("Dictionary installation has been aborted.")
            errorwin.showErrorMessage(title, msg)
            return
        

    # Install
    try:
        for fileInZip in zipFile.namelist():
            dirName = os.path.dirname(fileInZip)
            fileName = os.path.basename(fileInZip)

            if len(fileName) == 0:
                dirToCreate = os.path.join(pluginsPath, dirName)
                if not os.path.exists(dirToCreate):
                    os.mkdir(dirToCreate)
            else:
                fileToWrite = os.path.join(pluginsPath, dirName, fileName)
                fd = open(fileToWrite, 'wb')
                fd.write(zipFile.read(fileInZip))
                fd.close()
    except Exception, e:
        try:
            shutil.rmtree(os.path.join(pluginsPath, topLevelDir))
        except Exception, e:
            raise _("Error while removing created directories after " \
                    "plugin installation failure. This may be " \
                    "permission or disk space error.")

        raise _("Unable to install plugin")


    return os.path.join(info.LOCAL_HOME,
                        info.PLUGIN_DICT_DIR,
                        topDirectory)



def _installPlainPlugin(filePath):
    """Install prepared plain dictionary and return directory path"""

    zipFile = zipfile.ZipFile(filePath, 'r')
    topDirectory = zipFile.namelist()[0]

    # Test CRC
    if zipFile.testzip():
        raise Exception, _("Compressed dictionary file is corrupted")

    plainDictsPath = os.path.join(info.LOCAL_HOME,
                              info.PLAIN_DICT_DIR)

    # Check if already installed
    if os.path.exists(os.path.join(plainDictsPath,
                                   topDirectory)):
        raise Exception, _("This dictionary already installed. " \
                           "If you want to upgrade it, please remove " \
                           "old version first.")

    # Install
    try:
        for fileInZip in zipFile.namelist():
            dirName = os.path.dirname(fileInZip)
            fileName = os.path.basename(fileInZip)

            if len(fileName) == 0:
                dirToCreate = os.path.join(plainDictsPath, dirName)
                if not os.path.exists(dirToCreate):
                    os.mkdir(dirToCreate)
            else:
                fileToWrite = os.path.join(plainDictsPath, dirName, fileName)
                fd = open(fileToWrite, 'wb')
                fd.write(zipFile.read(fileInZip))
                fd.close()
    except Exception, e:
        try:
            shutil.rmtree(os.path.join(plainDictsPath, topDirectory))
        except Exception, e:
            raise _("Error while removing created directories after " \
                    "plugin installation failure. This may be " \
                    "permission or disk space error.")

        raise _("Unable to install dictionary")


    return os.path.join(info.LOCAL_HOME,
                        info.PLAIN_DICT_DIR,
                        topDirectory)



def removePlainDictionary(dictInstance):
    """Remove dictionary configuration"""

    filePath = dictInstance.getPath()
    fileName = os.path.basename(filePath)

    dictDir = dictInstance.getConfigDir()

    try:
        shutil.rmtree(dictDir)
    except Exception, e:
        raise Exception, str(e)


def removePluginDictionary(dictInstance):
    """Remove plugin dictionary"""

    filePath = dictInstance.getPath()
    fileName = os.path.basename(filePath)

    dictDir = dictInstance.getPath()

    try:
        shutil.rmtree(dictDir)
    except Exception, e:
        raise Exception, str(e)
    
