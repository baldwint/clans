import pytest
import tempfile
import shutil
import io
import os
from contextlib import contextmanager
import subprocess

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
        assert '--backup' not in stdout
    # if we load the extension, it should modify the help list
    extend_cfg = TEST_CFG + "[extensions]\nbackup="
    with temp_clansdir(extend_cfg % UN1, PW1) as cd:
        env = make_env(cd)
        stdout = subprocess.check_output('clans edit --help'.split(),
            stderr=subprocess.STDOUT, env=env)
        assert '--backup' in stdout

def test_backup_restore():
    #TODO: this just uses whatever value is pre-filled on the test
    #server, should probably parameterize
    extend_cfg = TEST_CFG + "[extensions]\nbackup="
    with temp_clansdir(extend_cfg % UN1, PW1) as cd:
        env = make_env(cd)
        # back plan up to file
        bakfile = os.path.join(cd, 'planbak.txt')
        rc = subprocess.call(['clans', 'edit',
            '--backup', bakfile, '--skip-update'], env=env)
        assert 'planbak.txt' in os.listdir(cd)
        # verify the restore: if it matches, clans won't update
        stdout = subprocess.check_output(['clans', 'edit',
            '--file', bakfile], stderr=subprocess.STDOUT, env=env)
        assert 'plan unchanged, aborting update' in stdout
