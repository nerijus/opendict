/*
 * Open Dictionary
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

#ifndef MAIN_WINDOW_H
#define MAIN_WINDOW_H

#if 0 //produces link errors "undefined reference to virtual table" with gcc>2.95
 #ifdef __GNUG__
 #pragma interface
 #pragma implementation
 #endif
#endif //0

#include "wx/wxprec.h"

#ifdef __BORLANDC__
#pragma hdrstop
#endif

#ifndef WX_PRECOMP
#include "wx/wx.h"
#endif

#include "DictWordList.h"
#include "DictLetterList.h"
#include "DictText.h"
#include "DictParser.h"
#include "About.h"

#include "wx/statline.h"
#include "wx/textctrl.h"
#include "wx/listctrl.h"
#include "wx/list.h"
#include "wx/html/htmlwin.h"
#include "wx/statusbr.h"
#include "wx/cursor.h"
#include "wx/utils.h"

#include <iostream> // :-)

class MainWindow: public wxFrame
{

 public:
  MainWindow(const wxString&,
	     const wxPoint&,
	     const wxSize&);
  ~MainWindow();

      void on_quit(wxCommandEvent& event);
      void on_about(wxCommandEvent& event);
      void on_clear(wxCommandEvent& event);
      void on_find(wxCommandEvent& event);
      void on_word_selected(wxCommandEvent& event);
      void on_letter_selected(wxCommandEvent& event);
      void on_change(wxCommandEvent& event);

      void open_slowo_dict(wxCommandEvent& event);
      void open_mova_dict(wxCommandEvent& event);
      void open_po_file(wxCommandEvent& event);

      void close_opened_dict(wxCommandEvent& event);

      void add_dict(wxCommandEvent& event);

      void activate_plugin(wxCommandEvent& event);

      void show_preferences(wxCommandEvent& event);

      void update_words_list(wxListBox*, DictParser*, wxChar);
      void set_letter_count_list(wxComboBox*, DictParser*);
      void update_letter_count_list(wxComboBox*, DictParser*, const wxChar&);
      void update_all_after_search(const wxString&);

      DictParser* dict;

 private:
      wxString default_encoding;
      wxString last_word;

      wxTextCtrl* find_entry;
      DictLetterList* letter_list;
      DictWordList* word_list;
      wxHtmlWindow* word_trans;
      wxHtmlWinParser* html_parser;
      About* about;

      DECLARE_EVENT_TABLE()
};

enum 
{
  QUIT = 1,
  ABOUT,
  OPEN_SLOWO_DICT,
  OPEN_MOVA_DICT,
  OPEN_PO_FILE,
  CLOSE_OPENED,
  ADD_DICT,
  CLEAR,
  FIND_ENTER,
  FIND,
  LETTER_SELECTED,
  OPEN_WEB_ALKONAS_DICT,
  PREFS,
  CHANGE_ENC
};

#endif

