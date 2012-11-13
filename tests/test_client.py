#!/usr/bin/env python
"""
Unit tests for :mod:`clans.client`.

"""

import unittest
from clans.client import PlansConnection
import subprocess
import cookielib
import pdb

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
        self.un = 'baldwint'
        self.pc = PlansConnection(base_url = TEST_URL)
        self.pc.plans_login(self.un, 'password')

class TestEdit(LoggedInTestCase):

    def prepend_and_remove(self, hello):
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

    def test_plaintext_editing(self):
        #prepend 'hello world' to plan text
        self.prepend_and_remove('hello world!')

    def test_html_editing(self):
        #make sure html is picked up
        self.prepend_and_remove("<tt># 10 11 12 -----------------</tt>")
        self.prepend_and_remove("<b>so excited</b>")
        self.prepend_and_remove("<hr>contact info blah blah<hr>")

    def test_md5(self):
        #TODO
        pass

class PlanChangingTestCase(LoggedInTestCase):
    """
    saves the original plan at the start of tests,
    and restores it at the end.

    """

    def setUp(self):
        super(PlanChangingTestCase, self).setUp()
        self.orig, self.hashnum = self.pc.get_edit_text(plus_hash=True)
        # tests should set hashnum as they go along

    def tearDown(self):
        result = self.pc.set_edit_text(self.orig, self.hashnum)
        self.assertTrue("Plan changed successfully" in str(result))


class TestPlanspeak(PlanChangingTestCase):
    """
    tests that strings entered in the edit field are
    converted properly to html

    """

    def planify(self, text, xf=None):
        self.pc.set_edit_text(text, self.hashnum)
        text_plan, self.hashnum = self.pc.get_edit_text(plus_hash=True)
        html_plan = self.pc.read_plan(self.un)
        return text_plan, html_plan

    def test_text(self):
        orig = 'hello world!'
        text, html = self.planify(orig)
        self.assertEqual(orig, text)
        self.assertEqual(orig, html)

    def test_multiline(self):
        orig = 'hello\nworld'
        text, html = self.planify(orig)
        self.assertEqual(orig, text)
        self.assertEqual('hello<br />world', html)
        # BeautifulSoup problem, should be:
        #self.assertEqual('hello<br>world', html)

    def test_allowed_html(self):
        examples = ['<b>hello world</b>',
                    '<i>hello world</i>',
                    '<tt>hello world</tt>',
                   ]
        for orig in examples:
            text, html = self.planify(orig)
            self.assertEqual(orig, text)
            self.assertEqual(orig, html)

    def test_underline(self):
        orig = '<u>hello world</u>'
        expect = '<span class="underline">hello world</span><!--u-->'
        # Plans weirdness; should the trailing comment be canonical?
        text, html = self.planify(orig)
        self.assertEqual(orig, text)
        self.assertEqual(expect, html)

    def test_strike(self):
        orig = '<strike>hello world</strike>'
        expect = '<span class="strike">hello world</span><!--strike-->'
        # Plans weirdness; should the trailing comment be canonical?
        text, html = self.planify(orig)
        self.assertEqual(orig, text)
        self.assertEqual(expect, html)

    @unittest.expectedFailure
    def test_pre(self):
        # my code problem (multiple <p class="sub">s)
        orig = '<pre>hello world</pre>'
        text, html = self.planify(orig)
        self.assertEqual(orig, text)
        self.assertEqual(orig, html)

    def test_horiz_rule(self):
        orig = 'hello<hr>world'
        text, html = self.planify(orig)
        self.assertEqual(orig, text)
        self.assertEqual('hello<hr />world', html)
        # BeautifulSoup problem, should be:
        #self.assertEqual('hello<hr>world', html)

class TestRead(LoggedInTestCase):

    def test_reading(self):
        #pdb.set_trace()
        html_plan = self.pc.read_plan(self.un)

if __name__ == "__main__":
    unittest.main()

