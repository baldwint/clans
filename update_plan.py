#!/usr/bin/env python
"""Edit your plan in $EDITOR."""

import urllib2
from urllib import urlencode
import cookielib
import os
import sys
import tempfile
import subprocess
import json
from BeautifulSoup import BeautifulSoup
from HTMLParser import HTMLParser

class PlansError(Exception):
    """Exception raised when there is an error talking to plans."""
    pass

class PlansPageParser(HTMLParser):
    """HTML parser for GrinnellPlans pages."""

    def handle_starttag(self, tag, attrs):
        if tag == 'body':
            # parse out id of body tag
            # (can use to identify page)
            for key, value in attrs:
                if key == 'id': self.page_id = value
        if tag == 'input':
            # parse edit text md5 from input tag.
            # in the current plans implementation,
            # the syntax is < > and not < />
            attrs = dict(attrs)
            try:
                if attrs['name'] == 'edit_text_md5':
                    self.edit_text_md5 = attrs['value']
            except KeyError:
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
        self.parser = PlansPageParser()

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
        try:
            handle = self.opener.open(req, post)
        except urllib2.URLError:
            err = "Check your internet connection. Plans could also be down."
            raise PlansError(err)
        return handle

    def plans_login(self, username='', password=''):
        """
        Log into plans.

        Returns True on success, False on failure. Leave username and
        password blank to check an existing login.
        
        """
        # the provided username and password ONLY get checked
        # by the plans server if our cookie is expired. 
        # hence, if we've logged in recently, this will return True even
        # if un/pw are not provided or are otherwise bad. 
        login_info = {'username': username,
                      'password': password,
                        'submit': 'Login' }
        response = self._get_page('index.php', post=login_info)
        # if login is successful, we'll be redirected to home
        return response.geturl()[-9:] == '/home.php'

    def get_edit_text(self, plus_hash=False):
        """
        Retrieve contents of the edit plan field.

        Optionally, simultaneously retrieve the md5 hash of
        the edit text, as computed on the server side.

        """
        # grab edit page
        html = self._get_page('edit.php').read()
        # parse out existing plan
        soup = BeautifulSoup(html)
        plan = soup.find('textarea')
        if plan is None:
            raise PlansError("Couldn't get edit text, are we logged in?")
        else:
            plan = plan.text.encode('utf8')
        if plus_hash:
            # parse out plan md5
            self.parser.feed(html)
            md5 = self.parser.edit_text_md5
            return plan, md5
        else:
            return plan

    def set_edit_text(self, newtext, md5):
        """
        Update plan with new content.

        To prevent errors, the server does a hash check on the existing
        plan before replacing it with the new one. We provide an
        md5 sum to confirm that yes, we really want to update the plan.

        Returns info message.
        
        """
        edit_info = {         'plan': newtext,
                     'edit_text_md5': md5,
                            'submit': 'Change Plan' }
        html = self._get_page('edit.php', post=edit_info).read()
        soup = BeautifulSoup(html)
        #TODO: what if the edit fails? catch warnings as well.
        info = soup.find('div', {'class': 'infomessage'})
        return info

    def get_autofinger(self):
        """
        Retrieve all levels of the autofinger (autoread) list.

        Returns a dictionary where the keys are the group names
        "Level 1", "Level 2", etc. and the values are a list of
        usernames waiting to be read.

        """
        # this actually doesn't scrape; there's a function for it
        # in the old JSON API. 
        get = {'task': 'autofingerlist'}
        response = self._get_page('api/1/index.php', get=get)
        data = json.loads(response.read())
        # the returned JSON is crufty; clean it up
        autofinger = {}
        for group in data['autofingerList']:
            name = "Level %s" % group['level']
            autofinger[name] = group['usernames']
        return autofinger


# ----------
# UI HELPERS
# ----------

def external_editor(text, **kwargs):
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


def main():
    import ConfigParser
    from argparse import ArgumentParser
    import getpass as getpass_mod

    def getpass(*args, **kwargs):
        password = getpass_mod.getpass(*args, **kwargs)
        if '\x03' in password:
            # http://bugs.python.org/issue11236 (2.6 only)
            raise KeyboardInterrupt('aborted by user')
        return password

    # set config file defaults
    config = ConfigParser.ConfigParser()
    config.add_section('login')
    config.set('login', 'username', '')
    config.set('login', 'url', 'http://www.grinnellplans.com')

    # create config directory if it doesn't exist
    config_dir = os.path.join(os.environ['HOME'], '.update_plan')
    try:
        # 0700 for secure-ish cookie storage.
        os.mkdir(config_dir, 0700)
    except OSError:
        pass # already exists

    # read user's config file, if present
    config.read(os.path.join(config_dir, 'update_plan.cfg'))

    # define command line arguments
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('-u', '--username', dest='username', default='',
              help='GrinnellPlans username, no brackets.')
    parser.add_argument('-p', '--password', dest='password', default='',
              help='GrinnellPlans password. Omit for secure entry.')
    parser.add_argument('-b', '--backup', dest='backup_file',
                        nargs='?', default=False, metavar='FILE',
              help="""Backup existing plan to file before editing.
                        To print to stdout, omit filename.""")
    parser.add_argument('-s', '--save', dest='save_edit',
                        default=False, metavar='FILE',
              help='Save a local copy of edited plan before submitting.')
    parser.add_argument('--skip-update', dest='skip_update',
                        action='store_true', default=False,
              help="Don't update the plan or open it for editing.")
    parser.add_argument('--pretend', dest='pretend',
                        action='store_true', default=False,
              help="Open plan for editing, but don't actually do the update.")
    parser.add_argument('--logout', dest='logout',
                        action='store_true', default=False,
              help='Log out after editing.')

    # get command line arguments
    args = parser.parse_args()

    # let command line args override equivalent config file settings
    username = args.username or config.get('login', 'username')

    cj = cookielib.LWPCookieJar(
        os.path.join(config_dir, '%s.cookie' % username))

    try:
        cj.load() # this will fail with IOError if it does not exist
    except IOError:
        pass      # no cookie saved for this user

    pc = PlansConnection(cj, base_url = config.get('login', 'url'))

    if pc.plans_login():
        pass # we're still logged in
    else:
        # we're not logged in, prompt for password if necessary
        password = args.password or getpass("[%s]'s password: " % username)
        success = pc.plans_login(username, password)
        if not success:
            print >> sys.stderr, 'Failed to log in as [%s].' % username
            sys.exit(1)

    plan_text, md5 = pc.get_edit_text(plus_hash=True)

    #TODO: get these to match somehow
    #import hashlib
    #print md5
    #print hashlib.md5(plan_text).hexdigest()

    if args.backup_file is False:
        pass
    elif args.backup_file is None:
        # print existing plan to stdout and exit
        print >> sys.stdout, plan_text
        sys.exit()
    elif args.backup_file:
        # save existing plan to file
        fp = open(args.backup_file, 'w')
        fp.write(plan_text)
        fp.close()

    if not args.skip_update:
        # open for external editing
        edited = external_editor(plan_text, suffix='.plan')
        edit_was_made = edited != plan_text

    if args.save_edit and not args.skip_update and edit_was_made:
        # save edited file
        fp = open(args.save_edit, 'w')
        fp.write(edited)
        fp.close()

    if args.skip_update:
        pass
    elif not edit_was_made:
        print >> sys.stderr, 'plan unchanged, aborting update'
    elif args.pretend:
        print >> sys.stderr, "in 'pretend' mode, not really editing"
    else:
        # do the plan update!
        info = pc.set_edit_text(edited, md5)
        print >> sys.stderr, info

    if args.logout:
        os.unlink(cj.filename)
    else:
        # save cookie
        cj.save()

if __name__ == '__main__':
    main()
