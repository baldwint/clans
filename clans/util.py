from hashlib import md5
import re
import dateutil.parser
import pytz
from datetime import datetime

import json
try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


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

ISO8601_UTC_FMT = '%Y-%m-%dT%H:%M:%SZ'
"""Format string for ISO 8601 datetimes, as represented in JSON.

The 'Z' for UTC is hardcoded, so only use this with UTC datetimes, or
naive datetimes that are assumed to be UTC.
"""


def json_output(dic):
    """Standard JSON output for clans.

    This handles some finer points, like converting datetimes to ISO
    8601 format, stripping whitespace, etc.
    """
    # first, a custom encoder class to handle datetimes
    class DatetimeEncoder(json.JSONEncoder):
        """ Handles encoding of datetimes as ISO 8601 format text in JSON """
        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.strftime(ISO8601_UTC_FMT)
            return json.JSONEncoder.default(self, obj)
    # if the provided dictionary is ordered, don't sort
    sort_keys = not isinstance(dic, OrderedDict)
    string = json.dumps(dic, indent=2,
                        cls=DatetimeEncoder,
                        sort_keys=sort_keys)
    # python prior to 3.4 inserted spaces after commas in json
    return re.sub(r', \n', ',\n', string)


def remove_ordinals(string):
    """Remove Anglocentric ordinal suffixes from numbers"""
    return re.sub(r'(\d+)(st|nd|rd|th)', r'\1', string)


def parse_plans_date(string, tz_name='US/Central'):
    """Convert date string to a python datetime.

    In plan headers, dates are displayed in a human-readable format,
    in Grinnell's local time zone. This reverses that format, and
    converts the result to UTC.

    Returns a naive datetime object - that is, it has no attached
    timezone information. Treat it as UTC.

    """
    # first, parse the string format. This yields a naive datetime
    dt = dateutil.parser.parse(string)
    # now add the timezone information
    dt = pytz.timezone(tz_name).localize(dt)
    # convert to UTC and make it naive again
    return dt.astimezone(pytz.utc).replace(tzinfo=None)
