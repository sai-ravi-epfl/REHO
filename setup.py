# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

setup(
    name='REHO',
    version='2.0',
    description='Renewable Energy Hub Optimizer',
    long_description=readme,
    author='Luise Middelhauve, Cédric Terrier, Dorsan Lepour',
    author_email='luise.middelhauve@epfl.ch',
    url='https://gitlab.epfl.ch/ipese/urban-systems/reho',
    packages=find_packages(exclude=('Examples', 'documentation')),
    install_requires=[
        'amplpy', 'pandas', 'numpy', 'matplotlib', 'openpyxl'
    ]
)
