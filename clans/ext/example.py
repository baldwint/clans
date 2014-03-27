# Example extension for clans, used for documentation.
# Should implement every available hook as a no-op.

"""
Each hook accepts one or more (usually mutable) arguments, and
need not return anything. Typically, arguments can be modified
in-place or left untouched.

The first argument passed is always the :class:`ClansSession` object.

"""

from __future__ import print_function

# Extensions get run as a script as soon as they are loaded. To have
# your extension do something as soon as possible, put it here.

import sys
print('Hello World!', file=sys.stderr)

# a common task is to initialize some mutable types here, so that our
# extension can save data in one hook and refer to it when a later
# hook is called.

storage = {}

# of course, this variable only lasts as long as clans is running. To
# store data between runtimes, you'll need to write out to files.


def post_load_commands(cs):
    """
    This hook is called right after the standard commands and
    arguments are defined.

    This hook is a good place to add arguments or subcommands to the
    command table, which you can do by modifying the ``commands``
    attribute of ``cs``.

    For example, to add an argument to an existing command::

        cs.commands['love'].add_argument(
                   '-t', '--time', dest='time',
                   action='store_true', default=False,
                   help="Order results by time first seen.")

    or, to add a whole new command::

        cs.commands.add_command(
                   'secrets', secrets, parents=[global_parser],
                   description='Glimpse into the souls of others.',
                   help='View secrets.')

    where ``secrets`` is a function you define elsewhere in your
    extension.

    """
    #TODO: extensions need access to global_parser
    pass


def post_get_edit_text(cs, plan_text):
    """
    This hook is called during plan editing, after the edit text has
    been retrieved from the server.

    The edit text is passed as an immutable unicode string as the
    second argument.

    If this hook returns any value other than ``None``, clans will skip
    interactive editing.

    """
    # for kicks, demonstrate storing variables
    storage['foo'] = 'bar'
    pass


def pre_set_edit_text(cs, edited):
    """
    This hook is called during plan editing, after the edit text has
    been modified, but before being submitted to the server.

    The modified edit text is passed as an immutable unicode string as
    the second argument.

    """
    # retrieve value stored in a previous hook
    assert storage['foo'] == 'bar'
    pass


def pre_search(cs, term, planlove):
    """
    This hook is called before a (quicklove or regular) search, and is
    passed the same arguments as is the search function:

     - the search ``term``
     - ``planlove``, a boolean of whether to restrict search to planlove.

    """
    pass


def post_search(cs, results):
    """
    This hook is called after a (quicklove or regular) search, and is
    passed a list containing the results.

    Elements of this list are 3-tuples:

     - the name of the plan on which the term was found (str)
     - the number of instances found (int)
     - a list of snippets.

    Note that the snippet list may not be the same length as the
    number of instances found.

    Lists are mutable, so results may be filtered by modifying this
    list in-place.

    """
    pass
