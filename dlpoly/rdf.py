"""
Module containing classes for loading rdf data from DL_POLY_4
"""

import numpy as np
from ruamel.yaml import YAML


class RDF():
    """ class for reading RDFDAT

        :param source: Source RDF to read

        """
    __version__ = "0"

    def __init__(self, source=None):
        self.n_rdf = 0
        self.n_points = 0
        self.x = None
        self.data = None
        self.labels = None
        self.is_yaml = False
        self.source = source

        if source is not None:
            self.read(source)

    def read(self, source="RDFDAT"):
        """ Read an RDF file into data

        :param source: File to read

        """
        with open(source, 'r', encoding='utf-8') as in_file:
            test_word = in_file.readline().split()[0]
            self.is_yaml = test_word == "%YAML"

        if self.is_yaml:
            self._read_yaml(source)
        else:
            self._read_plaintext(source)

    def _read_yaml(self, source):
        """ Read a YAML format RDF into data

        :param source: File to read

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

    def _read_plaintext(self, source):
        """ Read a plaintext format RDF into data

        :param source: File to read

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
