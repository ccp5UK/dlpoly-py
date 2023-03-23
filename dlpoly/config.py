"""
Module to handle DLPOLY config files
"""

import copy
import numpy as np

# from dlpoly-py.species import Species
from .utility import DLPData


def _format_3vec(list_in):
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

    def __init__(self, element="", pos=None, vel=None, forces=None, index=1):
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
        self.pos = np.zeros(3) if pos is None else pos
        self.vel = np.zeros(3) if vel is None else vel
        self.forces = np.zeros(3) if forces is None else forces
        self.index = index

    def write(self, level):
        """ Print own data to file w.r.t config print level

        :param level: Print level ; 1 = Pos, 2 = Vel, 3 = Forces

        """

        if level == 0:
            return (f"{self.element:8s}{self.index:10d}\n" +
                    _format_3vec(self.pos))

        if level == 1:
            return (f"{self.element:8s}{self.index:10d}\n" +
                    _format_3vec(self.pos),
                    _format_3vec(self.vel))

        if level == 2:
            return (f"{self.element:8s}{self.index:10d}\n" +
                    _format_3vec(self.pos),
                    _format_3vec(self.vel),
                    _format_3vec(self.forces))

        raise ValueError(f"Invalid print level {level} in Config.write")

    def __str__(self):
        return (f"{self.element:8s}{self.index:10d}\n" +
                _format_3vec(self.pos) +
                _format_3vec(self.vel) +
                _format_3vec(self.forces))

    @classmethod
    def read(cls, file_handle, level, i):
        """ Reads info for one atom

        :param file_handle: File to read
        :param level: Level to readd
        :param i: Index

        """
        line = file_handle.readline()
        if not line:
            return False

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

        if level > 0:
            vel = np.array(file_handle.readline().split(), dtype=float)
        else:
            vel = None

        if level > 1:
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

    def __init__(self, source=None):
        self.title = ""
        self.level = 0
        self.atoms = []
        self.pbc = 0
        self.cell = np.zeros((3, 3))

        if source is not None:
            self.source = source
            self.read(source)

    def write(self, filename="new.config", title=None, level=0):
        """ Output to file

        :param filename: File to write
        :param title: Title of run
        :param level: Print level ; 1 = Pos, 2 = Vel, 3 = Forces

        """
        self.level = level
        with open(filename, "w", encoding="utf-8") as out_file:
            print(f"{title if title else self.title:72s}", file=out_file)
            print(f"{level:10d}{self.pbc:10d}{self.natoms:10d}", file=out_file)
            if self.pbc > 0:
                for row in self.cell:
                    print(_format_3vec(row), file=out_file)

            for atom in self.atoms:
                print(atom.write(self.level), file=out_file)

    def add_atoms(self, other):
        """ Add two Configs together to make one bigger config

        :param other: Config to add

        """
        last_index = self.natoms

        if isinstance(other, Config):
            other = other.atoms

        self.atoms.extend(copy.copy(atom) for atom in other)

        # Shift new atoms' indices to reflect place in new config
        for atom in self.atoms[last_index:]:
            atom.index += last_index

    def read(self, filename="CONFIG"):
        """ Read file into Config

        :param filename: File to read

        """

        with open(filename, "r", encoding="utf-8") as in_file:
            self.title = in_file.readline().strip()
            line = in_file.readline().split()
            self.level = int(line[0])
            self.pbc = int(line[1])

            if self.pbc > 0:
                for j in range(3):
                    line = in_file.readline().split()
                    try:
                        self.cell[j, :] = np.array(line, dtype=float)
                    except ValueError as exc:
                        raise RuntimeError("Error reading cell") from exc

            self.atoms = []
            i = 0
            while atom := Atom.read(in_file, self.level, i):
                i += 1
                self.atoms.append(atom)

        return self


if __name__ == "__main__":
    CONFIG = Config().read()
    CONFIG.write()
