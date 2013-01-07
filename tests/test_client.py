#!/usr/bin/env python
"""
Unit tests for :mod:`clans.client`.

"""

import unittest
from clans.client import PlansConnection
import subprocess
import cookielib
import pdb
from hashlib import md5
from clans.client import PlansError

TEST_URL = 'http://localhost/~tkb/phplans'
# when using a local PHP-Plans development server to test clans,
# it is VITAL to set the 'display_errors' initialization parameter to
# FALSE in Plans.php. Otherwise, PHP debug messages will be tacked on
# to the top of pages, which will confuse the clans parser.

class TestAuth(unittest.TestCase):

    def test_login(self):
        self.pc = PlansConnection(base_url = TEST_URL)
        # we should not be admitted if we give the wrong password
        self.assertFalse(self.pc.plans_login('baldwint', 'wrong_password'))
        self.assertNotEqual('baldwint', self.pc.username)
        # we should be admitted if we provide the correct one
        self.assertTrue(self.pc.plans_login('baldwint', 'password'))
        self.assertEqual('baldwint', self.pc.username)
        # once we are logged in, plans_login always returns true
        self.assertTrue(self.pc.plans_login('baldwint', ''))
        self.assertEqual('baldwint', self.pc.username)
        # even if we give a bad username
        self.assertTrue(self.pc.plans_login('foobar', ''))
        self.assertEqual('baldwint', self.pc.username)

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
        with self.assertRaises(PlansError):
            # md5 mismatch error
            result = self.pc.set_edit_text(orig, hashsum)
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

    def test_md5_existing(self):
        # this just tests md5 on the existing plan data
        plan, server_hashnum = self.pc.get_edit_text(plus_hash=True)
        python_hashnum = md5(plan.encode('utf8')).hexdigest()
        self.assertEqual(server_hashnum, python_hashnum)

    def test_unicode_editing(self):
        self.prepend_and_remove(u"Non-breaking \xa0\xa0 spaces")

class PlanChangingTestCase(LoggedInTestCase):
    """
    saves the original plan at the start of tests,
    and restores it at the end.

    """

    def setUp(self):
        super(PlanChangingTestCase, self).setUp()
        self.orig, self.hashnum = self.pc.get_edit_text(plus_hash=True)
        # tests should set hashnum as they go along
        # (but sometimes they fail)

    def tearDown(self):
        whatever, ending_hash = self.pc.get_edit_text(plus_hash=True)
        result = self.pc.set_edit_text(self.orig, ending_hash)
        self.assertTrue("Plan changed successfully" in str(result))

class TestEditing(PlanChangingTestCase):

    def editandcheck(self, phrase):
        """
        Sets plan edit-text to the phrase given,
        then opens it for editing again to make
        sure it is still there.

        """
        result = self.pc.set_edit_text(phrase, self.hashnum)
        self.assertIn("Plan changed successfully", str(result))
        plan, server_hashnum = self.pc.get_edit_text(plus_hash=True)
        self.hashnum = server_hashnum # for later cleanup
        self.assertEqual(phrase, plan)

    def test_editing(self):
        self.editandcheck(u'plain text')
        self.editandcheck("<tt># 10 11 12 -----------------</tt>")
        self.editandcheck("<b>so excited</b>")
        self.editandcheck("<hr>contact info blah blah<hr>")
        self.editandcheck(u'Non-breaking \xa0\xa0 spaces!')
        self.editandcheck(u'Newline at the end\n')

    def test_unicode(self):
        self.editandcheck(u'Non-breaking \u00a0\u00a0 spaces!')
        self.editandcheck(u'Black \u2605 star')
        self.editandcheck(u"North \u2196 west")
        self.editandcheck(u"Gauss' \u2207\u2022E = \u03c1/\u03b5\u2080 law")

    @unittest.expectedFailure
    def test_unicode_edge(self):
        #plans bug: truncating after some unicode characters
        self.editandcheck(u'Pile of \U0001f4a9!') # poo

    def test_long_plan(self):
        # on the server side, plans are MySQL mediumtext,
        # which have a max length of 16777215 chars.
        # however, the max length warning triggers at much lower values.
        phrase = 'fu' * 35000 # about 107%
        with self.assertRaises(PlansError):
            # plan too long error
            result = self.pc.set_edit_text(phrase, self.hashnum)

class TestMD5(PlanChangingTestCase):

    #@unittest.expectedFailure
    def md5check(self, phrase):
        self.pc.set_edit_text(phrase, self.hashnum)
        plan, server_hashnum = self.pc.get_edit_text(plus_hash=True)
        self.hashnum = server_hashnum # for later cleanup
        python_hashnum = md5(plan.encode('utf-8')).hexdigest()
        self.assertEqual(server_hashnum, python_hashnum)

    def test_md5(self):
        self.md5check(u'plain text')
        self.md5check("<tt># 10 11 12 -----------------</tt>")
        self.md5check("<b>so excited</b>")
        self.md5check("<hr>contact info blah blah<hr>")
        self.md5check(u'Non-breaking \xa0\xa0 spaces!')
        self.md5check(u'Newline at the end\n')

class TestPlanspeak(PlanChangingTestCase):
    """
    tests that strings entered in the edit field are
    converted properly to html

    """

    def planify(self, text, xf=None):
        self.pc.set_edit_text(text, self.hashnum)
        text_plan, self.hashnum = self.pc.get_edit_text(plus_hash=True)
        plan_header, html_plan = self.pc.read_plan(self.un)
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
        plan_header, html_plan = self.pc.read_plan(self.un)
        self.assertEqual(plan_header['username'], self.un)

class TestSearch(PlanChangingTestCase):
    """
    tests that words written or planlove given in edits turns up in
    searches right afterward

    """

    def test_giving_planlove(self):
        text = ("No one doubts that [gorp] is among "
            "the finest college outdoor programs.")
        self.pc.set_edit_text(text, self.hashnum)
        result = self.pc.search_plans('gorp', planlove=True)
        plans_with_results = [tup[0] for tup in result]
        self.assertTrue(self.un in plans_with_results)

if __name__ == "__main__":
    unittest.main()

