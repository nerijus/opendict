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
# Module: gui.dictconnwin

from wxPython.wx import *
from wxPython.lib.rcsizer import RowColSizer

from parser import DictConnection
from extra import dictclient
from threads import Process
import misc

_ = wxGetTranslation

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

      self.entryServer = wxTextCtrl(self, -1, "dict.org")
      hboxServer.Add(self.entryServer, flag=wxEXPAND, row=0, col=1, border=1)
      hboxServer.Add(wxButton(self, 1000, _("Default server")),
                     flag=wxEXPAND, row=0, col=2, border=5)

      hboxServer.Add(wxStaticText(self, -1, _("Port: ")),
                     flag=wxALIGN_RIGHT | wxALIGN_CENTER_VERTICAL,
                     row=1, col=0, border=1)
      hboxServer.Add(wxButton(self, 1001, _("Default port")),
                     flag=wxEXPAND, row=1, col=2, border=5)

      self.entryPort = wxTextCtrl(self, -1, "2628")
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

      hboxServer.Add(wxButton(self, 1003, _("Update")), #size=(-1, 18)),
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

      self.update = None

      EVT_CHOICE(self, 1002, self.onDBSelected)
      EVT_BUTTON(self, 1000, self.onDefaultServer)
      EVT_BUTTON(self, 1001, self.onDefaultPort)
      EVT_BUTTON(self, 1003, self.onUpdateDB)
      EVT_BUTTON(self, 1007, self.onUpdateStrats)
      EVT_BUTTON(self, 1004, self.onOK)
      EVT_BUTTON(self, 1005, self.onCancel)
      EVT_TIMER(self, 1006, self.onTimerUpdateDB)


   def onTimerUpdateDB(self, event):
      if self.update != None:
         if self.update.isDone():
            print "Stopped"
            obj = self.update()
            if type(obj) == type({}):
               # this is dbs
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
               # this is connection, now get dbs
               self.SetStatusText(_("Receiving database list..."))
               self.update = Process(obj.getdbdescs)
            else:
               self.timerUpdateDB.Stop()
               self.SetStatusText(_("Can't connect"))


   def onTimerConnect(self, event):
      print "Connecting..."
      if self.connection != None:
         if self.connection.isDone:
            self.timerConnection.Stop()
            conn = self.connection()

   def onDefaultServer(self, event):
      self.entryServer.SetValue("dict.org")

   def onDefaultPort(self, event):
      self.entryPort.SetValue("2628")

   def onUpdateDB(self, event):
      print "Updating DB list..."
      self.SetStatusText(_("Connecting..."))
      self.timerUpdateDB.Start(10)
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
      print "DB:", event.GetString()
      #self.Fit()

   # Thread is not used there, because program don't hang if can't
   # connect. Otherwise, it may hang for a second depending on the
   # connection speed. TODO: someting better?
   def onOK(self, event):
      server = self.entryServer.GetValue()
      port = self.entryPort.GetValue()

      self.Hide()
      self.timerUpdateDB.Stop()
      self.app.window.SetStatusText(_("Connecting to %s...") % server)

      # Check if it is posibble to connect
      try:
         conn = dictclient.Connection(server, int(port))
      except:
         self.app.window.SetStatusText(_("Can't connect to %s") % server)
         return

      db = self.choiceDB.GetValue()
      if self.choiceDB.FindString(db) == 0:
         db = "*"
         db_name = ""
      else:
         try:
            dbs = conn.getdbdescs()
            for d in dbs.keys():
               if dbs[d] == db:
                  db = d
            db_name = dbs[db]
         except:
            self.app.window.SetStatusText(misc.errors[4])
            return

      self.app.window.onCloseDict(None)
      self.app.window.dict = DictConnection(self.app.window,
                                            server, int(port), db, "")

      if db_name != "":
         title = "OpenDict: %s:%s %s" % (server, port, db_name)
      else:
         title = "OpenDict: %s:%s" % (server, port)
      self.app.window.SetTitle(title)

      self.app.window.encoding = self.app.config.defaultEnc
      self.app.window.checkEncMenuItem(self.app.window.encoding)

      #if self.app.window.dict.needsList == 1:
      #   if self.app.window.wlHidden == 1:
      #      self.app.window.unhideWordList()
      #      self.app.window.wlHidden = 0
      #else:
      #   if self.app.window.wlHidden == 0:
      #      self.app.window.hideWordList()
      #      self.app.window.wlHidden = 1
      #self.app.window.checkIfNeedsList()
      self.app.window.wlHidden = 1
      self.app.window.hideWordList()

      self.app.window.SetStatusText("")
      self.timerUpdateDB.Stop()
      self.Destroy()

   def onCancel(self, event):
      self.timerUpdateDB.Stop()
      self.Destroy()

