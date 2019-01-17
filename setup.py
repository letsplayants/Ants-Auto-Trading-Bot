# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py
# https://github.com/kennethreitz/samplemod

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='ants',
    version='0.0.0',
    description='Sample package for Python-Guide.org',
    long_description=readme,
    author='muyoul lee',
    author_email='lemy0715@gmail.com',
    url='https://github.com/',
    license=license,
    packages=find_packages(exclude=('tests', 'docs','configs')),
    python_requires='>=3.6',
    test_suite="tests"
)