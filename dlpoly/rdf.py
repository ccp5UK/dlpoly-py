"""
File containing methods for loading rdf data from DL_POLY_4
"""

import numpy as np


class rdf():
    __version__ = "0"

    def __init__(self, source=None):
        self.nRDF = 0
        self.nPoints = 0
        self.data = None
        self.labels = None
        if source is not None:
            self.source = source
            self.read(source)

    def read(self, source="RDFDAT"):
      """ Read an RDF file into data """
      with open(source, 'r') as fileIn:
        # Discard title
        _ = fileIn.readline()
        self.nRDF, self.nPoints = map(int, fileIn.readline().split())

        self.data = np.zeros((self.nRDF, self.nPoints, 2))
        self.labels = []

        for sample in range(self.nRDF):
            species = fileIn.readline().split()
            self.labels.append(species)
            for point in range(self.nPoints):
                r, g_r = fileIn.readline().split()
                self.data[sample, point, :] = float(r), float(g_r)
