#!/usr/bin/env python

from distutils.core import setup

setup(name='clans',
      version='dev',
      description='GrinnellPlans plan-editing utility',
      author='Tom Baldwin',
      author_email='tbaldwin@uoregon.edu',
      requires=['argparse', 'BeautifulSoup'],
      packages=['clans',],
      scripts=['bin/clans',],
     )
