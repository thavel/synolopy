#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='synolopy',
    version='0.1.1',
    description='Synology Python API',
    author='thavel',
    packages=find_packages(),
    requires=[
        'requests'
    ],
)