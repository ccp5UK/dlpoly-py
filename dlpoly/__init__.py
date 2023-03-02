"""Simple DL_POLY_4 utilities to play with inputs and outputs.

typical usage

>>>   from dlpoly import DLPoly
>>>   dlPoly = DLPoly(control="Ar.control", config="Ar.config",
>>>                   field="Ar.field", workdir="argon")

"""

from distutils.version import LooseVersion
from pathlib import Path
import sys
import numpy as np

if sys.version_info[0] == 2:
    raise ImportError('dlpoly-py requires Python3. This is Python2.')

if LooseVersion(np.__version__) < '1.5':
    raise ImportError(
        'dlpoly-py needs NumPy-1.5.0 or later. You have: {:s}'.format(np.__version__))


# from https://stackoverflow.com/questions/1057431
modules = Path(__file__).parent.glob("*.py")
__all__ = [f.stem for f in modules if f.is_file()
           and f.name != '__init__.py']

__version__ = '0.3.12'

try:
    from .dlpoly import DLPoly
    print("Supported DL_POLY version {}".format(DLPoly.__version__))
except ImportError:
    raise ImportError('error importing dlpoly')
