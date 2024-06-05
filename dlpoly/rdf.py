"""
Module containing classes for loading rdf data from DL_POLY_4+.
"""

import numpy as np
from ruamel.yaml import YAML

from .types import OptPath, PathLike


class RDF():
    """
    Class for reading RDFDAT.

    Attributes
    ----------
    source : PathLike
        Original file read data from.
    is_yaml : bool
        Whether data are in YAML format.
    n_rdf : int
        Number of RDFs in file.
    n_points : int
        Number of points in each RDF.
    data : Optional[np.typing.NDArray]
        Data read from file.
    labels : Optional[List[str]]
        List of atoms from file.
    x : List[float]
        Radius of shell from origin.
    """
    __version__ = "0"

    def __init__(self, source: OptPath = None):
        """
        Instantiate class for reading RDFDAT.

        source : OptPath
            Source RDF to read.
        """

        self.n_rdf = 0
        self.n_points = 0
        self.x = None
        self.data = None
        self.labels = None
        self.is_yaml = False
        self.source = source

        if source is not None:
            self.read(source)

    def read(self, source: PathLike = "RDFDAT"):
        """
        Read RDF file in YAML or plaintext format.

        Parameters
        ----------
        source : PathLike
            File to read data from.
        """
        with open(source, 'r', encoding='utf-8') as in_file:
            test_word = in_file.readline().split()[0]
            self.is_yaml = test_word == "%YAML"

        if self.is_yaml:
            self._read_yaml(source)
        else:
            self._read_plaintext(source)

    def _read_yaml(self, source: PathLike):
        """
        Read RDF data from YAML format file.

        Parameters
        ----------
        source : PathLike
            File to read data from.
        """
        yaml_parser = YAML()

        with open(source, 'rb') as in_file:
            data = yaml_parser.load(in_file)

        self.n_rdf = data['npairs']
        self.n_points = data['ngrid']
        self.x = np.array(data['grid'])
        self.labels = [label['name'] for label in data['rdfs']]
        self.data = np.zeros((self.n_rdf, self.n_points, 2))

        for i in range(self.n_rdf):
            self.data[i, :, 0] = data['rdfs'][i]['gofr']
            self.data[i, :, 1] = data['rdfs'][i]['nofr']

    def _read_plaintext(self, source: PathLike):
        """
        Read RDF data from plain-text format file.

        Parameters
        ----------
        source : PathLike
            File to read data from.
        """
        with open(source, 'r', encoding='utf-8') as in_file:
            # Discard title
            in_file.readline()

            self.n_rdf, self.n_points = map(int, in_file.readline().split())

            self.x = np.zeros(self.n_points)
            self.data = np.zeros((self.n_rdf, self.n_points, 2))
            self.labels = []

            first_sample = True

            for sample in range(self.n_rdf):
                species = in_file.readline().split()

                if not species:
                    break

                self.labels.append(species)

                for point in range(self.n_points):
                    pos, g_r, n_r = map(float, in_file.readline().split())
                    if first_sample:
                        self.x[point] = pos

                    self.data[sample, point, :] = g_r, n_r

                first_sample = False
