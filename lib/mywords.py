# OpenDict
# Copyright (c) 2003-2004 Martynas Jocius <mjoc@akl.lt>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your opinion) any later version.
#
# This program is distributed in the hope that will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MECHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more detals.
#
# You shoud have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# 02111-1307 USA
#
# Module: mywords

# TODO: Write documentation strings for each class/method.

import os
import codecs

import info

from misc import *

from wxPython.wx import *
_ = wxGetTranslation

class MyWords:

    def __init__(self):

        self.words = []
        self.fileName = None 

        self.setFileName(os.path.join(info.uhome, "mywords.txt"))
         
#       try:
#           self.words = self.read(self.getFileName())
#       except Exception, e:
#           raise Exception, e


    def setFileName(self, fileName):

        self.fileName = fileName


    def getFileName(self):

        return self.fileName


    def getWords(self):

        return self.words


    def addWord(self, word):

        if not word in self.words:
            self.words.append(word)
            self.words.sort()

            status = self.save()
            if status:
                return status    
        else:
            return "Word \"%s\" already added" % word  


    def removeWord(self, word):

        if word in self.words:
            self.words.remove(word)
            status = self.save()
            if status:
                return status    
        else:
            return "No such word \"%s\"" % word  
              
        
    def read(self):

        self.words = []
                  
        try:
             fd = open(self.getFileName())
             data = fd.readlines()
               
             for line in data:
                self.words.append(line.strip())
        except Exception, e:
            raise Exception, e


    def save(self):

        text = ""
         
        for word in self.words:
            text += word + "\r\n"

        fd = open(self.getFileName(), "w")
        
        if info.__unicode__:
            try:
                
                sw = codecs.lookup("utf-8")[3]
                fd = sw(fd)
                
            except:
                printError() 
                return _("Can't save changes to %s") % self.getFileName()
                
        fd.write(text)
        fd.close()
        