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


def clean_json(string):
    """python prior to 3.4 inserted spaces after commas in json"""
    return re.sub(r', \n', ',\n', string)


def remove_ordinals(string):
    """Remove Anglocentric ordinal suffixes from numbers"""
    return re.sub(r'(\d+)(st|nd|rd|th)', r'\1', string)
