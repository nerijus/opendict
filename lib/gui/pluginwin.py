
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
import wx.lib.mixins.listctrl as listmix
import wx

from shutil import rmtree
import os
import traceback
import time

from gui import errorwin
import installer
import dicttype
import enc
import info
import misc
import xmltools
import util
from logger import systemLog, debugLog, DEBUG, INFO, WARNING, ERROR


_ = wxGetTranslation

#_addOnsListURL = 'http://localhost/~mjoc/OpenDict/opendict-add-ons.xml'
#_addOnsListURL = 'http://files.akl.lt/~mjoc/OpenDict/Data/opendict-add-ons.xml'
_addOnsListURL = 'http://opendict.sf.net/Repository/Data/opendict-add-ons.xml'


class DictListCtrl(wx.ListCtrl):
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        

class PluginManagerWindow(wxFrame):

   """Plugin Manager lets install, remove and view info
   about installed plugins"""

   def __init__(self, parent, id, title, pos=wxDefaultPosition,
                size=wxDefaultSize, style=wxDEFAULT_FRAME_STYLE):
      wxFrame.__init__(self, parent, id, title, pos, size, style)

      self.app = wxGetApp()
      self.mainWin = parent
      self.currentInstalledItemSelection = -1
      self.currentAvailItemSelection = -1

      vboxMain = wxBoxSizer(wxVERTICAL)

      self.installedDictionaries = {}
      self.availDictionaries = self.app.cache.get('addons') or {}
      installed = True

      for dictName in self.app.dictionaries.keys():
          self.installedDictionaries[dictName] = installed

      tabbedPanel = wx.Notebook(self, -1)

      # Add 'installed' panel
      panelInstalled = self._makeInstalledPanel(tabbedPanel)
      tabbedPanel.AddPage(panelInstalled, "Installed")

      # Add 'available' panel
      panelAvailable = self._makeAvailablePanel(tabbedPanel)
      tabbedPanel.AddPage(panelAvailable, "Available")

      vboxMain.Add(tabbedPanel, 1, wxALL | wxEXPAND, 2)

      # Add info panel
      panelInfo = self._makeInfoPanel()
      vboxMain.Add(panelInfo, 0, wxALL | wxEXPAND, 2)

      hboxButtons = wxBoxSizer(wxHORIZONTAL)

      self.buttonClose = wxButton(self, 163, _("Close"))
      hboxButtons.Add(self.buttonClose, 0, wxALL | wxALIGN_RIGHT, 3)

      vboxMain.Add(hboxButtons, 0, wxALL | wxALIGN_RIGHT, 1)

      self.SetIcon(wxIcon(os.path.join(info.GLOBAL_HOME,
                                       "pixmaps",
                                       "icon-24x24.png"),
                          wxBITMAP_TYPE_PNG))

      self.SetSizer(vboxMain)

      self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onPageChanged)
      
      EVT_BUTTON(self, 161, self.onInstall)
      EVT_BUTTON(self, 162, self.onRemove)
      EVT_BUTTON(self, 163, self.onClose)


   def _makeInstalledPanel(self, tabbedPanel):
       """Creates panel with for controlling installed dictionaries"""
       
       #
       # Boxes
       # 
       panelInstalled = wxPanel(tabbedPanel, -1)
       vboxInstalled = wxBoxSizer(wxVERTICAL)

       #
       # Installed list
       #
       idDictList = wx.NewId()
       self.installedList = DictListCtrl(panelInstalled, idDictList,
                                         style=wx.LC_REPORT
                                         | wx.LC_SINGLE_SEL
                                         | wx.SUNKEN_BORDER)
       vboxInstalled.Add(self.installedList, 1, wxALL | wxEXPAND, 1)

       hboxButtons = wx.BoxSizer(wx.HORIZONTAL)
       
       #
       # "Install from file" button
       #
       idInstallFile = wx.NewId()
       self.buttonInstallFile = wxButton(panelInstalled, idInstallFile, 
                                         "Install From File")
       hboxButtons.Add(self.buttonInstallFile, 0, wxALL | wxALIGN_RIGHT, 2)
       
       #
       # "Remove" button
       #
       idRemove = wx.NewId()
       self.buttonRemove = wxButton(panelInstalled, idRemove, "Remove")
       self.buttonRemove.Disable()
       hboxButtons.Add(self.buttonRemove, 0, wxALL | wxALIGN_RIGHT, 2)
       
       vboxInstalled.Add(hboxButtons, 0, wxALL | wxALIGN_RIGHT, 2)
       
       panelInstalled.SetSizer(vboxInstalled)
       vboxInstalled.Fit(panelInstalled)
       
       #
       # Make columns
       #
       self.installedList.InsertColumn(0, "Name")
       
       dictNames = self.installedDictionaries.keys()
       dictNames.sort()
       
       self.setInstalledDicts(dictNames)

       self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onInstalledSelected,
                 self.installedList)

       self.Bind(wx.EVT_BUTTON, self.onRemove, self.buttonRemove)
       self.Bind(wx.EVT_BUTTON, self.onInstallFile, self.buttonInstallFile)

       return panelInstalled


   def _makeAvailablePanel(self, tabbedPanel):
       """Creates panel with for controlling installed dictionaries"""
       
       #
       # Boxes
       # 
       panelAvailable = wxPanel(tabbedPanel, -1)
       vboxAvailable = wxBoxSizer(wxVERTICAL)

       #
       # Installed list
       #
       idAvailList = wx.NewId()
       self.availableList = DictListCtrl(panelAvailable, idAvailList,
                                         style=wx.LC_REPORT
                                         | wx.LC_SINGLE_SEL
                                         #| wx.LC_NO_HEADER
                                         | wx.SUNKEN_BORDER)
       vboxAvailable.Add(self.availableList, 1, wxALL | wxEXPAND, 1)


       # Horizontal box for buttons
       hboxButtons = wxBoxSizer(wxHORIZONTAL)

       #
       # "Update" button
       #
       idUpdate = wx.NewId()
       self.buttonUpdate = wxButton(panelAvailable, idUpdate,
                                    _("Update List"))
       hboxButtons.Add(self.buttonUpdate, 0, wxALL | wxALIGN_RIGHT, 2)
       
       #
       # "Install" button
       #
       idInstall = wx.NewId()
       self.buttonInstall = wxButton(panelAvailable, idInstall, _("Install"))
       self.buttonInstall.Disable()
       hboxButtons.Add(self.buttonInstall, 0, wxALL | wxALIGN_RIGHT, 2)

       vboxAvailable.Add(hboxButtons, 0, wxALL | wxALIGN_RIGHT, 1)
       
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
       panelInfo = wxPanel(self, -1)
       vboxInfo = wxBoxSizer(wxVERTICAL)
       vboxInfoBox = wxBoxSizer(wxVERTICAL)
       sbSizerInfo = wxStaticBoxSizer(\
          wxStaticBox(panelInfo, -1, 
                      _("Information About Dictionary")),
          wxVERTICAL)

       grid = wxFlexGridSizer(3, 2, 1, 1)
       
       self.labelName = wxStaticText(panelInfo, -1, "")
       self.labelVersion = wxStaticText(panelInfo, -1, "")
       self.labelFormat = wxStaticText(panelInfo, -1, "")
       self.labelAuthor = wxStaticText(panelInfo, -1, "")
       self.labelSize = wxStaticText(panelInfo, -1, "")
       
       self.textAbout = wxTextCtrl(panelInfo, -1, size=(-1, 100),
                                   style=wxTE_MULTILINE | wxTE_READONLY)

       self.stName = wxStaticText(panelInfo, -1, _("Name: "))
       self.stName.Disable()
       grid.Add(self.stName, 0, wxALL | wxALIGN_RIGHT)
       grid.Add(self.labelName, 0, wxALL)

       self.stVersion = wxStaticText(panelInfo, -1, _("Version: "))
       self.stVersion.Disable()
       grid.Add(self.stVersion, 0, wxALL | wxALIGN_RIGHT)
       grid.Add(self.labelVersion, 0, wxALL)

       self.stAuthor = wxStaticText(panelInfo, -1, _("Maintainer: "))
       self.stAuthor.Disable()
       grid.Add(self.stAuthor, 0, wxALL | wxALIGN_RIGHT)
       grid.Add(self.labelAuthor, 0, wxALL)

       vboxInfoBox.Add(grid, 1, wxALL | wxEXPAND, 1)
       vboxInfoBox.Add(self.textAbout, 0, wxALL | wxEXPAND, 1)
       
       sbSizerInfo.Add(vboxInfoBox, 1, wxALL | wxEXPAND, 5)
       
       vboxInfo.Add(sbSizerInfo, 1, wxALL | wxEXPAND, 5)

       panelInfo.SetSizer(vboxInfo)
       vboxInfo.Fit(panelInfo)

       return panelInfo


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
       
       self.currentInstalledItemSelection = event.m_itemIndex
       self.buttonRemove.Enable(1)
       
       self.showInstalledInfo()


   def showInstalledInfo(self):
       """Show information about selected dictionary"""

       dictName = self.installedList.GetItemText(\
          self.currentInstalledItemSelection)

       dictInstance = self.app.dictionaries.get(dictName)
       self.showInfo(dictInstance)


   def showAvailableInfo(self):
       """Show information about selected dictionary"""

       dictName = self.availableList.GetItemText(\
          self.currentAvailItemSelection)


       dictInstance = self.addons.get(dictName)

       if not dictInstance:
           systemLog(ERROR, "BUG: add-on %s not found by name" % dictName)
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

       self.installedList.DeleteAllItems()
       
       for dictionary in dictNames:
           index = self.installedList.InsertStringItem(0, dictionary)          
           self.installedList.SetItemData(index, index+1)

       self.installedList.SetColumnWidth(0, wx.LIST_AUTOSIZE)


   def setAvailDicts(self, addons):
       """Clear the list of available dictionaries and set
       new items"""

       self.availableList.DeleteAllItems()

       names = addons.keys()
       names.sort()

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
       downloader = util.DownloadThread(_addOnsListURL)

       progressDialog = wx.ProgressDialog(title,
                                          '',
                                          maximum=100,
                                          parent=self,
                                          style=wx.PD_CAN_ABORT
                                          | wx.PD_APP_MODAL)
       keepGoing = True
       error = None

       try:
           systemLog(INFO, "Opening %s..." % _addOnsListURL)
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
           error = _("Unable to download list from %s: %s" \
                     % (_addOnsListURL, e))

       if not error:
           error = downloader.getErrorMessage()

       if error:
           systemLog(ERROR, error)
           title = _("Unable to donwload list")
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

       app = wxGetApp()
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

       systemLog(INFO, "Removing %s" % self.installedList.GetItemText(\
           self.currentInstalledItemSelection))

       dictName = self.installedList.GetItemText(\
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
           msg = _("Unable to remove dictionary \"%s\"" % dictName)
           errorwin.showErrorMessage(title, msg)
           return

       self.installedList.DeleteItem(self.currentInstalledItemSelection)

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

       title = _("Downloading %s..." % dictInfo.getName())

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
           fd = open(localPath, 'w')
           downloader.start()

           while keepGoing and not downloader.finished():
               keepGoing = progressDialog.Update(downloader.getPercentage(),
                                                 downloader.getMessage())

               if not keepGoing:
                   downloader.stop()
                   stopped = True
                   break

               chunk = downloader.getBytes()
               fd.write(chunk)
               time.sleep(0.1)

           progressDialog.Destroy()

           bytes = downloader.getBytes()
           
           if len(bytes):
               fd.write(bytes)

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
           title = _("Unable to donwload")
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
               msg = _("Unable to remove old version of \"%s\". " \
                       "Error occured: \"<i>%s</i>\". New version " \
                       "cannot be installed without removing old one." \
                       % (dictInstance.getName(), e))
               errorwin.showErrorMessage(title, msg)
               return
       
       #
       # Install
       #
       try:
           inst = installer.Installer(self.mainWin, self.app.config)
           inst.install(localPath)

           if self.installedList.FindItem(0, dictInfo.getName()) == -1:
               index = self.installedList.InsertStringItem(0,
                                                           dictInfo.getName())
               self.installedList.SetItemData(index, index+1)
               self.installedList.SetColumnWidth(0, wx.LIST_AUTOSIZE)
           
       except Exception, e:
           traceback.print_exc()
           title = _("Unable to install")
           msg = _("Unable to install dictionary \"%s\"." \
                   % dictInfo.getName())
           errorwin.showErrorMessage(title, msg)

       self.availableList.DeleteItem(self.currentAvailItemSelection)
