#!/usr/bin/env python
"""
Unit tests for :mod:`clans.fmt`.

"""

import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import clans.fmt

from io import StringIO
from datetime import datetime

TEST_DATA = {
    'test_format_date': datetime(2015, 1, 28, 23, 46),
    'test_format_date_dst': datetime(2012, 4, 12, 20, 6),
    'test_format_plan': {
        'lastupdated': datetime(2013, 8, 5, 13, 22),
        'lastlogin': datetime(2013, 8, 7, 3, 42),
        'username': 'username',
        'planname': 'clever catchphrase',
        'plan': 'this is my plan\n'
        },
    'test_br_stripping': "one<br>two<br/>three<br />four",
    'test_crlf_stripping': "one\ntwo\rthree\r\nfour",
    'test_html_escapes': ("I develop in a &quot;quick &amp; dirty&quot; "
                          "&lt;style&gt;"),
    'test_tag_stripping': "This is <b>bold</b> and <i>italic</i>",
    'test_underline':  ('This is <span '
                         'class="underline">underlined</span><!--u-->'),
    'test_link_formatting': ('<a href="http://www.facebook.com/" '
                             'class="onplan">my favorite website</a>'),
    'test_love_formatting': ('[<a href="read.php?searchname=gorp" '
                             'class="planlove">GORP</a>]'),
    'test_love_formatting': ('[<a href="read.php?searchname=gorp" '
                             'class="planlove">GORP</a>]'),
    'test_psub_formatting': '<p class="sub">we all live in a yellow</p>',
    'test_hr_formatting': """I need a clean
<hr>break""",
    'test_print_list': ['one', 'two', 'three', 'four'],
    'test_print_autoread': {
        'Level 1': ['bff', 'interesting', 'funny', 'gorp'],
        'Level 2': ['roommate', 'rando'],
        'Level 3': ['meh', ],
        },
    'test_print_search_results': [
        ('plan1', 1, ['snip one <b>term</b> context', ]),
        ('plan2', 2, ['snip one <b>term</b> context',
                      'snip two <b>term</b> context']),
        ('plan3', 2, ['snip <b>term</b> twice <b>term</b> twice', ])
        ],
    }


class FakeStdout(unittest.TestCase):

    def setUp(self):
        self.real_stdout = sys.stdout
        sys.stdout = StringIO()

    def tearDown(self):
        sys.stdout = self.real_stdout

class TestRaw(FakeStdout):

    def setUp(self):
        FakeStdout.setUp(self)
        self.fmt = clans.fmt.RawFormatter()

    def test_format_date(self):
        date = TEST_DATA['test_format_date']
        text = self.fmt.format_date(date)
        expect = '2015-01-28 23:46:00' # no assumed timezone
        self.assertEqual(expect, text)

    # plan format test: a header, two newlines, then the plan.

    def test_format_plan(self):
        data = TEST_DATA['test_format_plan']
        text = self.fmt.format_plan(**data)
        expect = """\
Username: username
Last Updated: 2013-08-05 13:22:00
Last Login: 2013-08-07 03:42:00
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
one
two
three
four
"""
        self.assertEqual(expect, output)

    def test_print_bulleted_list(self):
        lst = TEST_DATA['test_print_list']
        self.fmt.print_list(lst, bullets=True)
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
bff
interesting
funny
gorp

Level 2:
roommate
rando

Level 3:
meh

"""
        self.assertEqual(expect, output)


class TestJSON(FakeStdout):

    def setUp(self):
        FakeStdout.setUp(self)
        self.fmt = clans.fmt.JSONFormatter()

    def test_format_date(self):
        date = TEST_DATA['test_format_date']
        text = self.fmt.format_date(date)
        expect = '2015-01-28T23:46:00Z' # ISO 8601, assume UTC
        self.assertEqual(expect, text)

    def test_format_plan(self):
        data = TEST_DATA['test_format_plan']
        text = self.fmt.format_plan(**data)
        expect = """\
{
  "username": "username",
  "lastupdated": "2013-08-05T13:22:00Z",
  "lastlogin": "2013-08-07T03:42:00Z",
  "planname": "clever catchphrase",
  "plan": "this is my plan\\n"
}"""
        self.assertEqual(expect, text)

    # other tests

    def test_print_list(self):
        lst = TEST_DATA['test_print_list']
        self.fmt.print_list(lst)
        output = sys.stdout.getvalue()
        expect = u"""\
[
  "one",
  "two",
  "three",
  "four"
]
"""
        self.assertEqual(expect, output)

    def test_print_search_results(self):
        results = TEST_DATA['test_print_search_results']
        self.fmt.print_search_results(results)
        output = sys.stdout.getvalue()
        expect = u"""\
[
  [
    "plan1",
    1,
    [
      "snip one <b>term</b> context"
    ]
  ],
  [
    "plan2",
    2,
    [
      "snip one <b>term</b> context",
      "snip two <b>term</b> context"
    ]
  ],
  [
    "plan3",
    2,
    [
      "snip <b>term</b> twice <b>term</b> twice"
    ]
  ]
]
"""
        self.assertEqual(expect, output)

    def test_print_autoread(self):
        autoread = TEST_DATA['test_print_autoread']
        self.fmt.print_autoread(autoread)
        output = sys.stdout.getvalue()
        expect = u"""\
{
  "Level 1": [
    "bff",
    "interesting",
    "funny",
    "gorp"
  ],
  "Level 2": [
    "roommate",
    "rando"
  ],
  "Level 3": [
    "meh"
  ]
}
"""
        self.assertEqual(expect, output)


class TestText(TestRaw):

    def setUp(self):
        FakeStdout.setUp(self)
        self.fmt = clans.fmt.TextFormatter()

    def test_format_date(self):
        date = TEST_DATA['test_format_date']
        text = self.fmt.format_date(date)
        expect = 'Wed January 28 2015, 5:46 PM'
        # timezone should have been converted to central.
        # same format as plans web (but w/o ordinal suffix)
        self.assertEqual(expect, text)

    def test_format_date_dst(self):
        date = TEST_DATA['test_format_date_dst']
        text = self.fmt.format_date(date)
        expect = 'Thu April 12 2012, 3:06 PM'
        self.assertEqual(expect, text)

    @unittest.expectedFailure
    def test_format_plan(self):
        data = TEST_DATA['test_format_plan']
        text = self.fmt.format_plan(**data)
        expect = """\
Username: username
Last Updated: Mon August 5 2013, 1:22 PM
Last Login: Wed August 7 2013, 3:42 AM
Name: clever catchphrase

this is my plan
"""
        self.assertEqual(expect, text)

    # filter_html tests

    def test_br_stripping(self):
        html = TEST_DATA['test_br_stripping']
        text = self.fmt.filter_html(html)
        expect = "one\ntwo\nthree\nfour"
        self.assertEqual(expect, text)

    def test_crlf_stripping(self):
        html = TEST_DATA['test_crlf_stripping']
        text = self.fmt.filter_html(html)
        expect = "onetwothreefour"
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

    def test_underline(self):
        html = TEST_DATA['test_underline']
        expect = 'This is underlined'
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

    def test_print_list_in_columns(self):
        lst = TEST_DATA['test_print_list']
        self.fmt.print_list(lst, columns=True)
        output = sys.stdout.getvalue()
        expect = u"""\
one    two    three  four
"""
        self.assertEqual(expect, output)

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
        FakeStdout.setUp(self)
        self.fmt = clans.fmt.ColorFormatter()

    # plan format test

    @unittest.expectedFailure
    def test_format_plan(self):
        data = TEST_DATA['test_format_plan']
        text = self.fmt.format_plan(**data)
        expect = """\
%sUsername%s: username
%sLast Updated%s: Mon August 5 2013, 1:22 PM
%sLast Login%s: Wed August 7 2013, 3:42 AM
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

    def test_underline(self):
        html = TEST_DATA['test_underline']
        expect = 'This is \x1b[4munderlined\x1b[0m'
        text = self.fmt.filter_html(html)
        self.assertEqual(expect, text)

    def test_link_formatting(self):
        html = TEST_DATA['test_link_formatting']
        expect = ('[\x1b[32mhttp://www.facebook.com/\x1b[39m|\x1b[35m'
                  'my favorite website\x1b[39m]')
        # green for the link, magenta for the link text
        text = self.fmt.filter_html(html)
        self.assertEqual(expect, text)

    def test_love_formatting(self):
        html = TEST_DATA['test_love_formatting']
        expect = '[\x1b[1m\x1b[34mGORP\x1b[22m\x1b[39m]'  # blue and bold
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
[{link}plan1{unlink}]: 1

 - snip one {bold}term{unbold} context

[{link}plan2{unlink}]: 2

 - snip one {bold}term{unbold} context
 - snip two {bold}term{unbold} context

[{link}plan3{unlink}]: 2

 - snip {bold}term{unbold} twice {bold}term{unbold} twice

""".format(bold='\x1b[1m', unbold='\x1b[22m',
           link='\x1b[1m\x1b[34m', unlink='\x1b[22m\x1b[39m')
        self.assertEqual(expect, output)

if __name__ == "__main__":
    unittest.main(buffer=True)
