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

#include "About.h"
#include "images/logo.xpm"

About::About(wxFrame* window)
  : wxDialog(window, -1, "About")
{
  wxString msg;
  msg.Printf(_T("OpenDict 0.1\n")
	     _T("Copyright (c) 2001-2002 Martynas Jocius <mjoc@delfi.lt>\n\n")
	     _T("OpenDict project's goals are to create the universal\n")
	     _T("multi-platform open-source dictionary program for\n")
	     _T("various dictionaries and translations.\n\n")
	     _T("Homepage: http://opendict.sourceforge.net"));

  wxBoxSizer* vbox = new wxBoxSizer(wxVERTICAL);

  wxBitmap* bitmap = new wxBitmap(logo_xpm);

  wxStaticBitmap *logo = new wxStaticBitmap(this, -1, *bitmap, 
					    wxPoint(-1, -1));
  
  vbox->Add(logo, 0, wxALL | wxCENTRE, 5);
  vbox->Add(new wxStaticText(this, -1, msg), 0, wxALL, 10);
  vbox->Add(new wxButton(this, wxID_CANCEL, "OK"), 1, 
	    wxALL | wxALIGN_CENTRE, 5);

  vbox->Fit(this);
  vbox->SetSizeHints(this);

  SetAutoLayout(TRUE);
  SetSizer(vbox);
}
