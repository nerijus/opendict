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
# Module: gui.prefswin

from wxPython.wx import *

from misc import encodings, savePrefs

_ = wxGetTranslation

class PrefsWindow(wxFrame):

   def __init__(self, parent, id, title, pos=wxDefaultPosition,
                size=wxDefaultSize, style=wxDEFAULT_FRAME_STYLE):
      wxFrame.__init__(self, parent, id, title, pos, size, style)

      self.app = wxGetApp()

      vboxMain = wxBoxSizer(wxVERTICAL)
      hboxDict = wxBoxSizer(wxHORIZONTAL)
      hboxEnc = wxBoxSizer(wxHORIZONTAL)
      hboxButtons = wxBoxSizer(wxHORIZONTAL)

      hboxDict.Add(wxStaticText(self, -1, _("Dictionary to load at start: ")),
                   0, wxALL | wxALIGN_CENTER_VERTICAL, 0)

      list = []
      list.extend(self.app.config.plugins.keys())
      list.extend(self.app.config.registers.keys())
      list.extend(self.app.config.groups.keys())
      list.insert(0, "")
      self.dictChooser = wxComboBox(self, 1100, self.app.config.dict,
                                   wxPoint(-1, -1),
                                   wxSize(-1, -1), list, wxTE_READONLY)
      hboxDict.Add(self.dictChooser, 1, wxALL | wxEXPAND, 0)
      vboxMain.Add(hboxDict, 0, wxALL | wxEXPAND, 2)

      hboxEnc.Add(wxStaticText(self, -1, _("Default encoding: ")),
                   0, wxALL | wxALIGN_CENTER_VERTICAL, 0)
      self.encChooser = wxComboBox(self, 1108,
                                  encodings.keys()[encodings.values().index(self.app.config.defaultEnc)],
                                  wxPoint(-1, -1),
                                  wxSize(-1, -1), encodings.keys(),
                                  wxTE_READONLY)
      hboxEnc.Add(self.encChooser, 1, wxALL | wxEXPAND, 0)
      vboxMain.Add(hboxEnc, 0, wxALL | wxEXPAND, 2)

      self.winSize = wxCheckBox(self, 1101, _("Save window size"))
      self.winSize.SetValue(self.app.config.saveWinSize)
      vboxMain.Add(self.winSize, 0, wxALL, 0)

      self.winPos = wxCheckBox(self, 1102, _("Save window position"))
      self.winPos.SetValue(self.app.config.saveWinPos)
      vboxMain.Add(self.winPos, 0, wxALL, 0)

      self.sashPos = wxCheckBox(self, 1103, _("Save sash position"))
      self.sashPos.SetValue(self.app.config.saveSashPos)
      vboxMain.Add(self.sashPos, 0, wxALL, 0)

      self.listReg = wxCheckBox(self, 1106, _("Use word list with files"))
      self.listReg.SetValue(self.app.config.useListWithRegs)
      vboxMain.Add(self.listReg, 0, wxALL, 0)

      self.listGroup = wxCheckBox(self, 1107, _("Use word list with dictionary groups"))
      self.listGroup.SetValue(self.app.config.useListWithGroups)
      vboxMain.Add(self.listGroup, 0, wxALL, 0)

      vboxMain.Add(wxStaticLine(self, -1), 0, wxALL | wxEXPAND, 5)

      self.buttonSave = wxButton(self, 1108, _("Save"))
      hboxButtons.Add(self.buttonSave, 1, wxALL | wxEXPAND, 1)
      
      self.buttonOK = wxButton(self, 1104, _("OK"))
      hboxButtons.Add(self.buttonOK, 1, wxALL | wxEXPAND, 1)

      self.buttonCancel = wxButton(self, 1105, _("Cancel"))
      hboxButtons.Add(self.buttonCancel, 1, wxALL | wxEXPAND, 1)

      vboxMain.Add(hboxButtons, 0, wxALL | wxEXPAND, 2)

      self.SetSizer(vboxMain)
      self.Fit()
      self.SetSize((400, -1))

      EVT_CHECKBOX(self, 1101, self.onSaveWinSizeClicked)
      EVT_CHECKBOX(self, 1102, self.onSaveWinPosClicked)
      EVT_CHECKBOX(self, 1103, self.onSaveSashPosClicked)
      EVT_CHECKBOX(self, 1106, self.onUseListRegClicked)
      EVT_CHECKBOX(self, 1107, self.onUseListGroupClicked)
      EVT_BUTTON(self, 1108, self.onSave)
      EVT_BUTTON(self, 1104, self.onOK)
      EVT_BUTTON(self, 1105, self.onCancel)

   def onSaveWinSizeClicked(self, event):
      print "WinSize:", event.Checked()
      if event.Checked() == 1:
         self.app.config.winSize = self.GetParent().GetSize()
         self.app.config.saveWinSize = 1
      else:
         self.app.config.saveWinSize = 0

   def onSaveWinPosClicked(self, event):
      print "WinPos:", event.Checked()
      if event.Checked() == 1:
         self.app.config.winPos = self.GetParent().GetPosition()
         self.app.config.saveWinPos = 1
      else:
         self.app.config.saveWinPos = 0

   def onSaveSashPosClicked(self, event):
      print "Sash:", event.Checked()
      if event.Checked() == 1:
         self.app.config.sashPos = self.GetParent().splitter.GetSashPosition()
         self.app.config.saveSashPos = 1
      else:
         self.app.config.saveSashPos = 0

   def onUseListRegClicked(self, event):
      self.app.config.useListWithRegs = event.Checked()

   def onUseListGroupClicked(self, event):
      self.app.config.useListWithGroups = event.Checked()
      
   def onSave(self, event):
       savePrefs(self.app.window)
       self.app.config.writeConfigFile()
       
   def onOK(self, event):
      self.app.config.dict = self.dictChooser.GetValue()

      self.app.config.defaultEnc = encodings[self.encChooser.GetValue()]
      if self.app.window.dict == None:
         self.app.window.checkEncMenuItem(self.app.config.defaultEnc)

      self.app.config.saveWinSize = self.winSize.GetValue()
      self.app.config.saveWinPos = self.winPos.GetValue()
      self.app.config.saveSashPos = self.sashPos.GetValue()
      self.app.config.useListWithRegs = self.listReg.GetValue()
      self.app.config.useListWithGroups = self.listGroup.GetValue()
      self.Destroy()

   def onCancel(self, event):
      self.Destroy()
