/*
 * OpenDict
 * Copyright (c) 2001-2002 Martynas Jocius <mjoc@delfi.lt>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your opinion) any later version.
 *
 * Yhis program is distributed in the hope that will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MECHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more detals.
 *
 * You shoud have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
 */

#include <iostream>

#include "MainWindow.h"
#include "DictText.h"
#include "DictLetterList.h"
#include "DictWordList.h"
#include "Fonts.h"
#include "About.h"
#include "DictParser.h"
#include "SlowoParser.h"
#include "MovaParser.h"

#include "wx/bmpbuttn.h"
#include "images/clear.xpm"

// Plugins
#include "plugins/WebAlkonasPlugin/WebAlkonasPlugin.h"

MainWindow::MainWindow(const wxString& title,
                       const wxPoint& pos,
                       const wxSize& size)
   : wxFrame((wxFrame*)NULL, -1, title, pos, size)
{
   cout<<"Making the main window...";

#if wxUSE_STATUSBAR
   CreateStatusBar(2);
#endif

   wxString choices[] = { };
   wxString ltrs[] = { };

   wxMenu* fileMenu = new wxMenu("", wxMENU_TEAROFF);
   wxMenu* dictMenu = new wxMenu("", wxMENU_TEAROFF);
   wxMenu* piMenu = new wxMenu("", wxMENU_TEAROFF);
   wxMenu* utMenu = new wxMenu("", wxMENU_TEAROFF);
   wxMenu* setMenu = new wxMenu("", wxMENU_TEAROFF);
   wxMenu* helpMenu = new wxMenu("", wxMENU_TEAROFF);
   
   fileMenu->Append(OPEN_SLOWO_DICT, 
		    "Open &Slowo dictionary\tCtrl-S", "Open Slowo dicitonary");
   fileMenu->Append(OPEN_MOVA_DICT, 
		    "Open &Mova dictionary\tCtrl-M", "Open Mova dicitonary");
   fileMenu->Append(OPEN_PO_FILE, 
		    "Open &Po translation file\tCtrl-P", "Open Po translation file");
   fileMenu->AppendSeparator();
   fileMenu->Append(CLOSE_OPENED, 
		    "Close opened dictionary", "Close opened dictionary");
   fileMenu->AppendSeparator();
   fileMenu->Append(QUIT, "E&xit\tCtrl-X", "Exit program");

   dictMenu->AppendSeparator();
   dictMenu->Append(ADD_DICT, 
		    "Add new dictionary...\tCtrl-D", "Add new dictionary");

   utMenu->AppendSeparator();
   utMenu->Append(0, "Add new utility...\tCtrl-U", "Add new utility program");
   
   piMenu->Append(OPEN_WEB_ALKONAS_DICT,
		 "Web Alkonas", "Alkonas internete");
   piMenu->AppendSeparator();
   piMenu->Append(0, "Add new plugin\tCtrl-L", "Add new plugin");
   piMenu->Append(0, "Edit plugins", "Edit plugins");

   setMenu->Append(PREFS, "Preferences...\tCtrl-P", "Preferences");

   wxMenu* encodings = new wxMenu("", wxMENU_TEAROFF);
   wxString tmp;
   for (int i=0, id=100; i<ENC; i++, id++) {
     tmp = font_encodings[i][1] + " (" + font_encodings[i][0] + ")";
     encodings->Append(id, tmp, font_encodings[i][1]);
   }
   setMenu->Append(0, "Change font encoding", encodings, 
		   "Change font encoding");

   /*
   wxMenu* families = new wxMenu("", wxMENU_TEAROFF);
   for (int i=0, id=150; i<FAM; i++, id++)
     families->Append(id, font_families[i], font_families[i]);
   setMenu->Append(0, "Change font family", families, "Change font family");
   */

   helpMenu->Append(ABOUT, "About...\tCtrl-A", "About");
   
   wxMenuBar* menu_bar = new wxMenuBar();

   menu_bar->Append(fileMenu, "&File");
   menu_bar->Append(dictMenu, "&Dictionaries");
   menu_bar->Append(piMenu, "&Plugins");
   menu_bar->Append(utMenu, "&Utilities");
   menu_bar->Append(setMenu, "&Settings");
   menu_bar->Append(helpMenu, "&Help");

   /*
    * Basic widgets
    */

   wxString findw[] = {};

   find_entry = new wxTextCtrl(this,
			       FIND_ENTER, "",
			       wxDefaultPosition, 
			       wxSize(330, -1),
			       wxSUNKEN_BORDER | wxTE_PROCESS_ENTER);

   letter_list = new DictLetterList(this, LETTER_SELECTED, "", 
				    wxDefaultPosition,
				    wxDefaultSize,
				    0, ltrs,
				    wxSUNKEN_BORDER | wxCB_READONLY);

   word_list = new DictWordList(this, 
			        wxEVT_COMMAND_LISTBOX_SELECTED, 
				wxPoint(0, 0),
                                wxSize(140, 200),
				0, 
                                choices, 
				wxLB_ALWAYS_SB);

   word_trans = new wxHtmlWindow(this);
   html_parser = new wxHtmlWinParser(word_trans);

   //htmlParser->SetOutputEncoding(wxFontEncoding(wxFONTENCODING_ISO8859_13));
   
   word_trans->SetBorders(5);
   word_trans->SetPage("");

   html_parser->SetInputEncoding(html_parser->GetOutputEncoding());
   html_parser->SetFontFace("courier");
   html_parser->SetFontSize(1);

   // Bitmap for clear button
   wxBitmap clear_bmp(clear_xpm);
  
   /*
    * Sizers
    */

   // Main vbox
   wxBoxSizer* vbox = new wxBoxSizer(wxVERTICAL);

   // search entry and button
   wxBoxSizer* hbox_find = new wxBoxSizer(wxHORIZONTAL); 

   hbox_find->Add(new wxBitmapButton(this, CLEAR, clear_bmp), 0, wxALL, 2);
   hbox_find->Add(find_entry, 1, wxALL | wxEXPAND, 1);
   hbox_find->Add(new wxButton(this, FIND, "Find"), 0, wxALL, 3);

   // hbox for another stuff
   wxBoxSizer* hbox_word = new wxBoxSizer(wxHORIZONTAL);

   // vbox for wordlist and combobox
   wxBoxSizer* vbox_list = new wxBoxSizer(wxVERTICAL);

   vbox_list->Add(word_list, 1, wxEXPAND);
   vbox_list->Add(letter_list, 0, wxEXPAND);

   hbox_word->Add(vbox_list, 0, wxEXPAND);
   hbox_word->Add(word_trans, 1, wxEXPAND);

   vbox->Add(hbox_find, 0, wxEXPAND | wxGROW);
   vbox->Add(hbox_word, 1, wxEXPAND | wxGROW);

   SetMenuBar(menu_bar);

   SetAutoLayout(TRUE);
   SetSizer(vbox);

   vbox->Fit(this);
   vbox->SetSizeHints(this);

   cout<<" done\n"; // Making main window
}

/*
 * Destructor
 */
MainWindow::~MainWindow()
{

  /* Do we need all this? */
  if (dict) {
    delete dict;
    dict = NULL;
  }

  delete find_entry;
  delete letter_list;
  delete word_list;
  delete word_trans;
  delete html_parser;

  find_entry = NULL;
  letter_list = NULL;
  word_list = NULL;
  word_trans = NULL;
  html_parser = NULL;
  about = NULL;
  dict = NULL;
}

/*
 * Exit methon
 */
void MainWindow::on_quit(wxCommandEvent& WXUNUSED(event))
{
  Close(TRUE);

  cout<<"Window closed\n";
}

/*
 * About window event
 */
void MainWindow::on_about(wxCommandEvent& WXUNUSED(event))
{
  about = new About(this);
  about->Show(TRUE);
}

/*
 * Clears the find entry
 */
void MainWindow::on_clear(wxCommandEvent& WXUNUSED(event))
{
  find_entry->SetValue("");
}

/*
 * Search and update widgets
 */
void MainWindow::on_find(wxCommandEvent& WXUNUSED(event))
{
  if (dict == NULL)
    {
      SetStatusText("There is no opened dictionary");
      return;
    } 

  wxString word = find_entry->GetValue();
  this->last_word = word;

  if (word.Length() == 0)
    {
      SetStatusText("Type a word to search for");
      return;
    }

  wxBeginBusyCursor(); 

  update_all_after_search(word);

  wxEndBusyCursor();
}

/*
 * Called after changing encoding in setting menu
 */
void MainWindow::on_change(wxCommandEvent& event)
{
  if (event.GetEventType() != wxEVT_COMMAND_MENU_SELECTED)
    return;

  int id = event.GetId();

  if (id >= 100 && id <= 100 + ENC)
    {
      cout<<"Change font encoding to ";
      cout<<font_encodings[id-100][0].c_str()<<endl;

      wxString enc = font_encodings[id-100][0];
      this->default_encoding = enc;

      if (this->dict) {
	this->dict->set_default_encoding(enc);
	update_all_after_search(this->last_word);
      }
   
      SetStatusText("Encoding changed to "+enc);
    }

  /*
  else if (id >= 150 && id <= 150 + FAM)
    {
      cout<<"Change font family to ";
      cout<<font_families[id-150].c_str()<<endl;

      wxString family = font_families[id-150];
      this->default_family = family;

      if (this->dict) {
      this->dict->set_default_family = family;
  */

}

/*
 * Updates word_list, letter_list and word_trans widgets
 * for the given keyword.
 */
void MainWindow::update_all_after_search(const wxString& word)
{
  word_trans->SetPage(dict->find(word));

  if (toupper(word[0]) != toupper(word_list->GetString(0)[0]))
    update_words_list(word_list, dict, word[0]);

  word_list->SetSelection(word_list->FindString(word));

  update_letter_count_list(letter_list, dict, word[0]);
}

/*
 * Called when user selects a word in word_list
 */
void MainWindow::on_word_selected(wxCommandEvent& WXUNUSED(event))
{
  wxBeginBusyCursor();
  update_all_after_search(word_list->GetString(word_list->GetSelection()));
  wxEndBusyCursor();
}

/*
 * Called when user selects an item of letter list
 */
void MainWindow::on_letter_selected(wxCommandEvent& WXUNUSED(event))
{
  wxBeginBusyCursor();
  char c = this->letter_list->GetString(this->letter_list->GetSelection())[0];
  c = toupper(c);

  update_words_list(this->word_list, this->dict, c);
  word_trans->SetPage(dict->find(word_list->GetString(0)));
  wxEndBusyCursor();
}

/*
 * Open Slowo dictionary file
 * Called when user opens Slowo dictionary from menu
 * File->Open Slowo dictionary
 */
void MainWindow::open_slowo_dict(wxCommandEvent& WXUNUSED(event))
{
  wxFileDialog* dialog = new wxFileDialog(this, 
					  "Choose Slowo dictionary file",
					  ".", "", "Slowo (*.dwa)|*.dwa|All files (*.*)|*.*");
  dialog->Show(TRUE);

  wxString file;

  if (dialog->ShowModal() == wxID_OK)
    {
      file = dialog->GetPath();
      SetStatusText(dialog->GetFilename(), 1);
    }
  else
    return;

  wxStatusBar* status_bar = GetStatusBar();

  wxBeginBusyCursor();

  cout<<"Parsing new slowo dictionary...\n";
 
  dict = new SlowoParser(file, default_encoding, status_bar);

  wxString first_word = dict->get_words_list()->Item(0);

  wxString page = dict->find(first_word);
  this->last_word = first_word;

  word_trans->SetPage(page);
  update_words_list(word_list, dict, first_word[0]);
  set_letter_count_list(letter_list, dict);

  wxEndBusyCursor();
}

/*
 * Opens Mova dicitonary file
 */
void MainWindow::open_mova_dict(wxCommandEvent& WXUNUSED(event))
{wxFileDialog* dialog = new wxFileDialog(this, 
					  "Choose Mova dictionary file");
  dialog->Show(TRUE);

  wxString file;

  if (dialog->ShowModal() == wxID_OK)
    {
      file = dialog->GetPath();
      SetStatusText(dialog->GetFilename(), 1);
    }
  else
    return;

  wxStatusBar* status_bar = GetStatusBar();

  wxBeginBusyCursor();

  cout<<"Parsing new mova dictionary...\n";
 
  dict = new MovaParser(file, default_encoding, status_bar);

  wxString first_word = dict->get_words_list()->Item(0);

  wxString page = dict->find(first_word);
  this->last_word = first_word;

  word_trans->SetPage(page);
  update_words_list(word_list, dict, first_word[0]);
  set_letter_count_list(letter_list, dict);

  wxEndBusyCursor();
}

/*
 * Opens Po translation file
 */
void MainWindow::open_po_file(wxCommandEvent& WXUNUSED(event))
{
  SetStatusText("No Po support yet");
}

void MainWindow::activate_plugin(wxCommandEvent& WXUNUSED(event))
{
  SetStatusText("Online Alkonas dictionary", 1);
  this->dict = new WebAlkonasPlugin(GetStatusBar());
}

/*
 * Register new dictionary file
 * Index words and add to the list
 */
void MainWindow::add_dict(wxCommandEvent& WXUNUSED(event))
{
  SetStatusText("No register system yet");
}

/*
 * Preferences window
 */
void MainWindow::show_preferences(wxCommandEvent& WXUNUSED(event))
{
  SetStatusText("No preferences window yet");
}

/*
 * Updates words list widget
 */
void MainWindow::update_words_list(wxListBox* list, 
				   DictParser* dict, 
				   char letter)
{
  cout<<"Updating words list for letter `"<<letter<<"'\n";
  wxString item;

  list->Clear();

  for (unsigned int i=0; i<dict->get_words_list()->Count(); i++)
    {
      item = dict->get_words_list()->Item(i);
      if (toupper(item[0]) == toupper(letter))
      {
	list->Append(item);
      }
    }
}

/*
 * Updates letter count list
 */
void MainWindow::set_letter_count_list(wxComboBox* list,
					  DictParser* dict)
{
  wxString item;

  list->Clear();

  for (unsigned int i=0; i<dict->get_letter_count()->Count(); i++)
    {
      list->Append(dict->get_letter_count()->Item(i));
    }
}

/*
 * Updates letter list for the given letter
 */
void MainWindow::update_letter_count_list(wxComboBox* list, 
					  DictParser* dict, 
					  const char& c)
{
  for (unsigned int i=0; i<dict->get_letter_count()->Count(); i++)
    {
      if (dict->get_letter_count()->Item(i)[0] == toupper(c))
	{
	  list->SetSelection(i);
	  return;
	}
    }
}

/*
 * Called when user closed opened dictionary by clicking
 * File->Close opened dictionary menu item
 */
void MainWindow::close_opened_dict(wxCommandEvent& WXUNUSED(event))
{
  if (! this->dict)
    {
      SetStatusText("There is no opened dictionary");
      return;
    }

  wxBeginBusyCursor();

  this->word_list->Clear();

  this->letter_list->Clear();
  this->letter_list->SetValue("");

  this->find_entry->Clear();
  this->find_entry->SetValue("");

  this->word_trans->SetPage("");

  wxStatusBar* status_bar = GetStatusBar();

  if(status_bar->GetStatusText(1) != "")
    status_bar->SetStatusText("\""+status_bar->GetStatusText(1)+"\" closed");
  status_bar->SetStatusText("", 1);

  if (this->dict)
    delete this->dict;
  this->dict = NULL;

  wxEndBusyCursor();
}
