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

# TODO: not usable yet, needs some work with encodings, gui, etc.

from wxPython.wx import *
from wxPython.lib.rcsizer import RowColSizer
import wx
import os
import codecs
import traceback

from lib.logger import systemLog, debugLog, DEBUG, INFO, WARNING, ERROR
from lib.misc import encodings, printError
from lib.parser import TMXParser
from lib.gui import errorwin
from lib import info
from lib import dicteditor
from lib import enc

_ = wxGetTranslation


class EditWordWindow(wxFrame):
    """Word editor window"""

    def __init__(self, word, parent, id, title, pos=wxDefaultPosition,
             size=wxDefaultSize, style=wxDEFAULT_FRAME_STYLE):
        wxFrame.__init__(self, parent, id, title, pos, size, style)

        vboxMain = wxBoxSizer(wxVERTICAL)
        hboxButtons = wxBoxSizer(wxHORIZONTAL)
        self.boxInfo = RowColSizer()


        self.boxInfo.Add(wxStaticText(self, -1, _("Word: "), pos=(-1, -1)),
                         flag=wxALIGN_RIGHT | wxALIGN_CENTER_VERTICAL,
                         row=0, col=0, border=1)

        self.entryWord = wxTextCtrl(self, -1, word)
        self.entryWord.Disable()
        self.boxInfo.Add(self.entryWord, flag=wxEXPAND,
                         row=0, col=1, border=1)


        self.transLabels = {}
        self.textEntries = {}

        unit = parent.editor.getUnit(word)

        if unit:
            translations = unit.getTranslations()
            for trans in translations:
                comment = translations[trans]
                if comment:
                    transcomm = u"%s // %s" % (trans, comment)
                else:
                    transcomm = trans
                    
                transcomm = enc.toWX(transcomm)
                
                self.onAddEmptyField(None)
                entry = self.textEntries.get(max(self.textEntries.keys()))
                if entry:
                    entry.SetValue(transcomm)

        self.boxInfo.AddGrowableCol(1)
        vboxMain.Add(self.boxInfo, 1, wxALL | wxEXPAND, 2)

        idAdd = wx.NewId()
        self.buttonAdd = wxButton(self, idAdd, _("Add translation field"))
        vboxMain.Add(self.buttonAdd, 0, wxALL | wxALIGN_RIGHT, 2)

        self.buttonOK = wxButton(self, 6050, _("OK"))
        hboxButtons.Add(self.buttonOK, 0, wxALL, 1)

        self.buttonCancel = wxButton(self, 6051, _("Cancel"))
        hboxButtons.Add(self.buttonCancel, 0, wxALL, 1)

        vboxMain.Add(hboxButtons, 0, wxALL | wxALIGN_RIGHT, 2)

        self.SetSizer(vboxMain)
        self.Fit()
        self.SetSize((500, -1))

        self.Bind(wx.EVT_BUTTON, self.onAddEmptyField, self.buttonAdd)
        self.Bind(wx.EVT_BUTTON, self.onSave, self.buttonOK)
        self.Bind(wx.EVT_BUTTON, self.onClose, self.buttonCancel)


    def onAddEmptyField(self, event):
        """Add empty translation field"""

        transLabel = wxStaticText(self, -1, _("Translation #%d: " \
                                              % (len(self.textEntries)+1)))
        self.transLabels[len(self.transLabels)] = transLabel
        self.boxInfo.Add(transLabel,
                         flag=wx.ALIGN_RIGHT | wx.ALIGN_CENTRE_VERTICAL,
                         row=len(self.transLabels), col=0, border=1)

        text = wxTextCtrl(self, -1,
                          "",
                          size=(100, -1))

        self.textEntries[len(self.textEntries)] = text

        self.boxInfo.Add(text, flag=wxEXPAND,
                         row=len(self.textEntries),
                         col=1, border=1)

        self.Fit()
        self.SetSize((500, -1))


    def onSave(self, event):
        """Apply changes"""

        parent = self.GetParent()
        word = enc.fromWX(self.entryWord.GetValue())

        translations = []

        for label in self.textEntries.values():
            translations.append(enc.fromWX(label.GetValue()))

        transcomm = {}

        for translation in translations:
            if not len(translation.strip()):
                continue
            chunks = translation.split('//', 1)
            if len(chunks) == 2:
                t = chunks[0]
                c = chunks[1]
            else:
                t = chunks[0]
                c = None

            transcomm[t] = c

        parent.editor.getUnit(word).setTranslations(transcomm)
        parent.setChanged(True)
        parent.checkAllButtons()

        self.Destroy()


    def onClose(self, event):
        """Close window withous saveing changes"""

        self.Destroy()



# IDs range: 6000-6200
class DictEditorWindow(wxFrame):

    """Built-in dictionary editor. This tool lets user create and
    manage his own dictionaries in TMX format."""

    class AddWordWindow(EditWordWindow):
        """Window for adding new word"""

        def __init__(self, parent, id, title, pos=wxDefaultPosition,
                 size=wxDefaultSize, style=wxDEFAULT_FRAME_STYLE):

            EditWordWindow.__init__(self, '', parent, id, title, pos,
                                    size, style)
            
            self.entryWord.Enable(1)
            self.onAddEmptyField(None)


        def onSave(self, event):
            """Apply changes"""

            parent = self.GetParent()
            word = enc.fromWX(self.entryWord.GetValue())

            translations = []

            for label in self.textEntries.values():
                translations.append(enc.fromWX(label.GetValue()))

            transcomm = {}

            for translation in translations:
                if not len(translation.strip()):
                    continue
                chunks = translation.split('//', 1)
                if len(chunks) == 2:
                    t = chunks[0]
                    c = chunks[1]
                else:
                    t = chunks[0]
                    c = None

                transcomm[t] = c

            unit = dicteditor.Translation()
            unit.setWord(word)
            unit.setTranslations(transcomm)
            parent.editor.addUnit(unit)
            parent.list.Append(enc.toWX(word))
            
            parent.setChanged(True)
            parent.checkAllButtons()

            self.Destroy()



    # IDs range: 6000-6003
    class ConfirmExitWindow(wxDialog):
        """Save confirmation dialog"""

        def __init__(self, parent, id, title, pos=wxDefaultPosition,
                 size=wxDefaultSize, style=wxDEFAULT_DIALOG_STYLE):
            
            wxDialog.__init__(self, parent, id, title, pos, size, style)

            self.parent = self.GetParent()
            
            vboxMain = wxBoxSizer(wxVERTICAL)
            hboxButtons = wxBoxSizer(wxHORIZONTAL)
            
            labelMsg = wxStaticText(self, -1,
                                    _("Dictionary \"%s\" has been changed") \
                                    % parent.name)
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
            
            if self.parent.cAction == "save":
                self.parent.onSave(None)
                self.parent.Destroy()
            elif self.parent.cAction == "open":
                self.parent.onSave(None)
                self.Hide()
                self.parent.open()
            elif self.parent.cAction == "close":
                self.parent.onSave(None)
                self.parent.Destroy()
                
            
        def onExitParent(self, event):
            
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
        self.savedOnce = False
        self.changed = False
        self.editor = dicteditor.Editor()
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
        self.buttonAdd.SetToolTipString(_("Add word"))
        self.controlButtons.append(self.buttonAdd)
        
        self.buttonEdit = wxButton(self, 6001, _("Edit"))
        self.buttonEdit.SetToolTipString(_("Change translation"))
        self.controlButtons.append(self.buttonEdit)

        self.buttonRemove = wxButton(self, 6002, _("Remove"))
        self.buttonRemove.SetToolTipString(_("Remove selected word"))
        self.controlButtons.append(self.buttonRemove)

        self.buttonSort = wxButton(self, 6004, _("Sort"))
        self.buttonSort.SetToolTipString(_("Sort word list"))
        self.controlButtons.append(self.buttonSort)

        self.buttonSave = wxButton(self, 6005, _("Save"))
        self.buttonSave.SetToolTipString(_("Save words to file"))
        self.controlButtons.append(self.buttonSave)

        self.buttonSaveAs = wxButton(self, 6006, _("Save As..."))
        self.buttonSaveAs.SetToolTipString(_("Save with a different file name"))
        self.controlButtons.append(self.buttonSaveAs)
        
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
                              
        sbSizerList.Add(self.list, 1, wxALL | wxEXPAND, 0)
        panelList.SetSizer(sbSizerList)
        panelList.SetAutoLayout(true)
        sbSizerList.Fit(panelList)

        hboxDict.Add(panelList, 1, wxALL | wxEXPAND, 0)
        hboxDict.Add(vboxEditButtons, 0, wxALL | wxEXPAND, 5)
        vboxDict.Add(hboxDict, 1, wxALL | wxEXPAND, 0)
        vboxMain.Add(vboxDict, 1, wxALL | wxEXPAND, 10)

        self.buttonNew = wxButton(self, 6030, _("New..."))
        self.buttonNew.SetToolTipString(_("Start new dictionary"))
        hboxButtons.Add(self.buttonNew, 0, wxALL | wxEXPAND, 1)

        self.buttonOpen = wxButton(self, 6031, _("Open..."))
        self.buttonOpen.SetToolTipString(_("Open dictionary file"))
        hboxButtons.Add(self.buttonOpen, 0, wxALL | wxEXPAND, 1)

        self.buttonClose = wxButton(self, 6032, _("Close"))
        self.buttonClose.SetToolTipString(_("Close editor window"))
        hboxButtons.Add(self.buttonClose, 0, wxALL | wxEXPAND, 1)

        vboxMain.Add(hboxButtons, 0, wxALL | wxALIGN_RIGHT, 2)

        self.SetIcon(wxIcon(os.path.join(info.GLOBAL_HOME,
                                        "pixmaps",
                                        "icon-24x24.png"),
                            wxBITMAP_TYPE_PNG))

        self.SetSizer(vboxMain)

        self.Bind(wx.EVT_LISTBOX, self.onWordSelected, self.list)
        self.Bind(wx.EVT_BUTTON, self.onCreate, self.buttonNew)

        EVT_BUTTON(self, 6000, self.onAddWord)
        EVT_BUTTON(self, 6001, self.onEdit)
        EVT_BUTTON(self, 6002, self.onRemove)
        EVT_BUTTON(self, 6003, self.onSearch)
        EVT_BUTTON(self, 6004, self.onSort)
        EVT_BUTTON(self, 6005, self.onSave)
        EVT_BUTTON(self, 6006, self.onSaveAs)
        EVT_BUTTON(self, 6031, self.onOpen)
        EVT_BUTTON(self, 6032, self.onClose)
        EVT_CLOSE(self, self.onClose)


    def onAddWord(self, event):
        
        self.SetStatusText("")
        
        window = self.AddWordWindow(self, -1, _("New Word"),
                                    size=(-1, -1), pos=(-1, -1),
                                    style=wxDEFAULT_FRAME_STYLE)
        window.CentreOnScreen()
        window.Show(True)


    def onEdit(self, event):
        
        self.SetStatusText("")
        
        word = self.list.GetStringSelection()
        if word == "":
            return

        window = EditWordWindow(word, self, -1, _("Edit Word"),
                                size=(-1, -1),
                                style=wxDEFAULT_FRAME_STYLE)
        window.CentreOnScreen()
        window.Show(True)

        self.checkAllButtons()


    def onRemove(self, event):
        
        self.SetStatusText("")
        word = self.list.GetStringSelection()
        if word != "":
            self.list.Delete(self.list.FindString(word))
        self.editor.removeUnit(self.editor.getUnit(word))
        self.setChanged(True)
        self.checkAllButtons()


    def onSearch(self, event):
        
        self.SetStatusText("")


    def onSort(self, event):
        
        words = []
        for unit in self.editor.getUnits():
            words.append(unit.getWord())
        
        if len(words) == 0:
            self.SetStatusText(_("List is empty"))
            return
        
        words.sort()
        self.list.Clear()
        self.list.InsertItems(words, 0)
        self.SetStatusText(_("List sorted"))

        self.setChanged(True)
        self.checkAllButtons()


    def onSaveAs(self, event):

        self.onSave(None)


    def onSave(self, event):

        self.SetStatusText("")
        self.cAction = "save"

        wildCard = "Slowo dictionaries (*.dwa)|*.dwa"
        default = 'Untitled-dictionary.dwa'

        if not self.savedOnce or not event:
            dialog = wx.FileDialog(self,
                                   wildcard=wildCard,
                                   defaultFile=default,
                                   message=_("Save file"),
                                   style=wx.SAVE | wx.CHANGE_DIR)
            if dialog.ShowModal() == wx.ID_OK:
                self.filePath = dialog.GetPaths()[0]
            else:
                return

        if os.path.isdir(self.filePath):
            if self.filePath.endswith('..'):
                self.filePath = self.filePath[:-2]

            self.filePath += default

        if not self.filePath.endswith('.dwa'):
            self.filePath += '.dwa'

        self.editor.save(self.filePath)
        self.setChanged(False)
        self.name = os.path.basename(self.filePath)
        self.savedOnce = True
        self.checkAllButtons()
        self.SetStatusText(_("Dictionary saved"))
        self.SetTitle("%s - %s" % (self.priTitle, self.name))


    def onCreate(self, event):

        self.editor = dicteditor.Editor()
        self.list.Clear()
        self.checkAllButtons()
        self.savedOnce = False
        self.name = _("Untitled")
        self.SetStatusText("")
        self.SetTitle("%s - %s" % (self.priTitle, self.name))


    def checkAddButton(self):
        """Check for add button visibility"""

        if not hasattr(self, 'editor'):
            self.buttonAdd.Disable()
        else:
            self.buttonAdd.Enable(1)


    def checkEditButton(self):
        """Check for edit button visibility"""

        if self.list.GetSelection() == -1:
            self.buttonEdit.Disable()
        else:
            self.buttonEdit.Enable(1)


    def checkRemoveButton(self):
        """Check for remove button visibility"""

        if self.list.GetSelection() == -1:
            self.buttonRemove.Disable()
        else:
            self.buttonRemove.Enable(1)


    def checkSortButton(self):
        """Check for sort button visibility"""

        if not hasattr(self, 'editor'):
            self.buttonSort.Disable()
        elif len(self.editor.getUnits()) < 2:
            self.buttonSort.Disable()
        else:
            self.buttonSort.Enable(1)


    def checkSaveButton(self):
        """Check for save button visibility"""

        if not hasattr(self, 'editor'):
            self.buttonSave.Disable()
        elif not self.changed:
            self.buttonSave.Disable()
        else:
            self.buttonSave.Enable(1)


    def checkAllButtons(self):
        """Check all buttons for visibility changes"""

        self.checkAddButton()
        self.checkEditButton()
        self.checkRemoveButton()
        self.checkSortButton()
        self.checkSaveButton()

        self.buttonSaveAs.Enable(True)
        

    def onOpen(self, event):
        
        if self.editor and self.changed:
                window = self.ConfirmExitWindow(self,
                                                -1,
                                                _("Exit confirmation"))
                self.cAction = "open"
                window.CentreOnScreen()
                window.Show(True)
        else:
            self.open()
            self.savedOnce = True # no need to specify file name

        
    def open(self):
        wildCard = "Slowo dictionaries (*.dwa)|*.dwa"
        
        dialog = wxFileDialog(self, message=_("Choose dictionary file"),
                              wildcard=wildCard, style=wxOPEN|wxMULTIPLE)
        if dialog.ShowModal() == wxID_OK:
            name = os.path.split(dialog.GetPaths()[0])[1]
            self.filePath = dialog.GetPaths()[0]
            self.name = os.path.split(self.filePath)[1]

            wx.BeginBusyCursor()
            
            try:
                self.editor.load(self.filePath)
            except Exception, e:
                wx.EndBusyCursor()
                traceback.print_exc()
                title = _("Open Failed")
                msg = _("Unable to open dictionary (got message: %s" % e)
                errorwin.showErrorMessage(title, msg)
                
                return
            
            self.SetTitle("%s - %s" % (self.priTitle, self.name))
            
            self.list.Clear()
            words = []
            for unit in self.editor.getUnits():
                words.append(enc.toWX(unit.getWord()))
            words.sort()

            self.list.InsertItems(words, 0)
            self.checkAllButtons()
            self.SetStatusText(_("Dictionary loaded"))

            wx.EndBusyCursor()


    def onWordSelected(self, event):
        """This method is invoked when list item is selected"""

        self.checkAllButtons()

            
    def onClose(self, event):
        
        if self.changed:
            self.cAction = "close"
            window = self.ConfirmExitWindow(self, -1, _("Exit confirmation"))
            window.CentreOnScreen()
            window.Show(True)
        else:
            self.Destroy()


    def setChanged(self, value):
        """Set changed=value"""
        
        self.changed = value


    def getChanged(self):
        """Get if changed"""

        return self.changed
