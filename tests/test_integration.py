import pytest
import tempfile
import shutil
import io
import os
import sys
from contextlib import contextmanager

if sys.version_info >= (2,7):
    import subprocess
else:
    import subprocess32 as subprocess

# VERY important in this module to always pass the env kwarg
# to subprocesses. Somehow there are race conditions associated with
# modifying environment variables in the working environment

UN1 = 'baldwint'
PW1 = u'password'
TEST_CFG = u"""[login]
username=%s
url=http://localhost/~tkb/phplans/
"""
DEVNULL = io.open(os.devnull, 'w')

@contextmanager
def temp_clansdir(cfg=None, pwd=None, activate=True):
    """
    context for a throwaway clans directory.

    """
    clansdir = tempfile.mkdtemp(suffix='.clansprofile')
    env = make_env(clansdir)
    if cfg is not None:
        # if cfg is provided, pre-fill 'clans.cfg'
        clans_cfg = os.path.join(clansdir, 'clans.cfg')
        with io.open(clans_cfg, 'w') as f:
            f.write(cfg)
    if pwd is not None:
        # if password is given, log us in
        rc = subprocess.call(['clans', '-p', pwd, 'list'],
                env=env, stdout=DEVNULL)
    if activate:
        # make this the default clans directory
        environ_bak = os.environ.copy()
        os.environ['CLANS_DIR'] = clansdir

    yield clansdir

    # now tear down
    if activate:
        os.environ = environ_bak
    shutil.rmtree(clansdir)

def make_env(clansdir):
    myenv = os.environ.copy()
    myenv['CLANS_DIR'] = clansdir
    return myenv

def test_login():
    with temp_clansdir(TEST_CFG % UN1) as cd:
        env = make_env(cd)
        assert '%s.cookie' % UN1 not in os.listdir(cd)
        # log us in
        rc = subprocess.call(['clans', '-p', PW1, 'list'], env=env)
        assert rc == 0
        assert '%s.cookie' % UN1 in os.listdir(cd)
        # no password necessary
        rc = subprocess.call(['clans', 'list'], env=env)
        assert rc == 0
        # log us out
        rc = subprocess.call(['clans', 'list', '--logout'], env=env)
        assert rc == 0
        assert '%s.cookie' % UN1 not in os.listdir(cd)

def test_extension_loading():
    # load the backup extension just to see if it works
    with temp_clansdir(TEST_CFG % UN1, PW1) as cd:
        env = make_env(cd)
        stdout = subprocess.check_output('clans edit --help'.split(),
            stderr=subprocess.STDOUT, env=env)
        assert '--backup' not in str(stdout)
    # if we load the extension, it should modify the help list
    extend_cfg = TEST_CFG + "[extensions]\nbackup="
    with temp_clansdir(extend_cfg % UN1, PW1) as cd:
        env = make_env(cd)
        stdout = subprocess.check_output('clans edit --help'.split(),
            stderr=subprocess.STDOUT, env=env)
        assert '--backup' in str(stdout)

def test_newlove_breakage():
    # there was a bug where the newlove ext would break regular search
    with temp_clansdir(TEST_CFG % UN1, PW1) as cd:
        env = make_env(cd)
        rc = subprocess.call(['clans', 'search', 'term'], env=env)
        assert rc == 0
    extend_cfg = TEST_CFG + "[extensions]\nnewlove="
    with temp_clansdir(extend_cfg % UN1, PW1) as cd:
        env = make_env(cd)
        rc = subprocess.call(['clans', 'search', 'term'], env=env)
        assert rc == 0

@pytest.mark.parametrize("content", [
    "foobar",
    "barfoo\r\n"*20,  #TODO: what about \n?
])
def test_backup_restore(content):
    extend_cfg = TEST_CFG + "[extensions]\nbackup="
    with temp_clansdir(extend_cfg % UN1, PW1) as cd:
        env = make_env(cd)
        # set plan contents
        with tempfile.NamedTemporaryFile('w+') as tf:
            tf.write(content)
            tf.flush()
            stdout = subprocess.check_output(['clans', 'edit',
                '--from-file', tf.name], stderr=subprocess.STDOUT, env=env)
            assert 'Plan changed successfully' in str(stdout)
        # back plan up to file
        bakfile = os.path.join(cd, 'planbak.txt')
        rc = subprocess.call(['clans', 'edit',
            '--backup', bakfile, '--skip-update'], env=env)
        # check that it matches our contents
        with io.open(bakfile, 'r', encoding='utf8', newline='') as bak:
            backup = bak.read()
            assert backup == content
            # diff against stdout method
            stdout = subprocess.check_output(['clans', 'edit',
                '--backup', '--skip-update'], env=env)
            assert stdout.decode('utf8') == backup
        # verify the restore: if it matches, clans won't update
        stdout = subprocess.check_output(['clans', 'edit',
            '--from-file', bakfile], stderr=subprocess.STDOUT, env=env)
        assert 'plan unchanged, aborting update' in stdout.decode('utf8')

def test_editing():
    content = 'bar foo baz\r\n'
    expect = 'bar FOO baz\r\n'
    editor = 'vim -c s/foo/FOO/g -c wq'
    # subtle points: -c arguments to vim should NOT be quoted, as they
    # would be in a shell. Also, vim will insist that files end in
    # newlines if they don't already, so test values should accomodate
    # this ahead of time if our comparisons are going to match.
    # Finally, if the percent sign character appears anywhere in our
    # editor definition, all hell will break loose since both python
    # and ConfigParser can interpret that as part of a formatting
    # mini-language.
    extend_cfg = (TEST_CFG + "[extensions]\nbackup=")
    with temp_clansdir(extend_cfg % UN1, PW1) as cd:
        env = make_env(cd)
        env['EDITOR'] = editor
        # set plan contents
        with tempfile.NamedTemporaryFile('w+') as tf:
            tf.write(content)
            tf.flush()
            stdout = subprocess.check_output(['clans', 'edit',
                '--from-file', tf.name], stderr=subprocess.STDOUT, env=env)
        # do edit
        #with tempfile.NamedTemporaryFile() as tf:
        #    stdout = subprocess.check_output(['clans', 'edit'],
        #        stderr=subprocess.STDOUT, env=env)
        #    assert 'Plan changed successfully' in stdout
        # do edit, with backup extension
        with tempfile.NamedTemporaryFile('w+b') as tf:
            stdout = subprocess.check_output(['clans', 'edit',
                '--save', tf.name], stderr=subprocess.STDOUT, env=env)
            assert 'Plan changed successfully' in stdout.decode('utf8')
            # edit should have been saved by the backup extension
            tf.flush()
            tf.seek(0)
            assert expect == tf.read().decode('utf8')
