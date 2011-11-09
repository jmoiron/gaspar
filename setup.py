#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Setup script for gaspar."""

from setuptools import setup, find_packages
import sys, os

try:
    from gaspar import VERSION
    version = '.'.join(VERSION)
except ImportError:
    version = '1.0'

# some trove classifiers:

# License :: OSI Approved :: MIT License
# Intended Audience :: Developers
# Operating System :: POSIX

setup(
    name='gaspar',
    version=version,
    description="gaspar eventlet zmq parallel worker",
    long_description=open('README.rst').read(),
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
    ],
    keywords='eventlet zmq parallel prefork',
    author='Jason Moiron',
    author_email='jmoiron@jmoiron.net',

    url='http://github.com/jmoiron/gaspar',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    test_suite="tests",
    install_requires=[
      # -*- Extra requirements: -*-
      'eventlet',
      'pyzmq',
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
)
