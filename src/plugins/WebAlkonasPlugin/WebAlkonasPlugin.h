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

#ifndef ALKONAS_PLUGIN_H
#define ALKONAS_PLUGIN_H

#include "wx/statusbr.h"
#include "wx/stream.h"
#include "wx/wfstream.h"
#include "wx/url.h"
#include "wx/log.h"
#include "wx/intl.h"

#include "../../DictParser.h"
#include <iostream>

class WebAlkonasPlugin: public DictParser
{
   public:
      WebAlkonasPlugin(wxStatusBar*);
      ~WebAlkonasPlugin() { wxLogDebug(_T("[+] WebAlkonasPlugin is dead")); };

      wxString find(const wxString &);
      wxChar dict_start_letter();
      CharVector word_first_letter();
      LongVector letter_starts_at_line();

      wxArrayString* get_words_list();
      wxArrayString* get_letter_count();

      const wxChar conv_to_upper(const wxChar&);

      bool found;
      bool get_found() { return found; }

      void set_default_encoding(const wxString& enc)
	{
	  default_encoding = enc;
	}

   private:
      wxURL* url;
      wxHTTP* http;

      wxString file_name;
      wxChar first_letter;
      wxString default_encoding;

      CharVector first_letter_array;
      LongVector letter_starts_at_line_array;

      wxArrayString* words_list;
      wxArrayString* letter_count;

      wxStatusBar* sbar;

      wxString rem_space(const wxString&);
      
};

#endif

