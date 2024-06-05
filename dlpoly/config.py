"""
Module to handle DLPOLY config files
"""

import copy
from collections.abc import Iterable
from enum import IntEnum
from typing import Optional, TextIO, Union

import numpy as np

from .types import PathLike, ThreeVec
from .utility import DLPData


class Imcon(IntEnum):
    """ DLPoly Image Convention """
    NONE = 0
    CUBIC = 1
    ORTHORHOMBIC = 2
    PARALLELOPIPED = 3
    SLAB = 6


class LevelOfDetail(IntEnum):
    """ DLPoly Config file LoD """
    POSITIONS = 0
    VELOCITIES = 1
    FORCES = 2


def _format_3vec(list_in: ThreeVec) -> str:
    "Format 3-vector for printing"
    return f"{list_in[0]:20.10f}{list_in[1]:20.10f}{list_in[2]:20.10f}\n"


class Atom(DLPData):
    """ Class defining a DLPOLY atom type

     :param element: Label
     :param pos: Position vector
     :param vel: Velocity vector
     :param forces: Net force vector
     :param index: ID

     """

    def __init__(self,
                 element: str = "",
                 pos: Optional[ThreeVec] = None,
                 vel: Optional[ThreeVec] = None,
                 forces: Optional[ThreeVec] = None,
                 index: int = 1):
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
        """ Print own data to file w.r.t config print level

        :param level: Print level

        """

        if level == LevelOfDetail.POSITIONS:
            return (f"{self.element:8s}{self.index:10d}\n" +
                    _format_3vec(self.pos))

        if level == LevelOfDetail.VELOCITIES:
            return (f"{self.element:8s}{self.index:10d}\n" +
                    _format_3vec(self.pos),
                    _format_3vec(self.vel))

        if level == LevelOfDetail.FORCES:
            return (f"{self.element:8s}{self.index:10d}\n" +
                    _format_3vec(self.pos),
                    _format_3vec(self.vel),
                    _format_3vec(self.forces))

        raise ValueError(f"Invalid print level {level} in Config.write")

    def __str__(self) -> str:
        return (f"{self.element:8s}{self.index:10d}\n" +
                _format_3vec(self.pos) +
                _format_3vec(self.vel) +
                _format_3vec(self.forces))

    @classmethod
    def read(cls,
             file_handle: TextIO,
             level: LevelOfDetail,
             i: int) -> Union["Atom", None]:
        """ Reads info for one atom

        :param file_handle: File to read
        :param level: Level to read
        :param i: Index

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


class Config:
    """ Class defining a DLPOLY config file

     :param source: File to read

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
        self.title = ""
        self.level = LevelOfDetail.POSITIONS
        self.atoms = []
        self.pbc = Imcon.NONE
        self.cell = np.zeros((3, 3))

        if source is not None:
            self.source = source
            self.read(source)

    def write(self,
              filename: PathLike = "new.config",
              title: Optional[str] = None,
              level: LevelOfDetail = LevelOfDetail.POSITIONS):
        """ Output to file

        :param filename: File to write
        :param title: Title of run
        :param level: Print level

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

    def add_atoms(self, other: Union[Iterable[Atom], "Config"]):
        """ Add two Configs together to make one bigger config

        :param other: Config to add

        """
        last_index = self.natoms

        if isinstance(other, Config):
            other = other.atoms

        self.atoms.extend(copy.copy(atom) for atom in other)

        # Shift new atoms' indices to reflect place in new config
        for new_index, atom in enumerate(self.atoms[last_index:], last_index+1):
            atom.index = new_index

    def _read_atoms(self, in_file: TextIO):
        i = 0
        while atom := Atom.read(in_file, self.level, i):
            yield atom
            i += 1

    def read(self, filename="CONFIG"):
        """ Read file into Config

        :param filename: File to read

        """

        with open(filename, "r", encoding="utf-8") as in_file:
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
