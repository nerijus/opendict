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

from misc import encodings, printError
from info import __version__
from parser import TMXParser

_ = wxGetTranslation

# IDs range: 6000-6200
class DictEditorWindow(wxFrame):

    """Built-in dictionary editor. This tool lets user create and
    manage its own dictionaries in TMX format."""

    # IDs range: 6050-6060
    class CreateNewDictWindow(wxFrame):

        """Enter some info and create new dictionary"""

        def __init__(self, parent, id, title, pos=wxDefaultPosition,
                 size=wxDefaultSize, style=wxDEFAULT_FRAME_STYLE):
            wxFrame.__init__(self, parent, id, title, pos, size, style)

            vboxMain = wxBoxSizer(wxVERTICAL)
            hboxButtons = wxBoxSizer(wxHORIZONTAL)
            boxInfo = RowColSizer()


            boxInfo.Add(wxStaticText(self, -1, _("Source language: ")),
                        flag=wxALIGN_RIGHT | wxALIGN_CENTER_VERTICAL,
                        row=0, col=0, border=1)

            langs = ["CS", "DE", "EN", "ES", "FI", "FR", "IS", "JA",
                       "LT", "LV", "PL", "RU", "SV", "UK"]
            self.choiceSrcLang = wxComboBox(self, -1, "",
                                         choices=langs)
            boxInfo.Add(self.choiceSrcLang, flag=wxEXPAND,
                        row=0, col=1, border=1)

            boxInfo.Add(wxStaticText(self, -1, _("Translation language: ")),
                        flag=wxALIGN_RIGHT | wxALIGN_CENTER_VERTICAL,
                        row=1, col=0, border=1)

            self.choiceLang = wxComboBox(self, -1, "",
                                         choices=langs)
            boxInfo.Add(self.choiceLang, flag=wxEXPAND, row=1, col=1, border=1)

            #self.entryLang = wxTextCtrl(self, -1, "")
            #boxInfo.Add(self.entryLang, flag=wxEXPAND, row=0, col=1, border=1)

            #boxInfo.Add(wxStaticText(self, -1, _("Segment type: ")),
            #            flag=wxALIGN_RIGHT | wxALIGN_CENTER_VERTICAL,
            #            row=1, col=0, border=1)

            #self.choiceSeg = wxComboBox(self, -1, "sentence",
            #                           choices=["block", "paragraph",
            #                                    "sentence", "phrase"],
            #                           style=wxTE_READONLY)
            #boxInfo.Add(self.choiceSeg, flag=wxEXPAND, row=1, col=1, border=1)

            #boxInfo.Add(wxStaticText(self, -1, _("Author: ")),
            #            flag=wxALIGN_RIGHT | wxALIGN_CENTER_VERTICAL,
            #            row=2, col=0, border=1)

            #self.entryAuthor = wxTextCtrl(self, -1, "")
            #boxInfo.Add(self.entryAuthor, flag=wxEXPAND,
            #            row=2, col=1, border=1)

            boxInfo.AddGrowableCol(1)
            vboxMain.Add(boxInfo, 1, wxALL | wxEXPAND, 2)

            self.buttonOK = wxButton(self, 6050, _("Save"))
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
            dialog = wxFileDialog(self, _("Save TMX file"), "", "mydict.tmx",
                                  style=wxSAVE|wxOVERWRITE_PROMPT)
            if dialog.ShowModal():
                print "Saving..."
                path = dialog.GetPaths()[0]
                print path

                lang = self.choiceLang.GetValue()
                srclang = self.choiceSrcLang.GetValue()
                segment = "sentence" # default one yet
                #author = self.entryAuthor.GetValue()
                
                if lang == "":
                    lang = "EN"
                #if author == "":
                #    author = "unknown"
                if srclang == "":
                    srclang = "unknown"
                    
                parent = self.GetParent()
                parent.file = path
                #parent.tool = "OpenDict %s" % __version__
                #parent.lang = lang
                
                parent.labelName.SetLabel(_("File name: %s") % os.path.split(path)[1])
                #parent.labelLang.SetLabel(_("Source language: %s") % lang)
                parent.list.Clear()

                parent.parser = TMXParser()
                
                parent.parser.header["o-tmf"] = "ABCTransMem"
                parent.parser.header["creationtool"] = "OpenDict"
                parent.parser.header["adminlang"] = "en-us"
                parent.parser.header["creationtoolversion"] = __version__
                parent.parser.header["srclang"] = srclang
                parent.parser.lang = lang
                parent.parser.header["datatype"] = "PlainText"
                parent.parser.header["segtype"] = "sentence"
                
                tmx = "<?xml version=\"1.0\"?>\n" \
                      "<tmx version=\"1.1\">\n"
                tmx += parent.tmxDictHeader(parent.parser)
                tmx += "  <body>\n" \
                       "  </body>\n" \
                       "</tmx>\n"
                
                fd = open(path, "w")
                fd.write(tmx)
                fd.close()
            
            self.Destroy()

        def onClose(self, event):
            self.Destroy()

    
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

            self.buttonOK = wxButton(self, 6050, _("Save"))
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
            trans = self.text.GetValue()

            parent.parser.mapping[word] = [trans]
            parent.list.Append(word)

            self.Destroy()

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

            self.buttonOK = wxButton(self, 6050, _("Save"))
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
            trans = self.text.GetValue()
            parent.parser.mapping[word] = [trans]

            self.Destroy()

        def onClose(self, event):
            self.Destroy()


    # -------------------------------------------------------------
    def __init__(self, parent, id, title, pos=wxDefaultPosition,
                 size=wxDefaultSize, style=wxDEFAULT_FRAME_STYLE):
        wxFrame.__init__(self, parent, id, title, pos, size, style)

        self.app = wxGetApp()
        self.CreateStatusBar()

        self.parser = None

        vboxMain = wxBoxSizer(wxVERTICAL)
        vboxDict = wxBoxSizer(wxVERTICAL)
        vboxList = wxBoxSizer(wxVERTICAL)
        hboxDict = wxBoxSizer(wxHORIZONTAL)
        vboxEditButtons = wxBoxSizer(wxVERTICAL)
        hboxButtons = wxBoxSizer(wxHORIZONTAL)

        self.labelName = wxStaticText(self, -1, _("File name: %s") % "")
        vboxDict.Add(self.labelName, 0, wxALL, 0)

        #self.labelTool = wxStaticText(self, -1, _("Creation tool: %s") % "")
        #vboxDict.Add(self.labelTool, 0, wxALL, 0)

        #self.labelLang = wxStaticText(self, -1, _("Source language: %s") % "")
        #vboxDict.Add(self.labelLang, 0, wxALL, 0)

        self.buttonAdd = wxButton(self, 6000, _("Add word"))
        vboxEditButtons.Add(self.buttonAdd, 0, wxALL | wxEXPAND, 1)

        self.buttonEdit = wxButton(self, 6001, _("Edit selected"))
        vboxEditButtons.Add(self.buttonEdit, 0, wxALL | wxEXPAND, 1)

        self.buttonRemove = wxButton(self, 6002, _("Remove selected"))
        vboxEditButtons.Add(self.buttonRemove, 0, wxALL | wxEXPAND, 1)

        self.buttonSearch = wxButton(self, 6003, _("Search"))
        vboxEditButtons.Add(self.buttonSearch, 0, wxALL | wxEXPAND, 1)

        self.buttonSort = wxButton(self, 6004, _("Sort"))
        vboxEditButtons.Add(self.buttonSort, 0, wxALL | wxEXPAND, 1)

        self.buttonSave = wxButton(self, 6005, _("Save"))
        vboxEditButtons.Add(self.buttonSave, 0, wxALL | wxEXPAND, 1)

        self.list = wxListBox(self, 6020,
                              wxPoint(-1, -1),
                              wxSize(-1, -1),
                              [],
                              wxLB_SINGLE | wxSUNKEN_BORDER)
        vboxList.Add(self.list, 1, wxALL | wxEXPAND, 0)

        #hboxNav = wxBoxSizer(wxHORIZONTAL)
        #
        #buttonBegin = wxButton(self, 6011)
        #bmp = wxBitmap(os.path.join(home, "pixmaps", "search.xpm"),
        #               wxBITMAP_TYPE_XPM)
        #buttonBegin = wxBitmapButton(self, 150, bmp, (16, 16),
        #                                 style=wxNO_BORDER)
        #hboxNav.Add(buttonBegin, 
        
        hboxDict.Add(vboxList, 1, wxALL | wxEXPAND, 0)
        hboxDict.Add(vboxEditButtons, 0, wxALL | wxEXPAND, 0)
        vboxDict.Add(hboxDict, 1, wxALL | wxEXPAND, 0)
        vboxMain.Add(vboxDict, 1, wxALL | wxEXPAND, 10)

        self.buttonNew = wxButton(self, 6030, _("Create new..."))
        hboxButtons.Add(self.buttonNew, 1, wxALL | wxEXPAND, 1)

        self.buttonOpen = wxButton(self, 6031, _("Open TMX file..."))
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
        if self.parser == None:
            self.SetStatusText(_("There is no opened dictionary"))
            return

        window = self.CreateNewWordWindow(self, -1, _("New Word"),
                                          size=(-1, -1), pos=(-1, -1),
                                          style=wxDEFAULT_FRAME_STYLE)
        window.CentreOnScreen()
        window.Show(True)           

    def onEdit(self, event):
        word = self.list.GetStringSelection()
        if word == "":
            return

        window = self.EditWordWindow(word, self, -1, _("Edit Word"),
                                     size=(-1, -1), pos=(-1, -1),
                                     style=wxDEFAULT_FRAME_STYLE)
        window.CentreOnScreen()
        window.Show(True) 

    def onRemove(self, event):
        print "Remove word"

    def onSearch(self, event):
        print "Search"

    def onSort(self, sort):
        print "Sort"

    def onSave(self, sort):

        code = "<?xml version=\"1.0\"?>\n" \
               "<tmx version=\"1.1\">\n"
        code += self.tmxDictHeader(self.parser)
        code += "  <body>\n"

        words = self.parser.mapping.keys()
        words.sort()

        print "Words:", len(words)

        for word in words:
            code += "    <tu>\n"
            code += "      <tuv lang=\"%s\">\n" % self.parser.header["srclang"]
            code += "        <seg>%s</seg>\n" % word
            code += "      </tuv>\n"
            code += "      <tuv lang=\"%s\">\n" % self.parser.lang
            for seg in self.parser.mapping[word]:
                # FIXME: what's a bug???
                code += "        <seg>%s</seg>\n" % seg
            code += "      </tuv>\n"
            code += "    </tu>\n"

        code += "  </body>\n" \
                "</tmx>\n"
        
        try:
            fd = open(self.file, "w")
            fd.write(code)
            fd.close()
            self.SetStatusText(_("Saved"))
        except:
            self.SetStatusText(_("Can't save changes to %s") % self.file)
            printError()

    def onCreate(self, event):
        print "Creating new"
        new = self.CreateNewDictWindow(self, -1, _("New TMX Dictionary"),
                                       size=(-1, -1),
                                       style=wxDEFAULT_FRAME_STYLE)
        new.CentreOnScreen()
        new.Show(True)

    def onOpen(self, event):
        dialog = wxFileDialog(self, _("Choose TMX dictionary file"), "", "",
                              "", wxOPEN|wxMULTIPLE)
        if dialog.ShowModal() == wxID_OK:
            name = os.path.split(dialog.GetPaths()[0])[1]
            self.file = dialog.GetPaths()[0]
            self.parser = TMXParser(self.file, None)
            self.labelName.SetLabel(_("File name: %s") % name)
            #print "Tool: '%s'" % parser.tool
            #self.labelTool.SetLabel(_("Creation tool: %s") % parser.tool)
            #self.labelLang.SetLabel(_("Source language: %s") % parser.srclang)
            
            self.list.Clear()
            words = self.parser.mapping.keys()
            words.sort()
            self.list.InsertItems(words, 0)

    def onClose(self, event):
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
