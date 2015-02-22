from hashlib import md5
import re
from datetime import datetime
import pytz


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


def parse_plans_date(string, format='%a %B %d %Y, %I:%M %p',
                     tz_name='US/Central'):
    """Convert date string to a python datetime.

    In plan headers, dates are displayed in a human-readable format,
    in Grinnell's local time zone. This reverses that format, and
    converts the result to UTC.

    Returns a naive datetime object - that is, it has no attached
    timezone information. Treat it as UTC.

    """
    # first, parse the string format. This yields a naive datetime
    dt = datetime.strptime(remove_ordinals(string), format)
    # now add the timezone information
    dt = pytz.timezone(tz_name).localize(dt)
    # convert to UTC and make it naive again
    return dt.astimezone(pytz.utc).replace(tzinfo=None)
