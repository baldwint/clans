#!/usr/bin/env python

from setuptools import setup

setup(name='clans',
      version='dev',
      description='A command-line client for the '
                  'GrinnellPlans social network.',
      author='Tom Baldwin',
      author_email='tbaldwin@uoregon.edu',
      install_requires=['appdirs', 'BeautifulSoup', 'colorama'],
      packages=['clans',],
      scripts=['bin/clans',],
     )
