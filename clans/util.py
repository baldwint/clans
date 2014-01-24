from hashlib import md5
import re


def plans_md5(plan):
    """compute the md5 sum of a plan, for verification"""
    return md5(plan.encode('utf8')).hexdigest()


def convert_endings(string, mode):
    mode = mode.upper()
    if mode == 'CRLF':
        return re.sub("\r(?!\n)|(?<!\r)\n", "\r\n", string)
    elif mode == 'LF':
        return string.replace('\r\n', '\n').replace('\r', '\n')
    elif mode == 'CR':
        return string.replace('\r\n', '\r').replace('\n', '\r')
