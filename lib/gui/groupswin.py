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
# Module: gui.groupswin

from wxPython.wx import *
import os

from info import home
import group

_ = wxGetTranslation

class GroupsWindow(wxFrame):

   class GroupEditWindow(wxFrame):

      def __init__(self, parent, id, title, pos=wxDefaultPosition,
                size=wxDefaultSize, style=wxDEFAULT_FRAME_STYLE):
         wxFrame.__init__(self, parent, id, title, pos, size, style)

         self.app = wxGetApp()

         vboxMain = wxBoxSizer(wxVERTICAL)
         hboxMain = wxBoxSizer(wxHORIZONTAL)
         vboxCurrent = wxBoxSizer(wxVERTICAL)
         vboxAvail = wxBoxSizer(wxVERTICAL)
         vboxDButtons = wxBoxSizer(wxVERTICAL)
         hboxButtons = wxBoxSizer(wxHORIZONTAL)

         vboxCurrent.Add(wxStaticText(self, -1, _("Current dictionaries")),
                         0, wxALL, 2)

         bmp = wxBitmap(os.path.join(home, "pixmaps", "left.xpm"),
                        wxBITMAP_TYPE_XPM)
         self.buttonAdd = wxBitmapButton(self, 195, bmp, (18, 18))
         self.buttonAdd.SetToolTipString(_("Add selected to the group"))
         vboxDButtons.Add(self.buttonAdd, 1, wxALL, 1)

         bmp = wxBitmap(os.path.join(home, "pixmaps", "right.xpm"),
                        wxBITMAP_TYPE_XPM)
         self.buttonRm = wxBitmapButton(self, 196, bmp, (18, 18))
         self.buttonRm.SetToolTipString(_("Remove selected from the group"))
         vboxDButtons.Add(self.buttonRm, 1, wxALL, 1)

         name = self.GetParent().curName
         self.clist = group.filesToNames(self.app.config.groups[name],
                                         self.app.config)


         self.curList = wxListBox(self, 197,
                                  wxPoint(-1, -1),
                                  wxSize(-1, -1),
                                  self.clist,
                                  wxLB_SINGLE | wxSUNKEN_BORDER)
         vboxCurrent.Add(self.curList, 1, wxALL | wxEXPAND, 2)

         vboxAvail.Add(wxStaticText(self, -1, _("Available dictionaries")),
                       0, wxALL, 2)

         # List of available dictionaries has only dictionaries
         # which are not included in the list of current dictionaries
         self.alist = []
         for item in self.app.config.plugins.keys():
            if not item in self.clist:
               self.alist.append(item)
         for item in self.app.config.registers.keys():
            if not item in self.clist:
               self.alist.append(item)

         self.availList = wxListBox(self, 198,
                                    wxPoint(-1, -1),
                                    wxSize(-1, -1),
                                    self.alist,
                                    wxLB_SINGLE | wxSUNKEN_BORDER)
         vboxAvail.Add(self.availList, 1, wxALL | wxEXPAND, 2)

         hboxMain.Add(vboxCurrent, 1, wxALL | wxEXPAND, 0)
         hboxMain.Add(vboxDButtons, 0, wxALL | wxCENTER, 0)
         hboxMain.Add(vboxAvail, 1, wxALL | wxEXPAND, 0)
         vboxMain.Add(hboxMain, 1, wxALL | wxEXPAND, 0)

         self.buttonClose = wxButton(self, 194, _("OK"))
         hboxButtons.Add(self.buttonClose, 0, wxALL, 1)

         self.buttonClose = wxButton(self, 199, _("Cancel"))
         hboxButtons.Add(self.buttonClose, 0, wxALL, 1)

         vboxMain.Add(hboxButtons, 0, wxALL | wxCENTER, 0)

         self.SetSizer(vboxMain)

         EVT_BUTTON(self, 195, self.onAdd)
         EVT_BUTTON(self, 196, self.onRemove)
         EVT_BUTTON(self, 194, self.onOK)
         EVT_BUTTON(self, 199, self.onClose)

      def onAdd(self, event):

         pos = self.availList.GetSelection()
         item = self.availList.GetStringSelection()

         if item == "":
            return
         print "Adding", item

         self.curList.Append(item)
         self.availList.Delete(pos)

      def onRemove(self, event):
         pos = self.curList.GetSelection()
         item = self.curList.GetStringSelection()

         if item == "":
            return
         print "Removing", item

         self.availList.Append(item)
         self.curList.Delete(pos)

      def onOK(self, event):
         names = []

	 # Get group dicts list
         for i in range(self.curList.Number()):
            names.append(self.curList.GetString(i))

	 

         parent = self.GetParent()
	 # Associate group name with list
         self.app.config.groups[parent.curName] = group.namesToFiles(names, self.app.config)
         print parent.curName, self.app.config.groups[parent.curName]


	 # Update dict number label
         pos = parent.groupsList.FindItem(0, parent.curName)
         parent.groupsList.SetStringItem(pos, 1,
                                         str(len(self.app.config.groups[parent.curName])))

         self.Destroy()

      def onClose(self, event):
         self.Destroy()


   def __init__(self, parent, id, title, pos=wxDefaultPosition,
                size=wxDefaultSize, style=wxDEFAULT_FRAME_STYLE):
      wxFrame.__init__(self, parent, id, title, pos, size, style)

      self.app = wxGetApp()

      vboxMain = wxBoxSizer(wxVERTICAL)

      self.groupsList = wxListCtrl(self, 190,
                                  wxPoint(-1, -1),
                                  wxSize(-1, -1),
                                  wxLC_REPORT | wxSUNKEN_BORDER)

      self.groupsList.InsertColumn(0, _("Group"))
      self.groupsList.InsertColumn(1, _("Dictionaries"))

      self.groupsList.SetColumnWidth(0, 245)
      self.groupsList.SetColumnWidth(1, 80)

      for i in range(len(self.app.config.groups.keys())):
         name, items = self.app.config.groups.items()[i]
         print name, len(items), items
         self.groupsList.InsertStringItem(i, name)
         self.groupsList.SetStringItem(i, 1, str(len(items)))

      vboxMain.Add(self.groupsList, 1, wxALL | wxEXPAND, 1)

      hboxButtons = wxBoxSizer(wxHORIZONTAL)

      self.buttonInstall = wxButton(self, 1301, _("Add"))
      hboxButtons.Add(self.buttonInstall, 1, wxALL | wxEXPAND, 1)

      self.buttonClose = wxButton(self, 1302, _("Edit"))
      hboxButtons.Add(self.buttonClose, 1, wxALL | wxEXPAND, 1)

      self.buttonRemove = wxButton(self, 1303, _("Remove"))
      hboxButtons.Add(self.buttonRemove, 1, wxALL | wxEXPAND, 1)

      self.buttonClose = wxButton(self, 1304, _("Close"))
      hboxButtons.Add(self.buttonClose, 1, wxALL | wxEXPAND, 1)

      vboxMain.Add(hboxButtons, 0, wxALL | wxEXPAND, 2)

      self.SetSizer(vboxMain)

      EVT_BUTTON(self, 1301, self.onAdd)
      EVT_BUTTON(self, 1302, self.onEdit)
      EVT_BUTTON(self, 1303, self.onRemove)
      EVT_BUTTON(self, 1304, self.onClose)

   def onAdd(self, event):
      dialog = wxTextEntryDialog(self, _("Enter group name"),
                            _("New Group"), "")
      dialog.SetValue(_("New group"))
      if dialog.ShowModal() == wxID_OK:
        name = dialog.GetValue()
        if name == "":
           pass
        if self.app.config.groups.has_key(name):
           pass

        pos = self.groupsList.GetItemCount()

        self.groupsList.InsertStringItem(pos, name)
        self.groupsList.SetStringItem(pos, 1, "0")

        self.app.config.groups[name] = []

        self.app.config.ids[name] = self.app.config.groupMenuIds
        self.app.config.groupMenuIds += 1

        item = wxMenuItem(self.app.config.window.menuDict,
                          self.app.config.ids[name],
                          name)

	EVT_MENU(self.app.config.window, self.app.config.ids[name],
                 self.app.config.window.onDefault)

        # wxPython 2.4.1.2 has a bug, menu items with bitmaps do not catch
        # events.
        #if wx.__version__ != "2.4.1.2":
        #   item.SetBitmap(wxBitmap(os.path.join(home, "pixmaps", "group.xpm"),
        #                           wxBITMAP_TYPE_XPM))

        self.app.config.window.menuDict.InsertItem(self.app.config.window.menuDict.GetMenuItemCount()-2, item)

      dialog.Destroy()

   def onEdit(self, event):
      item = self.groupsList.GetNextItem(-1,
                                         wxLIST_NEXT_ALL,
                                         wxLIST_STATE_SELECTED)

      if item == -1:
         return

      self.curName = self.groupsList.GetItemText(item)
      editWindow = self.GroupEditWindow(self, -1,
                                        _("Group \"%s\"") % self.curName,
                                        size=(450, 300),
                                        style=wxDEFAULT_FRAME_STYLE)
      editWindow.CentreOnScreen()
      editWindow.Show(True)

   def onRemove(self, event):
      item = -1
      while 1:
         item = self.groupsList.GetNextItem(item,
                                            wxLIST_NEXT_ALL,
                                            wxLIST_STATE_SELECTED)
         if item == -1:
            break

         print item, "is selected"
         name = self.groupsList.GetItemText(item)
         self.groupsList.DeleteItem(item)

         parent = self.GetParent()
         parent.menuDict.Delete(parent.menuDict.FindItem(name))

         del self.app.config.ids[name]
         del self.app.config.groups[name]
         print name, "deleted"

   def onClose(self, event):
      self.Destroy()
