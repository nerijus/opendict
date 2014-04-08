#
# OpenDict
# Copyright (c) 2003-2006 Martynas Jocius <martynas.jocius@idiles.com>
# Copyright (c) 2007 IDILES SYSTEMS, UAB <support@idiles.com>
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

"""
Dictionary editor module
"""


class Translation:
    """Translation in Slowo format

    Keeps one original word and a dictionary of translations
    """

    def __init__(self):
        """Initialize"""

        self.word = None
        self.translations = {}
        

    def setWord(self, word):
        """Set word"""

        self.word = word


    def getWord(self):
        """Return word"""

        return self.word


    def addTranslation(self, trans, comment=None):
        """Set translation object"""
        
        self.translations[trans] = comment


    def setTranslations(self, newTrans):
        """Set translation dictionary"""

        self.translations = newTrans


    def getTranslations(self):
        """Return translation object"""

        return self.translations


class Editor:
    """Slowo dictionary editor"""

    def __init__(self, filePath=None):
        """Initialize variables and load dictionary if requested"""

        self.filePath = filePath
        self.units = []
        self.encoding = 'UTF-8'

        if filePath:
            self.load(filePath)


    def load(self, filePath):
        """Load dictionary into memory"""

        self.filePath = filePath
        self.units = []

        try:
            fd = open(filePath)

            for line in fd:
                try:
                    line = unicode(line, self.encoding)
                except Exception, e:
                    raise Exception, "Unable to encode text in %s" \
                          % self.encoding
                
                word, end = line.split('=')
                word = word.strip()
                
                translation = Translation()
                translation.setWord(word)

                chunks = end.split(';')
                for chunk in chunks:
                    chunk = chunk.strip()
                    if not chunk:
                        continue
                    
                    try:
                        trans, comment = chunk.split('//')
                    except:
                        trans = chunk
                        comment = None

                    trans = trans.strip()
                    if comment:
                        comment = comment.strip()

                    translation.addTranslation(trans, comment)
                self.units.append(translation)

            fd.close()

        except Exception, e:
            raise Exception, "Unable to read dictionary: %s" % e


    def save(self, filePath=None):
        """Write data to disk"""

        if not filePath:
            filePath = self.filePath

        try:
            fd = open(filePath, 'w')

            for unit in self.getUnits():
                outstr = "%s = " % unit.getWord()
                chunks = []

                for trans, comment in unit.getTranslations().items():
                    if comment:
                        chunks.append("%s // %s" % (trans, comment))
                    else:
                        chunks.append(trans)
                outstr += u' ; '.join(chunks) + u' ;'
                outstr = outstr.encode(self.encoding)
                print >> fd, outstr
        except Exception, e:
            raise Exception, "Unable to save dictionary: %s" % e


    def getUnit(self, word):
        """Return Translation object for the word"""

        for unit in self.units:
            if unit.getWord() == word:
                return unit

        return None


    def addUnit(self, unit):
        """Adds translation unit to dictionary"""

        self.units.append(unit)


    def removeUnit(self, unit):
        """Removes translation unit defined by word"""

        self.units.remove(unit)


    def getUnits(self):
        """Return list of translation objects"""

        return self.units
    
