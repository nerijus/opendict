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

#ifndef OPENDICT_H
#define OPENDICT_H

#ifdef __GNUG__
#pragma interface
#pragma implementation
#endif

#include "wx/wxprec.h"

#ifdef __BORLANDC__
#pragma hdrstop
#endif

#ifndef WX_PRECOMP
#include "wx/wx.h"
#endif

#include "MainWindow.h"

class OpenDict: public wxApp
{
   public:
      virtual bool OnInit();
      virtual int OnExit();

      MainWindow* mainWindow;

};

BEGIN_EVENT_TABLE(MainWindow, wxFrame)

     EVT_MENU(OPEN_SLOWO_DICT, MainWindow::open_slowo_dict)
     EVT_MENU(OPEN_MOVA_DICT, MainWindow::open_mova_dict)
     EVT_MENU(OPEN_PO_FILE, MainWindow::open_po_file)
     EVT_MENU(CLOSE_OPENED, MainWindow::close_opened_dict)
     EVT_MENU(QUIT, MainWindow::on_quit)   
     EVT_MENU(ADD_DICT, MainWindow::add_dict)
     EVT_MENU(PREFS, MainWindow::show_preferences)
     EVT_MENU(ABOUT, MainWindow::on_about)
     EVT_MENU(OPEN_WEB_ALKONAS_DICT, MainWindow::activate_plugin)
     EVT_MENU(-1, MainWindow::on_change)
     EVT_TEXT_ENTER(FIND_ENTER, MainWindow::on_find)
     EVT_BUTTON(CLEAR, MainWindow::on_clear)
     EVT_BUTTON(FIND, MainWindow::on_find)
     EVT_LISTBOX(wxEVT_COMMAND_LISTBOX_SELECTED, MainWindow::on_word_selected)
     EVT_COMBOBOX(LETTER_SELECTED, MainWindow::on_letter_selected)
     
END_EVENT_TABLE()

IMPLEMENT_APP(OpenDict);

#endif

