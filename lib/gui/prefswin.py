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

import wx

from lib.logger import systemLog, debugLog, DEBUG, INFO, WARNING, ERROR
from lib.misc import encodings
from lib import enc

_ = wx.GetTranslation
PRON_COMMAND = "echo \"(SayText \\\"%s\\\")\" | festival"

class PrefsWindow(wx.Dialog):
   """Preferences dialog class"""


   def __init__(self, parent, id, title, pos=wx.DefaultPosition,
                size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE):
      """Initialize preferences dialog window"""
      
      wx.Dialog.__init__(self, parent, id, title, pos, size, style)

      self.app = wx.GetApp()

      vboxMain = wx.BoxSizer(wx.VERTICAL)
      hboxButtons = wx.BoxSizer(wx.HORIZONTAL)

      grid = wx.FlexGridSizer(2, 2, 1, 1)

      grid.Add(wx.StaticText(self, -1, _("Default dictionary: ")),
                   0, wx.ALIGN_CENTER_VERTICAL)

      dictNames = []
      for name, d in self.app.dictionaries.items():
          if d.getActive():
              dictNames.append(name)
      dictNames.sort()
      dictNames.insert(0, "")

      try:
         map(enc.toWX, dictNames)
      except Exception, e:
         systemLog(ERROR, "Unable to decode titles to UTF-8 (%s)" % e)
      
      self.dictChooser = wx.ComboBox(self, 1100,
                                    enc.toWX(self.app.config.get('defaultDict')),
                                    wx.Point(-1, -1),
                                    wx.Size(-1, -1), dictNames, wx.TE_READONLY)
      grid.Add(self.dictChooser, 0, wx.EXPAND)

      grid.Add(wx.StaticText(self, -1, _("Default encoding: ")),
               0, wx.ALIGN_CENTER_VERTICAL)
      self.encChooser = wx.ComboBox(self, 1108,
                                  encodings.keys()[encodings.values().index(self.app.config.get('encoding'))],
                                  wx.Point(-1, -1),
                                  wx.Size(-1, -1), encodings.keys(),
                                  wx.TE_READONLY)
      grid.Add(self.encChooser, 0, wx.EXPAND | wx.ALIGN_RIGHT)
      
      grid.AddGrowableCol(1)
      
      grid.Add(wx.StaticText(self, -1, _("Default DICT server: ")),
                   0, wx.ALIGN_CENTER_VERTICAL)
      self.serverEntry = wx.TextCtrl(self, -1,
                                    self.app.config.get('dictServer'))
      grid.Add(self.serverEntry, 0, wx.EXPAND)
      
      grid.Add(wx.StaticText(self, -1, _("Default DICT server port: ")),
                   0, wx.ALIGN_CENTER_VERTICAL)
      self.portEntry = wx.TextCtrl(self, -1,
                                  self.app.config.get('dictServerPort'))
      grid.Add(self.portEntry, 0, wx.EXPAND)
      
      vboxMain.Add(grid, 0, wx.ALL | wx.EXPAND, 4)
      
      #
      # Pronunciation
      #
      panelPron = wx.Panel(self, -1)
      sbSizerPron = wx.StaticBoxSizer(wx.StaticBox(panelPron, -1, 
                                                 _("Pronunciation")), 
                                     wx.VERTICAL)
      panelPron.SetSizer(sbSizerPron)
      panelPron.SetAutoLayout(True)
      sbSizerPron.Fit(panelPron)
      vboxMain.Add(panelPron, 0, wx.ALL | wx.EXPAND, 5)

      hboxPronCmd = wx.BoxSizer(wx.HORIZONTAL)
      hboxPronCmd.Add(wx.StaticText(panelPron, -1, _("System Command: ")), 0,
         wx.ALIGN_CENTER_VERTICAL)

      self.entryPron = wx.TextCtrl(panelPron, -1,
         self.app.config.get('pronunciationCommand') or \
         PRON_COMMAND)
      hboxPronCmd.Add(self.entryPron, 1, wx.EXPAND, 0)
      
      self.buttonDefaultPron = wx.Button(panelPron, 1106, _("Default"))
      hboxPronCmd.Add(self.buttonDefaultPron, 0, wx.ALL | wx.EXPAND)
      
      sbSizerPron.Add(hboxPronCmd, 0, wx.ALL | wx.EXPAND, 4)

      hboxPronWhat = wx.BoxSizer(wx.HORIZONTAL)
      self.rbPronOrig = wx.RadioButton(panelPron, -1, _("Pronounce original word"))
      hboxPronWhat.Add(self.rbPronOrig, 0, wx.ALL | wx.EXPAND, 3)
      self.rbPronTrans = wx.RadioButton(panelPron, -1, _("Pronounce translation"))
      if self.app.config.get('pronounceTrans') == 'True':
          self.rbPronTrans.SetValue(True)
      hboxPronWhat.Add(self.rbPronTrans, 0, wx.ALL | wx.EXPAND, 3)
      
      sbSizerPron.Add(hboxPronWhat, 0, wx.ALL | wx.EXPAND, 0)

      self.winSize = wx.CheckBox(self, 1101, _("Save window size on exit"))
      self.winSize.SetValue(self.app.config.get('saveWindowSize') == 'True')
      vboxMain.Add(self.winSize, 0, wx.ALL, 3)

      self.winPos = wx.CheckBox(self, 1102, _("Save window position on exit"))
      self.winPos.SetValue(self.app.config.get('saveWindowPos') == 'True')
      vboxMain.Add(self.winPos, 0, wx.ALL, 3)

      self.sashPos = wx.CheckBox(self, 1103, _("Save sash position on exit"))
      self.sashPos.SetValue(self.app.config.get('saveSashPos') == 'True')
      vboxMain.Add(self.sashPos, 0, wx.ALL, 3)

      self.clipboard = wx.CheckBox(self, 1103,
                                  _("Take words from the clipboard by default"))
      self.clipboard.SetValue(self.app.config.get('useClipboard') == 'True')
      vboxMain.Add(self.clipboard, 0, wx.ALL, 3)

      vboxMain.Add(wx.StaticLine(self, -1), 0, wx.ALL | wx.EXPAND, 5)

      self.buttonOK = wx.Button(self, 1104, _("OK"))
      hboxButtons.Add(self.buttonOK, 0, wx.ALL | wx.EXPAND, 1)

      self.buttonCancel = wx.Button(self, 1105, _("Cancel"))
      hboxButtons.Add(self.buttonCancel, 0, wx.ALL | wx.EXPAND, 1)

      vboxMain.Add(hboxButtons, 0, wx.ALL | wx.ALIGN_RIGHT, 4)

      self.SetSizer(vboxMain)
      self.Fit()
      self.SetSize((400, -1))

      wx.EVT_CHECKBOX(self, 1101, self.onSaveWinSizeClicked)
      wx.EVT_CHECKBOX(self, 1102, self.onSaveWinPosClicked)
      wx.EVT_CHECKBOX(self, 1103, self.onSaveSashPosClicked)
      wx.EVT_BUTTON(self, 1106, self.onDefaultPron)
      wx.EVT_BUTTON(self, 1104, self.onOK)
      wx.EVT_BUTTON(self, 1105, self.onCancel)


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
