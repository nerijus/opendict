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
import  wx.lib.mixins.listctrl  as  listmix
import wx

from shutil import rmtree
import os
import traceback

from misc import printError
from gui import errorwin
import installer
import dicttype

#import group
import misc

_ = wxGetTranslation


class DictListCtrl(wx.ListCtrl):
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        #listmix.ListCtrlAutoWidthMixin.__init__(self)

        

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
      self.availDictionaries = {}
      installed = True

      for dictName in self.app.dictionaries.keys():
          self.installedDictionaries[dictName] = installed

      #for xxx in [u'Vienas pienas', u'Du kartu', u'Trys kas nors']:
      #    self.allDictionaries[xxx] = not installed

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
       self.installedList.InsertColumn(0, "Dictionary Name")
       
       dictNames = self.installedDictionaries.keys()
       dictNames.sort()
       
       print dictNames
       
       for dictionary in dictNames:
           installed = self.installedDictionaries.get(dictionary)
           
           index = self.installedList.InsertStringItem(0, dictionary)
           
           self.installedList.SetItemData(index, index+1)

       # This should be called after updating list
       self.installedList.SetColumnWidth(0, wx.LIST_AUTOSIZE)

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
       self.availableList.InsertColumn(0, _("Dictionary Name"))

       item = wxListItem()
       item.m_mask = wx.LIST_MASK_TEXT | wxLIST_MASK_FORMAT
       item.m_format = wx.LIST_FORMAT_RIGHT
       item.m_text = _("Size")

       self.availableList.InsertColumnInfo(1, item)
       
       size = 100
       
       dictNames = self.availDictionaries.keys()
       dictNames.sort()
       
       print dictNames
       
       for dictionary in dictNames:
           installed = self.availDictionaries.get(dictionary)
           
           index = self.availableList.InsertStringItem(0, dictionary)
           
           sizeString = "%d KB"
               
           self.availableList.SetStringItem(index, 1,
                                            sizeString % size)
           size += 1000
           
           self.availableList.SetItemData(index, index+1)


       # Keep wide if list is empty yet
       if self.availDictionaries:
           self.availableList.SetColumnWidth(0, wx.LIST_AUTOSIZE)
           self.availableList.SetColumnWidth(1, wx.LIST_AUTOSIZE)
       else:
           self.availableList.SetColumnWidth(0, 200)
           self.availableList.SetColumnWidth(1, 70)

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
       grid.Add(self.stName, 0, wxALL)
       grid.Add(self.labelName, 0, wxALL)

       self.stVersion = wxStaticText(panelInfo, -1, _("Version: "))
       self.stVersion.Disable()
       grid.Add(self.stVersion, 0, wxALL)
       grid.Add(self.labelVersion, 0, wxALL)

       self.stAuthor = wxStaticText(panelInfo, -1, _("Author: "))
       self.stAuthor.Disable()
       grid.Add(self.stAuthor, 0, wxALL)
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
           print "Showing info about installed item %d" \
                 % self.currentInstalledItemSelection
           if self.currentInstalledItemSelection == -1:
               self.disableInfo()
           else:
               self.enableInfo()
       elif sel == _pageAvail:
           print "Showing info about avail item %d" \
                 % self.currentAvailItemSelection
           if self.currentAvailItemSelection == -1:
               self.disableInfo()
           else:
               self.enableInfo()
       

   def GetListCtrl(self):
        return self.list


   def onInstalledSelected(self, event):

      self.currentInstalledItemSelection = event.m_itemIndex
      self.buttonRemove.Enable(1)

      self.stName.Enable(1)
      self.stVersion.Enable(1)
      self.stAuthor.Enable(1)

      print self.installedList.GetItemText(self.currentInstalledItemSelection)
      
##       name = event.GetString()
##       size = -1
      
##       #if self.dictMap[name] == "plugin":
##       if name in self.app.config.plugins.keys():
##              plugin = self.app.config.plugins[name]

##              try:
##                 self.labelName.SetLabel(plugin.name.decode('UTF-8'))
##              except Exception, e:
##                 print "ERROR Unable to set label '%s' (%s)" \
##                       % (plugin.name, e)

##              try:
##                 self.labelVersion.SetLabel(plugin.version.decode('UTF-8'))
##              except Exception, e:
##                 print "ERROR: Unable to set label '%s' (%s)" \
##                       % (plugin.version, e)

##              self.labelFormat.SetLabel(_("OpenDict plugin"))
                
##              try:
##                 self.labelAuthor.SetLabel(plugin.author.decode('UTF-8'))
##              except Exception, e:
##                 print "ERROR: Unable to set label '%s' (%s)" \
##                       % (plugin.author, e)
                
##              self.textAbout.Clear()

##              try:
##                 self.textAbout.WriteText(plugin.about.decode('UTF-8'))
##              except Exception, e:
##                 print "ERROR: Unable to set label '%s' (%s)" \
##                       % (plugin.about, e)
             
##              path = self.app.config.plugins[name].dir

##              pluginDirPath = os.path.join(info.LOCAL_HOME,
##                                           info.__DICT_DIR,
##                                           info.__PLUGIN_DICT_DIR,
##                                           path)
##              if os.path.exists(pluginDirPath):
##                  size = misc.getDirSize(pluginDirPath,
##                                         0, 0, 10)
##              else:
##                  size = misc.getDirSize(os.path.join(info.GLOBAL_HOME,
##                                                      info.__DICT_DIR,
##                                                      info.__PLUGIN_DICT_DIR,
##                                                      path),
##                                         0, 0, 10)
                 
##       elif name in self.app.config.registers.keys():
##              regFile = self.app.config.registers[name]
##              self.labelName.SetLabel(name)
##              self.labelVersion.SetLabel("--")
##              self.labelFormat.SetLabel(misc.dictFormats[regFile[1]])
##              self.labelAuthor.SetLabel("--")
##              self.textAbout.Clear()
             
##              size = misc.getFileSize(self.app.config.registers[name][0])
##       else:
##           print "onPluginSelected(): misunderstood"
      
##       self.labelSize.SetLabel(str(size/1000.)+" KB")


   def onAvailableSelected(self, event):

      self.currentAvailItemSelection = event.m_itemIndex
      print self.availableList.GetItemText(self.currentAvailItemSelection)
      #self.installedList.
      self.buttonInstall.Enable(1)
      self.enableInfo()


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


   def onUpdate(self, event):
       """Update dictionaries list"""

       print "Update"
      

   def onInstall(self, event):
       """Install button pressed"""

       print "Install %s" % self.installedList.GetItemText(\
           self.currentAvailItemSelection)


   def onRemove(self, event):
       """Remove button pressed"""

       print "Remove %s" % self.installedList.GetItemText(\
           self.currentInstalledItemSelection)

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
       

   def onClose(self, event):
       """Close event occured"""
       
       self.Destroy()


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

