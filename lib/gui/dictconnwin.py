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
from wxPython.lib.rcsizer import RowColSizer
import traceback

from logger import systemLog, debugLog, DEBUG, INFO, WARNING, ERROR
from parser import DictConnection
from extra import dictclient
from threads import Process
import misc

_ = wxGetTranslation

CONNECTION_CHECK_INTERVAL = 400

class DictConnWindow(wxFrame):

   def __init__(self, parent, id, title, pos=wxDefaultPosition,
                size=wxDefaultSize, style=wxDEFAULT_FRAME_STYLE):
      wxFrame.__init__(self, parent, id, title, pos, size, style)

      self.app = wxGetApp()

      vboxMain = wxBoxSizer(wxVERTICAL)

      hboxButtons = wxBoxSizer(wxHORIZONTAL)
      hboxServer = RowColSizer()


      hboxServer.Add(wxStaticText(self, -1, _("Server: ")),
                     flag=wxALIGN_RIGHT | wxALIGN_CENTER_VERTICAL,
                     row=0, col=0, border=1)

      self.entryServer = wxTextCtrl(self, -1,
                                    self.app.config.get('dictServer'))
      hboxServer.Add(self.entryServer, flag=wxEXPAND, row=0, col=1, border=1)
      hboxServer.Add(wxButton(self, 1000, _("Default Server")),
                     flag=wxEXPAND, row=0, col=2, border=5)

      hboxServer.Add(wxStaticText(self, -1, _("Port: ")),
                     flag=wxALIGN_RIGHT | wxALIGN_CENTER_VERTICAL,
                     row=1, col=0, border=1)
      hboxServer.Add(wxButton(self, 1001, _("Default Port")),
                     flag=wxEXPAND, row=1, col=2, border=5)

      self.entryPort = wxTextCtrl(self, -1,
                                  self.app.config.get('dictServerPort'))
      hboxServer.Add(self.entryPort, flag=wxEXPAND, row=1, col=1, border=1)

      hboxServer.Add(wxStaticText(self, -1, _("Database: ")),
                     flag=wxALIGN_RIGHT | wxALIGN_CENTER_VERTICAL,
                     row=2, col=0, border=1)

      self.msgSearchInAll = _("Search in all databases")
      self.choiceDB = wxComboBox(self, 1002, self.msgSearchInAll,
                                 choices=[self.msgSearchInAll],
                                 style=wxTE_READONLY)
      self.choiceDB.SetInsertionPoint(0)
      hboxServer.Add(self.choiceDB, flag=wxEXPAND, row=2, col=1, border=1)

      hboxServer.Add(wxButton(self, 1003, _("Fetch List")), #size=(-1, 18)),
                     flag=wxEXPAND, row=2, col=2, border=1)

      #hboxServer.Add(wxStaticText(self, -1, _("Strategy: ")),
      #               flag=wxALIGN_RIGHT | wxALIGN_CENTER_VERTICAL,
      #               row=3, col=0, rowspan=1, border=1)
      #
      #self.choiceStrat = wxComboBox(self, 1006, #size=(-1, 20),
      #                         choices=[])
      #hboxServer.Add(self.choiceStrat, flag=wxEXPAND, row=3, col=1,
      #               rowspan=1, border=1)
      #
      #hboxServer.Add(wxButton(self, 1007, _("Update")), #size=(-1, 18)),
      #               flag=wxEXPAND, row=3, col=2, border=5)

      hboxServer.AddGrowableCol(1)

      vboxMain.Add(hboxServer, 1, wxALL | wxEXPAND, 4)

      self.buttonOK = wxButton(self, 1004, _("Connect"))
      hboxButtons.Add(self.buttonOK, 0, wxALL, 1)

      self.buttonCancel = wxButton(self, 1005, _("Cancel"))
      hboxButtons.Add(self.buttonCancel, 0, wxALL, 1)

      vboxMain.Add(hboxButtons, 0, wxALL | wxALIGN_CENTER, 2)

      self.CreateStatusBar()

      self.SetSizer(vboxMain)
      self.Fit()
      self.SetSize((500, -1))

      self.timerUpdateDB = wxTimer(self, 1006)
      self.timerConnect = wxTimer(self, 1007)

      self.update = None
      self.connection = None

      EVT_CHOICE(self, 1002, self.onDBSelected)
      EVT_BUTTON(self, 1000, self.onDefaultServer)
      EVT_BUTTON(self, 1001, self.onDefaultPort)
      EVT_BUTTON(self, 1003, self.onUpdateDB)
      EVT_BUTTON(self, 1007, self.onUpdateStrats)
      EVT_BUTTON(self, 1004, self.onOK)
      EVT_BUTTON(self, 1005, self.onCancel)
      EVT_TIMER(self, 1006, self.onTimerUpdateDB)
      EVT_TIMER(self, 1007, self.onTimerConnect)


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
               self.SetStatusText(_("Unable to connect"))


   def onTimerConnect(self, event):
      
      if self.connection != None:
         if self.connection.isDone():
            systemLog(INFO, "Connection timer stopped")
            self.timerConnect.Stop()
            self.conn = self.connection()
            
            if self.conn == None:
                self.SetStatusText(_("Unable to connect"))
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


   def onDBSelected(self, event):
      pass

   
   # Thread is not used there, because program don't hang if can't
   # connect. Otherwise, it may hang for a second depending on the
   # connection speed. TODO: better solution?
   def onOK(self, event):
      self.server = self.entryServer.GetValue()
      self.port = self.entryPort.GetValue()
          
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

      if db_name != "":
         title = "OpenDict - %s (%s)" % (self.server, db_name)
      else:
         title = "OpenDict - %s" % self.server
      self.app.window.SetTitle(title)

      self.app.window.checkEncMenuItem(self.app.config.get('encoding'))

      if not self.app.window.activeDictionary.getUsesWordList():
          self.app.window.hideWordList()

      self.app.window.SetStatusText("")
      self.timerUpdateDB.Stop()
      self.Destroy()

   def onCancel(self, event):
      self.timerUpdateDB.Stop()
      self.timerConnect.Stop()
      self.Destroy()


