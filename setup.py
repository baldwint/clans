#!/usr/bin/env python

from setuptools import setup
import sys

# build dependency list
reqs = ['appdirs', 'beautifulsoup4', 'html5lib', 'colorama']
extras = {'tests': ['pymysql', 'coverage',
                    'pytest', 'pytest-cov', 'tox'],
          'docs':  ['sphinx', ]}

if sys.version_info < (3, 3):
    extras['tests'].append('mock')

if sys.version_info >= (3,):
    pass
elif sys.version_info >= (2, 7):
    pass
elif sys.version_info >= (2, 6):
    reqs.extend(['argparse', 'ordereddict', 'importlib'])
    extras['tests'].append('unittest2')
    extras['tests'].append('subprocess32')
else:
    sys.stderr.write("Clans requires Python 2.6+ or 3.3+\n")
    sys.exit(1)

# http://stackoverflow.com/a/7071358/735926
import re
VERSIONFILE='clans/__init__.py'
verstrline = open(VERSIONFILE, 'rt').read()
VSRE = r'^__version__\s+=\s+[\'"]([^\'"]+)[\'"]'
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % VERSIONFILE)

setup(name='clans',
      version=verstr,
      description='A command-line client for the '
                  'GrinnellPlans social network.',
      author='Tom Baldwin',
      author_email='tbaldwin@uoregon.edu',
      license='MIT',
      install_requires=reqs,
      extras_require=extras,
      packages=['clans', 'clans.ext'],
      entry_points = {
          'console_scripts': ['clans=clans.ui:main'],
      },
      )
