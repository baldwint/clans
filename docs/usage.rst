Usage
=====

To get an overview of available Clans commands, run:: 

    $ clans --help

To get help on a specific subcommand, like ``edit``, run::

    $ clans edit --help

This will list all available arguments and option flags.

Logging in
----------

All commands share several option flags related to authentication with
the GrinnellPlans server:

    -u USERNAME, --username USERNAME  GrinnellPlans username, no brackets.
    -p PASSWORD, --password PASSWORD  GrinnellPlans password.
                                      Omit for secure entry.
    --logout                          Log out before quitting.

By default, you must specify your username with ``-u`` for every
``clans`` incantation::

    $ clans -u baldwint read portland

This can be avoided by :ref:`setting a default username <config-username>`
in clans.cfg.

It is *not* necessary to specify ``--password`` each time.
In fact, it is a good idea to omit this flag as a rule.
If your password is required, you will be prompted for it.

.. note ::

    ``clans`` stores active authentications, but will only use them if
    ``--username`` is specified on the command line, or a default
    username has been set in clans.cfg. This permits having multiple
    concurrent Plans logins.

Authentications generally expire on the server side after two days of
inactivity, unless ``--logout`` is given, in which case the
authentication token will be deleted immediately after the command completes.

In addition, all commands accept a ``--help`` option.

Reading Plans
-------------

To see what's new on your autoread list::

    $ clans list

This returns a list of plans on your autoread lists that have been
updated since you last read them.

To read a plan, use the ``read`` subcommand::

    $ clans read <planname>

This displays the contents of the specified plan in a pager application in
HTML format. It's normally easier to read plain text, though::

    $ clans read <planname> --format text

This formats the plan as plain text before displaying it.
Run ``clans read --help`` for a list of available formatters. You can
:ref:`configure a default formatter <config-formatter>` in clans.cfg.

Searching Plans and Quicklove
-----------------------------

To search plans, use::

    $ clans search <term>

This returns a lists of plans containing the search term, and a little
context. To restrict search to a planlove, use the ``--love``
flag::

    $ clans search --love <planname>

Searching for love of your own username ("quicklove") gets a shortcut::

    $ clans love

Editing Plans
-------------

To edit your own plan::

    $ clans edit

This opens your plan for editing in a text editor.
Clans decides which editor to use based on the following:

 1. The ``editor`` value configured in clans.cfg
 2. Failing that, the value of the ``$EDITOR`` environment variable
 3. Failing that, ``less``.

To submit your update, save and close the file. To cancel the update,
quit from the editor without saving.



