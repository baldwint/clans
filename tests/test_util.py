import pytest
from clans import util
from datetime import datetime

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

@pytest.mark.parametrize('data,hash', [
    (u'plain text', u'31bc5c2b8fd4f20cd747347b7504a385'),
    ('<tt># 10 11 12 -----------------</tt>',
        u'6523a6215d386e0e9c9a9ead96984bbe'),
    ('<b>so excited</b>', u'5353151279a27d0cf3622a38ac296eac'),
    ('<hr>contact info blah blah<hr>', u'73513621200053706fae792102065dac'),
    (u'Non-breaking \xa0\xa0 spaces!', u'a454725521eff14835d6c5d79e23998d'),
    (u'Newline at the end\n', u'c5628b1e47bcf016ba500b68e5bbe809'),
    (u'Newline in\nthe middle', u'8ca659f3e07dc3073b0fc87ec67e8454'),
    (u'Linefeed\r\nnewline', u'3e5ad339a8329429027960e549edcba9'),
    (u'\nNewline at the beginning', u'5324cc62896fd6ac2478e9c32df53df9'),
    (u'Non-breaking \xa0\xa0 spaces!', u'a454725521eff14835d6c5d79e23998d'),
    (u'Black \u2605 star', u'7b2c53532dce380bf22c94e24683da14'),
    (u'North \u2196 west', u'd99053cfb75d8be622f822e332317c70'),
    (u"Gauss' \u2207\u2022E = \u03c1/\u03b5\u2080 law",
        u'38748f0c1a9d1a97e36fb50f2ea29039'),
    (u'Pile of \U0001f4a9!', u'206f15e259a0216f1818ff230c339dc4'),
])
def test_hashes(data, hash):
    assert util.plans_md5(data) == hash


@pytest.mark.parametrize('lf,cr,crlf', [
    (u'hello\nworld\n', u'hello\rworld\r', u'hello\r\nworld\r\n'),
    (u'hello\n\nworld', u'hello\r\rworld', u'hello\r\n\r\nworld'),
])
def test_convert_endings(lf, cr, crlf):
    assert lf == util.convert_endings(cr, 'LF')
    assert lf == util.convert_endings(lf, 'LF')
    assert lf == util.convert_endings(crlf, 'LF')
    assert cr == util.convert_endings(cr, 'CR')
    assert cr == util.convert_endings(lf, 'CR')
    assert cr == util.convert_endings(crlf, 'CR')
    assert crlf == util.convert_endings(cr, 'CRLF')
    assert crlf == util.convert_endings(lf, 'CRLF')
    assert crlf == util.convert_endings(crlf, 'CRLF')


@pytest.mark.parametrize('orig,cleaned', [
    ('4th', '4'),
    ('January 12th', 'January 12'),
    ('Nov 2nd 2014', 'Nov 2 2014'),
])
def test_remove_ordinals(orig, cleaned):
    assert util.remove_ordinals(orig) == cleaned


@pytest.mark.parametrize('string,result', [
    # Central time is -6 in the winter and -5 in the summer
    ('Wed January 28th 2015, 5:46 PM',
        datetime(2015, 1, 28, 23, 46)),
    ('Thu April 12th 2012, 3:06 PM',
        datetime(2012, 4, 12, 20, 6)),
])
def test_parse_plans_date(string, result):
    assert util.parse_plans_date(string) == result


@pytest.mark.parametrize('dic,result', [
    # respect the order of ordered dicts
    (OrderedDict((("bae", "come over"),
                  ("me", "cant writing unit tests"))),
    '{\n  "bae": "come over",\n  "me": "cant writing unit tests"\n}'),
    (OrderedDict((("me", "cant writing unit tests"),
                  ("bae", "come over"))),
    '{\n  "me": "cant writing unit tests",\n  "bae": "come over"\n}'),
    # but regular dicts should be sorted
    (dict((("me", "cant writing unit tests"),
           ("bae", "come over"))),
    '{\n  "bae": "come over",\n  "me": "cant writing unit tests"\n}'),
    # and datetimes should be ISO-1601'd
    ({"beg": datetime(2013, 5, 1, 3, 26, 56),
      "end": datetime(2013, 5, 1, 5, 26, 56)},
    '{\n  "beg": "2013-05-01T03:26:56Z",\n  "end": "2013-05-01T05:26:56Z"\n}'),
])
def test_json_output(dic, result):
    thing = util.json_output(dic)
    assert util.json_output(dic) == result
