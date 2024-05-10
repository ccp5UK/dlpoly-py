#!/usr/bin/env python3
import unittest
from pathlib import Path

from ase.io import read
from dlpoly.calculator import DLPolyCalculator

DATA_PATH = Path(__file__).parent


class CalculatorTest(unittest.TestCase):

    def setUp(self):
        self.calculator = CalculatorTest.calculator
        self.atoms = CalculatorTest.atoms

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.calculator = DLPolyCalculator(control=DATA_PATH / "CONTROL",
                                          config=DATA_PATH / "CONFIG",
                                          field=DATA_PATH / "FIELD")

        cls.calculator.control['time_run'] = (0, 'steps')
        cls.calculator.control['time_equilibration'] = (0, 'steps')
        cls.atoms = read(cls.calculator.config_file, format='dlp4')
        cls.atoms.calc = cls.calculator

    def test_positions(self):
        self.assertEqual(list(self.atoms.get_positions()[-1]),
                         [28.02247594, 14.74976435, 24.7762946],
                         'incorrect atom positions')

    def test_velocities(self):
        self.assertEqual(list(self.atoms.get_velocities()[-1]),
                         [0.0008197670985684685, 0.0004644243373440111, 0.0003975945065119798],
                         'incorrect atom velocities')

    def test_momenta(self):
        self.assertEqual(list(self.atoms.get_momenta()[-1]),
                         [0.0008263252353570163, 0.00046813973204276317, 0.00040077526256407565],
                         'incorrect momenta')

    def test_forces(self):
        self.assertEqual(list(self.atoms.get_forces()[-1]),
                         [-0.004484684106032792, 0.016657116189381243, -0.01941887139048563],
                         "incorrect forces")


if __name__ == '__main__':
    unittest.main()
