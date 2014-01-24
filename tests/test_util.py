import pytest
from clans import util


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
def test_endings(data, hash):
    assert util.plans_md5(data) == hash
