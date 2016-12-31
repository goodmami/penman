#!/usr/bin/env python3

from setuptools import setup

long_description = (
    'The Penman library and utility allow for serializing graphs in the '
    'PENMAN format (e.g., as used by AMR (Abstract Meaning Representation)). '
    'This utility not only converts from PENMAN to triples, but also can '
    'reserialize PENMAN to re-indent or select a new top node.'
)

setup(
    name='Penman',
    version='0.4.0',
    description='PENMAN notation for graphs (e.g. AMR).',
    long_description=long_description,
    url='https://github.com/goodmami/penman',
    author='Michael Wayne Goodman',
    author_email='goodman.m.w@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Utilities'
    ],
    keywords='nlp semantics amr',
    py_modules=['penman'],
    install_requires=[
        'docopt >=0.6.0'
    ]
    # entry_points={
    #     'console_scripts': [
    #         'penman=...'
    #     ]
    # }
)
