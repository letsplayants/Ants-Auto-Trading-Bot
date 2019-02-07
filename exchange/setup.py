# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

setup(
    name='exchangem',
    version='0.0.0',
    description='Exchange intergrated',
    long_description=readme,
    author='muyoul lee',
    author_email='lemy0715@gmail.com',
    url='https://github.com/MuYoul/exchangem',
    license=license,
    packages=find_packages(exclude=('tests', 'docs','configs')),
    python_requires='>=3.6.7',
    test_suite="tests"
)