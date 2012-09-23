#!/usr/bin/env python
"""Command-line Plans."""

import cookielib
import os
import sys
import tempfile
import subprocess
from clans.client import PlansConnection

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

# -----------
# SUBCOMMANDS
# -----------

# these are functions that take three agruments:
#  - a PlansConnection instance
#  - a namespace of parsed arguments
#  - a configfile instance.

def edit(pc, args, config):
    """ plan-editing command """
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

    # globals: options/arguments inherited by all parsers, including root
    global_parser = ArgumentParser(add_help=False)

    global_parser.add_argument('-u', '--username', dest='username', default='',
              help='GrinnellPlans username, no brackets.')
    global_parser.add_argument('-p', '--password', dest='password', default='',
              help='GrinnellPlans password. Omit for secure entry.')
    global_parser.add_argument('--logout', dest='logout',
                        action='store_true', default=False,
                      help='Log out before quitting.')

    # main parser: has subcommands for everything
    parser = ArgumentParser(description=__doc__, parents=[global_parser])

    subparsers = parser.add_subparsers(title = "possible commands")

    # edit parser: options/arguments for editing plans
    edit_parser = subparsers.add_parser('edit', parents=[global_parser],
                        description='Opens your plan for editing in a text editor.',
                            help='Edit your plan in $EDITOR.')
    edit_parser.set_defaults(func=edit)
    edit_parser.add_argument('-b', '--backup', dest='backup_file',
                        nargs='?', default=False, metavar='FILE',
              help="""Backup existing plan to file before editing.
                        To print to stdout, omit filename.""")
    edit_parser.add_argument('-s', '--save', dest='save_edit',
                        default=False, metavar='FILE',
              help='Save a local copy of edited plan before submitting.')
    edit_parser.add_argument('--skip-update', dest='skip_update',
                        action='store_true', default=False,
              help="Don't update the plan or open it for editing.")
    edit_parser.add_argument('--pretend', dest='pretend',
                        action='store_true', default=False,
              help="Open plan for editing, but don't actually do the update.")

    # plugins down here (later)

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

    # pass execution to the subcommand
    args.func(pc, args, config)

    if args.logout:
        os.unlink(cj.filename)
    else:
        # save cookie
        cj.save()

if __name__ == '__main__':
    main()
