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
# Module: gui.mainwin

"""
Main window GUI module
"""

from wxPython.wx import *
from wxPython.html import *
import os
import cStringIO

from info import home, uhome, __version__, __enc__
from gui.dictconnwin import DictConnWindow
from gui.groupswin import GroupsWindow
from gui.pluginwin import PluginManagerWindow
from gui.registerwin import FileRegistryWindow
from gui.dicteditorwin import DictEditorWindow
from gui.mywordswin import MyWordsWindow
from gui.dictaddwin import DictAddWindow
from gui.prefswin import PrefsWindow
from gui.helpwin import ManualWindow, LicenseWindow, AboutWindow
from parser import SlowoParser
from parser import MovaParser
from parser import TMXParser
from parser import DictParser
from group import DictionaryGroup
from threads import Process
from mywords import MyWords
from history import History
from installer import Installer
from extra.html2text import html2text
import plugin
import misc, info

_ = wxGetTranslation

class HtmlWindow(wxHtmlWindow):

   """Html control for showing transaltion and catching
   link-clicking"""

   def OnLinkClicked(self, linkinfo):
      #self.base_OnLinkClicked(linkinfo)
      print "LinkInfo: searching for '%s'" % linkinfo.GetHref()
      #print linkinfo.GetTarget()
      wxBeginBusyCursor()
      parent = self.GetParent().GetParent().GetParent()
      parent.SetStatusText(_("Searching..."))
      #parent.buttonStop.Enable(1)
      parent.timerSearch.Start(parent.delay)
      parent.search = Process(parent.dict.search, linkinfo.GetHref())

class MainWindow(wxFrame):

   """Main OpenDict window with basic controls"""

   def __init__(self, parent, id, title, pos=wxDefaultPosition,
                size=wxDefaultSize, style=wxDEFAULT_FRAME_STYLE):
      wxFrame.__init__(self, parent, id, title, pos, size, style)

      self.app = wxGetApp()
      self.printer = wxHtmlEasyPrinting()
      self.history = History()
      self.htmlCode = ""
      self.dictName = ""
      self.encoding = self.app.config.defaultEnc
      self.dict = None
      self.list = []
      self.delay = 10 # miliseconds
      
      self.lastInstalledDictName = None

      # My words list
      self.myWords = MyWords()
       
      try: 
          self.myWords.read()
      except Exception, e:
          print "Warning: Unable to read mywords.txt file"


      # GUI instances
      self.myWordsWindow = None

      # Activation values
      self.activeMyWordsWindow = False 

      # This var is used by onTimerSearch to recognize search method.
      # If search was done by selecting a word in a list, then word list
      # is not updated, otherwise is.
      self.__searchedBySelecting = 0

      # Box sizers
      vboxMain = wxBoxSizer(wxVERTICAL)
      hboxToolbar = wxBoxSizer(wxHORIZONTAL)

      # Menu Bar
      menuBar = wxMenuBar()

      menuFile = wxMenu()
      menuFileOpen = wxMenu()
      menuFileOpen.Append(101, "Slowo dictionary",
                          _("Slowo dictionaries usually have 'dwa' extention"))
      menuFileOpen.Append(102, "Mova dictionary",
                          _("Mova dictionaries usually have 'mova' extention"))
      menuFileOpen.Append(103, "TMX dictionary",
                          _("TMX dictionaries usually have 'tmx' extention"))
      menuFileOpen.Append(104, "DICT dictionary",
                          _("DICT dictionaries usually have " \
                            "'dict' or 'dz' extention"))
      menuFile.AppendMenu(105, _("Load Dictionary From File"), menuFileOpen)

      menuFile.AppendSeparator()
      #menuFile.Append(2004, _("Print Translation"), "")
      #menuFile.Append(2006, _("Print Preview"), "")
      #menuFile.AppendSeparator()
      menuFile.Append(106, _("&Close Dictionary\tCtrl-W"),
                      _("Close opened dicitonary"))
      menuFile.Append(107, _("E&xit\tCtrl-Q"),
                      _("Exit program"))

      menuBar.Append(menuFile, _("&File"))

      menuEdit = wxMenu()

      #
      # Clear functions
      #
      menuEdit.Append(109, _("&Clear Search Entry\tCtrl-L"))
      menuEdit.Append(121, _("Clear History"))

      menuEdit.AppendSeparator()

      #
      # Clipboard functions
      #
      menuEdit.Append(108, _("Copy\tCtrl-C"),
                      _("Copy selected translation text"))
      menuEdit.Append(2005, _("Paste\tCtrl-V"),
                      _("Paste clipboard text into the search entry"))
      
      menuEdit.AppendSeparator()
      
      self.menuEncodings = wxMenu()
      i = 0
      keys = misc.encodings.keys()
      keys.sort()
      for enc in keys:
         self.menuEncodings.AppendRadioItem(2100+i , enc, "")
         EVT_MENU(self, 2100+i, self.onDefault)
         if self.app.config.defaultEnc == misc.encodings[enc]:
            self.menuEncodings.FindItemById(2100+i).Check(1)
         i+=1
      menuEdit.AppendMenu(2000, _("Encoding"), self.menuEncodings)
      self.menuFontFace = wxMenu()
      i = 0
      keys = misc.fontFaces.keys()
      keys.sort()
      for face in keys:
         self.menuFontFace.AppendRadioItem(2500+i, face, "")
         EVT_MENU(self, 2500+i, self.onDefault)
         if self.app.config.fontFace == misc.fontFaces[face]:
            self.menuFontFace.FindItemById(2500+i).Check(1)
         i+=1
      menuEdit.AppendMenu(2001, _("Font Face"), self.menuFontFace)
      self.menuFontSize = wxMenu()
      i = 0
      for size in misc.fontSizes:
         self.menuFontSize.AppendRadioItem(2600+i, size, "")
         EVT_MENU(self, 2600+i, self.onDefault)
         if self.app.config.fontSize == size:
            self.menuFontSize.FindItemById(2600+i).Check(1)
         i+=1
      menuEdit.AppendMenu(2002, _("Font Size"), self.menuFontSize)
      menuEdit.AppendSeparator()
      menuEdit.Append(111, _("Preferences...\tCtrl-P"), _("Edit preferences"))

      menuBar.Append(menuEdit, _("&Edit"))

      self.menuDict = wxMenu()

      keys = self.app.config.plugins.keys()
      keys.sort()
      for name in keys:
         #print "Name:", name
         item = wxMenuItem(self.menuDict,
                           self.app.config.ids[name],
                           name)

         self.menuDict.AppendItem(item)
         EVT_MENU(self, self.app.config.ids[name], self.onDefault)

      keys = self.app.config.registers.keys()
      keys.sort()
      for name in keys:
         item = wxMenuItem(self.menuDict,
                           self.app.config.ids[name],
                           name)
         EVT_MENU(self, self.app.config.ids[name], self.onDefault)
         self.menuDict.AppendItem(item)

      keys = self.app.config.groups.keys()
      keys.sort()
      for name in keys:
         item = wxMenuItem(self.menuDict,
                           self.app.config.ids[name],
                           name)
         self.menuDict.AppendItem(item)
         EVT_MENU(self, self.app.config.ids[name], self.onDefault)

      self.menuDict.AppendSeparator()
      
      self.menuDict.Append(112, _("&Add New Dictionary"))
      
      #menuDictAdd = wxMenu()
      #menuDictAdd.Append(112, _("&Register from file..."))
      #menuDictAdd.Append(113, _("&Install plugin..."))
      #self.menuDict.AppendMenu(114, _("Add new dictionary"), menuDictAdd)

      menuBar.Append(self.menuDict, _("&Dictionaries"))

      menuTools = wxMenu()
      menuTools.Append(110, _("Manage Dictionaries...\tCtrl-M"),
                      _("Install or remove dictionaries, see the information"))

      # FIXME: Remove group classes and files
      #menuTools.Append(122, _("Manage Groups...\tCtrl-G"),
      #                _("Edit groups of dictionaries"))
                      
      #menuTools.Append(110, _("Plugin manager...\tCtrl-M"),
      #                _("Edit plugins"))
      #menuTools.Append(120, _("File Register...\tCtrl-R"),
      #                _("Edit file registers"))
                      
      menuTools.AppendSeparator()
      menuTools.Append(123, _("Connect to DICT Server..."),
                          _("Open connection to DICT server"))

      #menuTools.AppendSeparator()
      
      # Editor can't be used with non-unicode GUI, because unicode
      # string are used with TMX files.

      if info.__unicode__:
          menuTools.Append(5002, _("Dictionaries Editor"),
                          _("Create and manage your own dictionaries"))  

      # FIXME: Remove atitinkamas classes
      #menuTools.Append(5003, _("My Words\tCtrl-W"),
      #                    _("Your significant words list"))
                           
      menuBar.Append(menuTools, _("Tools"))

      menuHelp = wxMenu()
      #menuHelp.Append(115, _("&Manual\tCtrl-H"))
      menuHelp.Append(117, _("&License"))
      menuHelp.Append(116, _("&About\tCtrl-A"))

      menuBar.Append(menuHelp, _("&Help"))

      self.SetMenuBar(menuBar)

      # Search Bar
      labelWord = wxStaticText(self, -1, _("Search for:"));
      hboxToolbar.Add(labelWord, 0, wxALL | wxCENTER, 3)
      
      self.entry = wxComboBox(self, 153, "", wxPoint(-1, -1),
                              wxSize(-1, -1), [], wxCB_DROPDOWN)
      hboxToolbar.Add(self.entry, 1, wxALL | wxCENTER, 1)

      # Search bitmap button
      #bmp = wxBitmap(os.path.join(home, "pixmaps", "search.xpm"),
      #               wxBITMAP_TYPE_XPM)
      #self.buttonSearch = wxBitmapButton(self, 150, bmp, (16, 16),
      #                                   style=wxNO_BORDER)
      #self.buttonSearch = wxButton(self, 150, _("Search"))
      self.buttonSearch = wxButton(self, wx.ID_FIND)
      self.buttonSearch.SetToolTipString(_("Look up word"))
      hboxToolbar.Add(self.buttonSearch, 0, wxALL | wxCENTER, 1)
      
      # Clear bitmap button
      #bmp = wxBitmap(os.path.join(home, "pixmaps", "clear5.xpm"),
      #bmp = wxBitmap(os.path.join(home, "pixmaps", "clear.xpm"),
      #               wxBITMAP_TYPE_XPM)
      #buttonClean = wxBitmapButton(self, 151, bmp, (16, 16),
      #                             style=wxNO_BORDER)
      #buttonClean.SetToolTipString(_("Clear search entry"))
      #hboxToolbar.Add(buttonClean, 0, wxALL | wxCENTER, 1)
      
      # Back button
      bmp = wxBitmap(os.path.join(home, "pixmaps", "left.png"),
                     wxBITMAP_TYPE_PNG)
      self.buttonBack = wxBitmapButton(self, 2010, bmp, (24, 24),
                                         style=wxNO_BORDER)
      self.buttonBack.SetToolTipString(_("Back"))
      self.buttonBack.Disable()
      hboxToolbar.Add(self.buttonBack, 0, wxALL | wxCENTER, 1)

      # Forward button
      bmp = wxBitmap(os.path.join(home, "pixmaps", "right.png"),
                     wxBITMAP_TYPE_PNG)
      self.buttonForward = wxBitmapButton(self, 2011, bmp, (24, 24),
                                         style=wxNO_BORDER)
      self.buttonForward.SetToolTipString(_("Forward"))
      self.buttonForward.Disable()
      hboxToolbar.Add(self.buttonForward, 0, wxALL | wxCENTER, 1)

      # Stop threads
      # TODO: how thread can be killed?
      #bmp = wxBitmap(os.path.join(home, "pixmaps", "stop.xpm"),
      #               wxBITMAP_TYPE_XPM)
      #self.buttonStop = wxBitmapButton(self, 155, bmp, (16, 16),
      #                                 style=wxNO_BORDER)
      #self.buttonStop.SetToolTipString(_("Stop"))
      #self.buttonStop.Disable()
      #hboxToolbar.Add(self.buttonStop, 0, wxALL | wxCENTER, 1)
      #self.buttonStop.Hide()

      #bmp = wxBitmap(os.path.join(home, "pixmaps", "add.xpm"),
      #               wxBITMAP_TYPE_XPM)
      #self.buttonAdd = wxBitmapButton(self, 5004, bmp, (16, 16),
      #                                 style=wxNO_BORDER)
      #self.buttonAdd.SetToolTipString(_("Add current word to \"My Words\""))
      #hboxToolbar.Add(self.buttonAdd, 0, wxALL | wxCENTER, 1)
      
      # List toggle bitmap button
      # If word list isn't hidden for this dict, else...
      self.wlHidden = 0
      bmp = wxBitmap(os.path.join(home, "pixmaps", "hide.xpm"),
                     wxBITMAP_TYPE_XPM)
      self.buttonHide = wxBitmapButton(self, 152, bmp, (24, 24),
                                       style=wxNO_BORDER)
      self.buttonHide.SetToolTipString(_("Hide word list"))
      hboxToolbar.Add(self.buttonHide, 0, wxALL | wxCENTER, 1)

      vboxMain.Add(hboxToolbar, 0, wxALL | wxEXPAND | wxGROW, 0)

      # Splitter Window
      self.splitter = wxSplitterWindow(self, -1)

      # List panel
      self.createListPanel()
      
      # Html window panel
      self.panelHtml = wxPanel(self.splitter, -1)
      sbSizerHtml = wxStaticBoxSizer(wxStaticBox(self.panelHtml, -1, 
                                                 _("Translation")),
                                     wxVERTICAL)
      self.htmlWin = HtmlWindow(self.panelHtml, -1, style=wxSUNKEN_BORDER)
      sbSizerHtml.Add(self.htmlWin, 1, wxALL | wxEXPAND, 0)
      self.panelHtml.SetSizer(sbSizerHtml)
      self.panelHtml.SetAutoLayout(true)
      sbSizerHtml.Fit(self.panelHtml)

      self.splitter.SplitVertically(self.panelList, self.panelHtml,
                                    self.app.config.sashPos)
      self.splitter.SetMinimumPaneSize(90)
      self.splitter.SetSashSize(5)

      if self.dict != None:
         if self.dict.needsList == 0:
            self.hideWordList()

      if not self.dict:
         self.hideWordList()

      vboxMain.Add(self.splitter, 1, wxALL | wxGROW | wxEXPAND, 0)

      # Status bar
      self.CreateStatusBar()

      # Main sizer
      self.SetSizer(vboxMain)

      self.timerSearch = wxTimer(self, 5000)
      self.timerLoad = wxTimer(self, 5001)
      self.search = None
      self.load = None

      # Load default dictionary
      if self.app.config.dict != "":
         try:
            self.SetStatusText(_("Loading \"%s\"...") % self.app.config.dict)
            if self.app.config.plugins.has_key(self.app.config.dict):
               #print "%s found in plugins, loading..." % self.app.config.dict
               self.loadPlugin(self.app.config.dict)

            elif self.app.config.registers.has_key(self.app.config.dict):
               #print "%s found in registers, loading..." % self.app.config.dict
               self.loadRegister(self.app.config.dict)

            elif self.app.config.groups.has_key(self.app.config.dict):
               self.loadGroup(self.app.config.dict)

         except Exception, e:
            self.SetStatusText(_("Error: failed to load \"%s\"") % self.app.config.dict)
            print "Exception:", e
            self.onCloseDict(None)

      # FIMXE: MS Windows doesn't want to show XPM pixmaps in the title bar
      wxInitAllImageHandlers()
      if os.name != "posix":
         icon = wxEmptyIcon()
         data = open(os.path.join(home, "pixmaps", "icon.png"), "rb").read()
         icon.CopyFromBitmap(wxBitmapFromImage(wxImageFromStream(cStringIO.StringIO(data))))
         self.SetIcon(icon)
      else:
         self.SetIcon(wxIcon(os.path.join(home, "pixmaps", "icon.xpm"),
                             wxBITMAP_TYPE_XPM))


      # If there is no dictionary, give user a tip what to do
      #if len(self.app.config.plugins) == 0 \
      #   and len(self.app.config.registers) == 0:
      #   self.SetStatusText(_("To add a dictionary, go to \"Dictionaries->Add new\" menu"))
      #elif self.app.config.dict == "":
      #   self.SetStatusText(_("Choose a dictionary from \"Dictionaries\" menu"))

      # Events
      EVT_MENU(self, 101, self.onOpenSlowo)
      EVT_MENU(self, 102, self.onOpenMova)
      EVT_MENU(self, 103, self.onOpenTMX)
      EVT_MENU(self, 104, self.onOpenDictFile)
      EVT_MENU(self, 2004, self.onPrint)
      EVT_MENU(self, 2006, self.onPreview)
      EVT_MENU(self, 123, self.onOpenDictConn)
      EVT_MENU(self, 106, self.onCloseDict)
      EVT_MENU(self, 107, self.onExit)
      EVT_MENU(self, 108, self.onCopy)
      EVT_MENU(self, 2005, self.onPaste)
      EVT_MENU(self, 109, self.onClean)
      EVT_MENU(self, 112, self.onAddDict)
      #EVT_MENU(self, 113, self.onAddFromPlugin)
      EVT_MENU(self, 121, self.onClearHistory)
      EVT_MENU(self, 122, self.onShowGroupsWindow)
      EVT_MENU(self, 110, self.onShowPluginManager)
      EVT_MENU(self, 120, self.onShowFileRegistry)
      EVT_MENU(self, 5002, self.onShowDictEditor)
      EVT_MENU(self, 5003, self.onShowMyWordList)
      EVT_MENU(self, 111, self.onShowPrefsWindow)
      EVT_MENU(self, 115, self.onManual)
      EVT_MENU(self, 117, self.onLicense)
      EVT_MENU(self, 116, self.onAbout)
      EVT_BUTTON(self, wx.ID_FIND, self.onSearch)
      EVT_BUTTON(self, 2010, self.onBack)
      EVT_BUTTON(self, 2011, self.onForward)
      EVT_BUTTON(self, 155, self.onStop)
      EVT_BUTTON(self, 151, self.onClean)
      EVT_BUTTON(self, 5004, self.onAddMyWord)
      EVT_BUTTON(self, 152, self.onHideUnhide)
      EVT_TEXT_ENTER(self, 153, self.onSearch)
      #EVT_TEXT(self, 153, self.onEntryUpdate)
      EVT_LISTBOX(self, 154, self.onWordSelected)
      EVT_TIMER(self, 5000, self.onTimerSearch)
      EVT_TIMER(self, 5001, self.onTimerLoad)
      EVT_CLOSE(self, self.onCloseWindow)

      # Prepare help message
      helpMessage = _("""
<html>
<head>
<meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\">
</head>
<body>
<h3>Welcome to OpenDict</h3>
<p>
<ul>
<li>To start using dictionary, select one from <i><b>Dictionaries</b></i>
menu.</li>
<li>To add new dictionary, select <i><b>Add New Dictionary</b></i>
from <i><b>Dictionaries</b></i> menu.</li>
</ul>

<p>
For more information visit project's homepage on
<i>http://sourceforge.net/projects/opendict</i>
</p>
</body>
</html>
""")

      # Set startup help message
      self.htmlWin.SetPage(helpMessage)
     

   # Callbacks and other functions

   def onExit(self, event):
      self.onCloseDict(None)
      misc.savePrefs(self)
      self.app.config.writeConfigFile()
      self.Close(True)

   def onCloseWindow(self, event):
      self.onCloseDict(None)
      misc.savePrefs(self)
      self.app.config.writeConfigFile()
      self.Destroy()

   def onTimerSearch(self, event):
      if self.search != None and self.search.isDone():
         wxEndBusyCursor()
         self.timerSearch.Stop()
         self.search.stop()
         #print "Search timer stopped"
         word = self.entry.GetValue()
         
         result = self.search()

         # Checking if dictionary returned valid result
         # (plugin may be bad-written)
         try:
            assert len(result) == 3
         except:
            self.SetStatusText(_(misc.errors[2]))
            #self.buttonStop.Disable()
            self.entry.Enable(1)
            self.entry.SetFocus()
            return

         self.SetStatusText("")
         #self.buttonStop.Disable()
         self.entry.Enable(1)
         self.search = None

         if self.entry.FindString(word) == -1:
            self.entry.Append(word)

         if result[2]:
            print "Errno:", result[2]
            self.SetStatusText(_(misc.errors[result[2]]))
            self.entry.Enable(1)
            self.entry.SetFocus()
            misc.printError()
            return

         self.htmlCode = result[0]
         #print self.htmlCode
         
         #if info.__unicode__ and type(self.htmlCode) != type(u''):
         #   print "WARNING: non-unicode string '%s'" % self.htmlCode
         #   self.htmlCode = unicode(self.htmlCode, __enc__)
         #else:
         #   print "Search result length: %d bytes" % len(self.htmlCode)
         
         if type(self.htmlCode) != type(u''):
            if not info.__unicode__:
                print "Setting page (not encoded)"
                #print self.htmlCode.decode("utf-8")
                try:
                    # FIXME: non-unicode version must be fixed
                    #self.htmlWin.SetPage(self.htmlCode.decode(self.encoding))
                    #self.history.add(self.htmlCode.decode(self.encoding))
                    
                    self.htmlWin.SetPage(self.htmlCode)
                    self.history.add(self.htmlCode)
                except:
                    self.SetStatusText(_(misc.errors[6]))
            else:
                print "Setting page (encoded in %s)" % info.__enc__
                # FIXME: non-unicode version must be fixed
                if hasattr(self.dict, "encoding"):
                    print "Dictionary has an encoding defined, huh!"
                    enc = self.dict.encoding
                else:
                    enc = info.__enc__
                self.htmlWin.SetPage(self.htmlCode.decode(enc))
                self.history.add(self.htmlCode.decode(enc))
         else:
            print "Setting unicode page"
            try:
               #self.htmlWin.SetPage(self.htmlCode)
               self.htmlWin.SetPage(self.htmlCode)#.encode(self.encoding, 
                                                         #"replace"))
               self.history.add(self.htmlCode)#.encode(self.encoding, 
                                                         #"replace"))
               #self.htmlWin.SetPage(result[0].encode(self.encoding, "replace"))
               #self.history.add(result[0].encode(self.encoding, "replace"))
            except:
               print "Failed to encode '%s'... to %s, iso-8859-1 used" \
                     % (self.htmlCode[:10], self.encoding)
               misc.printError()
               self.htmlWin.SetPage(self.htmlCode.encode("iso-8859-1", "replace"))
               self.history.add(self.htmlCode.encode("iso-8859-1", "replace"))
               #self.SetStatusText(_("Error: failed to encode in %s") % self.encoding)
         
         if not self.wlHidden:
            if not self.__searchedBySelecting:
               self.wordList.Clear()

               print "Appending list..."
               self.wordList.InsertItems(result[1], 0)
               self.list = result[1]

         if not self.__searchedBySelecting:
            matches = self.wordList.GetCount()
            if matches == 1:
               self.SetStatusText(_("1 word matches"))
            elif matches > 1:
               self.SetStatusText(_("%d words match") % matches)

         if self.history.canBack():
            self.buttonBack.Enable(1)
         self.buttonForward.Disable()
         self.entry.SetFocus()


   def onTimerLoad(self, event):
      if self.load != None and self.load.isDone():
         self.timerLoad.Stop()
         self.load.stop()

         self.dict = self.load()
         if self.dict == None:
            self.onCloseDict(None)
            self.load = None
            #self.buttonStop.Disable()
            self.entry.Enable(1)
            self.entry.SetFocus()
            self.SetStatusText(_("Error: failed to load"))
            return

         else:
            self.SetStatusText(_("Dictionary \"%s\" loaded") % self.dictName)

            if not hasattr(self.dict, "name"):
               self.dict.name = "unknown"

            if self.dict.name not in self.app.config.registers.keys() + \
               self.app.config.plugins.keys() + self.app.config.groups.keys():
               try:
                  self.dict.makeHashTable()
               except:
                  # Doesn't use it or is bad-written
                  pass
            elif self.dict.name in self.app.config.registers:
               # This is a register, hash table must be loaded
               if self.app.config.registers[self.dict.name][1] != "Dict":
                  print "Loading hash table..."
                  try:
                     if os.path.exists(os.path.join(uhome, "register", self.dict.name+".hash")):
                        self.dict.hash = self.app.reg.loadHashTable(os.path.join(uhome, "register", self.dict.name+".hash"))
                     else:
                        self.dict.hash = self.app.reg.loadHashTable(os.path.join(home, "register", self.dict.name+".hash"))
                  except:
                     print "Failed to load index table"
                     self.SetStatusText(_("Error: failed to load index table"))
                     misc.printError()

         self.checkIfNeedsList()
         
         self.load = None
         #self.buttonStop.Disable()
         self.entry.Enable(1)
         self.entry.SetFocus()


   #def onEntryUpdate(self, event):
      #word = self.entry.GetValue()
      #print "Word:", word
      #self.onSearch(None)
      #self.entry.SetFocus()
      #self.entry.SetSelection(0, 0)
      #self.entry.SetInsertioEnd()

   def onSearch(self, event):
      if self.dict == None:
         self.SetStatusText(_("There is no opened dictionary"))
         return

      word = self.entry.GetValue()
      #print "Got word value '%s', type '%s'" % (word, type(word))

      if word == "":
         self.SetStatusText(_("Enter a word"))
         return
      
      wxBeginBusyCursor()

      self.__searchedBySelecting = 0
      self.SetStatusText(_("Searching..."))

      self.timerSearch.Stop()
      self.search = None # should be killed here

      #self.buttonStop.Enable(1)
      self.entry.Disable()
      self.timerSearch.Start(self.delay)
      
      self.search = Process(self.dict.search, word)

   def onBack(self, event):
      self.buttonForward.Enable(1)
      self.htmlWin.SetPage(self.history.back())
      if not self.history.canBack():
         self.buttonBack.Disable()

   def onForward(self, event):
      self.buttonBack.Enable(1)
      self.htmlWin.SetPage(self.history.forward())
      if not self.history.canForward():
         self.buttonForward.Disable()

   def onStop(self, event):
      #self.buttonStop.Disable()
      self.entry.Enable(1)
      self.SetStatusText(_("Stopped"))
      self.timerSearch.Stop()
      self.timerLoad.Stop()

      if self.search:
         self.search.stop()
         self.search = None

      if self.load:
         self.load.stop()
         self.laod = None

   def onClean(self, event):
      self.entry.SetValue("")


   def onAddMyWord(self, event):
      word = self.entry.GetValue().strip()
      if word:
         status = self.myWords.addWord(word)
         if status:
            self.SetStatusText(_("Error: ")+status)
            return
               
         self.SetStatusText(_("Word \"%s\" has been added to " \
                            "\"My Words\" list") % word)

         if self.activeMyWordsWindow:
            self.myWordsWindow.updateList()   
      else:
         self.SetStatusText(_("Search entry is empty"))
         

   def onClearHistory(self, event):
      self.entry.Clear()
      self.history.clear()
      self.buttonBack.Disable()
      self.buttonForward.Disable()

   def onHideUnhide(self, event):
      if self.wlHidden == 1:
            self.unhideWordList()
            self.wlHidden = 0
      elif self.wlHidden == 0:
            self.hideWordList()
            self.wlHidden = 1

   def onOpenSlowo(self, event):
      dialog = wxFileDialog(self, _("Choose Slowo dictionary file"), "", "",
                         "", wxOPEN|wxMULTIPLE)
      if dialog.ShowModal() == wxID_OK:
         self.onCloseDict(event)
         self.entry.Disable()
         name = os.path.split(dialog.GetPaths()[0])[1]
         self.SetStatusText(_("Loading \"%s\"...") % name)
         self.SetTitle("%s - OpenDict" % name)
         try:
            self.timerLoad.Start(self.delay)
            self.load = Process(SlowoParser, dialog.GetPaths()[0],
                                self)
            self.dictName = name
            self.encoding = self.app.config.defaultEnc
            self.checkEncMenuItem(self.encoding)
         except:
            self.SetStatusText(_("Error: failed to open \"%s\"") % name)
            self.onCloseDict(None)

      dialog.Destroy()

   def onOpenMova(self, event):
      dialog = wxFileDialog(self, _("Choose Mova dictionary file"), "", "",
                         "", wxOPEN|wxMULTIPLE)
      if dialog.ShowModal() == wxID_OK:
         self.onCloseDict(event)
         self.entry.Disable()
         name = os.path.split(dialog.GetPaths()[0])[1]
         self.SetStatusText(_("Loading \"%s\"...") % name)
         self.SetTitle("%s - OpenDict" % name)
         try:
            self.timerLoad.Start(self.delay)
            self.load = Process(MovaParser, dialog.GetPaths()[0], self)
            self.dictName = name
            self.encoding = self.app.config.defaultEnc
            self.checkEncMenuItem(self.encoding)
         except:
            self.SetStatusText(_("Error: failed to open \"%s\"") % name)
            self.onCloseDict(None)

      dialog.Destroy()

   # TODO: write TMX parser
   def onOpenTMX(self, event):
      dialog = wxFileDialog(self, _("Choose TMX dictionary file"), "", "",
                         "", wxOPEN|wxMULTIPLE)
      if dialog.ShowModal() == wxID_OK:
         self.onCloseDict(event)
         self.entry.Disable()
         #self.buttonStop.Enable(1)
         name = os.path.split(dialog.GetPaths()[0])[1]
         self.SetTitle("%s - OpenDict" % name)
         self.SetStatusText(_("Loading \"%s\"...") % name)

         try:
            #os.chdir(os.path.split(dialog.GetPaths()[0])[0])
            self.timerLoad.Start(self.delay)
            self.load = Process(TMXParser, dialog.GetPaths()[0], self)
            self.dictName = name
            self.encoding = self.app.config.defaultEnc
            self.checkEncMenuItem(self.encoding)
         except:
            self.SetStatusText(_("Error: failed to open \"%s\"") % name)
            self.onCloseDict(None)

      dialog.Destroy()


   def onOpenDictFile(self, event):

      dialog = wxFileDialog(self, _("Choose dictionary file"), "", "",
                         "", wxOPEN|wxMULTIPLE)
      if dialog.ShowModal() == wxID_OK:
         self.onCloseDict(event)
         self.entry.Disable()
         name = os.path.split(dialog.GetPaths()[0])[1]
         # dictlib supports both zipped and not zipped files?
         if name.find(".dz"):
            basename = name.replace(".dict.dz", "")
         else:
            basename = name.replace(".dict", "")
         self.SetTitle("%s - OpenDict" % basename)

         self.SetStatusText(_("Loading \"%s\"...") % name)
         # do we need this try/except? I think it does nothing
         try:
            os.chdir(os.path.split(dialog.GetPaths()[0])[0])
            self.timerLoad.Start(self.delay)
            self.load = Process(DictParser, basename, self)
            self.dictName = name
            self.encoding = self.app.config.defaultEnc
            self.checkEncMenuItem(self.encoding)
         except:
            self.SetStatusText(_("Error: failed to open \"%s\"") % name)
            self.onCloseDict(None)

      dialog.Destroy()

   def onOpenDictConn(self, event):
      window = DictConnWindow(self, -1,
                              _("Connect to DICT server"),
                              style=wxDEFAULT_FRAME_STYLE)
      window.CentreOnScreen()
      window.Show(True)


   def onCloseDict(self, event):

      # If there was a registered dict, set it's default encoding
      try:
         print self.dict.name
         if self.dict.name in self.app.config.registers.keys():
            self.app.config.registers[self.dict.name][2] = self.encoding
      except:
         pass

      # Users requested not to clean text entry
      #self.entry.SetValue("")
      
      self.wordList.Clear()
      self.htmlWin.SetPage("")
      self.SetTitle("OpenDict")
      self.list = []
      self.dict = None
      self.encoding = self.app.config.defaultEnc
      self.checkEncMenuItem(self.encoding)

      self.SetStatusText(_("Choose a dictionary from \"Dictionaries\" menu"))
      #self.buttonStop.Disable()

   
   def onCopy(self, event):
      
      self.do = wxTextDataObject()
      self.do.SetText(self.htmlWin.SelectionToText())
      
      wxTheClipboard.Open()
      wxTheClipboard.SetData(self.do)
      wxTheClipboard.Close()

   
   def onPaste(self, event):
      do = wxTextDataObject()
      wxTheClipboard.Open()
      if wxTheClipboard.GetData(do):
         try:
            self.entry.SetValue(do.GetText())
         except:
            try:
               self.entry.SetValue(do.GetText().encode(self.encoding))
            except:
               self.SetStatusText(_("Failed to copy text from the clipboard"))
      else:
         self.SetStatusText(_("Clipboard contains no text data"))
      wxTheClipboard.Close()

   def onShowGroupsWindow(self, event):
      self.groupsWindow = GroupsWindow(self, -1,
                                          _("Groups"),
                                          size=(330, 150),
                                          style=wxDEFAULT_FRAME_STYLE)
      self.groupsWindow.CentreOnScreen()
      self.groupsWindow.Show(True)

   def onShowPluginManager(self, event):
      self.pmWindow = PluginManagerWindow(self, -1,
                                          _("Dictionaries Manager"),
                                          style=wxDEFAULT_FRAME_STYLE)
      self.pmWindow.CentreOnScreen()
      self.pmWindow.Show(True)

   def onShowFileRegistry(self, event):
      self.regWindow = FileRegistryWindow(self, -1,
                                          _("File Register"),
                                          size=(340, 200),
                                          style=wxDEFAULT_FRAME_STYLE)
      self.regWindow.CentreOnScreen()
      self.regWindow.Show(True)

   def onShowDictEditor(self, event):
      print "Editor"
      editor = DictEditorWindow(self, -1, _("Dictionary Editor"),
                                     size=(-1, -1),
                                     style=wxDEFAULT_FRAME_STYLE)
      editor.CentreOnScreen()
      editor.Show(True)

   def onShowMyWordList(self, event):
      print "My words"
      if self.activeMyWordsWindow:
          return
            
      self.myWordsWindow = MyWordsWindow(self, -1, _("My Words"),
                                         size=(300, 400),
                                         style=wxDEFAULT_FRAME_STYLE)
      self.myWordsWindow.CentreOnScreen()
      self.myWordsWindow.Show(True)
      self.activeMyWordsWindow = True 

      
   def onShowPrefsWindow(self, event):
      self.prefsWindow = PrefsWindow(self, -1, _("Preferences"),
                                     size=(-1, -1),
                                     style=wxDEFAULT_FRAME_STYLE)
      self.prefsWindow.CentreOnScreen()
      self.prefsWindow.Show(True)

   def onDefault(self, event):
      print "MainWindow: menu item selected, id:", event.GetId()

      id = event.GetId()
      if 200 <= id < 500:
         self.onCloseDict(None)
         name = self.app.config.ids.keys()[self.app.config.ids.values().index(id)]
         try:
            try:
               #print "MainWindow: Loading \"%s\"..." % name
               pass
            except Exception, p:
               print p
               print "MainWindow: Loading selected dictionary..."
               
            self.SetStatusText(_("Loading \"%s\"...") % name)
            #self.buttonStop.Enable(1)
            if 200 <= id < 300:
               # plugin
               self.loadPlugin(name)
            elif 300 <= id < 400:
               # register
               self.loadRegister(name)
            elif 400 <= id < 500:
               # group
               self.loadGroup(name)
         except:
            #print "Failed loading", name
            self.onCloseDict(None)
            self.SetStatusText(_("Error loading \"%s\"") % name)
            misc.printError()

      elif 2100 <= id < 2500:
         label = self.menuEncodings.FindItemById(id).GetLabel()
         self.changeEncoding(label)
      elif 2500 <= id < 2600:
         label = self.menuFontFace.FindItemById(id).GetLabel()
         self.changeFontFace(label)
      elif 2600 <= id < 2700:
         label = self.menuFontSize.FindItemById(id).GetLabel()
         self.changeFontSize(label)

   def checkIfNeedsList(self):
      if self.dict.needsList:
         if self.wlHidden == 1:
            self.unhideWordList()
            self.wlHidden = 0
      elif self.wlHidden == 0:
         self.hideWordList()
         self.wlHidden = 1

   def loadPlugin(self, name):
      p = self.app.config.plugins[name]

      # hmm, is this ok?
      if plugin.checkPluginVersion(p):
         self.SetStatusText("")
         #self.buttonStop.Disable() # temporarly uavailable
         return

      self.entry.Disable()
      self.timerLoad.Start(self.delay)
      self.load = Process(p.load, self)
      self.dictName = name
      self.SetTitle("%s - OpenDict" % name)

   def loadRegister(self, name):
      print "Loading '%s'..." % name

      self.SetTitle("%s - OpenDict" % name)
      item = self.app.config.registers[name]
      self.dictName = name
      self.entry.Disable()

      if item[1] == "dwa":
         self.timerLoad.Start(self.delay)
         self.load = Process(SlowoParser, item[0], self)
      elif item[1] == "mova":
         self.timerLoad.Start(self.delay)
         self.load = Process(MovaParser, item[0],
                             self)
      elif item[1] == "tmx":
         self.timerLoad.Start(self.delay)
         self.load = Process(TMXParser, item[0],
                             self)
      elif item[1] == "dz":
         self.timerLoad.Start(self.delay)
         self.load = Process(DictParser, item[0],
                             self)
      else:
         self.SetStatusText(_("Error: not supported dictionary type"))
         return

      self.encoding = item[2]
      self.checkEncMenuItem(self.encoding)

   def loadGroup(self, name):
      print "Loading '%s'..." % name
      self.SetTitle("%s - OpenDict" % name)

      self.entry.Disable()
      self.timerLoad.Start(self.delay)
      dicts = self.app.config.groups[name]
      self.load = Process(DictionaryGroup, dicts, self)
      self.dictName = name

   def changeEncoding(self, name):
      self.encoding = misc.encodings[name]
      self.SetStatusText(_("New encoding will be applied for the next search results"))

   def changeFontFace(self, name):
      self.app.config.fontFace = misc.fontFaces[name]
      self.SetStatusText(_("New font face will be applied for the next search results"))

   def changeFontSize(self, name):
      self.app.config.fontSize = name
      self.SetStatusText(_("New font size will be applied for the next search results"))

   def checkEncMenuItem(self, name):
      ename = ""
      for key in misc.encodings:
         if name == misc.encodings[key]:
            ename = key
            break
      self.menuEncodings.FindItemById(self.menuEncodings.FindItem(ename)).Check(1)

   def onAddDict(self, event):
      installer = Installer(self, self.app.config)
      installer.showGUI()
      
   def onAddFromFile(self, event):
      """Starts dictionary registration process"""

      fileDialog = wxFileDialog(self, _("Choose dictionary file"), "", "",
                            "", wxOPEN|wxMULTIPLE)

      if fileDialog.ShowModal() == wxID_OK:
         file = fileDialog.GetPaths()[0]
      else:
         fileDialog.Destroy()
         return

      flist = ["Slowo", "Mova", "TMX", "Dict"]

      msg = _("Select dictionary format. If you can't find\n" \
              "the format of your dictionary, the register\n" \
              "system does not support it yet.")
      formatDialog = wxSingleChoiceDialog(self,
                                          msg,
                                          _("Dictionary format"),
                                          flist, wxOK|wxCANCEL)
      if formatDialog.ShowModal() == wxID_OK:
         format = formatDialog.GetStringSelection()
      else:
         formatDialog.Destroy()
         return

      fileDialog.Destroy()
      formatDialog.Destroy()

      return self.app.reg.registerDictionary(file, format, self.app.config.defaultEnc)

   def onAddFromPlugin(self, event):
      """Starts plugin installation process"""

      dialog = wxFileDialog(self, _("Choose plugin file"), "", "",
                            "", wxOPEN|wxMULTIPLE)
      if dialog.ShowModal() == wxID_OK:
         plugin.installPlugin(self.app.config, dialog.GetPaths()[0])
      dialog.Destroy()

   def onManual(self, event):
      """Shows 'Manual' window"""

      manualWindow = ManualWindow(self, -1,
                                _("Manual"),
                                size=(500, 400),
                                style=wxDEFAULT_FRAME_STYLE)
      manualWindow.CentreOnScreen()
      manualWindow.Show(True)

   def onLicense(self, event):
      """Shows 'License' window"""

      licenseWindow = LicenseWindow(self, -1,
                                _("License"),
                                size=(500, 400),
                                style=wxDEFAULT_FRAME_STYLE)
      licenseWindow.CenterOnScreen()
      licenseWindow.Show(True)

   def onAbout(self, event):
      """Shows 'About' window"""

      aboutWindow = AboutWindow(self, -1,
                                _("About"),
                                #size=(300, 200),
                                style=wxDEFAULT_DIALOG_STYLE)
      aboutWindow.CentreOnScreen()
      aboutWindow.Show(True)

   def onWordSelected(self, event):
      """Is called when word list item is selected"""

      #print "Word selected: " + event.GetString()
      self.__searchedBySelecting = 1
      self.SetStatusText(_("Searching..."))
      #self.buttonStop.Enable(1)
      self.timerSearch.Start(self.delay)
      word = event.GetString()
      self.entry.SetValue(word) 
      self.search = Process(self.dict.search, event.GetString())

   def createListPanel(self):
      self.panelList = wxPanel(self.splitter, -1)
      #sbList = wxStaticBox(panelList, -1, _("Alternatives"))
      sbSizerList = wxStaticBoxSizer(wxStaticBox(self.panelList, -1, 
                                                 _("Word List")), 
                                     wxVERTICAL)
      self.wordList = wxListBox(self.panelList, 154, wxPoint(-1, -1),
                                wxSize(-1, -1), self.list, wxLB_SINGLE)
      sbSizerList.Add(self.wordList, 1, wxALL | wxEXPAND, 0)
      self.panelList.SetSizer(sbSizerList)
      self.panelList.SetAutoLayout(true)
      sbSizerList.Fit(self.panelList)
      
   def hideWordList(self):
      """Hides word list"""

      self.splitter.SetSashPosition(0)
      self.buttonHide.SetToolTipString(_("Show word list"))
      self.splitter.Unsplit(self.panelList)

   def unhideWordList(self):
      """Shows word list"""

      self.buttonHide.SetToolTipString(_("Hide word list"))
      self.createListPanel()
      self.splitter.SplitVertically(self.panelList, self.panelHtml)
      self.splitter.SetSashPosition(self.app.config.sashPos)

   def onPrint(self, event):

      try:
         self.printer.PrintText(self.htmlCode)
      except:
         try:
            self.printer.PreviewText(self.htmlCode.encode(self.encoding, 
                                                          "replace"))
         except:
            self.SetStatusText(_("Failed to print"))
            misc.printError()

   def onPreview(self, event):

      try:
         self.printer.PreviewText(self.htmlCode)
      except:
         try:
            self.printer.PreviewText(self.htmlCode.encode(self.encoding, 
                                                          "replace"))
         except:
            self.SetStatusText(_("Page preview failed"))
            misc.printError()

    
      
