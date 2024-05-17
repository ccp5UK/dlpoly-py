#!/usr/bin/env python3
import unittest
from pathlib import Path

import numpy as np
from dlpoly.output import Output

DATA_PATH = Path(__file__).parent


class OutputTest(unittest.TestCase):

    output = Output(source=DATA_PATH / "OUTPUT")

    def test_output_vdw(self):
        self.assertEqual(self.output.vdw_energy, -0.298721E+04,
                         'incorrect lrc correction energy')

    def test_output_pres(self):
        self.assertAlmostEqual(self.output.pressure, 1.1103E+01,
                               msg="incorrect pressure", delta=0.1)

    def test_output_steps(self):
        self.assertEqual(self.output.steps, 20,
                         'incorrect number of steps')

    def test_output_avcell(self):
        cell = np.array([[112.3847796072, 0.0, 0.0], [0.0, 94.3222490199, 0.0], [0.0, 0.0, 94.2720855812]])
        assert np.allclose(self.output.average_cell, cell)

    def test_output_diff(self):
        self.assertEqual(self.output.diffusion['O'], (4.3873E-02, 1.8640E-02),
                         'incorrect diffusion for oxygen')


if __name__ == '__main__':
    unittest.main()
