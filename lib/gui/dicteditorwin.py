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
# Module: gui.dicteditorwin

# TODO: not usable yet, needs some work with encodings, gui, etc.

from wxPython.wx import *
from wxPython.lib.rcsizer import RowColSizer
import os
import codecs

from misc import encodings, printError
from info import __version__
from parser import TMXParser
import info

_ = wxGetTranslation

# IDs range: 6000-6200
class DictEditorWindow(wxFrame):

    """Built-in dictionary editor. This tool lets user create and
    manage his own dictionaries in TMX format."""

    # IDs range: 6060-6069
    class CreateNewWordWindow(wxFrame):

        """Enter some info and add new word"""

        def __init__(self, parent, id, title, pos=wxDefaultPosition,
                 size=wxDefaultSize, style=wxDEFAULT_FRAME_STYLE):
            wxFrame.__init__(self, parent, id, title, pos, size, style)

            vboxMain = wxBoxSizer(wxVERTICAL)
            hboxButtons = wxBoxSizer(wxHORIZONTAL)
            boxInfo = RowColSizer()


            boxInfo.Add(wxStaticText(self, -1, _("Word: "), pos=(-1, -1)),
                        flag=wxALIGN_RIGHT | wxALIGN_CENTER_VERTICAL,
                        row=0, col=0, border=1)

            self.entryWord = wxTextCtrl(self, -1, "")
            boxInfo.Add(self.entryWord, flag=wxEXPAND, row=0, col=1, border=1)

            boxInfo.Add(wxStaticText(self, -1, _("Translation: ")),
                        flag=wxALIGN_RIGHT | wxALIGN_TOP,
                        row=1, col=0, border=1)

            self.text = wxTextCtrl(self, -1, "", size=(-1, 140),
                                   style=wxTE_MULTILINE)
            boxInfo.Add(self.text, flag=wxEXPAND, row=1, col=1, border=1)

            boxInfo.AddGrowableCol(1)
            vboxMain.Add(boxInfo, 1, wxALL | wxEXPAND, 2)

            self.buttonOK = wxButton(self, 6050, _("OK"))
            hboxButtons.Add(self.buttonOK, 1, wxALL, 1)

            self.buttonCancel = wxButton(self, 6051, _("Cancel"))
            hboxButtons.Add(self.buttonCancel, 1, wxALL, 1)

            vboxMain.Add(hboxButtons, 0, wxALL | wxEXPAND, 2)
            
            self.CreateStatusBar()

            self.SetSizer(vboxMain)
            self.Fit()
            self.SetSize((300, -1))

            EVT_BUTTON(self, 6050, self.onSave)
            EVT_BUTTON(self, 6051, self.onClose)

        def onSave(self, event):
           
            parent = self.GetParent()

            word = self.entryWord.GetValue()
            if word == "":
                word = _("(empty)")
            
            if not word in parent.parser.mapping.keys():
                parent.parser.mapping[word] = self.text.GetValue().split('\n')
                parent.list.Append(word)
                parent.changed = 1
                self.Destroy()
            else:
                self.SetStatusText(_("Error: word \"%s\" already exists") % word)

        def onClose(self, event):
            self.Destroy()


    class EditWordWindow(wxFrame):

        def __init__(self, word, parent, id, title, pos=wxDefaultPosition,
                 size=wxDefaultSize, style=wxDEFAULT_FRAME_STYLE):
            wxFrame.__init__(self, parent, id, title, pos, size, style)

            vboxMain = wxBoxSizer(wxVERTICAL)
            hboxButtons = wxBoxSizer(wxHORIZONTAL)
            boxInfo = RowColSizer()


            boxInfo.Add(wxStaticText(self, -1, _("Word: "), pos=(-1, -1)),
                        flag=wxALIGN_RIGHT | wxALIGN_CENTER_VERTICAL,
                        row=0, col=0, border=1)

            self.entryWord = wxTextCtrl(self, -1, word)
            self.entryWord.Disable()
            boxInfo.Add(self.entryWord, flag=wxEXPAND, row=0, col=1, border=1)

            boxInfo.Add(wxStaticText(self, -1, _("Translation: ")),
                        flag=wxALIGN_RIGHT | wxALIGN_TOP,
                        row=1, col=0, border=1)

            self.text = wxTextCtrl(self, -1,
                                   "\n".join(parent.parser.mapping[word]),
                                   size=(-1, 140),
                                   style=wxTE_MULTILINE)
            boxInfo.Add(self.text, flag=wxEXPAND, row=1, col=1, border=1)

            boxInfo.AddGrowableCol(1)
            vboxMain.Add(boxInfo, 1, wxALL | wxEXPAND, 2)

            self.buttonOK = wxButton(self, 6050, _("OK"))
            hboxButtons.Add(self.buttonOK, 1, wxALL, 1)

            self.buttonCancel = wxButton(self, 6051, _("Cancel"))
            hboxButtons.Add(self.buttonCancel, 1, wxALL, 1)

            vboxMain.Add(hboxButtons, 0, wxALL | wxEXPAND, 2)

            self.SetSizer(vboxMain)
            self.Fit()
            self.SetSize((300, -1))

            EVT_BUTTON(self, 6050, self.onSave)
            EVT_BUTTON(self, 6051, self.onClose)

        def onSave(self, event):
           
            parent = self.GetParent()
            word = self.entryWord.GetValue()
                
            parent.parser.mapping[word] = self.text.GetValue().split('\n')
            parent.changed = 1

            self.Destroy()

        def onClose(self, event):
            self.Destroy()

    # IDs range: 6000-6003
    class ConfirmExitWindow(wxDialog):

        def __init__(self, parent, id, title, pos=wxDefaultPosition,
                 size=wxDefaultSize, style=wxDEFAULT_DIALOG_STYLE):
            wxDialog.__init__(self, parent, id, title, pos, size, style)

            self.parent = self.GetParent()
            
            vboxMain = wxBoxSizer(wxVERTICAL)
            hboxButtons = wxBoxSizer(wxHORIZONTAL)
            
            labelMsg = wxStaticText(self, -1, _("Dictionary \"%s\" has been changed") % parent.name)
            vboxMain.Add(labelMsg, 1, wxALL | wxEXPAND, 15)
            
            buttonSave = wxButton(self, 6000, _("Save"))
            hboxButtons.Add(buttonSave, 0, wxALL | wxEXPAND, 3)
            
            buttonExit = wxButton(self, 6001, _("Do not save"))
            hboxButtons.Add(buttonExit, 0, wxALL | wxEXPAND, 3)
            
            buttonCancel = wxButton(self, 6002, _("Cancel"))
            hboxButtons.Add(buttonCancel, 0, wxALL | wxEXPAND, 3)
            
            vboxMain.Add(hboxButtons, 0, wxALL | wxEXPAND, 2)
            
            self.SetSizer(vboxMain)
            self.Fit()
            
            EVT_BUTTON(self, 6000, self.onSave)
            EVT_BUTTON(self, 6001, self.onExitParent)
            EVT_BUTTON(self, 6002, self.onClose)
            
        def onSave(self, event):
            print "Saving changes and exiting"
            if self.parent.cAction == "save":
                if self.parent.save(parent):
                    self.parent.Destroy()
            elif self.parent.cAction == "open":
                if self.parent.save(self.parent):
                    self.parent.open()
            elif self.parent.cAction == "close":
                if self.parent.save(self.parent):
                    self.parent.Destroy()
            
        def onExitParent(self, event):
            print "Exiting without saving"
            if self.parent.cAction == "save" or self.parent.cAction == "close":
                self.parent.Destroy()
            elif self.parent.cAction == "open":
                self.Hide()
                self.parent.open()
                self.Destroy()
            
        def onClose(self, event):
            self.Destroy()

    # -------------------------------------------------------------
    def __init__(self, parent, id, title, pos=wxDefaultPosition,
                 size=wxDefaultSize, style=wxDEFAULT_FRAME_STYLE):
        wxFrame.__init__(self, parent, id, title, pos, size, style)

        self.app = wxGetApp()
        self.CreateStatusBar()
        
        self.priTitle = _("Dictionary editor")
        self.saved = 1
        self.changed = 0
        self.parser = None
        self.cAction = None

        vboxMain = wxBoxSizer(wxVERTICAL)
        vboxDict = wxBoxSizer(wxVERTICAL)
        vboxList = wxBoxSizer(wxVERTICAL)
        hboxDict = wxBoxSizer(wxHORIZONTAL)
        vboxEditButtons = wxBoxSizer(wxVERTICAL)
        hboxButtons = wxBoxSizer(wxHORIZONTAL)

        # Control buttons
        self.controlButtons = []
        
        self.buttonAdd = wxButton(self, 6000, _("Add"))
        self.controlButtons.append(self.buttonAdd)
        
        self.buttonEdit = wxButton(self, 6001, _("Edit"))
        self.controlButtons.append(self.buttonEdit)

        self.buttonRemove = wxButton(self, 6002, _("Remove"))
        self.controlButtons.append(self.buttonRemove)

        #self.buttonSearch = wxButton(self, 6003, _("Search"))
        #self.controlButtons.append(self.buttonSearch)

        self.buttonSort = wxButton(self, 6004, _("Sort"))
        self.controlButtons.append(self.buttonSort)

        self.buttonSave = wxButton(self, 6005, _("Save"))
        self.controlButtons.append(self.buttonSave)
        
        for button in self.controlButtons:
            button.Disable()
            vboxEditButtons.Add(button, 0, wxALL | wxEXPAND, 1)
        
        panelList = wxPanel(self, -1)
        sbSizerList = wxStaticBoxSizer(wxStaticBox(panelList, -1, 
                                                 _("Word List")),
                                       wxVERTICAL)
        
        self.list = wxListBox(panelList, 6020,
                              wxPoint(-1, -1),
                              wxSize(-1, -1),
                              [],
                              wxLB_SINGLE | wxSUNKEN_BORDER)
                              
        sbSizerList.AddWindow(self.list, 1, wxALL | wxEXPAND, 0)
        panelList.SetSizer(sbSizerList)
        panelList.SetAutoLayout(true)
        sbSizerList.Fit(panelList)

        hboxDict.Add(panelList, 1, wxALL | wxEXPAND, 0)
        hboxDict.Add(vboxEditButtons, 0, wxALL | wxEXPAND, 5)
        vboxDict.Add(hboxDict, 1, wxALL | wxEXPAND, 0)
        vboxMain.Add(vboxDict, 1, wxALL | wxEXPAND, 10)

        self.buttonNew = wxButton(self, 6030, _("Create new dictionary..."))
        hboxButtons.Add(self.buttonNew, 1, wxALL | wxEXPAND, 1)

        self.buttonOpen = wxButton(self, 6031, _("Open existing..."))
        hboxButtons.Add(self.buttonOpen, 1, wxALL | wxEXPAND, 1)

        self.buttonClose = wxButton(self, 6032, _("Close"))
        hboxButtons.Add(self.buttonClose, 1, wxALL | wxEXPAND, 1)

        vboxMain.Add(hboxButtons, 0, wxALL | wxEXPAND, 2)

        self.SetSizer(vboxMain)
        self.Fit()

        EVT_BUTTON(self, 6000, self.onAddWord)
        EVT_BUTTON(self, 6001, self.onEdit)
        EVT_BUTTON(self, 6002, self.onRemove)
        EVT_BUTTON(self, 6003, self.onSearch)
        EVT_BUTTON(self, 6004, self.onSort)
        EVT_BUTTON(self, 6005, self.onSave)
        EVT_BUTTON(self, 6030, self.onCreate)
        EVT_BUTTON(self, 6031, self.onOpen)
        EVT_BUTTON(self, 6032, self.onClose)
        EVT_CLOSE(self, self.onClose)


    def onAddWord(self, event):
        self.SetStatusText("")
        
        window = self.CreateNewWordWindow(self, -1, _("New Word"),
                                          size=(-1, -1), pos=(-1, -1),
                                          style=wxDEFAULT_FRAME_STYLE)
        window.CentreOnScreen()
        window.Show(True)           

    def onEdit(self, event):
        self.SetStatusText("")
        
        word = self.list.GetStringSelection()
        if word == "":
            return

        window = self.EditWordWindow(word, self, -1, _("Edit Word"),
                                     size=(-1, -1), pos=(-1, -1),
                                     style=wxDEFAULT_FRAME_STYLE)
        window.CentreOnScreen()
        window.Show(True) 

    def onRemove(self, event):
        self.SetStatusText("")
        word = self.list.GetStringSelection()
        if word != "":
            del self.parser.mapping[word]
            self.list.Delete(self.list.FindString(word))

    def onSearch(self, event):
        self.SetStatusText("")

    def onSort(self, event):
        
        words = self.parser.mapping.keys()
        
        if len(words) == 0:
            self.SetStatusText(_("List is empty"))
            return
        
        words.sort()
        self.list.Clear()
        self.list.InsertItems(words, 0)
        self.SetStatusText(_("List sorted"))

    def onSave(self, event):
        self.cAction = "save"
        self.save(self)
    
    def save(self, instance):
        instance.SetStatusText("")
        
        if instance.saved == 0:
            dialog = wxFileDialog(instance, _("Save new TMX dictionary"), "", "mydict.tmx",
                                  style=wxSAVE | wxOVERWRITE_PROMPT)
            if dialog.ShowModal() == wxID_OK:
                instance.file = dialog.GetPaths()[0]
                
                if os.path.isdir(instance.file):
                    print "DictEditor: user seems to be saving file to mydict.tmx"
                    path = os.path.split(instance.file)[0]
                    instance.file = path + os.path.sep + "mydict.tmx"
                    instance.SetTitle("%s: %s" % (instance.priTitle, "mydict.tmx"))
                else:
                    instance.SetTitle("%s: %s" % (instance.priTitle,
                                              os.path.split(instance.file)[1]))
                
                instance.saved = 1
            else:
                print "DictEditor: save canceled"
                return 0
        
        if info.__unicode__:
            code = u"<?xml version=\"1.0\" encoding=\"utf-8\"?>\n" \
                   "<tmx version=\"1.1\">\n"
        else:
            code = "<?xml version=\"1.0\" encoding=\"%s\"?>\n" \
                   "<tmx version=\"1.1\">\n" % info.__enc__
                   
        code += instance.tmxDictHeader(instance.parser)
        code += "  <body>\n"

        words = instance.parser.mapping.keys()
        words.sort()

        print "Words:", len(words)

        for word in words:
            code += "    <tu>\n"
            code += "      <tuv lang=\"%s\">\n" % instance.parser.header["srclang"]
            code += "        <seg>%s</seg>\n" % word.replace("<", 
                                                "&lt;").replace(">", "&gt;")
            code += "      </tuv>\n"
            code += "      <tuv lang=\"%s\">\n" % instance.parser.lang
            for seg in instance.parser.mapping[word]:
                # FIXME: what's a bug???
                code += "        <seg>%s</seg>\n" % seg
            code += "      </tuv>\n"
            code += "    </tu>\n"

        code += "  </body>\n" \
                "</tmx>\n"
        
        fd = open(instance.file, "w")
        
        if info.__unicode__:
            try:
                
                sw = codecs.lookup("utf-8")[3]
                fd = sw(fd)
                
            except:
                instance.SetStatusText(_("Can't save changes to %s") % instance.file)
                printError()
                
                return 1
                
        fd.write(code)
        fd.close()
        instance.SetStatusText(_("Saved"))
        self.changed = 0

    def onCreate(self, event):
        self.list.Clear()

        self.parser = TMXParser()
        self.parser.header["o-tmf"] = "ABCTransMem"
        self.parser.header["creationtool"] = "OpenDict"
        self.parser.header["adminlang"] = "en-us"
        self.parser.header["creationtoolversion"] = __version__
        self.parser.header["srclang"] = "UnknownSourceLang"
        self.parser.lang = "UnknownTransLang"
        self.parser.header["datatype"] = "PlainText"
        self.parser.header["segtype"] = "sentence"
        
        self.name = _("Untitled")
        self.SetTitle("%s: %s" % (self.priTitle, self.name))
        
        self.SetStatusText(_("Empty dictionary created"))
        
        for button in self.controlButtons:
            button.Enable(1)
        
        self.saved = 0
        self.changed = 0

    def onOpen(self, event):
        if self.parser and self.changed:
                window = self.ConfirmExitWindow(self, -1, _("Exit confirmation"))
                self.cAction = "open"
                window.CentreOnScreen()
                window.Show(True)
        else:
            self.open()
        
    def open(self):
        dialog = wxFileDialog(self, _("Choose TMX dictionary file"), "", "",
                              "", wxOPEN|wxMULTIPLE)
        if dialog.ShowModal() == wxID_OK:
            name = os.path.split(dialog.GetPaths()[0])[1]
            self.file = dialog.GetPaths()[0]
            self.name = os.path.split(self.file)[1]
            try:
                self.parser = TMXParser(self.file, None)
            except:
                self.SetStatusText(_("Error: failed to load \"%s\"") % \
                                   self.name)
                return
            
            self.SetTitle("%s: %s" % (self.priTitle, self.name))
            
            self.list.Clear()
            words = self.parser.mapping.keys()
            words.sort()
            
            self.list.InsertItems(words
            , 0)
            
            for word in words:
                print self.parser.mapping[word]
            
            for button in self.controlButtons:
                button.Enable(1)
            
            self.SetStatusText(_("Dictionary loaded"))
            
    def onClose(self, event):
        
        if self.parser and self.changed:
            self.cAction = "close"
            window = self.ConfirmExitWindow(self, -1, _("Exit confirmation"))
            window.CentreOnScreen()
            window.Show(True)
        else:
            self.Destroy()

    def tmxDictHeader(self, parser):

        # New header
        code = "  <header " \
               "o-tmf=\"%s\" " \
               "creationtool=\"%s\" " \
               "creationtoolversion=\"%s\" " \
               "adminlang=\"%s\" " \
               "srclang=\"%s\" " \
               "datatype=\"%s\" " \
               "segtype=\"%s\" />\n" % \
               (parser.header["o-tmf"],
                parser.header["creationtool"],
                parser.header["creationtoolversion"],
                parser.header["adminlang"],
                parser.header["srclang"],
                parser.header["datatype"],
                parser.header["segtype"])

        return code
