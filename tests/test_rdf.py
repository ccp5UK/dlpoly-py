#!/usr/bin/env python3
import unittest
from pathlib import Path

from dlpoly.rdf import RDF

DATA_PATH = Path(__file__).parent


class RDFTest(unittest.TestCase):

    rdf = RDF(source=DATA_PATH / "RDFDAT")

    def test_rdf_nrdf(self):
        self.assertEqual(self.rdf.n_rdf, 190,
                         'incorrect number of rdfs')

    def test_rdf_npoints(self):
        self.assertEqual(self.rdf.n_points, 160,
                         'incorrect number of points')

    def test_rdf_label(self):
        self.assertListEqual(self.rdf.labels[1], ['O', 'CS'],
                             'incorrect labels')

    def test_rdf_point(self):
        self.assertListEqual(self.rdf.data[2, 12, :].tolist(),
                             [3.725672E+01, 2.343750E-03],
                             'incorrect point')
        self.assertEqual(self.rdf.x[12], 6.250000E-01,
                         'incorrect grid point')


if __name__ == '__main__':
    unittest.main()
