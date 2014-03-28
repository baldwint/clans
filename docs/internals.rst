Internals
=========

This section covers technical details of how clans works, in more
detail than you probably want to know. It might be useful if you are
interested in contributing to the clans source, developing an
extension, or writing some other application that will use clans as a
library.

Extension Hooks
---------------

Clans' extension framework is based on `hooks` - named points in the
execution of various commands where it stops to call other
code. Extensions are Python modules that define functions with
names matching one or more of these hooks.

Hooks all accept clans' controller object, ``ClansSession``, as the
first argument. Most are also passed a number of other arguments,
depending on the context. For example, the ``post_search`` hook is
passed the ``ClansSession`` as well as the ``results`` of that search.

To enable a clans extension that you write yourself, make sure the
module is on Python's module search path, so that it's importable via
``import my_clans_extension``. Then, in ``clans.cfg``, add it to the
``[extensions]`` section:

.. code-block:: ini

    [extensions]
    myext=my_clans_extension

On the left side of the equal sign is a casual name for your
extension, and the right should be its importable name, using Python
dot-syntax if necessary.

Some extensions are packaged with clans, like ``clans.ext.newlove``,
and for these it is unnecessary to specify the full importable path.
It is worth looking at the included ``clans.ext.example`` extension to
get an idea of how to write your own.

.. warning ::

    I think I've implemented this in a moderately intelligent way,
    but the hook API should not be considered stable prior to clans 1.0.

List of Hooks
+++++++++++++

.. automodule :: clans.ext.example
    :members:

Plans ScrAPI
------------

Plans does not have a complete API, so clans utilizes a Plans-specific
scraping library to communicate with the Plans server. This is
packaged as a separate sub-module so that it can be used in other
Python programs independent of clans.

.. warning ::

    Code changes on the server side could break the scrAPI at any
    time, so it should not be considered in any way stable.

The entire thing is built around one class, ``PlansConnection``.
Additionally there is the ``PlansError`` exception.
They can be imported like so:

.. code-block:: python

    from clans.scraper import PlansConnection, PlansError

Then we can instantiate a ``PlansConnection``, log into Plans, and begin
doing things:

.. code-block:: python

    pc = PlansConnection()
    pc.plans_login('baldwint', 'not_my_password_lol')
    pc.read_plan('gorp')

Method summary
++++++++++++++

.. autoclass :: clans.scraper.PlansConnection
    :members:

.. autoexception :: clans.scraper.PlansError
    :members:
