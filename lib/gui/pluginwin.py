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

#from wx import *
#import wx.lib.mixins.listctrl as listmix
import wx

from shutil import rmtree
import os
import traceback
import time

from lib.gui import errorwin
from lib import installer
from lib import dicttype
from lib import enc
from lib import info
from lib import misc
from lib import xmltools
from lib import util
from lib.logger import systemLog, debugLog, DEBUG, INFO, WARNING, ERROR


_ = wx.GetTranslation


class DictListCtrl(wx.ListCtrl):
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        

class PluginManagerWindow(wx.Frame):

   """Plugin Manager lets install, remove and view info
   about installed plugins"""

   def __init__(self, parent, id, title, pos=wx.DefaultPosition,
                size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE):
      wx.Frame.__init__(self, parent, id, title, pos, size, style)

      self.app = wx.GetApp()
      self.mainWin = parent
      self.currentInstalledItemSelection = -1
      self.currentAvailItemSelection = -1

      vboxMain = wx.BoxSizer(wx.VERTICAL)

      self.installedDictionaries = {}
      self.availDictionaries = self.app.cache.get('addons') or {}
      installed = True

      for dictName in self.app.dictionaries.keys():
          self.installedDictionaries[dictName] = installed

      tabbedPanel = wx.Notebook(self, -1)

      # Add 'installed' panel
      panelInstalled = self._makeInstalledPanel(tabbedPanel)
      tabbedPanel.AddPage(panelInstalled, _("Installed"))

      # Add 'available' panel
      panelAvailable = self._makeAvailablePanel(tabbedPanel)
      tabbedPanel.AddPage(panelAvailable, _("Available"))

      vboxMain.Add(tabbedPanel, 1, wx.ALL | wx.EXPAND, 2)

      # Add info panel
      panelInfo = self._makeInfoPanel()
      vboxMain.Add(panelInfo, 0, wx.ALL | wx.EXPAND, 2)

      hboxButtons = wx.BoxSizer(wx.HORIZONTAL)

      self.buttonClose = wx.Button(self, 163, _("Close"))
      hboxButtons.Add(self.buttonClose, 0, wx.ALL | wx.ALIGN_RIGHT, 3)

      vboxMain.Add(hboxButtons, 0, wx.ALL | wx.ALIGN_RIGHT, 1)

      self.SetIcon(wx.Icon(os.path.join(info.GLOBAL_HOME,
                                       "pixmaps",
                                       "icon-24x24.png"),
                          wx.BITMAP_TYPE_PNG))

      self.SetSizer(vboxMain)

      self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onPageChanged)
      
      wx.EVT_BUTTON(self, 161, self.onInstall)
      wx.EVT_BUTTON(self, 162, self.onRemove)
      wx.EVT_BUTTON(self, 163, self.onClose)

      self.addons = self.app.cache.get("addons", {})


   def _makeInstalledPanel(self, tabbedPanel):
       """Creates panel with for controlling installed dictionaries"""
       
       #
       # Boxes
       # 
       panelInstalled = wx.Panel(tabbedPanel, -1)
       vboxInstalled = wx.BoxSizer(wx.VERTICAL)

       # Help message
       labelHelp = wx.StaticText(panelInstalled, -1, 
          _("Checked dictionaries are available from the " \
          "menu, unchecked dictionaries \nare not available from the menu."));
       vboxInstalled.Add(labelHelp, 0, wx.ALL, 3)

       #
       # Installed list
       #
       idDictList = wx.NewId()
       self.installedList = wx.CheckListBox(panelInstalled, idDictList,
                                         style=wx.LC_REPORT
                                         | wx.LC_SINGLE_SEL
                                         | wx.SUNKEN_BORDER)
       self.Bind(wx.EVT_CHECKLISTBOX, self.onDictionaryChecked,
            self.installedList)
       self.Bind(wx.EVT_LISTBOX, self.onInstalledSelected,
            self.installedList)
       vboxInstalled.Add(self.installedList, 1, wx.ALL | wx.EXPAND, 1)

       hboxButtons = wx.BoxSizer(wx.HORIZONTAL)
       
       #
       # "Install from file" button
       #
       idInstallFile = wx.NewId()
       self.buttonInstallFile = wx.Button(panelInstalled, idInstallFile, 
                                         _("Install From File"))
       hboxButtons.Add(self.buttonInstallFile, 0, wx.ALL | wx.ALIGN_RIGHT, 2)
       
       #
       # "Remove" button
       #
       idRemove = wx.NewId()
       self.buttonRemove = wx.Button(panelInstalled, idRemove, _("Remove"))
       self.buttonRemove.Disable()
       hboxButtons.Add(self.buttonRemove, 0, wx.ALL | wx.ALIGN_RIGHT, 2)
       
       vboxInstalled.Add(hboxButtons, 0, wx.ALL | wx.ALIGN_RIGHT, 2)
       
       panelInstalled.SetSizer(vboxInstalled)
       vboxInstalled.Fit(panelInstalled)
       
       #
       # Make columns
       #

       dictNames = self.installedDictionaries.keys()
       dictNames.sort()
       self.setInstalledDicts(dictNames)

       self.Bind(wx.EVT_BUTTON, self.onRemove, self.buttonRemove)
       self.Bind(wx.EVT_BUTTON, self.onInstallFile, self.buttonInstallFile)

       return panelInstalled


   def _makeAvailablePanel(self, tabbedPanel):
       """Creates panel with for controlling installed dictionaries"""
       
       #
       # Boxes
       # 
       panelAvailable = wx.Panel(tabbedPanel, -1)
       vboxAvailable = wx.BoxSizer(wx.VERTICAL)

       #
       # List of available dictionaries
       #
       idAvailList = wx.NewId()
       self.availableList = DictListCtrl(panelAvailable, idAvailList,
                                         style=wx.LC_REPORT
                                         | wx.LC_SINGLE_SEL
                                         #| wx.LC_NO_HEADER
                                         | wx.SUNKEN_BORDER)
       vboxAvailable.Add(self.availableList, 1, wx.ALL | wx.EXPAND, 1)


       # Horizontal box for buttons
       hboxButtons = wx.BoxSizer(wx.HORIZONTAL)

       #
       # "Update" button
       #
       idUpdate = wx.NewId()
       self.buttonUpdate = wx.Button(panelAvailable, idUpdate,
                                    _("Update List"))
       hboxButtons.Add(self.buttonUpdate, 0, wx.ALL | wx.ALIGN_RIGHT, 2)
       
       #
       # "Install" button
       #
       idInstall = wx.NewId()
       self.buttonInstall = wx.Button(panelAvailable, idInstall, _("Install"))
       self.buttonInstall.Disable()
       hboxButtons.Add(self.buttonInstall, 0, wx.ALL | wx.ALIGN_RIGHT, 2)

       vboxAvailable.Add(hboxButtons, 0, wx.ALL | wx.ALIGN_RIGHT, 1)
       
       panelAvailable.SetSizer(vboxAvailable)
       vboxAvailable.Fit(panelAvailable)
       
       #
       # Make columns
       #
       self.availableList.InsertColumn(0, _("Name"))
       self.availableList.InsertColumn(1, _("Size"))

       addons = self.app.cache.get('addons')
       if not addons:
           addons = {}
       
       dictNames = addons.keys()
       dictNames.sort()
       
       for dictionary in dictNames:
           index = self.availableList.InsertStringItem(0, dictionary)
           sizeString = "%d KB" % addons.get(dictionary).getSize()
               
           self.availableList.SetStringItem(index, 1,
                                            sizeString)
           self.availableList.SetItemData(index, index+1)


       # Keep wide if list is empty yet
       if addons:
           self.availableList.SetColumnWidth(0, wx.LIST_AUTOSIZE)
           self.availableList.SetColumnWidth(1, wx.LIST_AUTOSIZE)
       else:
           self.availableList.SetColumnWidth(0, 200)
           self.availableList.SetColumnWidth(1, 120)

       self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onAvailableSelected,
                 self.availableList)

       self.Bind(wx.EVT_BUTTON, self.onInstall, self.buttonInstall)
       self.Bind(wx.EVT_BUTTON, self.onUpdate, self.buttonUpdate)

       return panelAvailable


   def _makeInfoPanel(self):
       """Create information panel"""

       #
       # Boxes
       # 
       panelInfo = wx.Panel(self, -1)
       vboxInfo = wx.BoxSizer(wx.VERTICAL)
       vboxInfoBox = wx.BoxSizer(wx.VERTICAL)
       sbSizerInfo = wx.StaticBoxSizer(\
          wx.StaticBox(panelInfo, -1, 
                      _("Information About Dictionary")),
          wx.VERTICAL)

       grid = wx.FlexGridSizer(3, 2, 1, 1)
       
       self.labelName = wx.StaticText(panelInfo, -1, "")
       self.labelVersion = wx.StaticText(panelInfo, -1, "")
       self.labelFormat = wx.StaticText(panelInfo, -1, "")
       self.labelAuthor = wx.StaticText(panelInfo, -1, "")
       self.labelSize = wx.StaticText(panelInfo, -1, "")
       
       self.textAbout = wx.TextCtrl(panelInfo, -1, size=(-1, 100),
                                   style=wx.TE_MULTILINE | wx.TE_READONLY)

       self.stName = wx.StaticText(panelInfo, -1, _("Name: "))
       self.stName.Disable()
       grid.Add(self.stName, 0, wx.ALL | wx.ALIGN_RIGHT)
       grid.Add(self.labelName, 0, wx.ALL)

       self.stVersion = wx.StaticText(panelInfo, -1, _("Version: "))
       self.stVersion.Disable()
       grid.Add(self.stVersion, 0, wx.ALL | wx.ALIGN_RIGHT)
       grid.Add(self.labelVersion, 0, wx.ALL)

       self.stAuthor = wx.StaticText(panelInfo, -1, _("Maintainer: "))
       self.stAuthor.Disable()
       grid.Add(self.stAuthor, 0, wx.ALL | wx.ALIGN_RIGHT)
       grid.Add(self.labelAuthor, 0, wx.ALL)

       vboxInfoBox.Add(grid, 1, wx.ALL | wx.EXPAND, 1)
       vboxInfoBox.Add(self.textAbout, 0, wx.ALL | wx.EXPAND, 1)
       
       sbSizerInfo.Add(vboxInfoBox, 1, wx.ALL | wx.EXPAND, 5)
       
       vboxInfo.Add(sbSizerInfo, 1, wx.ALL | wx.EXPAND, 5)

       panelInfo.SetSizer(vboxInfo)
       vboxInfo.Fit(panelInfo)

       return panelInfo


   def onDictionaryChecked(self, event, *args):
       index = event.GetSelection()
       label = self.installedList.GetString(index)
       if self.installedList.IsChecked(index):
           self._addDictToMenu(label)
           d = self.app.dictionaries.get(label)
           d.setActive()
       else:
           self._removeDictFromMenu(label)
           d = self.app.dictionaries.get(label)
           d.setActive(active=False)
       self.installedList.SetSelection(index)


   def _removeDictFromMenu(self, name):
       self.app.config.activedict.remove(name)
       self.app.config.activedict.save()
       self.app.window.removeDictionary(name)


   def _addDictToMenu(self, name):
       dict = None
       for k, v in self.app.dictionaries.items():
           if k == name:
               dict = v
       if dict:
           self.app.config.activedict.add(name)
           self.app.config.activedict.save()
           self.app.window.addDictionary(dict)


   def onPageChanged(self, event):

       _pageInstalled = 0
       _pageAvail = 1

       sel = event.GetSelection()

       if sel == _pageInstalled:
           if self.currentInstalledItemSelection == -1:
               self.clearInfo()
               self.disableInfo()
           else:
               self.enableInfo()
               self.showInstalledInfo()
       elif sel == _pageAvail:
           if self.currentAvailItemSelection == -1:
               self.clearInfo()
               self.disableInfo()
           else:
               self.enableInfo()
               self.showAvailableInfo()
               
               
   def onInstalledSelected(self, event):
       """Called when list item is selected"""
       
       self.currentInstalledItemSelection = event.GetSelection()
       self.buttonRemove.Enable(1)
       
       self.showInstalledInfo()


   def showInstalledInfo(self):
       """Show information about selected dictionary"""

       dictName = self.installedList.GetString(\
          self.currentInstalledItemSelection)

       dictInstance = self.app.dictionaries.get(dictName)
       self.showInfo(dictInstance)


   def showAvailableInfo(self):
       """Show information about selected dictionary"""

       dictName = self.availableList.GetItemText(\
          self.currentAvailItemSelection)


       dictInstance = self.addons.get(dictName)

       if not dictInstance:
           systemLog(ERROR, "BUG: add-on '%s' not found by name" % dictName)
           return
           
       self.showInfo(dictInstance)
       
       
   def showInfo(self, dictInstance):        
       """Show information about dictionary"""
       
       self.stName.Enable(1)
       self.stVersion.Enable(1)
       self.stAuthor.Enable(1)
       
       if dictInstance.getName():
           dictName = enc.toWX(dictInstance.getName())
       else:
           dictName = '--'
       self.labelName.SetLabel(dictName)
       
       if dictInstance.getVersion():
           dictVersion = enc.toWX(dictInstance.getVersion())
       else:
           dictVersion = '--'
       self.labelVersion.SetLabel(dictVersion)
       
       if dictInstance.getAuthors():
           authors = []
           for author in dictInstance.getAuthors():
               if author:
                   authors.append("%s <%s>" % (author.get('name'),
                                               author.get('email')))
      
           dictAuthors = enc.toWX(', '.join(authors))
       else:
           dictAuthors = '--'
       self.labelAuthor.SetLabel(dictAuthors)

       if dictInstance.getDescription():
           description = enc.toWX(dictInstance.getDescription().strip())
       else:
           description = ''
       self.textAbout.Clear()
       self.textAbout.WriteText(description)
      

   def onAvailableSelected(self, event):

      self.currentAvailItemSelection = event.m_itemIndex
      self.buttonInstall.Enable(1)
      self.showAvailableInfo()


   def clearInfo(self):
       """Clear info fields"""

       self.labelName.SetLabel('')
       self.labelVersion.SetLabel('')
       self.labelAuthor.SetLabel('')
       self.textAbout.Clear()


   def disableInfo(self):
       """Make info widgets inactive"""

       self.stName.Disable()
       self.stVersion.Disable()
       self.stAuthor.Disable()
       self.textAbout.Disable()


   def enableInfo(self):
       """Make info widgets active"""

       self.stName.Enable(1)
       self.stVersion.Enable(1)
       self.stAuthor.Enable(1)
       self.textAbout.Enable(1)


   def setInstalledDicts(self, dictNames):
       """Clear the list of installed dictionaries and set new items"""
    
       for i in range(self.installedList.GetCount()):
           self.installedList.Delete(i)

       dictNames.sort()
       i = 0

       for dictionary in dictNames:
           index = self.installedList.Insert(dictionary, i)
           if self.app.dictionaries[dictionary].getActive():
               self.installedList.Check(i)
           i += 1


   def setAvailDicts(self, addons):
       """Clear the list of available dictionaries and set
       new items"""

       self.availableList.DeleteAllItems()

       names = addons.keys()
       names.sort()
       names.reverse()

       for name in names:
           addon = addons.get(name)

           index = self.availableList.InsertStringItem(0, addon.getName())
           self.availableList.SetStringItem(index, 1,
                                            str(addon.getSize())+" KB")
           self.availableList.SetItemData(index, index+1)

       if names:
           self.availableList.SetColumnWidth(0, wx.LIST_AUTOSIZE)
       else:
           title = _("List updated")
           msg = _("All your dictionaries are up to date.")
           errorwin.showInfoMessage(title, msg)


   def onUpdate(self, event):
       """Update dictionaries list"""

       title = _("Downloading List")
       downloader = util.DownloadThread(self.app.config.get('repository-list'))

       progressDialog = wx.ProgressDialog(title,
                                          '',
                                          maximum=100,
                                          parent=self,
                                          style=wx.PD_CAN_ABORT
                                          | wx.PD_APP_MODAL)
       keepGoing = True
       error = None

       try:
           systemLog(INFO, "Opening %s..." % \
                     self.app.config.get('repository-list'))
           downloader.start()
           xmlData = ''
           
           while keepGoing and not downloader.finished():
               keepGoing = progressDialog.Update(downloader.getPercentage(),
                                                 downloader.getMessage())
               if not keepGoing:
                   downloader.stop()
                   break

               xmlData += downloader.getBytes()
               time.sleep(0.1)

           progressDialog.Destroy()
           xmlData += downloader.getBytes()

           systemLog(INFO, "Finished downloading list")
       except Exception, e:
           traceback.print_exc()
           progressDialog.Destroy()
           error = _("Unable to download list from %s: %s") \
                     % (self.app.config.get('repository-list'), e)

       if not error:
           error = downloader.getErrorMessage()

       if error:
           systemLog(ERROR, error)
           title = _("Unable to download list")
           errorwin.showErrorMessage(title, error)
           return

       if len(xmlData) == 0:
           return
       
       if hasattr(self, "addons"):
           del self.addons

       allAddons = xmltools.parseAddOns(xmlData)

       self.addons = {}

       for name, obj in allAddons.items():
           if name in self.app.dictionaries.keys() \
                  and obj.getVersion() <= (\
               self.app.dictionaries.get(name).getVersion() or ""):
               continue

           self.addons[name] = obj

       app = wx.GetApp()
       if app.cache.has_key("addons"):
           del app.cache["addons"]
       app.cache["addons"] = self.addons
       
       self.setAvailDicts(self.addons)
      

   def onInstall(self, event):
       """Install button pressed"""

       name = self.availableList.GetItemText(\
           self.currentAvailItemSelection)

       dictInfo = self.addons.get(name)

       if not dictInfo:
           systemLog(ERROR, "Interal Error, add-on %s not found in list" \
                     % name)
           return

       self._fetchAddon(dictInfo)


   def onInstallFile(self, event):
      """Install dictionary from file"""
      
      inst = installer.Installer(self.mainWin, self.app.config)
      inst.showGUI()

      dictNames = []
      for name in self.app.dictionaries.keys():
          dictNames.append(enc.toWX(name))
      self.setInstalledDicts(dictNames)


   def onRemove(self, event):
       """Remove button pressed"""

       systemLog(INFO, "Removing %s" % self.installedList.GetString(
           self.currentInstalledItemSelection))

       dictName = self.installedList.GetString(
           self.currentInstalledItemSelection)

       dictInstance = self.app.dictionaries.get(dictName)

       try:
           if dictInstance.getType() == dicttype.PLUGIN:
               removeDictionary = installer.removePluginDictionary
           else:
               removeDictionary = installer.removePlainDictionary

           removeDictionary(dictInstance)
       except Exception, e:
           traceback.print_exc()
           title = _("Unable to remove")
           msg = _("Unable to remove dictionary \"%s\"") % dictName
           errorwin.showErrorMessage(title, msg)
           return

       self.installedList.Delete(self.currentInstalledItemSelection)

       idDictMenuItem = None
       for iid, dictionary in self.app.config.ids.items():
           if dictionary == dictName:
               idDictMenuItem = iid

       if idDictMenuItem is not None:
           self.mainWin.menuDict.Delete(idDictMenuItem)

       parent = self.GetParent()
       if parent.activeDictionary \
              and dictName == parent.activeDictionary.getName():
           parent.onCloseDict(None)
               
       self.buttonRemove.Disable()
       del self.app.dictionaries[dictName]

       self.clearInfo()
       self.disableInfo()
       

   def onClose(self, event):
       """Close event occured"""
       
       self.Destroy()


   def _fetchAddon(self, dictInfo):
       """Fetch add-on using progress bar"""

       downloadsDir = os.path.join(info.LOCAL_HOME, 'downloads')
       if not os.path.exists(downloadsDir):
           os.mkdir(downloadsDir)
       localPath = os.path.join(downloadsDir,
                                os.path.basename(dictInfo.getLocation()))

       title = _("Downloading %s...") % dictInfo.getName()

       progressDialog = wx.ProgressDialog(title,
                                          '',
                                          maximum=100,
                                          parent=self,
                                          style=wx.PD_CAN_ABORT
                                          | wx.PD_APP_MODAL)
       keepGoing = True
       error = None

       downloader = util.DownloadThread(dictInfo.getLocation())
       stopped = False

       try:
           fd = open(localPath, 'wb')
           downloader.start()

           while keepGoing and not downloader.finished():
               keepGoing = progressDialog.Update(downloader.getPercentage(),
                                                 downloader.getMessage())

               if not keepGoing:
                   stopped = True
                   break

               chunk = downloader.getBytes()
               fd.write(chunk)
               time.sleep(0.1)
           
           bytes = downloader.getBytes()
           
           if len(bytes):
               fd.write(bytes)
           
	   progressDialog.Destroy()
	   downloader.stop()


       except Exception, e:
           traceback.print_exc()
           progressDialog.Destroy()

           error = "Unable to fetch \"%s\" from %s: %s" \
                   % (dictInfo.getName(), dictInfo.getLocation(), e)
           systemLog(ERROR, error)

       fd.close()

       if stopped:
           return

       if not error:
           error = downloader.getErrorMessage()

       if error:
           systemLog(ERROR, error)
           title = _("Unable to download")
           errorwin.showErrorMessage(title, error)
           return

       md5sum = util.getMD5Sum(localPath)

       #
       # Check checksum
       #
       if md5sum != dictInfo.getChecksum():
           title = _("File is damaged")
           msg = _("Downloaded file is damaged and cannot be installed. " \
                   "Please try again.")
           errorwin.showErrorMessage(title, msg)
           return

       #
       # Remove old version if exists
       #
       if dictInfo.getName() in self.app.dictionaries.keys():
           try:
               dictInstance = self.app.dictionaries.get(dictInfo.getName())
               if dictInstance.getType() == dicttype.PLUGIN:
                   installer.removePluginDictionary(dictInstance)
               else:
                   installer.removePlainDictionary(dictInstance)

           except Exception, e:
               traceback.print_exc()
               title = _("Error")
               msg = _("Unable to remove old version of \"%s\". "
                       "Error occured: \"<i>%s</i>\". New version "
                       "cannot be installed without removing old one.") \
                       % (dictInstance.getName(), e)
               errorwin.showErrorMessage(title, msg)
               return
       
       #
       # Install
       #
       try:
           inst = installer.Installer(self.mainWin, self.app.config)
           inst.install(localPath)

           if self.installedList.FindString(dictInfo.getName()) == wx.NOT_FOUND:
               index = self.installedList.Insert(dictInfo.getName(), 0)
               self.installedList.Check(0)
               self.app.config.activedict.add(dictInfo.getName())
               self.app.config.activedict.save()

               # FIXME: Code-wasting. Separated duplicated code into
               # functions.
           
       except Exception, e:
           traceback.print_exc()
           title = _("Unable to install")
           msg = _("Unable to install dictionary \"%s\".") \
                   % dictInfo.getName()
           errorwin.showErrorMessage(title, msg)
           return

       self.availableList.DeleteItem(self.currentAvailItemSelection)
       del self.addons[dictInfo.getName()]
       self.buttonInstall.Disable()

       self.clearInfo()
       self.disableInfo()
