"""
Formatters (views) for clans

"""

from __future__ import print_function, unicode_literals
import re
import colorama as cr
#TODO only import these if needed
from itertools import izip_longest
import sys

#in colorama, add support for underlining
cr.Style.UNDERLINE = '\x1b[4m'

HEADERS = [('Username', '{username}'),
           ('Last Updated', '{lastupdated}'),
           ('Last Login', '{lastlogin}'),
           ('Name', '{planname}')]


class RawFormatter(object):

    def filter_html(self, html):
        return html

    def format_plan(self, **kwargs):
        read_fmt = '\n'.join(': '.join(header) for header in HEADERS)
        read_fmt += "\n\n{plan}"
        return read_fmt.format(**kwargs)

    def format_planlove(self, un):
        return "[%s]" % un

    def print_list(self, items, bullets=False):
        """
        prints a list line by line

        :param items: a list of strings to print.

        """
        for item in items:
            item = self.filter_html(item)
            if bullets:
                item = (u" - {0}").format(item)
            print(item.encode('utf8'))

    def print_search_results(self, results):
        """
        prints search results to stdout.

        :param results: whatever was returned by the ``search_plans``
        method on PlansConnection.

        """
        for un, count, snips in results:
            username = self.format_planlove(un)
            print((u"{0}: {1}\n"
                   ).format(username, count).encode('utf8'))
            self.print_list(snips, bullets=True)
            print(u"")

    def print_autoread(self, results):
        for level in sorted(results.keys()):
            print(u"{level}:".format(level=level).encode('utf8'))
            self.print_list(results[level])
            print(u"")


class TextFormatter(RawFormatter):

    REGEX_LOVE = r'<a href="[^\s]*" class="planlove">(.+?)</a>'
    REGEX_LINK = r'<a href="([^\s]*)" class="onplan">(.+?)</a>'
    REGEX_SUB = r'<p class="sub">(.+?)</p>'
    REGEX_UL = r'<span class="underline">(.+?)</span><!--u-->'

    hr = '\n' + 70*'=' + '\n'
    a = r'[\1|\2]'

    def filter_html(self, html):
        """
        format plan html as plain text.

        """
        html = html.replace('\n','').replace('\r','')
        html = re.sub(r'<br ?/?>', '\n', html)
        html = re.sub(r'&quot;', '"', html)
        html = re.sub(r'&gt;', '>', html)
        html = re.sub(r'&lt;', '<', html)
        html = re.sub(r'&amp;', '&', html)
        html = re.sub(r'<b>(.+?)</b>', r'\1', html)
        html = re.sub(r'<i>(.+?)</i>', r'\1', html)
        html = re.sub(self.REGEX_UL,   r'\1', html)
        html = re.sub(self.REGEX_LOVE, r'\1', html)
        html = re.sub(self.REGEX_LINK, self.a, html)
        html = re.sub(re.compile(self.REGEX_SUB, flags=re.DOTALL), r'\1', html)
        html = re.sub(r'<hr ?/?>', self.hr, html)
        return html

    def print_list(self, items, columns=None, **kwargs):
        """
        print a list of text strings, formatting into columns

        """
        lst = list(items)
        if not lst:
            return  # nothing to print
        if columns is None:
            columns = sys.stdout.isatty()  # if printing to terminal
        max_len = max(len(word) for word in lst) + 2  # padding
        TERM_WIDTH = 80
        ncols = TERM_WIDTH // max_len
        if (not columns) or (ncols < 2):
            # if we are piping output, or only one column,
            # fall back to non-fancy formatting
            RawFormatter.print_list(self, items, **kwargs)
            return
        args = [iter(lst)] * ncols
        for group in izip_longest(fillvalue='', *args):
            print("".join(word.ljust(max_len) for word in group).rstrip())


class ColorFormatter(TextFormatter):

    hr = '\n' + cr.Fore.RED + 70*'=' + cr.Fore.RESET + '\n'
    a = r'[%s\1%s|%s\2%s]' % (cr.Fore.GREEN, cr.Fore.RESET,
                              cr.Fore.MAGENTA, cr.Fore.RESET)

    def format_plan(self, **kwargs):
        color_headers = [(cr.Style.BRIGHT + k + cr.Style.NORMAL, v)
                         for k, v in HEADERS]
        read_fmt = '\n'.join(': '.join(header) for header in color_headers)
        read_fmt += "\n\n{plan}"
        return read_fmt.format(**kwargs)

    def format_planlove(self, un):
        return "[" + cr.Style.BRIGHT + cr.Fore.BLUE + \
            un + cr.Style.NORMAL + cr.Fore.RESET + "]"

    def filter_html(self, html):
        """
        format html for display in the terminal, with colors.

        """
        html = re.sub(r'(<b>.+?</b>)',
                      cr.Style.BRIGHT + r'\1' + cr.Style.NORMAL, html)
        html = re.sub(r'(<i>.+?</i>)',
                      cr.Style.DIM + r'\1' + cr.Style.NORMAL, html)
        html = re.sub(self.REGEX_UL,  # Style.NORMAL doesn't reset underline
                      cr.Style.UNDERLINE + r'\1' + cr.Style.RESET_ALL, html)
        html = re.sub(self.REGEX_LOVE,
                      cr.Style.BRIGHT + cr.Fore.BLUE +
                      r'\1' + cr.Style.NORMAL + cr.Fore.RESET, html)
        html = super(ColorFormatter, self).filter_html(html)
        return html
