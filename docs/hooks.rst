Hooks
=====

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

List of Hooks
-------------

.. automodule :: clans.ext.example
    :members:
