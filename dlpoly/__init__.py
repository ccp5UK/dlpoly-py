''' simple dlpoly utilities to play with inputs and outputs '''

import sys
import numpy as np 
from distutils.version import LooseVersion

if sys.version_info[0] == 2:
    raise ImportError('dlpoly-py requires Python3. This is Python2.')

if LooseVersion(np.__version__) < '1.9':
    raise ImportError(
        'dlpoly=py needs NumPy-1.9.0 or later. You have: %s' % np.__version__)


# this is stupid shall be automatic

__all__ = ['cli',  'config',  'control',  'dlpoly',  'field', 'species',  'statis',  'utility']
__version__ = '0.0.1'

from .dlpoly import *
