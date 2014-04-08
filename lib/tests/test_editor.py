#
# OpenDict
# Copyright (c) 2003-2006 Martynas Jocius <martynas.jocius@idiles.com>
# Copyright (c) 2007 IDILES SYSTEMS, UAB <support@idiles.com>
#
# Unit Test for editor.py
#

"""
Unit tests for editor.py
"""

import unittest
import os
import sys

sys.path.append('..')

import dicteditor


class TestTranslation(unittest.TestCase):
    """Translation test"""

    translations = dicteditor.Translation()
        

    def test_word(self):
        """Set/Get word should return correct value"""

        self.translations.setWord('test')

        self.assertEquals(self.translations.getWord(), 'test')


    def test_translation(self):
        """Should return correct translations"""

        self.translations.addTranslation('trans1')
        self.translations.addTranslation('trans2', 'comment2')
        self.translations.addTranslation('trans3')
        self.translations.addTranslation('trans3', 'comment3')

        trans = self.translations.getTranslations()

        self.assertEquals(trans.has_key('trans1'), True)
        self.assertEquals(len(trans.keys()), 3)
        self.assertEquals(trans['trans3'], 'comment3')

        trans = {'key1': 'value1', 'key2': 'value2'}
        self.translations.setTranslations(trans)

        self.assertEquals(len(self.translations.getTranslations()), 2)



class TestEditor(unittest.TestCase):
    """Editor test"""

    def test_load(self):
        """Editor should load dictionary from file"""

        editor = dicteditor.Editor()
        self.assertEquals(len(editor.getUnits()), 0)
        
        editor.load("data/sampledict.dwa")
        self.assertEquals(len(editor.getUnits()), 7)


    def test_save(self):
        """Editor should correctly write dictionary to disk"""

        editor = dicteditor.Editor()
        editor.load("data/sampledict.dwa")
        units = editor.getUnits()
        
        editor.save("data/__output.dwa")
        editor.load("data/__output.dwa")

        self.assertEquals(len(units), len(editor.getUnits()))

        os.unlink("data/__output.dwa")


    def test_getUnit(self):
        """getUnit() should return desired Translation object"""

        editor = dicteditor.Editor()
        editor.load("data/sampledict.dwa")
        oldCount = len(editor.getUnits())

        self.assert_(editor.getUnit('du') != None)        


    def test_addUnit(self):
        """addUnit() should add new translation unit or update old one"""

        editor = dicteditor.Editor()
        editor.load("data/sampledict.dwa")
        oldCount = len(editor.getUnits())

        newUnit = dicteditor.Translation()
        newUnit.setWord("test")
        newUnit.addTranslation("utiutiu")

        editor.addUnit(newUnit)

        self.assertEquals(len(editor.getUnits()), oldCount + 1)


    def test_removeUnit(self):
        """removeUnit() should add new translation unit or update old one"""

        editor = dicteditor.Editor()
        editor.load("data/sampledict.dwa")
        oldCount = len(editor.getUnits())

        unit = editor.getUnit('vienas')
        editor.removeUnit(unit)
        
        self.assertEquals(len(editor.getUnits()), oldCount - 1)


    def test_unicode(self):
        """All the strings must be unicode objects"""

        editor = dicteditor.Editor()
        editor.load("data/sampledict.dwa")

        for unit in editor.getUnits()[:10]:
            for trans in unit.getTranslations().keys():
                self.assertEquals(type(trans), type(u''))
        

if __name__ == "__main__":
    unittest.main()
