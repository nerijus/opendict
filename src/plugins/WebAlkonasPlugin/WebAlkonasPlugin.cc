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

#include <cctype>
#include <iostream>
#include "wx/textfile.h"
#include "wx/protocol/http.h"

#include "WebAlkonasPlugin.h"

/*
 * SlowoParser class constructor
 * Does the indexing of letter positions
 */
WebAlkonasPlugin::WebAlkonasPlugin(wxStatusBar* status_bar)
{
  sbar = status_bar;

  words_list = new wxArrayString();
  letter_count = new wxArrayString();

  found = false;

  wxLogDebug(_T("WebAlkonasPlugin created"));
};

/*
 * Searches the file for the given keyword.
 * Returns the string with formatted HTML code.
 */
wxString WebAlkonasPlugin::find(const wxString &keyword)
{
  wxLogDebug(_T("Getting data stream..."));
  http = new wxHTTP();
  //url = new wxURL(wxURL::ConvertToValidURI(keyword));
  //if (url->GetProtocolName() == "http")
  //  url->GetProtocol.SetHeader("Host", "http://127.0.0.1/");
  
  if (! http->Connect("127.0.0.1"))
    {
      wxLogDebug(_T("Can't connect"));
      return "";
    }
  

  http->SetHeader("Content-type", "text/html");
  wxLogDebug(_T("Header: %s"), http->GetHeader("Content-type").c_str());
  //cout<<"URL: "<<url->GetURL().c_str()<<endl;
  //cout<<"Protocol: "<<url->GetProtocolName().c_str()<<endl;
  //cout<<"Path: "<<url->GetPath().c_str()<<endl;
  wxInputStream* stream = http->GetInputStream(keyword);

  if (http->GetError() != wxPROTO_NOERR)
    {
      wxLogDebug(_T("HTTP error"));

      switch(http->GetError())
	{
	case wxPROTO_NETERR:
	  {
	    wxLogDebug(_T("Network error"));
	    break;
	  }
	case wxPROTO_NOFILE:
	  {
	    wxLogDebug(_T("File doesn't exist"));
	    break;
	  }
	case wxPROTO_CONNERR:
	  {
	    wxLogDebug(_T("Connection error"));
	    break;
	  }
	default:
	  {
	    wxLogDebug(_T("Unknown http error"));
	    break;
	  }
	}

      return "";
    }

  //cout<<"Protocol name: "<<http->GetProtocolName().c_str()<<endl;

  if (! stream)
    {
      wxLogDebug(_T("Seems to be no stream..."));
      return "";
    }

  wxLogDebug(_T("Size: %u"), stream->GetSize());
  if (stream->GetSize() == (unsigned)-1)
    {
      wxLogDebug(_T("Unknown stream's size"));
      return "";
    }

  wxString result;
  char data[33];
  int bytes;

  while((bytes = (stream->Read(data, 32)).LastRead()) > 0)
    {
      data[bytes] = '\0';
      result.append(data);
    }

  if (stream) delete stream;

  return result;
}

/*
 * Returns the first letter to use when loading dictionary
 */
char WebAlkonasPlugin::dict_start_letter()
{
   return first_letter;
}

/*
 * Returns words_list array
 */
wxArrayString* WebAlkonasPlugin::get_words_list()
{
  return words_list;
}
/*
 * Returns letter count ("<letter> (<count>)")
 */
wxArrayString* WebAlkonasPlugin::get_letter_count()
{
  return letter_count;
}

/*
 * Removes space characters from the begin and the end of the string
 */
wxString WebAlkonasPlugin::rem_space(const wxString& bad_string)
{
  wxString string = bad_string;
  string = string.Trim();
  string = string.Trim(FALSE);
  return string;
}

/*
 * Converts symbol to upper case if it is alphabetical or
 * does nothing if it is a number
 * It is because converting number to upper case we get another
 * number. For example:
 * toupper('c') == 'C'
 * toupper('7') != '7'
 */
const char WebAlkonasPlugin::conv_to_upper(const char& c)
{
  if (isalpha(c))
    return toupper(c);
  else
    return c;
}


