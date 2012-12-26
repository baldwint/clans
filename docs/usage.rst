General Usage
=============

Clans has a variety of functions that can are invoked as subcommands
of the ``clans`` executable, like::

    $ clans edit

Supported commands are:

    ``edit``
        Edit your plan in $EDITOR.
    ``read``
        Print a plan's contents to stdout.

For help on a specific command, run::

    $ clans edit --help

Command-line options
--------------------

Each command accepts its own set of arguments and option flags. Some
option flags are accepted by all commands, because they handle
authentication:

    -u USERNAME, --username USERNAME  GrinnellPlans username, no brackets.
    -p PASSWORD, --password PASSWORD  GrinnellPlans password.
                                      Omit for secure entry.
    --logout                          Log out before quitting.

The ``--username`` and ``--password`` flags are used to authenticate
with the Plans server. If ``--password`` is not given, and is
required, you will be prompted to enter your password securely.

Authentications generally expire on the server side after two days of
inactivity, unless ``--logout`` is given, in which case the
authentication will expire immediately after the command completes.

``clans`` stores active authentications, but will only use them if
``--username`` is specified on the command line, or a default username has
been set in clans.cfg. This permits having multiple concurrent Plans logins.

.. Authentications are stored as ``USERNAME.cookie`` in a
.. system-dependent location.

In addition, all clans commands accept a ``--help`` option.

Configuration file (``clans.cfg``)
----------------------------------

Persistent configuration is set in a file called ``clans.cfg``.
The location of this file is reported by::

    $ clans --help

``clans.cfg`` follows the ConfigParser_ syntax: essentially, it
consists of sections, each led by a ``[section]``
header and followed by ``name: value`` or ``name=value`` entries.

The ``[login]`` section sets options to do with authentication. The
following configuration options may be set:

:username: sets a default value for the ``--username`` flag, if it is
           not specified.
:url:      sets the location of the Plans service to use for login.
           Defaults to ``http://www.grinnellplans.com``.

For example, my ``clans.cfg`` contains::

    [login]
    username=baldwint
    #url=http://localhost/~tkb/plans/

The middle line saves me from having to specify ``-u baldwint`` every
time I use clans.
The last line, which is commented out in this example, gives the
location of my local GrinnellPlans development server. I uncomment
this from time to time for testing purposes.

.. _ConfigParser: http://docs.python.org/2/library/configparser.html

