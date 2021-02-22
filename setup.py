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
docs_requirements = os.path.join(base_dir, 'docs', 'requirements.txt')
if os.path.isfile(docs_requirements):
    with open(docs_requirements) as f:
        docs_require = f.readlines()
else:
    docs_require = []


tests_require = [
    'pytest',
    'mypy',
    'flake8',
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
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Utilities'
    ],
    keywords='nlp semantics amr',
    packages=[
        'penman',
        'penman.models',
    ],
    setup_requires=['wheel >= 0.31.0'],
    install_requires=[
    ],
    extras_require={
        'docs': docs_require,
        'tests': tests_require,
        'dev': docs_require + tests_require + [
            # https://packaging.python.org/guides/making-a-pypi-friendly-readme
            'setuptools >= 38.6.0',
            'wheel >= 0.31.0',
            'twine >= 1.11.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'penman=penman.__main__:main'
        ]
    }
)
