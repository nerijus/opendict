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

#include "SlowoParser.h"

/*
 * SlowoParser class constructor
 * Does the indexing of letter positions
 */
SlowoParser::SlowoParser(const wxString &fname, 
			 const wxString& enc,
			 wxStatusBar* status_bar)
{
   file_name = fname;
   wxLogDebug(_T("SlowoParser(): file_name: %s"), file_name.c_str());

   if (enc.Length() != 0)
     default_encoding = enc;
   else
     default_encoding = _T("iso8859-1");

   sbar = status_bar;
   sbar->SetStatusText(_T("Parsing..."));

   wxTextFile *file = new wxTextFile();

   bool success = file->Open(file_name);
   if (success == false)
   {
      wxLogError(_("SlowoParser::SlowoParser(): Can't open %s"), file_name.c_str());
      exit(1);
   }

   words_list = new wxArrayString();
   letter_count = new wxArrayString();

   found = false;

   wxString line;
   wxString word;
   wxString translation;
   wxString tmp;

   wxChar c;
   int lnumber = 1;

   int l_count = 1;
   wxChar l_char;

   bool l_found = false;

   line = file->GetFirstLine();
   line = rem_space(line);
   l_char = c = conv_to_upper(line[0u]);
   first_letter_array.Add(c);
   letter_starts_at_line_array.Add(lnumber);
   lnumber++;

   // Adding first word to list
   for (unsigned int i=0; i<line.Length(); i++)
   {
      if (line[i] == '=')
      {
	words_list->Add(rem_space(line.SubString(0, i-1)));
      }
   }
   
   if (isalnum(c))
   {
      first_letter = c;
      l_found = true;
   }

   while(file->Eof() == false)
   {
      line = file->GetNextLine();
      line = rem_space(line);
      
      if (l_found == false)
      {
         if (isalnum(line[0u]))
         {
            first_letter = conv_to_upper(line[0u]);
            l_found = true;
         }
      }

      if (conv_to_upper(line[0u]) != c)
      {
         c = conv_to_upper(line[0u]);
         first_letter_array.Add(c);
         letter_starts_at_line_array.Add(lnumber);

	 tmp.Printf(_T("%c (%d)"), l_char, l_count); 
	 letter_count->Add(tmp);
	 l_char = c;
	 l_count = 0;
      }
      
      for(unsigned int i=0; i<line.Length(); i++)
      {
	if (line[i] == '=')
	{
	  words_list->Add(rem_space(line.SubString(0, i-1)));
	}
      }

      lnumber++;
      l_count++;
   }

   file->Close();
   wxLogDebug(_T("done"));

   sbar->SetStatusText(_T(""));
};

/*
 * Searches the file for the given keyword.
 * Returns the string with formatted HTML code.
 */
wxString SlowoParser::find(const wxString &keyword)
{
  wxString sbar_msg = _T("Searching... ");
  sbar->SetStatusText(sbar_msg);

  wxLogDebug(_T("Searching for \"%s\"... "), keyword.c_str());

   wxChar c = conv_to_upper(keyword[0]);
  
   long starts_at_line = (long)letter_starts_at_line_array.Item(first_letter_array.Index(c));
   
   int li = 0; // last index

   wxString line; // current line
   wxString word; // word maching keyword
   wxString translation; // translation
   wxString comment; // comment
   wxString result; // formatted HTML code

   bool not_first_trans = false;

   wxTextFile *file = new wxTextFile();
   bool success = file->Open(file_name);

   if (success == false)
   {
      wxLogError(_("SlowoParser::find(): Can't open %s"), file_name.c_str());
      exit(1);
   }
   
   found = false;
   short results_found = 0;

   bool starts_at_first_line = false;
   if (starts_at_line > 1) {
     file->GoToLine(starts_at_line-2);
   }
   else {
     file->GoToLine(1);
     starts_at_first_line = true;
   }

   // Start new HTML page, text encoding must be unicode, 
   // I'm doing different just for now.
   result = _T("<html>\n<head>\n<meta http-equiv=\"Content-Type\" ");
   result += _T("content=\"text/html; charset=") + default_encoding + _T("\">\n");
   result += _T("</head>\n<body>\n");
   result += _T("<font face=\"fixed\" size=\"2\">\n");

   bool searching = true;
   while(searching && file->Eof() == FALSE)
   {
     if (starts_at_first_line) {
       line = file->GetFirstLine();
       starts_at_first_line = false;
     }
     else
       line = file->GetNextLine();

     line = rem_space(line);

      if (conv_to_upper(line[0u]) != c)
	{
	  searching = false; // Stop if word starts in another letter
	  continue;
	}

      wxString orig;

      if (line.Contains(keyword))
      {
	found = true;
	results_found++;

         for (unsigned int i=0; i<line.Length(); i++)
         {
            if (line[i] == '=')
            {
               result += _T("<b>");
	       orig = rem_space(line.SubString(0, i-1));
	       if (! orig.Contains(keyword))
		 {
		   break;
		 }
               result += orig;
               result += _T("</b>:<br>\n");
               li = i + 1;
            }
   
            if (line[i] == _T(';'))
            {
               if (not_first_trans)
                  result += _T(", ");
               result += rem_space(line.SubString(li, i-1));
	       
               li = i + 1;
               not_first_trans = true;
            }

            if (line[i] == _T('/') && line[i+1] == _T('/'))
            {
               result += rem_space(line.SubString(li, i-1));
               result += _T("<br>\n(<i>");
               result += rem_space(line.SubString(i+2, line.Length()-2));
	       
               result += _T("</i>)\n<p>\n");
               break;
	    }
         }

	 if (line.Find(_T("//")) == -1)
	   result += _T("<p>\n");

	 not_first_trans = false;
      }
   }

   result += _T("</font>\n");
   result += _T("</body></html>");

   file->Close();

   if (found)
     {
       sbar_msg.Printf(_T("%d found"), results_found);
       sbar->SetStatusText(sbar_msg);
     }
   else
     {
       sbar_msg = _T("\"")+keyword+_T("\" not found");
       sbar->SetStatusText(sbar_msg);
     }

   return result;
}

/*
 * Returns the first letter to use when loading dictionary
 */
wxChar SlowoParser::dict_start_letter()
{
   return first_letter;
}

/*
 * Returns words_list array
 */
wxArrayString* SlowoParser::get_words_list()
{
  return words_list;
}
/*
 * Returns letter count ("<letter> (<count>)")
 */
wxArrayString* SlowoParser::get_letter_count()
{
  return letter_count;
}

/*
 * Removes space characters from the begin and the end of the string
 */
wxString SlowoParser::rem_space(const wxString& bad_string)
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
const wxChar SlowoParser::conv_to_upper(const wxChar& c)
{
  if (isalpha(c))
    return toupper(c);
  else
    return c;
}

void SlowoParser::set_default_encoding(const wxString& enc)
{
  default_encoding = enc;
}

