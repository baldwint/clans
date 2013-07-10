Extensions
==========

Clans has a hook-based extension framework for adding features on the
client side. Several extensions are already built in, and just need to
be enabled in ``clans.cfg``.

To enable a built-in extension, such as ``newlove``, edit the
``[extensions]`` section of the configuration file with a line like:

.. code-block:: ini

    [extensions]
    newlove=

For information on a specific extension, see below.

Newlove
-------

The ``newlove`` extension tracks the read and unread state of your
planlove, much like Ian Young's greasemonkey script of the same name.
This allows you to easily see what's new in your quicklove.

To enable this extension, add to ``clans.cfg``:

.. code-block:: ini

    [extensions]
    newlove=

With this line enabled, three new flags are added to ``clans love``:


      -t, --time            Order results by time first seen.
      -n, --new             Only show new planlove.
      --keep-unread         Preserve read state of any new planlove.

Now, ``clans love -n`` behaves roughly like the greasemonkey script:
You will only see context snippets that have changed since the last
time you checked. Alternately, ``clans love -t`` will present all past
snippets in chronological order.

Keep in mind that this extension doesn't know when planlove was
*given*, only when you first *received* the love. By default,
``newlove`` marks your planlove as read every time you do ``clans
love``, even if neither of the newlove flags (``-n`` and ``-t``) is
passed. To prevent this, pass ``--keep-unread``.

Your planlove read state is stored in a JSON-formatted file called
``username.love``, in the clans profile directory. When love is
deleted from plans, it is also removed from this file.

Backup
------

The ``backup`` extension adds flags to the ``clans edit`` command to
facilitate making local backups whenever you edit your plan. If your
edit fails, or the plan truncation troll pays a visit to your plan,
you may be able to recover your own lost data.

To enable this extension, add to ``clans.cfg``:

.. code-block:: ini

    [extensions]
    backup=

With this line enabled, three new flags are added to ``clans edit``:


      -b FILE, --backup FILE
                            Backup existing plan to file before editing. To print
                            to stdout, omit filename.
      -s FILE, --save FILE  Save a local copy of edited plan before submitting.
      --skip-update         Don't update the plan or open it for editing.

There are two points at which a backup may be made: before and after
you make your edits. To backup your plan as it existed on the server
prior to your editing it, use ``-b``. To backup your plan as it
existed in your text editor before submitting, use ``-s``. It doesn't
hurt to use both.

Both flags take a filename argument for the backed-up plan. In the
case of ``-b``, you can omit this and the plan will be piped to
standard output - but depending on your operating system, this might
not preserve character encodings very well.

To avoid specifying ``-b`` and ``-s`` flags all the time, add to
``clans.cfg``:

.. code-block:: ini

    [backup]                                                                    
    backup_file=/path/to/plan_backup.txt                        
    save_edit=/path/to/edited_plan.txt                        

and your plan will be backed up to these files every time you edit.
Keep in mind that these files will only store the most recent copy of
your plan. To keep editions going back several edits, you will need to
backup the backup with some other software. I just place them in a
folder where they are automatically backed up with the rest of my
system files.

The ``--skip-update`` flag forces ``clans edit`` to quit before
opening an interactive editor. When used in combination with ``-b``,
this is useful for automating your plan backups:

.. code-block:: console

    $ clans edit --skip-update -b [FILE]

is an idiom for grabbing your current edit field text.
