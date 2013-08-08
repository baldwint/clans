#!/usr/bin/env python
"""
A test to make sure the documentation isn't condescending as all hell

"""

import sys
if sys.version_info < (2,7):
    import unittest2 as unittest
else:
    import unittest

import os
from io import StringIO

class TestCondescension(unittest.TestCase):

    def setUp(self):
        # get texts
        testdir, _ = os.path.split(os.path.abspath(__file__))
        docdir = os.path.join(testdir, os.pardir, 'docs')

        texts = {}
        fts = ('.rst',)

        for fn in os.listdir(os.path.abspath(docdir)):
            _, ext = os.path.splitext(fn)
            if ext in fts:
                path = os.path.join(docdir, fn)
                with open(path) as fl:
                    texts[fn] = fl.read().decode('utf8')

        # loop over and make lower case
        for k,v in texts.iteritems():
            texts[k] = v.lower()
            
        self.texts = texts

    def should_not_contain(self, phrase):
        for fn, text in self.texts.iteritems():
            self.assertNotIn(phrase, text,
                    msg='%s contains "%s"' % (fn, phrase))

    def test_simply(self):
        self.should_not_contain(u'simply')

    def test_just(self):
        self.should_not_contain(u'just')

if __name__ == "__main__":
    unittest.main()

