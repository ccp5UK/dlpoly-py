''' simple dlpoly utilities to play with inputs and outputs '''

import sys
from distutils.version import LooseVersion
import glob

if sys.version_info[0] == 2:
    raise ImportError('dlpoly-py requires Python3. This is Python2.')

# this is stupid shall be automatic

__all__ = ['cli',  'config',  'control',  'dlpoly',  'field', 'species',  'statis',  'utility']
__version__ = '0.0.1'

from .dlpoly import utility
