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

#ifndef FONTS_H
#define FONTS_H

#include "wx/wx.h"

#define ENC 25
static wxString font_encodings[][2] = 
  {
    { _T("iso8859-1"), _T("Western European") }, 
    { _T("iso8859-2"), _T("Central European") },
    { _T("iso8859-3"), _T("Esperanto") },
    { _T("iso8859-4"), _T("Baltic (old)") },
    { _T("iso8859-5"), _T("Cyrilic") },
    { _T("iso8859-6"), _T("Arabic") },
    { _T("iso8859-7"), _T("Greek") },
    { _T("iso8859-8"), _T("Hebrew") },
    { _T("iso8859-9"), _T("Turkish") },
    { _T("iso8859-10"), _T("Nordic") },
    { _T("iso8859-11"), _T("Thai") },
    { _T("iso8859-12"), _T("Indian") },
    { _T("iso8859-13"), _T("Baltic") },
    { _T("iso8859-14"), _T("Celtic") },
    { _T("iso8859-15"), _T("Western European with Euro") },
    { _T("koi8-r"), _T("Cyrilic") },
    { _T("windows-1250"), _T("Windows Central European") },
    { _T("windows-1251"), _T("Windows Cyrilic") },
    { _T("windows-1252"), _T("Windows Western European") },
    { _T("windows-1253"), _T("Windows Greek") },
    { _T("windows-1254"), _T("Windows Turkish") },
    { _T("windows-1255"), _T("Windows Hebrew") },
    { _T("windows-1256"), _T("Windows Arabic") },
    { _T("windows-1257"), _T("Windows Baltic") },
    { _T("windows-437"), _T("Windows/DOS OEM") }
  };

#define FAM 12
static wxString font_families[] = 
  {
    _T("newspaper"),
    _T("fangsong ti"),
    _T("fixed"),
    _T("nil"),
    _T("clean"),
    _T("courier"),
    _T("helvetica"),
    _T("symbol"),
    _T("times"),
    _T("lucida"),
    _T("terminal"),
    _T("cursor")
  };


#endif
