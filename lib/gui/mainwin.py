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

"""
Main window GUI module
"""

import wx
import wx.html
import os
import cStringIO
import traceback

from lib import info
from lib.gui.dictconnwin import DictConnWindow
from lib.gui.pluginwin import PluginManagerWindow
from lib.gui.dicteditorwin import DictEditorWindow
from lib.gui.dictaddwin import DictAddWindow
from lib.gui.prefswin import PrefsWindow
from lib.gui import prefswin
from lib.gui.helpwin import LicenseWindow, AboutWindow
from lib.gui import errorwin
from lib.gui import miscwin
from lib.parser import SlowoParser
from lib.parser import MovaParser
from lib.parser import TMXParser
from lib.parser import DictParser
from lib.threads import Process
from lib.history import History
from lib.installer import Installer
from lib.extra.html2text import html2text
from lib.logger import systemLog, debugLog, DEBUG, INFO, WARNING, ERROR
from lib import misc
from lib import info
from lib import util
from lib import meta
from lib import enc
from lib import errortype
from lib import dicttype
from lib import plaindict

_ = wx.GetTranslation

# Constants
titleTemplate = "OpenDict - %s"
NORMAL_FONT_SIZE = '10'

# Used to remember word when searching by entering text to the entry,
# selecting one from the list or clicking a link.
lastLookupWord = None


class HtmlWindow(wx.html.HtmlWindow):

   """Html control for showing transaltion and catching
   link-clicking"""

   def OnLinkClicked(self, linkInfo):

      global lastLookupWord
      lastLookupWord = linkInfo.GetHref()
      wx.BeginBusyCursor()
      parent = self.GetParent().GetParent().GetParent()

      word = enc.fromWX(lastLookupWord)
      try:
         word = word.encode(parent.activeDictionary.getEncoding())
      except Exception, e:
         # FIXME: Code duplicates
         traceback.print_exc()
         parent.buttonStop.Disable()
         parent.entry.Enable(True)
         parent.timerSearch.Stop()
         parent.SetStatusText(_('Stopped'))
         wx.EndBusyCursor()
         
         systemLog(ERROR, "Unable to decode '%s': %s" % (word.encode('UTF-8'),
                                                         e))
         title = _("Encode Failed")
         msg = _("Unable to encode text \"%s\" in %s for \"%s\".") \
                 % (enc.toWX(word), parent.activeDictionary.getEncoding(),
                 parent.activeDictionary.getName())
                    
         errorwin.showErrorMessage(title, msg)

         return
      
      parent.SetStatusText(_("Searching..."))
      parent.entry.SetValue(word)
      parent.timerSearch.Start(parent.delay)
      parent.search = Process(parent.activeDictionary.search,
                              word)

      

class MainWindow(wx.Frame):

   """Main OpenDict window with basic controls"""

   def __init__(self, parent, id, title, pos=wx.DefaultPosition,
                size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE):
      wx.Frame.__init__(self, parent, id, title, pos, size, style)

      self.app = wx.GetApp()
      self.printer = wx.html.HtmlEasyPrinting()
      self.history = History()
      self.htmlCode = ""
      self.dictName = ""
      self.activeDictionary = None
      self.words = []
      self.delay = 10 # miliseconds
      
      self.lastInstalledDictName = None

      # This var is used by onTimerSearch to recognize search method.
      # If search was done by selecting a word in a list, then word list
      # is not updated, otherwise is.
      self.__searchedBySelecting = 0

      # Box sizers
      vboxMain = wx.BoxSizer(wx.VERTICAL)
      self.hboxToolbar = wx.BoxSizer(wx.HORIZONTAL)

      #
      # Menu Bar
      #
      self.menuBar = wx.MenuBar()

      #
      # File menu
      #
      menuFile = wx.Menu()

      idPrint = wx.NewId()
      #menuFile.Append(idPrint, _("Print Translation"), "")

      idPreview = wx.NewId()
      #menuFile.Append(idPreview, _("Print Preview"), "")

      idFind = wx.NewId()
      menuFile.Append(idFind, _("Look Up\tCtrl-U"),
                      _("Lookup up word in the dictionary"))
      
      menuFile.AppendSeparator()

      idCloseDict = wx.NewId()
      menuFile.Append(idCloseDict, _("&Close Dictionary\tCtrl-W"),
                      _("Close opened dicitonary"))

      idExit = wx.NewId()
      menuFile.Append(idExit, _("E&xit\tCtrl-Q"),
                      _("Exit program"))

      self.menuBar.Append(menuFile, _("&File"))

      menuEdit = wx.Menu()

      #
      # Clear functions
      #
      idClearEntry = wx.NewId()
      menuEdit.Append(idClearEntry, _("&Clear Search Entry\tCtrl-L"))

      idClearHistory = wx.NewId()
      menuEdit.Append(idClearHistory, _("Clear History"))

      menuEdit.AppendSeparator()

      #
      # Clipboard functions
      #
      idCopy = wx.NewId()
      menuEdit.Append(idCopy, _("Copy\tCtrl-C"),
                      _("Copy selected translation text"))

      idPaste = wx.NewId()
      menuEdit.Append(idPaste, _("Paste\tCtrl-V"),
                      _("Paste clipboard text into the search entry"))
      
      menuEdit.AppendSeparator()

      idPrefs = wx.NewId()
      menuEdit.Append(idPrefs, _("Preferences...\tCtrl-P"), _("Edit preferences"))

      self.menuBar.Append(menuEdit, _("&Edit"))


      #
      # View menu
      #      
      menuView = wx.Menu()

      # Font size
      self.menuFontSize = wx.Menu()
      self.menuFontSize.Append(2007, _("Increase\tCtrl-="),
                               _("Increase text size"))
      self.menuFontSize.Append(2008, _("Decrease\tCtrl--"),
                               _("Decrease text size"))
      self.menuFontSize.AppendSeparator()
      self.menuFontSize.Append(2009, _("Normal\tCtrl-0"),
                               _("Set normal text size"))
      menuView.AppendMenu(2002, _("Font Size"), self.menuFontSize)

      # Font face
      self.menuFontFace = wx.Menu()
      i = 0
      keys = misc.fontFaces.keys()
      keys.sort()
      
      for face in keys:
         self.menuFontFace.AppendRadioItem(2500+i, face, "")
         wx.EVT_MENU(self, 2500+i, self.onDefault)
         if self.app.config.get('fontFace') == misc.fontFaces[face]:
            self.menuFontFace.FindItemById(2500+i).Check(1)
         i+=1
         
      menuView.AppendMenu(2001, _("Font Face"), self.menuFontFace)
      

      # Font encoding
      self.menuEncodings = wx.Menu()
      i = 0
      keys = misc.encodings.keys()
      keys.sort()
      for encoding in keys:
         self.menuEncodings.AppendRadioItem(2100+i , encoding, "")
         wx.EVT_MENU(self, 2100+i, self.onDefault)
         if self.app.config.get('encoding') == misc.encodings[encoding]:
            self.menuEncodings.FindItemById(2100+i).Check(1)
         i+=1
         
      menuView.AppendMenu(2000, _("Character Encoding"), self.menuEncodings)
      
      menuView.AppendSeparator()

      idShowHide = wx.NewId()
      menuView.Append(idShowHide, _("Show/Hide Word List...\tCtrl-H"), 
            _("Show or hide word list"))
      

      self.menuBar.Append(menuView, _("&View"))

      
      #
      # Dictionaries menu
      #
      self.menuDict = wx.Menu()

      dicts = []
      for dictionary in self.app.dictionaries.values():
         dicts.append([dictionary.getName(), dictionary.getActive()])
      dicts.sort()
      
      for name, active in dicts:
         #if not self.app.config.activedict.enabled(name):
         #    continue
         if not active:
             continue

         encoded = enc.toWX(name)

         itemID = self.app.config.ids.keys()[\
            self.app.config.ids.values().index(name)]

         try:
            item = wx.MenuItem(self.menuDict,
                              itemID,
                              encoded)
            self.menuDict.AppendItem(item)
            wx.EVT_MENU(self, itemID, self.onDefault)
         except Exception, e:
            systemLog(ERROR, "Unable to create menu item for '%s' (%s)" \
                  % (name, e))

      self.menuDict.AppendSeparator()

      idAddDict = wx.NewId()
      self.menuDict.Append(idAddDict, _("&Install Dictionary From File..."))
      
      self.menuBar.Append(self.menuDict, _("&Dictionaries"))


      #
      # Tools menu
      #
      menuTools = wx.Menu()

      idManageDict = wx.NewId()
      menuTools.Append(idManageDict, _("Manage Dictionaries...\tCtrl-M"),
                      _("Install or remove dictionaries"))

      menuTools.Append(5002, _("Create Dictionaries..."),
                       _("Create and edit dictionaries"))  
                           
      menuTools.AppendSeparator()

      idUseScan = wx.NewId()
      item = wx.MenuItem(menuTools,
                        idUseScan,
                        _("Take Words From Clipboard"),
                        _("Scan the clipboard for text to translate"),
                        wx.ITEM_CHECK)
      menuTools.AppendItem(item)
      menuTools.Check(idUseScan, self.app.config.get('useClipboard') == 'True')

      menuTools.AppendSeparator()

      idDictServer = wx.NewId()
      menuTools.Append(idDictServer, _("Connect to DICT Server..."),
                          _("Open connection to DICT server"))

      menuTools.AppendSeparator()

      idPron = wx.NewId()
      menuTools.Append(idPron, _("Pronounce\tCtrl-E"),
          _("Pronounce word"))  
                           
      
      self.menuBar.Append(menuTools, _("Tools"))


      #
      # Help menu
      #
      menuHelp = wx.Menu()

      idAbout = wx.NewId()
      menuHelp.Append(idAbout, _("&About\tCtrl-A"))

      self.menuBar.Append(menuHelp, _("&Help"))

      self.SetMenuBar(self.menuBar)

      # Search Bar
      labelWord = wx.StaticText(self, -1, _("Word:"))
      self.hboxToolbar.Add(labelWord, 0, wx.ALL | wx.CENTER | wx.ALIGN_RIGHT, 5)
      
      self.entry = wx.ComboBox(self, 153, "", wx.Point(-1, -1),
                              wx.Size(-1, -1), [], wx.CB_DROPDOWN)
      self.entry.SetToolTipString(_("Enter some text and press " \
                                    "\"Look Up\" button or "
                                    "[ENTER] key on your keyboard"))
      self.hboxToolbar.Add(self.entry, 1, wx.ALL | wx.CENTER, 1)

      #self.buttonSearch = wx.Button(self, wx.ID_FIND)
      self.buttonSearch = wx.Button(self, idFind, _("Look Up"))
      self.buttonSearch.SetToolTipString(_("Click this button to look " \
                                           "up word in " \
                                           "the dictionary"))
      
      self.hboxToolbar.Add(self.buttonSearch, 0, wx.ALL | wx.CENTER, 1)

      # Back button
      bmp = wx.Bitmap(os.path.join(info.GLOBAL_HOME, "pixmaps", "left.png"),
                     wx.BITMAP_TYPE_PNG)
      self.buttonBack = wx.BitmapButton(self, 2010, bmp, (24, 24),
                                         style=wx.NO_BORDER)
      self.buttonBack.SetToolTipString(_("History Back"))
      self.buttonBack.Disable()
      self.hboxToolbar.Add(self.buttonBack, 0, wx.ALL | wx.CENTER, 1)

      # Forward button
      bmp = wx.Bitmap(os.path.join(info.GLOBAL_HOME, "pixmaps", "right.png"),
                     wx.BITMAP_TYPE_PNG)
      self.buttonForward = wx.BitmapButton(self, 2011, bmp, (24, 24),
                                         style=wx.NO_BORDER)
      self.buttonForward.SetToolTipString(_("History Forward"))
      self.buttonForward.Disable()
      self.hboxToolbar.Add(self.buttonForward, 0, wx.ALL | wx.CENTER, 1)

      # Stop threads
      # TODO: how thread can be killed?
      bmp = wx.Bitmap(os.path.join(info.GLOBAL_HOME, "pixmaps", "stop.png"),
                     wx.BITMAP_TYPE_PNG)
      self.buttonStop = wx.BitmapButton(self, 155, bmp, (16, 16),
                                       style=wx.NO_BORDER)
      self.buttonStop.SetToolTipString(_("Stop searching"))
      self.buttonStop.Disable()
      self.hboxToolbar.Add(self.buttonStop, 0, wx.ALL | wx.CENTER, 1)

      # Word list is hidden by default
      self.wlHidden = True
      
      bmp = wx.Bitmap(os.path.join(info.GLOBAL_HOME, "pixmaps", "hide.png"),
                     wx.BITMAP_TYPE_PNG)
      self.buttonHide = wx.BitmapButton(self, 152, bmp, (24, 24),
                                       style=wx.NO_BORDER)
      self.hboxToolbar.Add(self.buttonHide, 0, wx.ALL | wx.CENTER, 1)

      vboxMain.Add(self.hboxToolbar, 0, wx.ALL | wx.EXPAND | wx.GROW, 0)

      # Splitter Window
      self.splitter = wx.SplitterWindow(self, -1)

      # List panel
      self.createListPanel()
      
      # Html window panel
      self.panelHtml = wx.Panel(self.splitter, -1)
      sbSizerHtml = wx.StaticBoxSizer(wx.StaticBox(self.panelHtml, -1, 
                                                 _("Translation")),
                                     wx.VERTICAL)
      self.htmlWin = HtmlWindow(self.panelHtml, -1, style=wx.SUNKEN_BORDER)
      sbSizerHtml.Add(self.htmlWin, 1, wx.ALL | wx.EXPAND, 0)
      self.panelHtml.SetSizer(sbSizerHtml)
      self.panelHtml.SetAutoLayout(True)
      sbSizerHtml.Fit(self.panelHtml)

      self.splitter.SplitVertically(self.panelList, self.panelHtml,
                                    int(self.app.config.get('sashPos')))
         
      self.splitter.SetMinimumPaneSize(90)
      self.splitter.SetSashSize(5)

      if not self.activeDictionary:
         self.hideWordList()

      vboxMain.Add(self.splitter, 1, wx.ALL | wx.GROW | wx.EXPAND, 0)

      # Status bar
      self.CreateStatusBar()

      # Main sizer
      self.SetSizer(vboxMain)

      self.timerSearch = wx.Timer(self, 5000)
      self.timerLoad = wx.Timer(self, 5001)

      idClipboard = wx.NewId()
      self.timerClipboard = wx.Timer(self, idClipboard)
      self.scanTimeout = 2000
      
      self.search = None
      self.load = None

      wx.InitAllImageHandlers()      
      self.SetIcon(wx.Icon(os.path.join(info.GLOBAL_HOME,
                                       "pixmaps",
                                       "icon-32x32.png"),
                          wx.BITMAP_TYPE_PNG))


      #
      # Loading default dictionary
      #
      if self.app.config.get('defaultDict'):
         self.loadDictionary(self.app.dictionaries.get(\
            self.app.config.get('defaultDict')))


      self.SetMinSize((320, 160))


      #
      # Events
      #
      # TODO: New-style event definition

      # File menu events
      wx.EVT_MENU(self, idPrint, self.onPrint)
      wx.EVT_MENU(self, idPreview, self.onPreview)
      wx.EVT_MENU(self, idCloseDict, self.onCloseDict)
      wx.EVT_MENU(self, idExit, self.onExit)

      # Edit menu events
      wx.EVT_MENU(self, idClearHistory, self.onClearHistory)
      wx.EVT_MENU(self, idCopy, self.onCopy)
      wx.EVT_MENU(self, idPaste, self.onPaste)
      wx.EVT_MENU(self, idClearEntry, self.onClean)

      # View menu events
      wx.EVT_MENU(self, 2007, self.onIncreaseFontSize)
      wx.EVT_MENU(self, 2008, self.onDecreaseFontSize)
      wx.EVT_MENU(self, 2009, self.onNormalFontSize)
      wx.EVT_MENU(self, idShowHide, self.onHideUnhide)

      # Dictionaries menu events
      wx.EVT_MENU(self, idAddDict, self.onAddDict)

      # Tools menu events
      wx.EVT_MENU(self, idDictServer, self.onOpenDictConn)
      wx.EVT_MENU(self, idUseScan, self.onUseScanClipboard)
      wx.EVT_MENU(self, idManageDict, self.onShowPluginManager)
      wx.EVT_MENU(self, 5002, self.onShowDictEditor)
      wx.EVT_MENU(self, idPrefs, self.onShowPrefsWindow)
      wx.EVT_MENU(self, idPron, self.onPronounce)

      # Help menu events
      wx.EVT_MENU(self, idAbout, self.onAbout)

      # Other events
      self.Bind(wx.EVT_BUTTON, self.onSearch, self.buttonSearch)
      wx.EVT_MENU(self, idFind, self.onSearch)
         
      wx.EVT_BUTTON(self, 2010, self.onBack)
      wx.EVT_BUTTON(self, 2011, self.onForward)
      wx.EVT_BUTTON(self, 155, self.onStop)
      wx.EVT_BUTTON(self, 151, self.onClean)
      wx.EVT_BUTTON(self, 152, self.onHideUnhide)
      wx.EVT_TEXT_ENTER(self, 153, self.onSearch)
      wx.EVT_LISTBOX(self, 154, self.onWordSelected)
      wx.EVT_TIMER(self, 5000, self.onTimerSearch)
      wx.EVT_TIMER(self, idClipboard, self.onTimerClipboard)
      wx.EVT_CLOSE(self, self.onCloseWindow)

      self.entry.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)

      # Prepare help message
      self.htmlCode = _("""
<html>
<head>
<meta http-equiv=\"Content-Type\" content=\"text/html; charset=UTF-8\">
</head>
<body>
<h3>Welcome to OpenDict</h3>
<p><b>Short usage information:</b></p>
<ul>
  <li>To start using dictionary, select one from <i><b>Dictionaries</b></i>
    menu.
  </li>
  <li>To install new dictionary from the Internet, select
    <i><b>Manage Dictionaries</b></i>
    from <i><b>Tools</b></i> menu and choose <i><b>Available</b></i> tab.</li>
  <li>To install new dictionary from file, select <i><b>Install Dictionary From File...</b></i>
  from <i><b>Dictionaries</b></i> menu.
  </li>
</ul>
</body>
</html>
""")

      if self.activeDictionary:
         self.htmlCode = ""

      self.updateHtmlScreen()


      if self.app.invalidDictionaries:
         miscwin.showInvalidDicts(self, self.app.invalidDictionaries)

      if self.app.config.get('useClipboard') == 'True':
         self.timerClipboard.Start(self.scanTimeout)


   def onExit(self, event):

      self.onCloseWindow(None)


   def onCloseWindow(self, event):

      self.onCloseDict(None)
      self.savePreferences()
      self.Destroy()


   # TODO: Move aftersearch actions into separate method
   def onTimerSearch(self, event):
      """Search timer. When finished, sets search results"""
      
      if self.search != None and self.search.isDone():
         self.timerSearch.Stop()
         self.search.stop()

         #
         # Turn back active interface elements state
         wx.EndBusyCursor()
         self.SetStatusText("")
         self.entry.Enable(1)
         self.buttonStop.Disable()
         
         global lastLookupWord
         word = lastLookupWord

         if self.entry.FindString(word) == -1:
            self.entry.Append(word)
         
         result = self.search()

         # Check if search result is SerachResult object.
         # SearchResult class is used by new-type plugins.
         try:
            assert result.__class__ == meta.SearchResult
         except:
            self.SetStatusText(errortype.INTERNAL_ERROR.getMessage())

            if self.activeDictionary.getType() == dicttype.PLUGIN:
               title = errortype.INTERNAL_ERROR.getMessage()
               message = errortype.INTERNAL_ERROR.getLongMessage()
            else:
               title = errortype.OPENDICT_BUG.getMessage()
               message = errortype.OPENDICT_BUG.getLongMessage()

            systemLog(ERROR, "%s: %s" % (message, misc.getTraceback()))
            errorwin.showErrorMessage(title, message)
            
            return

         # Check status code
         if result.getError() != errortype.OK:
            systemLog(ERROR, result.getError())
            
            self.htmlWin.SetPage("")
            self.wordList.Clear()

            if result.getError() in \
                   [errortype.INTERNAL_ERROR, errortype.INVALID_ENCODING]:
               errorwin.showErrorMessage(result.getError().getMessage(),
                                         result.getError().getLongMessage())
            else:
               self.SetStatusText(result.getError().getMessage())
               
            return

         #
         # If dictionary (plugin) does not use NOT_FOUND notification,
         # check for translation and show it manually
         #
         if not result.getTranslation():
            self.SetStatusText(errortype.NOT_FOUND.getMessage())
            

         try:
            transUnicode = unicode(result.translation,
                                   self.activeDictionary.getEncoding())
         except Exception, e:
            systemLog(ERROR, "Unable to decode translation in %s (%s)" \
                      % (self.activeDictionary.getEncoding(),
                         e))
            title = errortype.INVALID_ENCODING.getMessage()
            msg = _("Translation cannot be displayed using selected " \
                    "encoding %s. Please try another encoding from " \
                    "View > Character Encoding menu.") \
                    % self.activeDictionary.getEncoding()
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
               self.words = wordsPreparedForWX

         if not self.__searchedBySelecting:
            matches = self.wordList.GetCount()
            if matches == 1:
               self.SetStatusText(_("1 word matches"))
            elif matches > 1:
               self.SetStatusText(_("%d words match") % matches)
         else:
            self.SetStatusText(_("Done"))

         if self.history.canBack():
            self.buttonBack.Enable(1)
            
         self.search = None


   def onTimerClipboard(self, event):
      """Clipboard timer, used to watch new text in a clipboard"""

      def getText():
         do = wx.TextDataObject()
         text = None
         wx.TheClipboard.Open()
         if wx.TheClipboard.GetData(do):
            try:
               text = do.GetText().strip()
            except Exception, e:
               print e
         wx.TheClipboard.Close()
         return enc.toWX(text)
      
      text = getText()
      old_text = ''
      if hasattr(self, 'old_clipboard_text'):
          old_text = self.old_clipboard_text
      if text and text != old_text:
         self.entry.SetValue(text)
         self.onSearch(None)
         self.old_clipboard_text = text


   def onUseScanClipboard(self, event):
      """Scan Clipboard menu item selected"""

      if event and event.GetInt():
         self.timerClipboard.Start(self.scanTimeout)
      else:
         self.timerClipboard.Stop()


   def onSearch(self, event):
      if self.activeDictionary == None:
         if len(self.app.dictionaries):
            title = _("No dictionary activated")
            msg = _("No dictionary activated. Please select one from "\
                 "\"Dictionaries\" menu and try again.")
         else:
            title = _("No dictionaries installed")
            msg = _("There is no dictionaries installed. You can " \
                      "install one by selecting Tools > Manage " \
                      "Dictionaries > Available")

         errorwin.showErrorMessage(title, msg)
         return

      if self.search and not self.search.isDone():
          self.onStop(None)

      word = self.entry.GetValue()

      if word == "":
         self.SetStatusText(_("Please enter some text and try again"))
         self.entry.SetFocus()
         return

      global lastLookupWord
      lastLookupWord = word
      wx.BeginBusyCursor()

      self.__searchedBySelecting = 0
      self.SetStatusText(_("Searching..."))

      self.timerSearch.Stop()
      self.search = None

      self.buttonStop.Enable(1)
      self.entry.Disable()
      self.timerSearch.Start(self.delay)

      word = enc.fromWX(word)
      try:
         word = word.encode(self.activeDictionary.getEncoding())
      except Exception, e:
         # FIXME: Code duplicates
         self.buttonStop.Disable()
         self.entry.Enable(True)
         self.timerSearch.Stop()
         self.SetStatusText(_('Stopped'))
         wx.EndBusyCursor()
         
         systemLog(ERROR, "Unable to decode '%s': %s" % (word.encode('UTF-8'),
                                                         e))
         title = _("Encode Failed")
         msg = _("Unable to encode text \"%s\" in %s for \"%s\". "
                 "That logically means the word "
                 "definition does not exist in the dictionary.") \
                 % (enc.toWX(word), self.activeDictionary.getEncoding(),
                 self.activeDictionary.getName())
                    
         errorwin.showErrorMessage(title, msg)

         return
         
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

      self.entry.Enable(1)
      self.SetStatusText(_("Stopped"))
      self.timerSearch.Stop()
      self.timerLoad.Stop()

      if self.search:
         self.search.stop()
         self.search = None

      if self.load:
         self.load.stop()
         self.load = None

      wx.EndBusyCursor()
      self.buttonStop.Disable()
      

   def onClean(self, event):
      self.entry.SetValue("")
      self.entry.SetFocus()
         

   def onKeyDown(self, event):
      """Key down event handler."""
      if event.GetKeyCode() == wx.WXK_ESCAPE:
         self.onClean(None)
      event.Skip()


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
      else:
            self.hideWordList()



   def onOpenDictConn(self, event):
      
      window = DictConnWindow(self, -1,
                              _("Connect to DICT server"),
                              style=wx.DEFAULT_FRAME_STYLE)
      window.CentreOnScreen()
      window.Show(True)


   def onCloseDict(self, event):
      """Clear widgets and set messages"""

      # If there was a registered dict, set it's default encoding
      # FIXME: new way
      try:
         if self.dict.name in self.app.config.registers.keys():
            self.app.config.registers[self.dict.name][2] = self.app.config.encoding
      except:
         pass

      self.wordList.Clear()
      self.htmlWin.SetPage("")
      self.SetTitle("OpenDict")
      self.words = []

      if self.activeDictionary:
         self.activeDictionary.stop()
         self.activeDictionary = None


      self.SetStatusText(_("Choose a dictionary from \"Dictionaries\" menu"))

   
   def onCopy(self, event):
      
      self.do = wx.TextDataObject()
      self.do.SetText(self.htmlWin.SelectionToText())
      
      wx.TheClipboard.Open()
      wx.TheClipboard.SetData(self.do)
      wx.TheClipboard.Close()

   
   def onPaste(self, event):
      """This method is invoked when Paste menu item is selected"""
      do = wx.TextDataObject()
      wx.TheClipboard.Open()
      if wx.TheClipboard.GetData(do):
         try:
            self.entry.SetValue(do.GetText())
         except:
            self.SetStatusText(_("Failed to copy text from the clipboard"))
      else:
         self.SetStatusText(_("Clipboard contains no text data"))
      wx.TheClipboard.Close()


   def onPronounce(self, event):
      """Pronouce word using external software."""

      word = self.entry.GetValue().strip()
      if word:
        cmd = self.app.config.get('pronunciationCommand') or prefswin.PRON_COMMAND

        if self.app.config.get('pronounceTrans') == 'True':
            word = html2text(self.htmlCode)
        
        import locale
        localeCharset = locale.getpreferredencoding()

        try:
            word = word.replace('(', '').replace(')', '').replace('\n', 
                '').replace('\r', '').replace('"', '\\"')
            cmd = (cmd % word).encode(localeCharset)
            Process(os.system, cmd)
        except Exception, e:
            traceback.print_exc()
            title = _("Error")
            msg = _("Unable to decode text using your locale charset %s" \
                % localeCharset)
            errorwin.showErrorMessage(title, msg)
            

   def onShowGroupsWindow(self, event):
      """This method is invoked when Groups menu item is selected"""
      self.groupsWindow = GroupsWindow(self, -1,
                                          _("Groups"),
                                          size=(330, 150),
                                          style=wx.DEFAULT_FRAME_STYLE)
      self.groupsWindow.CentreOnScreen()
      self.groupsWindow.Show(True)


   def onShowPluginManager(self, event):
      """This method is invoked when Dictionaries Manager
      menu item is selected"""
      try:
         self.pmWindow = PluginManagerWindow(self, -1,
                                             _("Manage Dictionaries"),
                                             size=(500, 500),
                                             style=wx.DEFAULT_FRAME_STYLE)
         self.pmWindow.CentreOnScreen()
         self.pmWindow.Show(True)
      except Exception, e:
         traceback.print_exc()
         systemLog(ERROR, "Unable to show prefs window: %s" % e)
         self.SetStatusText("Error occured, please contact developers (%s)" \
                            % e)
         

   def onShowFileRegistry(self, event):
      self.regWindow = FileRegistryWindow(self, -1,
                                          _("File Register"),
                                          size=(340, 200),
                                          style=wx.DEFAULT_FRAME_STYLE)
      self.regWindow.CentreOnScreen()
      self.regWindow.Show(True)


   def onShowDictEditor(self, event):
      editor = DictEditorWindow(self, -1, _("Create Dictionaries"),
                                     size=(400, 500),
                                     style=wx.DEFAULT_FRAME_STYLE)
      editor.CentreOnScreen()
      editor.Show(True)

      
   def onShowPrefsWindow(self, event):
      try:
         self.prefsWindow = PrefsWindow(self, -1, _("Preferences"),
                                        size=(-1, -1),
                                        style=wx.DEFAULT_FRAME_STYLE)
         self.prefsWindow.CentreOnScreen()
         self.prefsWindow.Show(True)
      except Exception, e:
         traceback.print_exc()
         systemLog(ERROR, "Unable to show preferences window: %s" % e)
         title = errortype.OPENDICT_BUG.getMessage()
         msg = errortype.OPENDICT_BUG.getLongMessage()
         errorwin.showErrorMessage(title, msg)
         

   def onDefault(self, event):
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
      
      if self.activeDictionary.getUsesWordList():
         if self.wordListHidden():
            self.unhideWordList()
      else:
         if not self.wordListHidden():
            self.hideWordList()


   def addDictionary(self, dictInstance):
      """Add dictionary to menu and updates ids"""

      app = wx.GetApp()
      app.dictionaries[dictInstance.getName()] = dictInstance
      unid = util.generateUniqueID()

      # Insert new menu item only if no same named dictionary exists
      #if not dictInstance.getName() in app.config.ids.values():
      app.config.ids[unid] = dictInstance.getName()
      item = wx.MenuItem(self.menuDict,
                        unid,
                        dictInstance.getName())
      wx.EVT_MENU(self, unid, self.onDefault)
      
      #self.menuDict.InsertItem(self.menuDict.GetMenuItemCount()-2, item)
      self.menuDict.InsertItem(0, item)


   def removeDictionary(self, name):
       """Remove dictionary from the menu"""

       item = self.menuDict.FindItem(name)
       if item:
           self.menuDict.Delete(item)


   def loadDictionary(self, dictInstance):
      """Prepares main window for using dictionary"""

      if not dictInstance:
         systemLog(ERROR, "loadDictionary: dictInstance is False")
         return

      #
      # Check licence agreement
      #
      licence = dictInstance.getLicence()
      
      if licence \
             and not self.app.agreements.getAccepted(dictInstance.getPath()):
         if not miscwin.showLicenceAgreement(None, licence):
            from lib.gui import errorwin
            title = _("Licence Agreement Rejected")
            msg = _("You cannot use dictionary \"%s\" without accepting "\
                    "licence agreement") % dictInstance.getName()
            errorwin.showErrorMessage(title, msg)
            return
         else:
            self.app.agreements.addAgreement(dictInstance.getPath())

      self.onCloseDict(None)
      self.activeDictionary = dictInstance
        
      if dictInstance.getType() in dicttype.indexableTypes:
         if plaindict.indexShouldBeMade(dictInstance):
            # Notify about indexing
            from lib.gui import errorwin
            title = _("Dictionary Index")
            msg = _("This is the first time you use this dictionary or it " \
                    "has been changed on disk since last indexing. " \
                    "Indexing is used to make search more efficient. " \
                    "The dictionary will be indexed now. It can take a few " \
                    "or more seconds.\n\n" \
                    "Press OK to continue...")
            errorwin.showInfoMessage(title, msg)

            # Make index
            try:
               wx.BeginBusyCursor()
               plaindict.makeIndex(dictInstance, 
                                   self.app.config.get('encoding'))
               wx.EndBusyCursor()
            except Exception, e:
               wx.EndBusyCursor()
               traceback.print_exc()
               title = _("Index Creation Error")
               msg = _("Error occured while indexing file. " \
                       "This may be because of currently selected " \
                       "character encoding %s is not correct for this " \
                       "dictionary. Try selecting " \
                       "another encoding from View > Character Encoding " \
                       "menu") % self.app.config.get('encoding')

               from lib.gui import errorwin
               errorwin.showErrorMessage(title, msg)
               return

         # Load index
         try:
            wx.BeginBusyCursor()
            index = plaindict.loadIndex(dictInstance)
            self.activeDictionary.setIndex(index)
            wx.EndBusyCursor()
         except Exception, e:
            wx.EndBusyCursor()
            traceback.print_exc()
            title = _("Error")
            msg = _("Unable to load dictionary index table. "
                    "Got error: %s") % e
            from lib.gui import errorwin
            errorwin.showErrorMessage(title, msg)
            return

      wx.BeginBusyCursor()
      self.activeDictionary.start()
      self.checkIfNeedsList()
      self.SetTitle(titleTemplate % dictInstance.getName())
      self.SetStatusText(enc.toWX(_("Dictionary \"%s\" loaded") \
                                    % dictInstance.getName()))

      self.entry.SetFocus()

      try:
         self.checkEncMenuItem(self.activeDictionary.getEncoding())
      except Exception, e:
         systemLog(ERROR, "Unable to select encoding menu item: %s" % e)

      wx.EndBusyCursor()
      

   def loadPlugin(self, name):
      """Sets plugin as currently used dictionary"""

      systemLog(INFO, "Loading plugin '%s'..." % name)
      self.entry.Disable()
      self.dictName = name
      self.activeDictionary = self.app.dictionaries.get(name)
      self.checkIfNeedsList()
      self.SetTitle(titleTemplate % name)
      self.entry.Enable(1)
      self.SetStatusText("Done") # TODO: Set something more useful
      self.htmlWin.SetPage("")
      


   # FIXME: deprecated, update!
   def loadRegister(self, name):

      self.SetTitle(titleTemplate % name) # TODO: should be set after loading
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


   def changeEncoding(self, name):
      self.app.config.set('encoding', misc.encodings[name])

      if self.activeDictionary:
         print "Setting encoding %s for dictionary %s" % \
            (self.app.config.get('encoding'), self.activeDictionary.name)
         self.activeDictionary.setEncoding(self.app.config.get('encoding'))
         systemLog(INFO, "Dictionary encoding set to %s" \
               % self.activeDictionary.getEncoding())
         plaindict.savePlainConfiguration(self.activeDictionary)
         

   def changeFontFace(self, name):
      """Save font face changes"""
      
      self.app.config.set('fontFace', misc.fontFaces[name])
      self.updateHtmlScreen()


   def changeFontSize(self, name):
      
      fontSize = int(name) * 10
      systemLog(INFO, "Setting font size %d" % fontSize)
      self.app.config.set('fontSize', fontSize)
      self.updateHtmlScreen()


   def updateHtmlScreen(self):
      """Update HtmlWindow screen"""

      self.htmlWin.SetFonts(self.app.config.get('fontFace'), "Fixed",
                            [int(self.app.config.get('fontSize'))]*5)
      self.htmlWin.SetPage(self.htmlCode)


   def onIncreaseFontSize(self, event):
      """Increase font size"""

      self.app.config.set('fontSize', int(self.app.config.get('fontSize'))+2)
      self.updateHtmlScreen()


   def onDecreaseFontSize(self, event):
      """Decrease font size"""

      self.app.config.set('fontSize', int(self.app.config.get('fontSize'))-2)
      self.updateHtmlScreen()


   def onNormalFontSize(self, event):
      """Set normal font size"""

      self.app.config.set('fontSize', NORMAL_FONT_SIZE)
      self.updateHtmlScreen()


   def checkEncMenuItem(self, name):
      """Select menu item defined by name"""
      
      ename = ""
      for key in misc.encodings:
         if name == misc.encodings[key]:
            ename = key
            break
         
      if len(ename) == 0:
         systemLog(ERROR, "Something wrong with encodings (name == None)")
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

      fileDialog = wx.FileDialog(self, _("Choose dictionary file"), "", "",
                            "", wx.OPEN|wx.MULTIPLE)

      if fileDialog.ShowModal() == wx.ID_OK:
         file = fileDialog.GetPaths()[0]
      else:
         fileDialog.Destroy()
         return

      flist = ["Slowo", "Mova", "TMX", "Dict"]

      msg = _("Select dictionary format. If you can't find\n" \
              "the format of your dictionary, the register\n" \
              "system does not support it yet.")
      formatDialog = wx.SingleChoiceDialog(self,
                                          msg,
                                          _("Dictionary format"),
                                          flist, wx.OK|wx.CANCEL)
      if formatDialog.ShowModal() == wx.ID_OK:
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

      dialog = wx.FileDialog(self, _("Choose plugin file"), "", "",
                            "", wx.OPEN|wx.MULTIPLE)
      if dialog.ShowModal() == wx.ID_OK:
         plugin.installPlugin(self.app.config, dialog.GetPaths()[0])
      dialog.Destroy()

   def onManual(self, event):
      """Shows Manual window"""

      systemLog(WARNING, "Manual function is not impelemented yet")
      

   def onAbout(self, event):
      """Shows 'About' window"""

      aboutWindow = AboutWindow(self, -1,
                                _("About"),
                                style=wx.DEFAULT_DIALOG_STYLE)
      aboutWindow.CentreOnScreen()
      aboutWindow.Show(True)


   def onWordSelected(self, event):
      """Is called when word list item is selected"""

      if self.search and not self.search.isDone():
          return

      self.__searchedBySelecting = 1
      self.SetStatusText(_("Searching..."))
      self.buttonStop.Enable(1)
      self.timerSearch.Start(self.delay)
      word = event.GetString()
      global lastLookupWord
      lastLookupWord = word
      self.entry.SetValue(word)
      word = enc.fromWX(word)
      word = word.encode(self.activeDictionary.getEncoding())
      self.search = Process(self.activeDictionary.search, word)
      wx.BeginBusyCursor()


   def createListPanel(self):
      self.panelList = wx.Panel(self.splitter, -1)
      sbSizerList = wx.StaticBoxSizer(wx.StaticBox(self.panelList, -1, 
                                                 _("Word List")), 
                                     wx.VERTICAL)
      self.wordList = wx.ListBox(self.panelList, 154, wx.Point(-1, -1),
                                wx.Size(-1, -1), self.words, wx.LB_SINGLE)
      sbSizerList.Add(self.wordList, 1, wx.ALL | wx.EXPAND, 0)
      self.panelList.SetSizer(sbSizerList)
      self.panelList.SetAutoLayout(True)
      sbSizerList.Fit(self.panelList)

      
   def hideWordList(self):
      """Hides word list"""

      systemLog(DEBUG, "Hiding word list...")
      self.splitter.SetSashPosition(0)
      self.splitter.Unsplit(self.panelList)
      self.wlHidden = True

      # And change the button pixmap
      bmp = wx.Bitmap(os.path.join(info.GLOBAL_HOME, "pixmaps", "unhide.png"),
                     wx.BITMAP_TYPE_PNG)
      self.buttonHide.SetBitmapLabel(bmp)
      self.buttonHide.SetToolTipString(_("Show word list"))
      self.buttonHide.Show(False)


   def unhideWordList(self):
      """Shows word list"""

      systemLog(DEBUG, "Showing word list...")
      self.createListPanel()
      self.splitter.SplitVertically(self.panelList, self.panelHtml)
      self.splitter.SetSashPosition(int(self.app.config.get('sashPos')))
      self.wlHidden = False

      # And change the pixmap
      bmp = wx.Bitmap(os.path.join(info.GLOBAL_HOME, "pixmaps", "hide.png"),
                     wx.BITMAP_TYPE_PNG)
      self.buttonHide.SetBitmapLabel(bmp)
      self.buttonHide.SetToolTipString(_("Hide word list"))


   def onPrint(self, event):
      """This method is invoked when print menu item is selected"""

      try:
         self.printer.PrintText(self.htmlCode)
      except Exception, e:
         self.SetStatusText(_("Failed to print"))
         systemLog(ERROR, "Unable to print translation (%s)" % e)
         traceback.print_exc()


   def onPreview(self, event):
      """This method is invoked when preview menu item is selected"""

      try:
         self.printer.PreviewText(self.htmlCode)
      except Exception, e:
         systemLog(ERROR, "Unable to preview translation (%s)" % e)
         self.SetStatusText(_("Page preview failed"))
         traceback.print_exc()


   def savePreferences(self):
      """Saves window preferences when exiting"""

      if self.app.config.get('saveWindowSize'):
         self.app.config.set('windowWidth', self.GetSize()[0])
         self.app.config.set('windowHeight', self.GetSize()[1])
      if self.app.config.get('saveWindowPos'):
         self.app.config.set('windowPosX', self.GetPosition()[0])
         self.app.config.set('windowPosY', self.GetPosition()[1])
      if self.app.config.get('saveSashPos'):
         if not self.wordListHidden():
             self.app.config.set('sashPos', self.splitter.GetSashPosition())

      try:
         self.app.config.save()
      except Exception, e:
         systemLog(ERROR, "Unable to save configuration: %s" % e)
         
