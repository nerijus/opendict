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
      
      grid = wxFlexGridSizer(4, 2, 1, 1)
      
      #self.dictMap = {}
      #for name in self.app.config.plugins.keys():
      #    self.dictMap[name] = "plugin"
      #for name in self.app.config.registers.keys():
      #    self.dictMap[name] = "register"


      installedDictionaries = self.app.dictionaries.keys()
      #print self.app.dictionaries
      #for d in self.app.dictionaries:
         #print d
      #   installedDictionaries.append(d.getName())
      
      #allDicts = self.app.config.plugins.keys() + \
      #           self.app.config.registers.keys()
      #allDicts.sort()

      #self.dictListCtrl = wxListBox(self, 160,
      #                              wxPoint(-1, -1),
      #                              wxSize(-1, -1),
      #                              installedDictinaries,
      #                              wxLB_SINGLE | wxSUNKEN_BORDER)
      idDictList = wx.NewId()
      
      self.dictListCtrl = DictListCtrl(self, idDictList,
                                       style=wx.LC_REPORT)
                                       #| wx.LC_SORT_ASCENDING
                                       #| wx.LC_EDIT_LABELS)


      #self.dictListCtrl.InsertColumn(0, "Name")
      #self.dictListCtrl.InsertColumn(1, "Size")

      #
      # Make columns
      #
      info = wx.ListItem()
      info.m_mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE \
      #              | wx.LIST_MASK_FORMAT
      info.m_image = -1
      info.m_format = 0
      info.m_text = "Dictionary name"
      self.dictListCtrl.InsertColumnInfo(0, info)

      info.m_image = -1
      info.m_format = 0
      info.m_text = "Size"
      self.dictListCtrl.InsertColumnInfo(1, info)

      info.m_image = -1
      info.m_format = 0
      info.m_text = "Status"
      self.dictListCtrl.InsertColumnInfo(2, info)
      
      #
      # TODO: neveikia si vieta
      # 
      #index = 0
      for dictionary in installedDictionaries:
         #print index
         #print dictionary
         index = self.dictListCtrl.InsertStringItem(0, dictionary)
         self.dictListCtrl.SetStringItem(index, 1, "1243 KB")
         self.dictListCtrl.SetStringItem(index, 2, "Installed")
         self.dictListCtrl.SetItemData(index, index+1)

         item = self.dictListCtrl.GetItem(index)
         #print item
         item.SetTextColour(wx.BLUE)
         self.dictListCtrl.SetItem(item)
         #index += 1

      #print dir(self.dictListCtrl)
      
      #self.itemDataMap = {0: ('dfsdf', 'sdfsf')}
      #listmix.ColumnSorterMixin.__init__(self, 2)

      self.dictListCtrl.SetColumnWidth(0, wx.LIST_AUTOSIZE)
      self.dictListCtrl.SetColumnWidth(1, wx.LIST_AUTOSIZE)
      self.dictListCtrl.SetColumnWidth(2, wx.LIST_AUTOSIZE)

      vboxMain.Add(self.dictListCtrl, 1, wxALL | wxEXPAND, 3)

      vboxInfo = wxBoxSizer(wxVERTICAL)
      
      self.labelName = wxStaticText(self, -1, "")
      self.labelVersion = wxStaticText(self, -1, "")
      self.labelFormat = wxStaticText(self, -1, "")
      self.labelAuthor = wxStaticText(self, -1, "")
      self.labelSize = wxStaticText(self, -1, "")
      
      # Adding description into separate static box
      self.panelDesc = wxPanel(self, -1)
      sbSizerDesc = wxStaticBoxSizer(wxStaticBox(self.panelDesc, -1, 
                                                 _("Description")),
                                     wxVERTICAL)

      self.textAbout = wxTextCtrl(self.panelDesc, -1, size=(-1, 60),
                       style=wxTE_MULTILINE | wxTE_READONLY)
      sbSizerDesc.Add(self.textAbout, 1, wxALL | wxEXPAND, 0)
      self.panelDesc.SetSizer(sbSizerDesc)
      self.panelDesc.SetAutoLayout(true)
      sbSizerDesc.Fit(self.panelDesc)

##       if len(allDicts) > 0:
##          self.pluginList.SetSelection(0)
         
##          # Simulating event
##          simEvent = wxCommandEvent()
##          simEvent.SetString(self.pluginList.GetStringSelection())
         
##          self.onPluginSelected(simEvent)
         
##          #if name in self.app.config.plugins.keys():
##          #    plugin = self.app.config.plugins[name]
##          #    version = plugin.version
##          #    format = "OpenDict plugin"
##          #    author = plugin.author
##          #    about = plugin.about
##          #else:
##          #    regFile = self.app.config.registers[name]
##          #    version = ""
##          #    format = misc.dictFormats[regFile[1]]
##          #    author = ""
##          #    about = ""
##       else:
##          # There's no installed plugins
##          name = ""
##          version = ""
##          format = ""
##          author = ""
##          about = ""
      
      grid.Add(wxStaticText(self, -1, _("Name: ")),
               0, wxALL)
      grid.Add(self.labelName, 0, wxALL)
      
      grid.Add(wxStaticText(self, -1, _("Version: ")),
               0, wxALL)
      grid.Add(self.labelVersion, 0, wxALL)
      
      grid.Add(wxStaticText(self, -1, _("Author: ")),
               0, wxALL)
      grid.Add(self.labelAuthor, 0, wxALL)
      
      grid.Add(wxStaticText(self, -1, _("Format: ")),
               0, wxALL)
      grid.Add(self.labelFormat, 0, wxALL)
      
      grid.Add(wxStaticText(self, -1, _("Size: ")),
               0, wxALL)
      grid.Add(self.labelSize, 0, wxALL)
      
      vboxInfo.Add(grid, 1, wxALL | wxEXPAND, 1)
      
      vboxInfo.Add(self.panelDesc, 1, wxALL | wxEXPAND, 1)
      #self.textAbout.WriteText(about)

      vboxMain.Add(vboxInfo, 0, wxALL | wxEXPAND, 10)

      hboxButtons = wxBoxSizer(wxHORIZONTAL)

      self.buttonInstall = wxButton(self, 161, _("Install new..."))
      hboxButtons.Add(self.buttonInstall, 1, wxALL | wxEXPAND, 1)

      self.buttonRemove = wxButton(self, 162, _("Remove selected"))
      hboxButtons.Add(self.buttonRemove, 1, wxALL | wxEXPAND, 1)

      self.buttonClose = wxButton(self, 163, _("Close"))
      hboxButtons.Add(self.buttonClose, 1, wxALL | wxEXPAND, 1)

      vboxMain.Add(hboxButtons, 0, wxALL | wxEXPAND, 2)

      self.SetSizer(vboxMain)
      #self.Fit()

      EVT_LISTBOX(self, 160, self.onPluginSelected)
      EVT_BUTTON(self, 161, self.onInstall)
      EVT_BUTTON(self, 162, self.onRemove)
      EVT_BUTTON(self, 163, self.onClose)


   def GetListCtrl(self):
        return self.list

   def onPluginSelected(self, event):
      #plugin = self.app.config.plugins[event.GetString()]
      name = event.GetString()
      size = -1
      
      #if self.dictMap[name] == "plugin":
      if name in self.app.config.plugins.keys():
             plugin = self.app.config.plugins[name]

             try:
                self.labelName.SetLabel(plugin.name.decode('UTF-8'))
             except Exception, e:
                print "ERROR Unable to set label '%s' (%s)" \
                      % (plugin.name, e)

             try:
                self.labelVersion.SetLabel(plugin.version.decode('UTF-8'))
             except Exception, e:
                print "ERROR: Unable to set label '%s' (%s)" \
                      % (plugin.version, e)

             self.labelFormat.SetLabel(_("OpenDict plugin"))
                
             try:
                self.labelAuthor.SetLabel(plugin.author.decode('UTF-8'))
             except Exception, e:
                print "ERROR: Unable to set label '%s' (%s)" \
                      % (plugin.author, e)
                
             self.textAbout.Clear()

             try:
                self.textAbout.WriteText(plugin.about.decode('UTF-8'))
             except Exception, e:
                print "ERROR: Unable to set label '%s' (%s)" \
                      % (plugin.about, e)
             
             path = self.app.config.plugins[name].dir

             pluginDirPath = os.path.join(info.LOCAL_HOME,
                                          info.__DICT_DIR,
                                          info.__PLUGIN_DICT_DIR,
                                          path)
             if os.path.exists(pluginDirPath):
                 size = misc.getDirSize(pluginDirPath,
                                        0, 0, 10)
             else:
                 size = misc.getDirSize(os.path.join(info.GLOBAL_HOME,
                                                     info.__DICT_DIR,
                                                     info.__PLUGIN_DICT_DIR,
                                                     path),
                                        0, 0, 10)
                 
      elif name in self.app.config.registers.keys():
             regFile = self.app.config.registers[name]
             self.labelName.SetLabel(name)
             self.labelVersion.SetLabel("--")
             self.labelFormat.SetLabel(misc.dictFormats[regFile[1]])
             self.labelAuthor.SetLabel("--")
             self.textAbout.Clear()
             
             size = misc.getFileSize(self.app.config.registers[name][0])
      else:
          print "onPluginSelected(): misunderstood"
      
      self.labelSize.SetLabel(str(size/1000.)+" KB")

   def onInstall(self, event):
      from installer import Installer # FIXME: bug with imports
      installer = Installer(self.app.config.window, self.app.config)
      installer.showGUI()
      
      if self.app.config.window.lastInstalledDictName != None:
          self.pluginList.Append(self.app.config.window.lastInstalledDictName)
          self.app.config.window.lastInstalledDictName = None

   def onRemove(self, event):
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
              elif os.path.exists(os.path.join(home, "register", item+".hash")):
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

