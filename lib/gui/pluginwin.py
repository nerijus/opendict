# OpenDict
# Copyright (c) 2003 Martynas Jocius <mjoc@akl.lt>
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
# Module: gui.pluginwin

from wxPython.wx import *
from shutil import rmtree
import os

from info import home, uhome
from misc import printError
from gui.errorwin import errDialog

import group
import misc

_ = wxGetTranslation

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
      
      allDicts = self.app.config.plugins.keys() + \
                 self.app.config.registers.keys()
      allDicts.sort()

      self.pluginList = wxListBox(self, 160,
                                  wxPoint(-1, -1),
                                  wxSize(-1, -1),
                                  allDicts,
                                  wxLB_SINGLE | wxSUNKEN_BORDER)

      vboxMain.Add(self.pluginList, 1, wxALL | wxEXPAND, 3)

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

      if len(allDicts) > 0:
         self.pluginList.SetSelection(0)
         
         # Simulating event
         simEvent = wxCommandEvent()
         simEvent.SetString(self.pluginList.GetStringSelection())
         
         self.onPluginSelected(simEvent)
         
         #if name in self.app.config.plugins.keys():
         #    plugin = self.app.config.plugins[name]
         #    version = plugin.version
         #    format = "OpenDict plugin"
         #    author = plugin.author
         #    about = plugin.about
         #else:
         #    regFile = self.app.config.registers[name]
         #    version = ""
         #    format = misc.dictFormats[regFile[1]]
         #    author = ""
         #    about = ""
      else:
         # There's no installed plugins
         name = ""
         version = ""
         format = ""
         author = ""
         about = ""
      
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
      self.Fit()

      EVT_LISTBOX(self, 160, self.onPluginSelected)
      EVT_BUTTON(self, 161, self.onInstall)
      EVT_BUTTON(self, 162, self.onRemove)
      EVT_BUTTON(self, 163, self.onClose)

   def onPluginSelected(self, event):
      #plugin = self.app.config.plugins[event.GetString()]
      name = event.GetString()
      size = -1
      
      #if self.dictMap[name] == "plugin":
      if name in self.app.config.plugins.keys():
             plugin = self.app.config.plugins[name]
             self.labelName.SetLabel(plugin.name)
             self.labelVersion.SetLabel(plugin.version)
             self.labelFormat.SetLabel(_("OpenDict plugin"))
             self.labelAuthor.SetLabel(plugin.author)
             self.textAbout.Clear()
             self.textAbout.WriteText(plugin.about)
             
             path = self.app.config.plugins[name].dir
             
             if os.path.exists(os.path.join(uhome, "plugins", path)):
                 size = misc.getDirSize(os.path.join(uhome, "plugins", path),
                                        0, 0, 10)
             else:
                 size = misc.getDirSize(os.path.join(home, "plugins", path),
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
          if os.path.exists(os.path.join(uhome, "plugins",
                                       self.app.config.plugins[item].dir)):
              try:
                  rmtree(os.path.join(uhome, "plugins",
                                  self.app.config.plugins[item].dir))
              except:
                  self.app.window.SetStatusText(_("Error removing \"%s\"") % item)
                  errDialog()
                  printError()
                  return
          elif os.path.exists(os.path.join(home, "plugins",
                                         self.app.config.plugins[item].dir)):
              try:
                  rmtree(os.path.join(home, "plugins",
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

