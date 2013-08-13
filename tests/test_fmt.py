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

#TODO: TestRaw, TestColor

class TestText(unittest.TestCase):

    def setUp(self):
        self.fmt = clans.fmt.TextFormatter() 

    # plan format test

    def test_format_plan(self):
        headers = {
                'lastupdated': 'Mon August 5th 2013, 1:22 PM',
                'lastlogin': 'Wed August 7th 2013, 3:42 AM',
                'username': 'username',
                'planname': 'clever catchphrase',
                }
        plan = 'this is my plan with the html filtered out\n'
        text = self.fmt.format_plan(plan = plan, **headers)
        expect = """\
Username: username
Last Updated: Mon August 5th 2013, 1:22 PM
Last Login: Wed August 7th 2013, 3:42 AM
Name: clever catchphrase

this is my plan with the html filtered out
"""
        self.assertEqual(expect, text)


    # filter_html tests

    def test_br_stripping(self):
        html = "one<br>two<br/>three<br />four"
        text = self.fmt.filter_html(html)
        expect = "one\ntwo\nthree\nfour"
        self.assertEqual(expect, text)

    def test_html_escapes(self):
        html = "I develop in a &quot;quick &amp; dirty&quot; &lt;style&gt;"
        text = self.fmt.filter_html(html)
        expect = 'I develop in a "quick & dirty" <style>'
        self.assertEqual(expect, text)

    def test_tag_stripping(self):
        html = "This is <b>bold</b> and <i>italic</i>"
        expect = "This is bold and italic"
        text = self.fmt.filter_html(html)
        self.assertEqual(expect, text)

    def test_link_formatting(self):
        html = '<a href="http://www.facebook.com/" class="onplan">my favorite website</a>'
        expect = '[http://www.facebook.com/|my favorite website]'
        text = self.fmt.filter_html(html)
        self.assertEqual(expect, text)

    def test_love_formatting(self):
        html = '[<a href="read.php?searchname=gorp" class="planlove">GORP</a>]'
        expect = '[GORP]'
        text = self.fmt.filter_html(html)
        self.assertEqual(expect, text)

    def test_psub_formatting(self):
        html = '<p class="sub">we all live in a yellow</p>'
        expect = 'we all live in a yellow'
        text = self.fmt.filter_html(html)
        self.assertEqual(expect, text)

    def test_hr_formatting(self):
        html = """I need a clean
<hr>break"""
        expect = """I need a clean

======================================================================
break"""
        text = self.fmt.filter_html(html)
        self.assertEqual(expect, text)

    # other tests

    def test_print_list(self):
        self.fmt.print_list(['one', 'two', 'three', 'four'])
        output = sys.stdout.getvalue()
        expect = u"""\
 - one
 - two
 - three
 - four
"""
        self.assertEqual(expect, output)

    def test_print_search_results(self):
        results = [
                ('plan1', 1, ['snip one <b>term</b> context',]),
                ('plan2', 2, ['snip one <b>term</b> context',
                              'snip two <b>term</b> context']),
                ('plan3', 2, ['snip <b>term</b> twice <b>term</b> twice',])
                ]
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

    def test_print_autoread(self):
        autoread = {
                'Level 1': ['bff', 'interesting', 'funny', 'gorp'],
                'Level 2': ['roommate', 'rando'],
                'Level 3': ['meh',],
                }
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

class TestColor(TestText):

    def setUp(self):
        self.fmt = clans.fmt.ColorFormatter()

    # plan format test

    def test_format_plan(self):
        headers = {
                'lastupdated': 'Mon August 5th 2013, 1:22 PM',
                'lastlogin': 'Wed August 7th 2013, 3:42 AM',
                'username': 'username',
                'planname': 'clever catchphrase',
                }
        plan = 'this is my plan with the html filtered out\n'
        text = self.fmt.format_plan(plan = plan, **headers)
        expect = """\
%sUsername%s: username
%sLast Updated%s: Mon August 5th 2013, 1:22 PM
%sLast Login%s: Wed August 7th 2013, 3:42 AM
%sName%s: clever catchphrase

this is my plan with the html filtered out
""" % (('\x1b[1m', '\x1b[22m') * 4)
        self.assertEqual(expect, text)


    # filter_html tests

    def test_tag_stripping(self):
        html = "This is <b>bold</b> and <i>italic</i>"
        expect = "This is \x1b[1mbold\x1b[22m and \x1b[2mitalic\x1b[22m"
        # italic is actually 'dim', bold 'bright'
        text = self.fmt.filter_html(html)
        self.assertEqual(expect, text)

    def test_link_formatting(self):
        html = '<a href="http://www.facebook.com/" class="onplan">my favorite website</a>'
        expect = '[\x1b[32mhttp://www.facebook.com/\x1b[39m|\x1b[35mmy favorite website\x1b[39m]'
        # green for the link, magenta for the link text
        text = self.fmt.filter_html(html)
        self.assertEqual(expect, text)

    def test_love_formatting(self):
        html = '[<a href="read.php?searchname=gorp" class="planlove">GORP</a>]'
        expect = '[\x1b[1m\x1b[34mGORP\x1b[22m\x1b[39m]' # blue and bold
        text = self.fmt.filter_html(html)
        self.assertEqual(expect, text)

    def test_hr_formatting(self):
        html = """I need a clean
<hr>break"""
        expect = """I need a clean

\x1b[31m======================================================================\x1b[39m
break"""
        # red
        text = self.fmt.filter_html(html)
        self.assertEqual(expect, text)

    # other tests

    def test_print_search_results(self):
        results = [
                ('plan1', 1, ['snip one <b>term</b> context',]),
                ('plan2', 2, ['snip one <b>term</b> context',
                              'snip two <b>term</b> context']),
                ('plan3', 2, ['snip <b>term</b> twice <b>term</b> twice',])
                ]
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

