Cookbook
========

Some common clans workflows.

New planlove notifications
--------------------------

Rather than checking planlove compulsively throughout the day, we can
schedule a cron job that runs ``clans love`` at a reasonable interval,
and emails us when there is something new.

For this we should install Clans on a machine that is on all the time,
and has a mail server installed. We will need to be able to send mail
from the command line using ``mail``, which usually works like so:

.. code-block:: console

    $ echo "Hello world!" | mail -s 'subject' not-my-email@baldwint.com

After verifying that I can send email to myself using this method, I
install clans on the server and configure ``clans.cfg`` like so:

.. code-block:: ini

    [login]
    username=baldwint
    [clans]
    format=text
    [extensions]
    newlove=

This enables the ``newlove`` extension, which filters the output of
``clans love`` to only show unread planlove when I do:

.. code-block:: console

    $ clans love -tn

The ``-n`` limits output to new planlove. The ``-t`` flag is for
time-ordering, which we only need because it makes the command's
output blank when there is no new love.

I write a script, ``lovenotify.sh``, which pipes the output into an
email if it's not blank:

.. code-block:: bash

    #!/bin/bash

    LOVE=`clans love -tn`;

    if [ -n "$LOVE" ]; then
        echo "$LOVE" | mail -s 'new planlove' not-my-email@baldwint.com
    fi

I make it executable (``chmod +x lovenotify.sh``) and make an entry in
my crontab::

    00 * * * * path/to/lovenotify.sh

This will run the script every hour on the hour. If you're less
obsessive than me, you might prefer to run it less frequently::

    00 */3 * * * path/to/lovenotify.sh # every 3 hours
    00 */6 * * * path/to/lovenotify.sh # every 6 hours
    00 08 * * * path/to/lovenotify.sh # every morning at 8

Please try not to cook the plans server by hitting your planlove every
minute. On the other hand, don't schedule it less often than once per
day, since plans will log you out after 2 days of inactivity.


Using clans on multitple computers
----------------------------------

If you use multiple computers, you can sync clans data between them
using a service such as Dropbox.

By default, clans stores its data in its *profile directory*. This
contains the ``clans.cfg`` file as well as other data (login cookies,
newlove read state, etc.). By symlinking this directory into your
Dropbox, the configuration file and all other data can be shared by
your clans installations.

The profile directory location is reported by ``clans --help``.
On Mac OS X, this turns out to be ``~/Library/Application\
Support/clans``. Move it, and leave a symlink in its place:

.. code-block:: console

    $ mv -r ~/Library/Application\ Support/clans ~/Dropbox/clansdata
    $ ln -s ~/Dropbox/clansdata ~/Library/Application\ Support/clans

Then repeat the second step on any synced computer with which you
would like to share settings.

   .. warning ::

      Anyone with read access to the clans data directory may
      be able to log into plans as you. For this reason, it has 700
      permissions by default, but *Dropbox does not sync this*.

      It is a good idea to remain logged out until you can do::

          chmod 700 ~/Dropbox/clansdata

      on all computers synced by your Dropbox. Consider using `selective
      sync`_ to limit which computers your login token is stored on.

      .. _`selective sync`: https://www.dropbox.com/help/175/en


Using clans with an alternate Plans
-----------------------------------

By default, clans communicates with the installation of Plans running
at http://www.grinnellplans.com/. It can also talk to other
installations, such as one running on your local development server.

The ``url`` setting in the ``[login]`` section of ``clans.cfg``
can be used to change which Plans we are talking to. However,
switching this back and forth can have unexpected consequences (for
example, when using the newlove extension, it will erase my read
state).

It is better to create an entirely separate profile directory, and use
the ``CLANS_DIR`` environment variable to control which one clans uses.

.. code-block:: console

    $ mkdir localhost.clansprofile
    $ nano localhost.clansprofile/clans.cfg

You can name this directory whatever you want (It doesn't have to have a
``.clansprofile`` extension, that just helps me remember what it is).
In this new ``clans.cfg`` file, define the location of the development
server and whatever other settings you want to use:

.. code-block:: ini

    [login]
    username=baldwint
    url=http://localhost/~tkb/plans/

Then, to switch between profiles, do

.. code-block:: console

    $ export CLANS_DIR=path/to/localhost.clansprofile

To switch back to the default profile:

.. code-block:: console

    $ export CLANS_DIR=

