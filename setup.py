#!/usr/bin/env python3

import os

from setuptools import setup

base_dir = os.path.dirname(__file__)

long_description = ''
with open(os.path.join(base_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

about = {}
with open(os.path.join(base_dir, "penman", "__about__.py")) as f:
    exec(f.read(), about)

# thanks: https://snarky.ca/clarifying-pep-518/
docs_require = [
    'sphinx',
    'sphinx-rtd-theme',
    'sphinx_autodoc_typehints'
]
tests_require = [
    'pytest'
]


setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__summary__'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=about['__uri__'],
    author=about['__author__'],
    author_email=about['__email__'],
    license=about['__license__'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Utilities'
    ],
    keywords='nlp semantics amr',
    packages=[
        'penman',
    ],
    install_requires=[
    ],
    extras_require={
        'docs': docs_require,
        'tests': tests_require,
        'dev': docs_require + tests_require,
    },
    entry_points={
        'console_scripts': [
            'penman=penman.main:main'
        ]
    }
)
