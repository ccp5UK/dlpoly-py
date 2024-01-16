"""
Provides typing for DLPoly
"""

import os
from typing import Annotated, Optional, Union

import numpy as np
import numpy.typing as npt

PathLike = Union[os.PathLike, str]
OptPath = Optional[PathLike]
ThreeByThree = Annotated[npt.NDArray[np.float64], (3, 3)]
ThreeVec = Annotated[npt.NDArray[np.float64], 3]
