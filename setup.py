#!/usr/bin/env python

# Copyright (c) 2016, Michael Boyle
# See LICENSE file for details: <https://github.com/moble/h5py_cache/blob/master/LICENSE>

from distutils.core import setup

setup(name='h5py-cache',
      description='Create h5py File object with specified cache',
      author='Michael Boyle',
      author_email='mob22@cornell.edu',
      version='1.0',
      url='https://github.com/moble/h5py_cache',
      packages=['h5py_cache', ],
      package_dir={'h5py_cache': '.'},
      )
