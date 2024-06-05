"""
Module to handle DLPOLY config files.
"""

from collections.abc import Generator, Iterable
import copy
from enum import IntEnum
from typing import Optional, TextIO, Union

import numpy as np

from .types import PathLike, ThreeVec
from .utility import DLPData


class Imcon(IntEnum):
    """
    DLPoly image convention.
    """

    NONE = 0
    CUBIC = 1
    ORTHORHOMBIC = 2
    PARALLELOPIPED = 3
    SLAB = 6


class LevelOfDetail(IntEnum):
    """
    DLPoly CONFIG file level of detail.
    """

    POSITIONS = 0
    VELOCITIES = 1
    FORCES = 2


def _format_3vec(list_in: ThreeVec) -> str:
    """
    Format 3-vector for printing.

    Parameters
    ----------
    list_in : ThreeVec
        Vector to convert.

    Returns
    -------
    str
        Standard formatted string for DLPoly style.
    """
    return f"{list_in[0]:20.10f}{list_in[1]:20.10f}{list_in[2]:20.10f}\n"


class Atom(DLPData):
    """
    Class defining a DLPoly atom.

    Attributes
    ----------
    element : str
        Atom label.
    pos : ThreeVec
        Position vector.
    vel : ThreeVec
        Velocity vector.
    forces : ThreeVec
        Net force vector.
    index : int
        Unique ID.
    molecule : Tuple[str, int]
        Owner molecule and count.

    Methods
    -------
    write(level)
        Write the `Atom` with given level of detail.
    read(file_handle, level, i)
        Read a single `Atom` from a file.
    """

    def __init__(
        self,
        element: str = "",
        pos: Optional[ThreeVec] = None,
        vel: Optional[ThreeVec] = None,
        forces: Optional[ThreeVec] = None,
        index: int = 1,
    ):
        """
        Instantiate a DLPoly atom.

        Parameters
        ----------
        element : str
            Atom label.
        pos : Optional[ThreeVec]
            Position vector.
        vel : Optional[ThreeVec]
            Velocity vector.
        forces : Optional[ThreeVec]
            Net force vector.
        index : int
            Unique ID.
        """
        DLPData.__init__(
            self,
            {
                "element": str,
                "pos": (float, float, float),
                "vel": (float, float, float),
                "forces": (float, float, float),
                "index": int,
                "molecule": (str, int),
            },
        )
        self.element = element
        self.pos = pos if pos is not None else np.zeros(3)
        self.vel = vel if vel is not None else np.zeros(3)
        self.forces = forces if forces is not None else np.zeros(3)
        self.index = index

    def write(self, level: LevelOfDetail) -> str:
        """
        Return string of own data ready to write to file at given print level.

        Parameters
        ----------
        level : LevelOfDetail
            Level of detail to print.

        Returns
        -------
        str
            Data in DLPoly CONFIG file format.

        Raises
        ------
        ValueError
            If print level is invalid.
        """

        if level == LevelOfDetail.POSITIONS:
            return f"{self.element:8s}{self.index:10d}\n" + _format_3vec(self.pos)

        if level == LevelOfDetail.VELOCITIES:
            return (
                f"{self.element:8s}{self.index:10d}\n" + _format_3vec(self.pos),
                _format_3vec(self.vel),
            )

        if level == LevelOfDetail.FORCES:
            return (
                f"{self.element:8s}{self.index:10d}\n" + _format_3vec(self.pos),
                _format_3vec(self.vel),
                _format_3vec(self.forces),
            )

        raise ValueError(f"Invalid print level {level} in Config.write")

    @classmethod
    def read(cls, file_handle: TextIO, level: LevelOfDetail, i: int) -> "Atom":
        """
        Read single atom.

        Parameters
        ----------
        file_handle : TextIO
            File to read from.
        level : LevelOfDetail
            Level of detail of input file.
        i : int
            Current index of atom.

        Returns
        -------
        Atom
            Instance of atom object.
        """
        line = file_handle.readline()
        if not line:
            return None

        elem_ind = line.split()

        if len(elem_ind) == 1:
            element = elem_ind[0]
            # there is no index in the file, we shall ignore
            # probably breaking hell loose somewhere else
            index = i
        elif len(elem_ind) == 2:
            element = elem_ind[0]
            index = int(elem_ind[1])

        pos = np.array(file_handle.readline().split(), dtype=float)

        if level >= LevelOfDetail.VELOCITIES:
            vel = np.array(file_handle.readline().split(), dtype=float)
        else:
            vel = None

        if level >= LevelOfDetail.FORCES:
            forces = np.array(file_handle.readline().split(), dtype=float)
        else:
            forces = None

        return cls(element, pos, vel, forces, index)

    def __str__(self) -> str:
        return (
            f"{self.element:8s}{self.index:10d}\n"
            + _format_3vec(self.pos)
            + _format_3vec(self.vel)
            + _format_3vec(self.forces)
        )


class Config:
    """
    Class defining a DLPoly CONFIG file.

    Attributes
    ----------
    title : str
        DLPoly title comment.
    level : LevelOfDetail
        Level of detail of CONFIG file to read/write.
    atoms : List[Atom]
        Atoms contained in configuration.
    pbc : Imcon
        Image convention.
    cell : np.ndarray
        3x3 Cartesian matrix defining cell.
    source : Optional[PathLike]
        File CONFIG originally read from.
    params : Dict[str, type]x
        Types associated with components.
    natoms : int
        Number of atoms.

    Methods
    -------
    read(filename)
        Read CONFIG from file.
    write(filename, title, level)
        Write CONFIG to file.
    add_atoms(other)
        Add atoms from `other` CONFIG or sequence of `Atom`.
    """

    params = {
        "atoms": list,
        "cell": np.ndarray,
        "pbc": int,
        "natoms": int,
        "level": int,
        "title": str,
    }

    natoms = property(lambda self: len(self.atoms))

    def __init__(self, source: Optional[PathLike] = None):
        """
        Instantiate class defining a DLPOLY config file.

        Parameters
        ----------
        source : Optional[PathLike]
            File to read.
        """
        self.title = ""
        self.level = LevelOfDetail.POSITIONS
        self.atoms = []
        self.pbc = Imcon.NONE
        self.cell = np.zeros((3, 3))

        if source is not None:
            self.source = source
            self.read(source)

    def _read_atoms(self, in_file: TextIO) -> Generator[Atom, None, None]:
        """
        Generator to read `Atom`s from file.

        Parameters
        ----------
        in_file : TextIO
            File to read atoms from.

        Yields
        ------
        Atom
            Atom read from file.
        """
        i = 0
        while atom := Atom.read(in_file, self.level, i):
            yield atom
            i += 1

    def read(self, filename: PathLike = "CONFIG") -> "Config":
        """
        Read file into Config.

        Parameters
        ----------
        filename : PathLike
            File to read.

        Returns
        -------
        "Config"
            Configuration as read from file.

        Raises
        ------
        RuntimeError
            If issue reading cell.
        """
        with open(filename, encoding="utf-8") as in_file:
            self.title = in_file.readline().strip()
            line = in_file.readline().split()
            self.level = LevelOfDetail(int(line[0]))
            self.pbc = Imcon(int(line[1]))

            if self.pbc != Imcon.NONE:
                for j in range(3):
                    line = in_file.readline().split()
                    try:
                        self.cell[j, :] = np.array(line, dtype=float)
                    except ValueError as exc:
                        raise RuntimeError("Error reading cell") from exc

            self.atoms = list(self._read_atoms(in_file))

        return self

    def write(
        self,
        filename: PathLike = "new.config",
        title: Optional[str] = None,
        level: LevelOfDetail = LevelOfDetail.POSITIONS,
    ):
        """
        Output `Config` to file.

        Parameters
        ----------
        filename : PathLike
            File to write config to.
        title : Optional[str]
            Title comment for first line.
        level : LevelOfDetail
            Level of detail to dump.
        """
        self.level = level
        with open(filename, "w", encoding="utf-8") as out_file:
            print(f"{title if title else self.title:72s}", file=out_file)
            print(f"{level:10d}{self.pbc:10d}{self.natoms:10d}", file=out_file)
            if self.pbc != Imcon.NONE:
                for row in self.cell:
                    print(_format_3vec(row), file=out_file)

            for atom in self.atoms:
                print(atom.write(self.level), file=out_file)

    def add_atoms(self, other: Union["Config", Iterable[Atom]]):
        """
        Add atoms from `Config` `other` to self.

        Parameters
        ----------
        other : Union[Config, Sequence[Atom]]
            Config to take atoms from or list of atoms to add.
        """
        last_index = self.natoms

        if isinstance(other, Config):
            other = other.atoms

        self.atoms.extend(copy.copy(atom) for atom in other)

        # Shift new atoms' indices to reflect place in new config
        for new_index, atom in enumerate(self.atoms[last_index:], last_index + 1):
            atom.index = new_index

    def __repr__(self):
        return f"""{self.title if self.title else "Untitled"}
        config file: {self.source}
        num_atoms: {self.natoms}
        image convention: {self.pbc.name} ({self.pbc.value})
        level of detail: {self.level.name} ({self.level.value})
        """


if __name__ == "__main__":
    CONFIG = Config().read()
    CONFIG.write()
