#!/usr/bin/env python
"""Command-line Plans."""

from __future__ import print_function

import os
import sys
if sys.version_info >= (3,3):
    from http.cookiejar import LWPCookieJar
elif sys.version_info < 3:
    #str = unicode
    #from cookielib import LWPCookieJar
    pass
elif sys.version_info >= 3:
    sys.stderr.write('Clans requires Python 3.3+')
    sys.exit(1)


import tempfile
import subprocess
import pydoc
from clans.scraper import PlansConnection, PlansError
import getpass as getpass_mod
import argparse
import clans.fmt

if sys.version_info >= (2, 7):
    from collections import OrderedDict
elif sys.version_info >= (2, 6):
    from ordereddict import OrderedDict
else:
    sys.stderr.write('Clans requires Python 2.6 or 2.7')
    sys.exit(1)


# ----------
# UI HELPERS
# ----------


def external_editor(text, editor=None, **kwargs):
    """
    Open some text for editing by the user.

    specify 'editor' to choose which editor to use

    Keyword arguments are passed to the tempfile constructor.

    """
    if 'text' not in kwargs:
        kwargs['text'] = True

    if editor is None:  # default to $EDITOR, or pico
        editor = os.environ.get('EDITOR', 'pico')

    fd, name = tempfile.mkstemp(**kwargs)  # make tempfile
    try:
        # populate the temp file with original text.
        with os.fdopen(fd, 'w') as f:
            f.write(text.encode('utf8'))

        # open in editor and wait for user to quit
        subprocess.call([editor, name])

        # retrieve edited text
        with open(name) as f:
            t = f.read()
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


def pager(text):
    """ unicode version of pager for py2 """
    if sys.version_info < (3,):
        # convert to bytestring
        text = text.encode('utf8')
    pydoc.pager(text)


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
            title="commands",
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


# -----------
# SUBCOMMANDS
# -----------

# these are functions that take one argument:
#  - a ClansSession instance

# the ClansSession instance is the `controller` type object, since it
# knows all the configuration, extension, and command line argument
# information. It knows how to initialize a PlansConnection (via
# the `make_plans_connection` method) or an output formatter (via the
# `make_formatter` method). These I think of as the `model` and `view`
# type objects, respectively.

# the pattern I follow below is to have subcommand functions take
# PlansConnection and formatter type objects as optional keyword
# arguments, and have the mandatory ClansSession argument initialize
# those if they are not provided. This approach permits these objects
# (or mock objects standing in for them) to be passed directly in
# testing. This is called dependency injection


def edit(cs, pc=None):
    """ plan-editing command """
    pc = pc or cs.make_plans_connection()

    plan_text, md5 = pc.get_edit_text(plus_hash=True)
    cs.hook('post_get_edit_text', plan_text)

    if cs.args.source_file:
        # read input from file
        with open(cs.args.source_file, 'r') as source:
            edited = source.read()
            edited = edited.decode('utf8')
    else:
        # open for external editing
        editor = cs.config.get('clans', 'editor')
        edited = external_editor(plan_text, editor=editor, suffix='.plan')

    assert type(edited) == str
    cs.hook('pre_set_edit_text', edited)

    edit_was_made = edited != plan_text

    if not edit_was_made:
        print('plan unchanged, aborting update', file=sys.stderr)
    else:
        # do the plan update!
        try:
            info = pc.set_edit_text(edited, md5)
            print(info, file=sys.stderr)
        except PlansError as err:
            print(err, file=sys.stderr)
            bakfile = '%s.plan.unsubmitted' % cs.username
            with open(bakfile, 'w') as fl:
                fl.write(edited.encode('utf8'))
            print("A copy of your unsubmitted edit"
                  " was stored in %s" % bakfile, file=sys.stderr)


def read(cs, pc=None, fmt=None):
    """ plan-reading command """
    pc = pc or cs.make_plans_connection()
    fmt = fmt or cs.make_formatter()

    try:
        header, plan = pc.read_plan(cs.args.plan)
    except PlansError as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    plan = fmt.filter_html(plan)
    pager(fmt.format_plan(plan=plan, **header))


def autoread(cs, pc=None, fmt=None):
    """ autoread list command """
    pc = pc or cs.make_plans_connection()
    fmt = fmt or cs.make_formatter()

    results = pc.get_autofinger()
    fmt.print_autoread(results)


def love(cs, pc=None, fmt=None):
    """ quicklove command """
    pc = pc or cs.make_plans_connection()
    fmt = fmt or cs.make_formatter()

    cs.hook('pre_search', pc.username, planlove=True)
    results = pc.search_plans(pc.username, planlove=True)
    cs.hook('post_search', results)
    fmt.print_search_results(results)


def search(cs, pc=None, fmt=None):
    """ search command """
    pc = pc or cs.make_plans_connection()
    fmt = fmt or cs.make_formatter()

    cs.hook('pre_search', cs.args.term, planlove=cs.args.love)
    results = pc.search_plans(cs.args.term, planlove=cs.args.love)
    cs.hook('post_search', results)
    fmt.print_search_results(results)


def watch(cs, pc=None, fmt=None):
    """ planwatch command """
    pc = pc or cs.make_plans_connection()
    fmt = fmt or cs.make_formatter()

    results = pc.planwatch(cs.args.hours)
    fmt.print_list([un for un,t in results])


def config(cs):
    """ config command """
    if cs.args.profile_dir:
        print(cs.profile_dir)
    else:
        subprocess.call([cs.config.get('clans', 'editor'), cs.config_loc])

# -------------
# CLANS SESSION
# -------------

if sys.version_info >= (3,3):
    from configparser import ConfigParser
elif sys.version_info < 3:
    #from ConfigParser import ConfigParser
    pass

import appdirs
import importlib


class ClansSession(object):
    """
    This object is created on each `clans` incantation as a storage
    place for configuration info, command-line arguments, and other
    stuff

    """

    def __init__(self, profile_dir=None):
        # profile folder: either passed directly (for testing only),
        # set by CLANS_DIR environment variable, or the standard user
        # data directory for this OS
        self.profile_dir = profile_dir or (
            os.environ.get('CLANS_DIR', '')
            or appdirs.user_data_dir(appname='clans',
                                     appauthor='baldwint'))

        # config file location: in data directory
        self.config_loc = os.path.join(self.profile_dir, 'clans.cfg')

        # load config, extensions, and define command line args
        self.config = self._load_config()
        self.extensions = self._load_extensions()
        self.formatters = self._load_formatters()
        self.commands = self._load_commands()

        # let extensions modify command list
        self.hook('post_load_commands')

    def run(self, argv=None):
        """
        Clans main function, run with specified arguments

        """
        # get command line arguments
        self.args = self.commands.main.parse_args(argv)

        # let command line args override equivalent config file settings
        self.username = (self.args.username or
                         self.config.get('login', 'username'))

        try:
            # pass execution to the subcommand
            self.args.func(self)
        finally:
            # do this part always, even if subcommand fails
            self.finish()

    def _load_config(self):
        # set config file defaults
        config = ConfigParser()
        config.add_section('login')
        config.set('login', 'username', '')
        config.set('login', 'url', 'http://www.grinnellplans.com')
        config.add_section('clans')
        # text editor: either specified in config file, or $EDITOR, or pico
        config.set('clans', 'editor', os.environ.get('EDITOR', 'pico'))
        config.set('clans', 'format', 'raw')

        # create profile directory if it doesn't exist
        try:
            # 0700 for secure-ish cookie storage.
            os.makedirs(self.profile_dir, 0o700)
        except OSError:
            pass  # already exists

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
                    if not path:
                        # if no value is specified,
                        # assume it is for a built-in extension
                        path = 'clans.ext.%s' % name
                    mod = importlib.import_module(path)
                    assert mod.__name__ == path
                except ImportError:
                    print('Failed to load extension "%s".' % name,
                          file=sys.stderr)
                else:
                    extensions[name] = mod
        return extensions

    def _load_formatters(self):
        """
        Load output formatters.

        """
        formatters = {
            'raw': clans.fmt.RawFormatter,
            'text': clans.fmt.TextFormatter,
            'color': clans.fmt.ColorFormatter,
            }
        return formatters

    def hook(self, name, *args, **kwargs):
        """
        Call the method named ``name`` in every loaded extension.

        """
        for ext_name, ext in self.extensions.items():
            func = getattr(ext, name, None)
            if func is not None:
                func(self, *args, **kwargs)

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
        global_parser.add_argument(
            '--logout', dest='logout',
            action='store_true', default=False,
            help='Log out before quitting.')

        # filters: options/arguments for those commands that format text
        filter_parser = argparse.ArgumentParser(add_help=False)
        filter_parser.add_argument(
            '--format', dest='fmt',
            default=self.config.get('clans', 'format'),
            choices=self.formatters,
            help="Display format to use")

        # main parser: has subcommands for everything
        commands = CommandSet(
            description=__doc__,
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

        # read parser
        commands.add_command(
            'read', read, parents=[global_parser, filter_parser],
            description="Read someone else's plan.",
            help="Print a plan's contents to stdout.",)
        commands["read"].add_argument(
            'plan', default=False, metavar='PLAN',
            help="Name of plan to be read.")

        # autoread list parser
        commands.add_command(
            'list', autoread, parents=[global_parser, filter_parser],
            description="Autoread list",
            help="Check unread plans",)

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

        # watch parser
        commands.add_command(
            'watch', watch, parents=[global_parser, filter_parser],
            description="See recently updated plans.",
            help="See recently updated plans.",)
        commands["watch"].add_argument(
            'hours', type=int, nargs='?',
            default=12, metavar='HOURS',
            help="Specify how many hours' worth of plan updates to show.")

        # config parser
        commands.add_command(
            'config', config, parents=[global_parser, filter_parser],
            description="The clans config file sets the default"
            " behavior of the client."
            " (Not to be confused with Plans preferences!)",
            help="Edit clans configuration file.")
        commands["config"].add_argument(
            '--dir', dest='profile_dir',
            action='store_true', default=False,
            help="Print the path to the clans profile directory.")

        return commands

    def make_plans_connection(self):
        """
        Connects to plans, prompting for passwords if necessary

        """
        # create a cookie
        self.cookie = LWPCookieJar(
            os.path.join(self.profile_dir, '%s.cookie' % self.username))
        try:
            self.cookie.load()  # fails with IOError if it does not exist
        except IOError:
            pass                # no cookie saved for this user

        # create plans connection using cookie
        pc = PlansConnection(self.cookie,
                             base_url=self.config.get('login', 'url'))

        if pc.plans_login():
            pass           # we're still logged in
        else:
            # we're not logged in, prompt for password if necessary
            password = (self.args.password or
                        getpass("[%s]'s password: " % self.username))
            success = pc.plans_login(self.username, password)
            if not success:
                print('Failed to log in as [%s].' % self.username,
                      file=sys.stderr)
                sys.exit(1)

        return pc

    def make_formatter(self):
        """
        Initialize and return the appropriate output formatter.

        """
        Fmt = self.formatters[self.args.fmt]
        fmt = Fmt()
        return fmt

    def finish(self):
        """
        Cookie-related cleanup.

        Either save the updated cookie, or delete it to log out

        """
        if not hasattr(self, 'cookie'):
            return  # no plans connection was made
        elif self.args.logout:
            os.unlink(self.cookie.filename)
        else:
            # save cookie
            self.cookie.save()


def main():
    cs = ClansSession()
    cs.run()

if __name__ == '__main__':
    main()
