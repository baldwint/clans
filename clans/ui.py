#!/usr/bin/env python
"""Command-line Plans."""

import cookielib
import os
import sys
import tempfile
import subprocess
from collections import OrderedDict
from clans.client import PlansConnection, PlansError
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

import clans.fmt
import pkgutil

def find_formatters():
    fmt_location = os.path.dirname(clans.fmt.__file__)
    gen = pkgutil.iter_modules([fmt_location])
    #formatters = dict((name, imp.find_module(name)) for imp,name,_ in gen)
    #return formatters
    names = [name for _, name, _ in gen]
    return names

formatters = find_formatters()

def print_search_results(results, filter_function=None):
    """
    prints search results to stdout.

    :param results: whatever was returned by the ``search_plans``
    method on PlansConnection.

    """
    for un, count, snips in results:
        print ("[{username}]: {0}\n").format(count, username=un)
        for snip in snips:
            if filter_function is not None:
                snip = filter_function(snip)
            print (" - {0}").format(snip)
        print ""

# -----------
# SUBCOMMANDS
# -----------

# these are functions that take two agruments:
#  - a PlansConnection instance
#  - a ClansSession instance

def edit(pc, cs):
    """ plan-editing command """
    plan_text, md5 = pc.get_edit_text(plus_hash=True)

    cs.hook('post_get_edit_text', plan_text)

    if cs.args.skip_update:
        return

    if cs.args.source_file:
        # read input from file
        with open(cs.args.source_file, 'r') as source:
            edited = source.read()
            edited = edited.decode('utf8')
    else:
        # open for external editing
        edited = external_editor(plan_text, suffix='.plan')

    assert type(edited) == unicode
    cs.hook('pre_set_edit_text', edited)

    edit_was_made = edited != plan_text

    if not edit_was_made:
        print >> sys.stderr, 'plan unchanged, aborting update'
    elif cs.args.pretend:
        print >> sys.stderr, "in 'pretend' mode, not really editing"
    else:
        # do the plan update!
        try:
            info = pc.set_edit_text(edited, md5)
            print >> sys.stderr, info
        except PlansError as err:
            print >> sys.stderr, err
            bakfile = '%s.plan.unsubmitted' % cs.username
            with open(bakfile, 'w') as fl:
                fl.write(edited.encode('utf8'))
            print >> sys.stderr, "A copy of your unsubmitted edit" \
                    " was stored in %s" % bakfile

def read(pc, cs):
    """ plan-reading command """
    header, plan = pc.read_plan(cs.args.plan)

    formatter = __import__('clans.fmt.%s' % cs.args.fmt,
                                        fromlist='clans.fmt')

    plan = formatter.filter_html(plan)

    print ("Username: {username}\n"
           "Last Updated: {lastupdated}\n"
           "Last Login: {lastlogin}\n"
           "Name: {planname}\n\n"
           "{plan}").format(plan=plan, **header)

def love(pc, cs):
    """ quicklove command """
    results = pc.search_plans(pc.username, planlove=True)
    formatter = __import__('clans.fmt.%s' % cs.args.fmt,
                                        fromlist='clans.fmt')
    print_search_results(results,
            filter_function=formatter.filter_html)

def search(pc, cs):
    """ search command """
    results = pc.search_plans(cs.args.term, planlove=cs.args.love)
    formatter = __import__('clans.fmt.%s' % cs.args.fmt,
                                        fromlist='clans.fmt')
    print_search_results(results,
            filter_function=formatter.filter_html)

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

        # let extensions modify command list
        self.hook('post_load_commands')

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
        """
        Load Clans extensions.

        reads the config file for extension information, and loads
        extensions as python modules into an ordered dictionary.

        """
        extensions = OrderedDict()
        if self.config.has_section('extensions'):
            for name, path in self.config.items('extensions'):
                try:
                    if path:
                        mod = imp.load_source("clans_ext_%s" % name, path)
                    else:
                        mod = __import__('clans.ext.%s' % name,
                                         fromlist='clans.ext')
                        assert mod.__name__ == 'clans.ext.%s' % name
                except (ImportError, IOError):
                    print >> sys.stderr, 'Failed to load extension "%s".' % name
                else:
                    extensions[name] = mod
        return extensions

    def hook(self, name, *args):
        """
        Call the method named ``name`` in every loaded extension.

        """
        for ext_name, ext in self.extensions.iteritems():
            func = getattr(ext, name, None)
            if func is not None:
                func(self, *args)

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

        # filters: options/arguments for those commands that format text
        filter_parser = argparse.ArgumentParser(add_help=False)
        filter_parser.add_argument(
                '--format', dest='fmt', default='raw',
                choices = formatters,
                help="Display format to use")

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
                '--skip-update', dest='skip_update',
                action='store_true', default=False,
                help="Don't update the plan or open it for editing.")
        commands["edit"].add_argument(
                '--pretend', dest='pretend',
                action='store_true', default=False,
                help="Open plan for editing, but don't actually do the update.")

        # read parser
        commands.add_command(
                'read', read, parents=[global_parser, filter_parser],
                description="Read someone else's plan.",
                help="Print a plan's contents to stdout.",)
        commands["read"].add_argument(
                'plan', default=False, metavar='PLAN',
                help="Name of plan to be read.")

        # quicklove parser
        commands.add_command(
                'love', love, parents=[global_parser, filter_parser],
                description="Search for other users giving you planlove.",
                help="Check quicklove.",)

        # search parser
        commands.add_command(
                'search', search, parents=[global_parser, filter_parser],
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

# -------------
# MAIN FUNCTION
# -------------

def main():
    """
    Initializes ClansSession, connects to plans, then calls subcommand.

    """
    # initialize clans session
    cs = ClansSession()

    # create a cookie
    cookie = cookielib.LWPCookieJar(
            os.path.join(cs.dirs.user_data_dir, '%s.cookie' % cs.username))
    try:
        cookie.load() # this will fail with IOError if it does not exist
    except IOError:
        pass          # no cookie saved for this user

    # create plans connection using cookie
    pc = PlansConnection(cookie, base_url = cs.config.get('login', 'url'))

    if pc.plans_login():
        pass # we're still logged in
    else:
        # we're not logged in, prompt for password if necessary
        password = (cs.args.password or
                getpass("[%s]'s password: " % cs.username))
        success = pc.plans_login(cs.username, password)
        if not success:
            print >> sys.stderr, 'Failed to log in as [%s].' % cs.username
            sys.exit(1)

    # pass execution to the subcommand
    cs.args.func(pc, cs)

    if cs.args.logout:
        os.unlink(cookie.filename)
    else:
        # save cookie
        cookie.save()

if __name__ == '__main__':
    main()
