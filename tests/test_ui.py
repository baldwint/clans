#!/usr/bin/env python
"""
Unit tests for :mod:`clans.ui`.

"""


import sys
if sys.version_info < (2,7):
    import unittest2 as unittest
else:
    import unittest

import clans.ui
import tempfile
import sys
import os
import shutil

class WithClansdir(unittest.TestCase):

    def setUp(self):
        # make a fake clans directory
        self.clansdir = tempfile.mkdtemp(suffix='.clansprofile')

    def tearDown(self):
        # remove temporary directory
        shutil.rmtree(self.clansdir)

class TestSession(WithClansdir):

    def test_empty_session(self):
        # an empty config directory
        cs = clans.ui.ClansSession(self.clansdir)

        # the config file should be called clans.cfg
        self.assertEqual(cs.config_loc,
                         os.path.join(self.clansdir, 'clans.cfg'))

        # test that sensible defaults were established
        default_url = cs.config.get('login', 'url')
        self.assertEqual(default_url, 'http://www.grinnellplans.com')

    def test_configured_session(self):
        # write to the config file
        clans_cfg = os.path.join(self.clansdir, 'clans.cfg')
        with open(clans_cfg, 'w') as fl:
            fl.write("[login]\nusername=baldwint")

        cs = clans.ui.ClansSession(self.clansdir)

        # test that these configured values were picked up
        username = cs.config.get('login', 'username')
        self.assertEqual(username, 'baldwint')


if __name__ == "__main__":
    unittest.main()

