# -*- coding: UTF-8 -*-
#
# OpenDict
# Copyright (c) 2003-2006 Martynas Jocius <martynas.jocius@idiles.com>
# Copyright (c) 2007 IDILES SYSTEMS, UAB <support@idiles.com>
#
# Unit Test for editor.py
#

"""
Unit tests for plugin.py
"""

import unittest
import os
import sys

sys.path.append('../..')

from lib import newplugin


class TestPluginInfo(unittest.TestCase):
    """PluginInfo test"""

    def test_getInfo(self):
        """PluginInfo should have correct attributes"""

        fd = open("data/plugin.xml")
        xmlData = fd.read()
        fd.close()

        info = newplugin.PluginInfo(xmlData)
        
        self.assertEquals(info.name, u"Sample plugin name ąčę")
        self.assertEquals(info.version, u"1.2.3")
        self.assertEquals(info.authors, [{"name": u"Sample author name ąčę",
                                "email": u"sample@example.com"}])
        self.assertEquals(info.module, {"name": u"mymodule.py",
                                        "lang": u"Python"})
        self.assertEquals(info.encoding, u"UTF-8")
        self.assertEquals(info.usesWordList, True)
        self.assertEquals(info.opendictVersion, u"0.5.8")
        self.assertEquals(info.pythonVersion, u"2.3")

        platforms =  [{"name": u"Linux"},
                                 {"name": u"Windows"},
                                 {"name": u"BSD"}]
        platforms.sort()
        self.assertEquals(info.platforms, platforms)
        self.assertEquals(info.description,
                          u"This is short or long description ąčę.")
        self.assertEquals(info.xmlData, xmlData)


class TestDictionaryPlugin(unittest.TestCase):
    """Test PluginHandler class"""

    def test_class(self):
        """__init__ should load plugin info and module"""
        
        p = newplugin.DictionaryPlugin(os.path.realpath('data/sampleplugin'))

        self.assertEquals(p.__class__, newplugin.DictionaryPlugin)
        self.assert_(p.info != None)
        self.assert_(p.dictionary != None)
        self.assert_(p.isValid() == True)
        self.assertEquals(p.info.__class__, newplugin.PluginInfo)
        self.assertEquals(len(p.dictionary.search('x').words), 20)

        self.assertRaises(newplugin.InvalidPluginException,
                          newplugin.DictionaryPlugin, 'blabla')
                                        



if __name__ == "__main__":
    unittest.main()
