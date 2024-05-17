#!/usr/bin/env python3
import unittest
from pathlib import Path

from dlpoly.statis import Statis

DATA_PATH = Path(__file__).parent


class StatisTest(unittest.TestCase):

    statis = Statis(source=DATA_PATH / "STATIS")

    def test_statis_ncolumns(self):
        self.assertEqual(self.statis.columns, 68,
                         'incorrect number of columns')

    def test_statis_nrows(self):
        self.assertEqual(self.statis.rows, 5,
                         'incorrect number of rows')

    def test_statis_steptime(self):
        self.assertListEqual(list(self.statis.data[1, 0:2]),
                             [5, 1.750000E-03],
                             'incorrect cell time/step')

    def test_statis_temperature(self):
        self.assertEqual(self.statis["System Temperature"][2], 3.000000E+02,
                         'incorrect temperature')

    def test_statis_pressure(self):
        self.assertEqual(self.statis[29][3], 1.170673E+01,
                         'incorrect pressure')

    def test_statis_vpmf(self):
        self.assertEqual(self.statis[28][1], 0.000000E+00,
                         'incorrect virial pmf')

    def test_statis_consQ(self):
        self.assertEqual(self.statis[3][4], 6.565874E+04,
                         'incorrect conserved quantity')

    def test_statis_energies(self):
        self.assertListEqual(list(self.statis[5:13][2]),
                             [6.022616E+03, 8.482584E+04, -4.086941E+05, 1.121753E+04,
                              3.073748E+05, 1.129854E+04, 0.000000E+00, 6.577677E+04],
                             'incorrect energy terms')

    def test_statis_virial(self):
        self.assertListEqual(list(self.statis.data[1, 13:20]),
                             [-6.506158E+03, -1.808586E+06, 4.084056E+05, 3.127625E+05,
                              0.000000E+00, 1.080912E+06, 0.000000E+00],
                             'incorrect virial terms')

    def test_statis_angles(self):
        self.assertListEqual(list(self.statis.data[1, 24:27]),
                             [90.0, 90.0, 90.0],
                             'incorrect angles')

    def test_statis_volume(self):
        self.assertEqual(self.statis.data[4, 20], 9.993474E+05,
                         'incorrect volume')

    def test_statis_stress(self):
        self.assertListEqual(list(self.statis.data[4, 30:39]),
                             [8.060310E+00, -2.636976E+00, -1.941572E+00,
                              -2.636976E+00, 2.316919E+01, 4.915622E-01,
                              -1.941572E+00, 4.915622E-01, 2.080145E+01],
                             'incorrect stress')


if __name__ == '__main__':
    unittest.main()
