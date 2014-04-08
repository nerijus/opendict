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
from wx.lib.rcsizer import RowColSizer
import traceback

from lib.logger import systemLog, debugLog, DEBUG, INFO, WARNING, ERROR
from lib.parser import DictConnection
from lib.extra import dictclient
from lib.threads import Process
from lib.gui import errorwin
from lib import misc

_ = wx.GetTranslation

CONNECTION_CHECK_INTERVAL = 400


class DictConnWindow(wx.Frame):

   def __init__(self, parent, id, title, pos=wx.DefaultPosition,
                size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE):
      wx.Frame.__init__(self, parent, id, title, pos, size, style)

      self.parent = parent
      self.app = wx.GetApp()

      vboxMain = wx.BoxSizer(wx.VERTICAL)

      hboxButtons = wx.BoxSizer(wx.HORIZONTAL)
      hboxServer = RowColSizer()

      #
      # Server address row
      #
      hboxServer.Add(wx.StaticText(self, -1, _("Server: ")),
                     flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL,
                     row=0, col=0, border=1)

      servers = ['dict.org', 'localhost']
      self.entryServer = wx.ComboBox(self, -1,
          self.app.config.get('dictServer'), wx.Point(-1, -1),
                              wx.Size(-1, -1), servers, wx.CB_DROPDOWN)
      hboxServer.Add(self.entryServer, flag=wx.EXPAND, row=0, col=1, border=1)
      hboxServer.Add(wx.Button(self, 1000, _("Default Server")),
                     flag=wx.EXPAND, row=0, col=2, border=5)

      #
      # Port entry row
      #
      hboxServer.Add(wx.StaticText(self, -1, _("Port: ")),
                     flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL,
                     row=1, col=0, border=1)
      hboxServer.Add(wx.Button(self, 1001, _("Default Port")),
                     flag=wx.EXPAND, row=1, col=2, border=5)

      self.entryPort = wx.TextCtrl(self, -1,
                                  self.app.config.get('dictServerPort'))
      hboxServer.Add(self.entryPort, flag=wx.EXPAND, row=1, col=1, border=1)

      #
      # Database selection row
      #
      hboxServer.Add(wx.StaticText(self, -1, _("Database: ")),
                     flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL,
                     row=2, col=0, border=1)

      self.msgSearchInAll = _("Search in all databases")
      self.choiceDB = wx.ComboBox(self, 1002, self.msgSearchInAll,
                                 choices=[self.msgSearchInAll],
                                 style=wx.TE_READONLY)
      self.choiceDB.SetInsertionPoint(0)
      hboxServer.Add(self.choiceDB, flag=wx.EXPAND, row=2, col=1, border=1)

      hboxServer.Add(wx.Button(self, 1003, _("Fetch List")), #size=(-1, 18)),
                     flag=wx.EXPAND, row=2, col=2, border=1)

      #
      # Encoding selection row
      #
      hboxServer.Add(wx.StaticText(self, -1, _("Character encoding: ")),
                     flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL,
                     row=3, col=0, border=1)

      self.entryEncoding = wx.ComboBox(self, 1006,
                              misc.encodings.keys()[
                                misc.encodings.values().index(
                                    self.app.config.get('dict-server-encoding'))],
                              wx.Point(-1, -1),
                              wx.Size(-1, -1), misc.encodings.keys(), 
                              wx.CB_DROPDOWN | wx.CB_READONLY)

      hboxServer.Add(self.entryEncoding, flag=wx.EXPAND, row=3, col=1, border=1)

      #hboxServer.Add(wx.StaticText(self, -1, _("Strategy: ")),
      #               flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL,
      #               row=3, col=0, rowspan=1, border=1)
      #
      #self.choiceStrat = wx.ComboBox(self, 1006, #size=(-1, 20),
      #                         choices=[])
      #hboxServer.Add(self.choiceStrat, flag=wx.EXPAND, row=3, col=1,
      #               rowspan=1, border=1)
      #
      #hboxServer.Add(wx.Button(self, 1007, _("Update")), #size=(-1, 18)),
      #               flag=wx.EXPAND, row=3, col=2, border=5)

      hboxServer.AddGrowableCol(1)

      vboxMain.Add(hboxServer, 1, wx.ALL | wx.EXPAND, 4)

      self.buttonOK = wx.Button(self, 1004, _("Connect"))
      hboxButtons.Add(self.buttonOK, 0, wx.ALL, 1)

      self.buttonCancel = wx.Button(self, 1005, _("Cancel"))
      hboxButtons.Add(self.buttonCancel, 0, wx.ALL, 1)

      vboxMain.Add(hboxButtons, 0, wx.ALL | wx.ALIGN_CENTER, 2)

      self.CreateStatusBar()

      self.SetSizer(vboxMain)
      self.Fit()
      self.SetSize((500, -1))

      self.timerUpdateDB = wx.Timer(self, 1006)
      self.timerConnect = wx.Timer(self, 1007)

      self.update = None
      self.connection = None

      wx.EVT_BUTTON(self, 1000, self.onDefaultServer)
      wx.EVT_BUTTON(self, 1001, self.onDefaultPort)
      wx.EVT_BUTTON(self, 1003, self.onUpdateDB)
      wx.EVT_BUTTON(self, 1007, self.onUpdateStrats)
      wx.EVT_BUTTON(self, 1004, self.onOK)
      wx.EVT_BUTTON(self, 1005, self.onCancel)
      wx.EVT_TIMER(self, 1006, self.onTimerUpdateDB)
      wx.EVT_TIMER(self, 1007, self.onTimerConnect)


   def onTimerUpdateDB(self, event):
      
      systemLog(DEBUG, "DictConnection: [IDLE] Receiving DB list...")
      if self.update != None:
         if self.update.isDone():
            systemLog(DEBUG, "DictConnection: DB list received")
            obj = self.update()
            if type(obj) == type({}):
               self.timerUpdateDB.Stop()
               self.update = None
               self.choiceDB.Clear()
               self.choiceDB.Append(self.msgSearchInAll)
               for name in obj.values():
                  self.choiceDB.Append(name)
               self.SetStatusText(_("Done"))
               self.choiceDB.SetValue(self.msgSearchInAll)
               self.choiceDB.SetInsertionPoint(0)
            elif obj != None:
               self.SetStatusText(_("Receiving database list..."))
               self.update = Process(obj.getdbdescs)
            else:
               self.timerUpdateDB.Stop()
               self.SetStatusText('')
               title = _("Connection Error")
               msg = _("Unable to connect to server")
               errorwin.showErrorMessage(title, msg)



   def onTimerConnect(self, event):
      
      if self.connection != None:
         if self.connection.isDone():
            systemLog(INFO, "Connection timer stopped")
            self.timerConnect.Stop()
            self.conn = self.connection()
            
            if self.conn == None:
                self.SetStatusText('')
                title = _("Connection Error")
                msg = _("Unable to connect to server")
                errorwin.showErrorMessage(title, msg)
            else:
                self.prepareForUsing()
            

   def onDefaultServer(self, event):
      
      self.entryServer.SetValue("dict.org")


   def onDefaultPort(self, event):
      
      self.entryPort.SetValue("2628")


   def onUpdateDB(self, event):
      
      self.SetStatusText(_("Connecting..."))
      self.timerUpdateDB.Start(CONNECTION_CHECK_INTERVAL)
      self.update = Process(dictclient.Connection,
                                self.entryServer.GetValue(),
                                int(self.entryPort.GetValue()))

   # not used, remove
   def onUpdateStrats(self, event):
      conn = dictclient.Connection()
      strats = conn.getstratdescs()

      for name in strats.values():
         self.choiceStrat.Append(name)


   # Thread is not used there, because program don't hang if can't
   # connect. Otherwise, it may hang for a second depending on the
   # connection speed. TODO: better solution?
   def onOK(self, event):
      self.server = self.entryServer.GetValue()
      self.app.config.set('dictServer', self.server)

      self.port = self.entryPort.GetValue()

      encName = self.entryEncoding.GetValue()
      try:
          enc = misc.encodings[encName]
      except KeyError:
          print 'Error: invalid encoding name "%s", defaulting to UTF-8' % \
              encName
          enc = 'UTF-8'
          
      self.encoding = (enc, encName)
          
      self.timerConnect.Stop()
      self.timerUpdateDB.Stop()
      self.SetStatusText(_("Connecting to %s...") % self.server)
      self.timerConnect.Start(CONNECTION_CHECK_INTERVAL)
      self.connection = Process(dictclient.Connection,
                                self.server, int(self.port))

         
   def prepareForUsing(self):
      """Prepare MainWindow for displaying data"""
       
      systemLog(INFO, "DictConnection: Connected, preparing main window...")

      db = self.choiceDB.GetValue()
      if self.choiceDB.FindString(db) == 0:
         db = "*"
         db_name = ""
      else:
         try:
            dbs = self.conn.getdbdescs()
            for d in dbs.keys():
               if dbs[d] == db:
                  db = d
            db_name = dbs[db]
         except:
            traceback.print_exc()
            self.app.window.SetStatusText(misc.errors[4])
            return

      self.app.window.onCloseDict(None)
      self.app.window.activeDictionary = DictConnection(self.server,
                                                        int(self.port), 
                                            db, "")
                                            
      self.app.config.set('dict-server-encoding', self.encoding[0])
      self.parent.changeEncoding(self.encoding[1])

      if db_name != "":
         title = "OpenDict - %s (%s)" % (self.server, db_name)
      else:
         title = "OpenDict - %s" % self.server
      self.app.window.SetTitle(title)

      self.app.window.checkEncMenuItem(self.encoding[0])

      if not self.app.window.activeDictionary.getUsesWordList():
          self.app.window.hideWordList()

      self.app.window.SetStatusText("")
      self.timerUpdateDB.Stop()
      self.Destroy()


   def onCancel(self, event):
      self.timerUpdateDB.Stop()
      self.timerConnect.Stop()
      self.Destroy()


