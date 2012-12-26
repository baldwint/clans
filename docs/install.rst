Installation
============

``clans`` is still in development, and there have been no versioned
releases. To use it, you will need to check out a copy from the
development repository using Mercurial_.

Installing from source repo
---------------------------

To check out and install ``clans`` in a single step, use pip_::

    $ pip install --user -e hg+https://bitbucket.org/tkb/clans#egg=clans

If you omit ``--user``, you may need to prefix this with ``sudo``.
This flag is unnecessary if you have some other means of organizing
python modules in your home directory (e.g., working in a virtualenv_).

If you don't have them already, install the following dependencies::

    $ pip install beautifulsoup
    $ pip install appdirs

As an optional step, install Sphinx_ so that you can build the
documentation::

    $ pip install sphinx

.. _Mercurial: http://mercurial.selenic.com/
.. _pip: http://mercurial.selenic.com/
.. _virtualenv: http://www.virtualenv.org/
.. _Sphinx: http://sphinx-doc.org

Staying up to date
------------------

In the installation step, you created an editable clone of the
repository in your home directory at ``$HOME/src/clans``. To update to
the latest version, change to this directory and do::

    $ hg pull
    $ hg update

You can make your own changes to clans by editing the python
source code in this folder. You can keep track of your changes
by committing to the existing Mercurial repo.

Contributing your changes to clans
----------------------------------

If you make modifications to clans, you may wish to contribute your
improvements to the project.

Create a Bitbucket account and fork the main clans repo. In your local
development copy, edit ``.hg/hgrc`` and change the line that reads::

    default = https://bitbucket.org/tkb/clans

to::

    default = ssh://hg@bitbucket.org/your_username/clans

You can now publish your modifications using ``hg push``. When you're
ready to submit your changes, open a pull request on Bitbucket.

