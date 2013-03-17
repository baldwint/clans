import re
from .text import REGEX_LOVE, REGEX_SUB
import colorama as cr

READ_FMT = (
    cr.Style.BRIGHT + "Username" + cr.Style.NORMAL + ": {username}\n" +
    cr.Style.BRIGHT + "Last Updated" + cr.Style.NORMAL + ": {lastupdated}\n" +
    cr.Style.BRIGHT + "Last Login" + cr.Style.NORMAL + ": {lastlogin}\n" +
    cr.Style.BRIGHT + "Name" + cr.Style.NORMAL + ": {planname}\n\n" +
            "{plan}")

def filter_html(html):
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
    html = re.sub(REGEX_SUB, r'\1', html, flags=re.DOTALL)
    html = re.sub(r'<hr ?/?>',
            cr.Fore.RED + 70*'=' + cr.Fore.RESET + '\n', html)
    html = re.sub(REGEX_LOVE,
            cr.Style.BRIGHT + cr.Fore.BLUE + \
            r'\1' + cr.Style.NORMAL + cr.Fore.RESET, html)
    return html

