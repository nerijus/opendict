#
# OpenDict
# Copyright (c) 2003-2005 Martynas Jocius <mjoc at akl.lt>
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

"""
Main window GUI module
"""

from wxPython.wx import *
from wxPython.html import *
import os
import cStringIO

#from info import info.GLOBAL_HOME, info.LOCAL_HOME, __version__
import info
from gui.dictconnwin import DictConnWindow
#from gui.groupswin import GroupsWindow
from gui.pluginwin import PluginManagerWindow
from gui.registerwin import FileRegistryWindow
from gui.dicteditorwin import DictEditorWindow
#from gui.mywordswin import MyWordsWindow
from gui.dictaddwin import DictAddWindow
from gui.prefswin import PrefsWindow
from gui.helpwin import LicenseWindow, AboutWindow
from gui import errorwin
from parser import SlowoParser
from parser import MovaParser
from parser import TMXParser
from parser import DictParser
#from group import DictionaryGroup
from threads import Process
#from mywords import MyWords
from history import History
from installer import Installer
from extra.html2text import html2text
import plugin
import misc
import info
import util
import meta
import enc
import errortype

_ = wxGetTranslation

class HtmlWindow(wxHtmlWindow):

   """Html control for showing transaltion and catching
   link-clicking"""

   def OnLinkClicked(self, linkinfo):
      #self.base_OnLinkClicked(linkinfo)
      print "DEBUG LinkInfo: searching for '%s'" % linkinfo.GetHref()
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
      #self.encoding = self.app.config.defaultEnc
      self.activeDictionary = None
      self.list = []
      self.delay = 10 # miliseconds
      
      self.lastInstalledDictName = None

      # My words list
      #self.myWords = MyWords()
       
      #try: 
      #    self.myWords.read()
      #except Exception, e:
      #    print "INFO Warning: Unable to read mywords.txt file"


      # GUI instances
      #self.myWordsWindow = None

      # Activation values
      #self.activeMyWordsWindow = False 

      # This var is used by onTimerSearch to recognize search method.
      # If search was done by selecting a word in a list, then word list
      # is not updated, otherwise is.
      self.__searchedBySelecting = 0

      # Box sizers
      vboxMain = wxBoxSizer(wxVERTICAL)
      hboxToolbar = wxBoxSizer(wxHORIZONTAL)

      #
      # Menu Bar
      #
      
      menuBar = wxMenuBar()

      #
      # File menu
      #

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

      menuFile.Append(2004, _("Print Translation"), "")
      menuFile.Append(2006, _("Print Preview"), "")
      menuFile.AppendSeparator()
      menuFile.Append(106, _("&Close\tCtrl-W"),
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
      menuEdit.Append(111, _("Preferences...\tCtrl-P"), _("Edit preferences"))

      menuBar.Append(menuEdit, _("&Edit"))


      #
      # View menu
      #
      
      menuView = wxMenu()

      # Font size
      self.menuFontSize = wxMenu()
      self.menuFontSize.Append(2007, _("Increase\tCtrl-+"),
                               _("Increase text size"))
      self.menuFontSize.Append(2008, _("Decrease\tCtrl--"),
                               _("Decrease text size"))
      self.menuFontSize.AppendSeparator()
      self.menuFontSize.Append(2009, _("Normal\tCtrl-0"),
                               _("Set normal text size"))
      menuView.AppendMenu(2002, _("Font Size"), self.menuFontSize)
      

      # Font face
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
         
      menuView.AppendMenu(2001, _("Font Face"), self.menuFontFace)
      

      # Font encoding
      self.menuEncodings = wxMenu()
      i = 0
      keys = misc.encodings.keys()
      keys.sort()
      for encoding in keys:
         self.menuEncodings.AppendRadioItem(2100+i , encoding, "")
         EVT_MENU(self, 2100+i, self.onDefault)
         if self.app.config.encoding == misc.encodings[encoding]:
            self.menuEncodings.FindItemById(2100+i).Check(1)
         i+=1
         
      menuView.AppendMenu(2000, _("Character Encoding"), self.menuEncodings)

      menuBar.Append(menuView, _("&View"))

      
      #
      # Dictionaries menu
      #

      self.menuDict = wxMenu()

      dictNames = self.app.dictionaries.keys()
      dictNames.sort()
      for name in dictNames:
         #print "Without trans: %s, %s" % (name, type(name))
         encoded = enc.toWX(name)
         #print "With toWX: %s, %s" % (encoded, type(encoded))
         #print self.app.config.ids[name]
         itemID = self.app.config.ids.keys()[\
            self.app.config.ids.values().index(encoded)]

         try:
            item = wxMenuItem(self.menuDict,
                              itemID,
                              encoded)
            self.menuDict.AppendItem(item)
            EVT_MENU(self, itemID, self.onDefault)
         except Exception, e:
            print "ERROR Unable to create menu item for '%s' (%s)" \
                  % (name, e)

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
      
      menuBar.Append(self.menuDict, _("&Dictionaries"))


      #
      # Tools menu
      #

      menuTools = wxMenu()
      menuTools.Append(110, _("Manage Dictionaries...\tCtrl-M"),
                      _("Install, remove dictionaries and get " \
                        "information about them"))

      # FIXME: Remove group classes and files
      #menuTools.Append(122, _("Manage Groups...\tCtrl-G"),
      #                _("Edit groups of dictionaries"))
                      
      menuTools.AppendSeparator()
      menuTools.Append(123, _("Connect to DICT Server..."),
                          _("Open connection to DICT server"))

      menuTools.AppendSeparator()
      
      # Editor can't be used with non-unicode GUI, because unicode
      # string are used with TMX files.

      #if info.__unicode__:
      menuTools.Append(5002, _("Dictionary Editor"),
                       _("Make your own dictionary"))  

      # FIXME: Remove atitinkamas classes
      #menuTools.Append(5003, _("My Words\tCtrl-W"),
      #                    _("Your significant words list"))
                           
      menuBar.Append(menuTools, _("Tools"))


      #
      # Help menu
      #

      menuHelp = wxMenu()
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

      self.buttonSearch = wxButton(self, wx.ID_FIND)
      self.buttonSearch.SetToolTipString(_("Look up word"))
      hboxToolbar.Add(self.buttonSearch, 0, wxALL | wxCENTER, 1)
      
      # Back button
      bmp = wxBitmap(os.path.join(info.GLOBAL_HOME, "pixmaps", "left.png"),
                     wxBITMAP_TYPE_PNG)
      self.buttonBack = wxBitmapButton(self, 2010, bmp, (24, 24),
                                         style=wxNO_BORDER)
      self.buttonBack.SetToolTipString(_("History Back"))
      self.buttonBack.Disable()
      hboxToolbar.Add(self.buttonBack, 0, wxALL | wxCENTER, 1)

      # Forward button
      bmp = wxBitmap(os.path.join(info.GLOBAL_HOME, "pixmaps", "right.png"),
                     wxBITMAP_TYPE_PNG)
      self.buttonForward = wxBitmapButton(self, 2011, bmp, (24, 24),
                                         style=wxNO_BORDER)
      self.buttonForward.SetToolTipString(_("History Forward"))
      self.buttonForward.Disable()
      hboxToolbar.Add(self.buttonForward, 0, wxALL | wxCENTER, 1)

      # Stop threads
      # TODO: how thread can be killed?
      #bmp = wxBitmap(os.path.join(info.GLOBAL_HOME, "pixmaps", "stop.xpm"),
      #               wxBITMAP_TYPE_XPM)
      #self.buttonStop = wxBitmapButton(self, 155, bmp, (16, 16),
      #                                 style=wxNO_BORDER)
      #self.buttonStop.SetToolTipString(_("Stop"))
      #self.buttonStop.Disable()
      #hboxToolbar.Add(self.buttonStop, 0, wxALL | wxCENTER, 1)
      #self.buttonStop.Hide()

      #bmp = wxBitmap(os.path.join(info.GLOBAL_HOME, "pixmaps", "add.xpm"),
      #               wxBITMAP_TYPE_XPM)
      #self.buttonAdd = wxBitmapButton(self, 5004, bmp, (16, 16),
      #                                 style=wxNO_BORDER)
      #self.buttonAdd.SetToolTipString(_("Add current word to \"My Words\""))
      #hboxToolbar.Add(self.buttonAdd, 0, wxALL | wxCENTER, 1)
      
      # List toggle bitmap button
      # If word list isn't hidden for this dict, else...

      # Word list is hidden by default
      self.wlHidden = True
      
      bmp = wxBitmap(os.path.join(info.GLOBAL_HOME, "pixmaps", "hide.png"),
                     wxBITMAP_TYPE_PNG)
      self.buttonHide = wxBitmapButton(self, 152, bmp, (24, 24),
                                       style=wxNO_BORDER)
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

      if not self.activeDictionary:
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
               self.loadPlugin(self.app.config.dict)

            elif self.app.config.registers.has_key(self.app.config.dict):
               self.loadRegister(self.app.config.dict)

            elif self.app.config.groups.has_key(self.app.config.dict):
               self.loadGroup(self.app.config.dict)

         except Exception, e:
            self.SetStatusText(_("Error: failed to load \"%s\"") % self.app.config.dict)
            print "ERROR Exception:", e
            self.onCloseDict(None)

      # FIMXE: MS Windows doesn't want to show XPM pixmaps in the title bar
      wxInitAllImageHandlers()
      if os.name != "posix":
         icon = wxEmptyIcon()
         data = open(os.path.join(info.GLOBAL_HOME, "pixmaps", "icon.png"), "rb").read()
         icon.CopyFromBitmap(wxBitmapFromImage(wxImageFromStream(cStringIO.StringIO(data))))
         self.SetIcon(icon)
      else:
         self.SetIcon(wxIcon(os.path.join(info.GLOBAL_HOME, "pixmaps", "icon.xpm"),
                             wxBITMAP_TYPE_XPM))


      #
      # Events
      #

      # File menu events
      EVT_MENU(self, 101, self.onOpenSlowo)
      EVT_MENU(self, 102, self.onOpenMova)
      EVT_MENU(self, 103, self.onOpenTMX)
      EVT_MENU(self, 104, self.onOpenDictFile)
      EVT_MENU(self, 2004, self.onPrint)
      EVT_MENU(self, 2006, self.onPreview)
      EVT_MENU(self, 106, self.onCloseDict)
      EVT_MENU(self, 107, self.onExit)

      # Edit menu events
      EVT_MENU(self, 121, self.onClearHistory)
      EVT_MENU(self, 108, self.onCopy)
      EVT_MENU(self, 2005, self.onPaste)
      EVT_MENU(self, 109, self.onClean)

      # View menu events
      EVT_MENU(self, 2007, self.onIncreaseFontSize)
      EVT_MENU(self, 2008, self.onDecreaseFontSize)
      EVT_MENU(self, 2009, self.onNormalFontSize)

      # Dictionaries menu events
      EVT_MENU(self, 112, self.onAddDict)

      # Tools menu events
      EVT_MENU(self, 123, self.onOpenDictConn)
      EVT_MENU(self, 122, self.onShowGroupsWindow)
      EVT_MENU(self, 110, self.onShowPluginManager)
      EVT_MENU(self, 120, self.onShowFileRegistry)
      EVT_MENU(self, 5002, self.onShowDictEditor)
      #EVT_MENU(self, 5003, self.onShowMyWordList)
      EVT_MENU(self, 111, self.onShowPrefsWindow)

      # Help menu events
      #EVT_MENU(self, 115, self.onManual)
      EVT_MENU(self, 117, self.onLicense)
      EVT_MENU(self, 116, self.onAbout)

      # Other events
      EVT_BUTTON(self, wx.ID_FIND, self.onSearch)
      EVT_BUTTON(self, 2010, self.onBack)
      EVT_BUTTON(self, 2011, self.onForward)
      EVT_BUTTON(self, 155, self.onStop)
      EVT_BUTTON(self, 151, self.onClean)
      #EVT_BUTTON(self, 5004, self.onAddMyWord)
      EVT_BUTTON(self, 152, self.onHideUnhide)
      EVT_TEXT_ENTER(self, 153, self.onSearch)
      EVT_LISTBOX(self, 154, self.onWordSelected)
      EVT_TIMER(self, 5000, self.onTimerSearch)
      EVT_TIMER(self, 5001, self.onTimerLoad)
      EVT_CLOSE(self, self.onCloseWindow)

      # Prepare help message
      self.htmlCode = _("""
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
<i>http://sourceforge.net/projects/opendict</i>.
</p>
</body>
</html>
""")

      # Set startup help message
      #self.htmlWin.SetPage(self.htmlCode)

      self.updateHtmlScreen()
     

   # Callback functions

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


   # TODO: Move aftersearch actions into separate method
   def onTimerSearch(self, event):
      """Search timer. When finished, sets search results"""
      
      if self.search != None and self.search.isDone():
         wxEndBusyCursor()
         self.timerSearch.Stop()
         self.search.stop()
         word = self.entry.GetValue()
         
         result = self.search()

         print "Search result: %s" % result, result.getError()

         # Check if search result is SerachResult object.
         # SearchResult class is used by new-type plugins.
         try:
            assert result.__class__ == meta.SearchResult
         except:
            self.SetStatusText(_(errortype.INTERNAL_ERROR.getMessage()))
            self.entry.Enable(1)
            self.entry.SetFocus()
            
            title = _("Dictionary Error")
            message = _("The dictionary you currently use has internal " \
                        "errors, so OpenDict cannot work with it.")
            
            errorwin.showErrorMessage(title, message)

            return


         print "Translation type:", type(result.getTranslation())

         self.SetStatusText("")
         self.entry.Enable(1)
         self.search = None

         # Check status code
         if result.getError() != errortype.OK:
            print "ERROR Error:", result.getError()
            if result.getError() == errortype.INTERNAL_ERROR:
               errorwin.showErrorMessage(result.getError().getMessage(),
                                         result.getError().getLongMessage())
            else:
               self.SetStatusText(_(result.getError().getMessage()))
               self.entry.Enable(1)
               self.entry.SetFocus()
               misc.printError()
            return

         try:
            transUnicode = unicode(result.translation,
                                   self.activeDictionary.getEncoding())
         except:
            title = _(errortype.INVALID_ENCODING.getMessage())
            msg = _("Translation cannot be decoded using selected " \
                    "encoding %s. Please try another encoding from " \
                    "View > Character Encoding menu." % self.app.config.encoding)
            self.SetStatusText(title)
            errorwin.showErrorMessage(title, msg)
            return 
            
         transPreparedForWX = enc.toWX(transUnicode)

         self.htmlWin.SetPage(transPreparedForWX)
         self.history.add(transPreparedForWX)

         # FIXME: Nasty names
         # Where it is used? htmlWin.GetPage
         self.htmlCode = transPreparedForWX
         
         if not self.wordListHidden():
            if not self.__searchedBySelecting:
               self.wordList.Clear()

               toUnicode = lambda s: unicode(s,
                                             self.activeDictionary.getEncoding())
               wordsInUnicode = map(toUnicode, result.words)
               wordsPreparedForWX = map(enc.toWX, wordsInUnicode)
               
               self.wordList.InsertItems(wordsPreparedForWX, 0)
               self.list = wordsPreparedForWX

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


   # FIXME: Deprecated
   def onTimerLoad(self, event):
      if self.load != None and self.load.isDone():
         self.timerLoad.Stop()
         self.load.stop()

         self.activeDictionary = self.load()
         if self.activeDictionary == None:
            self.onCloseDict(None)
            self.load = None
            #self.buttonStop.Disable()
            self.entry.Enable(1)
            self.entry.SetFocus()
            self.SetStatusText(_("Error: failed to load"))
            return

         else:
            self.SetStatusText(_("Dictionary \"%s\" loaded") % self.dictName)

            if not hasattr(self.activeDictionary, "name"):
               self.activeDictionary.getName = "unknown"

            if self.activeDictionary.name not in self.app.config.registers.keys() + \
               self.app.config.plugins.keys() + self.app.config.groups.keys():
               try:
                  self.activeDictionary.makeHashTable()
               except:
                  # Doesn't use it or is bad-written
                  pass
            elif self.activeDictionary.name in self.app.config.registers:
               # This is a register, hash table must be loaded
               if self.app.config.registers[self.activeDictionary.getName()][1] \
                      not in ['dz', 'dict']:
                  print "INFO Loading hash table..."
                  try:
                     if os.path.exists(os.path.join(info.LOCAL_HOME,
                                                    "register",
                                                    self.activeDictionary.name+".hash")):
                        self.dict.hash = self.app.reg.loadHashTable(os.path.join(info.LOCAL_HOME, "register", self.dict.name+".hash"))
                     else:
                        self.dict.hash = self.app.reg.loadHashTable(os.path.join(info.GLOBAL_HOME, "register", self.dict.name+".hash"))
                  except:
                     print "ERROR Failed to load index table"
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
      if self.activeDictionary == None:
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

      word = enc.fromWX(word)
      word = word.encode(self.activeDictionary.getEncoding())
      self.search = Process(self.activeDictionary.search, word)


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


##    def onAddMyWord(self, event):
##       word = self.entry.GetValue().strip()
##       if word:
##          status = self.myWords.addWord(word)
##          if status:
##             self.SetStatusText(_("Error: ")+status)
##             return
               
##          self.SetStatusText(_("Word \"%s\" has been added to " \
##                             "\"My Words\" list") % word)

##          if self.activeMyWordsWindow:
##             self.myWordsWindow.updateList()   
##       else:
##          self.SetStatusText(_("Search entry is empty"))
         

   def onClearHistory(self, event):
      self.entry.Clear()
      self.history.clear()
      self.buttonBack.Disable()
      self.buttonForward.Disable()


   def wordListHidden(self):
      """Returns True if word list marked to be hidden, False
      otherwise"""

      if self.wlHidden:
         return True

      return False
   

   def onHideUnhide(self, event):
      if self.wordListHidden():
            self.unhideWordList()
            #self.wlHidden = 0
      else:
            self.hideWordList()
            #self.wlHidden = 1


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
            #self.encoding = self.app.config.defaultEnc
            self.checkEncMenuItem(self.app.config.encoding)
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
            #self.encoding = self.app.config.defaultEnc
            self.checkEncMenuItem(self.app.config.encoding)
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
            #self.encoding = self.app.config.defaultEnc
            self.checkEncMenuItem(self.app.config.encoding)
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
            #self.encoding = self.app.config.defaultEnc
            self.checkEncMenuItem(self.app.config.encoding)
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
         if self.dict.name in self.app.config.registers.keys():
            self.app.config.registers[self.dict.name][2] = self.app.config.encoding
      except:
         pass

      # Users requested not to clean text entry
      #self.entry.SetValue("")
      
      self.wordList.Clear()
      self.htmlWin.SetPage("")
      self.SetTitle("OpenDict")
      self.list = []
      self.dict = None
      #self.encoding = self.app.config.defaultEnc
      self.checkEncMenuItem(self.app.config.encoding)

      self.SetStatusText(_("Choose a dictionary from \"Dictionaries\" menu"))
      #self.buttonStop.Disable()

   
   def onCopy(self, event):
      
      self.do = wxTextDataObject()
      self.do.SetText(self.htmlWin.SelectionToText())
      
      wxTheClipboard.Open()
      wxTheClipboard.SetData(self.do)
      wxTheClipboard.Close()

   
   def onPaste(self, event):
      """This method is invoked when Paste menu item is selected"""
      do = wxTextDataObject()
      wxTheClipboard.Open()
      if wxTheClipboard.GetData(do):
         try:
            self.entry.SetValue(do.GetText())
         except:
            self.SetStatusText(_("Failed to copy text from the clipboard"))
      else:
         self.SetStatusText(_("Clipboard contains no text data"))
      wxTheClipboard.Close()


   def onShowGroupsWindow(self, event):
      """This method is invoked when Groups menu item is selected"""
      self.groupsWindow = GroupsWindow(self, -1,
                                          _("Groups"),
                                          size=(330, 150),
                                          style=wxDEFAULT_FRAME_STYLE)
      self.groupsWindow.CentreOnScreen()
      self.groupsWindow.Show(True)


   def onShowPluginManager(self, event):
      """This method is invoked when Dictionaries Manager
      menu item is selected"""
      try:
         self.pmWindow = PluginManagerWindow(self, -1,
                                             _("Dictionaries Manager"),
                                             style=wxDEFAULT_FRAME_STYLE)
         self.pmWindow.CentreOnScreen()
         self.pmWindow.Show(True)
      except Exception, e:
         print "ERROR Unable to show prefs window: %s" % e
         self.SetStatusText("Error occured, please contact developers (%s)" \
                            % e)
         

   def onShowFileRegistry(self, event):
      self.regWindow = FileRegistryWindow(self, -1,
                                          _("File Register"),
                                          size=(340, 200),
                                          style=wxDEFAULT_FRAME_STYLE)
      self.regWindow.CentreOnScreen()
      self.regWindow.Show(True)


   def onShowDictEditor(self, event):
      editor = DictEditorWindow(self, -1, _("Dictionary Editor"),
                                     size=(-1, -1),
                                     style=wxDEFAULT_FRAME_STYLE)
      editor.CentreOnScreen()
      editor.Show(True)


   # FIXME: Remove
   
##    def onShowMyWordList(self, event):
##       print "My words"
##       if self.activeMyWordsWindow:
##           return
            
##       self.myWordsWindow = MyWordsWindow(self, -1, _("My Words"),
##                                          size=(300, 400),
##                                          style=wxDEFAULT_FRAME_STYLE)
##       self.myWordsWindow.CentreOnScreen()
##       self.myWordsWindow.Show(True)
##       self.activeMyWordsWindow = True 

      
   def onShowPrefsWindow(self, event):
      try:
         self.prefsWindow = PrefsWindow(self, -1, _("Preferences"),
                                        size=(-1, -1),
                                        style=wxDEFAULT_FRAME_STYLE)
         self.prefsWindow.CentreOnScreen()
         self.prefsWindow.Show(True)
      except Exception, e:
         print "ERROR Unable to show prefs window: %s" % e
         self.SetStatusText("Error occured, please contact developers (%s)" \
                            % e)
         

   def onDefault(self, event):
      print "DEBUG MainWindow: menu item selected, id:", event.GetId()
      # FIXME: Bad way. Try setting a few constants for each type
      # of dictionary and then check this type instead of IDs.


      eventID = event.GetId()
      if eventID in self.app.config.ids.keys():
         dictionary = self.app.dictionaries.get(self.app.config.ids.get(eventID))
         self.loadDictionary(dictionary)

      elif 2100 <= eventID < 2500:
         label = self.menuEncodings.FindItemById(eventID).GetLabel()
         self.changeEncoding(label)
      elif 2500 <= eventID < 2600:
         label = self.menuFontFace.FindItemById(eventID).GetLabel()
         self.changeFontFace(label)
      elif 2600 <= eventID < 2700:
         label = self.menuFontSize.FindItemById(eventID).GetLabel()
         self.changeFontSize(label)


   def checkIfNeedsList(self):
      """Unhides word list if current dictionary uses it"""
      
      if self.activeDictionary.getUsesWordList:
         if self.wordListHidden():
            self.unhideWordList()
      else:
         if not self.wordListHidden():
            self.hideWordList()


   def addDictionary(self, dictInstance):
      """Add dictionary to menu and updates ids"""

      app = wxGetApp()
      app.dictionaries[dictInstance.getName()] = dictInstance
      unid = util.generateUniqueID()
      app.config.ids[unid] = dictInstance.getName()
      
      item = wxMenuItem(self.menuDict,
                        unid,
                        dictInstance.getName())
      EVT_MENU(self, unid, self.onDefault)

      self.menuDict.InsertItem(self.menuDict.GetMenuItemCount()-2, item)


   def loadDictionary(self, dictInstance):
      """Prepares main window for using dictionary"""

      self.onCloseDict(None)
      self.activeDictionary = dictInstance
      self.activeDictionary.start()
      #self.wordList.Clear()
      self.checkIfNeedsList()
      self.SetTitle("%s - OpenDict" % dictInstance.getName())
      self.SetStatusText(_(enc.toWX("Dictionary \"%s\" loaded" \
                                    % dictInstance.getName())))
      #self.htmlWin.SetPage("")
      

   def loadPlugin(self, name):
      """Sets plugin as currently used dictionary"""

      print "Loading plugin '%s'..." % name
      self.entry.Disable()
      self.dictName = name
      self.activeDictionary = self.app.dictionaries.get(name)
      self.checkIfNeedsList()
      print "Dictionary instance: %s" % self.activeDictionary
      self.SetTitle("%s - OpenDict" % name)
      self.entry.Enable(1)
      self.SetStatusText("Done") # TODO: Set something more useful
      self.htmlWin.SetPage("")
      


   # FIXME: deprecated, update!
   def loadRegister(self, name):
      #print "INFO Loading '%s'..." % name

      self.SetTitle("%s - OpenDict" % name) # TODO: should be set after loading
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

      self.app.config.encoding = item[2]
      self.checkEncMenuItem(self.app.config.encoding)


   # FIXME: Deprecated
   def loadGroup(self, name):
      print "INFO Loading '%s'..." % name
      self.SetTitle("%s - OpenDict" % name)

      self.entry.Disable()
      self.timerLoad.Start(self.delay)
      dicts = self.app.config.groups[name]
      self.load = Process(DictionaryGroup, dicts, self)
      self.dictName = name


   def changeEncoding(self, name):
      self.app.config.encoding = misc.encodings[name]

      if self.activeDictionary:
         self.activeDictionary.setEncoding(self.app.config.encoding)
         print "Dictionary encoding set to %s" \
               % self.activeDictionary.getEncoding()
         
      self.SetStatusText(_("New encoding will be applied for the next search results"))


   def changeFontFace(self, name):
      """Save font face changes"""
      
      self.app.config.fontFace = misc.fontFaces[name]
      self.updateHtmlScreen()


   def changeFontSize(self, name):
      
      fontSize = int(name) * 10
      print "INFO Setting font size %d" % fontSize
      self.app.config.fontSize = fontSize
      self.updateHtmlScreen()


   def updateHtmlScreen(self):
      """Update HtmlWindow screen"""

      self.htmlWin.SetFonts(self.app.config.fontFace, "Fixed",
                            [self.app.config.fontSize]*5)
      self.htmlWin.SetPage(self.htmlCode)


   def onIncreaseFontSize(self, event):
      """Increase font size"""

      print "Increase"
      self.app.config.fontSize += 2
      self.updateHtmlScreen()


   def onDecreaseFontSize(self, event):
      """Decrease font size"""

      print "Decrease"
      self.app.config.fontSize -= 2
      self.updateHtmlScreen()


   def onNormalFontSize(self, event):
      """Set normal font size"""

      print "Normal"
      self.app.config.fontSize = 12
      self.updateHtmlScreen()


   def checkEncMenuItem(self, name):
      
      ename = ""
      for key in misc.encodings:
         if name == misc.encodings[key]:
            ename = key
            break
         
      print "Encoding name to save: '%s'" % ename
      if len(ename) == 0:
         print "ERROR Something wrong with encodings!"
         return
      
      self.menuEncodings.FindItemById(self.menuEncodings.FindItem(ename)).Check(1)


   def getCurrentEncoding(self):
      """Return currently set encoding"""

      # Is this the best way for keeping it?
      return self.app.config.encoding
   

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

      return self.app.reg.registerDictionary(file, format,
                                             self.app.config.defaultEnc)

   def onAddFromPlugin(self, event):
      """Starts plugin installation process"""

      dialog = wxFileDialog(self, _("Choose plugin file"), "", "",
                            "", wxOPEN|wxMULTIPLE)
      if dialog.ShowModal() == wxID_OK:
         plugin.installPlugin(self.app.config, dialog.GetPaths()[0])
      dialog.Destroy()

   def onManual(self, event):
      """Shows Manual window"""

      print "INFO Manual function is not impelemented yet"
      

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
      word = enc.fromWX(word)
      word = word.encode(self.activeDictionary.getEncoding())
      self.search = Process(self.activeDictionary.search, word)


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

      print "DEBUG Hiding word list..."
      self.splitter.SetSashPosition(0)
      self.splitter.Unsplit(self.panelList)
      self.wlHidden = True

      # And change the button pixmap
      print "DEBUG Setting unhide.png icon..."
      bmp = wxBitmap(os.path.join(info.GLOBAL_HOME, "pixmaps", "unhide.png"),
                     wxBITMAP_TYPE_PNG)
      self.buttonHide.SetBitmapLabel(bmp)
      self.buttonHide.SetToolTipString(_("Show word list"))


   def unhideWordList(self):
      """Shows word list"""

      print "DEBUG Showing word list..."
      self.createListPanel()
      self.splitter.SplitVertically(self.panelList, self.panelHtml)
      self.splitter.SetSashPosition(self.app.config.sashPos)
      self.wlHidden = False

      # And change the pixmap
      print "DEBUG Setting hide.png icon..."
      bmp = wxBitmap(os.path.join(info.GLOBAL_HOME, "pixmaps", "hide.png"),
                     wxBITMAP_TYPE_PNG)
      self.buttonHide.SetBitmapLabel(bmp)
      self.buttonHide.SetToolTipString(_("Hide word list"))


   def onPrint(self, event):
      """This method is invoked when print menu item is selected"""

      try:
         self.printer.PrintText(self.htmlCode)
      except:
         self.SetStatusText(_("Failed to print"))
         misc.printError()


   def onPreview(self, event):
      """This method is invoked when preview menu item is selected"""

      try:
         self.printer.PreviewText(self.htmlCode)
      except:
         self.SetStatusText(_("Page preview failed"))
         misc.printError()
