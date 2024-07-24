"""
Module to read correlation functions from DL_POLY_4+.
"""

from ruamel.yaml import YAML
from .types import OptPath, PathLike


class Correlations:
    """
    Class for reading Correlations.

    Attributes
    ----------
    source : PathLike
        Original file read data from.
    data : list[float]
        Data contained in file.
    blocks : list[str]
        Blocks present in file.
    window : list[int]
        Window size of correlations.
    points_per_block : list[int]
        Number of points in each correlation block.
    lags : list[int]
        Lags of correlation functions.
    observables : list[str]
        List of observables in file.
    is_yaml : bool
        Data source in YAML format.
    n_correlations : int
        Number of types of correlations.
    """

    def __init__(self, source: OptPath = None):
        """
        Instantiate class for reading Correlations.

        Parameters
        ----------
        source : OptPath
            Source correlations to read.
        """
        self.source = source
        self.data = []
        self.blocks = []
        self.window = []
        self.points_per_block = []
        self.lags = []
        self.observables = []
        self.is_yaml = False

        if source is not None:
            self.read(source)

    @property
    def n_correlations(self) -> int:
        """
        Number of correlations in file.

        Returns
        -------
        int
            Number of correlations in file.
        """
        return len(self.data)

    def read(self, source: PathLike = "COR"):
        """
        Read a COR file into components.

        Parameters
        ----------
        source : PathLike
            File to read.
        """
        with open(source, "r", encoding="utf-8") as in_file:
            test_word = in_file.readline().split()[0]
            self.is_yaml = test_word == "%YAML"

        if self.is_yaml:
            self._read_yaml(source)
        else:
            self._read_plaintext(source)

    def _read_yaml(self, source: PathLike):
        """
        Read a YAML format COR into components.

        Parameters
        ----------
        source : PathLike
            File to read.
        """
        yaml_parser = YAML()

        with open(source, "rb") as in_file:
            yaml = yaml_parser.load(in_file)
            self.data = yaml.get("correlations", None)
            self.observables = yaml.get("observables", None)

        for cor in self.data.values():
            self.blocks.append(cor["parameters"]["number_of_blocks"])
            self.window.append(cor["parameters"]["window_size"])
            self.points_per_block.append(cor["parameters"]["points_per_block"])
            self.lags.append(cor["lags"])

    def _read_plaintext(self, source: PathLike):
        """
        Read plaintext form of correlations.

        N.B. Not actually implemented in DLPoly.

        Parameters
        ----------
        source : PathLike
            File to read data from.

        Raises
        ------
        NotImplementedError
           Not needed as not in DLPoly.
        """
        raise NotImplementedError
