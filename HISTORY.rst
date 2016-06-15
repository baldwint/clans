.. :changelog:

Release History
---------------

0.3.0 (forthcoming)
++++++++++++++++++

- Clans now displays "Last Updated" and "Last Login" timestamps in
  your local timezone (or some other one you configure).
- Added ``timezone`` and ``date_format`` config options
- ScrAPI now returns Python datetime objects for time-related data,
  in the UTC time zone. A new ``timezone`` keyword argument specifies
  which zone the server is assumed to be in when making this conversion.
- Fixed a bug that prevented clans from logging in after 2016-06-14
- Miscellaneous structural changes

0.2.1 (2015-01-03)
++++++++++++++++++

- Bug fix in HTTPS handling

0.2.0 (2014-09-25)
++++++++++++++++++

- Added ability to use HTTPS and verify the certificate
- ScrAPI change: always retrieve server-side MD5 hash
- Support for Python 3.4

0.1.0 (2014-04-01)
++++++++++++++++++

- Initial public release

