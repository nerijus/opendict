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

#include "MovaParser.h"

/*
 * MovaParser class constructor
 * Does the indexing of letter positions
 */
MovaParser::MovaParser(const wxString &fname, 
		       const wxString &enc,
		       wxStatusBar* status_bar)
{
   file_name = fname;
   cout<<"MovaParser: file_name: "<<file_name.c_str()<<endl;

   if (enc.Length() != 0)
     default_encoding = enc;
   else
     default_encoding = "iso8859-1"; 

   sbar = status_bar;
   sbar->SetStatusText("Parsing...");

   wxTextFile *file = new wxTextFile();

   if (file->Open(file_name) == false)
   {
      cerr<<"MovaParser: can't open "<<file_name.c_str()<<endl;
      exit(1);
   }

   words_list = new wxArrayString();
   letter_count = new wxArrayString();

   found = false;

   wxString line;
   wxString word;
   wxString translation;
   wxString tmp;

   char c;
   int lnumber = 1;

   int l_count = 1;
   char l_char;

   bool l_found = false;

   line = file->GetFirstLine();
   line = rem_space(line);
   l_char = c = conv_to_upper(line[0]);
   first_letter_array.Add(c);
   letter_starts_at_line_array.Add(lnumber);
   lnumber++;

   // Adding first word to list
   for (unsigned int i=0; i<line.Length(); i++)
   {
      if (line[i] == ' ' && line[i+1] == ' ')
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
         if (isalnum(line[0]))
         {
            first_letter = conv_to_upper(line[0]);
            l_found = true;
         }
      }

      if (conv_to_upper(line[0]) != c)
      {
         c = conv_to_upper(line[0]);
         first_letter_array.Add(c);
         letter_starts_at_line_array.Add(lnumber);

	 tmp.Printf("%c (%d)", l_char, l_count); 
	 letter_count->Add(tmp);
	 l_char = c;
	 l_count = 0;
      }
      
      for(unsigned int i=0; i<line.Length(); i++)
      {
	if (line[i] == ' ' && line[i+1] == ' ')
	{
	  words_list->Add(rem_space(line.SubString(0, i-1)));
	}
      }

      lnumber++;
      l_count++;
   }

   file->Close();
   cout<<"done\n";

   sbar->SetStatusText("");
};

/*
 * Searches the file for the given keyword.
 * Returns the string with formatted HTML code.
 */
wxString MovaParser::find(const wxString &keyword)
{
  wxString sbar_msg = "Searching... ";
  sbar->SetStatusText(sbar_msg);

  cout<<"Searching for \""<<keyword.c_str()<<"\"... \n";

   char c = conv_to_upper(keyword[0]);
  
   long starts_at_line = (long)letter_starts_at_line_array.Item(first_letter_array.Index(c));

   wxString line; // current line
   wxString word; // word maching keyword
   wxString translation; // translation
   wxString comment; // comment
   wxString result; // formatted HTML code

   short results_found = 0;

   bool not_first_trans = false;

   wxTextFile *file = new wxTextFile();
   bool success = file->Open(file_name);

   if (success == false)
   {
      cerr<<"MovaParser::find(): can't open "<<file_name<<endl;
      exit(1);
   }
   
   found = false;

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
   result = "<html>\n<head>\n<meta http-equiv=\"Content-Type\" ";
   result += "content=\"text/html; charset=" + default_encoding + "\">\n";
   result += "</head>\n<body>\n";
   result += "<font face=\"fixed\" size=\"2\">\n";

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

      if (conv_to_upper(line[0]) != c)
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
            if (line[i] == ' ' && line[i+1] == ' ')
            {
               result += "<b>";
	       orig = rem_space(line.SubString(0, i-1));
	       if (! orig.Contains(keyword))
		 {
		   break;
		 }
               result += orig;
               result += "</b>:<br>\n";

	       result += rem_space(line.SubString(i, line.Length()));
	       result += "<p>\n\n";
	       break;
            }
	 }
	 not_first_trans = false;
      }
   }

   result += "</font>\n";
   result += "</body></html>";

   file->Close();

   if (found)
     {
       sbar_msg.Printf("%d found", results_found);
       sbar->SetStatusText(sbar_msg);
     }
   else
     {
       sbar_msg = "\""+keyword+"\" not found";
       sbar->SetStatusText(sbar_msg);
     }

   return result;
}

/*
 * Returns the first letter to use when loading dictionary
 */
char MovaParser::dict_start_letter()
{
   return first_letter;
}

/*
 * Returns words_list array
 */
wxArrayString* MovaParser::get_words_list()
{
  return words_list;
}

/*
 * Returns letter count ("<letter> (<count>)")
 */
wxArrayString* MovaParser::get_letter_count()
{
  return letter_count;
}

/*
 * Removes space characters from the begin and the end of the string
 */
wxString MovaParser::rem_space(const wxString& bad_string)
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
const char MovaParser::conv_to_upper(const char& c)
{
  if (isalpha(c))
    return toupper(c);
  else
    return c;
}

/*
 * Sets default html encoding
 */
void MovaParser::set_default_encoding(const wxString& enc)
{
  default_encoding = enc;
}

