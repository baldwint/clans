#!/usr/bin/env python
"""
Unit tests for :mod:`clans.ext.newlove`.

"""

import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import clans.ext.newlove as newlove
import datetime
import copy


class TestNewlove(unittest.TestCase):

    def test_love_added(self):
        old = datetime.datetime(2013, 5, 1, 3, 26, 56)
        now = datetime.datetime.utcnow()
        log    =  {'un1': {'result1': dict(timestamp=old, unread=False)},
                   'un2': {'result2': dict(timestamp=old, unread=False)}}
        result = [('un1', 1, ['result1', ]),
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
        result = [('un1', 1, ['result1', ]),
                  ('un2', 2, ['result2', ])]
        expect =  {'un1': {'result1': dict(timestamp=old, unread=False)},
                   'un2': {'result2': dict(timestamp=old, unread=False)}}
        left   =  {'un1': {},
                   'un2': {'result3': dict(timestamp=old, unread=False)}}
        updated = newlove._rebuild_log(log, result)
        self.assertDictEqual(expect, updated)
        # love was only added, so original log should be empty
        self.assertDictEqual(log, left)


class TestModifyResult(unittest.TestCase):

    def setUp(self):
        new = datetime.datetime(2013, 8, 4, 3, 26, 50)
        old = datetime.datetime(2013, 6, 1, 22, 28, 36)
        older = datetime.datetime(2012, 5, 1, 13, 36, 56)
        self.log    =  {'un1': {'result1': dict(timestamp=old, unread=False)},
                        'un2': {'result2': dict(timestamp=older, unread=False),
                                'result3': dict(timestamp=new, unread=True)}}
        self.result = [('un1', 1, ['result1', ]),
                       ('un2', 2, ['result2', 'result3'])]

    def test_no_options(self):
        result = copy.deepcopy(self.result)
        log = copy.deepcopy(self.log)
        # test with no options: nothing should be modified
        newlove.modify_results(result, log)
        self.assertEqual(result, self.result)
        self.assertDictEqual(log, self.log)

    def test_result_filtering(self):
        filtered_result = [('un1', 1, []),
                           ('un2', 2, ['result3', ])]
        result = copy.deepcopy(self.result)
        log = copy.deepcopy(self.log)
        # test to filter out old stuff
        newlove.modify_results(result, log, only_show_new=True)
        self.assertNotEqual(result, self.result)  # should be in-place modified
        self.assertDictEqual(log, self.log)       # should be left alone
        self.assertListEqual(result, filtered_result)

    def test_result_ordering(self):
        ordered_result = [('un2', '2012-05-01T13:36:56Z', ['result2', ]),
                          ('un1', '2013-06-01T22:28:36Z', ['result1', ]),
                          ('un2', '2013-08-04T03:26:50Z', ['result3', ])]
        # order by time
        result = copy.deepcopy(self.result)
        log = copy.deepcopy(self.log)
        newlove.modify_results(result, log, order_by_time=True)
        self.assertNotEqual(result, self.result)  # should be in-place modified
        self.assertDictEqual(log, self.log)       # should be left alone
        self.assertListEqual(result, ordered_result)

    def test_both(self):
        both_result = [('un2', '2013-08-04T03:26:50Z', ['result3', ]), ]
        # order by time AND show only new result
        result = copy.deepcopy(self.result)
        log = copy.deepcopy(self.log)
        newlove.modify_results(result, log,
                               order_by_time=True, only_show_new=True)
        self.assertNotEqual(result, self.result)  # should be in-place modified
        self.assertDictEqual(log, self.log)       # should be left alone
        self.assertListEqual(result, both_result)

from StringIO import StringIO


class TestFileFormat(unittest.TestCase):

    eg_encoded = """{
  "un1": {
    "snip1": {
      "timestamp": "2013-05-01T03:26:56Z", 
      "unread": false, 
      "love": true
    }
  }, 
  "un2": {
    "snip2": {
      "timestamp": "2013-07-01T03:46:56Z", 
      "unread": false, 
      "love": true
    }
  }
}"""
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
        self.assertMultiLineEqual(fl.read(), self.eg_encoded)
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
