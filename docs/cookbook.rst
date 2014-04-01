Cookbook
========

In addition to providing an alternate user interface for Plans,
clans can be used as a utility to achieve functionality not built into
Plans itself. Here are some examples.

New planlove notifications
--------------------------

Rather than checking planlove compulsively throughout the day, we can
schedule a cron job that runs ``clans love`` at a reasonable interval,
and emails us when there is something new.

For this we should install clans on a machine that is on all the time,
and has a mail server installed. We will need to be able to send mail
from the command line using ``mail``, which usually works like so:

.. code-block:: console

    $ echo "Hello world!" | mail -s 'subject' username@grinnell.edu

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

    CLANS='/full/path/to/clans'
    LOVE=`$CLANS love -tn`;

    if [ -n "$LOVE" ]; then
        echo "$LOVE" | mail -s 'new planlove' username@grinnell.edu
    fi

I make it executable (``chmod +x lovenotify.sh``) and make an entry in
my crontab::

    00 * * * * path/to/lovenotify.sh

This will run the script every hour on the hour. If you're less
obsessive than me, you might prefer to run it less frequently::

    00 */3 * * * path/to/lovenotify.sh # every 3 hours
    00 */6 * * * path/to/lovenotify.sh # every 6 hours
    48 07 * * * path/to/lovenotify.sh # every morning at 7:48

Please try not to cook the plans server by hitting your planlove every
minute. On the other hand, don't schedule it less often than once per
day, since plans will log you out after 2 days of inactivity.


Automated plan backups
----------------------

With the :ref:`backup extension <backup-extension>`, clans can be
configured to save a local copy of the plan every time we invoke
``clans edit``. But it would be nice for this to also back up edits
done on the web site, and it would be extra helpful to keep a
versioned history of every edit we have ever made. We can achieve this
by scheduling another job on the same server we used to run the
newlove notifications.

First, I add ``backup=`` to the ``[extensions]`` section of ``clans.cfg``
to enable the extension. Next, I create a folder ``plans_backups``
in my home directory, which will contain my first plans backup:

.. code-block:: console

    $ mkdir plans_backups
    $ cd plans_backups
    $ clans edit --skip-update --b baldwint.txt

Now I put the directory under version control. I use git, which is
total overkill, but is familiar to me:

.. code-block:: console

    $ git init
    $ git add baldwint.txt
    $ git commit -m "initial commit"

Finally I schedule a cron job to periodically run the following script:

.. code-block:: bash

    #!/bin/bash

    CLANS='/full/path/to/clans'

    REPO="full/path/to/plans_backups"
    BAKFILE="$REPO/baldwint.txt"

    $CLANS edit --skip-update -b $BAKFILE

    (cd $REPO && git commit -am "Automated commit `date`" >> /dev/null)

This backs up and commits a version of my plan every time it is run.
Usually, the plan will not have changed since the last time the script
was run, in which case the call to ``git commit`` will fail. That's
expected, so I silence its output by piping to ``/dev/null``.


Scheduling a plan update
------------------------

If you have in mind a hilarious April Fool's day joke to post on your
plan, but will be away from the computer on that day, you can prepare
it ahead of time and schedule clans to submit it at the proper time.

First copy the contents of your existing plan into a text file.
This is straightforward to do with the :ref:`backup extension
<backup-extension>` enabled:

.. code-block:: console

    $ clans edit --skip-update --backup myplan.txt

Now edit and re-save this file so that it includes the desired update.
The command we should give to our task scheduler to run on the morning
of April 1 is:

.. code-block:: console

    $ clans edit --from-file myplan.txt

We could use ``cron`` to schedule this, as we did in the previous
examples, or some equivalent thereof. I did this on a Mac, using
``launchd``, and the following LaunchAgent:

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
        <key>Label</key>
        <string>clans.edit</string>
        <key>ProgramArguments</key>
        <array>
            <string>/Users/tkb/bin/clans</string>
            <string>edit</string>
            <string>--from-file</string>
            <string>/Users/tkb/myplan.txt</string>
        </array>
        <key>StartCalendarInterval</key>
        <dict>
            <key>Day</key>
            <integer>1</integer>
            <key>Hour</key>
            <integer>7</integer>
            <key>Minute</key>
            <integer>48</integer>
        </dict>
    </dict>
    </plist>

This schedules the job to run at 7:48 AM on the 1st of the month.
Note that:

 - I used the ``/full/path/to/clans`` and
   ``/full/path/to/myplan.txt``, so the agent can run outside the
   environment defined by my shell.
 - Any change I make to the plan before the job runs will be
   overwritten when it eventually does.
 - This job will actually run on the 1st of `every` month, so I'll
   need to remember to disable it before the 1st of May.

Loading LaunchAgents by hand is super-cumbersome, so I usually use the
Lingon_ app to schedule them.

.. _Lingon: http://www.peterborgapps.com/lingon/


Using clans on multitple computers
----------------------------------

If you use multiple computers, you can sync clans data between them
using a service such as Dropbox.

By default, clans stores its data in its *profile directory*. This
contains the ``clans.cfg`` file as well as other data (login cookies,
newlove read state, etc.). By symlinking this directory into your
Dropbox, the configuration file and all other data can be shared by
your clans installations.

The profile directory location is reported by ``clans config --dir``.
Move it, and leave a symlink in its place:

.. code-block:: console

    $ mv -r "`clans config --dir`" ~/Dropbox/clansdata
    $ ln -s ~/Dropbox/clansdata "`clans config --dir`"

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


Using an alternate Plans server
-------------------------------

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
``.clansprofile`` extension, but this helps me remember what it is).
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

