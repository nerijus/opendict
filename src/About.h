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

#ifndef ABOUT_H
#define ABOUT_H

#include "wx/wx.h"
#include "wx/bitmap.h"
#include "wx/image.h"
#include "wx/statbmp.h"

class About: public wxDialog
{
 public:
  About(wxFrame*);

  // private:
  // DECLARE_EVENT_TABLE();
};

//enum {
//  ABOUT_OK
//}

#endif
