'''
Module containing utility functions supporting the DLPoly Python Workflow.
'''

from abc import ABC
from collections.abc import Iterable
import glob
import itertools
from pathlib import Path
import re
import shutil
import sys
from typing import Any, Dict, Iterator, Literal, Optional, TextIO, Tuple, Union

import numpy as np

from .types import OptPath, PathLike, ThreeByThree

COMMENT_CHAR = '#'


class DLPFile:
    """
    Descriptor for standard access to files listed in `Control` in DLPoly.

    Attributes
    ----------
    filename_var : str
        Override variable name used in `Control` to reference file.
    attr : str
        Variable name used in `Control` to reference file.
    """

    def __init__(self, filename_var: str = "") -> None:
        """
        Descriptor for standard access to control files in DLPoly.

        Parameters
        ----------
        filename_var : str
            Override variable name used in `Control` to reference file.
        """
        self.filename_var = filename_var

    def __set_name__(self, owner, name):
        """
        Assign name to access relevant `Control` object parameter.

        Parameters
        ----------
        owner : object
            Object which contains attribute.
        name : str
            Name of variable on object.
        """
        if self.filename_var:
            name = self.filename_var
        else:
            name = name.removesuffix('_file')
        self.attr = f"io_file_{name}"

    def __get__(self, obj, objtype=None) -> Union[Path, str]:
        """
        Return `Path` to file as determined from `Control` on `obj`.

        Parameters
        ----------
        obj : object
            Parent object which contains attribute.
        objtype : Optional[type]
            Class of owner.

        Returns
        -------
        Union[Path, str]
            Path of given file or empty string if not set.
        """
        return Path(filepath) if (filepath := getattr(obj.control, self.attr, "")) else ""

    def __set__(self, obj, value: OptPath):
        """
        Set value on `Control` of parent object.

        Parameters
        ----------
        obj : object
            Parent object which contains attribute.
        value : OptPath
            New path to file.
        """
        if value is None:
            setattr(obj.control, self.attr, None)
        else:
            setattr(obj.control, self.attr, str(value))


def copy_file(inpf: PathLike, outd: PathLike):
    """
    Copy a file in a folder, avoiding same file error.

    Parameters
    ----------
    inpf : PathLike
        Input file to copy.
    outd : PathLike
        Output directory to copy to.
    """
    try:
        shutil.copy(inpf, outd)
    except shutil.SameFileError:
        pass


def next_file(filename: PathLike) -> str:
    """
    Get the name of the next available file.

    Parameters
    ----------
    filename : Pathlike
        Filename to check.

    Returns
    -------
    str
        New output file name.
    """
    files = glob.glob(f"{filename}*")
    if files:
        # Get last dir number
        idx = (int(match.group(0)) for file in files
               if (match := re.search('([0-9]+)$', file)))

        new_num = max(idx, default=1) + 1

        outfile = f"{filename}{new_num}"
    else:
        outfile = f"{filename}"

    return outfile


def peek(iterable: Iterator[Any]) -> Union[None, Iterator[Any]]:
    """
    Test generator without modifying (creates new generator).

    Parameters
    ----------
    iterable : Iterator[Any]
        Generator to test.

    Returns
    -------
    Union[None, Iterator[Any]]
        Original generator if remaining else None.
    """
    try:
        first = next(iterable)
    except StopIteration:
        return None
    return itertools.chain([first], iterable)


def parse_line(line: str) -> str:
    """
    Handle comment chars and whitespace.

    Parameters
    ----------
    line : str
        Line to parse.

    Returns
    -------
    str
        Line with comments and leading/trailing whitespace removed.
    """
    return line.split(COMMENT_CHAR)[0].strip()


def read_line(in_file: TextIO) -> Optional[str]:
    """
    Read a line, stripping comments and blank lines.

    Parameters
    ----------
    in_file
        File to read.

    Returns
    -------
    Optional[str]
        Next line of `in_file` without comments or trailing whitespace.
        Returns `None` if file exhausted.
    """

    for line in in_file:
        line = parse_line(line)
        if line:
            return line

    return None


def batched(iterable: Iterator[Any], n: int) -> Iterator[Tuple[Any, ...]]:
    """
    Version independent itertools.batched [python >= 3.12].

    Parameters
    ----------
    iterable : Iterator[Any]
        Iterable to batch.
    n : int
        Size of batch.

    Yields
    ------
    Tuple[Any, ...]
        Batched generator items.

    Examples
    --------
    batched('ABCDEFG', 3) → ABC DEF G.
    """
    if n < 1:
        raise ValueError('n must be at least one')
    it = iter(iterable)
    while batch := tuple(itertools.islice(it, n)):
        yield batch


def build_3d_rotation_matrix(alpha: float = 0.,
                             beta: float = 0.,
                             gamma: float = 0.,
                             units: Literal["deg", "rad"] = "rad") -> ThreeByThree:
    """
    Build a rotation matrix in degrees or radians.

    Parameters
    ----------
    alpha : float
        Alpha rotation angle.
    beta : float
        Beta rotation angle.
    gamma : float
        Gamma rotation angle.
    units : {"deg", "rad"}
        Units of rotation.

    Returns
    -------
    ThreeByThree
        Rotation matrix.
    """
    if units == "deg":
        alpha, beta, gamma = map(np.deg2rad, (alpha, beta, gamma))
    salp, sbet, sgam = map(np.sin, (alpha, beta, gamma))
    calp, cbet, cgam = map(np.cos, (alpha, beta, gamma))
    matrix = np.asarray([[cbet*cgam, cgam*salp*sbet - calp*sgam, calp*cgam*sbet + salp*sgam],
                         [cbet*sgam, calp*cgam+salp*sbet*sgam, calp*sbet*sgam-cgam*salp],
                         [-1.*sbet, cbet*salp, calp*cbet]], dtype=float)
    return matrix


class DLPData(ABC):
    """
    Abstract datatype for handling automatic casting and restricted assignment.

    Attributes
    ----------
    datatypes : Dict[str, Union[type, Tuple[type, ...]]]
        Datatypes to handle as dict of "element name : dataype".
    keys : Set[str]
        Keys handled by class.
    set_keys : Iterator[str]
        Generator of keys which have been manually set.
    className : str
        Name of host class.
    """

    def __init__(self, datatypes: Dict[str, Union[type, Tuple[type, ...]]], strict: bool = False):
        """
        Instantiate a DLPoly data containing object with defined types.

        Parameters
        ----------
        datatypes : Dict[str, Union[type, Tuple[type, ...]]]
            Permitted keys and their types.
        strict : bool
            Whether fuzzy matching is enabled or whether errors are
            immediately thrown on mismatched key names.
        """
        self._datatypes = datatypes
        self._strict = strict

    datatypes = property(lambda self: self._datatypes)
    keys = property(lambda self: {key for key in self.datatypes
                                  if key not in ("keysHandled", "_strict")})
    set_keys = property(lambda self: (key for key in self.keys if self.is_set(key)))
    className = property(lambda self: type(self).__name__)

    def dump(self):
        """
        Dump keys to screen.
        """
        for key in self.keys:
            print(key, self[key])

    @property
    def strict(self) -> bool:
        """
        Whether should throw if bad keys supplied.
        """
        return self._strict

    def __setattr__(self, key: str, val: Any):
        """
        Set attribute with particular checks in place for particular keys.

        Parameters
        ----------
        key : str
            Key to set.
        val : Any
            Value to assign and check.

        Raises
        ------
        KeyError
            If `key` is `datatype` or `strict` and object already initialised.
            If `key` is "ensemble" and value if `None`
            If DLPData object is `strict` and key not found.

        Notes
        -----
        Does not allow over-writing of `datatypes` or `strict`.

        Maps types to those defined in `datatypes` before assigning.
        """
        if key == "_datatypes":  # Protect datatypes

            if not hasattr(self, "_datatypes"):
                self.__dict__[key] = {**val, "keysHandled": tuple, "_strict": bool}
            else:
                raise KeyError("Cannot alter datatypes")
            return

        if key == "_strict":
            if not hasattr(self, "_strict"):
                self.__dict__[key] = val
            else:
                raise KeyError("Cannot alter strict")
            return

        if key == "source":  # source is not really a keyword
            self.__dict__[key] = val
            return

        if key == "ensemble" and val is None:
            raise KeyError("Ensemble cannot be empty")

        if self.strict and key not in self.datatypes:
            raise KeyError(f"Param {key} not allowed in {self.className.lower()} definition")

        val = self._map_types(key, val)
        self.__dict__[key] = val

    def __getitem__(self, key: str) -> Any:
        """
        Fuzzy matching on get/set item.

        Parameters
        ----------
        key : str
           Key to search for.

        Returns
        -------
        Any
            Value for given `key`.
        """
        key = check_arg(key, *self.keys)
        return getattr(self, str(key))

    def __setitem__(self, key_in: str, val: Any):
        """
        Fuzzy matching on get/set item.

        Parameters
        ----------
        key_in : str
            Key to set.
        val : Any
            Value to assigne to key.

        Raises
        ------
        KeyError
            If key not found in type.
        """
        if not self.strict:
            key = check_arg(key_in, *self.keys)
            if not key:
                raise KeyError(f"'{key_in}' is not a member of {type(self).__name__}")
        else:
            key = key_in
        setattr(self, key, val)

    def __iter__(self):
        """
        Iterator over set keys and their values.

        Returns
        -------
        Iterator[Tuple[str, Any]]
            Keys and values which are not defaults.
        """
        return ((key, self[key]) for key in self.set_keys)

    def __add__(self, other: Iterable[Tuple[str, Any]]):
        """
        Set keys from `other` in `self`, with `self` taking priority.

        Parameters
        ----------
        other : Iterable[Tuple[str, Any]]
            Object to take keys from.

        Notes
        -----
        Works similarly to `dict.update`.
        """
        for key, val in other:
            if not self.is_set(key):
                self[key] = val

    def is_set(self, key: str) -> bool:
        """
        Check if key is set in this object.

        Parameters
        ----------
        key : str
            Key to check.

        Returns
        -------
        bool
            Whether `key` has been explicitly set.
        """
        return key in self.__dict__

    def _map_types(self, key: str, vals: Any) -> Any:
        """
        Map argument types to their respected types according to `datatypes`.

        Parameters
        ----------
        key : str
            Key to set.
        vals : Any
            Values to map to correct datatypes.

        Returns
        -------
        Any
            Corrected datatypes.

        Raises
        ------
        TypeError
            If unable to convert given `vals` into correct datatype.
        """
        datatype = self._datatypes[key]
        val: Any

        if all((isinstance(vals, (tuple, list)),          # Given a list but datatype
                not isinstance(datatype, (tuple, bool)),  # is some scalar non-boolean
                datatype is not tuple)):

            if not vals:
                pass
            elif len(vals) == 1:
                vals = vals[0]
            else:
                for arg in vals:  # Take first arg
                    try:
                        vals = arg
                        break
                    except TypeError:
                        pass
                else:
                    assert isinstance(datatype, type)
                    raise TypeError(f"No arg of {vals} ({[type(x).__name__ for x in vals]}) "
                                    f"for key {key} valid, must be castable to {datatype.__name__}")

        if isinstance(datatype, tuple):
            if isinstance(vals, (int, float, str)):
                vals = (vals,)

            # to parse e.g new_controls' random_seed [2017,2018,2019] - requires
            #   removal of [, and ]
            if key != "correlation_observable":
                vals = [v.strip("[] ") if isinstance(v, str) else v for v in vals]
            try:
                if ... in datatype:
                    loc = datatype.index(...)
                    if loc != len(datatype)-1:
                        pre: Tuple[type, ...] = datatype[:loc]
                        post: Tuple[type, ...] = datatype[loc+1:]
                        ellided: itertools.repeat = itertools.repeat(datatype[loc-1], len(post) - loc)

                        val_iter = iter(vals)

                        transf = itertools.chain(zip(val_iter, pre),
                                                 zip(val_iter, ellided),
                                                 zip(val_iter, post))
                        val = [target_type(item) for item, target_type in transf]
                    else:
                        pre, ellided = datatype[:loc], datatype[loc-1]
                        val = ([target_type(item) for item, target_type in zip(vals[:loc], pre)] +
                               [ellided(item) for item in vals[loc:]])

                else:
                    val = [target_type(item) for item, target_type in zip(vals, datatype)]
            except TypeError as err:
                message = (f"Type of {vals} ({[type(x).__name__ for x in vals]}) not valid, "
                           f"must be castable to {[x.__name__ for x in datatype]}")

                if not self.strict:
                    print(message)
                    return None

                raise TypeError(message) from err
        elif isinstance(vals, datatype):  # Already right type
            val = vals
        elif datatype is bool:  # If present true unless explicitly false
            val = vals not in (0, False, "off", "OFF")

        elif isinstance(datatype, type):
            try:
                val = datatype(vals)
            except TypeError as err:
                message = (f"Type of {vals} ({type(vals).__name__}) not valid, "
                           f"must be castable to {datatype.__name__}")

                if not self.strict:
                    print(err)
                    print(message)
                    return None

                raise TypeError(message) from err

        return val


def check_arg(key: str, *args: str) -> Optional[str]:
    """
    Perform fuzzy match against potential arguments.

    Parameters
    ----------
    key : str
        Key to check.
    *args
        Possible options to check against.

    Returns
    -------
    Optional[str]
        First match to key in arguments if found, else ``None``.
    """
    if key in args:
        return key

    for arg in args:
        if key.startswith(arg):
            return arg
    return None


def is_mpi() -> bool:
    """
    Check whether MPI is active and available.

    Returns
    -------
    bool
        Whether MPI is available.
    """
    # Imported mpi4py
    if 'mpi4py' in sys.modules:
        from mpi4py import MPI
        return MPI.COMM_WORLD.Get_size() > 1

    return False
