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

from misc import printError
from gui import errorwin

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

      vboxMain = wxBoxSizer(wxVERTICAL)

      self.allDictionaries = {}
      installed = True

      for dictName in self.app.dictionaries.keys():
          self.allDictionaries[dictName] = installed

      for xxx in [u'Vienas pienas', u'Du kartu', u'Trys kas nors']:
          self.allDictionaries[xxx] = not installed


      # Add 'installed' panel
      panelInstalled = self._makeInstalledPanel()
      vboxMain.Add(panelInstalled, 1, wxALL | wxEXPAND, 2)

      # Add 'available' panel
      panelAvailable = self._makeAvailablePanel()
      vboxMain.Add(panelAvailable, 1, wxALL | wxEXPAND, 2)

      # Add info panel
      panelInfo = self._makeInfoPanel()
      vboxMain.Add(panelInfo, 0, wxALL | wxEXPAND, 2)

      hboxButtons = wxBoxSizer(wxHORIZONTAL)

      self.buttonClose = wxButton(self, 163, _("Close"))
      hboxButtons.Add(self.buttonClose, 0, wxALL | wxALIGN_RIGHT, 3)

      vboxMain.Add(hboxButtons, 0, wxALL | wxALIGN_RIGHT, 1)

      self.SetSizer(vboxMain)
      
      self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onAvailableSelected,
                self.availableList)
      
      EVT_BUTTON(self, 161, self.onInstall)
      EVT_BUTTON(self, 162, self.onRemove)
      EVT_BUTTON(self, 163, self.onClose)


   def _makeInstalledPanel(self):
       """Creates panel with for controlling installed dictionaries"""
       
       #
       # Boxes
       # 
       panelInstalled = wxPanel(self, -1)
       vboxInstalled = wxBoxSizer(wxVERTICAL)
       vboxInstalledBox = wxBoxSizer(wxVERTICAL)
       sbSizerInstalled = wxStaticBoxSizer(\
          wxStaticBox(panelInstalled, -1, 
                      _("Installed Dictionaries")),
          wxVERTICAL)
       
       #
       # Installed list
       #
       idDictList = wx.NewId()
       self.installedList = DictListCtrl(panelInstalled, idDictList,
                                         style=wx.LC_REPORT)# | wx.BORDER_SUNKEN)
       vboxInstalledBox.Add(self.installedList, 1, wxALL | wxEXPAND, 1)
       
       #
       # "Remove" button
       #
       idRemove = wx.NewId()
       self.buttonRemove = wxButton(panelInstalled, idRemove, "Remove")
       vboxInstalledBox.Add(self.buttonRemove, 0, wxALL | wxALIGN_RIGHT, 2)
       
       sbSizerInstalled.Add(vboxInstalledBox, 1, wxALL | wxEXPAND, 0)
       panelInstalled.SetSizer(vboxInstalled)
       vboxInstalled.Fit(panelInstalled)
       
       vboxInstalled.Add(sbSizerInstalled, 1, wxALL | wxEXPAND, 0)
       
       #
       # Make columns
       #
       self.installedList.InsertColumn(0, "Dictionary Name")
       self.installedList.InsertColumn(1, "Size")
       
       size = 100
       
       dictNames = self.allDictionaries.keys()
       dictNames.sort()
       
       print dictNames
       
       for dictionary in dictNames:
           installed = self.allDictionaries.get(dictionary)
           
           index = self.installedList.InsertStringItem(0, dictionary)
           
           sizeString = "%d KB"
           
           #if not installed:
           #    sizeString = "%d KB"
               
           self.installedList.SetStringItem(index, 1,
                                            sizeString % size)
           size += 100
           

           #status = None
           #if installed:
           #    status = "Installed"
           #else:
           #    status = "Not installed"
         
           #self.installedList.SetStringItem(index, 2, status)
           self.installedList.SetItemData(index, index+1)
           
           #if installed:
           item = self.installedList.GetItem(index)
           item.SetTextColour(wx.BLUE)
           self.installedList.SetItem(item)

               
       self.installedList.SetColumnWidth(0, wx.LIST_AUTOSIZE)
       self.installedList.SetColumnWidth(1, wx.LIST_AUTOSIZE)
       #self.installedList.SetColumnWidth(2, wx.LIST_AUTOSIZE)

       self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onInstalledSelected,
                 self.installedList)

       return panelInstalled


   def _makeAvailablePanel(self):
       """Creates panel with for controlling installed dictionaries"""
       
       #
       # Boxes
       # 
       panelAvailable = wxPanel(self, -1)
       vboxAvailable = wxBoxSizer(wxVERTICAL)
       vboxAvailableBox = wxBoxSizer(wxVERTICAL)
       sbSizerAvailable = wxStaticBoxSizer(\
          wxStaticBox(panelAvailable, -1, 
                      _("Available Dictionaries")),
          wxVERTICAL)
       
       #
       # Installed list
       #
       idAvailList = wx.NewId()
       self.availableList = DictListCtrl(panelAvailable, idAvailList,
                                         style=wx.LC_REPORT)# | wx.BORDER_SUNKEN)
       vboxAvailableBox.Add(self.availableList, 1, wxALL | wxEXPAND, 1)


       # Horizontal box for buttons
       hboxButtons = wxBoxSizer(wxHORIZONTAL)
       
       #
       # "Install" button
       #
       idInstall = wx.NewId()
       self.buttonInstall = wxButton(panelAvailable, idInstall, _("Install"))
       hboxButtons.Add(self.buttonInstall, 0, wxALL | wxALIGN_RIGHT, 2)

       #
       # "Update" button
       #
       idUpdate = wx.NewId()
       self.buttonUpdate = wxButton(panelAvailable, idInstall, _("Update List"))
       hboxButtons.Add(self.buttonUpdate, 0, wxALL | wxALIGN_RIGHT, 2)

       vboxAvailableBox.Add(hboxButtons, 0, wxALL | wxALIGN_RIGHT, 1)
       
       sbSizerAvailable.Add(vboxAvailableBox, 1, wxALL | wxEXPAND, 0)
       panelAvailable.SetSizer(vboxAvailable)
       vboxAvailable.Fit(panelAvailable)
       
       vboxAvailable.Add(sbSizerAvailable, 1, wxALL | wxEXPAND, 0)
       
       #
       # Make columns
       #
       self.availableList.InsertColumn(0, _("Dictionary Name"))
       self.availableList.InsertColumn(1, _("Size Of Download"))
       
       size = 100
       
       dictNames = self.allDictionaries.keys()
       dictNames.sort()
       
       print dictNames
       
       for dictionary in dictNames:
           installed = self.allDictionaries.get(dictionary)
           
           index = self.availableList.InsertStringItem(0, dictionary)
           
           sizeString = "%d KB"
           
           #if not installed:
           #    sizeString = "%d KB (to download)"
               
           self.availableList.SetStringItem(index, 1,
                                            sizeString % size)
           size += 100
           

           #status = None
           #if installed:
           #    status = "Installed"
           #else:
           #    status = "Not installed"
         
           #self.availableList.SetStringItem(index, 2, status)
           self.availableList.SetItemData(index, index+1)
           
           #if installed:
           #    item = self.availableList.GetItem(index)
           #    item.SetTextColour(wx.BLUE)
           #    self.availableList.SetItem(item)

               
       self.availableList.SetColumnWidth(0, wx.LIST_AUTOSIZE)
       self.availableList.SetColumnWidth(1, 180)
       #self.availableList.SetColumnWidth(2, wx.LIST_AUTOSIZE)

       self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onAvailableSelected,
                 self.availableList)

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
                      _("Information")),
          wxVERTICAL)

       grid = wxFlexGridSizer(3, 2, 1, 1)
       
       self.labelName = wxStaticText(panelInfo, -1, "")
       self.labelVersion = wxStaticText(panelInfo, -1, "")
       self.labelFormat = wxStaticText(panelInfo, -1, "")
       self.labelAuthor = wxStaticText(panelInfo, -1, "")
       self.labelSize = wxStaticText(panelInfo, -1, "")
       
       self.textAbout = wxTextCtrl(panelInfo, -1, size=(-1, 100),
                                   style=wxTE_MULTILINE | wxTE_READONLY)
       
       grid.Add(wxStaticText(panelInfo, -1, _("Name: ")),
                0, wxALL)
       grid.Add(self.labelName, 0, wxALL)
       
       grid.Add(wxStaticText(panelInfo, -1, _("Version: ")),
                0, wxALL)
       grid.Add(self.labelVersion, 0, wxALL)
       
       grid.Add(wxStaticText(panelInfo, -1, _("Author: ")),
                0, wxALL)
       grid.Add(self.labelAuthor, 0, wxALL)

       vboxInfoBox.Add(grid, 1, wxALL | wxEXPAND, 1)
       vboxInfoBox.Add(self.textAbout, 0, wxALL | wxEXPAND, 1)
       
       sbSizerInfo.Add(vboxInfoBox, 1, wxALL | wxEXPAND, 0)
       
       vboxInfo.Add(sbSizerInfo, 1, wxALL | wxEXPAND, 0)

       panelInfo.SetSizer(vboxInfo)
       vboxInfo.Fit(panelInfo)

       return panelInfo
       

   def GetListCtrl(self):
        return self.list


   def onInstalledSelected(self, event):
      #plugin = self.app.config.plugins[event.GetString()]
      self.currentItem = event.m_itemIndex

      print self.installedList.GetItemText(self.currentItem)
      
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

      self.currentItem = event.m_itemIndex
      print self.availableList.GetItemText(self.currentItem)
      

   def onInstall(self, event):
       """Install button pressed"""
       
       from installer import Installer # FIXME: bug with imports
       installer = Installer(self.app.config.window, self.app.config)
       installer.showGUI()
       
       if self.app.config.window.lastInstalledDictName != None:
           self.pluginList.Append(self.app.config.window.lastInstalledDictName)
           self.app.config.window.lastInstalledDictName = None


   def onRemove(self, event):
       """Remove button pressed"""
       
       self.app.window.onCloseDict(None)
       item = self.pluginList.GetStringSelection()
       pos = self.pluginList.GetSelection()
       
       if item in self.app.config.plugins.keys():
           # This is a plugin
           pluginDirPath = os.path.join(info.LOCAL_HOME,
                                        info.__DICT_DIR,
                                        info.__PLUGIN_DICT_DIR,
                                        self.app.config.plugins[item].dir)
           if os.path.exists(pluginDirPath):
               try:
                   rmtree(pluginDirPath)
               except:
                   self.app.window.SetStatusText(_("Error removing \"%s\"") % item)
                   errDialog()
                   printError()
                   return
           elif os.path.exists(os.path.join(info.GLOBAL_HOME,
                                            info.__DICT_DIR,
                                            info.__PLUGIN_DICT_DIR,
                                            self.app.config.plugins[item].dir)):
               try:
                   rmtree(os.path.join(info.GLOBAL_HOME,
                                       info.__DICT_DIR,
                                       info.__PLUGIN_DICT_DIR,
                                       self.app.config.plugins[item].dir))
               except:
                   self.app.window.SetStatusText(_("Error removing \"%s\"") % item)
                   errDialog()
                   printError()
                   return
          
           del self.app.config.plugins[item]
           
       elif item in self.app.config.registers.keys():
           # This is a register
           if self.app.config.registers[item][1] != "Dict":
               if os.path.exists(os.path.join(uhome, "register", item+".hash")):
                   try:
                       os.remove(os.path.join(uhome, "register", item+".hash"))
                   except:
                       self.app.window.SetStatusText(_("Error while deleting \"%s\"") \
                                                     % (item+".hash"))
                       return
               elif os.path.exists(os.path.join(home, "register",
                                                item+".hash")):
                   try:
                       os.remove(os.path.join(home, "register", item+".hash"))
                   except:
                       self.app.window.SetStatusText(_("Error while deleting \"%s\"") \
                                                     % (item+".hash"))
                   return
               
           del self.app.config.registers[item]
           
       for list in self.app.config.groups.values():
           names = group.filesToNames(list, self.app.config)
           if item in names:
               list.pop(names.index(item))
               
       del self.app.config.ids[item]
       self.pluginList.Delete(pos)
       
       parent = self.GetParent()
       parent.menuDict.Delete(parent.menuDict.FindItem(item))
       self.labelName.SetLabel("")
       self.labelVersion.SetLabel("")
       self.labelAuthor.SetLabel("")
       self.labelFormat.SetLabel("")
       self.labelSize.SetLabel("")
       self.textAbout.Clear()
       

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

