#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='synolopy',
    version='0.1.2',
    description='Synology Python API',
    author='Thibaut Havel',
    packages=find_packages(),
    requires=[
        'requests'
    ],
)
