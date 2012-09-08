#!/usr/bin/env python

from distutils.core import setup

setup(name='update_plan',
      version='dev',
      description='GrinnellPlans plan-editing utility',
      author='Tom Baldwin',
      author_email='tbaldwin@uoregon.edu',
      requires=['argparse', 'BeautifulSoup'],
      packages=['clans',],
      py_modules=['update_plan',],
      scripts=['bin/uplan',],
     )
