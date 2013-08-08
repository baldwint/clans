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

class TestText(unittest.TestCase):

    def setUp(self):
        self.fmt = clans.fmt.TextFormatter() 

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
        expect = """\
 - one
 - two
 - three
 - four
"""
        self.assertEqual(expect, output)

if __name__ == "__main__":
    unittest.main(buffer=True)

