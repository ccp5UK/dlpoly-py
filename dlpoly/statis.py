"""
File containing methods for loading statistics data from DLPoly.
"""

from functools import singledispatchmethod
from typing import Optional, Tuple

import numpy as np
from ruamel.yaml import YAML

from .config import Config
from .control import Control
from .types import OptPath, PathLike


class Statis:
    """
    Class to parse and interpret STATIS file.

    Attributes
    ----------
    source : OptPath
        File data originally read from.
    is_yaml : bool
        Whether source file is in YAML format.
    data : np.ndarray
        Raw parsed data array.
    """

    __version__ = "0.1"

    def __init__(
        self,
        source: OptPath = None,
        control: Optional[Control] = None,
        config: Optional[Config] = None,
    ):
        """
        Instantiate class to parse and interpret STATIS file.

        Parameters
        ----------
        source : OptPath
            STATIS to read.
        control : Optional[Control]
            Associated CONTROL.
        config : Optional[Config]
            Associated CONFIG.
        """
        self.data = np.array([])
        self.is_yaml = False
        if source is not None:
            self.source = source
            self.read(source)
        if not self.is_yaml:
            self.gen_labels(control, config)

    @singledispatchmethod
    def __getitem__(self, val):
        """
        Get column(s) from `data`.

        If `val` is:
          - `int`: return 1-indexed column of `data`.
          - `slice`: return 1-indexed columns of `data.
          - `str`: First name match for column in `data` (based on `labels`)

        Parameters
        ----------
        val : Union[int, slice, str]
            Column to get.

        Raises
        ------
        NotImplementedError
            Bad type passed.
        """
        raise NotImplementedError(f"Unsupported get type ({type(val).__name__})")

    # 1 indexed slicing
    @__getitem__.register(int)
    def _(self, val):
        return self.data[:, val - 1]

    @__getitem__.register(slice)
    def _(self, val):
        val = slice(val.start - 1, val.stop - 1, val.step)
        return self.data[:, val]

    # Look up key
    @__getitem__.register(str)
    def _(self, val):
        if pos := next(
            (i for i, key in enumerate(self.labels) if val.lower() in key.lower()), None
        ):
            if val != self.labels[pos]:
                print(self.labels[pos])
            return self.data[:, pos]

        raise KeyError(f"Key {val} not found in statis")

    @property
    def rows(self) -> int:
        """
        Number of rows in data.
        """
        return self.data.shape[0]

    @property
    def columns(self) -> int:
        """
        Number of columns in data.
        """
        return self.data.shape[1]

    @property
    def _next_label(self) -> Tuple[int, int]:
        """
        Generate next label index from existing `labels`.

        Returns
        -------
        Tuple[int, int]
            Next label index.
        """
        row, col = divmod(len(self.labels), 5)
        return row + 1, col + 1

    def add_label(self, arg: str):
        """
        Add a label to the list of labels.

        Parameters
        ----------
        arg : str
            Label to add.
        """
        self.labels.append(f"{arg}")

    def read(self, filename: PathLike = "STATIS") -> "Statis":
        """
        Read and parse a STATIS file.

        Parameters
        ----------
        filename : PathLike
            File to read.

        Returns
        -------
        Statis
            Parsed statis.
        """
        with open(filename, "r", encoding="utf-8") as in_file:
            first_word = in_file.readline().split()[0]
            self.is_yaml = first_word == "%YAML"

        if self.is_yaml:
            yaml_parser = YAML()
            with open(filename, "rb") as in_file:
                data = yaml_parser.load(in_file)
                self.labels = data["labels"][0]
                self.data = np.array(data["timesteps"])
        else:
            with open(filename, "r", encoding="utf-8") as in_file:
                _, _, data = in_file.read().split("\n", 2)
                self.data = np.array(data.split(), dtype=float)
                columns = int(self.data[2]) + 3
                rows = self.data.size // (columns)
                self.data = self.data[: rows * columns]
                self.data.shape = rows, columns
                self.data = np.delete(self.data, 2, axis=1)

        return self

    def gen_labels(self, control: Optional[Control] = None, config: Optional[Config] = None):
        """
        Generate labels for headers in STATIS file.

        Parameters
        ----------
        control : Optional[Control]
            Control file relating to statis.
        config : Optional[Config]
            Config file relating to statis.
        """
        self.labels = [
            "Total Extended System Energy",
            "System Temperature",
            "Configurational Energy",
            "Short Range Potential Energy",
            "Electrostatic Energy",
            "Chemical Bond Energy",
            "Valence Angle And 3-Body Potential Energy",
            "Dihedral, Inversion, And 4-Body Potential Energy",
            "Tethering Energy",
            "Enthalpy (Total Energy + Pv)",
            "Rotational Temperature",
            "Total Virial",
            "Short-Range Virial",
            "Electrostatic Virial",
            "Bond Virial",
            "Valence Angle And 3-Body Virial",
            "Constraint Bond Virial",
            "Tethering Virial",
            "Volume",
            "Core-Shell Temperature",
            "Core-Shell Potential Energy",
            "Core-Shell Virial",
            "Md Cell Angle Α",
            "Md Cell Angle Β",
            "Md Cell Angle Γ",
            "Pmf Constraint Virial",
            "Pressure",
            "External Degree Of Freedom",
            "stress xx",
            "stress xy",
            "stress xz",
            "stress yx",
            "stress yy",
            "stress yz",
            "stress zx",
            "stress zy",
            "stress zz",
        ]

        if control:
            # Never true as yet
            if getattr(control, "l_msd", False) and config:
                for i in range(config.natoms):
                    self.add_label("Mean Squared Displacement")
                    self.add_label("Velocity . Velocity")
            if control.ensemble.ensemble in {"npt", "nst"}:
                for i in range(9):
                    self.add_label("Cell Dimensions")
                    self.add_label("Instantaneous PV")
                if any(key in control.ensemble.args for key in ("area", "tens", "semi", "orth")):
                    self.add_label("H_Z")
                    self.add_label("vol/h_z")
                    if any(key in control.ensemble.args for key in ("tens", "semi")):
                        self.add_label("gamma_x")
                        self.add_label("gamma_y")

        # Catch Remainder
        for i in range(len(self.labels) + 1, self.columns + 1):
            self.add_label(f"col_{i:d}")
        self.labels = ["iter", "time"] + self.labels

    def flatten(self):
        """
        Write data column-by-column to multiple files.

        Files will be named according to the label associated with each column in `Statis`.

        Note: If files already exist, they will be overwritten.
        """
        for i in range(self.columns - 3):
            with open(self.labels[i], "w", encoding="utf-8") as out_file:
                for j in range(self.rows):
                    out_file.write(f"{self.data[j, 1]} {self.data[j, i + 3]}\n")

    def __str__(self):
        return f"statis: {self.source} with {self.columns} columns: \n" + (
            "\n".join(f"{i} {label}" for i, label in enumerate(self.labels, 1))
        )

    def __repr__(self):
        return f"statis: {self.source} with {self.columns} columns: \n" + (
            ", ".join(f"{i} {label}" for i, label in enumerate(self.labels, 1))
        )
