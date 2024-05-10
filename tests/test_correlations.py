#!/usr/bin/env python3
import unittest
from pathlib import Path

from dlpoly.correlations import Correlations

DATA_PATH = Path(__file__).parent


class CorrelationsTest(unittest.TestCase):

    correlations = Correlations(source=DATA_PATH / "COR.yml")

    def test_correlations_ncorrelations(self):
        self.assertEqual(self.correlations.n_correlations, 3,
                         'incorrect number of correlations')

    def test_correlations_window(self):
        self.assertEqual(self.correlations.averaging_window, [1, 1, 1],
                         'incorrect averaging window parameters')

    def test_correlations_blocks(self):
        self.assertEqual(self.correlations.blocks, [1, 1, 1],
                         'incorrect blocks parameters')

    def test_correlations_points(self):
        self.assertEqual(self.correlations.points_per_block, [300, 300, 300],
                         'incorrect block points parameters')

    def test_correlations_labels(self):
        self.assertEqual(self.correlations.labels, [['vv', 'Ar'], ['vv', 'Kr'], ['ss', 'global']],
                         'incorrect correlation labels')

    def test_correlations_lags(self):
        self.assertEqual(sum(self.correlations.lags[0]), 22.425,
                         'incorrect lags checksum')

    def test_correlations_components(self):
        self.assertEqual(sum(self.correlations.components[0]['v_x-v_x']), -6.860305158479998,
                         'incorrect component checksum')


if __name__ == '__main__':
    unittest.main()
