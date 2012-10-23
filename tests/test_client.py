#!/usr/bin/env python
"""
Unit tests for :mod:`clans.client`.

"""

import unittest
from clans.client import PlansConnection
import subprocess
import cookielib

TEST_URL = 'http://localhost/~tkb/plans/plans2012'

class TestAuth(unittest.TestCase):

    def test_login(self):
        self.pc = PlansConnection(base_url = TEST_URL)
        # we should not be admitted if we give the wrong password
        self.assertFalse(self.pc.plans_login('baldwint', 'wrong_password'))
        # we should be admitted if we provide the correct one
        self.assertTrue(self.pc.plans_login('baldwint', 'password'))
        # once we are logged in, plans_login always returns true
        self.assertTrue(self.pc.plans_login('baldwint', ''))

    def test_cookie(self):
        oreo = cookielib.LWPCookieJar()
        # log in to create a good cookie
        pc = PlansConnection(oreo, base_url = TEST_URL)
        pc.plans_login('baldwint', 'password')
        # end session
        del pc
        # but we should remain logged in if we provide the cookie
        pc = PlansConnection(oreo, base_url = TEST_URL)
        self.assertTrue(pc.plans_login('baldwint', ''))

class LoggedInTestCase(unittest.TestCase):

    def setUp(self):
        self.pc = PlansConnection(base_url = TEST_URL)
        self.pc.plans_login('baldwint', 'password')

class TestEdit(LoggedInTestCase):

    def test_editing(self):
        #prepend 'hello world' to plan text
        hello = 'hello world!'
        orig, hashsum = self.pc.get_edit_text(plus_hash=True)
        result = self.pc.set_edit_text(hello + orig, hashsum)
        self.assertTrue("Plan changed successfully" in str(result))
        # check that plan was actually edited
        new, new_hashsum = self.pc.get_edit_text(plus_hash=True)
        self.assertEqual(new[:len(hello)], hello)
        # try to change back, with wrong hashsum
        result = self.pc.set_edit_text(orig, hashsum)
        self.assertFalse("Plan changed successfully" in str(result))
        # edit again, undoing
        result = self.pc.set_edit_text(orig, new_hashsum)
        self.assertTrue("Plan changed successfully" in str(result))

    def test_md5(self):
        #TODO
        pass

if __name__ == "__main__":
    unittest.main()

