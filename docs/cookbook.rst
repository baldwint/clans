Cookbook
========

Some common clans workflows.

Using clans on multitple computers
-----------------------------

If you use multiple computers, you can sync clans data between them
using a service such as Dropbox.

By default, clans stores its data in the same directory alongside the
``clans.cfg`` file. By symlinking this directory into your Dropbox,
the configuration file and all other data can be shared by your clans
installations.

For example, on Mac OS X::

    mv -r ~/Library/Application\ Support/clans ~/Dropbox/clansdata
    ln -s ~/Dropbox/clansdata ~/Library/Application\ Support/clans

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

