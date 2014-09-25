#!/usr/bin/env python

from setuptools import setup
import sys

# build dependency list
reqs = ['appdirs', 'beautifulsoup4', 'html5lib', 'colorama', 'requests']
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

with open('README.rst') as f:
    readme = f.read()

setup(name='clans',
      version=verstr,
      description='A command-line client for the '
                  'GrinnellPlans social network.',
      long_description=readme,
      url='https://github.com/baldwint/clans',
      author='Tom Baldwin',
      author_email='tbaldwin@uoregon.edu',
      license='MIT',
      classifiers=(
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'Topic :: Internet :: Finger',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
      ),
      install_requires=reqs,
      extras_require=extras,
      packages=['clans', 'clans.ext'],
      entry_points = {
          'console_scripts': ['clans=clans.ui:main'],
      },
      )
