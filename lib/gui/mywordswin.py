# -*- coding: iso-8859-1 -*-

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
# Module: gui.mywordswin

from wxPython.wx import *
from wxPython.lib.rcsizer import RowColSizer
import os
import codecs

from misc import encodings, printError
from info import __version__
from parser import TMXParser
import info

_ = wxGetTranslation

# IDs range: 6201-6220
class MyWordsWindow(wxFrame):

    """Built-in dictionary editor. This tool lets user create and
    manage his own dictionaries in TMX format."""

    class CreateNewWordWindow(wxFrame):

        """Enter some info and add new word"""

        def __init__(self, parent, id, title, pos=wxDefaultPosition,
                 size=wxDefaultSize, style=wxDEFAULT_FRAME_STYLE):
            wxFrame.__init__(self, parent, id, title, pos, size, style)

            vboxMain = wxBoxSizer(wxVERTICAL)
            hboxButtons = wxBoxSizer(wxHORIZONTAL)
#            boxInfo = RowColSizer()
            hboxAdd = wxBoxSizer(wxHORIZONTAL)

            hboxAdd.Add(wxStaticText(self, -1, _("Word: "), pos=(-1, -1)),
                        0, wxALL | wxALIGN_CENTER_VERTICAL, 2)

            self.entryWord = wxTextCtrl(self, -1, "")
            hboxAdd.Add(self.entryWord,
                        1, wxALL | wxEXPAND | wxALIGN_CENTER, 2)
            
            vboxMain.Add(hboxAdd, 1, wxALL | wxEXPAND, 2)
            
            self.buttonOK = wxButton(self, 6201, _("OK"))
            hboxButtons.Add(self.buttonOK, 1, wxALL, 1)

            self.buttonCancel = wxButton(self, 6202, _("Cancel"))
            hboxButtons.Add(self.buttonCancel, 1, wxALL, 1)

            vboxMain.Add(hboxButtons, 0, wxALL | wxEXPAND, 2)
            
            self.CreateStatusBar()

            self.SetSizer(vboxMain)
            self.Fit()
            self.SetSize((300, -1))

            EVT_BUTTON(self, 6201, self.onSave)
            EVT_BUTTON(self, 6202, self.onClose)
            

        def onSave(self, event):
           
            parent = self.GetParent()

            word = self.entryWord.GetValue()
            if word == "":
                self.SetStatusText("Enter a word")
                return

            status = parent.parent.myWords.addWord(word)
            if status:
                self.SetStatusText(_("Error: ")+status)    
                return

            parent.updateList() 
            self.onClose(None)
              

        def onClose(self, event):
            self.Destroy()


    # -------------------------------------------------------------
    def __init__(self, parent, id, title, pos=wxDefaultPosition,
                 size=wxDefaultSize, style=wxDEFAULT_FRAME_STYLE):
        wxFrame.__init__(self, parent, id, title, pos, size, style)

        self.app = wxGetApp()
        self.parent = parent 
        self.CreateStatusBar()

        vboxMain = wxBoxSizer(wxVERTICAL)
        vboxDict = wxBoxSizer(wxVERTICAL)
        vboxList = wxBoxSizer(wxVERTICAL)
        hboxDict = wxBoxSizer(wxHORIZONTAL)
        vboxButtons = wxBoxSizer(wxVERTICAL)

#        self.buttonSort = wxButton(self, 6210, _("Search"))
#       vboxButtons.Add(self.buttonSort, 0, wxALL | wxEXPAND, 1)

        self.buttonSearch = wxButton(self, 6215, _("Search"))
        vboxButtons.Add(self.buttonSearch, 0, wxALL | wxEXPAND, 1)

        self.buttonAdd = wxButton(self, 6211, _("Add..."))
        vboxButtons.Add(self.buttonAdd, 0, wxALL | wxEXPAND, 1)

        self.buttonAddCurrent = wxButton(self, 6214, _("Add current"))
        vboxButtons.Add(self.buttonAddCurrent, 0, wxALL | wxEXPAND, 1)  
        
        self.buttonRemove = wxButton(self, 6212, _("Remove"))
        vboxButtons.Add(self.buttonRemove, 0, wxALL | wxEXPAND, 1)

        self.buttonClose = wxButton(self, 6213, _("Close"))
        vboxButtons.Add(self.buttonClose, 0, wxALL | wxEXPAND, 1)
        
        panelList = wxPanel(self, -1)
        sbSizerList = wxStaticBoxSizer(wxStaticBox(panelList, -1, 
                                                 _("Word List")),
                                       wxVERTICAL)
        
        self.wordList = wxListBox(panelList, 6020,
                              wxPoint(-1, -1),
                              wxSize(-1, -1),
                              self.parent.myWords.getWords(),
                              wxLB_SINGLE | wxSUNKEN_BORDER)
                              
        sbSizerList.AddWindow(self.wordList, 1, wxALL | wxEXPAND, 0)
        panelList.SetSizer(sbSizerList)
        panelList.SetAutoLayout(true)
        sbSizerList.Fit(panelList)

        hboxDict.Add(panelList, 1, wxALL | wxEXPAND, 0)
        hboxDict.Add(vboxButtons, 0, wxALL | wxEXPAND, 5)
        vboxDict.Add(hboxDict, 1, wxALL | wxEXPAND, 0)
        vboxMain.Add(vboxDict, 1, wxALL | wxEXPAND, 10)

        self.SetSizer(vboxMain)
#        self.Fit()

        EVT_BUTTON(self, 6211, self.onAddWord)
        EVT_BUTTON(self, 6212, self.onRemove)
        EVT_BUTTON(self, 6213, self.onClose)
        EVT_BUTTON(self, 6214, self.onAddCurrent)
        EVT_BUTTON(self, 6215, self.onSearch)
        EVT_LISTBOX(self, 6020, self.onSelected)
        EVT_CLOSE(self, self.onClose)


    def onSearch(self, event):

        parent = self.GetParent()
        word = self.wordList.GetStringSelection()

        if word != "":
            parent.entry.SetValue(word)
            parent.onSearch(None)
        else:
            self.SetStatusText(_("No word selected"))     


    def onAddWord(self, event):
        self.SetStatusText("")
        
        window = self.CreateNewWordWindow(self, -1, _("New Word"),
                                          size=(-1, -1), pos=(-1, -1),
                                          style=wxDEFAULT_FRAME_STYLE)
        window.CentreOnScreen()
        window.Show(True)


    def onAddCurrent(self, event):

        self.SetStatusText("")
        parent = self.GetParent()
        word = parent.entry.GetValue().strip()

        if word:
            status = parent.myWords.addWord(word)

            if status:
                self.SetStatusText(_("Error: ")+status)
                return
                
            self.updateList()                   
        else:
            self.SetStatusText(_("Search entry is empty"))


    def updateList(self):

        parent = self.GetParent() 
        self.wordList.Clear()
        self.wordList.InsertItems(parent.myWords.getWords(), 0)
             

    def onRemove(self, event):
        self.SetStatusText("")
        word = self.wordList.GetStringSelection()

        if word != "":
#            index = self.parent.myWords.getWords().index(word)
#            self.words.remove(word)

            status = self.parent.myWords.removeWord(word)
            if status:
                self.SetStatusText(_("Error: ")+status)

            self.updateList() 
        else:
            self.SetStatusText(_("No word selected"))  

        
    def onSelected(self, event):

        word = self.wordList.GetStringSelection()
        parent = self.GetParent()
        parent.entry.SetValue(word)
        

    def onClose(self, event):

        print "Closing MyWords window"
        self.GetParent().activeMyWordsWindow = False  
        self.Destroy()
