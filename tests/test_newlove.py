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

class TestNewlove(unittest.TestCase):

    def test_love_added(self):
        log    =  {'un1': {'result1': dict(timestamp='old', unread=False)},
                   'un2': {'result2': dict(timestamp='old', unread=False)}}
        result = [('un1', 1, ['result1',]),
                  ('un2', 2, ['result2', 'result3'])]
        expect =  {'un1': {'result1': dict(timestamp='old', unread=False)},
                   'un2': {'result2': dict(timestamp='old', unread=False),
                           'result3': dict(timestamp='new', unread=True)}}
        updated = newlove._rebuild_log(log, result)
        # can't compare values, only keys, because object comparison fails
        # need to replace LoveState with a native type
        self.assertListEqual(expect.keys(), updated.keys())
        self.assertListEqual(expect['un1'].keys(), updated['un1'].keys())
        self.assertListEqual(expect['un2'].keys(), updated['un2'].keys())
        # love was only added, so original log should be empty
        self.assertDictEqual(log, {'un1': {}, 'un2': {}})

    def test_love_removed(self):
        log    =  {'un1': {'result1': dict(timestamp='old', unread=False)},
                   'un2': {'result2': dict(timestamp='old', unread=False),
                           'result3': dict(timestamp='old', unread=False)}}
        result = [('un1', 1, ['result1',]),
                  ('un2', 2, ['result2',])]
        expect =  {'un1': {'result1': dict(timestamp='old', unread=False)},
                   'un2': {'result2': dict(timestamp='old', unread=False)}}
        left   =  {'un1': {},
                   'un2': {'result3': dict(timestamp='old', unread=False)}}
        updated = newlove._rebuild_log(log, result)
        # can't compare values, only keys, because object comparison fails
        # need to replace LoveState with a native type
        self.assertListEqual(expect.keys(), updated.keys())
        self.assertListEqual(expect['un1'].keys(), updated['un1'].keys())
        self.assertListEqual(expect['un2'].keys(), updated['un2'].keys())
        # original log should still contain deleted love
        self.assertListEqual(log.keys(), left.keys())
        self.assertListEqual(log['un1'].keys(), left['un1'].keys())
        self.assertListEqual(log['un2'].keys(), left['un2'].keys())

import datetime
from StringIO import StringIO

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

    def test_decode(self):
        fl = StringIO(self.eg_encoded)
        decoded = newlove._load_log(fl)
        self.assertDictEqual(decoded, self.eg_decoded)

    def test_encode(self):
        fl = StringIO()
        newlove._save_log(self.eg_decoded, fl)
        fl.seek(0)
        self.assertEqual(fl.read(), self.eg_encoded)


if __name__ == "__main__":
    unittest.main()

