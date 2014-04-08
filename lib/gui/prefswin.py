#
# OpenDict
# Copyright (c) 2003-2006 Martynas Jocius <mjoc@akl.lt>
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

from lib.logger import systemLog, debugLog, DEBUG, INFO, WARNING, ERROR
from lib.misc import encodings
from lib import enc

_ = wxGetTranslation
PRON_COMMAND = "echo \"(SayText \\\"%s\\\")\" | festival"

class PrefsWindow(wxDialog):
   """Preferences dialog class"""


   def __init__(self, parent, id, title, pos=wxDefaultPosition,
                size=wxDefaultSize, style=wxDEFAULT_FRAME_STYLE):
      """Initialize preferences dialog window"""
      
      wxDialog.__init__(self, parent, id, title, pos, size, style)

      self.app = wxGetApp()

      vboxMain = wxBoxSizer(wxVERTICAL)
      hboxButtons = wxBoxSizer(wxHORIZONTAL)

      grid = wxFlexGridSizer(2, 2, 1, 1)

      grid.Add(wxStaticText(self, -1, _("Default dictionary: ")),
                   0, wxALIGN_CENTER_VERTICAL)

      dictNames = []
      for name, d in self.app.dictionaries.items():
          print name, d.getActive()
          if d.getActive():
              dictNames.append(name)
      dictNames.sort()
      dictNames.insert(0, "")

      try:
         map(enc.toWX, dictNames)
      except Exception, e:
         systemLog(ERROR, "Unable to decode titles to UTF-8 (%s)" % e)
      
      self.dictChooser = wxComboBox(self, 1100,
                                    enc.toWX(self.app.config.get('defaultDict')),
                                    wxPoint(-1, -1),
                                    wxSize(-1, -1), dictNames, wxTE_READONLY)
      grid.Add(self.dictChooser, 0, wxEXPAND)

      grid.Add(wxStaticText(self, -1, _("Default encoding: ")),
               0, wxALIGN_CENTER_VERTICAL)
      self.encChooser = wxComboBox(self, 1108,
                                  encodings.keys()[encodings.values().index(self.app.config.get('encoding'))],
                                  wxPoint(-1, -1),
                                  wxSize(-1, -1), encodings.keys(),
                                  wxTE_READONLY)
      grid.Add(self.encChooser, 0, wxEXPAND | wxALIGN_RIGHT)
      
      grid.AddGrowableCol(1)
      
      grid.Add(wxStaticText(self, -1, _("Default DICT server: ")),
                   0, wxALIGN_CENTER_VERTICAL)
      self.serverEntry = wxTextCtrl(self, -1,
                                    self.app.config.get('dictServer'))
      grid.Add(self.serverEntry, 0, wxEXPAND)
      
      grid.Add(wxStaticText(self, -1, _("Default DICT server port: ")),
                   0, wxALIGN_CENTER_VERTICAL)
      self.portEntry = wxTextCtrl(self, -1,
                                  self.app.config.get('dictServerPort'))
      grid.Add(self.portEntry, 0, wxEXPAND)
      
      vboxMain.Add(grid, 0, wxALL | wxEXPAND, 4)
      
      #
      # Pronunciation
      #
      panelPron = wxPanel(self, -1)
      sbSizerPron = wxStaticBoxSizer(wxStaticBox(panelPron, -1, 
                                                 _("Pronunciation")), 
                                     wxVERTICAL)
      panelPron.SetSizer(sbSizerPron)
      panelPron.SetAutoLayout(true)
      sbSizerPron.Fit(panelPron)
      vboxMain.Add(panelPron, 0, wxALL | wxEXPAND, 5)

      hboxPronCmd = wxBoxSizer(wxHORIZONTAL)
      hboxPronCmd.Add(wxStaticText(panelPron, -1, _("System Command: ")), 0,
         wxALIGN_CENTER_VERTICAL)

      self.entryPron = wxTextCtrl(panelPron, -1,
         self.app.config.get('pronunciationCommand') or \
         PRON_COMMAND)
      hboxPronCmd.Add(self.entryPron, 1, wxEXPAND, 0)
      
      self.buttonDefaultPron = wxButton(panelPron, 1106, _("Default"))
      hboxPronCmd.Add(self.buttonDefaultPron, 0, wxALL | wxEXPAND)
      
      sbSizerPron.Add(hboxPronCmd, 0, wxALL | wxEXPAND, 4)

      hboxPronWhat = wxBoxSizer(wxHORIZONTAL)
      self.rbPronOrig = wxRadioButton(panelPron, -1, _("Pronounce original word"))
      hboxPronWhat.Add(self.rbPronOrig, 0, wxALL | wxEXPAND, 3)
      self.rbPronTrans = wxRadioButton(panelPron, -1, _("Pronounce translation"))
      if self.app.config.get('pronounceTrans') == 'True':
          self.rbPronTrans.SetValue(True)
      hboxPronWhat.Add(self.rbPronTrans, 0, wxALL | wxEXPAND, 3)
      
      sbSizerPron.Add(hboxPronWhat, 0, wxALL | wxEXPAND, 0)

      self.winSize = wxCheckBox(self, 1101, _("Save window size on exit"))
      self.winSize.SetValue(self.app.config.get('saveWindowSize') == 'True')
      vboxMain.Add(self.winSize, 0, wxALL, 3)

      self.winPos = wxCheckBox(self, 1102, _("Save window position on exit"))
      self.winPos.SetValue(self.app.config.get('saveWindowPos') == 'True')
      vboxMain.Add(self.winPos, 0, wxALL, 3)

      self.sashPos = wxCheckBox(self, 1103, _("Save sash position on exit"))
      self.sashPos.SetValue(self.app.config.get('saveSashPos') == 'True')
      vboxMain.Add(self.sashPos, 0, wxALL, 3)

      self.clipboard = wxCheckBox(self, 1103,
                                  _("Take words from the clipboard by default"))
      self.clipboard.SetValue(self.app.config.get('useClipboard') == 'True')
      vboxMain.Add(self.clipboard, 0, wxALL, 3)

      vboxMain.Add(wxStaticLine(self, -1), 0, wxALL | wxEXPAND, 5)

      self.buttonOK = wxButton(self, 1104, _("OK"))
      hboxButtons.Add(self.buttonOK, 0, wxALL | wxEXPAND, 1)

      self.buttonCancel = wxButton(self, 1105, _("Cancel"))
      hboxButtons.Add(self.buttonCancel, 0, wxALL | wxEXPAND, 1)

      vboxMain.Add(hboxButtons, 0, wxALL | wxALIGN_RIGHT, 4)

      self.SetSizer(vboxMain)
      self.Fit()
      self.SetSize((400, -1))

      EVT_CHECKBOX(self, 1101, self.onSaveWinSizeClicked)
      EVT_CHECKBOX(self, 1102, self.onSaveWinPosClicked)
      EVT_CHECKBOX(self, 1103, self.onSaveSashPosClicked)
      EVT_BUTTON(self, 1106, self.onDefaultPron)
      EVT_BUTTON(self, 1104, self.onOK)
      EVT_BUTTON(self, 1105, self.onCancel)


   def onSaveWinSizeClicked(self, event):
      """This method is invoked when checkbox for window size
      is clicked"""
      
      if event.Checked() == 1:
         self.app.config.winSize = self.GetParent().GetSize()
         self.app.config.saveWinSize = 1
      else:
         self.app.config.saveWinSize = 0


   def onSaveWinPosClicked(self, event):
      """This method is invoked when checkbox for window position
      is clicked"""
      
      if event.Checked() == 1:
         self.app.config.winPos = self.GetParent().GetPosition()
         self.app.config.saveWinPos = 1
      else:
         self.app.config.saveWinPos = 0


   def onSaveSashPosClicked(self, event):
      """This method is invoked when checkbox for sash position
      is clicked"""
      
      if event.Checked() == 1:
         self.app.config.sashPos = self.GetParent().splitter.GetSashPosition()
         self.app.config.saveSashPos = 1
      else:
         self.app.config.saveSashPos = 0


   def onDefaultPron(self, event):
      """Set pronunciation command to default value"""

      self.entryPron.SetValue(PRON_COMMAND)


   def onOK(self, event):
      """Save configuration in the configuration object"""

      self.app.config.set('defaultDict',
                          enc.fromWX(self.dictChooser.GetValue()))

      self.app.config.set('encoding', encodings[self.encChooser.GetValue()])
      if self.app.window.activeDictionary == None:
         self.app.window.checkEncMenuItem(self.app.config.get('encoding'))
      
      self.app.config.set('dictServer', self.serverEntry.GetValue())
      self.app.config.set('dictServerPort', self.portEntry.GetValue())
      
      self.app.config.set('pronunciationCommand', self.entryPron.GetValue())
      self.app.config.set('pronounceTrans', str(self.rbPronTrans.GetValue()))

      self.app.config.set('saveWindowSize', str(self.winSize.GetValue()))
      self.app.config.set('saveWindowPos', str(self.winPos.GetValue()))
      self.app.config.set('saveSashPos', str(self.sashPos.GetValue()))
      self.app.config.set('useClipboard', str(self.clipboard.GetValue()))

      frame = self.GetParent()
      if self.app.config.get('saveWinSize'):
         self.app.config.set('windowWidth', frame.GetSize()[0])
         self.app.config.set('windowHeight', frame.GetSize()[1])
      if self.app.config.get('saveWindowPos'):
         self.app.config.set('windowPosX', frame.GetPosition()[0])
         self.app.config.set('windowPosY', frame.GetPosition()[1])

      if self.app.config.get('saveSashPos'):
         if not frame.wordListHidden():
            self.app.config.set('sashPos', frame.splitter.GetSashPosition())

      self.app.config.save()
      
      self.Destroy()


   def onCancel(self, event):
      """Close dialog window discarding changes"""
      
      self.Destroy()
