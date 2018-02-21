#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup
from setuptools.command.test import test as test_command

import sys

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'requests >= 2.0.0, < 3.0.0',
    'tld >= 0.7.3, < 1.0.0',
    'js2py >= 0.43',
]

classifiers = [
    'Development Status :: 3 - Alpha',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Topic :: Internet',
] + ['Programming Language :: Python :: ' + v for v in '2 2.7 3 3.3 3.4 3.5 3.6'.split()]


def get_version():
    p = os.path.join(os.path.dirname(
                     os.path.abspath(__file__)), "pypac", "__init__.py")
    with open(p) as f:
        for line in f.readlines():
            if "__version__" in line:
                return line.strip().split("=")[-1].strip(" '")
    raise ValueError("could not read version")


class PyTest(test_command):
    def finalize_options(self):
        test_command.finalize_options(self)
        self.test_args = ['--strict', '--verbose', '--tb=long', 'tests']
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name='pypac',
    version=get_version(),
    description="Proxy auto-config and auto-discovery for Python.",
    long_description=readme + '\n\n' + history,
    author="Carson Lam",
    author_email='carsonyylam@gmail.com',
    url='https://github.com/carsonyl/pypac',
    packages=[
        'pypac',
    ],
    package_dir={'pypac': 'pypac'},
    package_data={'': ['LICENSE']},
    include_package_data=True,
    install_requires=requirements,
    license="Apache 2.0",
    zip_safe=False,
    keywords='pypac pac proxy autoconfig requests',
    classifiers=classifiers,
    cmdclass={'test': PyTest},
    test_suite='tests',
    tests_require=[
        'pytest',
        'mock',
    ],
    extras_require={
        'socks': ['requests[socks]>=2.10.0'],
    },
)
