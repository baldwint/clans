Configuration file (``clans.cfg``)
----------------------------------

Persistent configuration is set in a file called ``clans.cfg``.
The location of this file is reported by::

    $ clans --help

You can go directly to editing the file with::

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

To set your username, create the ``[login]`` section and add a
``username`` entry::

    [login]
    username=baldwint

With this value set, I will no longer have to specify ``-u baldwint``
every time I use clans.

I'm also accustomed to passing ``--format color`` when I read plans. I
can avoid passing this every time by setting ``format=color`` in the
``[clans]`` section. I add the following::

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

