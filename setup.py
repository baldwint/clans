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
    sys.stderr.write("Clans requires Python 2.6 or 2.7\n")
    sys.exit(1)


setup(name='clans',
      version='dev',
      description='A command-line client for the '
                  'GrinnellPlans social network.',
      author='Tom Baldwin',
      author_email='tbaldwin@uoregon.edu',
      install_requires=reqs,
      extras_require=extras,
      packages=['clans', 'clans.ext'],
      scripts=['bin/clans', ],
      )
