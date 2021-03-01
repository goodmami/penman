# -*- coding: utf-8 -*-

__version__ = '1.2.0'
__version_info__ = tuple(
    int(x) if x.isdigit() else x
    for x in __version__.replace('.', ' ').replace('-', ' ').split()
)

__title__ = 'Penman'
__summary__ = 'PENMAN notation for graphs (e.g., AMR)'
__uri__ = 'https://github.com/goodmami/penman'

__author__ = 'Michael Wayne Goodman'
__email__ = 'goodman.m.w@gmail.com'

__license__ = 'MIT'
__copyright__ = '2016--2020 %s <%s>' % (__author__, __email__)
