Installation
============

``clans`` is still in development, and there have been no versioned
releases. To use it, you will need to check out a copy from the
development repository using Git_.

Installing from source repo
---------------------------

To check out and install clans in a single step, use pip_:

.. code-block:: console

    $ pip install --user -e git+/path/to/clans.git#egg=clans

This installs clans, along with several of its dependencies.
If you omit ``--user``, you may need to prefix this with ``sudo``.
This flag is unnecessary if you have some other means of organizing
python modules in your home directory (e.g., working in a virtualenv_).

As an optional step, install Sphinx_ so that you can build the
documentation:

.. code-block:: console

    $ pip install sphinx

.. _Git: http://git-scm.com/
.. _pip: http://www.pip-installer.org/
.. _virtualenv: http://www.virtualenv.org/
.. _Sphinx: http://sphinx-doc.org

Staying up to date
------------------

In the installation step, pip created an editable clone of the
repository in your home directory at ``$HOME/src/clans``. To update to
the latest version, change to this directory and do:

.. code-block:: console

    $ git pull

You can make your own changes to clans by editing the python
source code in this folder. You can keep track of your changes
by committing to the existing Git repo.

Contributing your changes to clans
----------------------------------

If you make modifications to clans, you may wish to contribute your
improvements to the project.

The first step is to publish your modifications. To do this, fork the
project on GitHub and add it as a remote in your local copy:

.. code-block:: console

    $ git remote add myfork https://github.com/your_username/clans.git

Now you can publish changes you made locally using ``git push myfork
master`` (although it is often a good idea to work in branches other
than ``master``). To submit your changes for review, open a pull
request on GitHub.
