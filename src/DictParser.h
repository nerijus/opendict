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

#ifndef DICT_PARSER_H
#define DICT_PARSER_H

#include "wx/dynarray.h"
#include "wx/string.h"

#ifndef CHAR_VECTOR
#define CHAR_VECTOR
WX_DEFINE_ARRAY(char, CharVector);
#endif

#ifndef LONG_VECTOR
#define LONG_VECTOR
WX_DEFINE_ARRAY(long, LongVector);
#endif

class DictParser
{
   public:
  DictParser() {};
  virtual ~DictParser() {};

  virtual wxString find(const wxString &) = 0;
  //   virtual char dict_start_letter() = 0;
  //  virtual CharVector first_letter() = 0;
  //  virtual LongVector first_letter_index() = 0;
  virtual wxArrayString* get_words_list() = 0;
  virtual wxArrayString* get_letter_count() = 0;

  virtual bool get_found() = 0;
  virtual void set_default_encoding(const wxString&) = 0;

  virtual wxString rem_space(wxString&);
  virtual const char conv_to_upper(const char&) = 0;
};

#endif

