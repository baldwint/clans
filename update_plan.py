#!/usr/bin/env python
"""Edit your plan in $EDITOR."""

import urllib2
from urllib import urlencode
import cookielib
import os
import tempfile
import subprocess
from BeautifulSoup import BeautifulSoup

class PlansError(Exception):
    """Exception raised when there is an error talking to plans."""
    pass

# -------------------------------------------
#              PLANS SCRAPEY-I
# get it? like "api" except... oh, never mind
# -------------------------------------------

class PlansConnection(object):
    """
    Encapsulates an active login to plans.

    """

    def __init__(self, cookiejar=None,
                 base_url="http://www.grinnellplans.com"):
        """
        Create a new plans connection.

        Optional keyword arguments:

        cookiejar -- an existing cookielib.CookieJar to store
                     credentials in.
        base_url --  URL at which to access plans, no trailing slash.

        """
        self.base_url = base_url
        if cookiejar is None:
            self.cookiejar = cookielib.LWPCookieJar()
        else:
            self.cookiejar = cookiejar
        proc = urllib2.HTTPCookieProcessor(self.cookiejar)
        self.opener = urllib2.build_opener(proc)

    def _get_page(self, name, get=None, post=None):
        """
        Retrieve an HTML page from plans.

        """
        url = '/'.join((self.base_url, name))
        if get is not None:
            url = '?'.join((url, urlencode(get)))
        req = urllib2.Request(url)
        if post is not None:
            post = urlencode(post)
        handle = self.opener.open(req, post)
        return handle.read()

    def plans_login(self, username, password):
        """
        Log into plans.
        
        """
        login_info = {'username': username,
                      'password': password,
                        'submit': 'Login' }
        html = self._get_page('index.php', post=login_info)
        # verify login by checking that body id="planspage_home"
        soup = BeautifulSoup(html)
        homepage = soup.find('body', {'id': 'planspage_home'})
        if homepage is None:
            raise PlansError('Could not log in as [%s].' % username)

    def get_edit_text(self, plus_hash=False):
        """
        Retrieve contents of the edit plan field.

        Optionally, simultaneously retrieve the md5 hash of
        the edit text, as computed on the server side.

        """
        # grab edit page
        html = self._get_page('edit.php')
        # parse out existing plan
        soup = BeautifulSoup(html)
        plan = soup.find('textarea')
        if plan is None:
            raise PlansError("Couldn't get edit text, are we logged in?")
        if plus_hash:
            # parse out plan md5
            md5tag = soup.find('input', {'name': 'edit_text_md5'})
            md5 = md5tag.attrMap['value']
            return plan.text, md5
        else:
            return plan.text

    def set_edit_text(self, newtext, md5):
        """
        Update plan with new content.

        To prevent errors, the server does a hash check on the existing
        plan before replacing it with the new one. We provide an
        md5 sum to confirm that yes, we really want to update the plan.

        Prints info message to stdout.
        
        """
        edit_info = {         'plan': newtext,
                     'edit_text_md5': md5,
                            'submit': 'Change Plan' }
        html = self._get_page('edit.php', post=edit_info)
        soup = BeautifulSoup(html)
        info = soup.find('div', {'class': 'infomessage'})
        print >> sys.stderr, info

# ----------
# UI HELPERS
# ----------

def edit(text, **kwargs):
    """
    Open some text for editing by the user.

    Keyword arguments are passed to the tempfile constructor.

    """
    if 'text' not in kwargs:
        kwargs['text'] = True

    # I cribbed this from the mercurial source code, in ui.py.
    fd, name = tempfile.mkstemp(**kwargs)
    try:
        # populate the temp file with original text.
        f = os.fdopen(fd, 'w')
        f.write(text)
        f.close()

        # open in $EDITOR (default to pico)
        editor = os.environ.get('EDITOR', 'pico')
        subprocess.call([editor, name])

        # retrieve edited text
        f = open(name)
        t = f.read()
        f.close()
    finally:
        os.unlink(name)

    return t



if __name__ == '__main__':
    import ConfigParser
    from argparse import ArgumentParser
    import getpass
    import sys

    # set config file defaults
    config = ConfigParser.ConfigParser()
    config.add_section('login')
    config.set('login', 'username', '')

    # read user's config file, if present
    config.read(os.path.expanduser('~/.update_plan.cfg'))

    # define command line arguments
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('-u', '--username', dest='username',
              help='GrinnellPlans username, no brackets.')
    parser.add_argument('-p', '--password', dest='password',
              help='GrinnellPlans password. Omit for secure entry.')
    parser.add_argument('-b', '--backup', dest='backup_file',
                        nargs='?', default=False, metavar='FILE',
              help="""Backup existing plan to file before editing.
                        To print to stdout, omit filename.""")
    parser.add_argument('-s', '--save', dest='save_edit',
                        default=False, metavar='FILE',
              help='Save a local copy of edited plan before submitting.')
    parser.add_argument('--pretend', dest='pretend',
                        action='store_true', default=False,
              help="Don't actually do the update.")
    parser.add_argument('--logout', dest='logout',
                        action='store_true', default=False,
              help='Log out after editing.')

    # get command line arguments
    args = parser.parse_args()

    # let command line args override equivalent config file settings
    username = args.username or config.get('login', 'username')

    cj = cookielib.LWPCookieJar(
        os.path.expanduser('~/.%s.plans.cookie' % username)
    )
    try:
        cj.load() # this will fail with IOError if it does not exist
                  #TODO: what if it exists, but is expired?
    except IOError:
        # no cookie saved for this user; log in.
        if args.password is None:
            # prompt for password if necessary
            args.password = getpass.getpass("[%s]'s password: " % username)
            if '\x03' in args.password:
                # http://bugs.python.org/issue11236 (2.6 only)
                raise PlansError('aborted by user')
        pc = PlansConnection(cj)
        pc.plans_login(username, args.password)
    else:
        pc = PlansConnection(cj)

    plan_text, md5 = pc.get_edit_text(plus_hash=True)

    #TODO: get these to match somehow
    #import hashlib
    #print md5
    #print hashlib.md5(plan_text.encode('utf8')).hexdigest()

    if args.backup_file is False:
        pass
    elif args.backup_file is None:
        # print existing plan to stdout and exit
        print >> sys.stdout, plan_text.encode('utf8')
        sys.exit()
    elif args.backup_file:
        # save existing plan to file
        fp = open(args.backup_file, 'w')
        fp.write(plan_text.encode('utf8'))
        fp.close()

    # open for external editing
    edited = edit(plan_text.encode('utf8'), suffix='.plan')
    edit_was_made = edited != plan_text.encode('utf8')

    if args.save_edit and edit_was_made:
        # save edited file
        fp = open(args.save_edit, 'w')
        fp.write(edited)
        fp.close()

    if not edit_was_made:
        print >> sys.stderr, 'plan unchanged, aborting update'
    elif args.pretend:
        print >> sys.stderr, "in 'pretend' mode, not really editing"
    else:
        # do the plan update!
        pc.set_edit_text(edited, md5)

    if args.logout:
        os.unlink(cj.filename)
    else:
        # save cookie
        cj.save()


