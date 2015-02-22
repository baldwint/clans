#!/usr/bin/env python
"""
Integration tests for :mod:`clans.scraper`, and the parts of
GrinnellPlans that this module provides a scrAPI for.

"""

import sys
from datetime import datetime
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

if sys.version_info >= (3,3):
    from http.cookiejar import LWPCookieJar
elif sys.version_info < (3,):
    from cookielib import LWPCookieJar

import pymysql

from clans.scraper import PlansConnection
from clans.scraper import PlansError
from clans.util import plans_md5

TEST_SERVER = {'base_url':  'http://localhost/~tkb/phplans',
               'server_tz': 'US/Pacific'}
# when using a local PHP-Plans development server to test clans,
# it is VITAL to set the 'display_errors' initialization parameter to
# FALSE in Plans.php. Otherwise, PHP debug messages will be tacked on
# to the top of pages, which will confuse the clans parser.

# For some tests, a few username/password pairs valid on the testing
# server are needed
USERNAME = 'baldwint'
PASSWORD = 'password'

USERNAME_2 = 'gorp'      # for now, this user is required to have
PASSWORD_2 = 'password'  # USERNAME_1 on her autoread with a level of 1.
                         # Future tests should set this

NONEX = 'fobar'        # a nonexistent user

# certain tests will access the database directly.
TEST_DB = {'host':   'localhost',
           'db':     'plans',
           'user':   'plans_dev',
           'passwd': 'plans_dev_password'}


class TestAuth(unittest.TestCase):

    def test_login(self):
        self.pc = PlansConnection(**TEST_SERVER)
        # we should not be admitted if we give the wrong password
        self.assertFalse(self.pc.plans_login(USERNAME, 'wrong_password'))
        self.assertNotEqual(USERNAME, self.pc.username)
        # we should be admitted if we provide the correct one
        self.assertTrue(self.pc.plans_login(USERNAME, PASSWORD))
        self.assertEqual(USERNAME, self.pc.username)
        # once we are logged in, plans_login always returns true
        self.assertTrue(self.pc.plans_login(USERNAME, ''))
        self.assertEqual(USERNAME, self.pc.username)
        # even if we give a bad username
        self.assertTrue(self.pc.plans_login(NONEX, ''))
        self.assertEqual(USERNAME, self.pc.username)

    def test_cookie(self):
        oreo = LWPCookieJar()
        # log in to create a good cookie
        pc = PlansConnection(oreo, **TEST_SERVER)
        pc.plans_login(USERNAME, PASSWORD)
        # end session
        del pc
        # but we should remain logged in if we provide the cookie
        pc = PlansConnection(oreo, **TEST_SERVER)
        self.assertTrue(pc.plans_login(USERNAME, ''))


class LoggedInTestCase(unittest.TestCase):

    def setUp(self):
        self.un = USERNAME
        self.pc = PlansConnection(**TEST_SERVER)
        self.pc.plans_login(self.un, PASSWORD)


class TestEdit(LoggedInTestCase):

    def prepend_and_remove(self, hello):
        orig, hashsum = self.pc.get_edit_text()
        result = self.pc.set_edit_text(hello + orig, hashsum)
        self.assertTrue("Plan changed successfully" in str(result))
        # check that plan was actually edited
        new, new_hashsum = self.pc.get_edit_text()
        self.assertEqual(new[:len(hello)], hello)
        # try to change back, with wrong hashsum
        with self.assertRaises(PlansError) as cm:
            # md5 mismatch error
            result = self.pc.set_edit_text(orig, hashsum)
        self.assertIn('Your plan was edited from another instance '
                      'of the edit page', repr(cm.exception))
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
        plan, server_hashnum = self.pc.get_edit_text()
        python_hashnum = plans_md5(plan)
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
        self.orig, self.hashnum = self.pc.get_edit_text()
        # tests should set hashnum as they go along
        # (but sometimes they fail)

    def tearDown(self):
        whatever, ending_hash = self.pc.get_edit_text()
        result = self.pc.set_edit_text(self.orig, ending_hash)
        self.assertTrue("Plan changed successfully" in str(result))


class TestEditing(PlanChangingTestCase):

    def editandcheck(self, phrase, expect=None):
        """
        Sets plan edit-text to the phrase given,
        then opens it for editing again to make
        sure it is still there.

        If we expect the edit-text to have been
        changed (pretty much only [date] does this),
        set `expect` to what we expect to find.

        """
        if expect is None:
            expect = phrase
        result = self.pc.set_edit_text(phrase, self.hashnum)
        self.assertIn("Plan changed successfully", str(result))
        plan, server_hashnum = self.pc.get_edit_text()
        self.hashnum = server_hashnum  # for later cleanup
        self.assertEqual(expect, plan)

    def test_editing(self):
        self.editandcheck(u'plain text')
        self.editandcheck("<tt># 10 11 12 -----------------</tt>")
        self.editandcheck("<b>so excited</b>")
        self.editandcheck("<hr>contact info blah blah<hr>")
        self.editandcheck(u'Non-breaking \xa0\xa0 spaces!')

    def test_newlines(self):
        # We should coerce to CRLF line endings, per the spec:
        # http://www.w3.org/TR/REC-html40/interact/forms.html#h-17.13.4
        # The Plans server does no conversion of newlines, but
        # browsers always use CRLF when submitting the contents of a
        # <textarea> tag. This makes it the de facto line ending
        # standard for plans.
        self.editandcheck(u'Newline at the end\n',
                expect=u'Newline at the end\r\n')
        self.editandcheck(u'Newline in\nthe middle',
                expect=u'Newline in\r\nthe middle')
        self.editandcheck(u'Newline at the end\r\n')
        self.editandcheck(u'Newline in\r\nthe middle')

    def test_leading_newline(self):
        # https://code.google.com/p/grinnellplans/issues/detail?id=260
        self.editandcheck(u'\r\nNewline at the beginning')

    def test_bad_html(self):
        # BS3 screws things up by correcting bad HTML in a textarea
        # field (even though it ignores HTML in there)
        self.editandcheck(u'</b')               # fails
        self.editandcheck(u'</b> &waffles')     # fails
        self.editandcheck(u'chicken &waffles')  # succeeds for some reason

    def test_ampersands(self):
        # BS3 would choke on ampersands in URLs, seemingly only
        # when they were preceded by another ampersand
        self.editandcheck(u'<b>Q&A</b>: Contact '
                u'[http://www.website.com/page?=contact&query=string|me]')

    def test_unicode(self):
        self.editandcheck(u'Non-breaking \u00a0\u00a0 spaces!')
        self.editandcheck(u'Black \u2605 star')
        self.editandcheck(u"North \u2196 west")
        self.editandcheck(u"Gauss' \u2207\u2022E = \u03c1/\u03b5\u2080 law")

    @unittest.expectedFailure
    def test_unicode_edge(self):
        #plans bug: truncating after some unicode characters
        self.editandcheck(u'Pile of \U0001f4a9!')  # poo

    @unittest.expectedFailure
    @unittest.skip
    def test_long_plan(self):
        # on the server side, plans are MySQL mediumtext,
        # which have a max length of 16777215 chars.
        # however, the max length warning triggers at much lower values.
        phrase = 'fu' * 35000  # about 107%
        with self.assertRaises(PlansError) as cm:
            # plan too long error
            self.pc.set_edit_text(phrase, self.hashnum)
        self.assertIn('plan is too long', repr(cm.exception))


class TestMD5(PlanChangingTestCase):

    #@unittest.expectedFailure
    def md5check(self, phrase):
        self.pc.set_edit_text(phrase, self.hashnum)
        plan, server_hashnum = self.pc.get_edit_text()
        self.hashnum = server_hashnum  # for later cleanup
        python_hashnum = plans_md5(plan)
        self.assertEqual(server_hashnum, python_hashnum)

    def test_md5(self):
        self.md5check(u'plain text')
        self.md5check("<tt># 10 11 12 -----------------</tt>")
        self.md5check("<b>so excited</b>")
        self.md5check("<hr>contact info blah blah<hr>")
        self.md5check(u'Non-breaking \xa0\xa0 spaces!')
        self.md5check(u'Newline at the end\r\n')


def psub(text):
    """
    Wraps some text in an annoying <p class="sub"> tag.

    """
    return '<p class="sub">%s</p>' % text


class TestPlanspeak(PlanChangingTestCase):
    """
    tests that strings entered in the edit field are
    converted properly to html

    """

    def planify(self, text, xf=None):
        self.pc.set_edit_text(text, self.hashnum)
        text_plan, self.hashnum = self.pc.get_edit_text()
        plan_header, html_plan = self.pc.read_plan(self.un)
        return text_plan, html_plan

    def test_text(self):
        orig = 'hello world!'
        text, html = self.planify(orig)
        self.assertEqual(orig, text)
        self.assertEqual(psub(orig), html)

    def test_multiline(self):
        orig = 'hello\r\nworld'
        text, html = self.planify(orig)
        self.assertEqual(orig, text)
        self.assertEqual(psub('hello\n<br>world'), html)
        # In reality, plans returns 'hello\r<br>world',
        # but that's weird, and our parser converts to '\n'

    def test_unicode(self):
        orig = u"Non-breaking \xa0\xa0 spaces"
        text, html = self.planify(orig)
        self.assertEqual(orig, text)
        self.assertEqual(psub(orig), html)

    def test_allowed_html(self):
        examples = ['<b>hello world</b>',
                    '<i>hello world</i>',
                    '<tt>hello world</tt>',
                    ]
        for orig in examples:
            text, html = self.planify(orig)
            self.assertEqual(orig, text)
            self.assertEqual(psub(orig), html)

    def test_underline(self):
        orig = '<u>hello world</u>'
        expect = '<span class="underline">hello world</span><!--u-->'
        # Plans weirdness; should the trailing comment be canonical?
        text, html = self.planify(orig)
        self.assertEqual(orig, text)
        self.assertEqual(psub(expect), html)

    def test_strike(self):
        orig = '<strike>hello world</strike>'
        expect = '<span class="strike">hello world</span><!--strike-->'
        # Plans weirdness; should the trailing comment be canonical?
        text, html = self.planify(orig)
        self.assertEqual(orig, text)
        self.assertEqual(psub(expect), html)

    @unittest.expectedFailure
    def test_pre(self):
        orig = '<pre>hello world</pre>'
        expect = psub(orig)
        # real plans doesn't do this - it applies class="sub" directly
        # to the pre tag. Additionally, if the plan starts (or ends)
        # with the pre tag, it puts an empty <p class="sub">
        # before (after) the pre tag. No idea why that is done,
        # possible plans bug
        text, html = self.planify(orig)
        self.assertEqual(orig, text)
        self.assertEqual(expect, html)

    def test_horiz_rule(self):
        orig = 'hello<hr>world'
        expect = psub('hello') + '<hr>' + psub('world')
        text, html = self.planify(orig)
        self.assertEqual(orig, text)
        self.assertEqual(expect, html)

    def test_html_escape(self):
        orig = 'angle>bracket'
        expect = psub('angle&gt;bracket')
        text, html = self.planify(orig)
        self.assertEqual(orig, text)
        self.assertEqual(expect, html)

    def test_quote(self):
        orig = 'double"quote'
        expect = psub('double&quot;quote')
        text, html = self.planify(orig)
        self.assertEqual(orig, text)
        self.assertEqual(expect, html)

    def test_planlove(self):
        orig = "May the [gorp] be with you."
        expect = ('May the [<a href="read.php?searchname=gorp"'
                  ' class="planlove">gorp</a>] be with you.')
        text, html = self.planify(orig)
        self.assertEqual(orig, text)
        self.assertEqual(psub(expect), html)

    def test_link(self):
        orig = "Where the hell is [http://grinnell.edu/|Grinnell]?"
        expect = ('Where the hell is <a href="http://grinnell.edu/"'
                  ' class="onplan">Grinnell</a>?')
        text, html = self.planify(orig)
        self.assertEqual(orig, text)
        self.assertEqual(psub(expect), html)

    def test_other_link(self):
        orig = "Where the hell is [http://grinnell.edu/]?"
        expect = ('Where the hell is <a href="http://grinnell.edu/"'
                  ' class="onplan">http://grinnell.edu/</a>?')
        text, html = self.planify(orig)
        self.assertEqual(orig, text)
        self.assertEqual(psub(expect), html)


class DbTestCase(LoggedInTestCase):

    def setUp(self):
        super(DbTestCase, self).setUp()
        self.db = pymysql.connect(**TEST_DB)
        self.c = self.db.cursor()

    def find_userid(self, un=None):
        if un is None:
            un = self.un
        self.c.execute("select userid from accounts "
                       "where username=%s", (un,))
        userid, = self.c.fetchone()
        return userid


class TestRead(DbTestCase):
    """
    The read_plan method should return plan text
    as it is formatted in the database

    One exception to this rule: plan html uses CR line endings,
    and clans converts these to LF endings

    """

    # this might fail because beautifulsoup doesn't preserve syntactically
    # irrelevant details of html. I've compensated for the obvious
    # ones (<br> vs <br />, etc.) but more remain to be found #TODO
    def test_reading(self):
        # TODO this currently just tests whatever's in the db at the
        # time. we should parametrize around input data
        userid = self.find_userid()
        self.c.execute("select plan from plans "
                       "where user_id=%s", (userid,))
        plan_in_db, = self.c.fetchone()
        plan_header, html_plan = self.pc.read_plan(self.un)
        self.assertEqual(plan_header['username'], self.un)
        self.assertEqual(html_plan, plan_in_db.replace('\r', '\n'))

    def test_nonexistent(self):
        # this test doesn't need db but whatever
        with self.assertRaises(PlansError) as cm:
            # nonexistent plan
            plan_header, html_plan = self.pc.read_plan(NONEX)
        self.assertIn('No such user', repr(cm.exception))


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

    def test_search_unicode(self):
        term = u"bigPileof"
        text = u"bigPileof \U0001f4a9"
        expect = u"<b>bigPileof</b> \U0001f4a9"
        self.pc.set_edit_text(text, self.hashnum)
        result = self.pc.search_plans(term)
        plans_with_results = [tup[0] for tup in result]
        self.assertTrue(self.un in plans_with_results)
        for un, n, snippets in result:
            if un == self.un:
                snippets_as_str = u''.join(snippets)
                self.assertIn(expect, snippets_as_str)

    def test_search_newline(self):
        term = u"uniqueSearchTerm"
        text = u"uniqueSearchTerm with\nnewlines"
        expect = u"<b>uniqueSearchTerm</b> with\n<br>newlines"
        self.pc.set_edit_text(text, self.hashnum)
        result = self.pc.search_plans(term)
        plans_with_results = [tup[0] for tup in result]
        self.assertTrue(self.un in plans_with_results)
        for un, n, snippets in result:
            if un == self.un:
                snippets_as_str = u''.join(snippets)
                self.assertIn(expect, snippets_as_str)

    def test_search_htmlescape(self):
        term = u"uniqueSearchTerm"
        text = u"uniqueSearchTerm with angle>bracket"
        expect = u"<b>uniqueSearchTerm</b> with angle&gt;bracket"
        self.pc.set_edit_text(text, self.hashnum)
        result = self.pc.search_plans(term)
        plans_with_results = [tup[0] for tup in result]
        self.assertTrue(self.un in plans_with_results)
        for un, n, snippets in result:
            if un == self.un:
                snippets_as_str = u''.join(snippets)
                self.assertIn(expect, snippets_as_str)

    def test_search_quote(self):
        term = u"uniqueSearchTerm"
        text = u"uniqueSearchTerm with double\"quote"
        expect = u"<b>uniqueSearchTerm</b> with double&quot;quote"
        self.pc.set_edit_text(text, self.hashnum)
        result = self.pc.search_plans(term)
        plans_with_results = [tup[0] for tup in result]
        self.assertTrue(self.un in plans_with_results)
        for un, n, snippets in result:
            if un == self.un:
                snippets_as_str = u''.join(snippets)
                self.assertIn(expect, snippets_as_str)

    def test_no_results(self):
        term = u"uniqueSearchTermThatDoesNotExist"
        result = self.pc.search_plans(term)
        self.assertEqual(result, [])


class TestPlanwatch(PlanChangingTestCase):
    """
    test plan watch etc.

    """

    def test_planwatch(self):
        text = "doesn't matter"
        self.pc.set_edit_text(text, self.hashnum)
        result = self.pc.planwatch(hours=2)
        uns = [un for un,timestamp in result]
        self.assertTrue(self.un in uns)


class TestTimestamp(PlanChangingTestCase):
    """
    Test datetime parsing of lastupdated.

    """

    def test_timestamp(self):
        text = "doesn't matter"
        gunshot = datetime.utcnow()
        self.pc.set_edit_text(text, self.hashnum)
        header,_ = self.pc.read_plan(self.un)
        delta = header['lastupdated'] - gunshot
        # displayed dates often round to the minute, so the diff
        # should be less than 60 seconds. Use 100 for good measure
        elapsed = (delta.seconds + delta.days * 24 * 3600)
        self.assertLessEqual(
            abs(elapsed), 100,
            "Timestamps mismatched, what is server's timezone?")


class TestAutofinger(PlanChangingTestCase):
    """
    test autofinger adding etc.

    """

    def setUp(self):
        super(TestAutofinger, self).setUp()
        # we need a second user (don't edit this one's plan)
        self.un2 = USERNAME_2
        self.pc2 = PlansConnection(**TEST_SERVER)
        self.pc2.plans_login(self.un2, PASSWORD_2)

    def test_get_autofinger(self):
        self.pc2.read_plan(self.un)  # clear read state
        autofinger = self.pc2.get_autofinger()
        unread = [un for level in autofinger.values() for un in level]
        self.assertNotIn(self.un, unread)  # read state should be empty
        # now update user 1's plan
        orig, hashsum = self.pc.get_edit_text()
        self.pc.set_edit_text("hello world", hashsum)
        # now user 1 should be on user 2's autofinger (level 1)
        autofinger = self.pc2.get_autofinger()
        self.assertIn(self.un, autofinger['Level 1'])
        # now read the plan and it should be marked as read
        self.pc2.read_plan(self.un)
        autofinger = self.pc2.get_autofinger()
        self.assertNotIn(self.un, autofinger['Level 1'])

#    @unittest.skip # aspirational
#    def test_autofinger_level(self):
#        orig_level = self.pc2.get_autofinger_level(self.un)
#        # put them on level 3, using integer
#        self.pc2.set_autofinger_level(self.un, 3)
#        level_now = self.pc2.get_autofinger_level(self.un)
#        self.assertEqual("Level 3", level_now)
#        # put them on level 1, using string
#        self.pc2.set_autofinger_level(self.un, "Level 1")
#        level_now = self.pc2.get_autofinger_level(self.un)
#        self.assertEqual("Level 1", level_now)
#        # remove them entirely
#        self.pc2.set_autofinger_level(self.un, None)
#        level_now = self.pc2.get_autofinger_level(self.un)
#        self.assertIsNone(level_now)
#        # now updates will not show up on any level
#        orig, hashsum = self.pc.get_edit_text()
#        result = self.pc.set_edit_text("no love", hashsum)
#        autofinger = self.pc2.get_autofinger()
#        unread = [un for level in autofinger.values() for un in level]
#        self.assertNotIn(self.un, unread)
#        # restore previous state
#        self.pc2.set_autofinger_level(self.un, orig_level)

if __name__ == "__main__":
    unittest.main()
