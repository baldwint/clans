import re

REGEX_LOVE = r'<a href=[^\s]* class="planlove">(.+?)</a>'
REGEX_SUB = r'<p class="sub">(.+?)</p>'

def filter_html(html):
    """
    format plan html as plain text.

    """
    html = re.sub(r'<br ?/?>', '\n', html)
    html = re.sub(r'&quot;', '"', html)
    html = re.sub(r'&gt;', '>', html)
    html = re.sub(r'&lt;', '<', html)
    html = re.sub(r'<b>(.+?)</b>', r'\1', html)
    html = re.sub(r'<i>(.+?)</i>', r'\1', html)
    html = re.sub(REGEX_LOVE, r'\1', html)
    html = re.sub(REGEX_SUB, r'\1', html, flags=re.DOTALL)
    html = re.sub(r'<hr ?/?>', 70*'=' + '\n', html)
    return html

