"""
Module to read correlation functions from DL_POLY_5
"""

from ruamel.yaml import YAML


class Correlations():
    """ class for reading Correlations

        :param source: Source correlations to read

    """

    def __init__(self, source=None):
        self.components = None
        self.blocks = None
        self.averaging_window = None
        self.points_per_block = None
        self.lags = None
        self.labels = None
        self.source = source
        self.derived = None
        self.is_yaml = False
        self.n_correlations = 0

        if source is not None:
            self.read(source)

    def read(self, source="COR"):
        """ Read a COR file into components

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
        """ Read a YAML format COR into components

        :param source: File to read

        """
        yaml_parser = YAML()

        with open(source, 'rb') as in_file:
            data = yaml_parser.load(in_file)

        self.n_correlations = len(data['correlations'])

        if self.n_correlations > 0:
            self.components = []
            self.blocks = []
            self.averaging_window = []
            self.points_per_block = []
            self.labels = []
            self.lags = []
            self.derived = []

        for i in range(self.n_correlations):
            cor = data['correlations'][i]

            self.components.append(cor['components'])
            self.blocks.append(cor['parameters']['number_of_blocks'])
            self.averaging_window.append(cor['parameters']['window_size'])
            self.points_per_block.append(cor['parameters']['points_per_block'])
            self.labels.append(cor['name'])
            self.lags.append(cor['lags'])

            if ('derived' in cor.keys()):
                self.derived.append(cor['derived'])

    def _read_plaintext(self, source):
        # unimplemented in dlpoly
        pass
