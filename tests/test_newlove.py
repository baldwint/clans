#!/usr/bin/env python
"""
Unit tests for :mod:`clans.ext.newlove`.

"""

import sys
if sys.version_info < (2,7):
    import unittest2 as unittest
else:
    import unittest

import clans.ext.newlove as newlove
import datetime

class TestNewlove(unittest.TestCase):

    def test_love_added(self):
        old = datetime.datetime(2013, 5, 1, 3, 26, 56)
        now = datetime.datetime.utcnow()
        log    =  {'un1': {'result1': dict(timestamp=old, unread=False)},
                   'un2': {'result2': dict(timestamp=old, unread=False)}}
        result = [('un1', 1, ['result1',]),
                  ('un2', 2, ['result2', 'result3'])]
        expect =  {'un1': {'result1': dict(timestamp=old, unread=False)},
                   'un2': {'result2': dict(timestamp=old, unread=False),
                           'result3': dict(timestamp=now, unread=True)}}
        left   =  {'un1': {}, 'un2': {}}
        updated = newlove._rebuild_log(log, result, timestamp=now)
        self.assertDictEqual(expect, updated)
        # love was only added, so original log should be empty
        self.assertDictEqual(log, left)

    def test_love_removed(self):
        old = datetime.datetime(2013, 5, 1, 3, 26, 56)
        log    =  {'un1': {'result1': dict(timestamp=old, unread=False)},
                   'un2': {'result2': dict(timestamp=old, unread=False),
                           'result3': dict(timestamp=old, unread=False)}}
        result = [('un1', 1, ['result1',]),
                  ('un2', 2, ['result2',])]
        expect =  {'un1': {'result1': dict(timestamp=old, unread=False)},
                   'un2': {'result2': dict(timestamp=old, unread=False)}}
        left   =  {'un1': {},
                   'un2': {'result3': dict(timestamp=old, unread=False)}}
        updated = newlove._rebuild_log(log, result)
        self.assertDictEqual(expect, updated)
        # love was only added, so original log should be empty
        self.assertDictEqual(log, left)

from StringIO import StringIO
import copy

class TestFileFormat(unittest.TestCase):

    eg_encoded = '{"un1": {"snip1": {"timestamp": "2013-05-01T03:26:56Z", "unread": false, "love": true}}, "un2": {"snip2": {"timestamp": "2013-07-01T03:46:56Z", "unread": false, "love": true}}}'
    eg_decoded = {
            "un1": {
                "snip1": {
                    "timestamp": datetime.datetime(2013, 5, 1, 3, 26, 56),
                    "unread": False,
                    "love": True
                    }
                },
            "un2": {
                "snip2": {
                    "timestamp": datetime.datetime(2013, 7, 1, 3, 46, 56),
                    "unread": False,
                    "love": True
                    }
                }
            }
    eg_flattened = [
            {
                "lover": "un1",
                "text": "snip1",
                "timestamp": datetime.datetime(2013, 5, 1, 3, 26, 56),
                "unread": False,
                "love": True
                },
            {
                "lover": "un2",
                "text": "snip2",
                "timestamp": datetime.datetime(2013, 7, 1, 3, 46, 56),
                "unread": False,
                "love": True
                }
            ]

    def test_decode(self):
        fl = StringIO(self.eg_encoded)
        decoded = newlove._load_log(fl)
        self.assertDictEqual(decoded, self.eg_decoded)

    def test_encode(self):
        fl = StringIO()
        log = copy.deepcopy(self.eg_decoded)
        newlove._save_log(log, fl)
        fl.seek(0)
        self.assertEqual(fl.read(), self.eg_encoded)
        # the dict should not have been modified
        self.assertDictEqual(log, self.eg_decoded)

    def test_flatten(self):
        log = copy.deepcopy(self.eg_decoded)
        flattened = newlove._flatten_log(log)
        self.assertListEqual(flattened, self.eg_flattened)
        # the dict should not have been modified
        self.assertDictEqual(log, self.eg_decoded)


if __name__ == "__main__":
    unittest.main()

