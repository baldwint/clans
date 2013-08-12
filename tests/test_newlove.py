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
        log    =  {'un1': {'result1': newlove.LoveState('old', unread=False)},
                   'un2': {'result2': newlove.LoveState('old', unread=False)}}
        result = [('un1', 1, ['result1',]),
                  ('un2', 2, ['result2', 'result3'])]
        expect =  {'un1': {'result1': newlove.LoveState('old', unread=False)},
                   'un2': {'result2': newlove.LoveState('old', unread=False),
                           'result3': newlove.LoveState('new', unread=True)}}
        updated = newlove._rebuild_log(log, result)
        # can't compare values, only keys, because object comparison fails
        # need to replace LoveState with a native type
        self.assertListEqual(expect.keys(), updated.keys())
        self.assertListEqual(expect['un1'].keys(), updated['un1'].keys())
        self.assertListEqual(expect['un2'].keys(), updated['un2'].keys())
        # love was only added, so original log should be empty
        self.assertDictEqual(log, {'un1': {}, 'un2': {}})

    def test_love_removed(self):
        log    =  {'un1': {'result1': newlove.LoveState('old', unread=False)},
                   'un2': {'result2': newlove.LoveState('old', unread=False),
                           'result3': newlove.LoveState('old', unread=False)}}
        result = [('un1', 1, ['result1',]),
                  ('un2', 2, ['result2',])]
        expect =  {'un1': {'result1': newlove.LoveState('old', unread=False)},
                   'un2': {'result2': newlove.LoveState('old', unread=False)}}
        left   =  {'un1': {},
                   'un2': {'result3': newlove.LoveState('old', unread=False)}}
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

if __name__ == "__main__":
    unittest.main()

