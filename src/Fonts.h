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
    { "iso8859-1", "Western European" }, 
    { "iso8859-2", "Central European" },
    { "iso8859-3", "Esperanto" },
    { "iso8859-4", "Baltic (old)" },
    { "iso8859-5", "Cyrilic" },
    { "iso8859-6", "Arabic" },
    { "iso8859-7", "Greek" },
    { "iso8859-8", "Hebrew" },
    { "iso8859-9", "Turkish" },
    { "iso8859-10", "Nordic" },
    { "iso8859-11", "Thai" },
    { "iso8859-12", "Indian" },
    { "iso8859-13", "Baltic" },
    { "iso8859-14", "Celtic" },
    { "iso8859-15", "Western European with Euro" },
    { "koi8-r", "Cyrilic" },
    { "windows-1250", "Windows Central European" },
    { "windows-1251", "Windows Cyrilic" },
    { "windows-1252", "Windows Western European" },
    { "windows-1253", "Windows Greek" },
    { "windows-1254", "Windows Turkish" },
    { "windows-1255", "Windows Hebrew" },
    { "windows-1256", "Windows Arabic" },
    { "windows-1257", "Windows Baltic" },
    { "windows-437", "Windows/DOS OEM" }
  };

#define FAM 12
static wxString font_families[] = 
  {
    "newspaper",
    "fangsong ti",
    "fixed",
    "nil",
    "clean",
    "courier",
    "helvetica",
    "symbol",
    "times",
    "lucida",
    "terminal",
    "cursor"
  };


#endif
