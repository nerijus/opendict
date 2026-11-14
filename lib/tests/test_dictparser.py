# -*- coding: utf-8 -*-
#
# Unit tests for lib/parser.py (dictd dictionaries)
#

"""
Unit tests for the built-in dictd dictionary parser (lib/parser.py)
"""

import os
import shutil
import sys
import tempfile
import unittest

sys.path.append('../..')

from lib.extra.dictdlib import b64_encode
from lib import errortype
from lib import parser

ENCODING = 'ISO-8859-13'

ENTRIES = [("cerkv\u0117", "church"),
           ("alias", "nickname"),
           ("\u017ealias", "green")]


def stripKey(word):
    """Index key the way dictfmt writes it without --allchars:
    only ASCII letters, digits and spaces are kept"""

    return bytes(b for b in word.encode(ENCODING).lower()
                 if b < 128 and (chr(b).isalnum() or b == 32))


class TestDictParser(unittest.TestCase):
    """Test DictParser class"""

    def setUp(self):
        self.directory = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.directory)

    def makeDictionary(self, allchars=False):
        """Write dictd files and return started parser"""

        data = b''
        index = []
        items = [(word.encode(ENCODING) if allchars else stripKey(word),
                  "%s\n     %s\n" % (word, trans))
                 for (word, trans) in ENTRIES]
        if allchars:
            items.append((b'00-database-allchars',
                          "00-database-allchars\n     \n"))

        for key, text in items:
            encoded = text.encode(ENCODING)
            index.append(key + b'\t' + b64_encode(len(data)).encode()
                         + b'\t' + b64_encode(len(encoded)).encode() + b'\n')
            data += encoded

        path = os.path.join(self.directory, 'test.dict')
        open(path, 'wb').write(data)
        open(os.path.join(self.directory, 'test.index'), 'wb') \
            .write(b''.join(index))

        dictionary = parser.DictParser(path)
        dictionary.setEncoding(ENCODING)
        dictionary.start()
        return dictionary

    def search(self, dictionary, word):
        return dictionary.search(word.encode(ENCODING))

    def test_nonAsciiLetters(self):
        """Word with non-ASCII letters should be found when the index
        keys are stripped of them"""

        dictionary = self.makeDictionary()
        result = self.search(dictionary, "cerkv\u0117")

        self.assertEqual(result.getError(), errortype.OK)
        self.assertTrue("church" in result.translation)
        self.assertEqual(result.words, ["cerkv\u0117".encode(ENCODING)])

    def test_sharedKey(self):
        """Only the entry for the searched word should be shown if several
        words share one stripped key"""

        dictionary = self.makeDictionary()

        result = self.search(dictionary, "\u017ealias")
        self.assertTrue("green" in result.translation)
        self.assertTrue("nickname" not in result.translation)

        result = self.search(dictionary, "alias")
        self.assertTrue("nickname" in result.translation)
        self.assertTrue("green" not in result.translation)

    def test_allchars(self):
        """Keys are not stripped if the database has 00-database-allchars"""

        dictionary = self.makeDictionary(allchars=True)
        result = self.search(dictionary, "\u017ealias")

        self.assertTrue("green" in result.translation)
        self.assertTrue("nickname" not in result.translation)

    def test_notFound(self):
        """Unknown word should not be found"""

        dictionary = self.makeDictionary()
        result = self.search(dictionary, "\u017eyvas")

        self.assertEqual(result.getError(), errortype.NOT_FOUND)

    def test_wrongEncoding(self):
        """Wrong encoding should give an error, not an exception"""

        dictionary = self.makeDictionary()
        dictionary.setEncoding('UTF-8')
        result = dictionary.search("cerkv\u0117".encode('UTF-8'))

        self.assertEqual(result.getError(), errortype.INVALID_ENCODING)


if __name__ == "__main__":
    unittest.main()
