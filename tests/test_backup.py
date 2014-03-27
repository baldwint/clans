import pytest
import tempfile
import sys
import io
import os
import shutil

if sys.version_info >= (3, 3):
    import unittest.mock as mock
else:
    import mock

from clans.ext import backup
from clans.ui import ClansSession

PLAN_TEXT = u'plan text'
TEST_PWD = u'password'
TEST_CFG = u"""
[login]
username=baldwint
url=http://localhost/~tkb/phplans/
[extensions]
backup=
"""

@pytest.fixture(scope='module')
def clansdir(request):
    # make a fake clans directory
    clansdir = tempfile.mkdtemp(suffix='.clansprofile')
    # configure to point to testing server
    clans_cfg = os.path.join(clansdir, 'clans.cfg')
    with io.open(clans_cfg, 'w') as f:
        f.write(TEST_CFG)
    # run a throwaway ClansSession to generate the cookie
    cs = ClansSession(profile_dir=clansdir)
    cs.run(['-p', TEST_PWD, 'list'])
    assert 'baldwint.cookie' in os.listdir(clansdir)
    # now back up the plan, and set it to a known value
    pc = cs.make_plans_connection()
    del cs
    orig_text, hash = pc.get_edit_text(plus_hash=True)
    pc.set_edit_text(PLAN_TEXT, hash)
    # define cleanup actions
    def cleanup():
        garbage, hash = pc.get_edit_text(plus_hash=True)
        pc.set_edit_text(orig_text, hash)
        shutil.rmtree(clansdir)  # remove temp dir
    request.addfinalizer(cleanup)
    return clansdir

def test_skipupdate(clansdir, capsys):
    # should give no output
    cs = ClansSession(profile_dir=clansdir)
    cs.run(['edit', '--skip-update'])
    stdout,stderr = capsys.readouterr()
    assert stdout == ''
    assert stderr == ''

def test_stdout(clansdir, capsys):
    cs = ClansSession(profile_dir=clansdir)
    cs.run(['edit', '--skip-update', '--backup'])
    # test that plan text matches stdout
    stdout,stderr = capsys.readouterr()
    assert stdout == PLAN_TEXT
    assert stderr == ''

def test_restore(clansdir, capsys):
    cs = ClansSession(profile_dir=clansdir)
    # restore from a temporary file
    fd, name = tempfile.mkstemp()
    restore_text = u"restored plan text"
    with io.open(fd, 'w',  encoding='utf8', newline='') as f:
        f.write(restore_text)
    cs.run(['edit', '--file', name])
    stdout,stderr = capsys.readouterr()
    assert stdout == ''
    assert stderr == 'Plan changed successfully.\n'
    pc = cs.make_plans_connection()
    text,hash = pc.get_edit_text(plus_hash=True)
    assert text == restore_text
