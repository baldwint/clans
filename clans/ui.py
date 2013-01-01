#!/usr/bin/env python
"""Command-line Plans."""

import cookielib
import os
import sys
import tempfile
import subprocess
from clans.client import PlansConnection
import getpass as getpass_mod
import argparse
import re

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
        f.write(text.encode('utf8'))
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

    return t.decode('utf8')

def getpass(*args, **kwargs):
    """ version of getpass that works better on py26 """
    password = getpass_mod.getpass(*args, **kwargs)
    if '\x03' in password:
        # http://bugs.python.org/issue11236 (2.6 only)
        raise KeyboardInterrupt('aborted by user')
    return password

class CommandSet(dict):
    """
    Dictionary of subcommands to a program.

    Initialize as you would the main ArgumentParser instance. Access
    the main parser by the `.main` attribute. Individual subcommand
    parsers are keyed by their names in the dictionary.

    """

    def __init__(self, **kwargs):
        self.main = argparse.ArgumentParser(**kwargs)
        self.subparsers = self.main.add_subparsers(
                title = "commands",
                metavar='COMMAND')
        super(CommandSet, self).__init__()

    def add_command(self, name, func, **kwargs):
        """
        Add a new subcommand to a program.

        :param name: name of the command.
        :param func: function implementing command

        Keyword arguments are passed to the ArgumentParser constructor.

        """
        parser = self.subparsers.add_parser(name, **kwargs)
        parser.set_defaults(func=func)
        self[name] = parser

def ttlify(html):
    """
    search and replace certain html tags with ttl equivalents.

    """
    html = re.sub(r'<br ?/?>', '\n', html)
    #TODO: lots of other things
    return html

def print_search_results(results):
    """
    prints search results to stdout.

    :param results: whatever was returned by the ``search_plans``
    method on PlansConnection.

    """
    for un, count, snips in results:
        print "%s: %d" % (un, count)
        for snip in snips:
            print " - %s" % snip
        print ""

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

    if args.backup_file is False:
        pass
    elif args.backup_file is None:
        # print existing plan to stdout and exit
        print >> sys.stdout, plan_text.encode(sys.stdout.encoding or 'utf8')
        sys.exit()
    elif args.backup_file:
        # save existing plan to file
        # NB, there will be no newline at the end of the file
        fp = open(args.backup_file, 'w')
        fp.write(plan_text.encode('utf8'))
        fp.close()

    if args.skip_update:
        return

    if args.source_file:
        # read input from file
        with open(args.source_file, 'r') as source:
            edited = source.read()
            edited = edited.decode('utf8')
    else:
        # open for external editing
        edited = external_editor(plan_text, suffix='.plan')

    edit_was_made = edited != plan_text

    if args.save_edit and edit_was_made:
        # save edited file
        fp = open(args.save_edit, 'w')
        fp.write(edited.encode('utf8'))
        fp.close()

    elif not edit_was_made:
        print >> sys.stderr, 'plan unchanged, aborting update'
    elif args.pretend:
        print >> sys.stderr, "in 'pretend' mode, not really editing"
    else:
        # do the plan update!
        assert type(edited) == unicode
        info = pc.set_edit_text(edited, md5)
        print >> sys.stderr, info

def read(pc, args, config):
    """ plan-reading command """
    header, plan = pc.read_plan(args.plan)

    if args.text:
        plan = ttlify(plan)

    print 'Username: ', header['username']
    print 'Last Updated: ', header['lastupdated']
    print 'Last Login: ', header['lastlogin']
    print 'Name: ', header['planname']
    print ''
    print plan

def love(pc, args, config):
    """ quicklove command """
    results = pc.search_plans(pc.username, planlove=True)
    print_search_results(results)

def search(pc, args, config):
    """ search command """
    results = pc.search_plans(args.term, planlove=args.love)
    print_search_results(results)

# -------------
# CLANS SESSION
# -------------

import ConfigParser
import appdirs
import imp

class ClansSession(object):
    """
    This object is created on each `clans` incantation as a storage
    place for configuration info, command-line arguments, and other
    stuff

    """

    def __init__(self):
        # configure configuration directory/file names.
        self.dirs = appdirs.AppDirs(appname='clans', appauthor='baldwint')
        self.config_loc = os.path.join(self.dirs.user_data_dir, 'clans.cfg')

        # load config, extensions, and define command line args
        self.config = self._load_config()
        self.extensions = self._load_extensions()
        self.commands = self._load_commands()

        # get command line arguments
        self.args = self.commands.main.parse_args()

        # let command line args override equivalent config file settings
        self.username = (self.args.username or
                self.config.get('login', 'username'))

    def _load_config(self):
        # set config file defaults
        config = ConfigParser.ConfigParser()
        config.add_section('login')
        config.set('login', 'username', '')
        config.set('login', 'url', 'http://www.grinnellplans.com')

        # create config directory if it doesn't exist
        try:
            # 0700 for secure-ish cookie storage.
            os.mkdir(self.dirs.user_data_dir, 0700)
        except OSError:
            pass # already exists

        # read user's config file, if present
        config.read(self.config_loc)

        return config

    def _load_extensions(self):
        # load extensions
        if self.config.has_section('extensions'):
            extensions, ext_order = {}, []
            for name, path in self.config.items('extensions'):
                try:
                    if path:
                        mod = imp.load_source("clans_ext_%s" % name, path)
                    else:
                        mod = __import__('clans.ext.%s' % name)
                except (ImportError, IOError):
                    print >> sys.stderr, 'Failed to load extension "%s".' % name
                else:
                    extensions[name] = mod
                    ext_order.append(name)

        return extensions, ext_order

    # TODO hooks into extension modules

    def _load_commands(self):
        # define command line arguments

        # globals: options/arguments inherited by all parsers, including root
        global_parser = argparse.ArgumentParser(add_help=False)

        global_parser.add_argument(
                '-u', '--username',
                dest='username', default='',
                help='GrinnellPlans username, no brackets.')
        global_parser.add_argument(
                '-p', '--password',
                dest='password', default='',
                help='GrinnellPlans password. Omit for secure entry.')
        global_parser.add_argument('--logout', dest='logout',
                            action='store_true', default=False,
                          help='Log out before quitting.')

        # main parser: has subcommands for everything
        commands = CommandSet(
                description= __doc__ + "\n\nconfiguration file:\n  " + self.config_loc,
                parents=[global_parser],
                formatter_class=argparse.RawTextHelpFormatter)

        # edit parser: options/arguments for editing plans
        commands.add_command(
                'edit', edit, parents=[global_parser],
                description='Opens your plan for editing in a text editor.',
                help='Edit your plan in $EDITOR.')
        commands["edit"].add_argument(
                '-f', '--file', dest='source_file',
                default=False, metavar='FILE',
                help="Replace plan with the contents of FILE. "
                "Skips interactive editing.")
        commands["edit"].add_argument(
                '-b', '--backup', dest='backup_file',
                nargs='?', default=False, metavar='FILE',
                help="Backup existing plan to file before editing. "
                "To print to stdout, omit filename.")
        commands["edit"].add_argument(
                '-s', '--save', dest='save_edit',
                default=False, metavar='FILE',
                help='Save a local copy of edited plan before submitting.')
        commands["edit"].add_argument(
                '--skip-update', dest='skip_update',
                action='store_true', default=False,
                help="Don't update the plan or open it for editing.")
        commands["edit"].add_argument(
                '--pretend', dest='pretend',
                action='store_true', default=False,
                help="Open plan for editing, but don't actually do the update.")

        # read parser
        commands.add_command(
                'read', read, parents=[global_parser],
                description="Read someone else's plan.",
                help="Print a plan's contents to stdout.",)
        commands["read"].add_argument(
                'plan', default=False, metavar='PLAN',
                help="Name of plan to be read.")
        commands["read"].add_argument(
                '-t', '--text', dest='text',
                action='store_true', default=False,
                help="Attempt to convert plan to plain text.")

        # quicklove parser
        commands.add_command(
                'love', love, parents=[global_parser],
                description="Search for other users giving you planlove.",
                help="Check quicklove.",)

        # search parser
        commands.add_command(
                'search', search, parents=[global_parser],
                description="Search plans for any word or phrase.",
                help="Search plans for any word or phrase.",)
        commands["search"].add_argument(
                'term', default=False, metavar='TERM',
                help="Term to search for.")
        commands["search"].add_argument(
                '-l', '--love', dest='love',
                action='store_true', default=False,
                help="Restrict search to planlove.")

        return commands

    # plugins down here (later)

# -------------
# MAIN FUNCTION
# -------------

def main():
    """
    Initializes ClansSession, connects to plans, then calls subcommand.

    """
    # initialize clans session
    session = ClansSession()

    # create a cookie
    cookie = cookielib.LWPCookieJar(
            os.path.join(
                session.dirs.user_data_dir,
                '%s.cookie' % session.username))
    try:
        cookie.load() # this will fail with IOError if it does not exist
    except IOError:
        pass          # no cookie saved for this user

    # create plans connection using cookie
    pc = PlansConnection(
            cookie, base_url = session.config.get('login', 'url'))

    if pc.plans_login():
        pass # we're still logged in
    else:
        # we're not logged in, prompt for password if necessary
        password = (session.args.password or
                getpass("[%s]'s password: " % session.username))
        success = pc.plans_login(session.username, password)
        if not success:
            print >> sys.stderr, 'Failed to log in as [%s].' % session.username
            sys.exit(1)

    # pass execution to the subcommand
    session.args.func(pc, session.args, session.config)

    if session.args.logout:
        os.unlink(cookie.filename)
    else:
        # save cookie
        cookie.save()

if __name__ == '__main__':
    main()
