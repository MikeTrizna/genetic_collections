#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'requests',
    'pandas',
    'lxml',
    'tqdm'
]

setup_requirements = [
    'pytest-runner',
    # TODO(MikeTrizna): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    # TODO: put package test requirements here
]

setup(
    name='genetic_collections',
    version='0.1.7',
    description="A Python library for connecting genetic records with specimen data.",
    long_description=readme + '\n\n' + history,
    author="Mike Trizna",
    author_email='mike.trizna@gmail.com',
    url='https://github.com/MikeTrizna/genetic_collections',
    packages=find_packages(include=['genetic_collections']),
    entry_points={
        'console_scripts': [
            'ncbi_inst_search=genetic_collections.cli:ncbi_inst_search',
            'gb_search=genetic_collections.cli:gb_search'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='genetic_collections',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
