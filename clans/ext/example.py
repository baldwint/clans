"""
Example extension for clans.

This extension implements every available hook as a no-op.

Each hook accepts one or more (usually mutable) arguments, and
returns nothing. Typically, arguments can be modified in-place or left
untouched.

The first argument passed is always the :class:`ClansSession` object.

"""

# Extensions get run as a script as soon as they are loaded. To have
# your extension do something as soon as possible, put it here.

import sys
print >> sys.stderr, 'Hello World!'

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

    """
    # for kicks, demonstrate storing variables
    storage['foo'] = 'bar'
    pass

def pre_set_edit_text(cs, edited):
    """
    This hook is called during plan editing, after the edit text has
    been modified, but before being submitted to the server

    The modified edit text is passed as an immutable unicode string as
    the second argument.

    """
    # retrieve value stored in a previous hook
    assert storage['foo'] == 'bar'
    pass
