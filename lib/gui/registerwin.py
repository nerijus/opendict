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
# Module: gui.registerwin

from wxPython.wx import *
import os

from info import home, uhome

_ = wxGetTranslation

class FileRegistryWindow(wxFrame):

   def __init__(self, parent, id, title, pos=wxDefaultPosition,
                size=wxDefaultSize, style=wxDEFAULT_FRAME_STYLE):
      wxFrame.__init__(self, parent, id, title, pos, size, style)

      self.app = wxGetApp()

      vboxMain = wxBoxSizer(wxVERTICAL)
      
      self.types = {}
      self.types['dwa'] = "Slowo"
      self.types['mova'] = "Mova"
      self.types['tmx'] = "TMX"
      self.types['dz'] = "DICT"

      self.fileList = wxListBox(self, 190,
                                wxPoint(-1, -1),
                                wxSize(-1, -1),
                                self.app.config.registers.keys(),
                                wxLB_SINGLE | wxSUNKEN_BORDER)

      vboxMain.Add(self.fileList, 1, wxALL | wxEXPAND, 1)

      vboxInfo = wxBoxSizer(wxVERTICAL)

      if len(self.app.config.registers.keys()) > 0:
         self.fileList.SetSelection(0)
         name = self.fileList.GetStringSelection()
         item = self.app.config.registers[name]
      else:
         # There's no registered dictionaries
         name = ""
         item = []
         item.extend(["", "", ""])

      self.labelName = wxStaticText(self, -1, _("Name: %s") % name)
      vboxInfo.Add(self.labelName, 0, wxALL, 0)

      self.labelPath = wxStaticText(self, -1, _("Path: %s") % item[0])
      vboxInfo.Add(self.labelPath, 0, wxALL, 0)

      self.labelFormat = wxStaticText(self, -1, _("Format: %s") % item[1])
      vboxInfo.Add(self.labelFormat, 0, wxALL, 0)

      self.labelEnc = wxStaticText(self, -1, _("Encoding: %s") % item[2])
      vboxInfo.Add(self.labelEnc, 0, wxALL, 0)

      vboxMain.Add(vboxInfo, 0, wxALL | wxEXPAND, 10)

      hboxButtons = wxBoxSizer(wxHORIZONTAL)

      self.buttonInstall = wxButton(self, 191, _("Add new..."))
      # FIXME: Needs to be rewritten
      #hboxButtons.Add(self.buttonInstall, 1, wxALL | wxEXPAND, 1)

      self.buttonRemove = wxButton(self, 192, _("Remove selected"))
      hboxButtons.Add(self.buttonRemove, 1, wxALL | wxEXPAND, 1)

      self.buttonClose = wxButton(self, 193, _("Close"))
      hboxButtons.Add(self.buttonClose, 1, wxALL | wxEXPAND, 1)

      vboxMain.Add(hboxButtons, 0, wxALL | wxEXPAND, 2)

      self.SetSizer(vboxMain)
      self.Fit()

      EVT_LISTBOX(self, 190, self.onFileSelected)
      EVT_BUTTON(self, 191, self.onInstall)
      EVT_BUTTON(self, 192, self.onRemove)
      EVT_BUTTON(self, 193, self.onClose)

   def onFileSelected(self, event):
      print event.GetString()
      info = self.app.config.registers[event.GetString()]

      self.labelName.SetLabel(_("Name: %s") % event.GetString())
      self.labelPath.SetLabel(_("Path: %s") % info[0])
      self.labelFormat.SetLabel(_("Format: %s") % self.types[info[1]])
      self.labelEnc.SetLabel(_("Encoding: %s") % info[2])

   def onInstall(self, event):
      self.fileList.Append(self.app.window.onAddFromFile(None))

   def onRemove(self, event):
      self.app.window.onCloseDict(None)
      pos = self.fileList.GetSelection()
      item = self.fileList.GetStringSelection()

      if item == "":
          return

      print "Name: %s, Pos: %s [%s]" % (item, pos,
                                        self.app.config.registers[item][0])
      self.fileList.Delete(pos)
      parent = self.GetParent()
      print parent.menuDict.FindItem(item)
      parent.menuDict.Delete(parent.menuDict.FindItem(item))

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

      del self.app.config.ids[item]
      del self.app.config.registers[item]

      for list in self.app.config.groups.values():
         if item in list:
            list.remove(item)

      self.labelName.SetLabel(_("Name: %s") % "")
      self.labelPath.SetLabel(_("Path: %s") % "")
      self.labelFormat.SetLabel(_("Format: %s") % "")
      self.labelEnc.SetLabel(_("Encoding: %s") % "")


   def onClose(self, event):
      self.Destroy()
