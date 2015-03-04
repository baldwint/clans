Configuration
-------------

Clans stores configuration information and other data
(login cookies, newlove read state, etc.)
in its *profile directory*.
The path to this directory is reported by:

.. code-block:: console

    $ clans config --dir

By default, this is a folder inside your operating system's designated
place for application data, but it can also be set using the
``$CLANS_DIR`` environment variable.

Persistent configuration is set in a file called ``clans.cfg``,
in the clans profile directory.
You can go directly to editing the configuration file with:

.. code-block:: console

    $ clans config

``clans.cfg`` follows the ConfigParser_ syntax: essentially, it
consists of sections, each led by a ``[section]``
header and followed by ``name: value`` or ``name=value`` entries.

.. _ConfigParser: http://docs.python.org/2/library/configparser.html

Getting started
++++++++++

You will probably want to set at least two values in the
configuration file:

 - your username
 - your preferred output format

.. _config-username:

To set your username, create the ``[login]`` section and add a
``username`` entry:

.. code-block:: ini

    [login]
    username=baldwint

With this value set, I will no longer have to specify ``-u baldwint``
every time I use clans.

.. _config-formatter:

I'm also accustomed to passing ``--format color`` when I read plans. I
can avoid passing this every time by setting ``format=color`` in the
``[clans]`` section. I add the following:

.. code-block:: ini

    [clans]
    format=color

Now clans will always make colorized output, unless I specify
otherwise.

By section
++++++++++

The ``[login]`` section sets options to do with authentication. The
following configuration options may be set:

:username: sets a default value for the ``--username`` flag, if it is
           not specified.
:url:      sets the location of the Plans service to use for login.
           Defaults to ``https://www.grinnellplans.com``.

The ``[clans]`` section controls how the command-line client behaves.

:format:   sets a default value for the ``--format`` flag, if it is
           not specified.
:editor:   sets which editor to use when editing your plan, in case
           you want to use one other than is set by the ``EDITOR``
           environment variable.
:timezone: timezone to use for displaying dates and times, specified
           as its name in the Olson tz database. Defaults to your
           local timezone (for text output) or UTC (for JSON output).
:date_format: format string for dates and times, specified in the
              `Unicode style`_. JSON output ignores this option and
              will always use the ISO 8601 format.

.. _`Unicode style`: http://unicode.org/reports/tr35/tr35-dates.html#Date_Format_Patterns
