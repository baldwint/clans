"""
Formatters (views) for clans

"""

import re
import colorama as cr
#TODO only import these if needed

class RawFormatter(object):

    def filter_html(self, html):
        return html

    HEADERS = [('Username', '{username}'),
               ('Last Updated', '{lastupdated}'),
               ('Last Login', '{lastlogin}'),
               ('Name', '{planname}')]

    READ_FMT = '\n'.join( ': '.join(header) for header in HEADERS)
    READ_FMT += "\n\n{plan}"

class TextFormatter(RawFormatter):

    REGEX_LOVE = r'<a href=[^\s]* class="planlove">(.+?)</a>'
    REGEX_SUB = r'<p class="sub">(.+?)</p>'

    def filter_html(self, html):
        """
        format plan html as plain text.

        """
        html = re.sub(r'<br ?/?>', '\n', html)
        html = re.sub(r'&quot;', '"', html)
        html = re.sub(r'&gt;', '>', html)
        html = re.sub(r'&lt;', '<', html)
        html = re.sub(r'<b>(.+?)</b>', r'\1', html)
        html = re.sub(r'<i>(.+?)</i>', r'\1', html)
        html = re.sub(self.REGEX_LOVE, r'\1', html)
        html = re.sub(re.compile(self.REGEX_SUB, flags=re.DOTALL), r'\1', html)
        html = re.sub(r'<hr ?/?>', '\n' + 70*'=' + '\n', html)
        return html

class ColorFormatter(TextFormatter):

    HEADERS = [(cr.Style.BRIGHT + k + cr.Style.NORMAL, v)
                    for k,v in RawFormatter.HEADERS]

    READ_FMT = '\n'.join( ': '.join(header) for header in HEADERS)
    READ_FMT += "\n\n{plan}"

    def filter_html(self, html):
        """
        format html for display in the terminal, with colors.

        """
        html = re.sub(r'<br ?/?>', '\n', html)
        html = re.sub(r'&quot;', '"', html)
        html = re.sub(r'&gt;', '>', html)
        html = re.sub(r'&lt;', '<', html)
        html = re.sub(r'<b>(.+?)</b>',
                cr.Style.BRIGHT + r'\1' + cr.Style.NORMAL, html)
        html = re.sub(r'<i>(.+?)</i>',
                cr.Style.DIM + r'\1' + cr.Style.NORMAL, html)
        html = re.sub(re.compile(self.REGEX_SUB, flags=re.DOTALL), r'\1', html)
        html = re.sub(r'<hr ?/?>',
                '\n' + cr.Fore.RED + 70*'=' + cr.Fore.RESET + '\n', html)
        html = re.sub(self.REGEX_LOVE,
                cr.Style.BRIGHT + cr.Fore.BLUE + \
                r'\1' + cr.Style.NORMAL + cr.Fore.RESET, html)
        return html

