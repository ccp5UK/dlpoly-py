"""
Module to handle miscellaneous input files.
"""

from abc import ABC, abstractmethod

from .types import PathLike, OptPath


class Input(ABC):
    """
    Abstract base class for tabulated potential files.

    Attributes
    ----------
    source
        File data originally read from.
    """

    def __init__(self, source: OptPath = None):
        """
        Instantiate tabulated potential input class.

        Parameters
        ----------
        source : OptPath
            File to read.
        """
        self.source = source

    @abstractmethod
    def read(self, source: PathLike):
        """
        Read file.

        Parameters
        ----------
        source : PathLike
            File to read.
        """
        self.source = source


class VDW(Input):
    """
    Class for tabulated VdW files.

    Attributes
    ----------
    source
        File data originally read from.
    """

    def read(self, source: PathLike = "TABVDW"):
        """
        Read file.

        Parameters
        ----------
        source : PathLike
            File to read.
        """
        self.source = source


class EAM(Input):
    """
    Class for tabulated EAM files.

    Attributes
    ----------
    source
        File data originally read from.
    """

    def read(self, source: PathLike = "TABEAM"):
        """
        Read file.

        Parameters
        ----------
        source : PathLike
            File to read.
        """
        self.source = source


class BND(Input):
    """
    Class for tabulated bond files.

    Attributes
    ----------
    source
        File data originally read from.
    """

    def read(self, source: PathLike = "TABBND"):
        """
        Read file.

        Parameters
        ----------
        source : PathLike
            File to read.
        """
        self.source = source


class ANG(Input):
    """
    Class for tabulated angle files.

    Attributes
    ----------
    source
        File data originally read from.
    """

    def read(self, source: PathLike = "TABANG"):
        """
        Read file.

        Parameters
        ----------
        source : PathLike
            File to read.
        """
        self.source = source


class DIH(Input):
    """
    Class for tabulated dihedral files.

    Attributes
    ----------
    source
        File data originally read from.
    """

    def read(self, source: PathLike = "TABDIH"):
        """
        Read file.

        Parameters
        ----------
        source : PathLike
            File to read.
        """
        self.source = source


class INV(Input):
    """
    Class for tabulated inversion files.

    Attributes
    ----------
    source
        File data originally read from.
    """

    def read(self, source: PathLike = "TABINV"):
        """
        Read file.

        Parameters
        ----------
        source : PathLike
            File to read.
        """
        self.source = source
