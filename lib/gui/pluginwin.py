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
import wx.lib.mixins.listctrl as listmix
import wx

from shutil import rmtree
import os
import traceback
import urllib2

from gui import errorwin
import installer
import dicttype
import enc
import info
import misc
import xmltools
from logger import systemLog, debugLog, DEBUG, INFO, WARNING, ERROR


_ = wxGetTranslation

_addOnsListURL = 'file:///home/mjoc/opendict-add-ons.xml'
#_addOnsListURL = 'http://files.akl.lt/~mjoc/opendict-add-ons.xml'


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
                                         #| wx.LC_NO_HEADER
                                         | wx.SUNKEN_BORDER)
       vboxInstalled.Add(self.installedList, 1, wxALL | wxEXPAND, 1)
       
       #
       # "Remove" button
       #
       idRemove = wx.NewId()
       self.buttonRemove = wxButton(panelInstalled, idRemove, "Remove")
       self.buttonRemove.Disable()
       vboxInstalled.Add(self.buttonRemove, 0, wxALL | wxALIGN_RIGHT, 2)
       
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

       self.stAuthor = wxStaticText(panelInfo, -1, _("Author: "))
       self.stAuthor.Disable()
       grid.Add(self.stAuthor, 0, wxALL | wxALIGN_RIGHT)
       grid.Add(self.labelAuthor, 0, wxALL)

       vboxInfoBox.Add(grid, 1, wxALL | wxEXPAND, 1)
       vboxInfoBox.Add(self.textAbout, 0, wxALL | wxEXPAND, 1)
       
       sbSizerInfo.Add(vboxInfoBox, 1, wxALL | wxEXPAND, 0)
       
       vboxInfo.Add(sbSizerInfo, 1, wxALL | wxEXPAND, 0)

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
       msg = _("Downloading list of available dictionaries...")

       progressDialog = wx.ProgressDialog(title,
                                          msg,
                                          maximum=100,
                                          parent=self,
                                          style=wx.PD_CAN_ABORT
                                          | wx.PD_APP_MODAL)
       keepGoing = True
       count = 2

       progressDialog.Update(0)

       try:
           systemLog(INFO, "Opening %s..." % _addOnsListURL)
           up = urllib2.urlopen(_addOnsListURL)
           dataChunks = []
           count = 0
           percents = 0
           fileSize = up.info().getheader('Content-length')

           systemLog(INFO, "Reading file...")
           
           while keepGoing and count < fileSize:
               percents = int(float(count) / float(fileSize) * 100)
               
               if percents == 100:
                   progressDialog.Destroy()
                   break
           
               keepGoing = progressDialog.Update(percents)
               if not keepGoing:
                   progressDialog.Destroy()
                   break
           
               chunk = up.read(1024)
               dataChunks.append(chunk)
               count += len(chunk)

           systemLog(INFO, "Closing connection...")
           up.close()
           
           xmlData = ''.join(dataChunks)
       except Exception, e:
           traceback.print_exc()
           progressDialog.Destroy()
           systemLog(ERROR, "Unable to fetch add-ons list from %s: %s" \
                     % (_addOnsListURL, e))
           title = _("Error")
           msg = _("Unable to download list of available dictionaries " \
                   "(error message: %s)" % e)
           errorwin.showErrorMessage(title, msg)
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
           title = _("Error")
           msg = _("Unable to remove dictionary '%s'" % dictName)
           errorwin.showErrorMessage(title, msg)
           return

       self.installedList.DeleteItem(self.currentInstalledItemSelection)

       idDictMenuItem = None
       for iid, dictionary in self.app.config.ids.items():
           if dictionary == dictName:
               idDictMenuItem = iid

       if idDictMenuItem is not None:
           self.mainWin.menuDict.Delete(idDictMenuItem)
               
       self.buttonRemove.Disable()
       del self.app.dictionaries[dictName]
       

   def onClose(self, event):
       """Close event occured"""
       
       self.Destroy()


   def _fetchAddon(self, dictInfo):
       """Fetch add-on using progress bar"""

       print "Fetching %s from %s (%d, %s)" % (dictInfo.getName(),
                                               dictInfo.getLocation(),
                                               dictInfo.getSize(),
                                               dictInfo.getChecksum())

       downloadsDir = os.path.join(info.LOCAL_HOME, 'downloads')
       if not os.path.exists(downloadsDir):
           os.mkdir(downloadsDir)
       localPath = os.path.join(downloadsDir,
                                os.path.basename(dictInfo.getLocation()))

       title = _("Downloading '%s'" % dictInfo.getName())
       msg = _("Downloading '%s'\nfrom %s..." % (dictInfo.getName(),
                                              dictInfo.getLocation()))

       progressDialog = wx.ProgressDialog(title,
                                          msg,
                                          maximum=100,
                                          parent=self,
                                          style=wx.PD_CAN_ABORT
                                          | wx.PD_APP_MODAL)
       keepGoing = True
       count = 2

       progressDialog.Update(0)

       try:
           up = urllib2.urlopen(dictInfo.getLocation())

           fd = open(localPath, 'w')
           count = 0
           percents = 0
           fileSize = up.info().getheader('Content-length')
           
           while keepGoing and count < fileSize:
               percents = int(float(count) / float(fileSize) * 100)
               
               if percents == 100:
                   progressDialog.Destroy()
                   break
           
               keepGoing = progressDialog.Update(percents)
               if not keepGoing:
                   progressDialog.Destroy()
                   break
           
               chunk = up.read(1024)
               fd.write(chunk)
               count += len(chunk)
               print "%d bytes writeen (RX:%d" % (len(chunk), count)


       except Exception, e:
           traceback.print_exc()
           progressDialog.Destroy()
           systemLog(ERROR, "Unable to fetch %s list from %s: %s" \
                     % (dictInfo.getName(), dictInfo.getLocation(), e))
           title = _("Error")
           msg = _("Unable to download '%s' " \
                   "(error message: %s)" % (dictInfo.getName(), e))
           errorwin.showErrorMessage(title, msg)
           return
       else:
           fd.close()
           up.close()


       try:
           print "Installing..."
           inst = installer.Installer(self.mainWin, self.app.config)
           inst.install(localPath)
       except Exception, e:
           traceback.print_exc()
           title = _("Error")
           msg = _("Unable to install dictionary '%s' (Error occured: %s" \
                   % (dictInfo.getName(), e))
           errorwin.showErrorMessage(title, msg)



class PluginLicenseWindow(wxDialog):

   def __init__(self, parent, id, title, msg, pos=wxDefaultPosition,
                size=wxDefaultSize, style=wxDEFAULT_DIALOG_STYLE):
      wxDialog.__init__(self, parent, id, title, pos, size, style)

      vbox = wxBoxSizer(wxVERTICAL)
      vboxButtons = wxBoxSizer(wxHORIZONTAL)

      label = _("Please read the following License Agreement. You must " \
                "accept the terms of this agreement\nto install the plugin.")

      vbox.Add(wxStaticText(self, -1, label), 0, wxALL, 5)

      text = wxTextCtrl(self, -1, size=wxSize(-1, 300),
                        style=wxTE_MULTILINE | wxTE_READONLY)
      text.write(msg)

      vbox.Add(text, 1, wxALL | wxEXPAND, 10)

      self.buttonNo = wxButton(self, wxID_CANCEL, _("Do not accept"))
      vboxButtons.Add(self.buttonNo, 1, wxALL | wxCENTRE, 2)

      self.buttonYes = wxButton(self, wxID_OK, _("Accept"))
      vboxButtons.Add(self.buttonYes, 1, wxALL | wxCENTRE, 2)

      vbox.Add(vboxButtons, 0, wxALL | wxEXPAND, 0)
      self.SetSizer(vbox)
      self.Fit()

