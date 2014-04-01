Installation
============

To install clans, you'll need the following:

 - A Unix-like operating system (e.g. Linux or Mac OS X)
 - Python 2.6+ or 3.3+ (usually preinstalled)
 - The pip_ installer

In addition, clans will only work with Plans accounts that are set to
use the **postmodern** interface.

.. _pip: http://www.pip-installer.org/

Stable version
--------------

Most people will want to use the latest stable release.
This installs clans and its dependencies:

.. code-block:: console

    $ pip install clans

If a newer version is available later, update to it with:

.. code-block:: console

    $ pip install --upgrade clans

To uninstall:

.. code-block:: console

    $ pip uninstall clans

Development version
-------------------

Clans development is versioned using Git_. To clone the repository and
install it in a single step:

.. code-block:: console

    $ pip install -e https://github.com/baldwint/clans.git#egg=clans

This installs clans in *editable* mode - it clones the repository into your
``src`` directory and configures Python to load it from there.

It is a good idea to work inside a virtualenv_ to keep things
separate from stable versions of clans on the same machine. I use
the virtualenvwrapper_ tool to do that. Using this, I would first do

.. code-block:: console

    $ mkvirtualenv clans

and then do the installation step. Then the repository would be
cloned into ``~/.virtualenvs/clans/src/clans``, but the installation
is only active if I first activate the virtualenv using ``workon clans``.

As an optional step, install extra dependencies for testing and
documentation:

.. code-block:: console

    $ cd ~/.virtualenvs/clans/src/clans
    $ pip install -e .[docs,tests]

.. _Git: http://git-scm.com/
.. _pip: http://www.pip-installer.org/
.. _virtualenv: http://www.virtualenv.org/
.. _virtualenvwrapper: http://virtualenvwrapper.readthedocs.org/

Getting updates and sharing improvements
++++++++++++++++++++++++++++++++++++++++

To get updates, ``cd`` to the repository and do:

.. code-block:: console

    $ git pull

You can make your own modifications to clans by editing the Python
source code in the repository. If you like, you can commit your
changes using Git and contribute them back to the project.

The first step is to publish your modifications. To do this, fork the
project on GitHub and add it as a remote in your local copy:

.. code-block:: console

    $ git remote add myfork https://github.com/your_username/clans.git

Now you can publish changes you made locally using ``git push myfork
master`` (although it is often a good idea to work in branches other
than ``master``). To submit your changes for review, open a pull
request on GitHub.
