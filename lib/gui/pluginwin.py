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

_ = wxGetTranslation

class PluginManagerWindow(wxFrame):

   """Plugin Manager lets install, remove and view info
   about installed plugins"""

   def __init__(self, parent, id, title, pos=wxDefaultPosition,
                size=wxDefaultSize, style=wxDEFAULT_FRAME_STYLE):
      wxFrame.__init__(self, parent, id, title, pos, size, style)

      self.app = wxGetApp()

      vboxMain = wxBoxSizer(wxVERTICAL)

      self.pluginList = wxListBox(self, 160,
                                  wxPoint(-1, -1),
                                  wxSize(-1, -1),
                                  self.app.config.plugins.keys(),
                                  wxLB_SINGLE | wxSUNKEN_BORDER)

      vboxMain.Add(self.pluginList, 1, wxALL | wxEXPAND, 3)

      vboxInfo = wxBoxSizer(wxVERTICAL)

      if len(self.app.config.plugins.keys()) > 0:
         self.pluginList.SetSelection(0)
         name = self.pluginList.GetStringSelection()
         plugin = self.app.config.plugins[name]
         version = plugin.version
         author = plugin.author
         about = plugin.about
      else:
         # There's no installed plugins
         name = ""
         version = ""
         author = ""
         about = ""

      self.labelName = wxStaticText(self, -1, _("Name: %s") % name)
      vboxInfo.Add(self.labelName, 0, wxALL, 0)

      self.labelVersion = wxStaticText(self, -1, _("Version: %s") % version)
      vboxInfo.Add(self.labelVersion, 0, wxALL, 0)

      self.labelAuthor = wxStaticText(self, -1, _("Author: %s") % author)
      vboxInfo.Add(self.labelAuthor, 0, wxALL, 0)
      
      self.textAbout = wxTextCtrl(self, -1, size=(-1, 60),
                       style=wxTE_MULTILINE | wxTE_READONLY)

      vboxInfo.Add(self.textAbout, 1, wxALL | wxEXPAND, 1)
      self.textAbout.WriteText(about)

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
      print event.GetString()
      plugin = self.app.config.plugins[event.GetString()]

      self.labelName.SetLabel(_("Name: %s") % plugin.name)
      self.labelVersion.SetLabel(_("Version: %s") % plugin.version)
      self.labelAuthor.SetLabel(_("Author: %s") % plugin.author)
      self.textAbout.Clear()
      self.textAbout.WriteText(plugin.about)

   def onInstall(self, event):
      print "inst"
      dialog = wxFileDialog(self, _("Choose plugin file"), "", "",
                            "", wxOPEN|wxMULTIPLE)

      if dialog.ShowModal() == wxID_OK:
         name = self.app.installPlugin(self.app.config,
                                     dialog.GetPaths()[0])
         if name != "":
            self.pluginList.Append(name)

      dialog.Destroy()

   def onRemove(self, event):
      self.app.window.onCloseDict(None)
      item = self.pluginList.GetStringSelection()
      pos = self.pluginList.GetSelection()

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
            printError()
            return

      for list in self.app.config.groups.values():
         names = group.filesToNames(list, self.app.config)
         if item in names:
            list.pop(names.index(item))

      del self.app.config.ids[item]
      del self.app.config.plugins[item]
      self.pluginList.Delete(pos)

      parent = self.GetParent()
      parent.menuDict.Delete(parent.menuDict.FindItem(item))
      self.labelName.SetLabel(_("Name: %s") % "")
      self.labelVersion.SetLabel(_("Version: %s") % "")
      self.labelAuthor.SetLabel(_("Author: %s") % "")
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

