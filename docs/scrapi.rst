ScrAPI
======

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
