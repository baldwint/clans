#!/usr/bin/env python
"""
Unit tests for :mod:`clans.fmt`.

"""

import sys
if sys.version_info < (2,7):
    import unittest2 as unittest
else:
    import unittest

import clans.fmt
import sys

TEST_DATA = {
        'test_format_plan': {
                'lastupdated': 'Mon August 5th 2013, 1:22 PM',
                'lastlogin': 'Wed August 7th 2013, 3:42 AM',
                'username': 'username',
                'planname': 'clever catchphrase',
                'plan': 'this is my plan\n'
                },
        'test_br_stripping': "one<br>two<br/>three<br />four",
        'test_html_escapes': "I develop in a &quot;quick &amp; dirty&quot; &lt;style&gt;",
        'test_tag_stripping': "This is <b>bold</b> and <i>italic</i>",
        'test_link_formatting': '<a href="http://www.facebook.com/" class="onplan">my favorite website</a>',
        'test_love_formatting': '[<a href="read.php?searchname=gorp" class="planlove">GORP</a>]',
        'test_love_formatting': '[<a href="read.php?searchname=gorp" class="planlove">GORP</a>]',
        'test_psub_formatting': '<p class="sub">we all live in a yellow</p>',
        'test_hr_formatting': """I need a clean
<hr>break""",
        'test_print_list': ['one', 'two', 'three', 'four'],
        'test_print_autoread': {
                'Level 1': ['bff', 'interesting', 'funny', 'gorp'],
                'Level 2': ['roommate', 'rando'],
                'Level 3': ['meh',],
                },
        'test_print_search_results': [
                ('plan1', 1, ['snip one <b>term</b> context',]),
                ('plan2', 2, ['snip one <b>term</b> context',
                              'snip two <b>term</b> context']),
                ('plan3', 2, ['snip <b>term</b> twice <b>term</b> twice',])
                ],
        }

class TestRaw(unittest.TestCase):

    def setUp(self):
        self.fmt = clans.fmt.RawFormatter()

    # plan format test: a header, two newlines, then the plan.

    def test_format_plan(self):
        data = TEST_DATA['test_format_plan']
        text = self.fmt.format_plan(**data)
        expect = """\
Username: username
Last Updated: Mon August 5th 2013, 1:22 PM
Last Login: Wed August 7th 2013, 3:42 AM
Name: clever catchphrase

this is my plan
"""
        self.assertEqual(expect, text)

    # other tests

    def test_print_list(self):
        lst = TEST_DATA['test_print_list']
        self.fmt.print_list(lst)
        output = sys.stdout.getvalue()
        expect = u"""\
 - one
 - two
 - three
 - four
"""
        self.assertEqual(expect, output)

    def test_print_search_results(self):
        results = TEST_DATA['test_print_search_results']
        self.fmt.print_search_results(results)
        output = sys.stdout.getvalue()
        expect = u"""\
[plan1]: 1

 - snip one <b>term</b> context

[plan2]: 2

 - snip one <b>term</b> context
 - snip two <b>term</b> context

[plan3]: 2

 - snip <b>term</b> twice <b>term</b> twice

"""
        self.assertEqual(expect, output)

    def test_print_autoread(self):
        autoread = TEST_DATA['test_print_autoread']
        self.fmt.print_autoread(autoread)
        output = sys.stdout.getvalue()
        expect = u"""\
Level 1:
 - bff
 - interesting
 - funny
 - gorp

Level 2:
 - roommate
 - rando

Level 3:
 - meh

"""
        self.assertEqual(expect, output)

class TestText(TestRaw):

    def setUp(self):
        self.fmt = clans.fmt.TextFormatter()

    # filter_html tests

    def test_br_stripping(self):
        html = TEST_DATA['test_br_stripping']
        text = self.fmt.filter_html(html)
        expect = "one\ntwo\nthree\nfour"
        self.assertEqual(expect, text)

    def test_html_escapes(self):
        html = TEST_DATA['test_html_escapes']
        text = self.fmt.filter_html(html)
        expect = 'I develop in a "quick & dirty" <style>'
        self.assertEqual(expect, text)

    def test_tag_stripping(self):
        html = TEST_DATA['test_tag_stripping']
        expect = "This is bold and italic"
        text = self.fmt.filter_html(html)
        self.assertEqual(expect, text)

    def test_link_formatting(self):
        html = TEST_DATA['test_link_formatting']
        expect = '[http://www.facebook.com/|my favorite website]'
        text = self.fmt.filter_html(html)
        self.assertEqual(expect, text)

    def test_love_formatting(self):
        html = TEST_DATA['test_love_formatting']
        expect = '[GORP]'
        text = self.fmt.filter_html(html)
        self.assertEqual(expect, text)

    def test_psub_formatting(self):
        html = TEST_DATA['test_psub_formatting']
        expect = 'we all live in a yellow'
        text = self.fmt.filter_html(html)
        self.assertEqual(expect, text)

    def test_hr_formatting(self):
        html = TEST_DATA['test_hr_formatting']
        expect = """I need a clean

======================================================================
break"""
        text = self.fmt.filter_html(html)
        self.assertEqual(expect, text)

    def test_print_search_results(self):
        results = TEST_DATA['test_print_search_results']
        self.fmt.print_search_results(results)
        output = sys.stdout.getvalue()
        expect = u"""\
[plan1]: 1

 - snip one term context

[plan2]: 2

 - snip one term context
 - snip two term context

[plan3]: 2

 - snip term twice term twice

"""
        self.assertEqual(expect, output)

class TestColor(TestText):

    def setUp(self):
        self.fmt = clans.fmt.ColorFormatter()

    # plan format test

    def test_format_plan(self):
        data = TEST_DATA['test_format_plan']
        text = self.fmt.format_plan(**data)
        expect = """\
%sUsername%s: username
%sLast Updated%s: Mon August 5th 2013, 1:22 PM
%sLast Login%s: Wed August 7th 2013, 3:42 AM
%sName%s: clever catchphrase

this is my plan
""" % (('\x1b[1m', '\x1b[22m') * 4)
        self.assertEqual(expect, text)


    # filter_html tests

    def test_tag_stripping(self):
        html = TEST_DATA['test_tag_stripping']
        expect = "This is \x1b[1mbold\x1b[22m and \x1b[2mitalic\x1b[22m"
        # italic is actually 'dim', bold 'bright'
        text = self.fmt.filter_html(html)
        self.assertEqual(expect, text)

    def test_link_formatting(self):
        html = TEST_DATA['test_link_formatting']
        expect = '[\x1b[32mhttp://www.facebook.com/\x1b[39m|\x1b[35mmy favorite website\x1b[39m]'
        # green for the link, magenta for the link text
        text = self.fmt.filter_html(html)
        self.assertEqual(expect, text)

    def test_love_formatting(self):
        html = TEST_DATA['test_love_formatting']
        expect = '[\x1b[1m\x1b[34mGORP\x1b[22m\x1b[39m]' # blue and bold
        text = self.fmt.filter_html(html)
        self.assertEqual(expect, text)

    def test_hr_formatting(self):
        html = TEST_DATA['test_hr_formatting']
        expect = """I need a clean

\x1b[31m======================================================================\x1b[39m
break"""
        # red
        text = self.fmt.filter_html(html)
        self.assertEqual(expect, text)

    # other tests

    def test_print_search_results(self):
        results = TEST_DATA['test_print_search_results']
        self.fmt.print_search_results(results)
        output = sys.stdout.getvalue()
        expect = u"""\
[plan1]: 1

 - snip one %sterm%s context

[plan2]: 2

 - snip one %sterm%s context
 - snip two %sterm%s context

[plan3]: 2

 - snip %sterm%s twice %sterm%s twice

""" % (('\x1b[1m', '\x1b[22m') * 5)
        self.assertEqual(expect, output)

if __name__ == "__main__":
    unittest.main(buffer=True)

