#!/usr/bin/env python
"""
Unit tests for :mod:`clans.ui`.

"""


import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

if sys.version_info >= (3, 3):
    import unittest.mock as mock
else:
    import mock

import clans.ui
import tempfile
import os
import shutil


class SubprocessMocked(unittest.TestCase):

    def setUp(self):
        # monkey patch subprocess with a mock
        # this excludes external processes from the SUT
        self.real_subprocess = clans.ui.subprocess
        clans.ui.subprocess = mock.Mock()

    def tearDown(self):
        # fix monkey patch
        clans.ui.subprocess = self.real_subprocess


class TestExternalEditor(SubprocessMocked):

    def test_specify_editor(self):
        orig = """hi there"""
        edited = clans.ui.external_editor(orig, 'foo')
        args, kwargs = clans.ui.subprocess.call.call_args
        editor_used, tmpfile_at = args[0]
        self.assertEqual(editor_used, 'foo')
        self.assertEqual(edited, orig)

    def test_edit_works(self):
        orig = """hi there"""

        def insult_user(arglist):
            editor_used, tmpfile = arglist
            with open(tmpfile, 'a') as fl:
                fl.write(" loser")
        clans.ui.subprocess.call.side_effect = insult_user
        edited = clans.ui.external_editor(orig, 'foo')
        self.assertEqual(edited, "hi there loser")


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
