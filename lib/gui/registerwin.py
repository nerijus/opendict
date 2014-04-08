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
# Module: gui.registerwin

import wx
import os

from info import home, uhome

_ = wx.GetTranslation

class FileRegistryWindow(wx.Frame):

   def __init__(self, parent, id, title, pos=wx.DefaultPosition,
                size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE):
      wx.Frame.__init__(self, parent, id, title, pos, size, style)

      self.app = wx.GetApp()

      vboxMain = wx.BoxSizer(wx.VERTICAL)
      
      self.types = {}
      self.types['dwa'] = "Slowo"
      self.types['mova'] = "Mova"
      self.types['tmx'] = "TMX"
      self.types['dz'] = "DICT"

      self.fileList = wx.ListBox(self, 190,
                                wx.Point(-1, -1),
                                wx.Size(-1, -1),
                                self.app.config.registers.keys(),
                                wx.LB_SINGLE | wx.SUNKEN_BORDER)

      vboxMain.Add(self.fileList, 1, wx.ALL | wx.EXPAND, 1)

      vboxInfo = wx.BoxSizer(wx.VERTICAL)

      if len(self.app.config.registers.keys()) > 0:
         self.fileList.SetSelection(0)
         name = self.fileList.GetStringSelection()
         item = self.app.config.registers[name]
      else:
         # There's no registered dictionaries
         name = ""
         item = []
         item.extend(["", "", ""])

      self.labelName = wx.StaticText(self, -1, _("Name: %s") % name)
      vboxInfo.Add(self.labelName, 0, wx.ALL, 0)

      self.labelPath = wx.StaticText(self, -1, _("Path: %s") % item[0])
      vboxInfo.Add(self.labelPath, 0, wx.ALL, 0)

      self.labelFormat = wx.StaticText(self, -1, _("Format: %s") % item[1])
      vboxInfo.Add(self.labelFormat, 0, wx.ALL, 0)

      self.labelEnc = wx.StaticText(self, -1, _("Encoding: %s") % item[2])
      vboxInfo.Add(self.labelEnc, 0, wx.ALL, 0)

      vboxMain.Add(vboxInfo, 0, wx.ALL | wx.EXPAND, 10)

      hboxButtons = wx.BoxSizer(wx.HORIZONTAL)

      self.buttonInstall = wx.Button(self, 191, _("Add new..."))
      # FIXME: Needs to be rewritten
      #hboxButtons.Add(self.buttonInstall, 1, wx.ALL | wx.EXPAND, 1)

      self.buttonRemove = wx.Button(self, 192, _("Remove selected"))
      hboxButtons.Add(self.buttonRemove, 1, wx.ALL | wx.EXPAND, 1)

      self.buttonClose = wx.Button(self, 193, _("Close"))
      hboxButtons.Add(self.buttonClose, 1, wx.ALL | wx.EXPAND, 1)

      vboxMain.Add(hboxButtons, 0, wx.ALL | wx.EXPAND, 2)

      self.SetSizer(vboxMain)
      self.Fit()

      wx.EVT_LISTBOX(self, 190, self.onFileSelected)
      wx.EVT_BUTTON(self, 191, self.onInstall)
      wx.EVT_BUTTON(self, 192, self.onRemove)
      wx.EVT_BUTTON(self, 193, self.onClose)

   def onFileSelected(self, event):
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

      self.fileList.Delete(pos)
      parent = self.GetParent()
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
